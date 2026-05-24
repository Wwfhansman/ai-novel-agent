#!/usr/bin/env python3
"""Preview and apply safe current-state updates for a writing round.

This tool intentionally handles only mechanical, high-confidence operations.
It is not a canon decision engine. Anything uncertain is left in manual_review
for the director/human to resolve.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_with_ruby(path: Path) -> Any:
    ruby = shutil.which("ruby")
    if not ruby:
        print(
            "PyYAML is not installed and ruby is not available; cannot parse YAML.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    ruby_code = "require 'yaml'; require 'json'; puts JSON.generate(YAML.load_file(ARGV[0]))"
    result = subprocess.run([ruby, "-e", ruby_code, str(path)], text=True, capture_output=True, check=False)
    if result.returncode != 0:
        print((result.stderr or result.stdout).strip(), file=sys.stderr)
        raise SystemExit(2)
    return json.loads(result.stdout) if result.stdout.strip() else {}


def dump_with_ruby(path: Path, data: Any) -> None:
    ruby = shutil.which("ruby")
    if not ruby:
        print(
            "PyYAML is not installed and ruby is not available; cannot write YAML.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    ruby_code = "require 'json'; require 'yaml'; puts YAML.dump(JSON.parse(STDIN.read))"
    result = subprocess.run(
        [ruby, "-e", ruby_code],
        input=json.dumps(data, ensure_ascii=False),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        print((result.stderr or result.stdout).strip(), file=sys.stderr)
        raise SystemExit(2)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.stdout, encoding="utf-8")


def get_yaml_module():
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        return None
    return yaml


def load_yaml(path: Path) -> Any:
    if not path.exists():
        return {}
    yaml = get_yaml_module()
    if yaml is None:
        return load_with_ruby(path)
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def dump_yaml(path: Path, data: Any) -> None:
    yaml = get_yaml_module()
    if yaml is None:
        dump_with_ruby(path, data)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )


def chapter_sort_key(chapter: str) -> tuple[int, str]:
    digits = "".join(ch for ch in chapter if ch.isdigit())
    return (int(digits) if digits else 0, chapter)


def _normalize_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if value in (None, ""):
        return []
    return [str(value)]


def extract_handoff(delta: dict[str, Any]) -> dict[str, Any]:
    """Return the chapter's canonical outbound handoff across schema variants."""
    raw = delta.get("actual_handoff") or delta.get("handoff_to_next_chapter")
    last_visible_moment = delta.get("last_visible_moment")

    handoff_block = delta.get("handoff")
    if isinstance(handoff_block, dict):
        raw = raw or handoff_block.get("current_handoff") or handoff_block.get("actual_handoff")
        last_visible_moment = last_visible_moment or handoff_block.get("last_visible_moment")

    return {
        "current_handoff": raw or [],
        "last_visible_moment": last_visible_moment,
    }


def iter_character_entries(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict) and isinstance(data.get("characters"), list):
        return [item for item in data["characters"] if isinstance(item, dict)]
    if isinstance(data, dict):
        entries: list[dict[str, Any]] = []
        for key, value in data.items():
            if isinstance(value, dict):
                value.setdefault("id", key)
                entries.append(value)
        return entries
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    return []


def find_character(entries: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    for entry in entries:
        candidates = {
            str(entry.get("id") or ""),
            str(entry.get("name") or ""),
            str(entry.get("character") or ""),
        }
        if name in candidates:
            return entry
    return None


def extract_character_changes(delta: dict[str, Any]) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    changes = delta.get("character_changes") or []
    if not isinstance(changes, list):
        return result
    for item in changes:
        if isinstance(item, dict):
            name = item.get("character") or item.get("name") or item.get("id")
            change = item.get("change") or item.get("description") or item.get("value")
            if name and change:
                result.append((str(name), str(change)))
        elif isinstance(item, str) and item.strip():
            result.append((item.strip(), item.strip()))
    return result


def state_sync_statuses(delta: dict[str, Any]) -> dict[str, str]:
    raw = delta.get("state_sync") or []
    statuses: dict[str, str] = {}
    if isinstance(raw, dict):
        return {str(k): str(v) for k, v in raw.items()}
    if not isinstance(raw, list):
        return statuses
    for item in raw:
        if isinstance(item, dict):
            target = item.get("target") or item.get("file") or item.get("path")
            status = item.get("status") or "merged"
            if target:
                statuses[str(target)] = str(status)
    return statuses


def build_preview(project: Path, round_id: str, chapters: list[str]) -> dict[str, Any]:
    chapters = sorted(chapters, key=chapter_sort_key)
    source_files: list[str] = []
    operations: list[dict[str, Any]] = []
    manual_review: list[dict[str, Any]] = []

    characters_path = project / "entities" / "characters.yml"
    characters_data = load_yaml(characters_path)
    character_entries = iter_character_entries(characters_data)

    deltas: list[tuple[str, dict[str, Any]]] = []
    for chapter in chapters:
        delta_path = project / "chapters" / chapter / "canon_delta.yml"
        memory_path = project / "chapters" / chapter / "memory_update_plan.md"
        if delta_path.exists():
            source_files.append(str(delta_path.relative_to(project)))
            delta = load_yaml(delta_path)
            if isinstance(delta, dict):
                deltas.append((chapter, delta))
        else:
            manual_review.append({
                "target": str(delta_path.relative_to(project)),
                "reason": "canon_delta.yml missing; cannot build state merge operations.",
                "evidence": chapter,
            })
        if memory_path.exists():
            source_files.append(str(memory_path.relative_to(project)))

    for chapter, delta in deltas:
        for target, status in state_sync_statuses(delta).items():
            if status.strip().lower() in {"needs_director_review", "pending", "todo", "open", "unmerged"}:
                manual_review.append({
                    "target": target,
                    "reason": f"state_sync target remains {status}; director must resolve before post-merge QA.",
                    "evidence": f"{chapter} canon_delta.yml",
                })

        for char_name, change in extract_character_changes(delta):
            entry = find_character(character_entries, char_name)
            if not entry:
                manual_review.append({
                    "target": "entities/characters.yml",
                    "reason": f"Changed character {char_name} has no matching id/name entry.",
                    "evidence": f"{chapter}: {change}",
                })
                continue
            entity_id = str(entry.get("id") or entry.get("name") or char_name)
            history = entry.get("change_history") or []
            history_value = {"chapter": chapter, "change": change}
            if not (isinstance(history, list) and history_value in history):
                operations.append({
                    "op": "append_change_history",
                    "target": "entities/characters.yml",
                    "chapter": chapter,
                    "entity": entity_id,
                    "value": history_value,
                    "evidence": f"{chapter} character_changes: {change}",
                    "confidence": "high",
                    "status": "pending",
                })
            if chapter not in str(entry.get("last_updated") or ""):
                operations.append({
                    "op": "set_last_updated",
                    "target": "entities/characters.yml",
                    "chapter": chapter,
                    "entity": entity_id,
                    "value": chapter,
                    "evidence": f"{chapter} character_changes mentions {char_name}.",
                    "confidence": "high",
                    "status": "pending",
                })

    rolling_path = project / "planning" / "rolling_plan.yml"
    rolling = load_yaml(rolling_path)
    rolling_chapters = rolling.get("chapters") if isinstance(rolling, dict) else []
    completed_path = project / "planning" / "completed_plan_log.yml"
    completed = load_yaml(completed_path)
    if isinstance(rolling_chapters, list):
        rolling_ids = {str(item.get("chapter")) for item in rolling_chapters if isinstance(item, dict)}
        for chapter, delta in deltas:
            if chapter in rolling_ids:
                handoff = extract_handoff(delta)
                operations.append({
                    "op": "archive_completed_chapter",
                    "target": "planning/rolling_plan.yml",
                    "chapter": chapter,
                    "entity": None,
                    "value": {
                        "chapter": chapter,
                        "status": "completed",
                        "actual_handoff": handoff["current_handoff"],
                    },
                    "evidence": f"{chapter} has final canon_delta and is still in rolling_plan.",
                    "confidence": "high",
                    "status": "pending",
                })

    completed_entries = completed.get("entries") if isinstance(completed, dict) else []
    if isinstance(completed_entries, list):
        for chapter, delta in deltas:
            handoff = extract_handoff(delta)
            for entry in completed_entries:
                if not isinstance(entry, dict) or entry.get("chapter") != chapter:
                    continue
                if _normalize_list(entry.get("actual_handoff")) != _normalize_list(handoff["current_handoff"]):
                    operations.append({
                        "op": "update_completed_plan_handoff",
                        "target": "planning/completed_plan_log.yml",
                        "chapter": chapter,
                        "entity": None,
                        "value": {
                            "actual_handoff": handoff["current_handoff"],
                        },
                        "evidence": f"{chapter} handoff from canon_delta.yml differs from completed_plan_log.yml.",
                        "confidence": "high",
                        "status": "pending",
                    })
                break

    if deltas:
        latest_chapter, latest_delta = deltas[-1]
        active_flow = load_yaml(project / "planning" / "active_flow.yml")
        current_flow = active_flow.get("current_flow", {}) if isinstance(active_flow, dict) else {}
        last_cut = current_flow.get("last_cut", {}) if isinstance(current_flow, dict) else {}
        expected = extract_handoff(latest_delta)
        expected_handoff = expected["current_handoff"]
        if not (
            isinstance(last_cut, dict)
            and last_cut.get("chapter") == latest_chapter
            and _normalize_list(last_cut.get("current_handoff")) == _normalize_list(expected_handoff)
            and (
                not expected.get("last_visible_moment")
                or last_cut.get("last_visible_moment") == expected.get("last_visible_moment")
            )
        ):
            value = {
                "chapter": latest_chapter,
                "current_handoff": expected_handoff,
            }
            if expected.get("last_visible_moment"):
                value["last_visible_moment"] = expected["last_visible_moment"]
            operations.append({
                "op": "update_active_flow_cut",
                "target": "planning/active_flow.yml",
                "chapter": latest_chapter,
                "entity": "current_flow.last_cut",
                "value": value,
                "evidence": f"{latest_chapter} actual_handoff from canon_delta.yml.",
                "confidence": "high",
                "status": "pending",
            })

    return {
        "project": project.name,
        "round": round_id,
        "chapters": chapters,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_files": source_files,
        "operations": operations,
        "manual_review": manual_review,
        "apply_log": [],
    }


def ensure_list(entry: dict[str, Any], key: str) -> list[Any]:
    value = entry.get(key)
    if isinstance(value, list):
        return value
    if value in (None, ""):
        entry[key] = []
        return entry[key]
    entry[key] = [value]
    return entry[key]


def apply_preview(project: Path, preview_path: Path) -> dict[str, Any]:
    preview = load_yaml(preview_path)
    if not isinstance(preview, dict):
        raise SystemExit(f"Invalid preview file: {preview_path}")

    operations = preview.get("operations") or []
    apply_log = preview.setdefault("apply_log", [])

    characters_path = project / "entities" / "characters.yml"
    characters_data = load_yaml(characters_path)
    character_entries = iter_character_entries(characters_data)

    active_flow_path = project / "planning" / "active_flow.yml"
    active_flow_data = load_yaml(active_flow_path)

    rolling_path = project / "planning" / "rolling_plan.yml"
    rolling_data = load_yaml(rolling_path)
    completed_path = project / "planning" / "completed_plan_log.yml"
    completed_data = load_yaml(completed_path)

    changed_paths: set[Path] = set()

    for op in operations:
        if not isinstance(op, dict):
            continue
        if op.get("status") != "pending" or op.get("confidence") != "high":
            continue
        name = op.get("op")
        if name in {"append_change_history", "set_last_updated"}:
            entry = find_character(character_entries, str(op.get("entity") or ""))
            if not entry:
                op["status"] = "manual_review"
                apply_log.append({"op": name, "status": "manual_review", "reason": "character entry missing"})
                continue
            if name == "append_change_history":
                history = ensure_list(entry, "change_history")
                value = op.get("value")
                if value not in history:
                    history.append(value)
            else:
                entry["last_updated"] = op.get("value")
            op["status"] = "applied"
            changed_paths.add(characters_path)
            apply_log.append({"op": name, "target": op.get("target"), "entity": op.get("entity"), "status": "applied"})
        elif name == "archive_completed_chapter":
            chapter = op.get("chapter")
            if isinstance(rolling_data, dict) and isinstance(rolling_data.get("chapters"), list):
                remaining = []
                archived = None
                for item in rolling_data["chapters"]:
                    if isinstance(item, dict) and item.get("chapter") == chapter:
                        archived = dict(item)
                    else:
                        remaining.append(item)
                rolling_data["chapters"] = remaining
                remaining_ids = [
                    str(item.get("chapter"))
                    for item in remaining
                    if isinstance(item, dict) and item.get("chapter")
                ]
                if remaining_ids:
                    rolling_data["current_window"] = f"{remaining_ids[0]}-{remaining_ids[-1]}"
                else:
                    rolling_data["current_window"] = ""
                if archived is not None:
                    archived["status"] = "completed"
                    archived["actual_handoff"] = (op.get("value") or {}).get("actual_handoff", [])
                    completed_data.setdefault("entries", [])
                    if isinstance(completed_data["entries"], list):
                        if not any(isinstance(x, dict) and x.get("chapter") == chapter for x in completed_data["entries"]):
                            completed_data["entries"].append(archived)
                        completed_data["archived_through"] = chapter
                    changed_paths.update({rolling_path, completed_path})
            op["status"] = "applied"
            apply_log.append({"op": name, "chapter": chapter, "status": "applied"})
        elif name == "update_completed_plan_handoff":
            chapter = op.get("chapter")
            if isinstance(completed_data, dict) and isinstance(completed_data.get("entries"), list):
                for entry in completed_data["entries"]:
                    if isinstance(entry, dict) and entry.get("chapter") == chapter:
                        entry["actual_handoff"] = (op.get("value") or {}).get("actual_handoff", [])
                        changed_paths.add(completed_path)
                        break
            op["status"] = "applied"
            apply_log.append({"op": name, "chapter": chapter, "status": "applied"})
        elif name == "update_active_flow_cut":
            if isinstance(active_flow_data, dict):
                current_flow = active_flow_data.setdefault("current_flow", {})
                if isinstance(current_flow, dict):
                    last_cut = current_flow.setdefault("last_cut", {})
                    if not isinstance(last_cut, dict):
                        last_cut = {}
                        current_flow["last_cut"] = last_cut
                    value = op.get("value") or {}
                    if isinstance(value, dict):
                        last_cut.update(value)
                    changed_paths.add(active_flow_path)
            op["status"] = "applied"
            apply_log.append({"op": name, "chapter": op.get("chapter"), "status": "applied"})

    if characters_path in changed_paths:
        dump_yaml(characters_path, characters_data)
    if active_flow_path in changed_paths:
        dump_yaml(active_flow_path, active_flow_data)
    if rolling_path in changed_paths:
        dump_yaml(rolling_path, rolling_data)
    if completed_path in changed_paths:
        dump_yaml(completed_path, completed_data)

    dump_yaml(preview_path, preview)
    return preview


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    preview_parser = sub.add_parser("preview")
    preview_parser.add_argument("project", type=Path)
    preview_parser.add_argument("--round", required=True, dest="round_id")
    preview_parser.add_argument("--chapters", nargs="+", required=True)
    preview_parser.add_argument("--output", type=Path)

    apply_parser = sub.add_parser("apply")
    apply_parser.add_argument("project", type=Path)
    apply_parser.add_argument("--preview", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "preview":
        output = args.output or args.project / "planning" / "merge_previews" / f"{args.round_id}.yml"
        data = build_preview(args.project, args.round_id, args.chapters)
        dump_yaml(output, data)
        print(f"Wrote merge preview: {output}")
        return 0
    if args.command == "apply":
        apply_preview(args.project, args.preview)
        print(f"Applied safe merge operations from: {args.preview}")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
