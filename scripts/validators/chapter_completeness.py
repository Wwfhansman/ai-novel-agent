"""Chapter artifact and quality-gate completeness checks."""

from __future__ import annotations

import re
from pathlib import Path

from .writing_packet import validate_writing_packet


HEADING_PATTERN = re.compile(r"^\s{0,3}(#{1,6})\s*(.+?)\s*$", re.MULTILINE)

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

REQUIRED_REVIEW_SECTIONS = [
    ("Reader Reward Check", "读者回报检查", "读者体验"),
    ("TXT Format Check", "TXT 格式检查", "正文质量", "格式"),
    ("Memory Update Check", "记忆更新检查", "工程状态", "记忆工程卫生检查"),
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


def validate_chapter_artifacts(chapter_dir: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for filename in REQUIRED_CHAPTER_FILES:
        path = chapter_dir / filename
        if not path.exists():
            errors.append(f"MISSING_FILE: {path}")

    for filename in QUALITY_GATE_FILES:
        path = chapter_dir / filename
        if not path.exists():
            warnings.append(
                f"MISSING_QUALITY_GATE: {path} is missing. New workflow expects this file before accepting final.txt."
            )

    reader_pass = chapter_dir / "reader_pass.md"
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
        if re.search(r"(联合|batch|combined).{0,30}memory_update_plan|memory_update_plan\s*位于|../ch\d+/memory_update_plan\.md", text, re.IGNORECASE):
            errors.append(
                f"BATCH_MEMORY_PLAN_POINTER_UNSUPPORTED: {memory_plan} points to a shared memory plan. "
                "Each completed chapter must have its own diff-only memory_update_plan.md with evidence and merge candidates."
            )
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
        packet_errors, packet_warnings = validate_writing_packet(writing_packet, samples_has_content)
        errors.extend(packet_errors)
        warnings.extend(packet_warnings)
    elif samples_has_content:
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
