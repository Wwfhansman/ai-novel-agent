"""Compile the bounded entering-state a writer needs for a chapter.

This is the bridge from the consistency engine to the creative layer. Instead of
asking the writer to read and understand the whole book, the engine projects
state through the previous chapter and hands over a compact, pre-resolved
"here is where things stand" pack: live characters, open debts (flagged when
overdue), unpaid foreshadowing, knowledge visibility, recent facts.

Its size is bounded by the *current state*, not by book length — which is the
property that makes long-form writing tractable.
"""

from __future__ import annotations

from .events import Event, chapter_sort_key
from .ledger_health import _window_end_chapter
from .projection import project_through


def entering_state(events: list[Event], chapter: str, *, recent: int = 5) -> dict:
    chapter_no = chapter_sort_key(chapter)
    state = project_through(events, chapter_no - 1)

    characters = {}
    for cid, char in state.characters.items():
        characters[cid] = {
            "name": char.get("name", cid),
            "role": char.get("role"),
            "current_goal": char.get("current_goal"),
            "current_stance": char.get("current_stance"),
            "intent": char.get("intent"),
            "relationships": char.get("relationships", {}),
            "last_seen": char.get("last_seen"),
        }

    open_debts = []
    for did, debt in sorted(state.debts.items()):
        if debt.get("status") == "paid":
            continue
        end = _window_end_chapter(debt.get("payoff_window"))
        open_debts.append({
            "id": did,
            "description": debt.get("description"),
            "urgency": debt.get("urgency"),
            "payoff_window": debt.get("payoff_window"),
            "overdue": end is not None and chapter_no > end,
        })

    live_foreshadowing = [
        {"id": fid, "content": fore.get("content"), "status": fore.get("status")}
        for fid, fore in sorted(state.foreshadowing.items())
        if fore.get("status") != "paid"
    ]

    knowledge = {
        topic: {h: lvl for h, lvl in vis.items() if h != "_meta"}
        for topic, vis in state.knowledge.items()
    }

    return {
        "entering_chapter": chapter,
        "characters": characters,
        "open_debts": open_debts,
        "live_foreshadowing": live_foreshadowing,
        "knowledge": knowledge,
        "recent_facts": [f["text"] for f in state.facts[-recent:]],
        "recent_world_state": [w["text"] for w in state.world_state[-recent:]],
    }
