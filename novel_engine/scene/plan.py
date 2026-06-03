"""A chapter's scene plan: load + validate, or draft a skeleton.

A scene plan is chapters/chNNN/scene_plan.yml:

    chapter: ch004
    scenes:
      - {id: ch004_s1, pov: ..., emotional_temperature: {...}, sensory_anchor: ..., exit_on: ..., one_change: ...}
      - ...

draft_from_rolling() bootstraps a skeleton by splitting the rolling_plan's
pressure_curve.chapter_internal_motion into beats and distributing the
narrative_weave beats — turning planning the project already has into a scene
worksheet the writer refines. The creative fill stays human/LLM; the structure
is engine-enforced (validated against schemas/scene_spec.schema.json).
"""

from __future__ import annotations

import re
from pathlib import Path

from ..contracts import validate_scene_spec
from ..yamlio import load_yaml

_ARROW = re.compile(r"\s*(?:→|->|⇒|=>|—>)\s*")


def _chapter_block(project: Path, chapter: str) -> dict:
    rolling = load_yaml(Path(project) / "planning" / "rolling_plan.yml")
    if isinstance(rolling, dict):
        for block in rolling.get("chapters", []) or []:
            if isinstance(block, dict) and block.get("chapter") == chapter:
                return block
    return {}


def load_plan(project: Path, chapter: str) -> tuple[list[dict], list[str]]:
    """Load and validate chapters/chNNN/scene_plan.yml. Returns (scenes, errors)."""
    path = Path(project) / "chapters" / chapter / "scene_plan.yml"
    if not path.exists():
        return [], [f"NO_SCENE_PLAN: {path}"]
    data = load_yaml(path)
    scenes = data.get("scenes") if isinstance(data, dict) else None
    if not isinstance(scenes, list):
        return [], [f"SCENE_PLAN_MALFORMED: {path} has no scenes list."]
    errors: list[str] = []
    valid: list[dict] = []
    for i, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            errors.append(f"SCENE_PLAN_MALFORMED: {path} scene {i} is not a mapping.")
            continue
        problems = validate_scene_spec(scene)
        if problems:
            errors.extend(f"SCENE_SPEC: {path}[{i}]: {p}" for p in problems)
        else:
            valid.append(scene)
    return valid, errors


def _weave_pool(block: dict) -> list[str]:
    weave = block.get("narrative_weave") or block.get("叙事织入") or {}
    beats: list[str] = []
    if isinstance(weave, dict):
        for group in weave.values():
            if isinstance(group, list):
                beats.extend(str(b) for b in group)
    return beats


def draft_from_rolling(project: Path, chapter: str, pov: str = "主角") -> list[dict]:
    """Draft scene skeletons from the rolling_plan beat list. Fields needing
    creative judgment are left as TODO for the writer to fill."""
    block = _chapter_block(project, chapter)
    pressure = block.get("pressure_curve") or {}
    motion = str(pressure.get("chapter_internal_motion") or "")
    beats = [b.strip() for b in _ARROW.split(motion) if b.strip()]
    # Drop a trailing "未闭合..." note if present; it is a handoff, not a scene.
    beats = [b for b in beats if not b.startswith("未闭合")]
    if not beats:
        beats = ["TODO"]

    weave = _weave_pool(block)
    seed = ((block.get("architecture_role") or {}).get("writable_scene_seed")
            or block.get("writable_scene_seed") or "")

    scenes: list[dict] = []
    for i, beat in enumerate(beats, start=1):
        assigned = weave[(i - 1) % len(weave)] if weave else "TODO"
        scenes.append({
            "id": f"{chapter}_s{i}",
            "pov": pov,
            "location": "TODO",
            "emotional_temperature": {"from": "TODO", "to": "TODO"},
            "sensory_anchor": "TODO",
            "weave_beats": [assigned],
            "one_change": beat,
            "enters_via": "TODO",
            "exit_on": seed if (i == len(beats) and seed) else "TODO",
        })
    return scenes
