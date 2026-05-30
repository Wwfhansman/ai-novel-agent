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

Use these planning layers:

- `book/longform_blueprint.yml`: protected whole-book scale, macro stage, progression budget, and reveal pacing authority.
- `planning/story_architecture.yml`: current volume/stage story architecture, pacing/growth/information-release operating plan.
- `planning/thread_board.yml`: active side-thread lifecycle, off-screen actions, and conflict-network board.
- `planning/active_flow.yml`: current continuous story pressure and latest actual handoff; may span rounds.
- `planning/rolling_plan.yml`: detailed 6-15 chapter future window; completed entries move to `completed_plan_log.yml`, distant entries to `future_backlog.yml`.
- `planning/current_round.yml`: lightweight production tracker only; never a second chapter plan.

## Hard Rules

- Never write `draft.txt` before generating:
  - `planning/context_packs/round_XXX_context_pack.md`
  - `chapters/chXXX/writing_packet.md`
- Never promote `draft.txt` into `final.txt` before completing draft self-check and `chapters/chXXX/reader_pass.md`.
- `reader_pass.md` should be produced by an independent cold-reader subagent whenever the environment supports subagents. Same-agent cold reading is a fallback, not the default.
- `planning/active_flow.yml`, `planning/rolling_plan.yml`, and `planning/current_round.yml` must be valid YAML before drafting.
- Do not translate a plan, synopsis, outline, or checklist directly into prose.
- Do not treat one chapter or one round as a complete narrative box.
- `writing_packet.md` must separate `Chapter Design` from `Writing Execution`: design fields say what changes; execution fields give sensory openings, scene moments, and ending gesture.
- Every Writing Card must include `time_span`, `ending_type`, and `position_in_flow`. Consecutive chapters must not default to one-day tasks ending in next-step decisions.
- Every core information release must state `enters_via`; if the only path is protagonist brain-summary or narrator explanation, redesign the scene before drafting.
- Background is a first-class writing asset. Any person, faction, place, item, institution, rule, historical cause, resource, technique, public rumor, or relationship network that affects action, dialogue, conflict, movement, identity, cost, or reader expectation must exist in `entities/` or `ledgers/` before drafting.
- Writer may add local sensory texture and harmless incidental details, but must not invent named factions, locations, major roles, institutional rules, power costs, historical grievances, resource sources, or recurring objects during prose drafting.
- Round boundaries are production boundaries, not story boundaries. Do not make ch003/ch006/ch009 feel like cleanup, recap, reset, or phase closure unless `planning/active_flow.yml` and `planning/rolling_plan.yml` explicitly say the story has earned payoff.
- 如果上一章的 `canon_delta.yml` 中有 `actual_handoff`，本章开头必须承接，除非在 `writing_packet.md` 和 review 中记录了有理有据的切换理由。
- 承接后，在本章的 `writing_packet.md` 和 `planning/rolling_plan.yml` 条目中体现该交接。
- Do not use docs, schemas, templates, examples, sample novels, or other projects as creative source material. They are process references only.
- Do not silently change protected canon. Route major changes to `novel-change`.
- Before accepting any `final.txt`, complete `reader_pass.md` and run `python scripts/validate_novel_output.py <project> --chapters chXXX` from the repository root when the script exists. If either quality gate blocks or validation fails, fix the listed issues and rerun. Do not call the chapter complete until both pass.
- Read `planning/rolling_plan.yml` in full before each round. It is the future-planning authority.
- Do not copy full project files or the full rolling plan into round context packs or writing packets. They are working memory, not a duplicated database.
- Follow `meta/model_policy.yml` when it exists. A fast or cheap model may assist mechanical tasks, but final prose, active_flow, rolling_plan, canon merges, and protected-file decisions must be confirmed by a premium model or human.
- Key `writing_packet.md` claims must include source refs. Do not rely on "I remember reading it."
- Read `book/longform_blueprint.yml` before refreshing planning and before drafting. Treat it as protected. If it is missing, create a stop/fix task instead of guessing long-form scale.
- Every round context pack and chapter writing packet must include a `Longform Scale Check`.
- If `style/samples.md` contains real project style guidance, treat it as a positive prose anchor, not an optional appendix. Extract 3-5 chapter-specific style anchors into each `writing_packet.md` Writing Card, and ask the cold reader/review to check sample alignment.
- Do not silently change target length, macro stages, world scale, faction scale, power pacing, or secret reveal windows. Route those changes to `novel-change`.
- If `rolling_plan.yml` has fewer than 4 future chapters, lacks `architecture_role`, or the next window is visibly a task chain with no world expansion / side-thread touch / growth budget, stop normal writing prep and run `novel-architect` or ask the user/director to do so before drafting.

## Context Budget Policy

Use working-memory context: keep whole-book promise, current volume goal, active flow, long-form scale, and rolling plan in mind; read entity/ledger entries by relevance; reread old chapter originals only when a concrete trigger exists.

Budgets: round context pack 3000-5000 Chinese characters; chapter `writing_packet.md` 1000-2500 Chinese characters, with a compact Writing Card. Read `rolling_plan.yml` in full each round, but summarize only the batch chapters, adjacent chapters, and later constraints that affect this task.

## Read First

Read once per session or when uncertain:

- `docs/CONTEXT_PACK.md`, `docs/CANON_AND_SAFETY.md`, `docs/MEMORY_MODEL.md`, `docs/FILE_FORMATS.md`, `docs/WRITING_CRAFT.md`
- Current project `project.yml`
- `book/constitution.md`, `book/longform_blueprint.yml`, `book/reader_model.yml`, `book/style_memory.md`
- `book/chapter_rhythm_guide.md`（本章类型对应的节奏模板）
- `style/rewrite_rules.md`, `style/samples.md`
- `planning/active_flow.yml`, `planning/rolling_plan.yml`, `planning/current_round.yml` if it exists
- `planning/story_architecture.yml`, `planning/thread_board.yml` if they exist
- `meta/model_policy.yml` if it exists

Do not paste these files into context packs or writing packets. Extract only the operational conclusions needed for the current task.

## Model Routing

Use `docs/MODEL_ROUTING.md` and project `meta/model_policy.yml` when available.

Default:

- Use `premium_model` for active_flow, rolling_plan, chapter concept, draft prose, final prose revision, ending rewrite, canon merge, and quality gate.
- Use `fast_model` only for YAML/TXT formatting, validator error summaries, diff summaries, session logs, and other mechanical tasks whose output can be checked.
- Hybrid writing packet drafting is allowed, but the writing agent must confirm the final packet before drafting.
- Never let `fast_model` directly write or approve `final.txt`.
- Never let `fast_model` make Level 3-5 change decisions or protected-file edits.

If model routing is used, record it in the round context pack or `meta/session_log.md`.

## Source Of Truth

Follow `docs/CANON_AND_SAFETY.md`. Key rule: `final.txt` is canon text, `canon_delta.yml` is a change log, and current state lives in `entities/`, `ledgers/`, and `planning/`. Do not merge contradictions casually.

## Narrative Flow Requirements

Before each round, ensure `planning/active_flow.yml` has current pressure, scene chain, last cut, next opening/handoff, and end conditions. Start a new flow only when the story genuinely changes subject, location, POV, objective, or dramatic mode; never just because a round begins.

## Rolling Synopsis Requirements

Before each round, ensure `planning/rolling_plan.yml` contains a detailed 6-15 chapter forward window.

Use `templates/project/planning/rolling_plan.yml` and `docs/FILE_FORMATS.md` for the full field list. Hard constraints:

- keep only the active 6-15 chapter future window;
- move completed plans to `planning/completed_plan_log.yml`;
- move distant or over-capacity plans to `planning/future_backlog.yml`;
- keep each chapter synopsis around 300-800 Chinese characters;
- include `cross_chapter_event`, `starts_mid_action`, `ends_mid_action`, `chapter_function`, `pressure_curve.position_in_flow`, `reader_question_flow`, `core_advance`, `information_release`, `side_yield`, `叙事织入`, and `planned_handoff`;
- include `architecture_role` with pacing mode, world expansion, protagonist growth budget, information reveal boundary, side-thread touch, off-screen pressure, recurring assets, must-not-resolve, and a writable scene seed;
- treat rolling plan as story-content planning, not an intra-chapter prose template.

## Background Completion Gate

Run this gate whenever refreshing `active_flow.yml`, sliding or expanding `rolling_plan.yml`, creating a round context pack, or generating a chapter `writing_packet.md`.

1. **Scan upcoming use**
   - Inspect the batch chapters and the next 3-6 chapters in `rolling_plan.yml`.
   - List all people, factions, places, roles/titles, institutions, rules, power-system elements, recurring items, historical causes, resources, rumors, debts, and foreshadowing that will enter scenes or constrain action.

2. **Verify storage**
   - Stable background must be in `entities/`: characters, factions, locations, items, power system.
   - Dynamic background must be in `ledgers/`: world pressure, knowledge visibility, narrative debts, foreshadowing, rumors, decisions.
   - `rolling_plan.yml` may reference and schedule background, but it must not be the only place where reusable background exists.
   - `writing_packet.md` may summarize chapter-relevant background, but it must cite the source file and must not invent missing background.

3. **Complete missing background before planning proceeds**
   - If a planned chapter needs an unnamed or underdefined entity, pause planning and create a compact Background Completion Pack.
   - Write the completed background into the proper `entities/` or `ledgers/` file before it appears in `rolling_plan.yml` or `writing_packet.md`.
   - It is acceptable to add narrowly scoped background just before writing, but it must be recorded first, then referenced by the packet, then used by writer.
   - If the missing background would alter protected book/volume/core-character/endgame facts, route to `novel-change`.

4. **Minimum usable background**
   - A faction needs: name, scale, hierarchy or internal structure, goal, resources, representative people, current action, attitude to protagonist, usable scene texture.
   - A location needs: name, scale, placement, sensory texture, social function, who controls it, what pressure or opportunity it creates.
   - A recurring character needs: name, role, current intent, relationship to protagonist, faction tie, speaking/action tendency, what they can change.
   - A rule/system event needs: host or enforcer, venue, participant scale, public rule, hidden rule, reward/cost, loophole or pressure point.
   - A power-system element needs: current stage meaning, test method, cost, failure mode, visible sign, what characters misunderstand about it.

5. **Do not pass the gate with placeholders**
   - Remove or resolve placeholders such as `待命名`, `自行命名`, `writer 自行`, `某宗门`, `某长老`, `某师兄`, `某管事`, `暂定`, `placeholder`, `TBD`, or equivalent.
   - Generic labels are allowed only for genuinely nameless extras who do not recur and do not affect canon.
   - If an entity can affect future state, give it a stable name or ID and store it.

## Round Workflow

See `docs/WORKFLOWS.md` for the full workflow. Default round mode:

1. **Prepare**: validate planning YAML, refresh `active_flow` / `rolling_plan`, compile round context, write `current_round.yml`.
   - If the future window is empty/thin or the story is shrinking, run `novel-architect` first: compile `architect_context_pack`, generate a development pack, director-review accepted updates, then refresh rolling_plan.
   - During refresh, run the Background Completion Gate. Do not generate round context until missing background for the batch and near-future window is resolved or explicitly routed to `novel-change`.
2. **Prebuild**: use `novel-planner` when available to create all batch `writing_packet.md` files before drafting. Each packet includes audit context, a design/execution Writing Card, and `Pre-Draft Self Check`.
   - Each packet must include a Background Use Audit with source references. If the audit has unresolved missing background, stop before drafting.
3. **Continuous draft**: use `novel-writer` when available to write all batch drafts back-to-back; between drafts only write `draft_handoff_note`. Do not run validator, merge canon, archive planning, or call QA between drafts.
4. **Batch cold read and finalize**: run draft self-check, run `check_not_but.py --files draft.txt`, use cold-reader, revise drafts, then write `final.txt`.
5. **Batch engineering merge**: write `review.md`, `summary.yml`, `canon_delta.yml`, diff-only `memory_update_plan.md`; generate a merge preview, review it, then apply safe current-state updates into `entities/`, `ledgers/`, `volumes/`, and `planning/`.
6. **Post-merge QA**: run validator / `novel-qa phase: post_merge` after all state files are merged. Do not mark complete before this passes.

Hard gates:

- `reader_pass.md` must exist and pass before `final.txt`.
- `canon_delta.yml` must include `state_sync` for affected current-state files.
- `state_sync.status: needs_director_review` is not a completion state. Before post-merge QA, resolve every such target to `merged` / `updated` / `synced`, or `n/a` only when there was no substantive change.
- Keep template headings stable in `writing_packet.md` and `review.md`; validator treats these headings as a machine-readable contract, not presentation text. Do not rename `Writing Card` or `Pre-Draft Self Check`.
- `writing_packet.md` must keep the full template heading contract: `Read Files`, `Source References`, `Longform Scale Check`, `Cut Continuity`, `Reader Reward Check`, `Writing Card`, `Pre-Draft Self Check`, and `Required Updates After Writing`. A dense packet with renamed headings is still invalid.
- `writing_packet.md` must include `Background Use Audit`. It must list chapter-critical entities/background, source files, missing or newly completed background, and writer freedom boundaries.
- `planning/rolling_plan.yml` chapter entries must include `background_dependencies` or equivalent explicit references for reusable people/factions/locations/items/rules used by the chapter.
- `planning/rolling_plan.yml` chapter entries should include `architecture_role`; missing architecture fields mean planner/writer must not invent world-expansion, growth, or side-thread logic.
- If `style/samples.md` has real content, round context and every Writing Card must include concrete positive sample anchors. Do not write "samples.md is empty" unless the file was actually checked and is empty/placeholding.
- Do not include examples that violate `prose_constraints` inside `opening_sensory`, `scene_moments`, `voice_examples`, or `sample_style_anchors`; writer will imitate examples more strongly than abstract bans.
- Changed character entries must update `last_updated` or `change_history`.
- `active_flow.last_cut` must match the latest completed chapter.
- `rolling_plan.yml` must only contain future unfinished chapters.
- `planning/merge_previews/round_XXX.yml` must be generated before current-state files are applied; unresolved high-confidence pending operations block completion.
- `planning/merge_previews/round_XXX.yml` must not be a template placeholder. If it says `project: template` or only lists `ch001` for a three-chapter round, regenerate it.
- `memory_update_plan.md` is per chapter. Do not satisfy ch002/ch003 by pointing to ch001's batch memory plan.

## 写作心法、TXT 格式和 draft self-check

详见 `docs/WRITING_CRAFT.md`。`writing_packet.md` 的 Writing Card 必须从该文档和本章 context 中摘取适用约束，但不要全文复制。

本 skill 内保留的硬门禁：

- `draft.txt` 必须先完成 draft self-check，才能进入 `reader_pass.md`。
- `novel-planner` 可负责 `writing_packet.md` 草案和 rolling_plan 局部细化建议；它不能写正文、不能合并 canon/state/planning。
- `novel-architect` 可负责 `planning/development_packs/dev_XXX.md` 和未来 10-30 章故事开发建议；它不能写正文、不能合并 canon/state/planning。
- `novel-writer` 可负责 `draft.txt`、根据 `reader_pass.md` 修稿、以及质量门通过后的 `final.txt`；它不能修改 summary/canon/state/planning。
- `python scripts/check_not_but.py <project> --chapters <batch chapters> --files draft.txt` 是 final 前硬门禁。
- `check_not_but.py` 同时扫描 not-but、三连否定内心声明、元叙述和箭头/编号式认知总结；出现后先改 draft。
- `draft.txt` 和 `final.txt` 必须遵守 TXT 格式：标题后一空行，正文普通段落之间不空行，多数段落 40-160 字，超过 220 字视为格式失败。
- 结尾必须留下外部运动交接，避免空泛反思式收束。
- “不是X而是Y / 不是X，是Y”默认禁用；确需使用时每章最多 1 次，且必须在 review 中说明不可替代性。

## Draft Self-Check And Cold Reader Gate

在写 `final.txt` 之前，必须先完成 draft self-check 和 `reader_pass.md`。这两步是质量门，不是事后总结。

`reader_pass.md` 默认由独立 cold-reader subagent 生成。该 subagent 的身份是同类型中文网文资深责编，只看读者体验、文笔自然度、节奏松紧、人物体温、对白是否像人说话，以及局部断句、短句堆叠、破折号密度、描写、转场是否僵硬。不要检查 YAML、账本或工程完整性。输出必须短，通常 300-800 字。

Cold-reader subagent 只接收：

- `draft.txt`
- `writing_packet.md` 中的 Writing Card
- `book/style_memory.md` 中与文笔有关的部分
- `style/samples.md`（如果有真实内容）
- 1-2 句必要前情

不要给 cold-reader subagent：`planning/rolling_plan.yml`、动态账本、`summary.yml`、`canon_delta.yml`、validator 输出或工程同步任务。避免工程上下文污染读者判断。

如果运行环境不能启用 subagent，允许同 agent fallback，但必须在 `reader_pass.md` 中写明：

- `reader: same_agent_fallback`
- fallback 原因
- 冷读置信度较低

`reader_pass.md` 输出：

0. reader：`cold_reader_subagent` / `same_agent_fallback`。
1. 最值得保留的一段：如果没有，写"没有"。
2. 最生硬的 3 处。
3. 叙述自然性与断句流畅性：判断短句、句号、破折号、省略号和段落切分是否服务情绪/动作/喜剧节奏；如果出现莫名短句连打、机械断句、破折号堆叠或同类顿挫连续重复，必须指出具体位置。
4. 局部润色建议：3-5 条，针对断句僵硬、短句堆叠、破折号过密、描写不自然、对话像信息交换、转场突兀或句式重复。可以给短句级替换方向，但不要整段代写，不要改变剧情事实。
5. 必须重写的 1-2 个局部。
6. 是否允许进入 final：`pass` / `revise required`。

如果输出 `revise required`、"最值得保留的一段"为"没有"，或冷读认为断句/短句/破折号问题已经影响阅读流畅性，必须重写 draft 后再重新冷读。

## 审查清单

`review.md` 必须使用 `templates/project/chapters/ch001/review.md` 的结构，保持诊断性，不做自我表扬。它必须至少指出一个弱点或风险，并记录最终 QA / validator 结果。

如果 `reader_pass.md` 曾输出 `revise required`，修稿后必须生成 `reader_recheck.md`，且 verdict 为 `pass` 后才能写 `final.txt`。

不要在 skill 中复制审查清单；审查细则以模板、`docs/WRITING_CRAFT.md`、`docs/CANON_AND_SAFETY.md` 和 `skills/novel-review/SKILL.md` 为准。

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

- `planning/active_flow.yml`, `planning/context_packs/*`, `planning/current_round.yml`, `planning/rolling_plan.yml`
- `chapters/chXXX/*`
- `entities/*`, `ledgers/*`, `volumes/*`, `arcs/*` when current state changes
- `book/global_summary.md`
- `book/style_memory.md` only for observed style memory, not constitution changes
- `meta/session_log.md`

Protected or confirmation-required:

- `book/constitution.md`, `book/longform_blueprint.yml`, endgame-level secrets, protagonist core motive, current volume goal, major character permanent removal, large retcons

## Failure Handling

Stop before drafting if planning YAML is invalid, source-of-truth files conflict, `longform_blueprint` / `active_flow` / `rolling_plan` are missing or stale, required prior files are missing, the chapter depends on an unconfirmed idea as canon, or the chapter needs background that has not been completed and stored in `entities/` or `ledgers/`.

Stop before finalizing if the draft reads like an outline/report, behaves as an isolated chapter box, ends on empty reflection, lacks external handoff, violates TXT format, lacks required artifacts, fails validator, or leaves current state / active_flow / rolling_plan stale.
