"""Extract structural records from a legacy planning/rolling_plan.yml.

Lets the structure engine run on existing projects (same migration spirit as
legacy.py for canon_delta), so the read-pull / anti-shrink checks work before a
project adopts the native structure/ layout.
"""

from __future__ import annotations

import re
from pathlib import Path

from ..events import chapter_sort_key
from ..yamlio import load_yaml
from .chapter_meta import ChapterMeta

# Growth markers, but not when negated (e.g. "不突破" = does NOT break through).
_GROWTH_MARKERS = re.compile(r"(?<![不未没无])(?:突破|升级|晋升|进阶)|power[_ -]?up|breakthrough", re.IGNORECASE)


def _nonempty(value) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip()) and value.strip().lower() not in {"n/a", "na", "none", "无", "[]", "{}"}
    if isinstance(value, (list, dict)):
        return len(value) > 0
    return bool(value)


def _tension_from_position(position: str | None, tension_by_position: dict) -> float | None:
    if not position:
        return None
    return tension_by_position.get(str(position).strip().lower())


def from_rolling_plan(project: Path, profile: dict | None = None) -> list[ChapterMeta]:
    project = Path(project)
    rolling = load_yaml(project / "planning" / "rolling_plan.yml")
    if not isinstance(rolling, dict) or not isinstance(rolling.get("chapters"), list):
        return []

    tension_by_position = ((profile or {}).get("structure", {}) or {}).get("tension_by_position", {})
    records: list[ChapterMeta] = []
    for block in rolling["chapters"]:
        if not isinstance(block, dict) or not block.get("chapter"):
            continue
        arch = block.get("architecture_role") or {}
        pressure = block.get("pressure_curve") or {}
        position = pressure.get("position_in_flow") or block.get("flow_position")
        growth_budget = str(arch.get("protagonist_growth_budget") or "")
        records.append(ChapterMeta(
            chapter=str(block["chapter"]),
            pacing_mode=arch.get("pacing_mode"),
            chapter_function=block.get("chapter_function"),
            position_in_flow=position,
            tension=_tension_from_position(position, tension_by_position),
            world_expansion=_nonempty(arch.get("world_expansion")),
            protagonist_growth=bool(_GROWTH_MARKERS.search(growth_budget)),
            side_threads=[str(s) for s in (arch.get("side_thread_touch") or [])],
            offscreen_pressure=_nonempty(arch.get("offscreen_pressure")),
        ))
    records.sort(key=lambda r: r.sort_key)
    return records
