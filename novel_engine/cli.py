#!/usr/bin/env python3
"""novel_engine command line.

    python -m novel_engine validate <project>     # schema + integrity over events/
    python -m novel_engine project  <project>     # print derived current state
    python -m novel_engine health   <project>     # overdue debts / stale foreshadowing
    python -m novel_engine shadow   <project>     # derived vs hand-written drift (migration)

`validate`, `project`, and `health` read the new events/ layout. `shadow` reads
the legacy chapters/chXXX/canon_delta.yml and changes nothing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import diff
from .context import entering_state
from .coverage import coverage_warnings
from .events import chapter_sort_key, load_project_events
from .experiment import write_experiment
from .gate import run_gate
from .kit import write_kit
from .migrate import seed_bootstrap
from .scene import exemplars as scene_exemplars
from .integrity import check_integrity
from .ledger_health import check_ledger_health
from .materialize import write_materialized
from .migrate import migrate
from .profile import load_profile, resolve_project_profile
from .projection import project
from .quality import prose_metrics, prose_patterns
from .quality import txt_format as quality_txt
from .scene.packet import build_scene_packets
from .structure import analyze as structure_analyze
from .structure import chapter_meta as structure_meta
from .structure import legacy_structure


def _current_chapter_no(events) -> int:
    return max((chapter_sort_key(e.chapter) for e in events), default=0)


def _cmd_validate(args) -> int:
    project_path = args.project
    events, errors = load_project_events(project_path)

    seeds: dict[str, set[str]] = {"characters": set(), "debts": set(), "foreshadowing": set()}
    if args.seed_legacy:
        from .legacy import adapt_project

        _events, seeds = adapt_project(project_path)

    int_errors, int_warnings = check_integrity(
        events,
        known_characters=seeds["characters"],
        known_debts=seeds["debts"],
        known_foreshadowing=seeds["foreshadowing"],
    )
    errors = errors + int_errors

    if int_warnings:
        print("Warnings:")
        for warning in int_warnings:
            print(f"  [WARN]  {warning}")
        print()
    if errors:
        print("Errors:")
        for error in errors:
            print(f"  [ERROR] {error}")
        return 2
    print(f"Validation passed: {len(events)} events, no integrity errors.")
    return 0


def _cmd_project(args) -> int:
    events, errors = load_project_events(args.project)
    if errors and not args.force:
        print("Refusing to project: fix these load/schema errors first (or pass --force):", file=sys.stderr)
        for error in errors:
            print(f"  [ERROR] {error}", file=sys.stderr)
        return 2
    state = project(events)
    output = json.dumps(state.to_dict(), ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
        print(f"Wrote derived state: {args.output}")
    else:
        print(output)
    return 0


def _cmd_health(args) -> int:
    events, errors = load_project_events(args.project)
    if errors:
        for error in errors:
            print(f"  [ERROR] {error}", file=sys.stderr)
        return 2
    state = project(events)
    profile = resolve_project_profile(args.project)
    lh = profile.get("ledger_health", {})
    warnings = check_ledger_health(
        state,
        _current_chapter_no(events),
        foreshadow_stale_after=lh.get("foreshadow_stale_after", 12),
        debt_overdue_grace=lh.get("debt_overdue_grace", 0),
    )
    if not warnings:
        print("Ledger health: no overdue debts or stale foreshadowing.")
        return 0
    print("Ledger health warnings:")
    for warning in warnings:
        print(f"  [WARN]  {warning}")
    return 0


def _cmd_shadow(args) -> int:
    report = diff.shadow_report(args.project)
    print(diff.format_report(report), end="")
    if args.json:
        Path(args.json).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote JSON report: {args.json}")
    return 0


def _cmd_init(args) -> int:
    try:
        path, count = seed_bootstrap(args.project, force=args.force)
    except FileExistsError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if count == 0:
        print(f"Wrote {path}, but it has 0 events — no initial entities/ledgers found.", file=sys.stderr)
        print("Bootstrap the story first (constitution/characters/rolling_plan), then re-run init.", file=sys.stderr)
        return 0
    print(f"Seeded {count} bootstrap event(s): {path}")
    print(f"Next: python -m novel_engine check {args.project}, then kit --chapter ch001.")
    return 0


def _cmd_migrate(args) -> int:
    try:
        events_dir, written = migrate(args.project, force=args.force)
    except FileExistsError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"Wrote {len(written)} event file(s) to {events_dir}:")
    for name in written:
        print(f"  {name}")
    if "bootstrap.yml" in written:
        print("Review events/bootstrap.yml (best-effort initial state), then run: "
              "python -m novel_engine check", args.project)
    else:
        print("Run: python -m novel_engine check", args.project)
    return 0


def _cmd_materialize(args) -> int:
    events, errors = load_project_events(args.project)
    if errors and not args.force:
        for error in errors:
            print(f"  [ERROR] {error}", file=sys.stderr)
        return 2
    state = project(events)
    written = write_materialized(state, args.project, in_place=args.in_place)
    where = "in place" if args.in_place else f"to {Path(args.project) / 'derived'}"
    print(f"Materialized {len(written)} state file(s) {where}:")
    for path in written:
        print(f"  {path}")
    return 0


def _cmd_context(args) -> int:
    events, errors = load_project_events(args.project)
    if errors and not args.force:
        for error in errors:
            print(f"  [ERROR] {error}", file=sys.stderr)
        return 2
    pack = entering_state(events, args.chapter)
    print(json.dumps(pack, ensure_ascii=False, indent=2))
    return 0


def _print_gate(result) -> None:
    print(f"Engine gate: {result.sections.get('event_count', 0)} events")
    if result.warnings:
        print("Warnings (advisory):")
        for warning in result.warnings:
            print(f"  [WARN]  {warning}")
    if result.errors:
        print("Errors (must fix):")
        for error in result.errors:
            print(f"  [ERROR] {error}")


def _cmd_check(args) -> int:
    result = run_gate(args.project)
    _print_gate(result)
    if not result.ok:
        return 2
    print("Gate passed (schema + integrity clean; warnings are advisory).")
    return 0


def _cmd_commit(args) -> int:
    result = run_gate(args.project)
    _print_gate(result)
    if not result.ok:
        print("Refusing to commit: fix the errors above first.", file=sys.stderr)
        return 2
    events, _ = load_project_events(args.project)
    state = project(events)
    written = write_materialized(state, args.project, in_place=True)
    print(f"Gate passed. Materialized {len(written)} derived state file(s) in place:")
    for path in written:
        print(f"  {path}")
    return 0


def _cmd_structure(args) -> int:
    profile = resolve_project_profile(args.project)
    records, meta_errors = structure_meta.load_native(args.project)
    source = "structure/"
    if not records:
        records = legacy_structure.from_rolling_plan(args.project, profile)
        source = "planning/rolling_plan.yml (legacy)"
    if meta_errors:
        for error in meta_errors:
            print(f"  [ERROR] {error}", file=sys.stderr)
        return 2
    if not records:
        print("No structural records found (no structure/ dir and no rolling_plan chapters).")
        return 0
    events, _ = load_project_events(args.project)
    report = structure_analyze.analyze(records, profile, events=events or None)
    print(f"Structure report for {Path(args.project).name} ({len(records)} chapters from {source}):")
    print("  tension curve: " + " ".join(
        f"{t['chapter']}={t['tension'] if t['tension'] is not None else '?'}" for t in report["tension_curve"]
    ))
    if not report["warnings"]:
        print("  No structure warnings (pacing varied, world alive, tension escalating).")
        return 0
    for warning in report["warnings"]:
        print(f"  [WARN]  {warning}")
    return 0


def _profile_for_file(path: Path, explicit: str | None) -> dict:
    if explicit:
        return load_profile(explicit)
    path = Path(path)
    # .../<project>/chapters/<chXXX>/final.txt -> use that project's profile (per-book overrides)
    if path.parent.parent.name == "chapters":
        return resolve_project_profile(path.parents[2])
    return load_profile()


def _cmd_coverage(args) -> int:
    events, errors = load_project_events(args.project)
    if errors:
        for error in errors:
            print(f"  [ERROR] {error}", file=sys.stderr)
        return 2
    state = project(events)
    profile = resolve_project_profile(args.project)
    warnings = coverage_warnings(args.project, events, state, profile)
    if not warnings:
        print("记忆覆盖 OK：没发现正文里关系变了却没记 relationship_changed 的情况。")
        return 0
    print("记漏检测（正文里关系变了但 events 没记）：")
    for warning in warnings:
        print(f"  [WARN]  {warning}")
    return 0


def _cmd_patterns(args) -> int:
    text = Path(args.file).read_text(encoding="utf-8")
    profile = _profile_for_file(args.file, args.profile)
    errors, warnings = prose_patterns.evaluate(text, profile)
    for hit in prose_patterns.scan(text, profile):
        print(f"  {hit.key}: {hit.count}  e.g. {hit.samples[0] if hit.samples else ''!r}")
    for warning in warnings:
        print(f"  [WARN]  {warning}")
    if errors:
        print("AI-prose tics over limit:")
        for error in errors:
            print(f"  [ERROR] {error}")
        return 2
    print("Prose patterns within profile limits.")
    return 0


def _cmd_fingerprint(args) -> int:
    text = Path(args.file).read_text(encoding="utf-8")
    print(json.dumps(prose_metrics.fingerprint(text), ensure_ascii=False, indent=2))
    return 0


def _cmd_compare(args) -> int:
    a = Path(args.file_a).read_text(encoding="utf-8")
    b = Path(args.file_b).read_text(encoding="utf-8")
    print(json.dumps(prose_metrics.compare(a, b), ensure_ascii=False, indent=2))
    return 0


def _cmd_scene(args) -> int:
    packets, notes = build_scene_packets(args.project, args.chapter)
    for note in notes:
        print(f"  [note] {note}", file=sys.stderr)
    payload = {"chapter": args.chapter, "scene_count": len(packets), "packets": packets}
    if args.output:
        Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {len(packets)} scene packet(s): {args.output}")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def _cmd_kit(args) -> int:
    out_dir, written, notes = write_kit(args.project, args.chapter)
    for note in notes:
        print(f"  [note] {note}", file=sys.stderr)
    print(f"Wrote chapter production kit to {out_dir}:")
    for name in written:
        print(f"  {name}")
    print(f"Next: follow {out_dir}/PRODUCE.md.")
    return 0


def _cmd_exemplars_init(args) -> int:
    path, created = scene_exemplars.scaffold(args.project)
    if created:
        print(f"Wrote starter exemplar corpus: {path}")
        print("Tag your best passages by scene type (building/relationship/reveal/...) for better retrieval.")
    else:
        print(f"Exemplar corpus already exists: {path}")
    return 0


def _cmd_experiment(args) -> int:
    out_dir, written = write_experiment(args.project, args.chapter)
    print(f"Wrote A/B experiment package to {out_dir}:")
    for name in written:
        print(f"  {name}")
    print(f"Next: follow {out_dir}/README.md (write out_A.txt / out_B.txt, then evaluate.md).")
    return 0


def _cmd_txt(args) -> int:
    profile = load_profile(args.profile) if args.profile else load_profile()
    errors, warnings = quality_txt.check_txt(args.file, profile, chapter_function=args.function)
    for warning in warnings:
        print(f"  [WARN]  {warning}")
    if errors:
        for error in errors:
            print(f"  [ERROR] {error}")
        return 2
    print("TXT format OK." if not warnings else f"TXT format OK with {len(warnings)} warning(s).")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="novel_engine", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate", help="schema + integrity over events/")
    p_validate.add_argument("project", type=Path)
    p_validate.add_argument("--seed-legacy", action="store_true", help="seed known ids from existing entities/ledgers")
    p_validate.set_defaults(func=_cmd_validate)

    p_project = sub.add_parser("project", help="print derived current state as JSON")
    p_project.add_argument("project", type=Path)
    p_project.add_argument("--output", type=Path)
    p_project.add_argument("--force", action="store_true", help="project even if some events failed to load")
    p_project.set_defaults(func=_cmd_project)

    p_health = sub.add_parser("health", help="overdue debts / stale foreshadowing")
    p_health.add_argument("project", type=Path)
    p_health.set_defaults(func=_cmd_health)

    p_shadow = sub.add_parser("shadow", help="derived vs hand-written drift (read-only)")
    p_shadow.add_argument("project", type=Path)
    p_shadow.add_argument("--json", type=Path, help="also write the full report as JSON")
    p_shadow.set_defaults(func=_cmd_shadow)

    p_init = sub.add_parser("init", help="new book: seed events/bootstrap.yml from initial entities/ledgers")
    p_init.add_argument("project", type=Path)
    p_init.add_argument("--force", action="store_true", help="overwrite an existing bootstrap.yml")
    p_init.set_defaults(func=_cmd_init)

    p_migrate = sub.add_parser("migrate", help="legacy project with written chapters -> events/ (best-effort)")
    p_migrate.add_argument("project", type=Path)
    p_migrate.add_argument("--force", action="store_true", help="overwrite an existing events/ directory")
    p_migrate.set_defaults(func=_cmd_migrate)

    p_materialize = sub.add_parser("materialize", help="render derived entities/ledgers from events/")
    p_materialize.add_argument("project", type=Path)
    p_materialize.add_argument("--in-place", action="store_true", help="overwrite entities/ledgers instead of writing to derived/")
    p_materialize.add_argument("--force", action="store_true", help="materialize even if some events failed to load")
    p_materialize.set_defaults(func=_cmd_materialize)

    p_context = sub.add_parser("context", help="compile a writer's entering-state pack for a chapter")
    p_context.add_argument("project", type=Path)
    p_context.add_argument("--chapter", required=True, help="chapter being written, e.g. ch004")
    p_context.add_argument("--force", action="store_true")
    p_context.set_defaults(func=_cmd_context)

    p_check = sub.add_parser("check", help="unified engine gate: schema + integrity + health + structure")
    p_check.add_argument("project", type=Path)
    p_check.set_defaults(func=_cmd_check)

    p_commit = sub.add_parser("commit", help="run the gate, then materialize derived state in place if it passes")
    p_commit.add_argument("project", type=Path)
    p_commit.set_defaults(func=_cmd_commit)

    p_structure = sub.add_parser("structure", help="read-pull / anti-shrink report over chapter structure")
    p_structure.add_argument("project", type=Path)
    p_structure.set_defaults(func=_cmd_structure)

    p_coverage = sub.add_parser("coverage", help="memory-coverage: relationship beats in prose not recorded as events")
    p_coverage.add_argument("project", type=Path)
    p_coverage.set_defaults(func=_cmd_coverage)

    p_patterns = sub.add_parser("patterns", help="scan a prose file for AI-prose tics (profile-driven)")
    p_patterns.add_argument("file", type=Path)
    p_patterns.add_argument("--profile", help="profile name or path (default zh-webnovel)")
    p_patterns.set_defaults(func=_cmd_patterns)

    p_fingerprint = sub.add_parser("fingerprint", help="voice fingerprint of a prose file")
    p_fingerprint.add_argument("file", type=Path)
    p_fingerprint.set_defaults(func=_cmd_fingerprint)

    p_compare = sub.add_parser("compare", help="compare two prose files (A/B / voice drift)")
    p_compare.add_argument("file_a", type=Path)
    p_compare.add_argument("file_b", type=Path)
    p_compare.set_defaults(func=_cmd_compare)

    p_txt = sub.add_parser("txt", help="profile-driven TXT format / paragraph-density check")
    p_txt.add_argument("file", type=Path)
    p_txt.add_argument("--profile", help="profile name or path (default zh-webnovel)")
    p_txt.add_argument("--function", help="chapter_function for genre-aware density (e.g. face_slap)")
    p_txt.set_defaults(func=_cmd_txt)

    p_experiment = sub.add_parser("experiment", help="assemble an A/B (chapter-level vs scene-level) writing experiment")
    p_experiment.add_argument("project", type=Path)
    p_experiment.add_argument("--chapter", required=True, help="chapter to run the A/B on, e.g. ch002")
    p_experiment.set_defaults(func=_cmd_experiment)

    p_scene = sub.add_parser("scene", help="assemble per-scene writing packets (entering-state + spec + exemplars)")
    p_scene.add_argument("project", type=Path)
    p_scene.add_argument("--chapter", required=True, help="chapter to build scene packets for, e.g. ch004")
    p_scene.add_argument("--output", type=Path, help="write packets JSON to this path")
    p_scene.set_defaults(func=_cmd_scene)

    p_kit = sub.add_parser("kit", help="turnkey chapter production kit (rendered prompts + events template + steps)")
    p_kit.add_argument("project", type=Path)
    p_kit.add_argument("--chapter", required=True, help="chapter to produce, e.g. ch004")
    p_kit.set_defaults(func=_cmd_kit)

    p_exinit = sub.add_parser("exemplars-init", help="scaffold style/exemplars.yml for voice-by-type retrieval")
    p_exinit.add_argument("project", type=Path)
    p_exinit.set_defaults(func=_cmd_exemplars_init)

    return parser, sub


def subcommand_names() -> list[str]:
    """Expose registered subcommands for the docs contract test."""
    _parser, sub = build_parser()
    return sorted(sub.choices)


def main(argv=None) -> int:
    parser, _sub = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
