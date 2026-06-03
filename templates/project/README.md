# Novel Project Template

This directory is the blank project template for AI Novel Agent (engine model).

## Usage

1. Copy `templates/project/` to `projects/<project-id>/`.
2. Use `novel-bootstrap` to generate the story DNA (constitution, blueprint,
   initial entities/ledgers, first rolling_plan) from the user seed.
3. Seed the engine: `python -m novel_engine init projects/<project-id>`
   (writes `events/bootstrap.yml` from the initial entities/ledgers).
4. Verify: `python -m novel_engine check projects/<project-id>`.
5. Write each chapter with `novel-engine-write`:
   `kit → 逐场写 → final.txt → events/chNNN.yml → check → commit`.

## Core rules (engine model)

- **`events/` is canon** — an append-only event log. `events/chXXX.yml` records
  the canon changes a chapter causes (typed events; `note` for non-mechanical).
- **`entities/` and `ledgers/` are derived** — `commit` projects them from
  `events/`. Do **not** hand-edit them; changes are overwritten.
- Chapter prose canon lives in `chapters/*/final.txt`.
- Whole-book scale lives in `book/longform_blueprint.yml` (protected).
- Current-volume architecture / pacing lives in `planning/story_architecture.yml`;
  near-future detailed synopsis lives in `planning/rolling_plan.yml`
  (maintained by `novel-architect`).
- Story development packs live in `planning/development_packs/` (recommendation
  snapshots, not canon).
- `meta/model_policy.yml` decides which tasks may use a fast model vs a premium
  model or human confirmation.
- TXT prose: one blank line after the title, no blank lines between ordinary
  body paragraphs (still paragraphed). Checked by `python -m novel_engine txt`.

## Long-form scale rule

- `book/longform_blueprint.yml` defines target length, macro stages, scale map,
  power pacing, opportunity cadence, and reveal windows.
- `novel-engine-write` and `novel-architect` must read it before planning/drafting.
- Do not silently shrink a world into a city, accelerate protagonist progression,
  or reveal future-stage secrets.
- Changes to target length, macro structure, scale map, power pacing, or secret
  pacing go through `novel-change`.

See `docs/ENGINE.md` and `docs/ENGINE_WORKFLOW.md` for the full engine model.
