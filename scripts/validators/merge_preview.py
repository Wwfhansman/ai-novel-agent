"""Merge preview validator checks."""

from __future__ import annotations

import re
from pathlib import Path


def _mentions_any_chapter(text: str, chapters: list[str]) -> bool:
    if not chapters:
        return True
    return any(re.search(rf"(?<![A-Za-z0-9_]){re.escape(chapter)}(?![A-Za-z0-9_])", text) for chapter in chapters)


def _artifact_chapters(text: str) -> set[str]:
    chapters: set[str] = set()
    cover_match = re.search(r"(?m)^\s*[-*]?\s*覆盖章节[：:]\s*(.+)$", text)
    if cover_match:
        chapters.update(re.findall(r"ch\d{3,}", cover_match.group(1)))

    yaml_match = re.search(r"(?ms)^chapters\s*:\s*\n(?P<block>(?:^\s*-\s*ch\d{3,}.*(?:\n|$))+)", text)
    if yaml_match:
        chapters.update(re.findall(r"(?m)^\s*-\s*(ch\d{3,})\b", yaml_match.group("block")))
    return chapters


def _artifact_relevant_to_chapters(text: str, chapters: list[str]) -> bool:
    if not chapters:
        return True
    artifact_chapters = _artifact_chapters(text)
    if artifact_chapters:
        return bool(artifact_chapters.intersection(chapters))
    return _mentions_any_chapter(text, chapters)


def validate_merge_previews(project: Path, chapters: list[str]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    preview_dir = project / "planning" / "merge_previews"
    if not preview_dir.exists():
        if any((project / "chapters" / chapter / "memory_update_plan.md").exists() for chapter in chapters):
            errors.append(
                f"MERGE_PREVIEW_MISSING: {preview_dir} is missing. "
                "Generate a merge preview before post-merge QA."
            )
        return errors, warnings

    preview_texts: list[tuple[Path, str]] = []
    for preview in sorted(preview_dir.glob("*.yml")):
        text = preview.read_text(encoding="utf-8")
        if chapters and not _artifact_relevant_to_chapters(text, chapters):
            continue
        preview_texts.append((preview, text))
        if re.search(r"(?m)^\s*project\s*:\s*template\s*$", text) or re.search(r"(?m)^\s*generated_at\s*:\s*template\s*$", text):
            errors.append(
                f"MERGE_PREVIEW_TEMPLATE_PLACEHOLDER: {preview} is still the template placeholder. "
                "Regenerate it with scripts/round_state_merge.py preview for the real project and round."
            )
        if "operations:" not in text:
            warnings.append(f"MERGE_PREVIEW_INCOMPLETE: {preview} lacks operations.")
        blocks = re.split(r"\n\s*-\s+op\s*:", "\n" + text)
        for block in blocks[1:]:
            if re.search(r"\bconfidence\s*:\s*high\b", block) and re.search(r"\bstatus\s*:\s*pending\b", block):
                errors.append(
                    f"MERGE_PREVIEW_PENDING_HIGH_CONFIDENCE: {preview} has a high-confidence pending operation. "
                    "Apply it with scripts/round_state_merge.py apply or move it to manual_review with a reason."
                )
        manual_review_match = re.search(r"(?ms)^manual_review\s*:\s*\n(?P<block>(?:^\s*-\s+.*(?:\n|$))+)", text)
        if manual_review_match:
            errors.append(
                f"MERGE_PREVIEW_MANUAL_REVIEW_UNRESOLVED: {preview} still has manual_review items. "
                "Resolve or explicitly move them to the chapter review before post-merge QA."
            )

    if any((project / "chapters" / chapter / "memory_update_plan.md").exists() for chapter in chapters):
        for chapter in chapters:
            if not any(re.search(rf"(^|\n)\s*-\s*{re.escape(chapter)}\s*(\n|$)", text) for _, text in preview_texts):
                errors.append(
                    f"MERGE_PREVIEW_CHAPTER_MISSING: no merge preview in {preview_dir} lists {chapter}. "
                    "Generate scripts/round_state_merge.py preview for the completed batch."
                )
    return errors, warnings
