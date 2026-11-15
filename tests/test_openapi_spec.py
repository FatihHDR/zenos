"""Guards the hand-written OpenAPI spec (docs/openapi.yaml) against drift from the app."""

from pathlib import Path

import pytest
import yaml

from api.app import app

SPEC_PATH = Path(__file__).resolve().parents[1] / "docs" / "openapi.yaml"
SHARED_SCHEMAS = ["Citation", "GroundedAnswer", "HealthResponse", "InfoResponse"]


@pytest.fixture(scope="module")
def spec():
    return yaml.safe_load(SPEC_PATH.read_text())


def _iter_refs(node):
    if isinstance(node, dict):
        if "$ref" in node:
            yield node["$ref"]
        for value in node.values():
            yield from _iter_refs(value)
    elif isinstance(node, list):
        for value in node:
            yield from _iter_refs(value)


def test_spec_is_openapi_31(spec):
    assert spec["openapi"].startswith("3.1.")


def test_all_refs_resolve(spec):
    for ref in set(_iter_refs(spec)):
        node = spec
        for part in ref.lstrip("#/").split("/"):
            assert part in node, f"unresolved $ref: {ref}"
            node = node[part]


def test_paths_and_operations_match_app(spec):
    live = app.openapi()
    assert sorted(spec["paths"]) == sorted(live["paths"])

    live_ops = {f"{m.upper()} {p}" for p, item in live["paths"].items() for m in item}
    spec_ops = {
        f"{m.upper()} {p}"
        for p, item in spec["paths"].items()
        for m in item
        if m in ("get", "post")
    }
    assert live_ops == spec_ops


@pytest.mark.parametrize("name", SHARED_SCHEMAS)
def test_shared_schema_fields_match_app(spec, name):
    live = set(app.openapi()["components"]["schemas"][name].get("properties", {}))
    written = set(spec["components"]["schemas"][name].get("properties", {}))
    assert live == written
