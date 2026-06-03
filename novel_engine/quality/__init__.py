"""Quality layer: deterministic prose measurement and material supply.

This is the verifiable half of the quality engine. It does not judge whether
prose is *good* (that stays an LLM job), but it:

- scans for known LLM prose tics (profile-driven, not hardcoded);
- computes a voice fingerprint so drift over a long novel is measurable and
  old-vs-new prose can be compared quantitatively.

The creative contracts (scene_spec, editor_verdict) live in ../schemas and are
validated with jsonschema_lite, same as events.
"""

__all__ = ["prose_patterns", "prose_metrics"]
