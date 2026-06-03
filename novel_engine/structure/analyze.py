"""Analyze structural records for read-pull and anti-shrink problems.

All checks are computed over the record sequence (and, for arc-stall, the event
log), with thresholds from the profile. This is the positive, typed replacement
for the legacy regex checks spread across cross_chapter.py and planning_audit.py.
"""

from __future__ import annotations

from ..events import Event, chapter_sort_key
from .chapter_meta import ChapterMeta


def _max_consecutive_run(values: list, predicate=None) -> tuple[int, object]:
    """Longest run of equal (or predicate-true) consecutive values; returns (length, value)."""
    best_len, best_val = 0, None
    run_len, run_val = 0, object()
    for value in values:
        key = predicate(value) if predicate else value
        if key == run_val and key is not None:
            run_len += 1
        else:
            run_val, run_len = key, 1
        if run_len > best_len:
            best_len, best_val = run_len, run_val
    return best_len, best_val


def _consecutive_true_run(flags: list[bool]) -> int:
    best = run = 0
    for flag in flags:
        run = run + 1 if flag else 0
        best = max(best, run)
    return best


def analyze(records: list[ChapterMeta], profile: dict, events: list[Event] | None = None) -> dict:
    cfg = (profile or {}).get("structure", {}) or {}
    warnings: list[str] = []
    records = sorted(records, key=lambda r: r.sort_key)
    chapters = [r.chapter for r in records]

    # 1. Pacing / function monotony (chapter-shape repetition).
    pacing = [r.pacing_mode for r in records]
    run, val = _max_consecutive_run(pacing)
    if val and run >= cfg.get("max_consecutive_same_pacing", 3):
        warnings.append(f"PACING_LOOP: {run} consecutive chapters with pacing_mode={val}. Vary the rhythm budget.")

    funcs = [r.chapter_function for r in records]
    run, val = _max_consecutive_run(funcs)
    if val and run >= cfg.get("max_consecutive_same_function", 3):
        warnings.append(f"FUNCTION_LOOP: {run} consecutive chapters with chapter_function={val}. Vary chapter shape.")

    # 2. World-aliveness drought (anti-shrink).
    no_world = [not r.world_expansion for r in records]
    drought = _consecutive_true_run(no_world)
    if drought >= cfg.get("world_expansion_drought", 3):
        warnings.append(
            f"WORLD_EXPANSION_DROUGHT: {drought} consecutive chapters with no world_expansion. "
            "Risk: the world is shrinking into a protagonist task chain. Run the architect/world pass."
        )
    no_offscreen = [not r.offscreen_pressure for r in records]
    off_drought = _consecutive_true_run(no_offscreen)
    if off_drought >= cfg.get("offscreen_drought", 4):
        warnings.append(
            f"OFFSCREEN_PRESSURE_DROUGHT: {off_drought} consecutive chapters with no off-screen pressure. "
            "Simulate what factions/rivals do when the protagonist does nothing."
        )

    # 3. Tension flatline (read-pull).
    flat_positions = {p.lower() for p in cfg.get("flat_positions", ["opening", "aftermath_trough"])}
    flat_flags = [(r.position_in_flow or "").lower() in flat_positions for r in records]
    flat_run = _consecutive_true_run(flat_flags)
    if flat_run >= cfg.get("flat_position_run", 3):
        warnings.append(
            f"TENSION_FLATLINE: {flat_run} consecutive chapters sit at low-tension positions "
            f"({'/'.join(sorted(flat_positions))}). Verify the flow is actually escalating."
        )

    # 4. Growth density (anti power-creep).
    growth_chapters = [r.chapter for r in records if r.protagonist_growth]
    growth_cap = max(cfg.get("growth_density_max", 2), len(records) // 3)
    if len(growth_chapters) > growth_cap:
        warnings.append(
            f"GROWTH_TOO_DENSE: {len(growth_chapters)} growth chapters ({', '.join(growth_chapters[:8])}) "
            f"exceed budget {growth_cap}. Check the growth budget before drafting."
        )

    # 5. Arc stall (from events): a main character untouched for too long.
    arc_warnings: list[str] = []
    if events:
        arc_warnings = _arc_stall(records, events, cfg)
        warnings.extend(arc_warnings)

    # Tension curve for display.
    tension_curve = [
        {"chapter": r.chapter, "position_in_flow": r.position_in_flow, "tension": r.tension}
        for r in records
    ]

    return {
        "chapters": chapters,
        "tension_curve": tension_curve,
        "growth_chapters": growth_chapters,
        "warnings": warnings,
    }


def _arc_stall(records: list[ChapterMeta], events: list[Event], cfg: dict) -> list[str]:
    arc_roles = {str(r).lower() for r in cfg.get("arc_roles", ["protagonist", "antagonist"])}
    stall_after = cfg.get("arc_stall_chapters", 8)

    current_no = max((r.sort_key for r in records), default=0)
    current_no = max([current_no] + [chapter_sort_key(e.chapter) for e in events])

    roles: dict[str, str] = {}
    last_change: dict[str, int] = {}
    for event in events:
        d = event.data
        if event.kind == "character_introduced":
            roles[d["id"]] = str(d.get("role") or "").lower()
            last_change.setdefault(d["id"], chapter_sort_key(event.chapter))
        elif event.kind == "character_changed":
            last_change[d["id"]] = chapter_sort_key(event.chapter)

    warnings: list[str] = []
    for cid, role in roles.items():
        if role not in arc_roles:
            continue
        last = last_change.get(cid, -1)
        if last >= 0 and current_no - last >= stall_after:
            warnings.append(
                f"ARC_STALL: {cid} (role={role}) has not changed since ch{last:03d}; "
                f"{current_no - last} chapters of arc silence at ch{current_no:03d}."
            )
    return warnings
