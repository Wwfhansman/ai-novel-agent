"""Memory-coverage check: catch under-recorded relationship changes.

The engine guarantees that what IS recorded stays consistent (no drift). It
cannot, on its own, know that the writer *should* have recorded something. This
heuristic closes part of that gap: it scans each chapter's final.txt for
relationship/attitude language between two known characters, and warns when the
chapter's events contain no matching `relationship_changed`.

It is deliberately a heuristic — it will miss some and over-flag some. Its job is
to stop the common failure where a major relationship beat is written into prose
but never recorded as a typed event (so it never reaches derived state). Trigger
words live in the profile (`coverage.relationship_words`) so they are tunable.
"""

from __future__ import annotations

import re
from pathlib import Path

from .events import Event, chapter_sort_key
from .projection import State

_DEFAULT_TRIGGERS = [
    "结盟", "联手", "盟友", "结仇", "反目", "翻脸", "决裂", "和解", "拜师", "收徒",
    "结拜", "背叛", "出卖", "投靠", "归顺", "示好", "定情", "倾心", "动情",
    "化敌为友", "反目成仇", "盯梢", "投诚", "效忠", "决裂",
]
_SENTENCE_SPLIT = re.compile(r"[。！？!?\n]")
_MAX_WARNINGS = 12


def _name_to_id(state: State) -> dict[str, str]:
    out: dict[str, str] = {}
    for cid, char in state.characters.items():
        name = char.get("name")
        if name and len(str(name)) >= 2:
            out[str(name)] = cid
    return out


def _recorded_pairs(events: list[Event]) -> dict[str, set[frozenset]]:
    by_chapter: dict[str, set[frozenset]] = {}
    for event in events:
        if event.kind == "relationship_changed":
            a, b = event.get("a"), event.get("b")
            if a and b:
                by_chapter.setdefault(event.chapter, set()).add(frozenset((str(a), str(b))))
    return by_chapter


def coverage_warnings(project: Path, events: list[Event], state: State, profile: dict) -> list[str]:
    cov = (profile or {}).get("coverage", {}) or {}
    triggers = cov.get("relationship_words", _DEFAULT_TRIGGERS)
    name_to_id = _name_to_id(state)
    if len(name_to_id) < 2:
        return []
    names_by_len = sorted(name_to_id, key=len, reverse=True)
    recorded = _recorded_pairs(events)

    project = Path(project)
    chapter_root = project / "chapters"
    if not chapter_root.exists():
        return []
    # Scan chapters that have prose, from the filesystem — a chapter written with
    # zero events must still be checked (that is itself a coverage failure).
    chapter_dirs = sorted(
        (p for p in chapter_root.glob("ch*") if (p / "final.txt").exists()),
        key=lambda p: chapter_sort_key(p.name),
    )
    warnings: list[str] = []
    for chapter_dir in chapter_dirs:
        chapter = chapter_dir.name
        text = (chapter_dir / "final.txt").read_text(encoding="utf-8", errors="ignore")
        chapter_recorded = recorded.get(chapter, set())
        flagged: set[frozenset] = set()
        for sentence in _SENTENCE_SPLIT.split(text):
            trigger = next((t for t in triggers if t in sentence), None)
            if not trigger:
                continue
            present_ids: list[str] = []
            for name in names_by_len:
                if name in sentence and name_to_id[name] not in present_ids:
                    present_ids.append(name_to_id[name])
            if len(present_ids) < 2:
                continue
            for i in range(len(present_ids)):
                for j in range(i + 1, len(present_ids)):
                    pair = frozenset((present_ids[i], present_ids[j]))
                    if pair in chapter_recorded or pair in flagged:
                        continue
                    flagged.add(pair)
                    a_name = state.characters[present_ids[i]].get("name", present_ids[i])
                    b_name = state.characters[present_ids[j]].get("name", present_ids[j])
                    snippet = sentence.strip()[:40]
                    warnings.append(
                        f"COVERAGE_RELATIONSHIP_UNRECORDED: {chapter} 正文出现 {a_name}↔{b_name} 的关系信号"
                        f"（「{trigger}」附近），但本章 events 没有对应 relationship_changed。例：…{snippet}…"
                    )
                    if len(warnings) >= _MAX_WARNINGS:
                        warnings.append("COVERAGE_TRUNCATED: 还有更多未记关系，先补上面这些。")
                        return warnings
    return warnings
