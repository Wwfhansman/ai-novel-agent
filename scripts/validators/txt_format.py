"""Chapter TXT format and ending validator checks."""

from __future__ import annotations

import re
from pathlib import Path


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

ENDING_EXTERNAL_ACTION_SIGNALS = [
    r"推门|开门|走出|跑|追|喊|叫|动手|出手|拔剑|拔刀|落地|脚步声|马蹄",
    r"出现|赶到|闯|冲|拦|挡|抓住|松开|递|扔|砸|碎|裂",
    r"抬头|低头|起身|站起|转身|回头|停下",
    r"开口|出声|笑|哭|喘|吼|骂|沉默|不说话",
]

MIN_PARAGRAPHS_BY_GENRE = {
    "crisis": 15,
    "face_slap": 15,
    "breakthrough": 15,
    "competition": 15,
    "showing_off": 15,
    "investigation": 20,
    "reveal": 20,
    "dungeon_rule": 20,
    "auction": 20,
    "building": 25,
    "relationship": 25,
    "domestic_management": 25,
    "aftermath": 25,
    "transition": 25,
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
    for pattern in ENDING_EXTERNAL_ACTION_SIGNALS:
        if re.search(pattern, text):
            return True
    return False


def _guess_chapter_function(chapter_dir: Path) -> str | None:
    """Try to read chapter_function from writing_packet.md or summary.yml."""
    for fname in ("writing_packet.md", "summary.yml"):
        path = chapter_dir / fname
        if path.exists():
            text = path.read_text(encoding="utf-8")
            match = re.search(r"chapter_function\s*:\s*(\S+)", text)
            if match:
                return match.group(1).strip().strip('"').strip("'")
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
    body_blank_numbers = [index + 3 for index, line in enumerate(body_lines) if not line.strip()]
    if body_blank_numbers:
        sample = ", ".join(map(str, body_blank_numbers[:10]))
        errors.append(
            f"TXT_BLANK_LINES: {path} has {len(body_blank_numbers)} blank body lines "
            f"(first lines: {sample}). Ordinary body paragraphs must not be separated by blank lines."
        )

    body_paragraphs = [(index + 3, line.strip()) for index, line in enumerate(body_lines) if line.strip()]
    body_char_count = sum(len(line) for _, line in body_paragraphs)
    paragraph_count = len(body_paragraphs)
    body_text = "\n".join(text for _, text in body_paragraphs)

    if re.search(r"[一-鿿]\s+(of|the|and|or|in|to|from)\s+[一-鿿]", body_text, re.IGNORECASE):
        errors.append(
            f"FOREIGN_TOKEN_CONTAMINATION: {path} appears to contain an English connector inside Chinese prose."
        )

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

    ending_window = "\n".join(nb[-8:])
    last = nb[-1]

    if len(last) <= 14 and not last.endswith(("？", "！", "”")):
        warnings.append(
            f"SHORT_ATMOSPHERE_ENDING: {path} last nonblank line is short: {last!r}. "
            "This can be a valid stylistic choice, but verify the chapter does not end on an empty mood beat."
        )

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

    thought_match = re.search(
        r"(他|她|主角|少年|女子|男人|女人).{0,15}(想|知道|明白|意识到|决定|思忖|暗忖|盘算|打算)",
        ending_window,
    )
    if thought_match and not has_external:
        thought_sentence = ending_window[thought_match.start():thought_match.end() + 30]
        has_new_info = bool(re.search(r"原来|发现|看到|听到|闻到|摸到|察觉|猜到|终于|竟然|果然|难怪", thought_sentence))
        if not has_new_info:
            warnings.append(
                f"PROTAGONIST_THOUGHT_ENDING: {path} ending section is driven by "
                "protagonist cognition without external action or new information release. "
                "If this is strategic thinking that advances the plot, ignore this warning."
            )

    return errors, warnings
