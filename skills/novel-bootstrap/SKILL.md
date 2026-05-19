---
name: novel-bootstrap
description: Initialize a new AI Novel Agent project from a seed idea. Use when a novel project is empty, the user explicitly asks to start a new novel, or the user explicitly requests a full reboot/rebuild of the book premise, protagonist, world, or core creative constitution.
---

# Novel Bootstrap

Use this skill to create a new novel project from a seed. Do not use it for ordinary mid-story ideas, local setting changes, character adjustments, or current-volume revisions; use `novel-change` for those.

## Required Inputs

- User seed: premise, setting, protagonist image, genre, opening scene, or desired payoff.
- Target project path under `projects/<project-id>/`.
- Empty or template-based project directory.

If the target project already has canon chapters, stop and route to `novel-change` unless the user explicitly requested a reboot.

## Read First

Read:

- `templates/project/README.md`
- `docs/MEMORY_MODEL.md`
- `docs/CANON_AND_SAFETY.md`
- `docs/FILE_FORMATS.md`

Use `templates/project/` as the required output structure.

## Workflow

1. **Assess the seed**
   - Extract genre, protagonist, core conflict, reader payoff, and long-form potential.
   - If the seed is underspecified, generate 3-5 viable directions and recommend one.

2. **Create the creative constitution**
   - Write `book/constitution.md`.
   - Include genre, core selling point, protagonist long-term desire, reader promises, forbidden moves, and protected boundaries.

3. **Initialize book-level memory**
   - Write `book/global_summary.md` as the initial book state.
   - Write `book/reader_model.yml`.
   - Write `book/style_memory.md`.
   - Write `book/endgame_hypotheses.yml` as hypotheses, not canon.

4. **Initialize volume 001**
   - Write `volumes/vol_001/volume_outline.md`.
   - Write `volume_summary.md`, `volume_state.yml`, `volume_threads.yml`, and `volume_debts.yml`.
   - Keep the current volume clear; do not pretend the whole multi-million-word story is fixed.

5. **Initialize entities and ledgers**
   - Create protagonist and initial important entities in `entities/`.
   - Create empty or initial entries in `ledgers/`.
   - Keep `idea_pool.yml` separate from canon.

6. **Initialize planning**
   - Write `planning/rolling_plan.yml` with a 9-15 chapter window.
   - Write `planning/current_round.yml` for round 001.
   - Do not write正文 yet unless the user explicitly asks to continue with `novel-write`.

7. **Write meta state**
   - Update `project.yml` and `meta/project_state.yml`.
   - Record bootstrap decisions in `ledgers/decision_log.yml` or `meta/session_log.md`.

## Output Requirements

After bootstrapping, the project must let a fresh agent answer:

- What is this book?
- What does the target reader expect?
- Who is the protagonist and what do they want?
- What is volume 001 trying to accomplish?
- What are the next 9-15 chapters likely doing?
- Which files are protected from silent edits?

## Protected Files

You may create protected files during bootstrap. After bootstrap, do not silently modify:

- `book/constitution.md`
- `book/reader_model.yml`
- `book/style_memory.md` core rules
- `volumes/vol_001/volume_outline.md` volume goal
- protagonist core desire and line-not-cross in `entities/characters.yml`
- endgame-level secrets in `ledgers/knowledge_state.yml`

## Failure Handling

Stop and ask for direction if:

- The target project already contains confirmed chapters and the user did not ask for reboot.
- The seed implies mutually incompatible genres or reader promises.
- Required template files are missing.
- You cannot determine whether to overwrite existing canon.

