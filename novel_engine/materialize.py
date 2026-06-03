"""Render projected state into the canonical entities/ledgers file format.

This is the keystone that lets entities/ledgers stop being hand-maintained: once
state is *materialized* from the event log, the class of drift the shadow tool
finds (e.g. a foreshadow planted in a delta but never copied into the ledger)
cannot exist — the file is generated, not edited.

By default it writes to <project>/derived/ so it never clobbers hand-written
files during migration review. Use in_place=True only after you have decided to
flip the project to derived state.
"""

from __future__ import annotations

from pathlib import Path

from .projection import State
from .yamlio import dump_yaml


def materialize(state: State) -> dict[str, dict]:
    """Return {relative_path: data} for the derivable current-state files."""
    characters = []
    for cid, char in state.characters.items():
        rels = [{"target": other, "state": rel} for other, rel in (char.get("relationships") or {}).items()]
        entry = {
            "id": cid,
            "name": char.get("name", cid),
        }
        for key in ("role", "fixed_profile", "current_goal", "current_stance", "intent"):
            if char.get(key) is not None:
                entry[key] = char[key]
        if rels:
            entry["relationships"] = rels
        if char.get("last_seen"):
            entry["last_seen"] = char["last_seen"]
        if char.get("last_updated"):
            entry["last_updated"] = char["last_updated"]
        if char.get("change_history"):
            entry["change_history"] = char["change_history"]
        if char.get("notes"):
            entry["notes"] = char["notes"]
        characters.append(entry)

    debts = []
    for did, debt in state.debts.items():
        entry = {"id": did, "status": debt.get("status", "open"), "description": debt.get("description", "")}
        for key in ("type", "urgency", "payoff_window", "opened_in", "last_touched"):
            if debt.get(key) is not None:
                entry[key] = debt[key]
        debts.append(entry)

    foreshadowing = []
    for fid, fore in state.foreshadowing.items():
        foreshadowing.append({
            "id": fid,
            "status": fore.get("status", "planted"),
            "content": fore.get("content", ""),
            "planted_in": fore.get("planted_in"),
            "last_touched": fore.get("last_touched"),
        })

    knowledge_items = []
    for topic, vis in state.knowledge.items():
        visibility = {holder: level for holder, level in vis.items() if holder != "_meta"}
        entry = {"id": topic, "visibility": visibility}
        meta = vis.get("_meta") or {}
        if meta.get("last_updated"):
            entry["last_updated"] = meta["last_updated"]
        knowledge_items.append(entry)

    return {
        "entities/characters.yml": {"characters": characters},
        "ledgers/narrative_debts.yml": {"debts": debts},
        "ledgers/foreshadowing.yml": {"foreshadowing": foreshadowing},
        "ledgers/knowledge_state.yml": {"knowledge_items": knowledge_items},
    }


def write_materialized(state: State, project: Path, *, in_place: bool = False) -> list[Path]:
    """Write derived state files. Returns the paths written."""
    project = Path(project)
    base = project if in_place else project / "derived"
    written: list[Path] = []
    for rel, data in materialize(state).items():
        target = base / rel
        dump_yaml(target, data)
        written.append(target)
    return written
