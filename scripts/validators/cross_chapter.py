"""Cross-chapter validator checks."""

from __future__ import annotations

import re
from pathlib import Path


HEADING_PATTERN = re.compile(r"^\s{0,3}(#{1,6})\s*(.+?)\s*$", re.MULTILINE)
NOT_BUT_PATTERN = re.compile(r"(?<![是岂])不是(?:(?!不是).){0,30}(?:而是|[，,。；;\s]+是)")
MAX_NOT_BUT_PER_CHAPTER = 1


def _chapter_sort_key(chapter: str) -> int:
    match = re.search(r"ch(\d+)", chapter)
    return int(match.group(1)) if match else -1


def _normalize_heading(text: str) -> str:
    text = re.sub(r"[`*_：:（）()\[\]【】/／-]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def _extract_section(text: str, aliases: tuple[str, ...]) -> str:
    matches = list(HEADING_PATTERN.finditer(text))
    normalized_aliases = [_normalize_heading(alias) for alias in aliases]
    for index, match in enumerate(matches):
        heading = _normalize_heading(match.group(2))
        if any(alias and alias in heading for alias in normalized_aliases):
            level = len(match.group(1))
            start = match.end()
            end = len(text)
            for next_match in matches[index + 1:]:
                if len(next_match.group(1)) <= level:
                    end = next_match.start()
                    break
            return text[start:end].strip()
    return ""


def _extract_markdown_field(text: str, field: str) -> str:
    pattern = re.compile(rf"^\s*[-*]?\s*{re.escape(field)}\s*:\s*(.*?)\s*$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    value = match.group(1).strip().strip('"').strip("'")
    value = re.sub(r"\s*#.*$", "", value).strip()
    return value


def _read_writing_packet_fields(project: Path, chapter: str) -> dict[str, str]:
    path = project / "chapters" / chapter / "writing_packet.md"
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    card = _extract_section(text, ("Writing Card", "正文抬头纸", "写作卡")) or text
    return {
        "time_span": _extract_markdown_field(card, "time_span"),
        "ending_type": _extract_markdown_field(card, "ending_type"),
        "position_in_flow": _extract_markdown_field(card, "position_in_flow"),
    }


def validate_cross_chapter_patterns(project: Path, chapters: list[str]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    ordered = sorted(chapters, key=_chapter_sort_key)
    fields = [(chapter, _read_writing_packet_fields(project, chapter)) for chapter in ordered]

    next_step_chain = [
        chapter for chapter, data in fields
        if data.get("ending_type", "").strip().lower().startswith("next_step_decision")
    ]
    if len(next_step_chain) >= 3:
        errors.append(
            "NARRATIVE_CONTAINER_LOOP: three or more checked chapters use ending_type=next_step_decision "
            f"({', '.join(next_step_chain)}). Cut at action, arrival, interruption, or cost instead."
        )

    one_day_chain = [
        chapter for chapter, data in fields
        if data.get("time_span", "").strip() in {"一天", "一日", "one_day", "1 day", "1day"}
    ]
    if len(one_day_chain) >= 3:
        warnings.append(
            "SINGLE_DAY_CHAPTER_CHAIN: three or more checked chapters use time_span=一天 "
            f"({', '.join(one_day_chain)}). Verify the story is not becoming one-day-one-task containers."
        )

    flat_positions = [
        chapter for chapter, data in fields
        if data.get("position_in_flow", "").strip().lower() in {"opening", "aftermath_trough"}
    ]
    if len(flat_positions) >= 3:
        warnings.append(
            "FLOW_POSITION_LOOP: checked chapters mostly sit at opening/aftermath positions "
            f"({', '.join(flat_positions)}). Verify the active flow is actually escalating."
        )

    chapters_with_not_but_over_limit: list[str] = []
    for chapter in ordered:
        final_txt = project / "chapters" / chapter / "final.txt"
        if final_txt.exists():
            flat = final_txt.read_text(encoding="utf-8").replace("\n", "")
            if len(NOT_BUT_PATTERN.findall(flat)) > MAX_NOT_BUT_PER_CHAPTER:
                chapters_with_not_but_over_limit.append(chapter)
    if len(chapters_with_not_but_over_limit) >= 2:
        errors.append(
            "BATCH_OVERUSED_CONTRAST_NEGATION: more than one checked chapter exceeds the not-but limit "
            f"({', '.join(chapters_with_not_but_over_limit)}). Fix draft/final before post-merge QA."
        )

    return errors, warnings
