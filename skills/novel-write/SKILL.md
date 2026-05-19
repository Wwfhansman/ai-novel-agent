---
name: novel-write
description: Continue an existing AI Novel Agent project by writing the next chapter or next three-chapter round. Use for daily novel production, active narrative flow maintenance, detailed rolling synopsis updates, context pack generation, prose drafting, chapter review, canon delta creation, and memory updates.
---

# Novel Write

Use this skill for normal production writing. Default execution unit: one round of 3 chapters.

Important distinction:

- **Narrative Flow** is the story continuity unit.
- **Round** is only a production batch.
- **Chapter** is only a serial cut point inside a larger flow.

Never let the round size decide the story shape. A narrative flow may span 2, 5, 9, or more chapters, and may cross round boundaries.

## Core Model

Use three planning layers:

1. `planning/active_flow.yml`
   - The current continuous story flow.
   - Tracks the ongoing pressure, scene chain, last visible cut, and next opening.
   - It is allowed to span across multiple rounds.

2. `planning/rolling_plan.yml`
   - The detailed 6-15 chapter synopsis.
   - Each chapter should link to a flow and identify its entry/pickup and cut point.

3. `planning/current_round.yml`
   - A 3-chapter production extract.
   - It must not become a narrative container.

## Hard Rules

- Never write `draft.txt` or `final.txt` before generating:
  - `planning/context_packs/round_XXX_context_pack.md`
  - `chapters/chXXX/context_pack.md`
- `planning/active_flow.yml`, `planning/rolling_plan.yml`, and `planning/current_round.yml` must be valid YAML before drafting.
- Do not translate a plan, synopsis, outline, or checklist directly into prose.
- Do not treat one chapter or one round as a complete narrative box.
- Round boundaries are production boundaries, not story boundaries. Do not make ch003/ch006/ch009 feel like cleanup, recap, reset, or phase closure unless `planning/active_flow.yml` and `planning/rolling_plan.yml` explicitly say the story has earned payoff.
- If the previous chapter declares `handoff_to_next_chapter`, this chapter's opening must pick it up directly unless a justified transition is recorded in context pack and review.
- If the previous chapter declares `handoff_to_next_chapter` in `canon_delta.yml`, reflect it in this chapter's `brief.md`, `context_pack.md`, and `planning/rolling_plan.yml` entry before drafting.
- Do not use docs, schemas, templates, examples, sample novels, or other projects as creative source material. They are process references only.
- Do not silently change protected canon. Route major changes to `novel-change`.
- Before accepting any `final.txt`, run `python scripts/validate_novel_output.py <project> --chapters chXXX` from the repository root when the script exists. If it fails, fix the listed issues and rerun. Do not call the chapter complete until validation passes.
- Read `planning/rolling_plan.yml` in full before each round. It is the future-planning authority.
- Do not copy full project files or the full rolling plan into context packs. Context packs are working memory, not a duplicated database.
- Follow `meta/model_policy.yml` when it exists. A fast or cheap model may assist mechanical tasks, but final prose, active_flow, rolling_plan, canon merges, and protected-file decisions must be confirmed by a premium model or human.

## Context Budget Policy

Use working-memory context, like a human writer:

- remember the whole-book promise, current volume goal, active flow, and full future rolling plan;
- keep recent chapters sharp: previous chapter full text, recent summaries, and recent full text when continuity needs it;
- read entity and ledger entries by relevance, not by default full dump;
- reread old chapter originals only when a concrete trigger exists.

Recommended context pack budgets:

- round context pack: 3000-5000 Chinese characters;
- chapter context pack: 1000-2500 Chinese characters.

`planning/rolling_plan.yml` is the exception to the lean-read rule: read it in full each round, because future planning decides how the current chapter should be written. But summarize only the batch chapters, adjacent chapters, and later constraints that affect this task.

## Banned Default Endings

These are hard failures unless the project style explicitly demands them and the review explains why:

- protagonist sits and thinks;
- protagonist summarizes lessons;
- protagonist plans the next step in abstract;
- protagonist looks at night, window, candle, distance, or empty room as a mood button;
- "he knew..." / "he understood..." / "this step was important..." endings;
- final one-line abstract atmosphere paragraphs;
- chapter ending exists only to say the next chapter will matter.

Prefer cut points:

- an action has just begun;
- a conversation is interrupted or left unfinished;
- someone arrives;
- a cost lands;
- a concrete object, order, wound, document, or sound changes the situation;
- a choice is made publicly and cannot be withdrawn;
- pressure moves before the protagonist can fully process it.

## Read First

Read once per session or when uncertain:

- `docs/CONTEXT_PACK.md`
- `docs/CANON_AND_SAFETY.md`
- `docs/MEMORY_MODEL.md`
- `docs/FILE_FORMATS.md`
- Current project `project.yml`
- `book/constitution.md`
- `book/reader_model.yml`
- `book/style_memory.md`
- `style/rewrite_rules.md`
- `planning/active_flow.yml`
- `planning/rolling_plan.yml`
- `planning/current_round.yml` if it exists
- `meta/model_policy.yml` if it exists

Do not paste these files into context packs. Extract only the operational conclusions needed for the current task.

## Model Routing

Use `docs/MODEL_ROUTING.md` and project `meta/model_policy.yml` when available.

Default:

- Use `premium_model` for active_flow, rolling_plan, chapter concept, draft prose, final prose revision, ending rewrite, canon merge, and quality gate.
- Use `fast_model` only for YAML/TXT formatting, validator error summaries, diff summaries, session logs, and other mechanical tasks whose output can be checked.
- Hybrid context pack drafting is allowed, but the writing agent must confirm the final context pack before drafting.
- Never let `fast_model` directly write or approve `final.txt`.
- Never let `fast_model` make Level 3-5 change decisions or protected-file edits.

If model routing is used, record it in the round context pack or `meta/session_log.md`.

## Source Of Truth

- `final.txt` is chapter canon text.
- `summary.yml` records what happened in that chapter.
- `canon_delta.yml` records what changed in that chapter. It is a change log, not current state.
- Current character state lives in `entities/characters.yml`.
- Current world state lives in `ledgers/world_state.yml`.
- Current knowledge visibility lives in `ledgers/knowledge_state.yml`.
- Current continuous flow lives in `planning/active_flow.yml`.
- Future 6-15 chapter synopsis lives in `planning/rolling_plan.yml`.
- Current round extract lives in `planning/current_round.yml`.

When files conflict, follow `docs/CANON_AND_SAFETY.md`. Do not merge contradictions casually.

## Narrative Flow Requirements

Before each round, ensure `planning/active_flow.yml` describes the current continuous story flow.

A flow should include:

- flow id and status;
- intended chapter span or flexible range;
- current pressure already in motion;
- story question or practical problem driving the flow;
- scene chain, not chapter boxes;
- last cut from the previous chapter;
- required next opening if one exists;
- conditions for ending this flow;
- whether this round continues, turns, or ends the flow.

Start a new flow only when the story genuinely changes subject, location, POV, objective, or dramatic mode. Do not start a new flow merely because a new round begins.

## Rolling Synopsis Requirements

Before each round, ensure `planning/rolling_plan.yml` contains a detailed 6-15 chapter forward window.

Each planned chapter should include:

- chapter id and provisional title;
- status;
- `flow_id`;
- `flow_position`: start / continue / turn / end / bridge;
- 300-800 Chinese characters of story synopsis;
- `entry_from_previous`: the concrete pickup from the prior cut;
- required plot developments;
- important characters and what they want;
- pressure, obstacle, or complication;
- `chapter_turn`: the irreversible external change caused by the chapter;
- expected payoff, reveal, or reader reward;
- `cut_point`: where the chapter should cut without closing the narrative;
- `handoff_to_next_chapter`: the first visible moment, external pressure, object, consequence, or unfinished action the next chapter should pick up;
- forbidden moves or canon constraints.

This is story-content planning, not an intra-chapter prose template.

If the rolling synopsis is too thin, expand it before drafting. Do not compensate for a thin synopsis by inventing a rigid `outline.md`.

## Round Workflow

1. **Establish checkpoint**
   - If Git is available and the project tracks real content, create or recommend a checkpoint before the round.

2. **Validate planning YAML**
   - Parse `planning/active_flow.yml`, `planning/rolling_plan.yml`, and `planning/current_round.yml` if present.
   - Stop if any of them are invalid YAML.
   - Run `python scripts/validate_novel_output.py <project> --chapters <recent chapters> --skip-planning` only for TXT checks when validating old chapters, then run without `--skip-planning` before drafting the new batch.
   - If planning validation reports stale fields such as `bridge_to_next`, `continuity_from_previous`, or `next_hook`, rewrite planning files into the active-flow format before drafting.

3. **Refresh active flow and rolling synopsis**
   - Read current canon and planning files.
   - Update `planning/active_flow.yml` so the ongoing flow continues across the round boundary when appropriate.
   - Update `planning/rolling_plan.yml` so the next 6-15 chapters are detailed enough to drive prose.
   - Remove or mark completed chapters; do not leave future chapters repeating decisions already made.

4. **Compile round context**
   - Read according to `docs/CONTEXT_PACK.md`.
   - Read `meta/model_policy.yml` if present and record the model routing plan.
   - Always read `planning/rolling_plan.yml` in full.
   - Read recent 12-15 chapter summaries when available.
   - Read recent 1-3 chapter `final.txt` files when continuity needs exact prose, scene carryover, or tone.
   - Read only relevant entity and ledger entries for this batch.
   - Read key old chapter originals when old foreshadowing, debts, objects, relationships, rules, or lines become relevant.
   - Write `planning/context_packs/round_XXX_context_pack.md`.
   - Keep the round pack within the context budget unless the project is at a major transition or user explicitly asks for a fuller audit.

5. **Create current round extract**
   - Plan exactly 3 chapters unless the user asks otherwise.
   - Extract or condense each chapter from `planning/rolling_plan.yml`.
   - Include `flow_id`, `flow_position`, `inbound_pressure`, `chapter_turn`, `outbound_pressure`, and `handoff_to_next_chapter`.
   - Use `batch_tasks`, not round-level story goals.
   - Do not invent a separate competing plan.
   - Write `planning/current_round.yml`.

6. **Write each chapter as a cut from the flow**
   - Create or update `chapters/chXXX/brief.md` from the detailed synopsis and flow continuity.
   - Generate `chapters/chXXX/context_pack.md`.
   - Chapter context should include this chapter's rolling-plan entry, adjacent chapter constraints when useful, previous handoff, active flow, and relevant targeted entity/ledger entries. Do not include full ledgers or the whole rolling plan.
   - Keep the chapter pack within the context budget unless the chapter is paying off old material.
   - Optionally write `outline.md` only as freeform notes if useful. Do not make it a required scene-beat checklist.
   - Draft `draft.txt` as novel prose.
   - Revise for continuity, concreteness, anti-reporting, and cut-point behavior.
   - Write confirmed text to `final.txt`.
   - If a cheaper model assisted formatting or summaries, confirm no unreviewed cheap-model prose entered `final.txt` or canon state.
   - Run `python scripts/validate_novel_output.py <project> --chapters chXXX --fix-format`.
   - If validation reports a reflective ending, short atmosphere ending, or protagonist thought ending, rewrite the ending and rerun validation.
   - Write `review.md`, `summary.yml`, and `canon_delta.yml`.
   - Merge current state into `entities/`, `ledgers/`, `volumes/`, and `planning/`.
   - Update `planning/active_flow.yml` with the chapter's actual last visible cut and handoff.

7. **End round**
   - Do not close the narrative flow just because the round ended.
   - Do not generate a round-level story conclusion.
   - Update current volume summary/state and active arc.
   - Evaluate idea pool and narrative debts.
   - Refresh `planning/rolling_plan.yml` so the next round picks up the active flow.
   - Record a session summary in `meta/session_log.md`.

## Drafting Guidance

During prose drafting, focus on **what is happening now**.

Good drafting behavior:

- open from the prior chapter's last visible pressure when possible;
- let characters pursue wants in the scene instead of explaining their roles;
- let exposition surface because someone needs, hides, misreads, trades, or weaponizes information;
- allow small local inventions if they serve the chapter and do not break canon;
- cut while the situation is still moving;
- make the next chapter feel like the next breath, not a new task.

Avoid:

- reset openings that ignore the prior cut;
- ending with a neat protagonist recap;
- numbered lessons in prose such as "first, second, third" unless the character is literally writing a document;
- default openings like "the next day" when time passage is not the drama;
- paragraphs that only restate the plan;
- repetitive "arrive -> observe -> analyze -> arrange -> think" chapters;
- forcing every chapter or every round to have the same internal rhythm.
- making every third chapter cleaner, more reflective, or more conclusive than the surrounding chapters just because the batch ended.

## TXT Format Rule

`draft.txt` and `final.txt` must look like normal TXT novel text:

```text
第八章 章名

正文第一段。
正文第二段。
正文第三段。
```

- Keep one blank line after the chapter title.
- Do not put blank lines between ordinary body paragraphs.
- Use an extra blank line only for a deliberate scene break.
- Do not include review notes, YAML, Markdown headings, or checklist language inside `draft.txt` or `final.txt`.
- Normal paragraphing is still required. "No blank lines between paragraphs" means paragraphs are separated by a single newline, not that multiple actions should be merged into giant blocks.
- For a 2000-3500 Chinese character web-novel chapter, aim for 25-60 body paragraphs.
- Most body paragraphs should be 40-160 Chinese characters.
- Split when action changes, speaker changes, a reaction lands, a new piece of information appears, the camera shifts, or the rhythm needs a beat.
- A paragraph over 220 Chinese characters is a warning sign. A paragraph over 360 Chinese characters is usually a formatting failure unless it is a deliberate long-shot passage explained in review.
- Do not swing back to fake rhythm: avoid dense one-line paragraphs unless they carry a real beat.

## Review Checklist

Before writing `final.txt`, create or update `review.md`.

The review must be diagnostic, not self-praise. It must name at least one weakness or risk and say whether it was fixed.

Check:

- Is this chapter a cut from the active flow, not an independent container?
- Does the opening pick up the previous cut? If not, is the transition justified?
- Does the chapter follow the detailed synopsis without sounding like a synopsis?
- Does it contain concrete fictional material, not only explanation and planning?
- Did a character make a choice, pay a cost, gain leverage, lose something, expose something, or change a relationship?
- Is there enough reader reward for the genre and current debt window?
- Does the ending avoid recap/thought-summary behavior?
- Does the ending create a concrete `handoff_to_next_chapter` grounded in external motion?
- If this is the last chapter of a round, does it avoid becoming a round summary or artificial pause?
- Are body paragraphs single-spaced in TXT format?
- Is paragraph density readable on mobile, with normal body paragraphs rather than 7-9 giant blocks?
- Did `scripts/validate_novel_output.py` pass for this chapter?
- Are `summary.yml`, `canon_delta.yml`, and current state files updated?
- Did `active_flow.yml` and `rolling_plan.yml` change so the next chapter continues the flow?

## Do Not Silently Modify

Route to `novel-change` if writing would:

- modify the creative constitution;
- change protagonist core desire;
- kill or permanently remove a major character;
- reveal an endgame-level secret;
- change the current volume goal;
- promote a major idea into mainline canon;
- perform a large retcon.

## Writable Files

During normal writing, this skill may modify:

- `planning/active_flow.yml`
- `planning/context_packs/*`
- `planning/current_round.yml`
- `planning/rolling_plan.yml`
- `chapters/chXXX/*`
- `entities/*` when current state changes
- `ledgers/*`
- `volumes/*`
- `arcs/*`
- `book/global_summary.md`
- `book/style_memory.md` only for observed style memory, not constitution changes
- `meta/session_log.md`

Protected or confirmation-required:

- `book/constitution.md`
- endgame-level secrets
- protagonist core motive
- current volume goal
- major character permanent removal
- large retcons

## Failure Handling

Stop before drafting if:

- planning YAML is invalid;
- context packs cannot identify required current state;
- source-of-truth files conflict and cannot be resolved;
- a protected file must change;
- required prior chapter files are missing;
- the chapter depends on an unconfirmed idea as if it were canon;
- `planning/active_flow.yml` is missing or stale;
- `planning/rolling_plan.yml` is too thin to drive prose.
- planning files still contain stale old-format fields that encourage chapter containers: `bridge_to_next`, `continuity_from_previous`, `next_hook`, `结尾方向`, `情绪节奏`, `本轮需要`.

Stop before finalizing if:

- the draft reads like an expanded outline or task report;
- the chapter behaves as an independent container;
- the ending is mainly internal reflection, analysis, or next-step planning;
- the ending lacks a concrete next-chapter pickup;
- no external state changes;
- ordinary body paragraphs are separated by blank lines;
- the chapter has too few body paragraphs or contains giant paragraphs that should be split;
- `scripts/validate_novel_output.py` reports failure;
- `draft.txt`, `review.md`, `summary.yml`, or `canon_delta.yml` is missing;
- current state files, `active_flow.yml`, or `rolling_plan.yml` are stale after writing.
