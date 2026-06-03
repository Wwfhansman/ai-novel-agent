"""Migrate a legacy project into a real events/ log.

Produces:
  events/bootstrap.yml   character_introduced / debt_opened / foreshadow_planted /
                         knowledge_changed for everything that existed at bootstrap
                         (created_in == bootstrap, plus all current characters).
  events/chXXX.yml       per-chapter events derived from canon_delta.yml.

This is best-effort: the legacy format does not preserve full history, so the
bootstrap step introduces every current character up front and seeds initial
ledger entries. The produced log validates cleanly and projects to an
approximation of current state. The real win is that *new* chapters then append
clean typed events. Review events/bootstrap.yml before adopting.
"""

from __future__ import annotations

from pathlib import Path

from .events import chapter_sort_key
from .legacy import _delta_to_events
from .yamlio import dump_yaml, load_yaml


def _as_list(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def build_bootstrap_events(project: Path) -> list[dict]:
    events: list[dict] = []

    chars = load_yaml(project / "entities" / "characters.yml")
    if isinstance(chars, dict):
        for item in _as_list(chars.get("characters")):
            if not isinstance(item, dict) or not item.get("id"):
                continue
            ev = {"kind": "character_introduced", "chapter": "bootstrap", "id": str(item["id"])}
            for key in ("name", "role", "fixed_profile", "current_goal", "current_stance", "intent"):
                if item.get(key):
                    ev[key] = item[key]
            ev.setdefault("name", str(item["id"]))
            events.append(ev)

    # factions / locations / items / power: introduce everything present at bootstrap.
    for filename, listkey, kind, attrs in (
        ("factions.yml", "factions", "faction_introduced", ("scale", "goal", "attitude_to_protagonist", "resources", "current_action")),
        ("locations.yml", "locations", "location_introduced", ("scale", "controlled_by", "texture", "function")),
        ("items.yml", "items", "item_introduced", ("holder",)),
        ("power_system.yml", "power_system", "power_introduced", ("stage_meaning", "cost", "test_method")),
    ):
        data = load_yaml(project / "entities" / filename)
        if not isinstance(data, dict):
            continue
        entries = data.get(listkey)
        if not isinstance(entries, list):
            # power_system.yml may be a dict of named elements; coerce.
            entries = [{"id": k, **(v if isinstance(v, dict) else {"name": str(v)})} for k, v in data.items()] \
                if listkey == "power_system" else []
        for item in _as_list(entries):
            if not isinstance(item, dict) or not item.get("id"):
                continue
            ev = {"kind": kind, "chapter": "bootstrap", "id": str(item["id"])}
            for key in attrs:
                if item.get(key) is not None:
                    ev[key] = item[key]
            ev["name"] = str(item.get("name") or item["id"])
            events.append(ev)

    debts = load_yaml(project / "ledgers" / "narrative_debts.yml")
    if isinstance(debts, dict):
        for item in _as_list(debts.get("debts")):
            if isinstance(item, dict) and item.get("id") and str(item.get("created_in")) == "bootstrap":
                ev = {"kind": "debt_opened", "chapter": "bootstrap", "id": str(item["id"]),
                      "description": str(item.get("description") or "")}
                for key, src in (("type", "type"), ("urgency", "urgency"), ("payoff_window", "expected_payoff_window")):
                    if item.get(src):
                        ev[key] = str(item[src])
                events.append(ev)

    fore = load_yaml(project / "ledgers" / "foreshadowing.yml")
    if isinstance(fore, dict):
        items = fore.get("foreshadowing") if "foreshadowing" in fore else fore.get("items")
        for item in _as_list(items):
            if isinstance(item, dict) and item.get("id") and str(item.get("created_in")) == "bootstrap":
                events.append({"kind": "foreshadow_planted", "chapter": "bootstrap",
                               "id": str(item["id"]), "content": str(item.get("content") or "")})

    knowledge = load_yaml(project / "ledgers" / "knowledge_state.yml")
    if isinstance(knowledge, dict):
        for item in _as_list(knowledge.get("knowledge_items")):
            if not isinstance(item, dict):
                continue
            topic = item.get("id") or item.get("topic")
            visibility = item.get("visibility")
            if topic and isinstance(visibility, dict):
                for holder, level in visibility.items():
                    events.append({"kind": "knowledge_changed", "chapter": "bootstrap",
                                   "topic": str(topic), "holder": str(holder), "level": str(level)})

    return events


def build_chapter_events(project: Path) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    chapter_root = project / "chapters"
    if not chapter_root.exists():
        return out
    for chapter_dir in sorted((p for p in chapter_root.glob("ch*") if p.is_dir()),
                              key=lambda p: chapter_sort_key(p.name)):
        delta = load_yaml(chapter_dir / "canon_delta.yml")
        if not isinstance(delta, dict):
            continue
        events = _delta_to_events(chapter_dir.name, delta, f"migrated:{chapter_dir.name}", rel_as_note=True)
        out[chapter_dir.name] = [e.data for e in events]
    return out


def seed_bootstrap(project: Path, force: bool = False) -> tuple[Path, int]:
    """New-book path: write only events/bootstrap.yml from the project's initial
    entities/ledgers (no chapter conversion). Returns (path, event_count)."""
    project = Path(project)
    path = project / "events" / "bootstrap.yml"
    if path.exists() and not force:
        raise FileExistsError(f"{path} already exists; pass force=True to overwrite.")
    bootstrap = build_bootstrap_events(project)
    dump_yaml(path, {"chapter": "bootstrap", "events": bootstrap})
    return path, len(bootstrap)


def migrate(project: Path, force: bool = False) -> tuple[Path, list[str]]:
    """Write events/ for a legacy project. Returns (events_dir, written_filenames)."""
    project = Path(project)
    events_dir = project / "events"
    if events_dir.exists() and any(events_dir.glob("*.yml")) and not force:
        raise FileExistsError(f"{events_dir} already has event files; pass force=True to overwrite.")
    events_dir.mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    bootstrap = build_bootstrap_events(project)
    if bootstrap:
        dump_yaml(events_dir / "bootstrap.yml", {"chapter": "bootstrap", "events": bootstrap})
        written.append("bootstrap.yml")
    for chapter, events in build_chapter_events(project).items():
        dump_yaml(events_dir / f"{chapter}.yml", {"chapter": chapter, "events": events})
        written.append(f"{chapter}.yml")
    return events_dir, written
