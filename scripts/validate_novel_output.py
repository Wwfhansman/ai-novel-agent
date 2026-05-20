#!/usr/bin/env python3
"""Validate AI Novel Agent chapter output for common failure modes.

This is intentionally lightweight. It checks the problems that repeatedly
survive prose-only instructions: missing chapter artifacts, weak context packs,
TXT blank lines, paragraph density, reflective endings, short atmosphere
endings, and stale planning fields that push chapters back into container-like
summaries.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REFLECTIVE_ENDING_PATTERNS = [
    r"下一步",
    r"想了一会",
    r"想了很久",
    r"他在想",
    r"她在想",
    r"心里知道",
    r"知道[，,。]",
    r"明白[了，,。]",
    r"意识到",
    r"决定",
    r"不会持续太久",
    r"这只是开始",
    r"更大的威胁",
    r"会怎么想",
    r"该怎么办",
    r"要看.*反应",
    r"看着.*黑暗",
    r"窗外",
    r"夜色",
    r"吹灭.*灯",
]

STALE_PLANNING_PATTERNS = [
    r"\bbridge_to_next\s*:",
    r"\bcontinuity_from_previous\s*:",
    r"\bnext_hook\s*:",
    r"结尾方向",
    r"情绪节奏",
    r"本轮需要",
    r"本轮三章必须",
    r"决定下一步",
    r"想下一步",
]

REQUIRED_PLANNING_FIELDS = [
    "macro_stage",
    "scale_level",
    "inbound_pressure",
    "chapter_turn",
    "outbound_pressure",
    "handoff_to_next_chapter",
    "scale_pacing_constraints",
]

REQUIRED_CHAPTER_FILES = [
    "brief.md",
    "context_pack.md",
    "draft.txt",
    "final.txt",
    "review.md",
    "summary.yml",
    "canon_delta.yml",
]

REQUIRED_CONTEXT_SECTIONS = [
    "## Read Files",
    "## Source References",
    "## Longform Scale Check",
    "## Reader Reward Check",
    "## Cut Continuity",
    "## Required Updates After Writing",
]

REQUIRED_REVIEW_SECTIONS = [
    "## Reader Reward Check",
    "## TXT Format Check",
    "## Memory Update Check",
]

MIN_PARAGRAPHS_FOR_NORMAL_CHAPTER = 20
NORMAL_CHAPTER_CHAR_THRESHOLD = 1800
GIANT_PARAGRAPH_CHARS = 360
LONG_PARAGRAPH_CHARS = 220
TITLE_PATTERN = re.compile(r"^第[一二三四五六七八九十百千万零〇两0-9]+章\s*\S+")


def nonblank(lines: list[str]) -> list[str]:
    return [line.strip() for line in lines if line.strip()]


def normalize_txt(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines:
        return False

    title = lines[0].rstrip()
    body_start = 1
    if len(lines) > 1 and not lines[1].strip():
        body_start = 2

    body = [line.rstrip() for line in lines[body_start:] if line.strip()]
    fixed = title + "\n\n" + "\n".join(body) + "\n"
    if fixed != text:
        path.write_text(fixed, encoding="utf-8", newline="\n")
        return True
    return False


def validate_txt(path: Path, fix_format: bool) -> list[str]:
    issues: list[str] = []
    if not path.exists():
        return [f"MISSING_FINAL: {path}"]

    if fix_format:
        normalize_txt(path)

    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 3:
        issues.append(f"TXT_TOO_SHORT: {path}")
        return issues

    title = lines[0].strip()
    if not TITLE_PATTERN.search(title):
        issues.append(
            f"TITLE_FORMAT: {path} first line should look like a chapter title, e.g. 第十二章 对峙."
        )

    body_lines = lines[2:]
    body_blank_numbers = [i + 3 for i, line in enumerate(body_lines) if not line.strip()]
    if body_blank_numbers:
        sample = ", ".join(map(str, body_blank_numbers[:10]))
        issues.append(
            f"TXT_BLANK_LINES: {path} has {len(body_blank_numbers)} blank body lines "
            f"(first lines: {sample}). Ordinary body paragraphs must not be separated by blank lines."
        )

    body_paragraphs = [(i + 3, line.strip()) for i, line in enumerate(body_lines) if line.strip()]
    body_char_count = sum(len(line) for _, line in body_paragraphs)
    paragraph_count = len(body_paragraphs)
    body_text = "\n".join(text for _, text in body_paragraphs)
    if re.search(r"[\u4e00-\u9fff]\s+(of|the|and|or|in|to|from)\s+[\u4e00-\u9fff]", body_text, re.IGNORECASE):
        issues.append(
            f"FOREIGN_TOKEN_CONTAMINATION: {path} appears to contain an English connector inside Chinese prose."
        )
    if body_char_count >= NORMAL_CHAPTER_CHAR_THRESHOLD and paragraph_count < MIN_PARAGRAPHS_FOR_NORMAL_CHAPTER:
        issues.append(
            f"LOW_PARAGRAPH_DENSITY: {path} has {paragraph_count} body paragraphs for "
            f"{body_char_count} characters. Normal web-novel TXT paragraphing should usually "
            "have 25-60 body paragraphs for a 2000-3500 Chinese character chapter. "
            "Do not confuse 'no blank lines' with 'few paragraphs'."
        )

    giant_paragraphs = [
        (line_no, len(text))
        for line_no, text in body_paragraphs
        if len(text) > GIANT_PARAGRAPH_CHARS
    ]
    if giant_paragraphs:
        sample = ", ".join(f"line {line_no}: {length} chars" for line_no, length in giant_paragraphs[:5])
        issues.append(
            f"GIANT_PARAGRAPH: {path} has paragraphs over {GIANT_PARAGRAPH_CHARS} characters "
            f"({sample}). Split at action changes, speaker changes, reaction beats, new facts, "
            "camera shifts, or rhythm pauses."
        )

    long_paragraphs = [
        (line_no, len(text))
        for line_no, text in body_paragraphs
        if len(text) > LONG_PARAGRAPH_CHARS
    ]
    if body_char_count >= NORMAL_CHAPTER_CHAR_THRESHOLD and len(long_paragraphs) > max(3, paragraph_count // 3):
        sample = ", ".join(f"line {line_no}: {length} chars" for line_no, length in long_paragraphs[:5])
        issues.append(
            f"LONG_PARAGRAPH_OVERUSE: {path} has {len(long_paragraphs)} paragraphs over "
            f"{LONG_PARAGRAPH_CHARS} characters ({sample}). Most body paragraphs should be "
            "40-160 Chinese characters."
        )

    nb = nonblank(lines)
    if not nb:
        issues.append(f"TXT_EMPTY: {path}")
        return issues

    last = nb[-1]
    ending_window = "\n".join(nb[-8:])

    if len(last) <= 14 and not last.endswith(("？", "！", "”")):
        issues.append(
            f"SHORT_ATMOSPHERE_ENDING: {path} last nonblank line is too short: {last!r}"
        )

    for pattern in REFLECTIVE_ENDING_PATTERNS:
        if re.search(pattern, ending_window):
            issues.append(
                f"REFLECTIVE_ENDING: {path} ending matches /{pattern}/. "
                "End with external motion, not protagonist recap, planning, or mood-button closure."
            )
            break

    if re.search(r"(他|她|萧衍|主角).{0,12}(想|知道|明白|意识到|决定)", ending_window):
        issues.append(
            f"PROTAGONIST_THOUGHT_ENDING: {path} final section is driven by protagonist cognition."
        )

    return issues


def validate_chapter_artifacts(chapter_dir: Path) -> list[str]:
    issues: list[str] = []
    for filename in REQUIRED_CHAPTER_FILES:
        path = chapter_dir / filename
        if not path.exists():
            issues.append(f"MISSING_CHAPTER_FILE: {path}")

    context_pack = chapter_dir / "context_pack.md"
    if context_pack.exists():
        text = context_pack.read_text(encoding="utf-8")
        for section in REQUIRED_CONTEXT_SECTIONS:
            if section not in text:
                issues.append(f"MISSING_CONTEXT_SECTION: {context_pack} lacks {section}.")
        if (
            "source:" not in text
            and "Source:" not in text
            and "Source Refs" not in text
            and "Source References" not in text
        ):
            issues.append(
                f"MISSING_SOURCE_REFS: {context_pack} must cite file sources for key claims."
            )

    review = chapter_dir / "review.md"
    if review.exists():
        text = review.read_text(encoding="utf-8")
        for section in REQUIRED_REVIEW_SECTIONS:
            if section not in text:
                issues.append(f"MISSING_REVIEW_SECTION: {review} lacks {section}.")

    summary = chapter_dir / "summary.yml"
    if summary.exists():
        text = summary.read_text(encoding="utf-8")
        if "handoff_to_next_chapter" not in text:
            issues.append(f"MISSING_HANDOFF: {summary} lacks handoff_to_next_chapter.")

    canon_delta = chapter_dir / "canon_delta.yml"
    if canon_delta.exists():
        text = canon_delta.read_text(encoding="utf-8")
        if "handoff_to_next_chapter" not in text:
            issues.append(f"MISSING_HANDOFF: {canon_delta} lacks handoff_to_next_chapter.")

    return issues


def validate_planning(project: Path) -> list[str]:
    issues: list[str] = []
    longform = project / "book" / "longform_blueprint.yml"
    if not longform.exists():
        issues.append(
            f"MISSING_LONGFORM_BLUEPRINT: {longform}. Create it during bootstrap or migrate the project before writing."
        )
    else:
        text = longform.read_text(encoding="utf-8")
        for field in [
            "target_length",
            "macro_structure",
            "scale_map",
            "power_pacing",
            "secret_pacing",
            "scale_guardrails",
        ]:
            if field not in text:
                issues.append(f"LONGFORM_BLUEPRINT_INCOMPLETE: {longform} lacks {field}.")

    planning_files = [
        project / "planning" / "rolling_plan.yml",
        project / "planning" / "current_round.yml",
        project / "planning" / "active_flow.yml",
    ]

    for path in planning_files:
        if not path.exists():
            issues.append(f"MISSING_PLANNING: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in STALE_PLANNING_PATTERNS:
            if re.search(pattern, text):
                issues.append(
                    f"STALE_PLANNING_FIELD: {path} contains old planning language matching /{pattern}/."
                )
        if path.name in {"rolling_plan.yml", "current_round.yml"}:
            for field in REQUIRED_PLANNING_FIELDS:
                if field not in text:
                    issues.append(f"MISSING_FLOW_FIELD: {path} lacks {field}.")
        if path.name == "rolling_plan.yml" and re.search(r"\bstatus\s*:\s*completed\b", text):
            issues.append(
                f"COMPLETED_PLAN_NOT_ARCHIVED: {path} contains completed chapters. "
                "Move finished chapter plan entries to planning/completed_plan_log.yml and keep rolling_plan.yml as the future window."
            )

    for path in [
        project / "planning" / "completed_plan_log.yml",
        project / "planning" / "future_backlog.yml",
    ]:
        if not path.exists():
            issues.append(f"MISSING_PLANNING: {path}")

    for path in (project / "chapters").glob("ch*/summary.yml"):
        text = path.read_text(encoding="utf-8")
        if re.search(r"\bnext_hook\s*:", text):
            issues.append(f"STALE_SUMMARY_FIELD: {path} uses next_hook; use handoff_to_next_chapter.")

    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path, help="Novel project path, e.g. projects/my-novel")
    parser.add_argument("--chapters", nargs="*", help="Chapter ids to validate, e.g. ch011 ch012")
    parser.add_argument("--fix-format", action="store_true", help="Remove blank body lines from final.txt")
    parser.add_argument("--skip-planning", action="store_true", help="Skip planning-memory checks")
    parser.add_argument("--skip-artifacts", action="store_true", help="Skip chapter artifact/context/review checks")
    args = parser.parse_args()

    project = args.project
    issues: list[str] = []

    if not project.exists():
        print(f"Project not found: {project}", file=sys.stderr)
        return 2

    if not args.skip_planning:
        issues.extend(validate_planning(project))

    chapters = args.chapters
    if not chapters:
        chapter_root = project / "chapters"
        chapters = sorted(p.name for p in chapter_root.glob("ch*") if p.is_dir())[-3:]

    for chapter in chapters:
        chapter_dir = project / "chapters" / chapter
        if not args.skip_artifacts:
            issues.extend(validate_chapter_artifacts(chapter_dir))
        issues.extend(validate_txt(chapter_dir / "final.txt", args.fix_format))

    if issues:
        print("Validation failed:")
        for issue in issues:
            print(f"- {issue}")
        return 2

    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
