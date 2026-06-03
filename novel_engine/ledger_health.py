"""Computed ledger health: are setups paying off on time?

This is the first seed of the structure engine. Because debts and foreshadowing
are projected from the event log with their opened/planted chapters, "this debt
blew past its promised payoff window" and "this foreshadow has been dangling for
N chapters untouched" become *computed* facts, not things a human must remember
to check.

Thresholds come from a profile so the engine stays genre/language neutral.
"""

from __future__ import annotations

import re

from .projection import State

_WINDOW_END_RE = re.compile(r"ch(\d+)\s*$")
_WINDOW_ANY_RE = re.compile(r"ch(\d+)")


def _window_end_chapter(window: str | None) -> int | None:
    """Parse the last numeric chapter from a payoff window like 'ch002-ch004'."""
    if not window or not isinstance(window, str):
        return None
    end = _WINDOW_END_RE.search(window.strip())
    if end:
        return int(end.group(1))
    matches = _WINDOW_ANY_RE.findall(window)
    return int(matches[-1]) if matches else None


def check_ledger_health(
    state: State,
    current_chapter_no: int,
    *,
    foreshadow_stale_after: int = 12,
    debt_overdue_grace: int = 0,
) -> list[str]:
    """Return warnings about overdue debts and stale foreshadowing."""
    warnings: list[str] = []

    for debt_id, debt in sorted(state.debts.items()):
        if debt.get("status") == "paid":
            continue
        end = _window_end_chapter(debt.get("payoff_window"))
        if end is not None and current_chapter_no > end + debt_overdue_grace:
            warnings.append(
                f"DEBT_OVERDUE: {debt_id} (urgency={debt.get('urgency')}) promised payoff by "
                f"{debt.get('payoff_window')} but is still {debt.get('status')} at ch{current_chapter_no:03d}. "
                f"Description: {debt.get('description')}"
            )

    for fid, fore in sorted(state.foreshadowing.items()):
        if fore.get("status") == "paid":
            continue
        last = _WINDOW_ANY_RE.search(str(fore.get("last_touched") or ""))
        last_no = int(last.group(1)) if last else None
        if last_no is not None and current_chapter_no - last_no >= foreshadow_stale_after:
            warnings.append(
                f"FORESHADOW_STALE: {fid} planted/last-touched at ch{last_no:03d}, untouched for "
                f"{current_chapter_no - last_no} chapters (status={fore.get('status')}). "
                f"Content: {fore.get('content')}"
            )

    return warnings
