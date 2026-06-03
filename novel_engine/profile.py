"""Load a genre/language profile.

A profile holds every threshold and pattern that is specific to a kind of
writing (Chinese web-novel, English literary fiction, ...). The engine code is
neutral; the profile is data. A project selects its profile via
meta/model_policy.yml or project.yml `profile:`; callers may also pass a path.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from .yamlio import load_yaml

_PROFILE_DIR = Path(__file__).resolve().parent / "profiles"
_DEFAULT_PROFILE = "zh-webnovel"

_DEFAULTS: dict[str, Any] = {
    "ledger_health": {"foreshadow_stale_after": 12, "debt_overdue_grace": 0},
    "knowledge_holders": ["reader", "public"],
}


def _merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


@lru_cache(maxsize=8)
def load_profile(name_or_path: str = _DEFAULT_PROFILE) -> dict[str, Any]:
    candidate = Path(name_or_path)
    if candidate.exists():
        path = candidate
    else:
        path = _PROFILE_DIR / f"{name_or_path}.yml"
    if not path.exists():
        raise FileNotFoundError(f"Profile not found: {name_or_path} (looked in {_PROFILE_DIR})")
    data = load_yaml(path) or {}
    return _merge(_DEFAULTS, data)


def resolve_project_profile(project: Path) -> dict[str, Any]:
    """Pick a project's profile and apply per-book overrides.

    A project.yml / meta/model_policy.yml may set `profile: <name>` to pick a base
    profile, and `profile_overrides: {...}` to deep-merge book-specific tweaks
    (e.g. banned_patterns.max_not_but_per_chapter: 0 to ban not-but entirely)."""
    project = Path(project)
    base = load_profile()
    overrides: dict[str, Any] = {}
    for rel in ("project.yml", "meta/model_policy.yml"):
        data = load_yaml(project / rel)
        if not isinstance(data, dict):
            continue
        if data.get("profile"):
            try:
                base = load_profile(str(data["profile"]))
            except FileNotFoundError:
                pass
        if isinstance(data.get("profile_overrides"), dict):
            overrides = _merge(overrides, data["profile_overrides"])
    return _merge(base, overrides) if overrides else base
