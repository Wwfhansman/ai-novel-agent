"""Shadow diff: derived state vs hand-written entities/ledgers.

This is the zero-risk first migration step. It reconstructs state from the
(legacy-adapted) event log and compares it against the hand-maintained
entities/ledgers files. It changes nothing; it produces a number: how much the
hand-written current state disagrees with what the chapter deltas actually
imply. A high number is the argument for switching entities/ledgers to derived
projections.

Reconciliation is scoped to what the legacy format can express faithfully:
character change history, debt lifecycle, foreshadow lifecycle. Relationship and
knowledge deltas are reported as informational (the old format omits the
holder/level/identity needed to reconcile them).
"""

from __future__ import annotations

from pathlib import Path

from .legacy import adapt_project
from .projection import project as project_state
from .yamlio import load_yaml


def _hand_characters(project: Path) -> dict[str, dict]:
    data = load_yaml(project / "entities" / "characters.yml")
    out: dict[str, dict] = {}
    if isinstance(data, dict) and isinstance(data.get("characters"), list):
        for item in data["characters"]:
            if isinstance(item, dict) and item.get("id"):
                out[str(item["id"])] = item
    return out


def _hand_ledger_ids(project: Path, filename: str, key: str) -> dict[str, dict]:
    data = load_yaml(project / "ledgers" / filename)
    out: dict[str, dict] = {}
    if isinstance(data, dict):
        items = data.get(key)
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict) and item.get("id"):
                    out[str(item["id"])] = item
    return out


def _change_set(history) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    if isinstance(history, list):
        for item in history:
            if isinstance(item, dict):
                pairs.add((str(item.get("chapter") or ""), str(item.get("change") or "")))
    return pairs


def shadow_report(project: Path) -> dict:
    project = Path(project)
    events, _seeds = adapt_project(project)
    derived = project_state(events)

    report: dict = {
        "project": project.name,
        "event_count": len(events),
        "drift": [],
        "unmerged": [],
        "informational": [],
        "summary": {},
    }

    # --- Characters: derived change history vs hand-written ---
    hand_chars = _hand_characters(project)
    for cid, dchar in derived.characters.items():
        if cid not in hand_chars:
            # derived entity with no hand-written counterpart (often a legacy
            # relationship delta that used a display name or a faction).
            if dchar.get("change_history"):
                report["informational"].append(
                    f"DERIVED_ONLY_ENTITY: events reference {cid!r} but entities/characters.yml has no such id "
                    "(legacy relationship deltas use display names / non-character targets)."
                )
            continue
        derived_changes = _change_set(dchar.get("change_history"))
        hand_changes = _change_set(hand_chars[cid].get("change_history"))
        for chapter, change in sorted(derived_changes - hand_changes):
            report["unmerged"].append(
                f"CHARACTER_CHANGE_NOT_IN_ENTITY: {cid} {chapter} delta change "
                f"is absent from entities/characters.yml change_history: {change!r}"
            )
        for chapter, change in sorted(hand_changes - derived_changes):
            report["drift"].append(
                f"ENTITY_CHANGE_WITHOUT_DELTA: {cid} change_history has {chapter} entry "
                f"with no matching canon_delta change: {change!r}"
            )

    # --- Debts: derived status vs ledger ---
    hand_debts = _hand_ledger_ids(project, "narrative_debts.yml", "debts")
    for did, ddebt in derived.debts.items():
        if did not in hand_debts:
            report["unmerged"].append(
                f"DEBT_NOT_IN_LEDGER: events open/advance debt {did} but ledgers/narrative_debts.yml has no entry."
            )
            continue
        hand_status = str(hand_debts[did].get("status") or "open")
        derived_status = "paid" if ddebt.get("status") == "paid" else "open"
        if hand_status == "paid" and derived_status != "paid":
            report["drift"].append(
                f"DEBT_STATUS_DRIFT: ledger marks {did} paid but events never paid it."
            )
        if derived_status == "paid" and hand_status != "paid":
            report["drift"].append(
                f"DEBT_STATUS_DRIFT: events paid {did} but ledger still marks it {hand_status}."
            )
        opened_in = ddebt.get("opened_in")
        created_in = str(hand_debts[did].get("created_in") or "")
        if opened_in and created_in and created_in != opened_in and created_in != "bootstrap":
            report["informational"].append(
                f"DEBT_ORIGIN_MISMATCH: {did} opened by event in {opened_in}, ledger says created_in={created_in}."
            )

    # --- Foreshadowing: derived status vs ledger ---
    hand_fore = _hand_ledger_ids(project, "foreshadowing.yml", "foreshadowing")
    if not hand_fore:
        hand_fore = _hand_ledger_ids(project, "foreshadowing.yml", "items")
    for fid, dfore in derived.foreshadowing.items():
        if fid not in hand_fore:
            report["unmerged"].append(
                f"FORESHADOW_NOT_IN_LEDGER: events plant/touch {fid} but ledgers/foreshadowing.yml has no entry."
            )

    # --- Knowledge/relationship: informational only ---
    rel_notes = sum(1 for e in events if e.kind == "relationship_changed")
    know_notes = sum(1 for e in events if e.kind == "note" and e.get("scope") == "knowledge")
    if rel_notes:
        report["informational"].append(
            f"LEGACY_RELATIONSHIP_DELTAS: {rel_notes} relationship change(s) cannot be reconciled "
            "(old format stores a display-name pair, not stable ids)."
        )
    if know_notes:
        report["informational"].append(
            f"LEGACY_KNOWLEDGE_DELTAS: {know_notes} knowledge change(s) cannot be reconciled "
            "(old format omits holder + visibility level)."
        )

    report["summary"] = {
        "drift": len(report["drift"]),
        "unmerged": len(report["unmerged"]),
        "informational": len(report["informational"]),
    }
    return report


def format_report(report: dict) -> str:
    lines = [
        f"Shadow diff for {report['project']} ({report['event_count']} adapted events)",
        f"  drift:         {report['summary']['drift']}  (hand-written state disagrees with the event log)",
        f"  unmerged:      {report['summary']['unmerged']}  (deltas not reflected in current state)",
        f"  informational: {report['summary']['informational']}  (legacy format too loose to reconcile)",
        "",
    ]
    for bucket in ("drift", "unmerged", "informational"):
        if report[bucket]:
            lines.append(f"[{bucket}]")
            lines.extend(f"  - {item}" for item in report[bucket])
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"
