#!/usr/bin/env python3
"""Validate AI Novel Agent chapter output for common failure modes.

Checks: missing chapter artifacts, weak context packs, TXT blank lines,
paragraph density, reflective endings, short atmosphere endings, and stale
planning fields.

Ending checks now use composite pattern detection instead of single-keyword
matching, to avoid false positives on normal Chinese web-novel prose.
Paragraph density thresholds are advisory (warnings) with genre-aware lower
bounds instead of a single hard minimum.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ---- ending patterns ----

# Single-keyword matches are too broad for Chinese web novels.
# Instead, detect the *combination*: protagonist cognition + no external action.
# These patterns search for empty-reflection endings.
WEAK_REFLECTIVE_SIGNALS = [
    r"下一步",
    r"想了一会",
    r"想了很久",
    r"心里知道",
    r"不会持续太久",
    r"这只是开始",
    r"更大的威胁",
    r"会怎么想",
    r"该怎么办",
    r"要看.*反应",
    r"看着.*黑暗",
    r"吹灭.*灯",
]

# Endings that are worth flagging when they co-occur with no external motion.
ENDING_EXTERNAL_ACTION_SIGNALS = [
    r"推门|开门|走出|跑|追|喊|叫|动手|出手|拔剑|拔刀|落地|脚步声|马蹄",
    r"出现|赶到|闯|冲|拦|挡|抓住|松开|递|扔|砸|碎|裂",
    r"抬头|低头|起身|站起|转身|回头|停下",
    r"开口|出声|笑|哭|喘|吼|骂|沉默|不说话",
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
    "chapter_function",
    "pressure_curve",
    "reader_question_flow",
    "core_advance",
    "information_release",
    "chapter_turn",
    "side_yield",
    "planned_handoff",
    "叙事织入",
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

# Genre-aware paragraph density minimums.
# Different chapter types naturally have different paragraph counts
# even at the same character count.
MIN_PARAGRAPHS_BY_GENRE = {
    # action-heavy: rapid cuts, many short paragraphs
    "crisis": 15,
    "face_slap": 15,
    "breakthrough": 15,
    "competition": 15,
    "showing_off": 15,
    # investigation/explanation: moderate density
    "investigation": 20,
    "reveal": 20,
    "dungeon_rule": 20,
    "auction": 20,
    # daily-life / building: looser, more description
    "building": 25,
    "relationship": 25,
    "domestic_management": 25,
    "aftermath": 25,
    "transition": 25,
    # default for unclassified chapters
    "_default": 25,
}

NORMAL_CHAPTER_CHAR_THRESHOLD = 1800
GIANT_PARAGRAPH_CHARS = 220
LONG_PARAGRAPH_CHARS = 160
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


def _has_external_action_in_window(text: str) -> bool:
    """Check whether the ending window contains any external-action signal."""
    for pattern in ENDING_EXTERNAL_ACTION_SIGNALS:
        if re.search(pattern, text):
            return True
    return False


def _guess_chapter_function(chapter_dir: Path) -> str | None:
    """Try to read chapter_function from brief.md or summary.yml."""
    for fname in ("brief.md", "summary.yml"):
        p = chapter_dir / fname
        if p.exists():
            text = p.read_text(encoding="utf-8")
            m = re.search(r"chapter_function\s*:\s*(\S+)", text)
            if m:
                return m.group(1).strip().strip('"').strip("'")
    return None


def validate_txt(path: Path, fix_format: bool, strict: bool = False) -> tuple[list[str], list[str]]:
    """Validate chapter TXT. Returns (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        errors.append(f"MISSING_FINAL: {path}")
        return errors, warnings

    if fix_format:
        normalize_txt(path)

    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 3:
        errors.append(f"TXT_TOO_SHORT: {path}")
        return errors, warnings

    title = lines[0].strip()
    if not TITLE_PATTERN.search(title):
        errors.append(
            f"TITLE_FORMAT: {path} first line should look like a chapter title, "
            f"e.g. 第十二章 对峙."
        )

    body_lines = lines[2:]
    body_blank_numbers = [i + 3 for i, line in enumerate(body_lines) if not line.strip()]
    if body_blank_numbers:
        sample = ", ".join(map(str, body_blank_numbers[:10]))
        errors.append(
            f"TXT_BLANK_LINES: {path} has {len(body_blank_numbers)} blank body lines "
            f"(first lines: {sample}). Ordinary body paragraphs must not be separated by blank lines."
        )

    body_paragraphs = [(i + 3, line.strip()) for i, line in enumerate(body_lines) if line.strip()]
    body_char_count = sum(len(line) for _, line in body_paragraphs)
    paragraph_count = len(body_paragraphs)
    body_text = "\n".join(text for _, text in body_paragraphs)

    if re.search(r"[一-鿿]\s+(of|the|and|or|in|to|from)\s+[一-鿿]", body_text, re.IGNORECASE):
        errors.append(
            f"FOREIGN_TOKEN_CONTAMINATION: {path} appears to contain an English connector inside Chinese prose."
        )

    # Paragraph density — warning, not error. Threshold depends on chapter function.
    if body_char_count >= NORMAL_CHAPTER_CHAR_THRESHOLD:
        chapter_dir = path.parent
        func = _guess_chapter_function(chapter_dir)
        min_para = MIN_PARAGRAPHS_BY_GENRE.get(func or "", MIN_PARAGRAPHS_BY_GENRE["_default"])
        if paragraph_count < min_para:
            warnings.append(
                f"LOW_PARAGRAPH_DENSITY: {path} has {paragraph_count} body paragraphs for "
                f"{body_char_count} characters (chapter_function={func or 'unknown'}, "
                f"min expected={min_para}). Consider splitting at action changes, speaker changes, "
                "reaction beats, new information, camera shifts, and rhythm pauses."
            )

    # Giant paragraph check — error (clearly unreadable on mobile)
    giant_paragraphs = [
        (line_no, len(text))
        for line_no, text in body_paragraphs
        if len(text) > GIANT_PARAGRAPH_CHARS
    ]
    if giant_paragraphs:
        sample = ", ".join(f"line {line_no}: {length} chars" for line_no, length in giant_paragraphs[:5])
        errors.append(
            f"GIANT_PARAGRAPH: {path} has paragraphs over {GIANT_PARAGRAPH_CHARS} characters "
            f"({sample}). Split at action changes, speaker changes, reaction beats, new facts, "
            "camera shifts, or rhythm pauses."
        )

    # Long paragraph overuse — warning
    long_paragraphs = [
        (line_no, len(text))
        for line_no, text in body_paragraphs
        if len(text) > LONG_PARAGRAPH_CHARS
    ]
    if body_char_count >= NORMAL_CHAPTER_CHAR_THRESHOLD and len(long_paragraphs) > max(3, paragraph_count // 3):
        sample = ", ".join(f"line {line_no}: {length} chars" for line_no, length in long_paragraphs[:5])
        warnings.append(
            f"LONG_PARAGRAPH_OVERUSE: {path} has {len(long_paragraphs)} paragraphs over "
            f"{LONG_PARAGRAPH_CHARS} characters ({sample}). Most body paragraphs should be "
            "40-160 Chinese characters for comfortable mobile reading."
        )

    nb = nonblank(lines)
    if not nb:
        errors.append(f"TXT_EMPTY: {path}")
        return errors, warnings

    # ---- ending checks ----
    ending_window = "\n".join(nb[-8:])
    last = nb[-1]

    # Short atmosphere ending — warning (can be a deliberate stylistic choice)
    if len(last) <= 14 and not last.endswith(("？", "！", "”")):
        warnings.append(
            f"SHORT_ATMOSPHERE_ENDING: {path} last nonblank line is short: {last!r}. "
            "This can be a valid stylistic choice, but verify the chapter does not end on an empty mood beat."
        )

    # Reflective ending — only flag when ending is dominated by internal cognition
    # AND lacks external action signals.
    reflective_hits = []
    for pattern in WEAK_REFLECTIVE_SIGNALS:
        if re.search(pattern, ending_window):
            reflective_hits.append(pattern)

    has_external = _has_external_action_in_window(ending_window)

    if reflective_hits and not has_external:
        warnings.append(
            f"REFLECTIVE_ENDING_RISK: {path} ending matches {reflective_hits} "
            "with no detected external action signal. If the chapter ends on protagonist "
            "recap, abstract planning, or empty mood, consider rewriting to end with "
            "external motion (arrival, action, cost, object, sound, relationship change)."
        )

    # Protagonist thought ending — composite check.
    # Only flag when the final section is dominated by cognition with no external handoff.
    thought_match = re.search(
        r"(他|她|主角|少年|女子|男人|女人).{0,15}(想|知道|明白|意识到|决定|思忖|暗忖|盘算|打算)",
        ending_window,
    )
    if thought_match and not has_external:
        # Check if the thought contains new information release (not just empty reflection)
        thought_sentence = ending_window[thought_match.start():thought_match.end() + 30]
        has_new_info = bool(re.search(r"原来|发现|看到|听到|闻到|摸到|察觉|猜到|终于|竟然|果然|难怪", thought_sentence))
        if not has_new_info:
            warnings.append(
                f"PROTAGONIST_THOUGHT_ENDING: {path} ending section is driven by "
                "protagonist cognition without external action or new information release. "
                "If this is strategic thinking that advances the plot, ignore this warning."
            )

    return errors, warnings


def validate_chapter_artifacts(chapter_dir: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for filename in REQUIRED_CHAPTER_FILES:
        path = chapter_dir / filename
        if not path.exists():
            errors.append(f"MISSING_CHAPTER_FILE: {path}")

    context_pack = chapter_dir / "context_pack.md"
    if context_pack.exists():
        text = context_pack.read_text(encoding="utf-8")
        for section in REQUIRED_CONTEXT_SECTIONS:
            if section not in text:
                warnings.append(f"MISSING_CONTEXT_SECTION: {context_pack} lacks {section}.")
        if (
            "source:" not in text
            and "Source:" not in text
            and "Source Refs" not in text
            and "Source References" not in text
        ):
            warnings.append(
                f"MISSING_SOURCE_REFS: {context_pack} must cite file sources for key claims."
            )

    review = chapter_dir / "review.md"
    if review.exists():
        text = review.read_text(encoding="utf-8")
        for section in REQUIRED_REVIEW_SECTIONS:
            if section not in text:
                warnings.append(f"MISSING_REVIEW_SECTION: {review} lacks {section}.")

    # Handoff checks — accept both old and new field names
    for fname, label in [("summary.yml", "summary"), ("canon_delta.yml", "canon_delta")]:
        path = chapter_dir / fname
        if path.exists():
            text = path.read_text(encoding="utf-8")
            has_handoff = (
                "handoff_to_next_chapter" in text
                or "actual_handoff" in text
                or "planned_handoff" in text
                or "current_handoff" in text
            )
            if not has_handoff:
                errors.append(f"MISSING_HANDOFF: {path} lacks a handoff field.")

    return errors, warnings


def validate_planning(project: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    longform = project / "book" / "longform_blueprint.yml"
    if not longform.exists():
        errors.append(
            f"MISSING_LONGFORM_BLUEPRINT: {longform}. "
            "Create it during bootstrap or migrate the project before writing."
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
                warnings.append(f"LONGFORM_BLUEPRINT_INCOMPLETE: {longform} lacks {field}.")

    planning_files = [
        project / "planning" / "rolling_plan.yml",
        project / "planning" / "current_round.yml",
        project / "planning" / "active_flow.yml",
    ]

    for path in planning_files:
        if not path.exists():
            errors.append(f"MISSING_PLANNING: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in STALE_PLANNING_PATTERNS:
            if re.search(pattern, text):
                errors.append(
                    f"STALE_PLANNING_FIELD: {path} contains old planning language matching /{pattern}/."
                )
        if path.name == "rolling_plan.yml":
            for field in REQUIRED_PLANNING_FIELDS:
                if field not in text:
                    warnings.append(f"MISSING_FLOW_FIELD: {path} lacks {field}.")
        if path.name == "rolling_plan.yml" and re.search(r"\bstatus\s*:\s*completed\b", text):
            errors.append(
                f"COMPLETED_PLAN_NOT_ARCHIVED: {path} contains completed chapters. "
                "Move finished chapter plan entries to planning/completed_plan_log.yml "
                "and keep rolling_plan.yml as the future window."
            )

    for path in [
        project / "planning" / "completed_plan_log.yml",
        project / "planning" / "future_backlog.yml",
    ]:
        if not path.exists():
            warnings.append(f"MISSING_PLANNING: {path}")

    for path in (project / "chapters").glob("ch*/summary.yml"):
        text = path.read_text(encoding="utf-8")
        if re.search(r"\bnext_hook\s*:", text):
            errors.append(
                f"STALE_SUMMARY_FIELD: {path} uses next_hook; use actual_handoff or handoff_to_next_chapter."
            )

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path, help="Novel project path, e.g. projects/my-novel")
    parser.add_argument("--chapters", nargs="*", help="Chapter ids to validate, e.g. ch011 ch012")
    parser.add_argument("--fix-format", action="store_true", help="Remove blank body lines from final.txt")
    parser.add_argument("--skip-planning", action="store_true", help="Skip planning-memory checks")
    parser.add_argument("--skip-artifacts", action="store_true", help="Skip chapter artifact/context/review checks")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()

    project = args.project
    all_errors: list[str] = []
    all_warnings: list[str] = []

    if not project.exists():
        print(f"Project not found: {project}", file=sys.stderr)
        return 2

    if not args.skip_planning:
        errs, warns = validate_planning(project)
        all_errors.extend(errs)
        all_warnings.extend(warns)

    chapters = args.chapters
    if not chapters:
        chapter_root = project / "chapters"
        chapters = sorted(p.name for p in chapter_root.glob("ch*") if p.is_dir())[-3:]

    for chapter in chapters:
        chapter_dir = project / "chapters" / chapter
        if not args.skip_artifacts:
            errs, warns = validate_chapter_artifacts(chapter_dir)
            all_errors.extend(errs)
            all_warnings.extend(warns)
        errs, warns = validate_txt(chapter_dir / "final.txt", args.fix_format, strict=args.strict)
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
