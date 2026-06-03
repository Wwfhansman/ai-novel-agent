---
name: novel-change
description: Manage mid-story changes in an AI Novel Agent project. Use when the user wants to add an idea, alter a setting, change a character or relationship, adjust an outline, promote an idea, resolve canon conflicts, or perform a reboot-level change.
---

# Novel Change

Use this skill for changes after bootstrap. Do not default to rebooting the novel. Most changes should be evaluated, scoped, and integrated into existing memory.

> ⚠️ **引擎项目（有 `events/`）**：当前状态变化记进 `events/`（`relationship_changed`/`character_changed`/`faction_changed`/`knowledge_changed`…），由 `commit` 物化进 `entities/ledgers`——**不要手写 `entities/ledgers`，也不用写 `canon_delta.yml`**。下文提到的 `canon_delta.yml`/`summary.yml` 属未迁移旧项目。受保护文件与变更分级规则（见 `docs/CANON_AND_SAFETY.md`）对两套都适用。

## Read First

Read:

- `docs/CANON_AND_SAFETY.md`（受保护文件与变更分级）
- `docs/ENGINE.md`（引擎正史/状态模型：events 权威、entities/ledgers 派生）
- Target project `project.yml`
- `meta/model_policy.yml` if present
- Relevant current-state files. 引擎项目里，canon 变化记进 `events/`，不手写 `entities/ledgers`。

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

## Mid-Story Idea Intake

Treat every user mid-story post as an intake item first, not canon by default.

Classify the requested change into one of these buckets before editing files:

```text
candidate_idea: interesting but not committed; store in `ledgers/idea_pool.yml`.
future_setup: likely useful later; store in `ledgers/foreshadowing.yml` or future backlog.
near_term_plan: affects the next 6-15 chapters; update `planning/rolling_plan.yml`.
current_flow_change: affects the current scene chain or immediate handoff; update `planning/active_flow.yml`.
current_state_change: changes present-time character/world/knowledge/faction/location state; record it as a typed event in `events/chNNN.yml` (relationship_changed / character_changed / faction_changed / knowledge_changed / …), then `commit` — do NOT hand-edit `entities/`/`ledgers/` (they are derived).
protected_change: touches protected book/volume/core-character/secret files; require Change Summary and checkpoint.
retcon: contradicts existing `final.txt`; require explicit user approval before rewriting canon.
```

Do not promote a user idea directly into canon just because it is appealing. First decide whether it is a candidate, setup, plan change, current-state change, protected change, or retcon.

## Continuity and Handoff Rules

Respect the current continuity authorities:

- `final.txt` is the authority for already written prose facts.
- `events/chXXX.yml` is the authority for what a chapter changed; current state is **derived** from it (`entities/`/`ledgers/` are materialized by `commit`, not hand-written).
- `planning/rolling_plan.yml` is the authority for the next 6-15 chapter plan.
- `planning/active_flow.yml` (if used) tracks the current cross-round scene chain.

When a change affects upcoming continuity:

- If it changes what should happen soon, update `rolling_plan.yml`.
- If it changes the immediate ongoing pressure / next opening, update `active_flow.yml`.
- If it changes current character/world/knowledge/faction/location state, record a typed event in `events/` and `commit`. Never leave it only as prose or hand-edit the derived `entities/`/`ledgers/`.
- For changes to already-written canon (retcon), get user approval; then add corrective events and, if prose must change, edit the affected `final.txt`.

## 工作流

1. **重述变更请求**
   - 识别精确的用户意图。
   - 判断它属于 candidate_idea / future_setup / near_term_plan / current_flow_change / current_state_change / protected_change / retcon。

2. **分级影响**
   - 分配 Level 1-5。
   - 识别受影响文件和受保护文件。

3. **读取相关正史**
   - 读取当前权威状态文件。
   - 如果变更触及已有正文，读取相关章节全文——retcon 敏感的变更不能只靠摘要。

4. **评估兼容性**
   - 检查创作宪法、读者模型、当前卷目标、角色意图和信息可见性、叙事债务和伏笔影响。

5. **提出接入方案**
   - 提供一个推荐路径，有需要时给出备选。
   - 判断写入 `idea_pool` / `foreshadowing` / `active_flow` / `rolling_plan` / `entities` / `ledgers` / 受保护文件。
   - 明确是否影响 `planned_handoff`、`actual_handoff` 或 `current_handoff`；不要把三者混写。

6. **只应用安全变更**
   - 受保护文件：修改前输出 diff 摘要、建立 checkpoint、要求确认。
   - Level 3-5 变更：根据 `meta/model_policy.yml` 要求 premium_model 或人类确认。
   - 普通变更：更新权威文件并记录决策。

7. **记录决策**
   - 更新 `ledgers/decision_log.yml` 或 `meta/session_log.md`。
   - 如果不立即应用，写入 `ledgers/idea_pool.yml`。

## 安全落脚点

- 新的不确定点子 → `ledgers/idea_pool.yml`
- 潜在未来 payoff → `ledgers/foreshadowing.yml`
- 当前角色状态 → `entities/characters.yml`
- 当前信息可见性 → `ledgers/knowledge_state.yml`
- 当前世界反应 → `ledgers/world_state.yml`
- 当前跨轮 flow → `planning/active_flow.yml`
- 未来章纲路径 → `planning/rolling_plan.yml`
- 全书规模/宏观阶段/递进节奏/揭示窗口 → `book/longform_blueprint.yml`（受保护）
- 当前卷目标 → 受保护，只在显式变更流程中修改。

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
