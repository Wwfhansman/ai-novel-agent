---
name: novel-change
description: Manage mid-story changes in an AI Novel Agent project. Use when the user wants to add an idea, alter a setting, change a character or relationship, adjust an outline, promote an idea, resolve canon conflicts, or perform a reboot-level change.
---

# Novel Change

Use this skill for changes after bootstrap. Do not default to rebooting the novel. Most changes should be evaluated, scoped, and integrated into existing memory.

## Read First

Read:

- `docs/CANON_AND_SAFETY.md`
- `docs/MEMORY_MODEL.md`
- `docs/WORKFLOWS.md`
- Target project `project.yml`
- `meta/model_policy.yml` if present
- Relevant current-state files.

## Change Levels

Classify every change first:

```text
Level 1: Style or expression change
Level 2: Local setting, item, location, or rule change
Level 3: Character, relationship, or intention change
Level 4: Main thread, current volume, or rolling plan change
Level 5: Work DNA change requiring reboot-level handling
```

Only Level 5, or explicit user request, should route to `novel-bootstrap`.

## Workflow

1. **Restate the requested change**
   - Identify exact user intent.
   - Identify whether it is canon, proposal, or idea.

2. **Classify impact**
   - Assign Level 1-5.
   - Identify affected files and protected files.

3. **Read relevant canon**
   - Read current authoritative state files.
   - Read related chapters if the change touches existing正文.
   - Do not rely only on summaries for retcon-sensitive changes.

4. **Assess compatibility**
   - Check creative constitution.
   - Check reader model.
   - Check current volume goal.
   - Check character intent and knowledge state.
   - Check narrative debt and foreshadowing effects.

5. **Propose integration**
   - Offer one recommended path and alternatives when useful.
   - Decide whether to write to `idea_pool`, `foreshadowing`, `planning`, `entities`, or protected files.

6. **Apply only safe changes**
   - For protected files, output a diff summary and require checkpoint/confirmation before modification.
   - For Level 3-5 changes, require premium_model or human confirmation according to `meta/model_policy.yml` if present.
   - For ordinary changes, update authoritative files and record the decision.

7. **Record decision**
   - Update `ledgers/decision_log.yml` or `meta/session_log.md`.
   - If not applying immediately, write the idea to `ledgers/idea_pool.yml`.

## Safe Destinations

- New uncertain idea: `ledgers/idea_pool.yml`
- Potential future payoff: `ledgers/foreshadowing.yml`
- Current character state: `entities/characters.yml`
- Current information visibility: `ledgers/knowledge_state.yml`
- Current world reaction: `ledgers/world_state.yml`
- Current cross-round flow: `planning/active_flow.yml`
- Future 9-15 chapter route: `planning/rolling_plan.yml`
- Whole-book scale, macro stages, power pacing, and reveal windows: `book/longform_blueprint.yml` (protected)
- Current volume goal: protected; modify only with explicit change process.

## Diff Summary for Protected Changes

Before protected edits, produce:

```text
Change Summary
- Modification reason
- Affected files
- Old state
- New state
- Impact scope
- Required setup or rewrites
- Whether user confirmation is required
```

## Failure Handling

Stop and ask for direction if:

- The change contradicts the creative constitution and the user did not request a reboot.
- Multiple existing chapters would need retcon and the user has not approved it.
- A protected file must change without checkpoint.
- The change promotes an unconfirmed idea into canon without enough setup.
