"""Project the event log into current state.

This is the reducer. Given events in chapter order, it folds them into the
current authoritative state. Because state is *derived*, it can never silently
disagree with the event log — the class of "canon_delta says X but entities/ says
Y" drift becomes impossible by construction.

State shape (all dict-of-id for stable diffing):

    characters[id]  = {id, name, role, fixed_profile, current_goal, current_stance,
                       intent, relationships{other: state}, last_seen, last_updated,
                       change_history[{chapter, change}]}
    debts[id]       = {id, status, description, type, urgency, payoff_window,
                       opened_in, last_touched, history[{chapter, action, note}]}
    foreshadowing[id] = {id, status, content, planted_in, last_touched, history[...]}
    knowledge[topic][holder] = level   (+ knowledge_meta[topic] = {last_updated})
    items[item]     = {holder, last_moved}
    facts           = [{chapter, text}]
    world_state     = [{chapter, text}]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .events import Event


@dataclass
class State:
    characters: dict[str, dict] = field(default_factory=dict)
    factions: dict[str, dict] = field(default_factory=dict)
    locations: dict[str, dict] = field(default_factory=dict)
    power: dict[str, dict] = field(default_factory=dict)
    debts: dict[str, dict] = field(default_factory=dict)
    foreshadowing: dict[str, dict] = field(default_factory=dict)
    knowledge: dict[str, dict] = field(default_factory=dict)
    items: dict[str, dict] = field(default_factory=dict)
    facts: list[dict] = field(default_factory=list)
    world_state: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "characters": self.characters,
            "factions": self.factions,
            "locations": self.locations,
            "power": self.power,
            "debts": self.debts,
            "foreshadowing": self.foreshadowing,
            "knowledge": self.knowledge,
            "items": self.items,
            "facts": self.facts,
            "world_state": self.world_state,
        }


# Generic entity (faction/location/power) introduce/change reducers.
def _entity_introduce(store: dict, d: dict, chapter: str, attrs: tuple[str, ...]) -> None:
    entry = store.setdefault(d["id"], {"id": d["id"], "change_history": []})
    for key in ("name", *attrs):
        if key in d:
            entry[key] = d[key]
    entry.setdefault("introduced_in", chapter)
    entry["last_updated"] = chapter


def _entity_change(store: dict, d: dict, chapter: str) -> None:
    entry = store.setdefault(d["id"], {"id": d["id"], "change_history": []})
    entry.setdefault("change_history", []).append({"chapter": chapter, "change": d["change"]})
    for key, value in (d.get("set") or {}).items():
        entry[key] = value
    entry["last_updated"] = chapter


def _touch_character(state: State, char_id: str, chapter: str) -> dict:
    entry = state.characters.setdefault(
        char_id,
        {
            "id": char_id,
            "relationships": {},
            "change_history": [],
        },
    )
    entry["last_updated"] = chapter
    return entry


def _apply(state: State, event: Event) -> None:
    kind = event.kind
    chapter = event.chapter
    d = event.data

    if kind == "fact_added":
        state.facts.append({"chapter": chapter, "text": d["text"]})

    elif kind == "world_state_changed":
        state.world_state.append({"chapter": chapter, "text": d["text"]})

    elif kind == "character_introduced":
        entry = _touch_character(state, d["id"], chapter)
        for key in ("name", "role", "fixed_profile", "current_goal", "current_stance", "intent"):
            if key in d:
                entry[key] = d[key]
        entry["introduced_in"] = entry.get("introduced_in", chapter)
        entry["last_seen"] = chapter

    elif kind == "character_changed":
        entry = _touch_character(state, d["id"], chapter)
        entry["change_history"].append({"chapter": chapter, "change": d["change"]})
        entry["last_seen"] = d.get("last_seen", chapter)
        for key, value in (d.get("set") or {}).items():
            entry[key] = value

    elif kind == "relationship_changed":
        a = _touch_character(state, d["a"], chapter)
        b = _touch_character(state, d["b"], chapter)
        a.setdefault("relationships", {})[d["b"]] = d["to"]
        b.setdefault("relationships", {})[d["a"]] = d["to"]

    elif kind == "knowledge_changed":
        topic = d["topic"]
        vis = state.knowledge.setdefault(topic, {})
        vis[d["holder"]] = d["level"]
        vis.setdefault("_meta", {})["last_updated"] = chapter

    elif kind == "faction_introduced":
        _entity_introduce(state.factions, d, chapter, ("scale", "goal", "attitude_to_protagonist", "resources", "current_action"))
    elif kind == "faction_changed":
        _entity_change(state.factions, d, chapter)

    elif kind == "location_introduced":
        _entity_introduce(state.locations, d, chapter, ("scale", "controlled_by", "texture", "function"))
    elif kind == "location_changed":
        _entity_change(state.locations, d, chapter)

    elif kind == "power_introduced":
        _entity_introduce(state.power, d, chapter, ("stage_meaning", "cost", "test_method"))
    elif kind == "power_changed":
        _entity_change(state.power, d, chapter)

    elif kind == "item_introduced":
        entry = state.items.setdefault(d["id"], {"id": d["id"]})
        entry["name"] = d.get("name", d["id"])
        if d.get("holder"):
            entry["holder"] = d["holder"]
        entry["introduced_in"] = entry.get("introduced_in", chapter)

    elif kind == "item_moved":
        state.items[d["item"]] = {"holder": d["to"], "last_moved": chapter}

    elif kind == "debt_opened":
        existing = state.debts.get(d["id"])
        if existing is None:
            state.debts[d["id"]] = {
                "id": d["id"],
                "status": "open",
                "description": d.get("description", ""),
                "type": d.get("type"),
                "urgency": d.get("urgency"),
                "payoff_window": d.get("payoff_window"),
                "opened_in": chapter,
                "last_touched": chapter,
                "history": [{"chapter": chapter, "action": "opened"}],
            }
        else:
            # Re-emitted open (common when migrating legacy double-records):
            # preserve lineage, fill only fields the existing entry lacks.
            for key in ("description", "type", "urgency", "payoff_window"):
                if d.get(key) and not existing.get(key):
                    existing[key] = d[key]
            existing["last_touched"] = chapter
            existing["history"].append({"chapter": chapter, "action": "reopened"})

    elif kind in ("debt_advanced", "debt_paid"):
        entry = state.debts.get(d["id"])
        if entry is not None:
            action = "advanced" if kind == "debt_advanced" else "paid"
            entry["status"] = "advanced" if kind == "debt_advanced" else "paid"
            entry["last_touched"] = chapter
            entry["history"].append({"chapter": chapter, "action": action, "note": d.get("note")})

    elif kind == "foreshadow_planted":
        existing = state.foreshadowing.get(d["id"])
        if existing is None:
            state.foreshadowing[d["id"]] = {
                "id": d["id"],
                "status": "planted",
                "content": d.get("content", ""),
                "planted_in": chapter,
                "last_touched": chapter,
                "history": [{"chapter": chapter, "action": "planted"}],
            }
        else:
            if d.get("content") and not existing.get("content"):
                existing["content"] = d["content"]
            existing["last_touched"] = chapter
            existing["history"].append({"chapter": chapter, "action": "replanted"})

    elif kind in ("foreshadow_advanced", "foreshadow_paid"):
        entry = state.foreshadowing.get(d["id"])
        if entry is not None:
            action = "advanced" if kind == "foreshadow_advanced" else "paid"
            entry["status"] = action
            entry["last_touched"] = chapter
            entry["history"].append({"chapter": chapter, "action": action, "note": d.get("note")})

    elif kind == "note":
        # Free-text narrative change: attach to the named scope if it is a known
        # character, else keep as a global note. Never promoted to machine state.
        scope = d.get("scope")
        note = {"chapter": chapter, "text": d["text"]}
        if scope and scope in state.characters:
            state.characters[scope].setdefault("notes", []).append(note)
        else:
            state.facts.append({"chapter": chapter, "text": d["text"], "note": True})


def project(events: list[Event]) -> State:
    """Fold events (already in chapter order) into current state."""
    state = State()
    for event in events:
        _apply(state, event)
    return state


def project_through(events: list[Event], through_chapter_no: int) -> State:
    """Project only events at or before a chapter number.

    Used to compute the state a writer is *entering* a chapter with: project
    everything strictly before the chapter being written. bootstrap events
    (chapter_sort_key -1) are always included.
    """
    from .events import chapter_sort_key

    selected = [e for e in events if chapter_sort_key(e.chapter) <= through_chapter_no]
    return project(selected)
