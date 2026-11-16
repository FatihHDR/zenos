# Phase 4 — Scenario 3 & 4: hasil lengkap (retrieval + generasi)

Scenario 3 (hybrid RRF + cross-encoder — model utama) dan Scenario 4 (hybrid tanpa
reranker — ablasi) dari PRD Section 5, dengan **seluruh tujuh metrik PRD Section 6**:
Recall@25, Recall@5, MRR, groundedness, citation precision, refusal accuracy, dan TTFT.

Dijalankan terpisah dengan alasan memori: Scenario 4 hanya butuh embedder, Scenario 3 butuh
embedder + cross-encoder; menjalankannya terpisah juga membuat Scenario 4 jadi uji konsistensi
terhadap harness lama (§5). Metrik generasi butuh endpoint LLM hidup.

Data mentah (semuanya artefak mentah, bukan angka yang diketik ulang):

| Berkas | Isi |
| --- | --- |
| `results/scenarios-3.json` | retrieval, Scenario 3 |
| `results/scenarios-4.json` | retrieval, Scenario 4 |
| `results/generation-3.json` | generasi + TTFT, Scenario 3 |
| `results/generation-4.json` | generasi + TTFT, Scenario 4 |

Generated: retrieval `2026-11-16T15:23Z` · generasi `2026-11-16T15:52Z`

---

## Bagian A — Retrieval

### A.1 Konteks: perbandingan keempat skenario

Semua angka diukur pada korpus yang sama (223 chunk), eval set yang sama (8 pertanyaan
relevan), k=25, top_n=5. Baris S1/S2 berasal dari `results/scenarios-1-2.md`.

| Skenario | Mode | Reranker | Recall@25 | MRR@25 | **Recall@5** | MRR@5 | Retrieval ms | Rerank ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | dense | ya | 1.000 | 0.535 | **0.812** | 0.692 | 2 815 | 67 914 |
| 2 | sparse | ya | 1.000 | 0.596 | **0.812** | 0.688 | 2 310 | 67 866 |
| **3** | **hybrid** | **ya** | 1.000 | **0.623** | **0.812** | 0.681 | **1 778** | **39 671** |
| **4** | **hybrid** | tidak | 1.000 | 0.623 | **0.688** | 0.594 | 2 082 | 0 |

Kolom latensi di sini **tidak sebanding lintas baris**: S1/S2 diukur saat host kehabisan swap
(8/8 GB), S3/S4 saat memori sehat. Hanya baris S3 vs S4 yang boleh dibandingkan — dan itupun
sebagai indikasi, bukan benchmark (§6).

### A.2 Scenario 3 vs 4 — kontribusi reranker

| Metrik | S3 (reranker) | S4 (tanpa) | Selisih |
| --- | --- | --- | --- |
| Recall@25 | 1.000 | 1.000 | 0.000 |
| MRR@25 | 0.623 | 0.623 | 0.000 |
| **Recall@5** | **0.812** | **0.688** | **+0.124** |
| **MRR@5** | **0.681** | **0.594** | **+0.087** |
| Rerank ms | 39 671 | 0 | +39,7 s |

Recall@25 dan MRR@25 **identik sampai 4 desimal**, persis seperti yang PRD nyatakan: kedua
skenario memakai kandidat yang sama, reranker hanya mengurutkan ulang. Ini sekaligus bukti
internal bahwa ablasi benar-benar mematikan reranker dan tidak diam-diam mengubah retrieval.

### A.3 Per pertanyaan (S3 vs S4)

| Pertanyaan | S3 Recall@5 | S4 Recall@5 | S3 MRR@5 | S4 MRR@5 |
| --- | --- | --- | --- | --- |
| Asas Pelindungan Data Pribadi | **1.000** | 0.000 | 0.250 | 0.000 |
| Definisi Pengendali Data Pribadi | 1.000 | 1.000 | 1.000 | 1.000 |
| Sanksi administratif | 1.000 | 1.000 | 1.000 | 1.000 |
| Manfaat virtual memory | 1.000 | 1.000 | 1.000 | 1.000 |
| TLB hit vs TLB miss | 0.500 | 0.500 | 0.200 | 0.250 |
| Urutan penanganan page fault | 0.000 | 0.000 | 0.000 | 0.000 |
| MMU address translation | 1.000 | 1.000 | **1.000** | 0.500 |
| Page vs page frame | 1.000 | 1.000 | 1.000 | 1.000 |

### A.4 Scenario 3 vs 1 & 2 — kontribusi fusion (RRF)

| Metrik | S1 dense | S2 sparse | S3 hybrid |
| --- | --- | --- | --- |
| Recall@25 | 1.000 | 1.000 | 1.000 |
| **MRR@25** | 0.535 | 0.596 | **0.623** |
| Recall@5 | 0.812 | 0.812 | 0.812 |
| MRR@5 | **0.692** | 0.688 | 0.681 |

### A.5 Konsistensi harness

| Konfigurasi | Jalur | Recall@25 | Recall@5 |
| --- | --- | --- | --- |
| hybrid, tanpa reranker | `evaluate_recall.py --mode hybrid --k 5` (jalur lama) | 1.000 | 0.688 |
| hybrid, tanpa reranker = Scenario 4 | `evaluate_scenarios.py --scenarios 4` (jalur baru) | 1.000 | **0.688** |

Dua harness berbeda, ditulis terpisah, menghasilkan angka **identik sampai 4 desimal**. Ini
validasi bahwa runner skenario mengukur hal yang sama dengan harness Phase 2.

---

## Bagian B — Generasi

### B.1 Definisi metrik (deterministik, tanpa LLM-as-judge)

* **Groundedness** = klaim yang punya sitasi valid / seluruh klaim, dihitung pada jawaban untuk
  8 pertanyaan relevan. Jawaban yang menolak tidak punya klaim untuk dilacak, jadi dikecualikan
  dan dinilai oleh refusal accuracy.
* **Citation precision** = tag valid / seluruh tag yang diemitkan. Tag valid bila
  `(source_name, page)`-nya benar-benar ada di konteks yang dikirim ke model.
* **Refusal accuracy** = negative control ditolak / jumlah negative control.
* **TTFT** = dari query dikirim sampai token pertama keluar (termasuk retrieve + rerank).

### B.2 Hasil

| Metrik | Target PRD | **S3** (reranker) | **S4** (tanpa reranker) |
| --- | --- | --- | --- |
| Groundedness | > 95% | **0.653** (32/49 klaim) | **0.727** (32/44 klaim) |
| Citation precision | — | **1.000** (33/33 tag) | **1.000** (35/35 tag) |
| Refusal accuracy | harus menolak | **1.000** (1/1) | **0.000** (0/1) |
| False refusal (pertanyaan relevan) | 0 | 0.000 | 0.000 |
| **TTFT mean** | **< 2,5 s** | **67 318 ms** | **5 671 ms** |
| TTFT p50 / p95 / max | | 66 046 / 99 544 / 99 544 ms | 4 116 / 15 421 / 15 421 ms |

### B.3 Rincian TTFT

| Komponen | S3 | S4 |
| --- | --- | --- |
| Retrieval (+ rerank) — mean | 55 283 ms | 1 537 ms |
| LLM sampai token pertama — mean | 12 035 ms | 4 134 ms |
| **TTFT total — mean** | **67 318 ms** | **5 671 ms** |

Reranker menyumbang **~54 s** dari TTFT Scenario 3 (55,3 s vs 1,5 s retrieval). Di Scenario 4,
LLM sampai token pertama saja **4,1 s** — di atas anggaran 2,5 s **sebelum** retrieval dihitung.

### B.4 Per pertanyaan

| Pertanyaan | S3 klaim bersitasi | S3 tag | S3 TTFT | S4 klaim bersitasi | S4 tag | S4 TTFT |
| --- | --- | --- | --- | --- | --- | --- |
| Asas Pelindungan Data Pribadi | 8/17 | 8/8 | 59,0 s | 6/8 | 6/6 | 15,4 s |
| Definisi Pengendali Data Pribadi | 1/1 | 1/1 | 40,0 s | 1/1 | 1/1 | 2,7 s |
| Sanksi administratif | 5/6 | 5/5 | 56,1 s | 5/6 | 5/5 | 3,8 s |
| Manfaat virtual memory | 4/5 | 4/4 | 62,8 s | 4/4 | 4/4 | 6,9 s |
| TLB hit vs TLB miss | 2/7 | 3/3 | 66,0 s | 6/6 | 6/6 | 4,1 s |
| Urutan penanganan page fault | 3/4 | 3/3 | 77,6 s | 4/11 | 4/4 | 4,9 s |
| MMU address translation | 7/7 | 7/7 | 71,0 s | 4/5 | 5/5 | 2,9 s |
| Page vs page frame | 2/2 | 2/2 | 73,6 s | 2/3 | 2/2 | 3,4 s |
| **Negative control** | 0/1 **(menolak)** | 0/0 | 99,5 s | 2/3 **(menjawab!)** | 2/2 | 6,8 s |

---

## Findings

### Retrieval

1. **RRF akhirnya terlihat berkontribusi — tapi hanya di tahap retrieval, dan hanya lewat MRR.**
   MRR@25 hybrid **0.623** vs sparse 0.596 vs dense 0.535: fusion menaikkan posisi chunk relevan
   pertama di dalam pool. Recall@25 tetap 1.000 untuk ketiganya sehingga buta terhadap perbedaan
   ini — persis alasan PRD menyebut MRR sebagai metrik pendamping.
2. **Tapi keunggulan fusion itu hilang setelah reranker.** Recall@5 ketiganya seri di 0.812, dan
   MRR@5 justru sedikit memihak dense (0.692) dibanding hybrid (0.681). Setelah ada
   cross-encoder, pilihan mode retrieval hampir tidak lagi menentukan hasil akhir; nilai RRF
   yang terukur ada di kualitas pool (MRR@25), bukan di konteks akhir.
3. **Keuntungan reranker bertumpu pada SATU pertanyaan.** Seluruh kenaikan Recall@5 dari
   0.688 → 0.812 berasal dari *"asas Pelindungan Data Pribadi"* (0.000 → 1.000); tujuh
   pertanyaan lain tidak berubah (1/8 = 0.125 ≈ +0.124 yang terukur). Nilai reranker yang lebih
   meyakinkan ada di *pengurutan* — misalnya MMU, MRR@5 0.500 → 1.000.
4. **Dua pertanyaan gagal secara sistematis di semua konfigurasi.** *"Urutan penanganan page
   fault"* = 0.000 di 6 dari 6 konfigurasi yang pernah diukur, dan *"TLB hit vs TLB miss"* mentok
   0.500 di semua skenario ber-reranker. Karena Recall@25 = 1.000 (bukti *ada* di pool, di
   ranking 6–25), ini **kegagalan pemeringkatan, bukan retrieval** — dan karena konsisten lintas
   mode, tersangkanya reranker, chunking, atau ground-truth-nya sendiri. Item investigasi nomor satu.
5. **Tidak ada skenario yang mencapai target Recall@5 > 90%** (terbaik 81,3%). Karena kedua
   pertanyaan yang gagal itu gagal di semua mode, menambah korpus atau mengganti mode retrieval
   bukan jawabannya.

### Generasi

6. **Nol sitasi dikarang.** Citation precision **1.000 di kedua skenario**: 68 tag yang diemitkan
   model semuanya menunjuk chunk yang benar-benar dikirim sebagai konteks. Jadi kekurangan
   grounding **bukan** halusinasi sumber, melainkan **sitasi yang hilang** — sejumlah kalimat
   tidak diberi tag. Perbaikannya kepatuhan format, bukan kejujuran model.
7. **Groundedness 0,65–0,73, jauh di bawah target 95%.** Terparah pada jawaban panjang:
   *"asas Pelindungan Data Pribadi"* 8 dari 17 klaim (9 klaim tanpa tag) di S3, *"page fault"*
   4 dari 11 di S4. Model cenderung memberi tag pada poin utama lalu meninggalkan kalimat
   penjelas tanpa tag.
8. **Target TTFT tidak tercapai bahkan tanpa reranker.** S4 = **5,67 s** (p95 15,4 s), 2,3× di
   atas anggaran; S3 = **67,3 s**, 27× di atas. Karena LLM sampai token pertama saja 4,1 s di S4,
   **tidak ada optimasi retrieval yang bisa memenuhi < 2,5 s dengan endpoint ini**.
9. **Hipotesis PRD soal S3 vs S4 terkonfirmasi, dengan margin besar.** PRD menduga Scenario 4
   lebih rendah kualitasnya tapi TTFT-nya lebih rendah: reranker menambah **+61,6 s TTFT** demi
   **+0,124 Recall@5**. Pertukaran yang sangat mahal di mesin ini.
10. **Refusal tidak stabil, dan itu kelemahan nyata pada n=1.** S3 menolak negative control (1/1),
    S4 menjawabnya (0/1) dengan dua sitasi valid, sementara run S4 identik sebelumnya **menolak**.
    Dengan satu control, angkanya 0,000 atau 1,000 tergantung undian.
11. **Kasus S4 itu memperlihatkan batas metrik deterministik.** Pertanyaan negative control tidak
    bisa dijawab dari korpus, tapi S4 menjawabnya dan **semua tag-nya valid** → groundedness
    deterministik menilainya "grounded". **Sitasi valid ≠ jawaban benar.** Inilah alasan PRD
    menyebut Ragas sebagai indikator pendamping.
12. **Reranker lokal ~40 s/query** bahkan dengan memori sehat (vs anggaran TTFT 2,5 s). Angka
    73,7 s di `results/scenarios-1-2.md` menggelembung ~2× akibat swap penuh; yang "bersih"
    39,7 s. Kesimpulan operasionalnya tetap: cross-encoder fp32 di CPU mesin ini terlalu lambat,
    perlu Cohere API atau GPU.

---

## Caveats

* **Latensi terkontaminasi beban host — jangan disajikan sebagai benchmark.** Retrieval terbaca
  1,5–2,8 s di run skenario, sementara pengukuran terisolasi sebelumnya 0,22–0,32 s (7–13×
  berbeda). Swap pernah penuh 8/8 GB dan pod Qdrant `OOMKilled` 6×. LLM sampai token pertama di
  S3 (12,0 s) juga >2× S4 (4,1 s) tanpa penjelasan yang jelas. Angka TTFT absolut = batas atas;
  **selisih S3 vs S4** tetap bermakna karena diukur di run yang sama.
* **Refusal accuracy n=1.** Satu negative control; lihat findings 10 dan 11.
* **n = 8 pertanyaan, satu run per konfigurasi** — belum ada error bar. Selisih di bawah ~0,1
  (mis. MRR@5 S3 0.681 vs S1 0.692, atau groundedness S3 0.653 vs S4 0.727) sebaiknya dibaca
  sebagai seri, bukan keunggulan.
* **Ground truth bersifat leksikal** (anchor phrase → chunk id): reproducible dan fail-fast,
  tapi lebih kasar daripada penilaian relevansi manusia.
* **Groundedness deterministik = proxy.** Ia mengukur "apakah klaim punya sitasi yang valid",
  bukan "apakah isi klaim benar" (finding 11).
* **Scenario 1 & 2 belum diukur untuk metrik generasi** — jadi tabel empat skenario baru lengkap
  untuk kolom retrieval.
* Negative control tidak masuk metrik retrieval (tidak punya ground truth); di sini ia dinilai
  oleh refusal accuracy.

---

## Reproduksi

```bash
# butuh Qdrant; metrik generasi juga butuh endpoint LLM
kubectl -n zenos port-forward svc/qdrant 6333:6333 6334:6334
kubectl -n zenos port-forward svc/nine-router 20128:20128

# retrieval
python scripts/evaluate_scenarios.py --scenarios 4 --out results/scenarios-4.json
python scripts/evaluate_scenarios.py --scenarios 3 --out results/scenarios-3.json

# generasi (groundedness, citation precision, refusal accuracy, TTFT)
python scripts/evaluate_generation.py --scenarios 4 --out results/generation-4.json
python scripts/evaluate_generation.py --scenarios 3 --out results/generation-3.json
```

Catatan mesin uji: single node, 7,5 GiB RAM tanpa GPU. Kedua model (~4,5 GB) berjalan di CPU,
sehingga latensi di dokumen ini adalah batas atas, bukan karakteristik sistem.
