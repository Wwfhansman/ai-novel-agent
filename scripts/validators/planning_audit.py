"""Planning and project-structure validator checks."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path


HEADING_PATTERN = re.compile(r"^\s{0,3}(#{1,6})\s*(.+?)\s*$", re.MULTILINE)

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
    ("background_dependencies", "背景依赖", "背景落库"),
]

REQUIRED_ROUND_CONTEXT_PACK_SECTIONS = [
    ("Director Directive", "导演指令", "本轮导演指令"),
    ("Background Completion Audit", "背景补全审计", "背景完整性审计", "背景落库检查"),
]

ARCHITECTURE_ROLE_FIELDS = [
    "architecture_role",
    "pacing_mode",
    "world_expansion",
    "protagonist_growth_budget",
    "information_reveal",
    "side_thread_touch",
    "offscreen_pressure",
    "recurring_assets",
    "writable_scene_seed",
]

GROWTH_EVENT_PATTERNS = [
    r"突破",
    r"升级",
    r"晋升",
    r"进阶",
    r"power[_ -]?up",
    r"breakthrough",
]

ROLLING_PLAN_SIZE_WARN_BYTES = 20000


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


def _artifact_relevant_to_chapters(text: str, chapters: list[str]) -> bool:
    if not chapters:
        return True
    return any(chapter in text for chapter in chapters)


def _chapter_sort_key(chapter: str) -> int:
    match = re.search(r"ch(\d+)", chapter)
    return int(match.group(1)) if match else -1


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


def _find_yaml_duplicate_keys(path: Path) -> list[tuple[str, int]]:
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

        match = key_pattern.match(line)
        if not match:
            continue

        indent = len(match.group(1))
        key = match.group(2)
        while stack and stack[-1][0] >= indent:
            stack.pop()
        scope = tuple(name for _, name in stack)
        seen[(scope, key)] = seen.get((scope, key), 0) + 1
        stack.append((indent, key))

    for (_scope, key), count in seen.items():
        if count > 1:
            duplicates.append((key, count))
    return duplicates


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


def _extract_rolling_plan_chapter_blocks(text: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    matches = list(re.finditer(r"^\s*-\s*chapter\s*:\s*[\"']?(ch\d+)[\"']?", text, re.MULTILINE))
    for index, match in enumerate(matches):
        chapter = match.group(1)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append((chapter, text[match.start():end]))
    return blocks


def _extract_archived_chapters(text: str) -> set[str]:
    return set(re.findall(r"^\s*-\s*chapter\s*:\s*[\"']?(ch\d+)[\"']?", text, re.MULTILINE))


def _validate_planning_state_uniqueness(project: Path) -> list[str]:
    errors: list[str] = []
    rolling = project / "planning" / "rolling_plan.yml"
    completed = project / "planning" / "completed_plan_log.yml"
    if not rolling.exists() or not completed.exists():
        return errors

    rolling_text = rolling.read_text(encoding="utf-8")
    completed_text = completed.read_text(encoding="utf-8")
    rolling_chapters = _extract_rolling_plan_chapters(rolling_text)
    chapter_counts: dict[str, int] = {}
    for chapter, _status in rolling_chapters:
        chapter_counts[chapter] = chapter_counts.get(chapter, 0) + 1
    duplicates = sorted((chapter for chapter, count in chapter_counts.items() if count > 1), key=_chapter_sort_key)
    if duplicates:
        errors.append(
            f"ROLLING_PLAN_DUPLICATE_CHAPTER: {rolling} contains duplicate entries for "
            f"{', '.join(duplicates)}. Keep exactly one planning entry per future chapter."
        )
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


def _extract_architecture_field(block: str, field: str) -> str:
    pattern = re.compile(rf"^\s*{re.escape(field)}\s*:\s*[\"']?([^\"'\n#]*)", re.MULTILINE)
    match = pattern.search(block)
    return match.group(1).strip() if match else ""


def _is_empty_architecture_value(block: str, field: str) -> bool:
    lines = block.splitlines()
    for index, line in enumerate(lines):
        match = re.match(rf"^(\s*){re.escape(field)}\s*:\s*(.*)$", line)
        if not match:
            continue
        indent = len(match.group(1))
        value = re.sub(r"\s+#.*$", "", match.group(2)).strip()
        if value and value.lower() not in {"[]", "{}", "n/a", "na", "none", "无"}:
            return False
        for next_line in lines[index + 1:]:
            if not next_line.strip() or next_line.lstrip().startswith("#"):
                continue
            next_indent = len(next_line) - len(next_line.lstrip(" "))
            stripped = next_line.strip()
            if next_indent < indent:
                break
            if next_indent == indent and not stripped.startswith("- "):
                break
            if stripped not in {"[]", "{}"}:
                return False
        return True
    return True


def _validate_architecture_files(project: Path) -> list[str]:
    warnings: list[str] = []
    planning = project / "planning"
    expected = [
        planning / "story_architecture.yml",
        planning / "thread_board.yml",
        planning / "completed_threads_log.yml",
    ]
    for path in expected:
        if not path.exists():
            warnings.append(
                f"MISSING_STORY_ARCHITECTURE_FILE: {path} is missing. "
                "Projects should include story architecture files before running novel-architect."
            )
    if not (planning / "development_packs").exists():
        warnings.append(
            f"MISSING_DEVELOPMENT_PACK_DIR: {planning / 'development_packs'} is missing. "
            "novel-architect writes development packs there."
        )
    return warnings


def _validate_rolling_architecture(project: Path) -> list[str]:
    warnings: list[str] = []
    rolling = project / "planning" / "rolling_plan.yml"
    if not rolling.exists():
        return warnings
    text = rolling.read_text(encoding="utf-8")
    blocks = _extract_rolling_plan_chapter_blocks(text)
    if not blocks:
        warnings.append(
            f"ROLLING_PLAN_EMPTY: {rolling} has no future chapter blocks. "
            "Run novel-architect before the next writing round to develop the next 6-15 chapters."
        )
        return warnings
    if len(blocks) < 4:
        warnings.append(
            f"ROLLING_PLAN_WINDOW_THIN: {rolling} has only {len(blocks)} future chapter block(s). "
            "Run novel-architect before the next round so the writer is not planning from the last remaining chapter."
        )

    missing_architecture: list[str] = []
    thin_world: list[str] = []
    thin_threads: list[str] = []
    growth_chapters: list[str] = []
    pacing_modes: list[tuple[str, str]] = []

    for chapter, block in blocks:
        missing_fields = [field for field in ARCHITECTURE_ROLE_FIELDS if field not in block]
        if missing_fields:
            missing_architecture.append(f"{chapter}({', '.join(missing_fields[:4])})")
        if "architecture_role" in block:
            mode = _extract_architecture_field(block, "pacing_mode").lower()
            if mode:
                pacing_modes.append((chapter, mode))
            if _is_empty_architecture_value(block, "world_expansion"):
                thin_world.append(chapter)
            if _is_empty_architecture_value(block, "side_thread_touch"):
                thin_threads.append(chapter)
            growth_value = _extract_architecture_field(block, "protagonist_growth_budget")
            if any(re.search(pattern, growth_value, re.IGNORECASE) for pattern in GROWTH_EVENT_PATTERNS):
                growth_chapters.append(chapter)

    if missing_architecture:
        warnings.append(
            f"ROLLING_PLAN_ARCHITECTURE_ROLE_MISSING: {rolling} has chapter entries without complete "
            f"architecture_role fields: {', '.join(missing_architecture[:6])}. "
            "Run novel-architect or fill pacing/world/growth/thread constraints before generating writing packets."
        )
    if len(thin_world) >= 3:
        warnings.append(
            f"ROLLING_PLAN_WORLD_EXPANSION_THIN: {rolling} has {len(thin_world)} chapters with empty "
            f"world_expansion ({', '.join(thin_world[:8])}). This risks world shrinkage."
        )
    if len(thin_threads) >= 4:
        warnings.append(
            f"ROLLING_PLAN_SIDE_THREADS_THIN: {rolling} has {len(thin_threads)} chapters with empty "
            f"side_thread_touch ({', '.join(thin_threads[:8])}). This risks protagonist-only task flow."
        )
    if len(growth_chapters) > max(2, len(blocks) // 3):
        warnings.append(
            f"ROLLING_PLAN_GROWTH_TOO_DENSE: {rolling} marks frequent protagonist growth in "
            f"{', '.join(growth_chapters[:8])}. Check story_architecture growth_budget before drafting."
        )

    for i in range(len(pacing_modes) - 2):
        trio = pacing_modes[i:i + 3]
        if trio[0][1] and trio[0][1] == trio[1][1] == trio[2][1]:
            warnings.append(
                f"ROLLING_PLAN_PACING_LOOP: {rolling} has three consecutive chapters with "
                f"pacing_mode={trio[0][1]} ({', '.join(ch for ch, _mode in trio)}). "
                "Check rhythm budget before drafting."
            )
            break
    return warnings


def validate_planning(project: Path, chapters: list[str] | None = None) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    chapters = chapters or []

    errs, warns = validate_project_yaml(project)
    errors.extend(errs)
    warnings.extend(warns)
    warnings.extend(_validate_architecture_files(project))

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
        for pattern in BACKGROUND_PLACEHOLDER_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                errors.append(
                    f"BACKGROUND_PLACEHOLDER: {path} contains unresolved background placeholder matching /{pattern}/. "
                    "Complete and store reusable background in entities/ or ledgers before planning/drafting."
                )
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
            warnings.extend(_validate_rolling_architecture(project))
        if path.name == "rolling_plan.yml" and re.search(r"\bstatus\s*:\s*completed\b", text):
            errors.append(
                f"COMPLETED_PLAN_NOT_ARCHIVED: {path} contains completed chapters. "
                "Move finished chapter plan entries to planning/completed_plan_log.yml "
                "and keep rolling_plan.yml as the future window."
            )

    context_pack_dir = project / "planning" / "context_packs"
    samples = project / "style" / "samples.md"
    samples_has_content = False
    if samples.exists():
        sample_text = samples.read_text(encoding="utf-8").strip()
        samples_has_content = bool(sample_text) and "占位" not in sample_text and "暂无" not in sample_text
    for path in sorted(context_pack_dir.glob("round_*_context_pack.md")):
        text = path.read_text(encoding="utf-8")
        if chapters and not _artifact_relevant_to_chapters(text, chapters):
            continue
        for pattern in BACKGROUND_PLACEHOLDER_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                errors.append(
                    f"BACKGROUND_PLACEHOLDER: {path} contains unresolved background placeholder matching /{pattern}/. "
                    "Resolve background before sending packets to planner/writer."
                )
        for section_aliases in REQUIRED_ROUND_CONTEXT_PACK_SECTIONS:
            if not _has_section(text, section_aliases):
                warnings.append(
                    f"ROUND_CONTEXT_DIRECTIVE_MISSING: {path} lacks {_section_label(section_aliases)}. "
                    "Planner needs explicit round-level boundaries before generating writing_packet.md."
                )
        if samples_has_content and re.search(r"samples\.md\s*(不存在|为空|不存在或为空)|不使用样本文风锚点", text):
            errors.append(
                f"ROUND_CONTEXT_SAMPLE_MISMATCH: {path} says style/samples.md is missing or empty, "
                f"but {samples} contains real content. Extract sample anchors before calling planner/writer."
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
