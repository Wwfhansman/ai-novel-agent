#!/usr/bin/env python3
"""Compile a bounded context pack for novel-architect."""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PLANNING = ROOT / "templates" / "project" / "planning"


def read_excerpt(path: Path, limit: int) -> str:
    if not path.exists():
        return f"[missing] {path}\n"
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    if len(text) <= limit:
        return text + "\n"
    return text[:limit].rstrip() + "\n...[truncated]\n"


def write_if_missing(path: Path, template: Path) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    if template.exists() and template.is_file():
        shutil.copyfile(template, path)
    else:
        path.write_text("", encoding="utf-8")
    return True


def init_missing_architecture_files(project: Path) -> list[Path]:
    created: list[Path] = []
    mapping = {
        project / "planning" / "story_architecture.yml": TEMPLATE_PLANNING / "story_architecture.yml",
        project / "planning" / "thread_board.yml": TEMPLATE_PLANNING / "thread_board.yml",
        project / "planning" / "completed_threads_log.yml": TEMPLATE_PLANNING / "completed_threads_log.yml",
    }
    for target, template in mapping.items():
        if write_if_missing(target, template):
            created.append(target)
    pack_dir = project / "planning" / "development_packs"
    if not pack_dir.exists():
        pack_dir.mkdir(parents=True, exist_ok=True)
        created.append(pack_dir)
    return created


def chapter_sort_key(path: Path) -> int:
    digits = "".join(ch for ch in path.name if ch.isdigit())
    return int(digits) if digits else -1


def latest_chapters(project: Path, count: int) -> list[str]:
    chapter_root = project / "chapters"
    chapters = sorted((p for p in chapter_root.glob("ch*") if p.is_dir()), key=chapter_sort_key)
    return [p.name for p in chapters[-count:]]


def section(title: str, body: str) -> str:
    return f"\n## {title}\n\n{body.strip()}\n"


def compile_context(project: Path, output: Path, chapters: list[str], excerpt_limit: int) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    read_files: list[Path] = []

    def include(path: Path, limit: int | None = None) -> str:
        read_files.append(path)
        return read_excerpt(path, limit or excerpt_limit)

    parts: list[str] = [
        "# Architect Context Pack\n",
        section(
            "Metadata",
            "\n".join([
                f"- project: {project}",
                f"- generated_at: {datetime.now(timezone.utc).isoformat()}",
                f"- purpose: novel-architect story development before writing",
                f"- recent_chapters: {', '.join(chapters) if chapters else 'none'}",
            ]),
        ),
        section("Project", include(project / "project.yml", 2000)),
        section("Constitution", include(project / "book" / "constitution.md", 5000)),
        section("Longform Blueprint", include(project / "book" / "longform_blueprint.yml", 7000)),
        section("Reader Model", include(project / "book" / "reader_model.yml", 3000)),
        section("Current Volume Outline", include(project / "volumes" / "vol_001" / "volume_outline.md", 5000)),
        section("Current Volume State", include(project / "volumes" / "vol_001" / "volume_state.yml", 3000)),
        section("Active Flow", include(project / "planning" / "active_flow.yml", 5000)),
        section("Rolling Plan", include(project / "planning" / "rolling_plan.yml", 12000)),
        section("Story Architecture", include(project / "planning" / "story_architecture.yml", 6000)),
        section("Thread Board", include(project / "planning" / "thread_board.yml", 7000)),
        section("Future Backlog", include(project / "planning" / "future_backlog.yml", 5000)),
    ]

    recent_parts: list[str] = []
    for chapter in chapters:
        chapter_dir = project / "chapters" / chapter
        recent_parts.append(f"### {chapter}\n")
        recent_parts.append("#### summary.yml\n")
        recent_parts.append(include(chapter_dir / "summary.yml", 2500))
        recent_parts.append("#### canon_delta.yml\n")
        recent_parts.append(include(chapter_dir / "canon_delta.yml", 2500))
        final_path = chapter_dir / "final.txt"
        if final_path.exists():
            recent_parts.append("#### final.txt excerpt\n")
            recent_parts.append(include(final_path, 2500))
    parts.append(section("Recent Canon", "\n".join(recent_parts)))

    entity_parts: list[str] = []
    for path in [
        project / "entities" / "characters.yml",
        project / "entities" / "factions.yml",
        project / "entities" / "locations.yml",
        project / "entities" / "items.yml",
        project / "entities" / "power_system.yml",
    ]:
        entity_parts.append(f"### {path.relative_to(project)}\n")
        entity_parts.append(include(path, 6000))
    parts.append(section("Entity State Excerpts", "\n".join(entity_parts)))

    ledger_parts: list[str] = []
    for path in [
        project / "ledgers" / "world_state.yml",
        project / "ledgers" / "knowledge_state.yml",
        project / "ledgers" / "narrative_debts.yml",
        project / "ledgers" / "foreshadowing.yml",
        project / "ledgers" / "idea_pool.yml",
        project / "ledgers" / "decision_log.yml",
    ]:
        ledger_parts.append(f"### {path.relative_to(project)}\n")
        ledger_parts.append(include(path, 5000))
    parts.append(section("Ledger Excerpts", "\n".join(ledger_parts)))

    parts.append(section(
        "Architect Task",
        "\n".join([
            "- Diagnose whether the story is shrinking into a protagonist task chain.",
            "- Simulate what major actors and factions do if the protagonist does nothing.",
            "- Design future 10-30 chapter world expansion, conflict network, thread lifecycle, pacing, growth budget, and information-release plan.",
            "- Produce scene-ready writable material, not encyclopedia notes.",
            "- Recommend storage targets for story_architecture, thread_board, entities, ledgers, future_backlog, and rolling_plan.",
            "- Mark protected changes as needs_novel_change.",
        ]),
    ))

    parts.append(section(
        "Read Files",
        "\n".join(f"- {path}" for path in read_files),
    ))

    output.write_text("\n".join(parts).strip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile a context pack for novel-architect.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--latest", type=int, default=9, help="Number of latest chapters to include.")
    parser.add_argument("--chapters", nargs="*", help="Explicit chapter ids to include.")
    parser.add_argument("--excerpt-limit", type=int, default=4000)
    parser.add_argument("--init-missing", action="store_true", help="Create missing story architecture planning files from templates.")
    args = parser.parse_args()

    project = args.project
    if not project.exists():
        print(f"Project not found: {project}")
        return 2

    if args.init_missing:
        created = init_missing_architecture_files(project)
        for path in created:
            print(f"created: {path}")

    chapters = args.chapters if args.chapters else latest_chapters(project, args.latest)
    if args.output:
        output = args.output
    else:
        context_dir = project / "planning" / "context_packs"
        existing = sorted(context_dir.glob("architect_context_pack_*.md"))
        next_no = len(existing) + 1
        output = context_dir / f"architect_context_pack_{next_no:03d}.md"

    compile_context(project, output, chapters, args.excerpt_limit)
    print(f"Wrote architect context pack: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
