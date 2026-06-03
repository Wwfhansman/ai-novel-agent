"""Assemble the per-scene writing packet.

For each scene in a chapter's plan, bundle exactly what the writer needs to write
that one scene well — and nothing more:

  scene          the scene spec (experiential-first contract)
  entering_state  the engine-resolved state entering the chapter (shared)
  exemplars       target-voice passages retrieved for this scene's type
  prose_constraints  what to avoid (profile AI-tics) + the experiential rule

This is the operational form of the validated B method: small unit, concrete
spec, real exemplars, hard exit rule — handed over one scene at a time.
"""

from __future__ import annotations

from pathlib import Path

from ..context import entering_state
from ..events import load_project_events
from ..legacy import adapt_project
from ..profile import resolve_project_profile
from ..yamlio import load_yaml
from . import exemplars, plan


def _events_for(project: Path):
    events, _ = load_project_events(project)
    if events:
        return events
    legacy, _ = adapt_project(project)
    return legacy


def _chapter_function(project: Path, chapter: str) -> str | None:
    rolling = load_yaml(Path(project) / "planning" / "rolling_plan.yml")
    if isinstance(rolling, dict):
        for block in rolling.get("chapters", []) or []:
            if isinstance(block, dict) and block.get("chapter") == chapter:
                return block.get("chapter_function")
    return None


def _prose_constraints(profile: dict) -> list[str]:
    banned = (profile or {}).get("banned_patterns", {}) or {}
    avoid = [k for k in banned if k != "max_not_but_per_chapter"]
    constraints = ["场景是经历单位:先写够 pov/情绪/感官/织入,one_change 只是小料,可为空。",
                   "结尾切在外部动作,不切在'任务完成'。",
                   "新信息按 enters_via 进入,禁止主角脑内总结。"]
    if avoid:
        constraints.append("避免句式: " + ", ".join(avoid))
    return constraints


def build_scene_packets(project: Path, chapter: str) -> tuple[list[dict], list[str]]:
    """Return (packets, notes). Uses chapters/chNNN/scene_plan.yml if present,
    else drafts a skeleton from the rolling_plan."""
    project = Path(project)
    notes: list[str] = []

    scenes, errors = plan.load_plan(project, chapter)
    if not scenes:
        scenes = plan.draft_from_rolling(project, chapter)
        notes.append("scene_plan.yml not found; drafted a skeleton from rolling_plan (fill the TODOs).")
    elif errors:
        notes.extend(errors)

    es = entering_state(_events_for(project), chapter)
    profile = resolve_project_profile(project)
    chapter_function = _chapter_function(project, chapter)
    constraints = _prose_constraints(profile)

    packets: list[dict] = []
    for scene in scenes:
        scene_type = scene.get("scene_type") or chapter_function
        packets.append({
            "scene": scene,
            "entering_state": es,
            "exemplars": exemplars.retrieve(project, scene_type, k=3),
            "prose_constraints": constraints,
        })
    return packets, notes
