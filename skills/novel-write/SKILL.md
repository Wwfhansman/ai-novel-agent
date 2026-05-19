---
name: novel-write
description: Continue an existing AI Novel Agent project by writing the next chapter or next three-chapter round. Use for daily novel production, context pack generation, attention-driven chapter drafting, chapter review, canon delta creation, and memory updates.
---

# Novel Write

Use this skill for normal production writing. Default unit: one round of 3 chapters.

This skill has two layers:

1. **Memory Backend**: read files, compile context packs, protect canon, update summaries and ledgers.
2. **Creative Frontend**: write chapters as living fiction, not as expanded outlines or event reports.

The backend may be structured. The frontend must preserve freedom, scene life, character intent, reader curiosity, and local surprise.

## Hard Rules

- Never write `draft.txt` or `final.txt` before generating:
  - `planning/context_packs/round_XXX_context_pack.md`
  - `chapters/chXXX/context_pack.md`
- Do not translate `outline.md` directly into prose. The outline gives direction; the chapter must find a scene.
- A chapter fails if it can be reduced to: "the protagonist arrives, observes a problem, analyzes it, makes an arrangement, then thinks about the future."
- Do not use docs, schemas, templates, examples, or other projects as creative source material. They are process references only.
- Do not silently change protected canon. Route major changes to `novel-change`.

## Read First

Read:

- `docs/CONTEXT_PACK.md`
- `docs/CANON_AND_SAFETY.md`
- `docs/MEMORY_MODEL.md`
- Current project `project.yml`
- `book/constitution.md`
- `book/reader_model.yml`
- `book/style_memory.md`
- `style/rewrite_rules.md`
- `planning/chapter_shape_history.yml` if it exists

## Source Of Truth

- `final.txt` is chapter canon text.
- `summary.yml` records what happened in that chapter.
- `canon_delta.yml` records what changed in that chapter. It is a change log, not current state.
- Current character state lives in `entities/characters.yml`.
- Current world state lives in `ledgers/world_state.yml`.
- Current knowledge visibility lives in `ledgers/knowledge_state.yml`.
- Current future plan lives in `planning/rolling_plan.yml`.

When files conflict, follow `docs/CANON_AND_SAFETY.md`. Do not merge contradictions casually.

## Round Workflow

1. **Establish checkpoint**
   - If Git is available and the project tracks real content, create or recommend a checkpoint before the round.

2. **Compile round context**
   - Read the default files from `docs/CONTEXT_PACK.md`.
   - Read recent 12-15 chapter summaries when available.
   - Read recent 3-5 chapter `final.txt` files when available.
   - Read key old chapter originals when an old foreshadowing, debt, object, relationship, rule, line, or scene becomes relevant.
   - Write `planning/context_packs/round_XXX_context_pack.md`.

3. **Plan the round**
   - Plan exactly 3 chapters unless the user asks otherwise.
   - For each chapter, identify a different attention source and chapter shape.
   - Update or create `planning/current_round.yml`.

4. **Write each chapter independently**
   - Create or update `chapters/chXXX/brief.md`.
   - Generate `chapters/chXXX/context_pack.md`.
   - Design the chapter's attention engine before writing prose.
   - Draft `draft.txt`.
   - Review and revise until the chapter no longer reads like a container.
   - Write confirmed text to `final.txt`.
   - Write `review.md`, `summary.yml`, and `canon_delta.yml`.
   - Merge current state into `entities/`, `ledgers/`, `volumes/`, and `planning/`.
   - Append the chapter shape to `planning/chapter_shape_history.yml` if the file exists; create it if useful.

5. **End round**
   - Update current volume summary/state and active arc.
   - Evaluate idea pool and narrative debts.
   - Adjust `planning/rolling_plan.yml`.
   - Record a session summary in `meta/session_log.md`.

## Chapter Creative Frontend

Before drafting, write the following into the chapter context pack.

### 1. Attention Source

Choose the force that keeps the reader reading. Examples:

- unknown object, abnormal event, large-scale wonder, or hidden rule;
- immediate danger, time pressure, public embarrassment, or social pressure;
- character conflict, incompatible desire, negotiation, deception, or test;
- resource movement, debt movement, relationship movement, status movement;
- irony, contradiction, dark humor, mistaken understanding, or rule reversal;
- emotional rupture, shame, longing, fear, resentment, loyalty, or temptation.

Do not choose a generic task such as "advance the plot" or "explain the plan."

### 2. Reader Question Curve

State how the reader's active question changes during the chapter:

```text
opening question -> middle question -> late question -> next-chapter pull
```

If the question does not change, the chapter is probably flat.

### 3. Entry Method

Do not default to time reset openings such as "the next day." Enter through one of:

- a visible abnormal detail;
- a line of dialogue with pressure behind it;
- a consequence already in motion;
- a character doing something specific;
- a social, material, or physical disturbance;
- a quiet but loaded image.

Use a time opening only when the passage of time is itself dramatic.

### 4. Scene Growth

Let the scene grow from concrete pressure, not from explanation.

- Introduce setting through what obstructs, tempts, exposes, or costs someone.
- Let characters reveal intent through choices, omissions, gestures, bargains, and refusals.
- Let information appear because someone needs it, hides it, misreads it, pays for it, or weaponizes it.
- Allow small local inventions: a minor character, object, misunderstanding, rumor, obstacle, or sensory detail may appear if it serves the current scene and does not break canon.

Local inventions must be handled after writing:

- canon-relevant: add to `canon_delta.yml` and current state files;
- reusable but not confirmed: add to `ledgers/idea_pool.yml` or `ledgers/foreshadowing.yml`;
- one-scene color only: mention in `review.md` as disposable scene texture.

### 5. State Delta

Every chapter must change at least one external state:

- relationship;
- resource;
- knowledge visibility;
- debt or promise;
- location control;
- reputation;
- danger level;
- faction move;
- physical condition;
- plan feasibility.

Internal realization alone is not enough.

## Drafting Principles

- Write from scene pressure, not from a task list.
- Prefer specific action over abstract explanation.
- Prefer character intent over author summary.
- Keep strategy visible through execution, argument, resource trade, failed attempt, or consequence.
- Use short paragraphs only when they create turn, pause, impact, contrast, humor, threat, or emotional pressure.
- Vary paragraph length naturally. Do not make every sentence its own paragraph by habit.
- Let dialogue carry desire, concealment, status, and conflict. Do not use dialogue only to deliver exposition.
- Avoid repeated chapter endings where the protagonist sits, thinks, understands, decides, or looks into the distance.
- End outward: an action begins, someone arrives, a fact is exposed, a cost lands, a promise is made, a rule changes, or pressure moves to the next chapter.

## Chapter Shape Diversity

Across one round, adjacent chapters should not share the same shape.

Track:

- opening type;
- dominant attention source;
- main conflict mode;
- exposition mode;
- ending hook type;
- primary state delta.

If two adjacent chapters have the same shape, revise one before finalizing.

## Review Checklist

Before writing `final.txt`, create or update `review.md` and answer:

- What is this chapter's attention source?
- How did the reader question change from opening to ending?
- What concrete state changed?
- Which scene would be boring if summarized? Did the draft dramatize it instead?
- Does any paragraph exist only because the outline needed a beat? If yes, rewrite it as scene or cut it.
- Are short paragraphs functional, or just AI rhythm?
- Does the protagonist act, bargain, risk, refuse, lose, gain, or expose something?
- Did another character or the world push back?
- Is information visibility correct?
- Are narrative debts added, advanced, paid, or intentionally delayed?
- Does the ending push outward rather than collapse into thought?
- Is the chapter shape different from adjacent chapters?

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
- `planning/chapter_shape_history.yml`
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
- the chapter has no attention source beyond "advance plot."

Stop before finalizing if:

- the draft reads like an expanded outline;
- the chapter is mostly arrival, observation, analysis, arrangement, and thought;
- no external state changes;
- adjacent chapters share the same opening, middle, and ending pattern;
- the ending is only internal reflection;
- `review.md`, `summary.yml`, or `canon_delta.yml` is missing.
