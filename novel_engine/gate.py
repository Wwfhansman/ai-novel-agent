"""The unified engine gate for a writing round.

This is the production-backbone piece of M1: one call that runs every engine
check a finished batch must pass — schema validity, referential/temporal
integrity, ledger health, and structure — and returns a single pass/fail with a
structured report. It is the engine-native replacement for the legacy
round_state_merge.py + validate_novel_output.py end-of-round dance.

Policy mirrors the project's long-standing stance: schema and integrity problems
are ERRORS (must fix); ledger-health and structure problems are WARNINGS
(advisory, not blocking).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .coverage import coverage_warnings
from .events import chapter_sort_key, load_project_events
from .integrity import check_integrity
from .ledger_health import check_ledger_health
from .profile import resolve_project_profile
from .projection import project as project_state
from .structure import analyze as structure_analyze
from .structure import chapter_meta as structure_meta
from .structure import legacy_structure


@dataclass
class GateResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    sections: dict = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors


def run_gate(project: Path) -> GateResult:
    project = Path(project)
    result = GateResult()
    profile = resolve_project_profile(project)

    events, load_errors = load_project_events(project)
    result.errors.extend(load_errors)
    result.sections["event_count"] = len(events)

    # Integrity (errors + warnings).
    int_errors, int_warnings = check_integrity(events)
    result.errors.extend(int_errors)
    result.warnings.extend(int_warnings)

    if events:
        state = project_state(events)
        current_no = max((chapter_sort_key(e.chapter) for e in events), default=0)

        lh = profile.get("ledger_health", {})
        result.warnings.extend(check_ledger_health(
            state, current_no,
            foreshadow_stale_after=lh.get("foreshadow_stale_after", 12),
            debt_overdue_grace=lh.get("debt_overdue_grace", 0),
        ))

        # Structure (native records, else legacy rolling_plan).
        records, meta_errors = structure_meta.load_native(project)
        result.errors.extend(meta_errors)
        if not records:
            records = legacy_structure.from_rolling_plan(project, profile)
        if records:
            report = structure_analyze.analyze(records, profile, events=events or None)
            result.warnings.extend(report["warnings"])
            result.sections["structure"] = report

        # Memory coverage: relationship beats written in prose but not recorded.
        result.warnings.extend(coverage_warnings(project, events, state, profile))

    return result
