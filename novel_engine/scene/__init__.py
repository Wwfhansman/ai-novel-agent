"""Scene pipeline: operationalize the validated scene-level writing method.

The A/B confirmed scene-level prose (experiential-first, texture budgeted per
scene) reads better than chapter-level. This package makes that method a
repeatable engine pipeline instead of a one-off:

  plan.py      a chapter's scene plan (load/validate; draft a skeleton from the
               rolling_plan's chapter_internal_motion + narrative_weave)
  exemplars.py retrieve target-voice passages by scene type (the biggest single
               lever for LLM prose quality: real few-shot, not abstract rules)
  packet.py    assemble the per-scene writing packet the writer gets one at a
               time: entering-state slice + scene spec + exemplars + constraints
"""

__all__ = ["plan", "exemplars", "packet"]
