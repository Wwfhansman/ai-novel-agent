# Chapter Review

Example chapter not written.

## Reader Reward Check

- Required reward: old-wick memory anomaly plus a risky physical clue.
- New expectation: patrol's recovery motive should become the next question.
- Risk: the example final is intentionally tiny, so it only demonstrates protocol shape.

## TXT Format Check

- Title line should match `第X章 标题`.
- Body should use one blank line after title and no blank lines between ordinary paragraphs.
- Formal project chapters should use normal paragraph density; this example is intentionally short.

## Memory Update Check

- `summary.yml` and `canon_delta.yml` should record `handoff_to_next_chapter`.
- `planning/active_flow.yml` and `planning/rolling_plan.yml` should carry the patrol handoff.
- Current state files should not treat this example as a real full chapter.

After formal writing, check:

- Did the prose follow the detailed rolling synopsis without sounding like a synopsis?
- Did it feel like a concrete repair scene rather than a lore explanation?
- Did it deliver a concrete reader reward, such as an old-wick memory anomaly, a risky hidden fragment, or a new question?
- Did it create a new expectation for ch002?
- Did the opening and ending behave as a cut from `arc_001_old_wick` rather than as a self-contained chapter container?
- Did the ending avoid protagonist recap or next-step analysis?
- Did the ending leave an external handoff for ch002?
- Did `final.txt` use one blank line after title and no blank lines between ordinary body paragraphs?
- Did the chapter use normal mobile-readable paragraph density rather than a few giant blocks?
- Did `python scripts/validate_novel_output.py projects/example-project --chapters ch001 --fix-format` pass?
- Were `summary.yml`, `canon_delta.yml`, `entities/`, `ledgers/`, `planning/active_flow.yml`, and `planning/rolling_plan.yml` updated?
