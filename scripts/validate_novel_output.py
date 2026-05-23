#!/usr/bin/env python3
"""Validate AI Novel Agent chapter output for common failure modes.

Checks: missing chapter artifacts, weak writing packets, TXT blank lines,
paragraph density, reflective endings, short atmosphere endings, and stale
planning fields.

Ending checks now use composite pattern detection instead of single-keyword
matching, to avoid false positives on normal Chinese web-novel prose.
Paragraph density thresholds are advisory (warnings) with genre-aware lower
bounds instead of a single hard minimum.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
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
    ("macro_stage",),
    ("scale_level",),
    ("cross_chapter_event",),
    ("starts_mid_action",),
    ("ends_mid_action",),
    ("chapter_function",),
    ("pressure_curve",),
    ("position_in_flow",),
    ("reader_question_flow",),
    ("core_advance",),
    ("information_release",),
    ("chapter_turn",),
    ("side_yield",),
    ("planned_handoff",),
    ("叙事织入", "narrative_weave"),
]

REQUIRED_CHAPTER_FILES = [
    "writing_packet.md",
    "draft.txt",
    "final.txt",
    "review.md",
    "summary.yml",
    "canon_delta.yml",
]

QUALITY_GATE_FILES = [
    "reader_pass.md",
    "memory_update_plan.md",
]

REQUIRED_WRITING_PACKET_SECTIONS = [
    ("Read Files", "读取文件", "输入文件清单", "读过的文件"),
    ("Source References", "来源引用", "来源文件", "证据来源"),
    ("Longform Scale Check", "长篇规模检查", "规模检查"),
    ("Reader Reward Check", "读者回报检查", "reader reward check", "读者体验"),
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
    ("must_happen", "必须发生"),
    ("must_not_complete", "必须不完成"),
    ("information_release", "信息释放"),
    ("enters_via", "进入方式"),
    ("narrative_weave", "叙事织入"),
    ("opening_sensory", "开头感官"),
    ("scene_moments", "场景瞬间"),
    ("ending_gesture", "结尾动作"),
]

REQUIRED_REVIEW_SECTIONS = [
    ("Reader Reward Check", "读者回报检查", "读者体验"),
    ("TXT Format Check", "TXT 格式检查", "正文质量", "格式"),
    ("Memory Update Check", "记忆更新检查", "工程状态", "记忆工程卫生检查"),
]

PROTECTED_FILES = [
    "book/constitution.md",
    "book/longform_blueprint.yml",
    "book/reader_model.yml",
    "book/style_memory.md",
    "book/endgame_hypotheses.yml",
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
ROLLING_PLAN_SIZE_WARN_BYTES = 20000
TITLE_PATTERN = re.compile(r"^第[一二三四五六七八九十百千万零〇两0-9]+章\s*\S+")
HEADING_PATTERN = re.compile(r"^\s{0,3}#{1,6}\s*(.+?)\s*$", re.MULTILINE)


def nonblank(lines: list[str]) -> list[str]:
    return [line.strip() for line in lines if line.strip()]


def _normalize_heading(text: str) -> str:
    text = re.sub(r"[`*_：:（）()\[\]【】/／-]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def _has_section(text: str, aliases: tuple[str, ...]) -> bool:
    headings = [_normalize_heading(match.group(1)) for match in HEADING_PATTERN.finditer(text)]
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
        heading = _normalize_heading(match.group(1))
        if any(alias and alias in heading for alias in normalized_aliases):
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
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
    """Try to read chapter_function from writing_packet.md or summary.yml."""
    for fname in ("writing_packet.md", "summary.yml"):
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

    for filename in QUALITY_GATE_FILES:
        path = chapter_dir / filename
        if not path.exists():
            warnings.append(
                f"MISSING_QUALITY_GATE: {path} is missing. New workflow expects this file before accepting final.txt."
            )

    reader_pass = chapter_dir / "reader_pass.md"
    reader_requested_revision = False
    if reader_pass.exists():
        text = reader_pass.read_text(encoding="utf-8")
        reader_requested_revision = bool(
            re.search(r"(是否允许进入\s*final|final verdict|verdict)\s*[:：]?\s*\n\s*revise required\b", text, re.IGNORECASE)
            or re.search(
                r"^\s*(是否允许进入\s*final|final verdict|verdict)\s*[:：]\s*revise required\b",
                text,
                re.IGNORECASE | re.MULTILINE,
            )
        )
        if reader_requested_revision:
            recheck = chapter_dir / "reader_recheck.md"
            if not recheck.exists():
                errors.append(
                    f"READER_PASS_BLOCKED: {reader_pass} records revise required and {recheck} is missing; "
                    f"add {recheck} with verdict: pass after revising draft."
                )
            else:
                recheck_text = recheck.read_text(encoding="utf-8")
                if not re.search(r"(verdict|是否允许进入\s*final|结果)\s*[:：]?\s*(pass|通过)", recheck_text, re.IGNORECASE):
                    errors.append(
                        f"READER_RECHECK_NOT_PASS: {recheck} must record verdict: pass after fixing reader blockers."
                    )
        if "最值得保留的一段" not in text and "Passage Worth Keeping" not in text:
            warnings.append(
                f"READER_PASS_INCOMPLETE: {reader_pass} should identify a passage worth keeping."
            )
        if "cold_reader_subagent" not in text and "same_agent_fallback" not in text:
            warnings.append(
                f"READER_PASS_READER_UNSPECIFIED: {reader_pass} should record cold_reader_subagent or same_agent_fallback."
            )
        if "局部润色建议" not in text and "Prose Polish" not in text:
            warnings.append(
                f"READER_PASS_POLISH_MISSING: {reader_pass} should include local prose polish suggestions "
                "for stiff phrasing, odd cuts, unnatural description, or dialogue rhythm."
            )

    memory_plan = chapter_dir / "memory_update_plan.md"
    if memory_plan.exists():
        text = memory_plan.read_text(encoding="utf-8")
        if not re.search(r"status\s*:\s*(ready_for_director_merge|needs_director_review)", text):
            warnings.append(
                f"MEMORY_PLAN_STATUS_MISSING: {memory_plan} should record status: "
                "ready_for_director_merge / needs_director_review."
            )
        if not re.search(r"evidence|证据", text, re.IGNORECASE):
            warnings.append(
                f"MEMORY_PLAN_EVIDENCE_MISSING: {memory_plan} should cite evidence from final.txt "
                "for proposed memory changes."
            )
        if re.search(r"(已在\s*director\s*监督下直接更新|本章已完成的更新|以下文件已.*直接更新|已直接更新|##\s*合并判断|已合并文件|director\s*已审核并合并)", text):
            errors.append(
                f"ARCHIVIST_DIRECT_MERGE_CLAIM: {memory_plan} claims files were directly updated. "
                "memory_update_plan.md must remain a draft proposal; director merge status belongs in review.md."
            )
        line_count = len([line for line in text.splitlines() if line.strip()])
        if line_count > 60:
            warnings.append(
                f"MEMORY_PLAN_TOO_LONG: {memory_plan} has {line_count} nonblank lines. "
                "v2 expects a diff-only plan around 50 lines; remove summary restatement and full YAML drafts."
            )
        for section_aliases in [
            ("Coverage Gaps", "覆盖缺口"),
            ("State Update Candidates", "状态更新候选"),
            ("Planning Update Candidates", "规划更新候选"),
            ("Manual Review", "人工复核"),
            ("Merge Boundary", "合并边界"),
        ]:
            if not _has_section(text, section_aliases):
                warnings.append(
                    f"MEMORY_PLAN_SECTION_MISSING: {memory_plan} lacks {_section_label(section_aliases)}."
                )
        if re.search(r"```yaml|##\s*(Chapter Summary Draft|Canon Delta Draft)|detailed_summary\s*:|characters_present\s*:", text):
            warnings.append(
                f"MEMORY_PLAN_FULL_YAML_DRAFT: {memory_plan} appears to include full YAML drafts. "
                "v2 archivist output should be diff-only candidates."
            )

    project = chapter_dir.parent.parent
    samples = project / "style" / "samples.md"
    samples_has_content = False
    if samples.exists():
        sample_text = samples.read_text(encoding="utf-8").strip()
        samples_has_content = bool(sample_text) and "占位" not in sample_text and "暂无" not in sample_text

    writing_packet = chapter_dir / "writing_packet.md"
    if writing_packet.exists():
        text = writing_packet.read_text(encoding="utf-8")
        for section_aliases in REQUIRED_WRITING_PACKET_SECTIONS:
            if not _has_section(text, section_aliases):
                warnings.append(
                    f"MISSING_WRITING_PACKET_SECTION: {writing_packet} lacks {_section_label(section_aliases)}."
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
            warnings.append(f"WRITING_CARD_MISSING: {writing_packet} must include a Writing Card section.")
        else:
            for en_marker, zh_marker in WRITING_CARD_REQUIRED_MARKERS:
                if en_marker not in writing_card and zh_marker not in writing_card:
                    warnings.append(
                        f"WRITING_CARD_FIELD_MISSING: {writing_packet} Writing Card lacks {en_marker} / {zh_marker}."
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
            if re.search(r"new_core_variables\s*:\s*(?!\n\s*-)", writing_card) and "enters_via" not in writing_card:
                warnings.append(
                    f"INFORMATION_ENTRY_MODE_MISSING: {writing_packet} should state enters_via for each core variable."
                )
    elif samples_has_content:
        # The missing required file error is emitted above; keep this branch quiet.
        pass

    review = chapter_dir / "review.md"
    if review.exists():
        text = review.read_text(encoding="utf-8")
        for section_aliases in REQUIRED_REVIEW_SECTIONS:
            if not _has_section(text, section_aliases):
                warnings.append(
                    f"MISSING_REVIEW_SECTION: {review} lacks {_section_label(section_aliases)}."
                )
        if samples_has_content and not _has_section(text, ("Sample Alignment Check", "样本文风对齐", "文风对齐")):
            warnings.append(
                f"MISSING_REVIEW_SECTION: {review} lacks Sample Alignment Check / 样本文风对齐 "
                "while style/samples.md has content."
            )
        stale_markers = [
            (chapter_dir / "memory_update_plan.md", r"memory_update_plan\.md\s*(尚未生成|未生成|待.*生成|将在.*生成)"),
            (chapter_dir / "summary.yml", r"summary\.yml\s*(⏳|尚未生成|未生成|待.*生成)"),
            (chapter_dir / "canon_delta.yml", r"canon_delta\.yml\s*(⏳|尚未生成|未生成|待.*生成)"),
            (chapter_dir / "reader_pass.md", r"reader_pass\.md\s*(尚未生成|未生成|待.*生成)"),
        ]
        for artifact, pattern in stale_markers:
            if artifact.exists() and re.search(pattern, text, re.IGNORECASE):
                errors.append(
                    f"STALE_REVIEW_STATUS: {review} still says {artifact.name} is pending/missing, "
                    "but the file exists. Refresh review.md after final reconciliation."
                )
        memory_plan = chapter_dir / "memory_update_plan.md"
        if memory_plan.exists() and not re.search(
            r"(Post[- ]Merge QA|最终\s*QA|最终验证|最终校验|Validation passed|validator.*(通过|passed))",
            text,
            re.IGNORECASE,
        ):
            errors.append(
                f"POST_MERGE_QA_MISSING: {review} must record the final post-merge QA/validator result. "
                "Run QA after director merges memory and planning updates; pre-merge QA is not enough."
            )
        unresolved_state_checks = [
            r"-\s*\[\s*\]\s*`canon_delta\.yml`.*state_sync",
            r"-\s*\[\s*\]\s*`entities/`.*当前状态变化已同步",
            r"-\s*\[\s*\]\s*`ledgers/`.*当前状态变化已同步",
            r"-\s*\[\s*\]\s*`planning/active_flow\.yml`.*已更新",
            r"-\s*\[\s*\]\s*`planning/rolling_plan\.yml`.*已刷新",
            r"-\s*\[\s*\]\s*`planning/merge_previews/.*`.*",
        ]
        for pattern in unresolved_state_checks:
            if re.search(pattern, text):
                errors.append(
                    f"UNRESOLVED_STATE_SYNC_CHECKLIST: {review} still has unchecked current-state "
                    "sync items. Do not pass post-merge QA with canon_delta.yml updated but "
                    "entities/ledgers/planning left stale. Mark the item done or explicitly note N/A."
                )

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
        preview_texts.append((preview, text))
        if "operations:" not in text:
            warnings.append(f"MERGE_PREVIEW_INCOMPLETE: {preview} lacks operations.")
        # Conservative text-level block detector: a high-confidence operation
        # left pending after post-merge means the director has not closed the
        # mechanical merge loop.
        blocks = re.split(r"\n\s*-\s+op\s*:", "\n" + text)
        for block in blocks[1:]:
            if re.search(r"\bconfidence\s*:\s*high\b", block) and re.search(r"\bstatus\s*:\s*pending\b", block):
                errors.append(
                    f"MERGE_PREVIEW_PENDING_HIGH_CONFIDENCE: {preview} has a high-confidence pending operation. "
                    "Apply it with scripts/round_state_merge.py apply or move it to manual_review with a reason."
                )
    if any((project / "chapters" / chapter / "memory_update_plan.md").exists() for chapter in chapters):
        for chapter in chapters:
            if not any(re.search(rf"(^|\n)\s*-\s*{re.escape(chapter)}\s*(\n|$)", text) for _, text in preview_texts):
                errors.append(
                    f"MERGE_PREVIEW_CHAPTER_MISSING: no merge preview in {preview_dir} lists {chapter}. "
                    "Generate scripts/round_state_merge.py preview for the completed batch."
                )
    return errors, warnings


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


def validate_planning(project: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    errs, warns = validate_project_yaml(project)
    errors.extend(errs)
    warnings.extend(warns)

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
            for aliases in REQUIRED_PLANNING_FIELDS:
                if not any(field in text for field in aliases):
                    warnings.append(f"MISSING_FLOW_FIELD: {path} lacks {' / '.join(aliases)}.")
            rp_size = len(text.encode("utf-8"))
            if rp_size > ROLLING_PLAN_SIZE_WARN_BYTES:
                warnings.append(
                    f"ROLLING_PLAN_SIZE_LARGE: {path} is {rp_size} bytes. "
                    "Keep rolling_plan.yml to the active 6-10 chapter window when possible; move "
                    "far-future entries into planning/future_backlog.yml without thinning near-term prose-critical plans."
                )
        if path.name == "rolling_plan.yml" and re.search(r"\bstatus\s*:\s*completed\b", text):
            errors.append(
                f"COMPLETED_PLAN_NOT_ARCHIVED: {path} contains completed chapters. "
                "Move finished chapter plan entries to planning/completed_plan_log.yml "
                "and keep rolling_plan.yml as the future window."
            )

    errors.extend(_validate_planning_state_uniqueness(project))

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
                f"STALE_SUMMARY_FIELD: {path} uses next_hook; use actual_handoff."
            )

    # YAML duplicate key check for critical state files
    yaml_files = list((project / "entities").glob("*.yml"))
    yaml_files += list((project / "ledgers").glob("*.yml"))
    yaml_files += [
        project / "planning" / "active_flow.yml",
        project / "planning" / "rolling_plan.yml",
    ]
    for yf in yaml_files:
        if yf.exists():
            dups = _find_yaml_duplicate_keys(yf)
            if dups:
                for key, count in dups:
                    errors.append(
                        f"YAML_DUPLICATE_KEY: {yf} has key '{key}' defined {count} times. "
                        "YAML parsers silently keep only the last value, causing data loss."
                    )

    return errors, warnings


def _chapter_sort_key(chapter: str) -> int:
    match = re.search(r"ch(\d+)", chapter)
    return int(match.group(1)) if match else -1


def _expand_window(window: str) -> set[str]:
    match = re.search(r"ch(\d+)\s*-\s*ch(\d+)", window)
    if not match:
        one = re.search(r"ch(\d+)", window)
        return {f"ch{int(one.group(1)):03d}"} if one else set()
    start = int(match.group(1))
    end = int(match.group(2))
    if end < start:
        return set()
    return {f"ch{i:03d}" for i in range(start, end + 1)}


def _extract_rolling_plan_chapters(text: str) -> list[tuple[str, str | None]]:
    chapters: list[tuple[str, str | None]] = []
    matches = list(re.finditer(r"^\s*-\s*chapter\s*:\s*[\"']?(ch\d+)[\"']?", text, re.MULTILINE))
    for i, match in enumerate(matches):
        chapter = match.group(1)
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[match.start():end]
        status_match = re.search(r"^\s*status\s*:\s*[\"']?([\w_-]+)", block, re.MULTILINE)
        chapters.append((chapter, status_match.group(1) if status_match else None))
    return chapters


def _extract_archived_chapters(text: str) -> set[str]:
    return set(re.findall(r"^\s*-\s*chapter\s*:\s*[\"']?(ch\d+)[\"']?", text, re.MULTILINE))


def _validate_planning_state_uniqueness(project: Path) -> list[str]:
    """Check that finished plan history and future rolling window do not overlap."""
    errors: list[str] = []
    rolling = project / "planning" / "rolling_plan.yml"
    completed = project / "planning" / "completed_plan_log.yml"
    if not rolling.exists() or not completed.exists():
        return errors

    rolling_text = rolling.read_text(encoding="utf-8")
    completed_text = completed.read_text(encoding="utf-8")
    rolling_chapters = _extract_rolling_plan_chapters(rolling_text)
    rolling_ids = {chapter for chapter, _status in rolling_chapters}
    completed_ids = _extract_archived_chapters(completed_text)
    overlap = sorted(rolling_ids & completed_ids, key=_chapter_sort_key)
    if overlap:
        errors.append(
            f"PLANNING_SOURCE_OVERLAP: {rolling} and {completed} both contain "
            f"{', '.join(overlap)}. Keep completed chapters only in completed_plan_log.yml."
        )

    window_match = re.search(r"current_window\s*:\s*[\"']?([^\"'\n#]+)", rolling_text)
    if window_match:
        window_ids = _expand_window(window_match.group(1).strip())
        window_overlap = sorted(window_ids & completed_ids, key=_chapter_sort_key)
        if window_overlap:
            errors.append(
                f"ROLLING_WINDOW_INCLUDES_ARCHIVED: {rolling} current_window includes archived chapters "
                f"{', '.join(window_overlap)}. Slide the window to the first unfinished chapter."
            )

    archived_match = re.search(r"archived_through\s*:\s*[\"']?(ch\d+)", completed_text)
    if archived_match:
        archived_no = _chapter_sort_key(archived_match.group(1))
        stale = sorted(
            chapter for chapter, _status in rolling_chapters if _chapter_sort_key(chapter) <= archived_no
        )
        if stale:
            errors.append(
                f"ROLLING_PLAN_BEFORE_ARCHIVE_BOUNDARY: {rolling} contains {', '.join(stale)} "
                f"at or before archived_through={archived_match.group(1)}."
            )
    return errors


def _validate_active_flow_catches_up(project: Path, chapters: list[str]) -> list[str]:
    """Check that active_flow.last_cut is not behind the validated batch."""
    errors: list[str] = []
    active_flow = project / "planning" / "active_flow.yml"
    if not active_flow.exists() or not chapters:
        return errors

    requested = [_chapter_sort_key(chapter) for chapter in chapters]
    requested = [chapter_no for chapter_no in requested if chapter_no >= 0]
    if not requested:
        return errors

    text = active_flow.read_text(encoding="utf-8")
    block_match = re.search(r"(?ms)^\s*last_cut\s*:\s*\n(?P<block>(?:^\s+.*(?:\n|$))+)", text)
    if not block_match:
        errors.append(
            f"ACTIVE_FLOW_LAST_CUT_MISSING: {active_flow} lacks last_cut. "
            "Each completed chapter must update active_flow.last_cut with the actual handoff."
        )
        return errors

    chapter_match = re.search(r"chapter\s*:\s*[\"']?(ch\d+)", block_match.group("block"))
    if not chapter_match:
        return errors

    last_cut_no = _chapter_sort_key(chapter_match.group(1))
    latest_validated_no = max(requested)
    if last_cut_no >= 0 and last_cut_no < latest_validated_no:
        errors.append(
            f"ACTIVE_FLOW_LAST_CUT_STALE: {active_flow} last_cut.chapter is "
            f"{chapter_match.group(1)}, but validation includes ch{latest_validated_no:03d}. "
            "Merge each chapter's actual_handoff into active_flow.last_cut before post-merge QA."
        )
    return errors


STATE_SYNC_TARGETS = {
    "character_changes": "entities/characters.yml",
    "relationship_changes": "entities/characters.yml",
    "world_state_changes": "ledgers/world_state.yml",
    "knowledge_changes": "ledgers/knowledge_state.yml",
}


def _is_substantive_change(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, list):
        return any(_is_substantive_change(item) for item in value)
    if isinstance(value, dict):
        return bool(value)
    if isinstance(value, str):
        return bool(value.strip()) and value.strip().lower() not in {"none", "n/a", "na", "无"}
    return bool(value)


def _state_sync_statuses(delta: dict) -> dict[str, str]:
    """Return target file -> sync status from canon_delta structured markers."""
    statuses: dict[str, str] = {}
    raw = delta.get("state_sync") or delta.get("state_targets") or []
    if isinstance(raw, dict):
        raw = [
            {"target": target, "status": status}
            for target, status in raw.items()
        ]
    if not isinstance(raw, list):
        return statuses
    for item in raw:
        if isinstance(item, str):
            statuses[item] = "merged"
        elif isinstance(item, dict):
            target = item.get("target") or item.get("file") or item.get("path")
            status = item.get("status") or item.get("sync_status") or "merged"
            if target:
                statuses[str(target)] = str(status)
    return statuses


def _target_is_confirmed(statuses: dict[str, str], target: str, *, allow_not_applicable: bool = False) -> bool:
    accepted = {"merged", "updated", "synced"}
    if allow_not_applicable:
        accepted |= {"n/a", "na", "not_applicable", "none"}
    for seen_target, status in statuses.items():
        if target == seen_target or target.endswith(seen_target) or seen_target.endswith(target):
            return status.strip().lower() in accepted
    return False


def _is_unresolved_state_sync_status(status: str) -> bool:
    return status.strip().lower() in {
        "needs_director_review",
        "needs_review",
        "pending",
        "todo",
        "open",
        "unmerged",
    }


def _iter_character_entries(characters_data: object) -> list[dict]:
    if isinstance(characters_data, dict):
        if isinstance(characters_data.get("characters"), list):
            return [item for item in characters_data["characters"] if isinstance(item, dict)]
        return [
            {"id": key, **value}
            for key, value in characters_data.items()
            if isinstance(key, str) and isinstance(value, dict)
        ]
    if isinstance(characters_data, list):
        return [item for item in characters_data if isinstance(item, dict)]
    return []


def _extract_changed_character_ids(changes: object) -> set[str]:
    names: set[str] = set()
    if not isinstance(changes, list):
        return names
    for change in changes:
        if isinstance(change, dict):
            value = change.get("character") or change.get("name") or change.get("id")
            if value:
                names.add(str(value))
        elif isinstance(change, str) and change.strip():
            names.add(change.strip())
    return names


def _entry_matches_character(entry: dict, name: str) -> bool:
    candidates = {
        str(entry.get("id") or ""),
        str(entry.get("name") or ""),
        str(entry.get("character") or ""),
    }
    return name in candidates


def _entry_mentions_chapter(entry: dict, chapter: str) -> bool:
    for field in ("last_updated", "last_seen", "updated_at", "chapter"):
        value = entry.get(field)
        if value is not None and chapter in str(value):
            return True
    history = entry.get("change_history") or entry.get("history") or []
    if isinstance(history, list):
        for item in history:
            if isinstance(item, dict) and chapter in str(item.get("chapter") or item.get("at") or item.get("source") or ""):
                return True
            if isinstance(item, str) and chapter in item:
                return True
    return False


def _normalize_handoff(value: object) -> str:
    if isinstance(value, list):
        return " ".join(str(item) for item in value)
    if isinstance(value, dict):
        return " ".join(str(item) for item in value.values())
    return str(value or "")


def validate_state_drift(project: Path, chapters: list[str], lookback: int = 3) -> tuple[list[str], list[str]]:
    """Check structured markers proving recent canon deltas reached current state.

    This deliberately avoids pretending to understand every prose change.
    The hard gate is structural: changed canon_delta fields must declare their
    current-state targets, and character entries should carry a recent update
    marker (`last_updated` or `change_history`) for changed characters.
    """
    errors: list[str] = []
    warnings: list[str] = []

    def load_yaml(path: Path) -> object:
        try:
            import yaml  # type: ignore[import-not-found]
            return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except ImportError:
            ruby = shutil.which("ruby")
            if not ruby:
                raise RuntimeError("NO_YAML_PARSER")
            ruby_code = "require 'yaml'; require 'json'; puts JSON.generate(YAML.load_file(ARGV[0]))"
            result = subprocess.run(
                [ruby, "-e", ruby_code, str(path)],
                text=True,
                capture_output=True,
                check=False,
            )
            if result.returncode != 0:
                detail = (result.stderr or result.stdout).strip().splitlines()
                raise RuntimeError(detail[0] if detail else "unknown YAML parse error")
            return json.loads(result.stdout) if result.stdout.strip() else {}

    if chapters:
        selected = sorted(set(chapters), key=_chapter_sort_key)[-lookback:]
    else:
        chapter_root = project / "chapters"
        selected = sorted((p.name for p in chapter_root.glob("ch*") if p.is_dir()), key=_chapter_sort_key)[-lookback:]

    recent_deltas: list[tuple[str, dict]] = []
    for chapter in selected:
        delta_path = project / "chapters" / chapter / "canon_delta.yml"
        if not delta_path.exists():
            continue
        try:
            data = load_yaml(delta_path)
        except RuntimeError as exc:
            if str(exc) == "NO_YAML_PARSER":
                warnings.append(
                    "STATE_DRIFT_SKIPPED: PyYAML is not installed and ruby is not available; "
                    "structured state drift checks were skipped."
                )
                return errors, warnings
            errors.append(f"CANON_DELTA_PARSE_ERROR: {delta_path}: {exc}")
            continue
        except Exception as exc:  # pragma: no cover - parser-specific detail
            errors.append(f"CANON_DELTA_PARSE_ERROR: {delta_path}: {exc}")
            continue
        if isinstance(data, dict):
            recent_deltas.append((chapter, data))

    if not recent_deltas:
        return errors, warnings

    characters_data: object | None = None
    characters_path = project / "entities" / "characters.yml"
    if characters_path.exists():
        try:
            characters_data = load_yaml(characters_path)
        except Exception as exc:  # pragma: no cover - parser-specific detail
            errors.append(f"STATE_FILE_PARSE_ERROR: {characters_path}: {exc}")

    for chapter, delta in recent_deltas:
        statuses = _state_sync_statuses(delta)
        for target, status in sorted(statuses.items()):
            if _is_unresolved_state_sync_status(status):
                errors.append(
                    f"UNRESOLVED_STATE_SYNC_REVIEW: {project / 'chapters' / chapter / 'canon_delta.yml'} "
                    f"state_sync target {target} is still {status}. Resolve it before post-merge QA: "
                    "merge the target current-state file and set status to merged/updated/synced, "
                    "or set status: n/a only when the corresponding change is genuinely empty."
                )
        for field, target in STATE_SYNC_TARGETS.items():
            if _is_substantive_change(delta.get(field)) and not _target_is_confirmed(statuses, target):
                errors.append(
                    f"STATE_SYNC_TARGET_MISSING: {project / 'chapters' / chapter / 'canon_delta.yml'} "
                    f"has non-empty {field}, but state_sync does not confirm merge to {target}. "
                    "Add state_sync with status: merged/updated/synced after updating the current state file. "
                    "status: n/a is only valid when the corresponding change field is empty."
                )

        if characters_data is not None:
            entries = _iter_character_entries(characters_data)
            changed_chars = _extract_changed_character_ids(delta.get("character_changes"))
            for char_name in sorted(changed_chars):
                matches = [entry for entry in entries if _entry_matches_character(entry, char_name)]
                if not matches:
                    errors.append(
                        f"CHARACTER_STATE_ENTRY_MISSING: {chapter} changes {char_name}, "
                        f"but {characters_path} has no matching id/name entry."
                    )
                    continue
                if not any(_entry_mentions_chapter(entry, chapter) for entry in matches):
                    errors.append(
                        f"CHARACTER_STATE_STALE: {chapter} changes {char_name}, but the matching "
                        f"entry in {characters_path} has no last_updated/change_history marker for {chapter}."
                    )

    active_flow_path = project / "planning" / "active_flow.yml"
    latest_chapter, latest_delta = recent_deltas[-1]
    if active_flow_path.exists():
        try:
            active_flow_data = load_yaml(active_flow_path)
        except Exception as exc:  # pragma: no cover - parser-specific detail
            errors.append(f"STATE_FILE_PARSE_ERROR: {active_flow_path}: {exc}")
            active_flow_data = {}
        current_flow = active_flow_data.get("current_flow", {}) if isinstance(active_flow_data, dict) else {}
        last_cut = current_flow.get("last_cut", {}) if isinstance(current_flow, dict) else {}
        if isinstance(last_cut, dict):
            af_ch = str(last_cut.get("chapter") or "")
            if af_ch and _chapter_sort_key(af_ch) < _chapter_sort_key(latest_chapter):
                errors.append(
                    f"ACTIVE_FLOW_HANDOFF_BEHIND: {active_flow_path} last_cut.chapter={af_ch}, "
                    f"but latest checked canon_delta is {latest_chapter}."
                )
            delta_handoff = _normalize_handoff(latest_delta.get("actual_handoff") or latest_delta.get("handoff_to_next_chapter"))
            active_handoff = _normalize_handoff(last_cut.get("current_handoff"))
            if delta_handoff and active_handoff:
                delta_items = latest_delta.get("actual_handoff") or []
                if isinstance(delta_items, list):
                    overlap = any(str(item).strip() and str(item).strip() in active_handoff for item in delta_items)
                    if not overlap:
                        warnings.append(
                            f"ACTIVE_FLOW_HANDOFF_TEXT_MISMATCH: {active_flow_path} last_cut.current_handoff "
                            f"does not directly include any full actual_handoff item from {latest_chapter}. "
                            "This can be an intentional summary, but verify it preserves the same external handoff."
                        )

    return errors, warnings


def validate_project_yaml(project: Path) -> tuple[list[str], list[str]]:
    """Validate YAML syntax for project files when a local parser is available."""
    errors: list[str] = []
    warnings: list[str] = []
    yaml_files = sorted(project.rglob("*.yml"))
    if not yaml_files:
        return errors, warnings

    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        yaml = None

    if yaml is not None:
        for yf in yaml_files:
            try:
                yaml.safe_load(yf.read_text(encoding="utf-8"))
            except Exception as exc:  # pragma: no cover - parser-specific detail
                detail = str(exc).strip().splitlines()[0] if str(exc).strip() else "unknown YAML parse error"
                errors.append(f"YAML_PARSE_ERROR: {yf}: {detail}")
        return errors, warnings

    ruby = shutil.which("ruby")
    if not ruby:
        warnings.append(
            "YAML_PARSE_SKIPPED: PyYAML is not installed and ruby is not available; "
            "syntax parsing was skipped."
        )
        return errors, warnings

    ruby_code = "require 'yaml'; YAML.load_file(ARGV[0])"
    for yf in yaml_files:
        result = subprocess.run(
            [ruby, "-e", ruby_code, str(yf)],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            message = (result.stderr or result.stdout).strip().splitlines()
            detail = message[0] if message else "unknown YAML parse error"
            errors.append(f"YAML_PARSE_ERROR: {yf}: {detail}")
    return errors, warnings


def validate_protected_files(project: Path) -> tuple[list[str], list[str]]:
    """Best-effort visibility check for protected-file change logging."""
    errors: list[str] = []
    warnings: list[str] = []
    protected_present = [path for path in PROTECTED_FILES if (project / path).exists()]
    if not protected_present:
        return errors, warnings

    decision_log = project / "ledgers" / "decision_log.yml"
    session_log = project / "meta" / "session_log.md"
    if not decision_log.exists() and not session_log.exists():
        warnings.append(
            f"NO_CHANGE_LOG: Protected files exist ({', '.join(protected_present)}) but neither "
            f"{decision_log} nor {session_log} exists. Protected-file changes must go through "
            "novel-change and record a Change Summary."
        )
        return errors, warnings

    log_text = ""
    for path in (decision_log, session_log):
        if path.exists():
            log_text += "\n" + path.read_text(encoding="utf-8", errors="ignore")
    if not re.search(r"(Change Summary|novel-change|受保护|protected|change:)", log_text, re.IGNORECASE):
        warnings.append(
            "PROTECTED_CHANGE_LOG_WEAK: A decision/session log exists, but it does not mention "
            "Change Summary / novel-change / protected-file handling. This is advisory; verify "
            "any protected-file edits were explicitly approved."
        )
    return errors, warnings


def _find_yaml_duplicate_keys(path: Path) -> list[tuple[str, int]]:
    """Find duplicate mapping keys within the same approximate YAML scope.

    This lightweight check complements real YAML parsing. It handles common
    nested maps and list items well enough for project memory files.
    """
    key_pattern = re.compile(r"^(\s*)([\w一-鿿_-]+)\s*:")
    list_key_pattern = re.compile(r"^(\s*)-\s+([\w一-鿿_-]+)\s*:")
    bare_list_item_pattern = re.compile(r"^(\s*)-\s*(?:#.*)?$")
    seen: dict[tuple[tuple[str, ...], str], int] = {}
    duplicates: list[tuple[str, int]] = []
    stack: list[tuple[int, str]] = []

    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        list_match = list_key_pattern.match(line)
        if list_match:
            indent = len(list_match.group(1))
            key = list_match.group(2)
            while stack and stack[-1][0] >= indent:
                stack.pop()
            item_marker = f"[]@{lineno}"
            scope = tuple(name for _, name in stack) + (item_marker,)
            seen[(scope, key)] = seen.get((scope, key), 0) + 1
            stack.append((indent, item_marker))
            stack.append((indent + 2, key))
            continue

        bare_list_item_match = bare_list_item_pattern.match(line)
        if bare_list_item_match:
            indent = len(bare_list_item_match.group(1))
            while stack and stack[-1][0] >= indent:
                stack.pop()
            stack.append((indent, f"[]@{lineno}"))
            continue

        m = key_pattern.match(line)
        if not m:
            continue

        indent = len(m.group(1))
        key = m.group(2)
        while stack and stack[-1][0] >= indent:
            stack.pop()
        scope = tuple(name for _, name in stack)
        seen[(scope, key)] = seen.get((scope, key), 0) + 1
        stack.append((indent, key))

    for (_scope, key), count in seen.items():
        if count > 1:
            duplicates.append((key, count))
    return duplicates


# ---- prose pattern diversity check ----

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


def _check_prose_patterns(path: Path) -> tuple[list[str], list[str]]:
    """Check for overused sentence patterns in chapter prose."""
    errors: list[str] = []
    warnings: list[str] = []
    text = path.read_text(encoding="utf-8")
    # Merge across lines for cross-paragraph patterns
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path, help="Novel project path, e.g. projects/my-novel")
    parser.add_argument("--chapters", nargs="*", help="Chapter ids to validate, e.g. ch011 ch012")
    parser.add_argument("--fix-format", action="store_true", help="Remove blank body lines from final.txt")
    parser.add_argument("--skip-planning", action="store_true", help="Skip planning-memory checks")
    parser.add_argument("--skip-state-drift", action="store_true", help="Skip structured state drift checks")
    parser.add_argument("--drift-lookback", type=int, default=3, help="Number of recent chapters to check for state drift")
    parser.add_argument("--check-protected-files", action="store_true", help="Check protected-file change log visibility")
    parser.add_argument("--skip-artifacts", action="store_true", help="Skip chapter artifact/context/review checks")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()

    project = args.project
    all_errors: list[str] = []
    all_warnings: list[str] = []

    if not project.exists():
        print(f"Project not found: {project}", file=sys.stderr)
        return 2

    chapters = args.chapters
    if not chapters:
        chapter_root = project / "chapters"
        chapters = sorted(p.name for p in chapter_root.glob("ch*") if p.is_dir())[-3:]

    if not args.skip_planning:
        errs, warns = validate_planning(project)
        all_errors.extend(errs)
        all_warnings.extend(warns)
        errs, warns = validate_merge_previews(project, chapters)
        all_errors.extend(errs)
        all_warnings.extend(warns)
        errs, warns = validate_cross_chapter_patterns(project, chapters)
        all_errors.extend(errs)
        all_warnings.extend(warns)
        all_errors.extend(_validate_active_flow_catches_up(project, chapters))
        if not args.skip_state_drift:
            errs, warns = validate_state_drift(project, chapters, lookback=args.drift_lookback)
            all_errors.extend(errs)
            all_warnings.extend(warns)

    if args.check_protected_files:
        errs, warns = validate_protected_files(project)
        all_errors.extend(errs)
        all_warnings.extend(warns)

    for chapter in chapters:
        chapter_dir = project / "chapters" / chapter
        if not args.skip_artifacts:
            errs, warns = validate_chapter_artifacts(chapter_dir)
            all_errors.extend(errs)
            all_warnings.extend(warns)
        errs, warns = validate_txt(chapter_dir / "final.txt", args.fix_format, strict=args.strict)
        all_errors.extend(errs)
        all_warnings.extend(warns)
        # Prose pattern diversity check
        final_txt = chapter_dir / "final.txt"
        if final_txt.exists():
            errs, warns = _check_prose_patterns(final_txt)
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
