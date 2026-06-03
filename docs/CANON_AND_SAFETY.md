# 正史与安全规则

> ⚠️ **引擎模型下的事实来源**：`events/chXXX.yml` 是变化的权威，当前状态由它派生（`commit` 物化进 `entities/`、`ledgers/`，**不手写**）。下文的"唯一事实来源"表与 `summary.yml`/`canon_delta.yml`/`memory_update_plan.md`/旧 `scripts/` 属未迁移旧流程；引擎项目以 events 为准，见 [引擎化写作流程](ENGINE_WORKFLOW.md)。**本文仍然有效的核心是"受保护文件"与"变更分级"规则**（`novel-change` 用）。

## 1. 目标

本项目采用“文件即数据库”。这要求每类事实都有明确的唯一事实来源，并且 agent 不能随意修改受保护文件。

如果不定义冲突规则，冷启动时 agent 会读到互相矛盾的状态，长篇创作会失控。

## 2. 正史状态分层

项目中的内容分为：

```text
canon: 已确认正史
draft: 草稿
proposal: 提案
idea: 未确认灵感
retcon: 对旧正史的修订计划
```

默认规则（引擎模型）：

- `final.txt` 是已确认章节正文（原文细节最高权威）。
- `events/chNNN.yml` 是本章造成的 canon 变化的权威（append-only 事件日志）。
- `entities/`、`ledgers/` 是**派生产物**：由 `commit` 从 events 投影出来，**不手写**。
- `idea_pool.yml` 不是正史，除非晋升并写入规划/伏笔/正文（记成事件）。

## 3. 唯一事实来源

冲突时按下表判断。

| 事实类型 | 权威来源 | 说明 |
| --- | --- | --- |
| 已发生的正文事实 | `chapters/chXXX/final.txt` | 原文细节以 `final.txt` 为准。 |
| 某章造成了什么变化 | `events/chXXX.yml` | ★append-only 事件日志；当前状态由它派生。 |
| 人物/势力/地点/物品/力量体系当前状态 | `entities/*.yml` | ★由 events 派生（`commit` 物化），不手写。 |
| 世界局势/信息差/伏笔/读者期待债 | `ledgers/*.yml` | ★同为派生产物。 |
| 近期未来计划 | `planning/rolling_plan.yml` | 6-15 章详细章纲，由 `novel-architect` 维护。 |
| 当前卷编剧控制 | `planning/story_architecture.yml` / `thread_board.yml` | 卷节奏、成长、信息释放、支线调度。 |
| 重大创作决策 | `ledgers/decision_log.yml` 或 `meta/session_log.md` | 决策必须落盘。 |
| 长篇规模递进 | `book/longform_blueprint.yml` | ★受保护。 |

## 4. 同步规则（引擎模型）

每章完成后：

```text
final.txt → events/chXXX.yml（把本章变化记成类型化事件）→ check → commit（物化派生状态）
```

同步原则：

- 机械变化（关系/人物状态/信息差/势力/地点/债务/伏笔/道具）**必须用类型化事件**，不塞进 `fact_added`/`note`。
- **不手工编辑 `entities/`、`ledgers/`**——`commit` 会用 events 重算并覆盖。
- 章末外部交接记进 `events/chXXX.yml`（`note` 或类型化事件）；规划中的未来交接写 `rolling_plan.yml` 的 `planned_handoff`。
- 旧状态失效时，追加更正事件（如新的 `*_changed`）；不要手改派生文件。
- 拿不准是否构成 canon 变化时，写 `meta/open_questions.md` 或调用 `novel-memory-recheck`，不要静默猜。

## 5. 冲突处理规则

当 agent 发现冲突时：

1. 停止写正文。
2. 列出冲突文件和冲突内容。
3. 根据唯一事实来源表判断默认权威。
4. 如果仍不确定，进入 `novel-review` 或 `novel-change`。
5. 生成冲突解决摘要。
6. 修改相关文件并记录到 `decision_log`。

## 6. 受保护文件

以下文件受保护，写作流程（`novel-engine-write` 等）不能静默修改：

```text
book/constitution.md
book/longform_blueprint.yml
book/reader_model.yml
book/style_memory.md 的核心风格规则
book/endgame_hypotheses.yml 中已确认的终局约束
volumes/vol_XXX/volume_outline.md 的卷目标
entities/characters.yml 中主角核心欲望和底线
ledgers/knowledge_state.yml 中终局级秘密
ledgers/decision_log.yml
```

## 7. 修改前确认规则

涉及以下事项时，必须进入 `novel-change`，并在修改前给出 diff 摘要：

- 修改创作宪法。
- 改变作品类型、核心卖点或读者承诺。
- 改变主角核心欲望。
- 杀死或永久移除主要角色。
- 揭露终局级秘密。
- 改变当前卷目标。
- 大规模 retcon 已写正文。
- 将 `idea_pool` 中的重大点子晋升为主线。

## 8. Diff 摘要要求

修改受保护文件前，agent 必须输出：

```text
Change Summary
- 修改原因
- 受影响文件
- 旧设定/旧状态
- 新设定/新状态
- 影响范围
- 是否需要补铺垫或重写旧章节
- 是否需要用户确认
```

## 9. Git Checkpoint

MVP 阶段建议使用 Git 作为文件数据库安全带。

推荐规则：

- 每轮三章生产批次开始前建立 checkpoint。
- 每轮三章生产批次结束后提交一次。
- 每次受保护文件修改前提交一次。
- 每次大规模变更后提交一次。

推荐提交信息：

```text
checkpoint: before round 003
write: complete round 003 chapters 007-009
change: promote idea_014 into volume 001 outline
review: resolve knowledge_state conflict after ch012
```

即使未来产品化不直接暴露 Git，MVP 阶段也应把 Git 当作回滚工具。

如果项目准备公开开源，真实小说内容不应提交到公共仓库。可以采用两种方式：

- 开源系统仓库忽略 `/projects/*`，真实小说项目放在单独的私有 Git 仓库。
- 在公共仓库只保留 `projects/example-project/`，真实项目使用本地私有分支或独立工作区。

不要一边忽略真实小说文件，一边指望公共仓库的 Git checkpoint 能回滚小说内容。用于创作安全带的 Git 必须跟踪实际小说项目文件。

## 10. 受保护文件修改可见性检查

MVP 阶段无法只靠 validator 完全阻止 agent 修改受保护文件。系统采用“确认流程 + 可见性检查”增加摩擦力：

1. **修改前确认**：修改受保护文件前必须进入 `novel-change`，输出 Change Summary，并由用户确认。
2. **变更记录**：修改必须记录到 `ledgers/decision_log.yml` 或 `meta/session_log.md`。
3. **变更可见性**：确认 `ledgers/decision_log.yml` 或 `meta/session_log.md` 里有本次受保护改动的 `Change Summary` 记录。这是可见性约定，不是技术隔离。

如果项目使用 Git，受保护文件修改前建议创建 checkpoint，修改后的 commit message 使用 `change:` 前缀。
