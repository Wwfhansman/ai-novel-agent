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

## Review Modes

### Cold-Start Review

Act as a fresh agent. Read only project files, not prior conversation. Verify that the project explains:

- What the book is.
- Current volume goal and stage.
- Current protagonist and major character goals.
- Active narrative debts.
- Knowledge state and secrets.
- World state and pressures.
- Next round writing target.

### Chapter Review

Review a specific chapter:

- `context_pack.md`
- `outline.md`
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

Check whether the round produced coherent progress.

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

4. **Character intent**
   - Check whether each important character acted from current goals, not just plot convenience.

5. **Knowledge visibility**
   - Check whether any character knows something they should not.
   - Check whether secrets were revealed too early.

6. **World state**
   - Check whether factions, resources, crises, and public pressure reacted to recent chapters.

7. **Style and genre alignment**
   - Compare to `book/constitution.md`, `book/reader_model.yml`, and `book/style_memory.md`.

## Output Format

Produce:

```text
Review Summary
- Overall status: pass / pass with risks / fail
- Biggest risks
- Required fixes
- Suggested fixes
- Files that appear stale or conflicting
- Whether novel-change is needed
```

## Failure Handling

If the project cannot be continued safely:

- Do not rewrite正文.
- List blocking missing files or contradictions.
- Recommend `novel-change` for structural changes.
- Recommend context pack regeneration if the writing input record is incomplete.

