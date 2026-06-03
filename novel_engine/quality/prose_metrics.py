"""Voice fingerprint: deterministic, quantitative prose metrics.

Two uses:
  1. A/B: compare new scene-level prose against the old chapter-level prose with
     a number, not just a subjective blind read.
  2. Long-form drift: does ch200 still sound like ch5? compare() a late chapter
     against an established baseline.

It measures texture (sentence-length rhythm, dialogue ratio, paragraph shape,
punctuation density), not quality. A fingerprint match does not mean good prose;
a fingerprint drift means the voice moved.
"""

from __future__ import annotations

import re
import statistics

_SENTENCE_SPLIT = re.compile(r"[。！？!?…]+")
_DIALOGUE = re.compile(r"[“「\"]([^”」\"]*)[”」\"]")
_DASH = re.compile(r"—")
_ELLIPSIS = re.compile(r"…|\.\.\.")


def _nonblank_paragraphs(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def fingerprint(text: str) -> dict:
    paragraphs = _nonblank_paragraphs(text)
    body = "".join(paragraphs)
    char_count = len(body)

    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(body) if s.strip()]
    sentence_lengths = [len(s) for s in sentences]
    paragraph_lengths = [len(p) for p in paragraphs]

    dialogue_chars = sum(len(m) for m in _DIALOGUE.findall(text))

    def per_1000(n: int) -> float:
        return round(n / char_count * 1000, 2) if char_count else 0.0

    def mean(values):
        return round(statistics.fmean(values), 2) if values else 0.0

    def stdev(values):
        return round(statistics.pstdev(values), 2) if len(values) > 1 else 0.0

    return {
        "char_count": char_count,
        "paragraph_count": len(paragraphs),
        "sentence_count": len(sentences),
        "mean_sentence_len": mean(sentence_lengths),
        "stdev_sentence_len": stdev(sentence_lengths),
        "mean_paragraph_len": mean(paragraph_lengths),
        "stdev_paragraph_len": stdev(paragraph_lengths),
        "dialogue_ratio": round(dialogue_chars / char_count, 3) if char_count else 0.0,
        "dash_per_1000": per_1000(len(_DASH.findall(text))),
        "ellipsis_per_1000": per_1000(len(_ELLIPSIS.findall(text))),
    }


_COMPARE_KEYS = (
    "mean_sentence_len",
    "stdev_sentence_len",
    "mean_paragraph_len",
    "dialogue_ratio",
    "dash_per_1000",
    "ellipsis_per_1000",
)


def compare(text_a: str, text_b: str) -> dict:
    """Compare two texts. Returns both fingerprints, per-key relative deltas, and
    a single divergence score (mean relative difference across key metrics)."""
    fa, fb = fingerprint(text_a), fingerprint(text_b)
    deltas: dict[str, float] = {}
    rel_diffs: list[float] = []
    for key in _COMPARE_KEYS:
        a, b = fa[key], fb[key]
        denom = max(abs(a), abs(b), 1e-9)
        rel = abs(a - b) / denom
        deltas[key] = round(rel, 3)
        rel_diffs.append(rel)
    return {
        "a": fa,
        "b": fb,
        "relative_deltas": deltas,
        "divergence_score": round(statistics.fmean(rel_diffs), 3) if rel_diffs else 0.0,
    }
