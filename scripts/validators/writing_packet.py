"""Writing packet validator checks."""

from __future__ import annotations

import re
from pathlib import Path


HEADING_PATTERN = re.compile(r"^\s{0,3}(#{1,6})\s*(.+?)\s*$", re.MULTILINE)

BACKGROUND_PLACEHOLDER_PATTERNS = [
    r"待命名",
    r"自行命名",
    r"writer\s*自行",
    r"某宗门",
    r"某长老",
    r"某师兄",
    r"某管事",
    r"background[_ -]?placeholder",
    r"背景占位",
    r"\bTBD\b",
]

REQUIRED_WRITING_PACKET_SECTIONS = [
    ("Read Files", "读取文件", "输入文件清单", "读过的文件"),
    ("Source References", "来源引用", "来源文件", "证据来源"),
    ("Longform Scale Check", "长篇规模检查", "规模检查"),
    ("Reader Reward Check", "读者回报检查", "reader reward check", "读者体验"),
    ("Background Use Audit", "背景使用审计", "背景审计", "背景落库检查"),
    ("Cut Continuity", "切分连续性", "上一章承接", "连续性"),
    ("Writing Card", "正文抬头纸", "写作卡"),
    ("Pre-Draft Self Check", "写前自检", "draft 前自检", "pre draft self check"),
    ("Required Updates After Writing", "写完后必须更新的文件", "写后必须更新", "写完后更新"),
]

WRITING_CARD_REQUIRED_MARKERS = [
    ("chapter_function", "本章功能"),
    ("time_span", "时间跨度"),
    ("ending_type", "结尾类型"),
    ("pressure_curve", "压力曲线"),
    ("position_in_flow", "大弧位置"),
    ("architecture_role", "编剧层角色"),
    ("pacing_mode", "节奏模式"),
    ("world_expansion", "世界扩张"),
    ("protagonist_growth_budget", "主角成长预算"),
    ("writable_scene_seed", "可写场景触发点"),
    ("must_happen", "必须发生"),
    ("must_not_complete", "必须不完成"),
    ("information_release", "信息释放"),
    ("enters_via", "进入方式"),
    ("narrative_weave", "叙事织入"),
    ("opening_sensory", "开头感官"),
    ("voice_examples", "人物语感"),
    ("foreshadowing_weight", "伏笔分量"),
    ("relationship_temperature", "关系温度"),
    ("body_scene_texture", "身体场景质感"),
    ("dialogue_mode", "对话模式"),
    ("scene_moments", "场景瞬间"),
    ("ending_gesture", "结尾动作"),
]


def _normalize_heading(text: str) -> str:
    text = re.sub(r"[`*_：:（）()\[\]【】/／-]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def _has_section(text: str, aliases: tuple[str, ...]) -> bool:
    headings = [_normalize_heading(match.group(2)) for match in HEADING_PATTERN.finditer(text)]
    normalized_aliases = [_normalize_heading(alias) for alias in aliases]
    for heading in headings:
        for alias in normalized_aliases:
            if alias and alias in heading:
                return True
    return False


def _section_label(aliases: tuple[str, ...]) -> str:
    return " / ".join(aliases[:2])


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


def validate_writing_packet(writing_packet: Path, samples_has_content: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    text = writing_packet.read_text(encoding="utf-8")

    for pattern in BACKGROUND_PLACEHOLDER_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            errors.append(
                f"BACKGROUND_PLACEHOLDER: {writing_packet} contains unresolved background placeholder matching /{pattern}/. "
                "Complete and store reusable background in entities/ or ledgers before drafting."
            )

    missing_packet_sections: list[str] = []
    for section_aliases in REQUIRED_WRITING_PACKET_SECTIONS:
        if not _has_section(text, section_aliases):
            missing_packet_sections.append(_section_label(section_aliases))
    if missing_packet_sections:
        errors.append(
            f"WRITING_PACKET_TEMPLATE_BROKEN: {writing_packet} lacks required machine-readable sections: "
            f"{', '.join(missing_packet_sections)}. Use the template headings exactly before drafting."
        )

    if (
        "source:" not in text
        and "Source:" not in text
        and "Source Refs" not in text
        and "Source References" not in text
        and "来源" not in text
    ):
        warnings.append(
            f"MISSING_SOURCE_REFS: {writing_packet} must cite file sources for key claims."
        )

    writing_card = _extract_section(text, ("Writing Card", "正文抬头纸", "写作卡"))
    if not writing_card:
        errors.append(f"WRITING_CARD_MISSING: {writing_packet} must include a Writing Card section.")
        return errors, warnings

    for marker_aliases in WRITING_CARD_REQUIRED_MARKERS:
        if not any(marker in writing_card for marker in marker_aliases):
            warnings.append(
                f"WRITING_CARD_FIELD_MISSING: {writing_packet} Writing Card lacks {' / '.join(marker_aliases)}."
            )

    background_audit = _extract_section(text, ("Background Use Audit", "背景使用审计", "背景审计", "背景落库检查"))
    if background_audit and re.search(r"missing_background\s*:\s*(?!\s*(#|$|\n\s*(-\s*)?$))", background_audit):
        errors.append(
            f"BACKGROUND_AUDIT_UNRESOLVED: {writing_packet} lists missing_background. "
            "Resolve background into entities/ledgers or route to novel-change before drafting."
        )

    if samples_has_content and not re.search(r"(sample_style_anchors|样本.*(文风|风格|锚点)|文笔锚点|从样本提取|sample)", writing_card, re.IGNORECASE):
        warnings.append(
            f"SAMPLE_ANCHORS_MISSING: {writing_packet} Writing Card should include 3-5 positive style anchors "
            "from style/samples.md when samples are available."
        )
    if "Chapter Design" not in writing_card and "设计面" not in writing_card:
        warnings.append(
            f"WRITING_CARD_DESIGN_BLOCK_MISSING: {writing_packet} should separate Chapter Design from prose execution."
        )
    if "Writing Execution" not in writing_card and "执行面" not in writing_card:
        warnings.append(
            f"WRITING_CARD_EXECUTION_BLOCK_MISSING: {writing_packet} should include writable scene moments, not only task goals."
        )

    writer_material_fields = [
        "voice_examples",
        "foreshadowing_weight",
        "relationship_temperature",
        "body_scene_texture",
        "dialogue_mode",
    ]
    missing_writer_material = [field for field in writer_material_fields if field not in writing_card]
    if missing_writer_material:
        warnings.append(
            f"WRITER_CONTEXT_THIN: {writing_packet} Writing Card lacks writer-specific prose material: "
            f"{', '.join(missing_writer_material)}."
        )

    if re.search(r"new_core_variables\s*:\s*(?!\n\s*-)", writing_card) and "enters_via" not in writing_card:
        warnings.append(
            f"INFORMATION_ENTRY_MODE_MISSING: {writing_packet} should state enters_via for each core variable."
        )

    prose_input = re.split(r"\n\s*-\s*prose_constraints\s*:", writing_card, maxsplit=1)[0]
    if re.search(r"禁止.*不是X.*是Y|not-but", writing_card, re.IGNORECASE) and re.search(
        r"(opening_sensory|scene_moments|voice_examples|sample_style_anchors|开头感官|场景瞬间|人物语感|样本).{0,300}不是.{0,12}(而是|，是|。是)",
        prose_input,
        re.DOTALL,
    ):
        errors.append(
            f"WRITING_PACKET_CONSTRAINT_CONFLICT: {writing_packet} bans not-but contrast but includes "
            "not-but examples in prose input fields. Remove the example before calling writer."
        )

    return errors, warnings
