---
name: novel-write
description: Continue an existing AI Novel Agent project by writing the next chapter or next three-chapter round. Use for daily novel production, chapter drafting, round planning, context pack generation, chapter review, canon delta creation, and memory updates.
---

# Novel Write

Use this skill for normal production writing. Default unit: one round of 3 chapters. Each chapter must independently compile context, plan, draft, review, finalize, and update memory.

## Hard Rule

Never write正文 before generating context packs:

```text
planning/context_packs/round_XXX_context_pack.md
chapters/chXXX/context_pack.md
```

The context pack is the visible record of what you read, why you read it, what you understood, what remains uncertain, and what must be updated after writing.

## Read First

Read:

- `docs/CONTEXT_PACK.md`
- `docs/CANON_AND_SAFETY.md`
- `docs/WORKFLOWS.md`
- `docs/MEMORY_MODEL.md`
- Current project `project.yml`

## Round Workflow

1. **Establish checkpoint**
   - If Git is available and the project tracks real content, create or recommend a checkpoint before the round.

2. **Compile round context**
   - Read the required files from `docs/CONTEXT_PACK.md`.
   - Read recent 12-15 chapter summaries and recent 3-5 chapter `final.txt` files when available.
   -回看 key old chapter原文 when伏笔、叙事债、重大关系、旧道具、旧台词, or user-specified old content is relevant.
   - Write `planning/context_packs/round_XXX_context_pack.md`.

3. **Plan the round**
   - Update or create `planning/current_round.yml`.
   - Plan exactly 3 chapters unless the user asks for a smaller scope.

4. **For each chapter**
   - Create or update `chapters/chXXX/brief.md`.
   - Write `chapters/chXXX/context_pack.md`.
   - Create `outline.md` scene beats.
   - Draft `draft.txt`.
   - Review the draft.
   - Write confirmed text to `final.txt` only after review.
   - Generate `summary.yml` and `canon_delta.yml`.
   - Merge current state into `entities/`, `ledgers/`, `volumes/`, and `planning/`.

5. **End round**
   - Update current volume summary/state and active arc.
   - Evaluate idea pool and narrative debts.
   - Adjust `planning/rolling_plan.yml`.
   - Record a session summary in `meta/session_log.md`.

## Current-State Rules

- `final.txt` is chapter canon text.
- `summary.yml` says what happened in that chapter.
- `canon_delta.yml` says what changed in that chapter.
- Current character state is in `entities/characters.yml`.
- Current world state is in `ledgers/world_state.yml`.
- Current knowledge state is in `ledgers/knowledge_state.yml`.
- Current future plan is in `planning/rolling_plan.yml`.

Do not treat old `canon_delta.yml` files as current state.

## Do Not Silently Modify

Route to `novel-change` if writing would:

- Modify creative constitution.
- Change protagonist core desire.
- Kill or permanently remove a major character.
- Reveal an endgame-level secret.
- Change the current volume goal.
- Promote a major idea into mainline canon.
- Perform large retcon.

## Review Checklist

Before finalizing each chapter, check:

- Clear event and conflict.
- Protagonist acts, not just reacts.
- Target reader receives progress or pressure.
- Narrative debts are added, advanced, paid, or intentionally delayed.
- Character behavior follows current intent.
- Knowledge visibility is correct.
- World state reacts to actions.
- Foreshadowing is not leaked too early.
- Ending has next-chapter pull.

## Failure Handling

Stop before正文 if:

- Context pack cannot identify required current state.
- Source-of-truth files conflict and cannot be resolved by `docs/CANON_AND_SAFETY.md`.
- A protected file must change.
- Required prior chapter files are missing.
- The chapter would depend on an unconfirmed idea as if it were canon.

