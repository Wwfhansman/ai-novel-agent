# 正史与安全规则

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

默认规则：

- `final.txt` 是已确认章节正文。
- `draft.txt` 不是正史。
- `idea_pool.yml` 不是正史，除非条目状态为 `promoted` 且被写入规划、伏笔或正文。
- `canon_delta.yml` 是章节造成的状态变化记录，不是当前状态总表。
- `entities/`、`ledgers/`、`planning/` 存当前权威状态。
- `planning/active_flow.yml` 是当前连续剧情流的权威来源。

## 3. 唯一事实来源

冲突时按下表判断。

| 事实类型 | 权威来源 | 辅助来源 | 说明 |
| --- | --- | --- | --- |
| 已发生的正文事实 | `chapters/chXXX/final.txt` | `summary.yml`, `canon_delta.yml` | 原文细节以 `final.txt` 为准。 |
| 某章发生了什么 | `chapters/chXXX/summary.yml` | `final.txt` | 摘要用于快速理解，冲突时回看正文。 |
| 某章造成了什么变化 | `chapters/chXXX/canon_delta.yml` | `summary.yml` | delta 是变更日志，不代表当前最终状态。 |
| 人物当前状态 | `entities/characters.yml` | 最近 `canon_delta.yml` | 当前目标、立场、关系、意图以实体库为准。 |
| 势力当前状态 | `entities/factions.yml` | `ledgers/world_state.yml` | 势力基本资料在实体库，外部局势在世界状态。 |
| 地点/物品设定 | `entities/locations.yml`, `entities/items.yml` | 相关章节正文 | 设定以实体库为准，历史细节看正文。 |
| 当前世界局势 | `ledgers/world_state.yml` | `volume_state.yml`, `canon_delta.yml` | 主角之外的外部系统以 world_state 为准。 |
| 谁知道什么 | `ledgers/knowledge_state.yml` | 相关章节正文 | 信息差以 knowledge_state 为准。 |
| 读者期待债 | `ledgers/narrative_debts.yml` | `volume_debts.yml`, `canon_delta.yml` | 全局债务以 ledger 为准。 |
| 伏笔状态 | `ledgers/foreshadowing.yml` | `canon_delta.yml` | 是否已埋、推进、回收以 ledger 为准。 |
| 当前卷进展 | `volumes/vol_XXX/volume_state.yml` | `volume_summary.md` | 结构化当前进展以 state 为准。 |
| 当前连续剧情流 | `planning/active_flow.yml` | `arcs/*`, `rolling_plan.yml`, 最近 `canon_delta.yml` | active_flow 决定章节从哪个压力中切出，不受 round 边界控制。 |
| 近期未来计划 | `planning/rolling_plan.yml` | `current_round.yml` | 6-15 章详细章纲以 rolling_plan 为准。 |
| 本批次追踪状态 | `planning/current_round.yml` | `planning/rolling_plan.yml`, `planning/active_flow.yml`, round context pack | current_round 只记录本轮写哪几章、状态和起止 flow，不能复制章纲、另起冲突计划或写 round 级剧情目标。 |
| 未确认点子 | `ledgers/idea_pool.yml` | `opportunity_ledger.yml` | 不可当作正史。 |
| 重大创作决策 | `ledgers/decision_log.yml` 或 `meta/decision_log.*` | 用户对话摘要 | 决策必须落盘。 |

## 4. 同步规则

每章完成后，agent 必须按顺序同步：

```text
final.txt
→ summary.yml
→ canon_delta.yml
→ entities/*
→ ledgers/*
→ volumes/*
→ planning/*
```

同步原则：

- `canon_delta.yml` 只追加或记录本章变化，不承担当前总状态。
- 当前状态必须合并进 `entities/` 和 `ledgers/`。
- 每章造成的外部交接必须写入 `canon_delta.yml` 的 `actual_handoff`，并同步到 `planning/active_flow.yml` 的 `last_cut.current_handoff`；规划中的未来交接写入 `planning/rolling_plan.yml` 的 `planned_handoff`。
- 旧状态如果失效，必须显式更新状态字段，不要保留冲突描述。
- 如果无法确定是否应覆盖旧状态，写入 `review.md` 或 `meta/open_questions.md`，不要静默猜。

## 5. 冲突处理规则

当 agent 发现冲突时：

1. 停止写正文。
2. 列出冲突文件和冲突内容。
3. 根据唯一事实来源表判断默认权威。
4. 如果仍不确定，进入 `novel-review` 或 `novel-change`。
5. 生成冲突解决摘要。
6. 修改相关文件并记录到 `decision_log`。

## 6. 受保护文件

以下文件受保护，不能由 `novel-write` 静默修改：

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
3. **Validator 辅助**：运行：

```bash
python scripts/validate_novel_output.py <project> --check-protected-files
```

该检查会确认项目存在变更日志入口，并提示日志是否缺少 `Change Summary`、`novel-change` 或 protected-file 相关记录。它是可见性检查，不是完整的技术隔离。

如果项目使用 Git，受保护文件修改前建议创建 checkpoint，修改后的 commit message 使用 `change:` 前缀。
