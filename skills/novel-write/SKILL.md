---
name: novel-write
description: Continue an existing AI Novel Agent project by writing the next chapter or next three-chapter round. Use for daily novel production, detailed rolling synopsis updates, context pack generation, prose drafting, chapter review, canon delta creation, and memory updates.
---

# Novel Write

Use this skill for normal production writing. Default unit: one round of 3 chapters.

The writing source is the **detailed rolling synopsis** in `planning/rolling_plan.yml`. The prose should grow from story content, continuity, characters, pressure, and scene imagination, not from a fixed intra-chapter template.

## Core Shift

- Planning may be structured.
- Prose drafting must be free, continuous, and fiction-first.
- `rolling_plan.yml` is the authority for the next 6-15 chapters.
- `current_round.yml` is only a 3-chapter extract from `rolling_plan.yml`.
- `outline.md` is optional scratch. It is not required and must not become scene-beat scaffolding.
- Review is diagnostic after drafting; it must not become a template that shapes every paragraph.

## Hard Rules

- Never write `draft.txt` or `final.txt` before generating:
  - `planning/context_packs/round_XXX_context_pack.md`
  - `chapters/chXXX/context_pack.md`
- Do not translate a plan, synopsis, outline, or checklist directly into prose.
- A chapter fails if it reads like a report of tasks completed.
- A chapter fails if the last section is mainly the protagonist summarizing lessons, analyzing the situation, or thinking about the next step.
- Do not use docs, schemas, templates, examples, sample novels, or other projects as creative source material. They are process references only.
- Do not silently change protected canon. Route major changes to `novel-change`.

## Read First

Read:

- `docs/CONTEXT_PACK.md`
- `docs/CANON_AND_SAFETY.md`
- `docs/MEMORY_MODEL.md`
- `docs/FILE_FORMATS.md`
- Current project `project.yml`
- `book/constitution.md`
- `book/reader_model.yml`
- `book/style_memory.md`
- `style/rewrite_rules.md`
- `planning/rolling_plan.yml`
- `planning/current_round.yml` if it exists

## Source Of Truth

- `final.txt` is chapter canon text.
- `summary.yml` records what happened in that chapter.
- `canon_delta.yml` records what changed in that chapter. It is a change log, not current state.
- Current character state lives in `entities/characters.yml`.
- Current world state lives in `ledgers/world_state.yml`.
- Current knowledge visibility lives in `ledgers/knowledge_state.yml`.
- Future 6-15 chapter synopsis lives in `planning/rolling_plan.yml`.
- Current round extract lives in `planning/current_round.yml`.

When files conflict, follow `docs/CANON_AND_SAFETY.md`. Do not merge contradictions casually.

## Rolling Synopsis Requirements

Before each round, ensure `planning/rolling_plan.yml` contains a detailed 6-12 chapter forward window.

Each planned chapter should include:

- chapter id and provisional title;
- status;
- 300-800 Chinese characters of story synopsis;
- continuity from previous chapter;
- required plot developments;
- important characters and what they want;
- pressure, obstacle, or complication;
- expected payoff, reveal, or reader reward;
- bridge to the next chapter;
- forbidden moves or canon constraints.

This is not an intra-chapter structure. It describes what story content should happen, not how the chapter must be arranged.

If the rolling synopsis is too thin, expand it before drafting. Do not compensate for a thin synopsis by inventing a rigid `outline.md`.

## Round Workflow

1. **Establish checkpoint**
   - If Git is available and the project tracks real content, create or recommend a checkpoint before the round.

2. **Refresh detailed rolling synopsis**
   - Read current canon and planning files.
   - Update `planning/rolling_plan.yml` so the next 6-12 chapters are coherent and detailed enough to drive prose.
   - Remove chapters already completed or mark them completed; do not leave future chapters repeating decisions already made.

3. **Compile round context**
   - Read the default files from `docs/CONTEXT_PACK.md`.
   - Read recent 12-15 chapter summaries when available.
   - Read recent 3-5 chapter `final.txt` files when available.
   - Read key old chapter originals when old foreshadowing, debts, objects, relationships, rules, or lines become relevant.
   - Write `planning/context_packs/round_XXX_context_pack.md`.

4. **Create current round extract**
   - Plan exactly 3 chapters unless the user asks otherwise.
   - Copy or condense each chapter from `planning/rolling_plan.yml`.
   - Do not invent a separate competing plan.
   - Write `planning/current_round.yml`.

5. **Write each chapter**
   - Create or update `chapters/chXXX/brief.md` from the detailed synopsis and immediate continuity.
   - Generate `chapters/chXXX/context_pack.md`.
   - Optionally write `outline.md` only as freeform notes if useful. Do not make it a required scene-beat checklist.
   - Draft `draft.txt` as novel prose.
   - Revise for continuity, concreteness, anti-reporting, and ending behavior.
   - Write confirmed text to `final.txt`.
   - Write `review.md`, `summary.yml`, and `canon_delta.yml`.
   - Merge current state into `entities/`, `ledgers/`, `volumes/`, and `planning/`.

6. **End round**
   - Update current volume summary/state and active arc.
   - Evaluate idea pool and narrative debts.
   - Refresh `planning/rolling_plan.yml` so the next round does not repeat completed choices.
   - Record a session summary in `meta/session_log.md`.

## Drafting Guidance

During prose drafting, focus on **what is happening now**, not on proving that the plan was followed.

Good drafting behavior:

- enter through a concrete moment, pressure, action, dialogue, object, or consequence;
- let characters pursue wants in the scene instead of explaining their roles;
- let exposition surface because someone needs, hides, misreads, trades, or weaponizes information;
- allow small local inventions if they serve the chapter and do not break canon;
- make the chapter feel like it continues from the prior chapter's pressure, not like a new independent task card;
- let the ending land in the world: a cost, arrival, exposed fact, changed relationship, action already underway, or pressure that naturally continues.

Avoid:

- ending with a neat protagonist recap;
- numbered lessons in prose such as "first, second, third" unless the character is literally writing a document;
- default openings like "the next day" when time passage is not the drama;
- paragraphs that only restate the plan;
- repetitive "arrive -> observe -> analyze -> arrange -> think" chapters;
- forcing every chapter to have the same internal rhythm.

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

## Review Checklist

Before writing `final.txt`, create or update `review.md`.

The review must be diagnostic, not self-praise. It must name at least one weakness or risk and say whether it was fixed.

Check:

- Does the chapter follow the detailed synopsis without sounding like a synopsis?
- Does it continue naturally from the previous chapter?
- Does it contain concrete fictional material, not only explanation and planning?
- Did the protagonist or another character make a choice, pay a cost, gain leverage, lose something, expose something, or change a relationship?
- Is there enough reader reward for the genre and current debt window?
- Does the ending avoid recap/thought-summary behavior?
- Are body paragraphs single-spaced in TXT format?
- Are `summary.yml`, `canon_delta.yml`, and current state files updated?
- Did `rolling_plan.yml` change so future chapters do not repeat already-completed decisions?

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

- context packs cannot identify required current state;
- source-of-truth files conflict and cannot be resolved;
- a protected file must change;
- required prior chapter files are missing;
- the chapter depends on an unconfirmed idea as if it were canon;
- `planning/rolling_plan.yml` is too thin to drive prose.

Stop before finalizing if:

- the draft reads like an expanded outline or task report;
- the ending is mainly internal reflection, analysis, or next-step planning;
- no external state changes;
- ordinary body paragraphs are separated by blank lines;
- `review.md`, `summary.yml`, or `canon_delta.yml` is missing;
- current state files or `rolling_plan.yml` are stale after writing.
