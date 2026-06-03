"""Profile-driven TXT format / paragraph-density check.

Ports the format half of the legacy scripts/validators/txt_format.py, but reads
every threshold from the profile (prose.* + prose.min_paragraphs_by_genre)
instead of hardcoding them — closing the loop so the profile's prose block
actually drives a check, and making the same engine usable for other genres.

Scope: blank-line / giant-paragraph / long-paragraph / paragraph-density /
title format. The fuzzy ending heuristics stay in the legacy validator.
"""

from __future__ import annotations

import re
from pathlib import Path

_TITLE_PATTERN = re.compile(r"^第[一二三四五六七八九十百千万零〇两0-9]+章\s*\S+")


def check_txt(path: Path, profile: dict, chapter_function: str | None = None) -> tuple[list[str], list[str]]:
    path = Path(path)
    errors: list[str] = []
    warnings: list[str] = []
    if not path.exists():
        return [f"MISSING_FILE: {path}"], warnings

    prose = (profile or {}).get("prose", {}) or {}
    normal_threshold = prose.get("normal_chapter_char_threshold", 1800)
    giant = prose.get("giant_paragraph_chars", 220)
    long_chars = prose.get("long_paragraph_chars", 160)
    min_by_genre = prose.get("min_paragraphs_by_genre", {})

    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 3:
        return [f"TXT_TOO_SHORT: {path}"], warnings

    title = lines[0].strip()
    if not _TITLE_PATTERN.search(title):
        errors.append(f"TITLE_FORMAT: {path} first line should be a chapter title, e.g. 第十二章 对峙.")

    body_lines = lines[2:]
    blank = [i + 3 for i, line in enumerate(body_lines) if not line.strip()]
    if blank:
        errors.append(
            f"TXT_BLANK_LINES: {path} has {len(blank)} blank body line(s) "
            f"(first: {', '.join(map(str, blank[:10]))}). Body paragraphs must not be blank-separated."
        )

    paragraphs = [(i + 3, line.strip()) for i, line in enumerate(body_lines) if line.strip()]
    body_chars = sum(len(text) for _, text in paragraphs)
    count = len(paragraphs)

    giant_paras = [(n, len(t)) for n, t in paragraphs if len(t) > giant]
    if giant_paras:
        sample = ", ".join(f"line {n}: {ln} chars" for n, ln in giant_paras[:5])
        errors.append(
            f"GIANT_PARAGRAPH: {path} has paragraph(s) over {giant} chars ({sample}). "
            "Split at action/speaker/reaction/new-fact/camera/rhythm changes."
        )

    if body_chars >= normal_threshold:
        min_para = min_by_genre.get(chapter_function or "", min_by_genre.get("_default", 25))
        if count < min_para:
            warnings.append(
                f"LOW_PARAGRAPH_DENSITY: {path} has {count} paragraphs for {body_chars} chars "
                f"(chapter_function={chapter_function or 'unknown'}, min expected={min_para})."
            )
        long_paras = [(n, len(t)) for n, t in paragraphs if len(t) > long_chars]
        if len(long_paras) > max(3, count // 3):
            sample = ", ".join(f"line {n}: {ln}" for n, ln in long_paras[:5])
            warnings.append(
                f"LONG_PARAGRAPH_OVERUSE: {path} has {len(long_paras)} paragraphs over {long_chars} chars "
                f"({sample}). Most should be {prose.get('paragraph_min_chars', 40)}-{long_chars} chars."
            )

    return errors, warnings
