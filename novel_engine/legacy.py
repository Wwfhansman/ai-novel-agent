"""Best-effort adapter: legacy chapters/chXXX/canon_delta.yml -> events.

This exists for migration only. It lets the reducer run on a project that still
uses the old hand-written canon_delta format, so the shadow tool can measure how
much the legacy hand-maintained entities/ledgers drift from what the deltas
actually imply. It is deliberately conservative: fields the old format cannot
express faithfully (e.g. knowledge holder/level) are emitted as notes rather
than fabricated typed events.
"""

from __future__ import annotations

import re
from pathlib import Path

from .events import Event, chapter_sort_key
from .yamlio import load_yaml

_PAIR_SPLIT = re.compile(r"\s*(?:<->|<>|＜＞|->|→|与|和)\s*")


def _as_list(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _seed_known_ids(project: Path) -> tuple[set[str], set[str], set[str]]:
    characters: set[str] = set()
    chars = load_yaml(project / "entities" / "characters.yml")
    if isinstance(chars, dict) and isinstance(chars.get("characters"), list):
        for item in chars["characters"]:
            if isinstance(item, dict):
                for key in ("id", "name"):
                    if item.get(key):
                        characters.add(str(item[key]))

    debts: set[str] = set()
    debt_data = load_yaml(project / "ledgers" / "narrative_debts.yml")
    if isinstance(debt_data, dict):
        for item in _as_list(debt_data.get("debts")):
            if isinstance(item, dict) and item.get("id"):
                debts.add(str(item["id"]))

    foreshadowing: set[str] = set()
    fore_data = load_yaml(project / "ledgers" / "foreshadowing.yml")
    if isinstance(fore_data, dict):
        key = "foreshadowing" if "foreshadowing" in fore_data else "items"
        for item in _as_list(fore_data.get(key)):
            if isinstance(item, dict) and item.get("id"):
                foreshadowing.add(str(item["id"]))

    return characters, debts, foreshadowing


def _delta_to_events(chapter: str, delta: dict, source: str, rel_as_note: bool = False) -> list[Event]:
    """Convert one legacy canon_delta dict to events.

    rel_as_note: emit relationship changes as notes instead of relationship_changed.
    The old format stores a display-name pair (not stable ids), so relationship
    events cannot pass referential integrity. The shadow tool keeps them typed to
    *count* them; migration emits notes so the produced log validates cleanly.
    """
    events: list[Event] = []

    def emit(kind: str, **data):
        data["kind"] = kind
        data["chapter"] = chapter
        events.append(Event(kind=kind, chapter=chapter, data=data, source=source))

    for text in _as_list(delta.get("new_facts")):
        emit("fact_added", text=str(text))

    for change in _as_list(delta.get("character_changes")):
        if isinstance(change, dict):
            cid = change.get("character") or change.get("name") or change.get("id")
            if cid:
                emit("character_changed", id=str(cid), change=str(change.get("change") or change.get("description") or ""))

    for change in _as_list(delta.get("relationship_changes")):
        if isinstance(change, dict) and change.get("pair"):
            if rel_as_note:
                emit("note", scope="relationship", text=f"{change['pair']}: {change.get('change')}")
                continue
            parts = [p for p in _PAIR_SPLIT.split(str(change["pair"])) if p.strip()]
            if len(parts) >= 2:
                emit("relationship_changed", a=parts[0].strip(), b=parts[1].strip(), to=str(change.get("change") or ""))

    for text in _as_list(delta.get("world_state_changes")):
        emit("world_state_changed", text=str(text))

    # Old knowledge_changes lack holder/level; preserve as a note instead of guessing.
    for change in _as_list(delta.get("knowledge_changes")):
        if isinstance(change, dict):
            emit("note", scope="knowledge", text=f"{change.get('topic')}: {change.get('change')}")

    for item in _as_list(delta.get("foreshadowing_added")):
        if isinstance(item, dict) and item.get("id"):
            emit("foreshadow_planted", id=str(item["id"]), content=str(item.get("content") or ""))
    for item in _as_list(delta.get("foreshadowing_advanced")):
        if isinstance(item, dict) and item.get("id"):
            emit("foreshadow_advanced", id=str(item["id"]))
    for item in _as_list(delta.get("foreshadowing_paid")):
        if isinstance(item, dict) and item.get("id"):
            emit("foreshadow_paid", id=str(item["id"]))

    for item in _as_list(delta.get("narrative_debts_added")):
        if isinstance(item, dict) and item.get("id"):
            emit("debt_opened", id=str(item["id"]), description=str(item.get("description") or ""))
    for item in _as_list(delta.get("narrative_debts_advanced")):
        if isinstance(item, dict) and item.get("id"):
            emit("debt_advanced", id=str(item["id"]))
    for item in _as_list(delta.get("narrative_debts_paid")):
        if isinstance(item, dict) and item.get("id"):
            emit("debt_paid", id=str(item["id"]))

    return events


def adapt_project(project: Path) -> tuple[list[Event], dict[str, set[str]]]:
    """Return (events_in_chapter_order, seed_known_ids)."""
    project = Path(project)
    chapter_root = project / "chapters"
    events: list[Event] = []
    if chapter_root.exists():
        chapter_dirs = sorted(
            (p for p in chapter_root.glob("ch*") if p.is_dir()),
            key=lambda p: chapter_sort_key(p.name),
        )
        for chapter_dir in chapter_dirs:
            delta_path = chapter_dir / "canon_delta.yml"
            delta = load_yaml(delta_path)
            if isinstance(delta, dict):
                events.extend(_delta_to_events(chapter_dir.name, delta, f"legacy:{delta_path.name}"))

    chars, debts, fore = _seed_known_ids(project)
    return events, {"characters": chars, "debts": debts, "foreshadowing": fore}
