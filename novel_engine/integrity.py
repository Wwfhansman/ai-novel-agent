"""Referential and temporal integrity checks over the event log.

These run on the ordered events (not just the projected state), because the
class of bugs they catch is fundamentally about *order*: paying a debt that was
never opened, revealing knowledge to a character who has not been introduced,
changing a character who does not exist. None of this is expressible as a regex
over YAML; it requires folding the log.

`known_*` seeds let the shadow/migration tooling declare entities that were
introduced at bootstrap (outside the event log) so legacy data is not falsely
flagged.
"""

from __future__ import annotations

from .events import Event

# Holders that are valid knowledge targets without being character entities.
NON_CHARACTER_HOLDERS = {"reader", "public", "audience", "读者", "公众"}


def check_integrity(
    events: list[Event],
    known_characters: set[str] | None = None,
    known_debts: set[str] | None = None,
    known_foreshadowing: set[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Return (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    characters: set[str] = set(known_characters or set())
    debt_status: dict[str, str] = {debt: "open" for debt in (known_debts or set())}
    foreshadow_status: dict[str, str] = {fid: "planted" for fid in (known_foreshadowing or set())}
    entities: dict[str, set[str]] = {"faction": set(), "location": set(), "power": set()}

    def loc(event: Event) -> str:
        return f"{event.chapter} ({event.source})"

    for event in events:
        kind = event.kind
        d = event.data

        if kind == "character_introduced":
            if d["id"] in characters:
                warnings.append(f"DUPLICATE_INTRODUCTION: {loc(event)} re-introduces character {d['id']}.")
            characters.add(d["id"])

        elif kind == "character_changed":
            if d["id"] not in characters:
                errors.append(
                    f"UNKNOWN_CHARACTER: {loc(event)} changes {d['id']} before it was introduced."
                )

        elif kind == "relationship_changed":
            for who in (d["a"], d["b"]):
                if who not in characters:
                    errors.append(
                        f"UNKNOWN_CHARACTER: {loc(event)} sets a relationship for {who} before it was introduced."
                    )

        elif kind in ("faction_introduced", "location_introduced", "power_introduced"):
            entities[kind.split("_")[0]].add(d["id"])

        elif kind in ("faction_changed", "location_changed", "power_changed"):
            etype = kind.split("_")[0]
            if d["id"] not in entities[etype]:
                errors.append(f"UNKNOWN_{etype.upper()}: {loc(event)} changes {etype} {d['id']} before it was introduced.")

        elif kind == "knowledge_changed":
            holder = d["holder"]
            if holder not in characters and holder not in NON_CHARACTER_HOLDERS:
                errors.append(
                    f"UNKNOWN_KNOWLEDGE_HOLDER: {loc(event)} sets knowledge for {holder!r}, "
                    "which is neither an introduced character nor a known non-character holder "
                    f"({', '.join(sorted(NON_CHARACTER_HOLDERS))})."
                )

        elif kind == "item_moved":
            to = d["to"]
            if to not in characters and to not in NON_CHARACTER_HOLDERS:
                warnings.append(
                    f"ITEM_HOLDER_UNVERIFIED: {loc(event)} moves item {d['item']!r} to {to!r}, "
                    "which is not an introduced character (may be a faction/location)."
                )

        elif kind == "debt_opened":
            if debt_status.get(d["id"]) in ("open", "advanced"):
                warnings.append(f"DEBT_REOPENED: {loc(event)} opens debt {d['id']} which is already open.")
            debt_status[d["id"]] = "open"

        elif kind in ("debt_advanced", "debt_paid"):
            status = debt_status.get(d["id"])
            if status is None:
                errors.append(
                    f"UNKNOWN_DEBT: {loc(event)} {kind.replace('_', 's ')} {d['id']} which was never opened."
                )
            elif status == "paid":
                warnings.append(f"DEBT_TOUCHED_AFTER_PAID: {loc(event)} {kind} on already-paid debt {d['id']}.")
            debt_status[d["id"]] = "paid" if kind == "debt_paid" else "advanced"

        elif kind == "foreshadow_planted":
            if foreshadow_status.get(d["id"]) is not None:
                warnings.append(f"FORESHADOW_REPLANTED: {loc(event)} replants foreshadow {d['id']}.")
            foreshadow_status[d["id"]] = "planted"

        elif kind in ("foreshadow_advanced", "foreshadow_paid"):
            status = foreshadow_status.get(d["id"])
            if status is None:
                errors.append(
                    f"UNKNOWN_FORESHADOW: {loc(event)} {kind} {d['id']} which was never planted."
                )
            elif status == "paid":
                warnings.append(f"FORESHADOW_TOUCHED_AFTER_PAID: {loc(event)} {kind} on already-paid {d['id']}.")
            foreshadow_status[d["id"]] = "paid" if kind == "foreshadow_paid" else "advanced"

    return errors, warnings
