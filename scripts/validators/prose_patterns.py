"""Prose pattern diversity validator checks."""

from __future__ import annotations

import re
from pathlib import Path


REPETITIVE_SENTENCE_PATTERNS = [
    (r"并非.{0,30}(而是|是)", "并非X而是Y"),
    (r"没有.{0,10}(害怕|紧张|恐惧|担心|犹豫|迟疑)", "没有害怕/紧张/恐惧/担心..."),
]

NOT_BUT_PATTERN = re.compile(r"(?<![是岂])不是(?:(?!不是).){0,30}(?:而是|[，,。；;\s]+是)")
TRIPLE_NEGATED_INNER_STATE_PATTERN = re.compile(
    r"没有(?:分析|想|评估|判断|琢磨|权衡|害怕|紧张|犹豫).{0,24}"
    r"没有(?:分析|想|评估|判断|琢磨|权衡|害怕|紧张|犹豫).{0,24}"
    r"没有(?:分析|想|评估|判断|琢磨|权衡|害怕|紧张|犹豫)"
)
META_ORIGINAL_TEXT_PATTERN = re.compile(r"原书中|在原书里|按照原著|原著里|原文中")
ARROW_OR_NUMBERED_COGNITION_PATTERN = re.compile(
    r"(?:她|他|我|主角).{0,18}(?:想|判断|意识到|明白|确定).{0,24}(?:->|→|⇒|=>|第一|第二|第三|其一|其二)"
)
MAX_NOT_BUT_PER_CHAPTER = 1


def _has_contrast_negation_justification(review_text: str) -> bool:
    """Require a filled justification, not just an unanswered review prompt."""
    empty_values = {"", "n/a", "na", "none", "无", "没有", "未使用", "不适用"}
    for raw_line in review_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if not re.search(r"(not[-_ ]?but|不是X而是Y|不是X，是Y|不是.*而是|不是.*，是)", line, re.IGNORECASE):
            continue
        if re.search(r"\bnot_but_justification\s*:", line, re.IGNORECASE):
            value = re.sub(r"^[-*]\s*", "", line)
            value = re.sub(r"(?i)^not_but_justification\s*:\s*", "", value).strip()
            value = re.sub(r"\s*[（(].*?[）)]\s*$", "", value).strip()
            if value.lower() not in empty_values:
                return True
            continue
        if "是否" in line or line.endswith(("?", "？")):
            continue
        if re.search(r"(保留|使用).{0,30}(因为|用于|体现|必须|不可替代|对比价值)", line):
            return True
    return False


def check_prose_patterns(path: Path) -> tuple[list[str], list[str]]:
    """Check for overused sentence patterns in chapter prose."""
    errors: list[str] = []
    warnings: list[str] = []
    text = path.read_text(encoding="utf-8")
    flat = text.replace("\n", "")

    not_but_count = len(NOT_BUT_PATTERN.findall(flat))
    if not_but_count > MAX_NOT_BUT_PER_CHAPTER:
        errors.append(
            f"OVERUSED_NOT_BUT_PATTERN: {path} uses '不是X而是Y / 不是X，是Y' "
            f"{not_but_count} times; max allowed is {MAX_NOT_BUT_PER_CHAPTER}. "
            "This sentence shape is reserved for one deliberate contrast per chapter. "
            "Rewrite the rest as direct observation, action, dialogue, image, or consequence."
        )
    elif not_but_count == 1:
        review = path.parent / "review.md"
        review_text = review.read_text(encoding="utf-8") if review.exists() else ""
        if not _has_contrast_negation_justification(review_text):
            warnings.append(
                f"CONTRAST_NEGATION_JUSTIFICATION_MISSING: {path} uses one not-but contrast. "
                "This is allowed only when review.md states why the contrast is not replaceable."
            )

    hard_patterns = [
        (TRIPLE_NEGATED_INNER_STATE_PATTERN, "TRIPLE_NEGATED_INNER_STATE", "三连否定声明内心状态"),
        (META_ORIGINAL_TEXT_PATTERN, "META_ORIGINAL_TEXT", "原书/原著元叙述"),
        (ARROW_OR_NUMBERED_COGNITION_PATTERN, "ARROW_OR_NUMBERED_COGNITION", "箭头/编号式认知总结"),
    ]
    for pattern, code, label in hard_patterns:
        count = len(pattern.findall(flat))
        if count:
            errors.append(
                f"{code}: {path} contains {count} {label} pattern(s). "
                "Move the information into action, dialogue, consequence, or scene texture."
            )

    for pattern, label in REPETITIVE_SENTENCE_PATTERNS:
        count = len(re.findall(pattern, flat))
        if count >= 8:
            warnings.append(
                f"REPETITIVE_PATTERN: {path} uses '{label}' {count} times. "
                "Overuse makes prose feel like a series of footnotes. "
                "Vary sentence structure: some observations can stand without negation."
            )
    return errors, warnings
