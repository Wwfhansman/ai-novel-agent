"""Load and validate per-chapter structural records.

Native layout:
    structure/
      ch002.yml      # one chapter_meta object, or {chapter: ch002, ...}
      ch003.yml

Falls back to extracting from planning/rolling_plan.yml when no structure/ dir
exists (see legacy_structure.py).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from .. import jsonschema_lite
from ..events import chapter_sort_key
from ..yamlio import load_yaml

_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "chapter_meta.schema.json"


@lru_cache(maxsize=1)
def chapter_meta_schema() -> dict:
    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


@dataclass
class ChapterMeta:
    chapter: str
    pacing_mode: str | None = None
    chapter_function: str | None = None
    position_in_flow: str | None = None
    time_span: str | None = None
    tension: float | None = None
    world_expansion: bool = False
    protagonist_growth: bool = False
    side_threads: list[str] = field(default_factory=list)
    offscreen_pressure: bool = False
    scene_types: list[str] = field(default_factory=list)

    @property
    def sort_key(self) -> int:
        return chapter_sort_key(self.chapter)

    @classmethod
    def from_dict(cls, data: dict) -> "ChapterMeta":
        return cls(
            chapter=str(data.get("chapter")),
            pacing_mode=data.get("pacing_mode"),
            chapter_function=data.get("chapter_function"),
            position_in_flow=data.get("position_in_flow"),
            time_span=data.get("time_span"),
            tension=data.get("tension"),
            world_expansion=bool(data.get("world_expansion", False)),
            protagonist_growth=bool(data.get("protagonist_growth", False)),
            side_threads=list(data.get("side_threads") or []),
            offscreen_pressure=bool(data.get("offscreen_pressure", False)),
            scene_types=list(data.get("scene_types") or []),
        )


def validate_record(obj: dict) -> list[str]:
    return jsonschema_lite.validate(obj, chapter_meta_schema())


def load_native(project: Path) -> tuple[list[ChapterMeta], list[str]]:
    directory = Path(project) / "structure"
    records: list[ChapterMeta] = []
    errors: list[str] = []
    if not directory.exists():
        return records, errors
    for path in sorted(directory.glob("*.yml"), key=lambda p: chapter_sort_key(p.stem)):
        raw = load_yaml(path)
        if not isinstance(raw, dict):
            continue
        raw.setdefault("chapter", path.stem)
        problems = validate_record(raw)
        if problems:
            errors.extend(f"CHAPTER_META_SCHEMA: {path}: {p}" for p in problems)
            continue
        records.append(ChapterMeta.from_dict(raw))
    records.sort(key=lambda r: r.sort_key)
    return records, errors
