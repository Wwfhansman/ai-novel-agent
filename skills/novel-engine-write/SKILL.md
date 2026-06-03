---
name: novel-engine-write
description: Produce the next chapter of a novel project on the novel_engine backbone — scene-level prose driven by an engine-resolved entering-state, with canon stored as events and derived state, gated by check/commit. This is the default writing flow. For a brand-new book, run novel-bootstrap then `novel_engine init` first; for an old project still on hand-written canon_delta, run `novel_engine migrate` first.
---

# Novel Engine Write

Produce one chapter on the `novel_engine` backbone. State is **derived from events**, prose is written **scene by scene** from an engine-resolved entering-state, and the chapter is gated by `check` / `commit`. This is the default writing flow.

Full design: `docs/ENGINE.md` and `docs/ENGINE_WORKFLOW.md`.

## When to use

- The project has an `events/` directory (already migrated), or you are willing to migrate it first.
- You want scene-level prose (validated to read better than chapter-level) plus drift-proof state.

If the project is still legacy (hand-written `canon_delta.yml`, no `events/`), run `python -m novel_engine migrate <project>` first to bring it onto the engine.

## The loop (one chapter)

```
1. 套件     python -m novel_engine kit <project> --chapter chNNN
            → chapters/chNNN/_kit/  (scene_prompts.md, stitch_prompt.md, events.template.yml, PRODUCE.md)
2. 写       按 scene_prompts.md 逐场写正文（经历优先；one_change 小、可空；出口切外部动作）
3. 缝合     按 stitch_prompt.md 连成整章 → chapters/chNNN/final.txt
4. 自检     python -m novel_engine txt chapters/chNNN/final.txt
            python -m novel_engine patterns chapters/chNNN/final.txt
5. 事件     按 events.template.yml 把本章 canon 变化写进 events/chNNN.yml
6. 门禁     python -m novel_engine check <project>   # schema+完整性+健康+结构
7. 提交     python -m novel_engine commit <project>  # 通过则物化派生 entities/ledgers
```

## Hard rules

- Do not hand-edit `entities/` or `ledgers/` on a migrated project — they are **derived** (`commit` overwrites them). Record canon changes only as events.
- `events/chNNN.yml` must pass `check` (schema + referential/temporal integrity). Fix errors before `commit`; warnings are advisory.
- Mechanical canon changes use typed events; non-mechanical narrative changes use `kind: note`. Vocabulary: `novel_engine/schemas/event.schema.json`.
- A scene is an **experience unit, not a task unit**: write the sensory/emotional/weave material first; `one_change` is small and may be empty. Cut on external motion, never on "objective achieved".
- New information enters via `enters_via`, never as protagonist brain-summary.
- The chapter's entering-state comes from the engine (`context` / the kit) — do not contradict it. To know where things stand, read the kit's entering-state summary, not 300 chapters.
- Protected changes (constitution, blueprint, killing a major character, endgame secrets, volume goal) still route to `novel-change`.

## Quality

- If `style/exemplars.yml` exists, the kit injects voice exemplars per scene; otherwise run `python -m novel_engine exemplars-init <project>` and tag your best passages by scene type.
- A finished chapter should beat the chapter-level method on: lived-in texture, rhythm (not uniform advancement), information experienced not explained, external-motion ending. Use `python -m novel_engine compare A B` to check voice drift against an established chapter.

## Boundaries

- The engine handles bookkeeping: state projection, continuity, gates, metrics. It does not write prose or judge whether prose is good — that stays the writer (LLM) and the human.
- Run `structure` and `health` periodically (not every chapter) to catch read-pull / anti-shrink / overdue-payoff problems early.
