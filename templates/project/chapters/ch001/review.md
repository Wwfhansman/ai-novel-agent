# Chapter Review

## Synopsis Fit

Did the chapter follow the detailed rolling synopsis without sounding like a synopsis?

## Continuity

Did it continue naturally from the previous chapter?

Did the opening pick up `handoff_to_next_chapter` from the prior chapter or justify a transition?

## Fictional Material

What concrete scenes, actions, objects, dialogue, or consequences made this feel like fiction rather than a report?

## Reader Reward Check

- What concrete reader reward did this chapter deliver?
- What existing expectation, debt, or promise did it advance or pay?
- What new expectation did it create?
- What external cost, leverage shift, reveal, or relationship change happened?
- What image, line, action, or object is memorable?

## Ending Check

Does the ending avoid protagonist recap, analysis, or "next step" thinking?

Does the ending leave motion in the world through action, cost, arrival, exposure, pressure, relationship change, or information visibility?

Is the last paragraph more than a mood button or abstract one-line hook?

## Round Container Check

- [ ] This chapter did not open/reset/close merely to fit a three-chapter batch.
- [ ] If this is the last chapter of a round, it does not become a round summary unless the active flow earned a payoff.
- [ ] `handoff_to_next_chapter` points to a concrete external continuation.

## TXT Format Check

- [ ] One blank line after the chapter title.
- [ ] No blank lines between ordinary body paragraphs.
- [ ] Extra blank lines only for deliberate scene breaks.
- [ ] Paragraph density is mobile-readable, not a few giant blocks.
- [ ] Most paragraphs are 40-160 Chinese characters; any paragraph over 220 characters has a reason.
- [ ] `python scripts/validate_novel_output.py <project> --chapters ch001 --fix-format` passed.

## Weakness Or Risk

Name at least one weakness or risk. If revised, describe the fix.

## Memory Update Check

- [ ] `summary.yml` updated.
- [ ] `canon_delta.yml` updated.
- [ ] `entities/` synchronized when current state changed.
- [ ] `ledgers/` synchronized when current state changed.
- [ ] `planning/active_flow.yml` updated with actual cut and handoff.
- [ ] `planning/rolling_plan.yml` refreshed so future chapters do not repeat completed choices.
