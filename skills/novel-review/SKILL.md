---
name: novel-review
description: Review an AI Novel Agent project, round, chapter, or memory state. Use for cold-start continuity checks, quality review, source-of-truth conflict detection, context pack validation, narrative debt checks, information visibility checks, and run-drift diagnosis.
---

# Novel Review

Use this skill to inspect whether a project can be safely continued by a fresh agent and whether recent writing remains aligned with the book.

## Read First

Read:

- `docs/CANON_AND_SAFETY.md`
- `docs/CONTEXT_PACK.md`
- `docs/MEMORY_MODEL.md`
- `docs/WORKFLOWS.md`
- Target project `project.yml`
- `meta/model_policy.yml` if present

## Review Modes

### Cold-Start Review

Act as a fresh agent. Read only project files, not prior conversation. Verify that the project explains:

- What the book is.
- What long-form scale the book is aiming for.
- Which macro stage/map/volume the current chapters occupy.
- Whether world, region, city, faction, and power-system scale remain stable.
- Whether progression and secret reveals respect the current pacing budget.
- Current volume goal and stage.
- Current protagonist and major character goals.
- Active narrative debts.
- Knowledge state and secrets.
- World state and pressures.
- Active cross-round narrative flow.
- Next round writing target.
- Whether model routing is safe and no fast-model output entered final prose or canon without premium/human confirmation.

### Chapter Review

Review a specific chapter:

- `context_pack.md`
- `brief.md`
- optional `outline.md` if it exists
- `draft.txt` or `final.txt`
- `summary.yml`
- `canon_delta.yml`
- affected `entities/`, `ledgers/`, and `planning/`

Check whether final state files were updated after the chapter.

### Round Review

Review the last 3 chapters:

- round context pack
- all chapter context packs
- all chapter summaries and deltas
- updated ledgers and rolling plan

Check whether the batch produced coherent progress without becoming an artificial three-chapter story unit.

## Required Checks

1. **Context pack validity**
   - Does it list read files, reasons, key takeaways, old chapter lookbacks, unknowns, and required updates?

2. **Source-of-truth consistency**
   - Use `docs/CANON_AND_SAFETY.md`.
   - If summary, delta, entity state, ledger, and planning disagree, identify the authoritative file.

3. **Reader and debt health**
   - Identify overdue debts.
   - Identify too much setup without payoff.
   - Identify missing payoff for target reader.
   - Identify whether each chapter delivered a concrete reader reward.
   - Identify whether each chapter created or advanced a next expectation.

4. **Character intent**
   - Check whether each important character acted from current goals, not just plot convenience.

5. **Knowledge visibility**
   - Check whether any character knows something they should not.
   - Check whether secrets were revealed too early.

6. **World state**
   - Check whether factions, resources, crises, and public pressure reacted to recent chapters.

7. **Style and genre alignment**
   - Compare to `book/constitution.md`, `book/reader_model.yml`, and `book/style_memory.md`.

8. **Long-form scale control**
   - Check whether `book/longform_blueprint.yml` exists and is current.
   - Check whether the current chapter range belongs to the expected macro stage.
   - Check whether world-level names, regions, cities, factions, and institutions keep their intended scale.
   - Flag scale collapse, such as a world becoming a city, a regional force behaving like a household, or an opening-map conflict being treated as the whole book.
   - Check whether protagonist power, major opportunities, and artifact/secret reveals are moving within the current stage budget.
   - Check whether `planning/rolling_plan.yml`, `active_flow.yml`, and recent prose contradict the blueprint.
   - Treat target length, macro structure, scale map, power pacing, and secret pacing as protected unless `novel-change` confirms a change.

9. **Detailed synopsis alignment**
   - Check whether `planning/active_flow.yml` is present, current, and compatible with the last written chapter.
   - Check whether `planning/rolling_plan.yml` is detailed enough to drive prose.
   - Check whether `planning/rolling_plan.yml` contains only upcoming chapters, not completed history.
   - Check whether completed chapters were archived to `planning/completed_plan_log.yml`.
   - Check whether distant ideas live in `planning/future_backlog.yml`, not the current future window.
   - Check whether `current_round.yml` is only a production extract, not a competing plan or hidden round goal.
   - Check whether future planned chapters repeat decisions already completed.

10. **Cross-round flow continuity**
   - Check whether each chapter opens from the previous external handoff or records a justified transition.
   - Check whether the last chapter of the batch closes because the story earned closure, not because the batch ended.
   - Check whether `planning/rolling_plan.yml` continues the same event chain after the batch when the flow is still active.
   - Check whether ch003/ch006/ch009-style chapters are disproportionately recap-like, reflective, or conclusive.

11. **Prose and TXT format**
   - Run `python scripts/validate_novel_output.py <project> --chapters <reviewed chapters>` from the repository root when the script exists.
   - Treat validator failures as required fixes, not suggestions.
   - Check whether the chapter reads like fiction rather than a task report.
   - Check whether the ending collapses into protagonist recap, analysis, or next-step thinking.
   - Check whether `handoff_to_next_chapter` comes from external motion, not only from a protagonist decision.
   - Check whether `final.txt` uses one blank line after the title and no blank lines between ordinary body paragraphs.

12. **Reader reward**
   - Check whether each chapter has a `Reader Reward Check` in review or context pack.
   - Check whether the reward appears in the actual prose, not only the plan.
   - Flag chapters that only move setup forward without payoff, reveal, cost, leverage shift, relationship change, or memorable fictional material.

13. **Model routing**
   - Check whether `meta/model_policy.yml` exists.
   - Check context packs and session logs for model routing records when multiple models were used.
   - Flag any final prose, active_flow, rolling_plan, protected-file change, or canon merge that appears to have been done only by a fast or cheap model.

## Output Format

Produce:

```text
Review Summary
- Overall status: pass / pass with risks / fail
- Biggest risks
- Required fixes
- Suggested fixes
- Files that appear stale or conflicting
- Long-form scale risks
- Model routing risks
- Whether novel-change is needed
```

## Failure Handling

If the project cannot be continued safely:

- Do not rewrite正文.
- List blocking missing files or contradictions.
- Recommend `novel-change` for structural changes.
- Recommend context pack regeneration if the writing input record is incomplete.
