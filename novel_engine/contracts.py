"""Validate creative-layer artifacts (scene specs, editor verdicts) against their
JSON Schemas — same emit-time validation philosophy as canon events.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from . import jsonschema_lite

_SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"


@lru_cache(maxsize=8)
def load_schema(name: str) -> dict:
    path = _SCHEMA_DIR / f"{name}.schema.json"
    if not path.exists():
        raise FileNotFoundError(f"Schema not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_scene_spec(obj: dict) -> list[str]:
    return jsonschema_lite.validate(obj, load_schema("scene_spec"))


def validate_editor_verdict(obj: dict) -> list[str]:
    return jsonschema_lite.validate(obj, load_schema("editor_verdict"))
