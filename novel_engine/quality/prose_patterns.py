"""Profile-driven AI-prose-tic scanner.

The patterns and limits come from the profile (profiles/zh-webnovel.yml
banned_patterns), not from hardcoded constants. This both decouples the checks
from a single genre/language and closes the loop on the profile, which until now
held patterns nothing read.

These are draft-stage advisories, mirroring the legacy check_not_but.py policy:
the not-but contrast is allowed once per chapter; the other shapes are hard tics
to revise. The scanner returns located hits; evaluate() applies the limit.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Names of the hard (always-flag) patterns inside profile.banned_patterns.
_HARD_KEYS = ("triple_negated_inner_state", "meta_original_text", "arrow_or_numbered_cognition")


@dataclass
class Hit:
    key: str
    count: int
    samples: list[str]


def _flatten(text: str) -> str:
    return text.replace("\n", "")


def scan(text: str, profile: dict) -> list[Hit]:
    """Return per-pattern hit counts (with up to 3 sample matches each)."""
    banned = (profile or {}).get("banned_patterns", {}) or {}
    flat = _flatten(text)
    hits: list[Hit] = []
    for key, pattern in banned.items():
        if not isinstance(pattern, str) or key == "max_not_but_per_chapter":
            continue
        try:
            matches = re.findall(pattern, flat)
        except re.error:
            continue
        if matches:
            samples = [m if isinstance(m, str) else next((g for g in m if g), "") for m in matches[:3]]
            hits.append(Hit(key=key, count=len(matches), samples=samples))
    return hits


def evaluate(text: str, profile: dict) -> tuple[list[str], list[str]]:
    """Apply the profile's policy. Returns (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []
    banned = (profile or {}).get("banned_patterns", {}) or {}
    max_not_but = banned.get("max_not_but_per_chapter", 1)
    by_key = {hit.key: hit for hit in scan(text, profile)}

    contrast = by_key.get("contrast_negation")
    if contrast and contrast.count > max_not_but:
        errors.append(
            f"OVERUSED_NOT_BUT_PATTERN: '不是X而是Y' used {contrast.count} times "
            f"(max {max_not_but}). Rewrite the rest as direct observation, action, dialogue, or consequence."
        )

    for key in _HARD_KEYS:
        hit = by_key.get(key)
        if hit:
            errors.append(
                f"{key.upper()}: {hit.count} occurrence(s). "
                "Move the information into action, dialogue, consequence, or scene texture."
            )
    return errors, warnings
