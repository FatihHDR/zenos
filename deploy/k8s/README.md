# Zenos on Kubernetes (local kind / single node)

Runs **Qdrant** and **9router** in the cluster. Access from the host uses the node
IP + **NodePort** (see "Why NodePort" below).

| Component | In-cluster DNS | Host access (`.env`) |
| --- | --- | --- |
| Qdrant | `qdrant.zenos.svc:6333/6334` | `172.20.0.2:30633` / `30634` |
| 9router | `nine-router.zenos.svc:20128` | `172.20.0.2:30128` |

> 9router is deployed as `nine-router` because Kubernetes Service names must
> start with a letter.
> The node IP is stable for the cluster's lifetime; get it with `kubectl get nodes -o wide`.

## Why NodePort, not hostPort
`hostPort` does not work on this host: the CNI portmap plugin issues
`iptables -m multiport`, but the kernel (`7.2.11-zen1-1-zen`) has **no
`xt_multiport`** module at all (`Extension multiport revision 0 not supported`),
so pod sandboxes never get created (`FailedCreatePodSandBox`). NodePort is
handled by kube-proxy instead and works.

## Prerequisites
- Cluster reachable via `kubectl` (this repo targets the local kind cluster `kind-k8s-local`).
- StorageClass `standard` (kind `local-path`).
- `kind` CLI — the node cannot reach Docker Hub, so images must be loaded locally.

## Deploy

```bash
# 1. Free any host ports used by the old containers
docker rm -f zenos-qdrant 9router

# 2. Load images into the kind node (docker save + ctr import; `kind load` chokes on OCI digests)
SP=$(mktemp -d)
docker pull busybox:1.36
for img in qdrant/qdrant:v1.13.4 decolua/9router:latest busybox:1.36; do
  docker save "$img" -o "$SP/img.tar"
  docker exec -i k8s-local-control-plane ctr -n k8s.io images import --snapshotter=overlayfs - < "$SP/img.tar"
done

# 3. Namespace + secret (real values, not committed)
kubectl apply -f deploy/k8s/namespace.yaml
kubectl -n zenos create secret generic zenos-secrets \
  --from-literal=INITIAL_PASSWORD='<9router password>' \
  --from-literal=OPENAI_API_KEY='<9router API key>' \
  --dry-run=client -o yaml | kubectl apply -f -

# 4. 9router PVC + seed existing ~/.9router data (kind cannot bind host dirs)
kubectl apply -f deploy/k8s/nine-router-data.yaml
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata: {name: nine-router-seed, namespace: zenos}
spec:
  restartPolicy: Never
  containers:
    - name: seed
      image: busybox:1.36
      imagePullPolicy: IfNotPresent
      command: ["sh", "-c", "sleep 3600"]
      volumeMounts: [{name: data, mountPath: /data}]
  volumes:
    - name: data
      persistentVolumeClaim: {claimName: nine-router-data}
EOF
kubectl -n zenos wait --for=condition=Ready pod/nine-router-seed --timeout=120s
kubectl -n zenos cp ~/.9router/. nine-router-seed:/data
kubectl -n zenos delete pod nine-router-seed

# 5. Deploy workloads
kubectl apply -k deploy/k8s
kubectl -n zenos rollout status statefulset/qdrant
kubectl -n zenos rollout status deployment/nine-router
```

Then point `.env` at the node IP + NodePorts:

```
QDRANT_HOST=172.20.0.2
QDRANT_PORT=30633
QDRANT_GRPC_PORT=30634
OPENAI_BASE_URL=http://172.20.0.2:30128/v1
```

If seeding is skipped, 9router starts empty and providers/keys must be
re-created in the dashboard.

## Cluster DNS note
This cluster's CoreDNS was crash-looping (51 restarts) and pods could not resolve
external names (`EAI_AGAIN`). Fixed by pointing the Corefile `forward` at an
explicit resolver:

```bash
kubectl -n kube-system get cm coredns -o yaml \
  | sed 's#forward . /etc/resolv.conf#forward . 192.168.1.1 1.1.1.1#' \
  | kubectl apply -f -
kubectl -n kube-system rollout restart deployment coredns
```

## Verify

```bash
kubectl -n zenos get pods,svc,pvc
curl -s http://172.20.0.2:30633/collections
curl -s -o /dev/null -w '%{http_code}\n' http://172.20.0.2:30128/api/health     # 200
python scripts/setup_db.py && python scripts/ask.py -q "..."                     # end-to-end
```

## Rollback

```bash
kubectl delete namespace zenos
docker-compose up -d          # Qdrant back on host
docker run -d --name 9router -p 127.0.0.1:20128:20128 \
  -v "$HOME/.9router:/app/data" -e DATA_DIR=/app/data \
  -e INITIAL_PASSWORD='<9router password>' decolua/9router:latest
# and restore .env to 127.0.0.1:6333 / 127.0.0.1:20128
```

## Zenos API (FastAPI)
`api.yaml` deploys the FastAPI app (PRD Phase 4, point 3) on port 8000 with its own
model-cache PVC at `/models` (`HF_HOME`). It reaches the other services via
ClusterIP DNS (`qdrant:6333`, `nine-router:20128/v1`) — no NodePort needed.

```bash
docker build -t zenos-api:local .          # ~3.3GB (CPU-only torch)
docker save zenos-api:local -o /tmp/zenos-api.tar
docker exec -i k8s-local-control-plane ctr -n k8s.io images import --snapshotter=overlayfs - < /tmp/zenos-api.tar
kubectl apply -k deploy/k8s
kubectl -n zenos rollout status deployment/zenos-api
```

### Model cache (required)
The pod cannot download from the Hub — `snapshot_download` stalls at
`Fetching N files: 0%` from inside the cluster even though the host fetches the
same repo in seconds. So the models must be **pre-seeded** and the pod runs
**offline** (`HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1` in `api.yaml`).

Both `BAAI/bge-m3` and `BAAI/bge-reranker-v2-m3` are needed (flag any missing
`pytorch_model.bin` — an incomplete snapshot silently triggers the fastembed
fallback and then fails). Seed with `tar -h`: the host cache stores weights as
symlinks into a xet CAS, and copying without dereferencing produces a broken
cache.

```bash
kubectl -n zenos scale deployment/zenos-api --replicas=0
kubectl -n zenos apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata: {name: api-cache-seed, namespace: zenos}
spec:
  restartPolicy: Never
  containers:
    - name: seed
      image: busybox:1.36
      command: ["sh", "-c", "sleep 3600"]
      volumeMounts: [{name: m, mountPath: /models}]
  volumes:
    - name: m
      persistentVolumeClaim: {claimName: zenos-api-cache}
EOF
kubectl -n zenos wait --for=condition=Ready pod/api-cache-seed --timeout=120s
tar -h -C ~/.cache/huggingface -cf - \
  hub/models--BAAI--bge-m3 hub/models--BAAI--bge-reranker-v2-m3 \
  | kubectl -n zenos exec -i api-cache-seed -- tar -C /models -xf -
kubectl -n zenos delete pod api-cache-seed
kubectl -n zenos scale deployment/zenos-api --replicas=1
```

Build the host cache first if needed (`HF_HUB_DISABLE_XET=1` is faster here):

```bash
HF_HUB_DISABLE_XET=1 .venv/bin/python -c \
 "from huggingface_hub import snapshot_download as d; d('BAAI/bge-m3'); d('BAAI/bge-reranker-v2-m3')"
```

### Try it
The **first** request loads the models (~10s); later ones are fast.

```bash
kubectl -n zenos exec deploy/zenos-api -- curl -s localhost:8000/health
kubectl -n zenos exec deploy/zenos-api -- \
  curl -s -X POST localhost:8000/answer -H 'Content-Type: application/json' -d '{"query":"..."}'
# or from the host (port 8000 must be free locally):
kubectl -n zenos port-forward svc/zenos-api 8000:8000
```

### Resources
`BGE-M3` + reranker are ~4.5GiB of weights in RAM; the manifest requests 1Gi and
limits 6Gi. On a 7.5GiB host this is tight — reduce other workloads if the pod is
OOMKilled.

## Notes
- The API has **no auth** — keep it internal or put it behind a reverse proxy.
- `secret.example.yaml` is a template only — never commit real credentials.
