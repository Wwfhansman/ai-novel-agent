"""State drift validator checks."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path


STATE_SYNC_TARGETS = {
    "character_changes": "entities/characters.yml",
    "relationship_changes": "entities/characters.yml",
    "world_state_changes": "ledgers/world_state.yml",
    "knowledge_changes": "ledgers/knowledge_state.yml",
}


def _chapter_sort_key(chapter: str) -> int:
    match = re.search(r"ch(\d+)", chapter)
    return int(match.group(1)) if match else -1


def validate_active_flow_catches_up(project: Path, chapters: list[str]) -> list[str]:
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


def _extract_delta_handoff(delta: dict) -> tuple[object, object]:
    handoff = delta.get("actual_handoff") or delta.get("handoff_to_next_chapter")
    last_visible_moment = delta.get("last_visible_moment")
    block = delta.get("handoff")
    if isinstance(block, dict):
        handoff = handoff or block.get("current_handoff") or block.get("actual_handoff")
        last_visible_moment = last_visible_moment or block.get("last_visible_moment")
    return handoff, last_visible_moment


def _load_yaml(path: Path) -> object:
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


def validate_state_drift(project: Path, chapters: list[str], lookback: int = 3) -> tuple[list[str], list[str]]:
    """Check structured markers proving recent canon deltas reached current state."""
    errors: list[str] = []
    warnings: list[str] = []

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
            data = _load_yaml(delta_path)
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
            characters_data = _load_yaml(characters_path)
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
            active_flow_data = _load_yaml(active_flow_path)
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
            raw_delta_handoff, delta_last_visible_moment = _extract_delta_handoff(latest_delta)
            delta_handoff = _normalize_handoff(raw_delta_handoff)
            active_handoff = _normalize_handoff(last_cut.get("current_handoff"))
            if delta_handoff and not active_handoff:
                errors.append(
                    f"ACTIVE_FLOW_HANDOFF_EMPTY: {active_flow_path} last_cut.current_handoff is empty, "
                    f"but {latest_chapter} canon_delta has an outbound handoff."
                )
            if delta_last_visible_moment and last_cut.get("last_visible_moment") != delta_last_visible_moment:
                errors.append(
                    f"ACTIVE_FLOW_LAST_VISIBLE_MOMENT_STALE: {active_flow_path} last_cut.last_visible_moment "
                    f"does not match {latest_chapter} canon_delta handoff."
                )
            if delta_handoff and active_handoff:
                delta_items = raw_delta_handoff or []
                if isinstance(delta_items, list):
                    overlap = any(str(item).strip() and str(item).strip() in active_handoff for item in delta_items)
                    if not overlap:
                        warnings.append(
                            f"ACTIVE_FLOW_HANDOFF_TEXT_MISMATCH: {active_flow_path} last_cut.current_handoff "
                            f"does not directly include any full actual_handoff item from {latest_chapter}. "
                            "This can be an intentional summary, but verify it preserves the same external handoff."
                        )

    return errors, warnings
