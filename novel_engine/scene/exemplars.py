"""Retrieve target-voice exemplars by scene type.

The single biggest lever for LLM prose quality is strong, specific in-context
examples of the target voice — not abstract style rules. This indexes a project's
exemplar corpus by scene type and returns the best-matching passages for a scene,
so each scene's writer prompt carries real few-shot anchors.

Corpus format — style/exemplars.yml (optional):

    face_slap:
      - "passage in the target voice ..."
      - "another ..."
    domestic:
      - "..."
    _default:
      - "general voice anchor ..."

If the file is absent, retrieval falls back to whole paragraphs of
style/samples.md (untyped), which is better than nothing.
"""

from __future__ import annotations

from pathlib import Path

from ..yamlio import load_yaml

# Map common chapter_function / pacing values onto exemplar buckets so a chapter
# function like "building / relationship" finds relevant anchors.
_TYPE_ALIASES = {
    "face_slap": ("face_slap", "打脸"),
    "building": ("building", "种田", "日常", "domestic"),
    "relationship": ("relationship", "关系", "社交", "domestic"),
    "reveal": ("reveal", "揭秘", "悬疑", "mystery"),
    "investigation": ("investigation", "调查", "mystery"),
    "battle": ("battle", "战斗", "打斗"),
    "comedy": ("comedy", "搞笑", "沙雕"),
}


def _candidate_keys(scene_type: str | None) -> list[str]:
    if not scene_type:
        return ["_default"]
    raw = [part.strip().lower() for part in str(scene_type).replace("/", " ").split() if part.strip()]
    keys: list[str] = []
    for token in raw:
        keys.append(token)
        for canonical, aliases in _TYPE_ALIASES.items():
            if token in aliases or token == canonical:
                keys.extend([canonical, *aliases])
    keys.append("_default")
    # de-dupe, preserve order
    seen: set[str] = set()
    return [k for k in keys if not (k in seen or seen.add(k))]


def _load_corpus(project: Path) -> dict[str, list[str]]:
    data = load_yaml(Path(project) / "style" / "exemplars.yml")
    if isinstance(data, dict):
        return {str(k): [str(v) for v in (vs or [])] for k, vs in data.items()}
    return {}


def _samples_fallback(project: Path, k: int) -> list[str]:
    path = Path(project) / "style" / "samples.md"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    # Quoted blockquote lines are the most exemplar-like part of samples.md.
    quotes = [line.lstrip("> ").strip() for line in text.splitlines() if line.strip().startswith(">")]
    quotes = [q for q in quotes if len(q) > 12]
    return quotes[:k]


def scaffold(project: Path) -> tuple[Path, bool]:
    """Write a starter style/exemplars.yml: samples.md quotes seed _default, with
    empty typed buckets to fill. Returns (path, created)."""
    path = Path(project) / "style" / "exemplars.yml"
    if path.exists():
        return path, False
    seed = _samples_fallback(project, 5)
    data: dict[str, list[str]] = {
        "_default": seed or ["在这里放 1-3 段能代表本书语感的真实正文。"],
        "building": [], "relationship": [], "reveal": [],
        "investigation": [], "battle": [], "comedy": [],
    }
    from ..yamlio import dump_yaml

    dump_yaml(path, data)
    return path, True


def retrieve(project: Path, scene_type: str | None, k: int = 3) -> list[str]:
    """Return up to k exemplar passages for a scene type."""
    corpus = _load_corpus(project)
    out: list[str] = []
    if corpus:
        for key in _candidate_keys(scene_type):
            for passage in corpus.get(key, []):
                if passage not in out:
                    out.append(passage)
                if len(out) >= k:
                    return out[:k]
    if len(out) < k:
        for passage in _samples_fallback(project, k):
            if passage not in out:
                out.append(passage)
            if len(out) >= k:
                break
    return out[:k]
