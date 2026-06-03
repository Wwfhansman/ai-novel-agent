"""Load and validate canon events.

New authoritative layout (per project):

    events/
      ch001.yml      # a list of event objects, or {chapter: ch001, events: [...]}
      ch002.yml
      ...

Each event is validated against schemas/event.schema.json. The chapter id is
injected from the filename when an event omits it.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from . import jsonschema_lite
from .yamlio import load_yaml

_SCHEMA_PATH = Path(__file__).resolve().parent / "schemas" / "event.schema.json"
_CHAPTER_RE = re.compile(r"ch(\d+)")


@lru_cache(maxsize=1)
def event_schema() -> dict:
    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


def chapter_sort_key(chapter: str) -> int:
    match = _CHAPTER_RE.search(chapter or "")
    return int(match.group(1)) if match else -1


@dataclass(frozen=True)
class Event:
    kind: str
    chapter: str
    data: dict[str, Any] = field(default_factory=dict)
    source: str = ""

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)


def _coerce_event_list(raw: Any, chapter_hint: str) -> list[dict[str, Any]]:
    if raw is None:
        return []
    if isinstance(raw, dict) and "events" in raw:
        events = raw.get("events") or []
    elif isinstance(raw, list):
        events = raw
    else:
        events = []
    out: list[dict[str, Any]] = []
    for item in events:
        if isinstance(item, dict):
            item = dict(item)
            item.setdefault("chapter", chapter_hint)
            out.append(item)
    return out


def validate_event(obj: dict[str, Any]) -> list[str]:
    return jsonschema_lite.validate(obj, event_schema())


def load_chapter_events(path: Path) -> tuple[list[Event], list[str]]:
    """Load and validate events from one events/chXXX.yml file."""
    path = Path(path)
    chapter_hint = path.stem
    errors: list[str] = []
    try:
        raw = load_yaml(path)
    except Exception as exc:  # parser-specific
        return [], [f"EVENT_PARSE_ERROR: {path}: {exc}"]

    events: list[Event] = []
    for index, obj in enumerate(_coerce_event_list(raw, chapter_hint)):
        problems = validate_event(obj)
        if problems:
            for problem in problems:
                errors.append(f"EVENT_SCHEMA: {path}[{index}]: {problem}")
            continue
        events.append(
            Event(
                kind=obj["kind"],
                chapter=str(obj.get("chapter") or chapter_hint),
                data=obj,
                source=f"{path.name}[{index}]",
            )
        )
    return events, errors


def events_dir(project: Path) -> Path:
    return Path(project) / "events"


def load_project_events(project: Path) -> tuple[list[Event], list[str]]:
    """Load every events/ch*.yml in chapter order, validating each event."""
    directory = events_dir(project)
    all_events: list[Event] = []
    all_errors: list[str] = []
    if not directory.exists():
        return all_events, [f"NO_EVENTS_DIR: {directory} does not exist."]
    # Includes a leading bootstrap.yml (chapter_sort_key -> -1 sorts first).
    files = sorted(directory.glob("*.yml"), key=lambda p: chapter_sort_key(p.stem))
    for path in files:
        events, errors = load_chapter_events(path)
        all_events.extend(events)
        all_errors.extend(errors)
    return all_events, all_errors
