# Novel Project Template

This directory is the blank project template for AI Novel Agent.

Usage:

1. Copy the whole `templates/project/` directory to `projects/<project-id>/`.
2. Use `novel-bootstrap` to initialize project memory from the user seed.
3. Treat project files as the long-term memory and agent conversations as temporary workspaces.
4. Fill `meta/model_policy.yml` with the actual model roles when model routing is used.

Core rules:

- Chapter canon lives in `chapters/*/final.txt`.
- Current state lives in `entities/`, `ledgers/`, and `planning/`.
- Whole-book scale lives in `book/longform_blueprint.yml`; it is protected.
- Current continuous story motion lives in `planning/active_flow.yml`.
- Current volume/stage story architecture lives in `planning/story_architecture.yml`.
- Active side threads, off-screen actions, and conflict network live in `planning/thread_board.yml`.
- Near-future detailed synopsis lives in `planning/rolling_plan.yml`.
- Story development packs live in `planning/development_packs/` and are recommendation snapshots, not canon by themselves.
- Completed chapter plans move to `planning/completed_plan_log.yml`.
- Completed thread lifecycles move to `planning/completed_threads_log.yml`.
- Distant future ideas live in `planning/future_backlog.yml`.
- `planning/current_round.yml` is only a production-batch tracker, not a story unit or second chapter plan.
- `canon_delta.yml` is a chapter change log, not the current-state table.
- A `writing_packet.md` must be generated before chapter prose drafting.
- Writing packets must include `Longform Scale Check`, `Pre-Draft Self Check`, and a concise design/execution `Writing Card`.
- `meta/model_policy.yml` decides which tasks may use a fast model and which require a premium model or human confirmation.
- TXT prose uses one blank line after the title and no blank lines between ordinary body paragraphs, while still keeping normal paragraphing.

Long-form scale rule:

- `book/longform_blueprint.yml` defines target length, macro stages, scale map, power pacing, opportunity cadence, and reveal windows.
- `novel-write` must read it before planning or drafting.
- Do not silently shrink a world into a city, accelerate protagonist progression, or reveal future-stage secrets.
- Changes to target length, macro structure, scale map, power pacing, or secret pacing should go through `novel-change`.
