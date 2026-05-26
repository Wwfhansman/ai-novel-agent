#!/usr/bin/env python3
"""Validate AI Novel Agent chapter output for common failure modes.

Checks: missing chapter artifacts, weak writing packets, TXT blank lines,
paragraph density, reflective endings, short atmosphere endings, and stale
planning fields.

Ending checks now use composite pattern detection instead of single-keyword
matching, to avoid false positives on normal Chinese web-novel prose.
Paragraph density thresholds are advisory (warnings) with genre-aware lower
bounds instead of a single hard minimum.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from validators.chapter_completeness import validate_chapter_artifacts
from validators.cross_chapter import validate_cross_chapter_patterns
from validators.merge_preview import validate_merge_previews
from validators.planning_audit import validate_planning
from validators.prose_patterns import check_prose_patterns
from validators.protected_files import validate_protected_files
from validators.state_drift import validate_active_flow_catches_up, validate_state_drift
from validators.txt_format import validate_txt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path, help="Novel project path, e.g. projects/my-novel")
    parser.add_argument("--chapters", nargs="*", help="Chapter ids to validate, e.g. ch011 ch012")
    parser.add_argument("--fix-format", action="store_true", help="Remove blank body lines from final.txt")
    parser.add_argument("--skip-planning", action="store_true", help="Skip planning-memory checks")
    parser.add_argument("--skip-state-drift", action="store_true", help="Skip structured state drift checks")
    parser.add_argument("--drift-lookback", type=int, default=3, help="Number of recent chapters to check for state drift")
    parser.add_argument("--check-protected-files", action="store_true", help="Check protected-file change log visibility")
    parser.add_argument("--skip-artifacts", action="store_true", help="Skip chapter artifact/context/review checks")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()

    project = args.project
    all_errors: list[str] = []
    all_warnings: list[str] = []

    if not project.exists():
        print(f"Project not found: {project}", file=sys.stderr)
        return 2

    chapters = args.chapters
    if not chapters:
        chapter_root = project / "chapters"
        chapters = sorted(p.name for p in chapter_root.glob("ch*") if p.is_dir())[-3:]

    if not args.skip_planning:
        errs, warns = validate_planning(project, chapters)
        all_errors.extend(errs)
        all_warnings.extend(warns)
        errs, warns = validate_merge_previews(project, chapters)
        all_errors.extend(errs)
        all_warnings.extend(warns)
        errs, warns = validate_cross_chapter_patterns(project, chapters)
        all_errors.extend(errs)
        all_warnings.extend(warns)
        all_errors.extend(validate_active_flow_catches_up(project, chapters))
        if not args.skip_state_drift:
            errs, warns = validate_state_drift(project, chapters, lookback=args.drift_lookback)
            all_errors.extend(errs)
            all_warnings.extend(warns)

    if args.check_protected_files:
        errs, warns = validate_protected_files(project)
        all_errors.extend(errs)
        all_warnings.extend(warns)

    for chapter in chapters:
        chapter_dir = project / "chapters" / chapter
        if not args.skip_artifacts:
            errs, warns = validate_chapter_artifacts(chapter_dir)
            all_errors.extend(errs)
            all_warnings.extend(warns)
        errs, warns = validate_txt(chapter_dir / "final.txt", args.fix_format, strict=args.strict)
        all_errors.extend(errs)
        all_warnings.extend(warns)
        # Prose pattern diversity check
        final_txt = chapter_dir / "final.txt"
        if final_txt.exists():
            errs, warns = check_prose_patterns(final_txt)
            all_errors.extend(errs)
            all_warnings.extend(warns)

    exit_code = 0

    if all_warnings:
        print("Warnings:")
        for w in all_warnings:
            print(f"  [WARN]  {w}")
        print()

    if all_errors:
        print("Errors:")
        for e in all_errors:
            print(f"  [ERROR] {e}")
        exit_code = 2

    if args.strict and all_warnings:
        print("Strict mode: warnings are treated as failures.")
        exit_code = 2

    if not all_errors and not all_warnings:
        print("Validation passed.")
    elif exit_code == 0:
        print(f"Validation passed with {len(all_warnings)} warning(s).")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
