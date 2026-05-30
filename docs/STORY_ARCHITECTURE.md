# 编剧层与世界运营

`novel-architect` 是主编剧 / 世界大脑。它负责把全书、当前卷和未来 10-30 章当作一个多方博弈系统来设计和推演，持续给正文写作供给世界、人物、势力、支线、制度、资源、信息差和节奏约束。

它不是 `novel-planner`，也不是 `novel-writer`。`novel-planner` 把既有规划编译成 `writing_packet.md`；`novel-writer` 写正文；`novel-architect` 负责在写作前设计未来世界如何运行、当前卷如何扩张、哪些支线和信息应该进入近期窗口。

## 1. 三层边界

```text
novel-architect
  设计未来、运营世界、控制卷节奏、开发可写素材
  ↓
novel-planner / novel-writer
  把已落库、已进入 rolling_plan 的内容写成正文
  ↓
novel-archivist / review / validator
  根据 final.txt 记录已发生事实，维护当前状态
```

核心边界：

- `architect` 设计未来，不记录已发生事实。
- `writer` 写正文，不临时决定关键设定。
- `archivist` 记录已发生，不发明未来。
- `director` 保持唯一合并入口和最终裁决权。

## 2. 与现有文件的所有权边界

新增编剧层文件不能复制已有账本的职责。冲突时按下表判断：

| 主题 | 既有权威 | 编剧层文件 | 边界 |
|------|---------|-----------|------|
| 全书规模递进 | `book/longform_blueprint.yml` | `planning/story_architecture.yml` | `longform_blueprint` 是全书级约束，受保护；`story_architecture` 是当前卷/当前阶段的操作化执行方案。 |
| 信息分布 | `ledgers/knowledge_state.yml` | `planning/story_architecture.yml` | `knowledge_state` 记录已发生的信息分布；`story_architecture.information_release_plan` 记录未来释放计划。 |
| 外部世界压力 | `ledgers/world_state.yml` | `planning/thread_board.yml` | `world_state` 是当前快照；`thread_board.offscreen_actions` 是带时间线的行动计划。 |
| 读者期待和伏笔 | `ledgers/narrative_debts.yml` / `ledgers/foreshadowing.yml` | `planning/thread_board.yml` | 账本面向读者体验和正史证据；`thread_board.threads` 面向编剧调度和支线生命周期。 |

简化说法：

```text
blueprint = 宪法
story_architecture = 当前卷施政纲要
world_state = 照片
thread_board = 剧本
narrative_debts / foreshadowing = 读者等待什么
thread_board.threads = 编剧怎么调度这些线
```

## 3. Director 与 Architect

`novel-architect` 是 `novel-director` 的 subagent，而不是平级决策者。

推荐权限：

- 可写：`planning/development_packs/dev_XXX.md`
- 可建议：`planning/story_architecture.yml`、`planning/thread_board.yml`、`planning/future_backlog.yml`、`planning/rolling_plan.yml`、`entities/`、`ledgers/`
- 不直接合并：正史文件、当前状态文件、受保护文件

工作流：

```text
director 触发 architect
→ director 先确认状态未漂移
→ director 编译 architect_context_pack.md
→ architect 输出 development_pack
→ director 审核、接受、修改或拒绝
→ director 将接受内容写入 planning / entities / ledgers
```

`architect` 享有战略建议权；最终合并权属于 `director`。

## 4. 上下文包机制

`architect` 需要全局理解，但不能每次无控制地读取全项目。运行前由 `director` 编译：

```text
planning/context_packs/architect_context_pack_XXX.md
```

建议长度：8000-15000 中文字。

必须压缩进入 context pack 的内容：

- `book/constitution.md` 的类型承诺、禁区和读者承诺。
- `book/longform_blueprint.yml` 的当前宏观阶段、力量递进、规模递进。
- 当前卷 `volume_outline.md` / `volume_state.yml` 的目标和限制。
- `planning/active_flow.yml` 的当前压力、last_cut、下一步承接。
- `planning/rolling_plan.yml` 的完整未来窗口摘要。
- `planning/story_architecture.yml` 和 `planning/thread_board.yml` 的当前状态。
- 近 6-9 章 `summary.yml`，必要时最近 1-2 章 `final.txt` 的关键片段。
- 相关 `entities/`、`ledgers/` 的定向摘要，而不是全量复制。

必须原文读取或精确摘录的内容：

- 受保护约束的相关条款。
- 当前 `active_flow.last_cut`。
- 当前 `rolling_plan` 的 batch 章节和后续 3-6 章。
- `knowledge_state` 中与本次开发相关的秘密边界。

## 5. 核心能力

### 全局叙事推演

把世界当作多方博弈系统运行：

- 如果主角不行动，各方势力会做什么？
- 每个重要角色有什么目标、资源、约束？
- 哪些摩擦来自利益、位置、资源、规则，而不是单纯性格坏？
- 主角介入后，谁获利、谁受损、谁误判？

### 多线程编排

支线有生命周期：

```text
seeded → dormant → rising → intersecting → payoff → aftermath
```

每条活跃支线必须知道：

- 上次触碰在哪章；
- 沉默了多久；
- 下次如何浮现；
- 与主线的交汇点；
- 预期后果和回收窗口。

### 世界预制

预制不是百科设定，而是提前想清可交互空间：

- 地点：感官质感、社会结构、权力关系、日常运转、可触发冲突。
- 角色：动机、资源、约束、说话方式、秘密、与主角的利益关系。
- 势力：目标、资源、内部分裂、当前行动、代表人物。
- 制度：规则、执行者、漏洞、代价、历史由来、误用后果。

### 节奏和规模管控

`architect` 必须审计：

- 是否连续多章都在主角眼前任务推进；
- 主角实力、身份、资源、认知成长是否过密；
- 世界尺度是否停滞；
- 高潮后是否有余波；
- 信息是否揭得太快或拖太久；
- 配角和势力是否有 off-screen 生活。

### 素材可写化

输出必须能让 writer 直接转化为场景。

差：

```text
外门制度森严。
```

好：

```text
主角去领月例时，杂役弟子的牌号被排在外门弟子之后。管事没有辱骂他，只按规矩让他等三个时辰。压迫来自“程序正确”，不是恶人嘴脸。
```

## 6. pacing_budget 语义

`story_architecture.yml` 中的节奏预算必须区分目标、硬限制和实际用量：

```yaml
pacing_budget:
  window: ch001-ch030
  chapter_type_targets:
    pressure: "8-12"
    payoff: "4-6"
    expansion: "4-6"
    relationship: "3-5"
    recovery: "2-4"
    mystery: "2-3"
  hard_limits:
    max_consecutive_same_type: 2
    max_growth_events_per_10ch: 2
  actual_usage:
    pressure: 0
    payoff: 0
    expansion: 0
    relationship: 0
    recovery: 0
    mystery: 0
```

`chapter_type_targets` 是目标分布；`hard_limits` 是不应突破的硬边界；`actual_usage` 由 `director` 或 `architect` 在每次开发后更新。

## 7. thread_board 维护责任

| 状态转移 | 负责人 | 时机 |
|----------|--------|------|
| 新建 `seeded` / `dormant` | `architect` | 生成 development pack 时 |
| `dormant` → `rising` | `architect` | 下次运行，根据未来 rolling_plan 推进 |
| `rising` → `intersecting` | `director` | 合并 canon_delta 时，正文触发交汇 |
| `intersecting` → `payoff` | `director` | 合并 canon_delta 时，正文完成回收 |
| `payoff` → `aftermath` | `architect` | 下次运行，整理余波 |
| `aftermath` → 归档 | `architect` / `director` | 移入 `planning/completed_threads_log.yml` |

`thread_board.yml` 只保留活跃线程。已完成余波归档到 `completed_threads_log.yml`。

## 8. planned 与 active

为避免未来计划和正史状态混淆，实体可使用可选字段：

```yaml
canon_status: planned
source: development_pack dev_003
first_expected_use: ch012
```

默认值是 `active`，已有实体不需要补字段。

状态含义：

- `candidate`：灵感，未被 director 接受。
- `planned`：已被接受，准备进入未来正文，但尚未出现。
- `active`：已经进入正文正史。
- `retired`：已完成作用或退出舞台。

`architect` 可以建议创建 `candidate` / `planned`。正文出现后，由记忆维护层根据 `final.txt` 升级为 `active` 并记录 `first_appeared`。

## 9. writer 现场发挥边界

关键设定必须预制或经过 director 审批：

- 命名势力；
- 重要配角；
- 核心制度；
- 重要地点；
- 力量体系规则；
- 会复用的道具、资源、传闻和利益链。

氛围细节允许 writer 现场发挥：

- 一次性路人；
- 菜名、器物、小摊、小巷；
- 非复用场景质感；
- 不影响后续状态的临时动作。

如果现场发挥内容后来变得重要，archivist / director 应在写后补录。

## 10. development_pack 和 thread_board 容量

`development_pack` 是快照和决策记录，保留用于审计和冷启动回溯，但 `architect` 默认不读取旧 pack。它读取 `story_architecture.yml` 和 `thread_board.yml`，这两个文件是历次 pack 的浓缩结果。

`thread_board.yml` 只保留活跃线程。`aftermath` 线程在下一次 architect 运行时移入：

```text
planning/completed_threads_log.yml
```

`offscreen_actions` 在行动完成、取消或被正文消费后移除或归档。

## 11. 运行前检查

触发 architect 前先确认当前状态可信：

```text
触发 architect
→ 运行 validator / state drift 检查
→ 如有漂移，先修复 entities / ledgers / planning
→ 编译 architect_context_pack
→ 调用 architect
→ director 审核并合并可接受内容
```

如果当前状态漂移，architect 必须停止，不基于错误记忆设计未来。

可使用脚本生成上下文包并为旧项目补齐编剧层文件：

```bash
python3 scripts/compile_architect_context.py projects/<name> --init-missing
```

## 12. development_pack 模板

```markdown
# Story Development Pack

## Current Diagnosis
当前世界、节奏、成长、支线、设定厚度诊断。

## World Simulation
如果主角不行动，各方势力和角色会怎么动。

## Conflict Network Updates
未来 10-30 章的结构性冲突网络。

## Thread Lifecycle Updates
支线播种、浮现、交汇、回收计划。

## Prebuilt Assets
可复用地点、势力、人物、制度、资源、传闻。

## Writable Scene Materials
writer 可直接使用的场景触发点。

## Rhythm And Growth Budget
未来窗口节奏、主角成长、信息释放安排。

## Rolling Plan Inserts
建议进入 rolling_plan 的章节约束。

## Storage Plan
哪些进入 entities / ledgers / future_backlog / rolling_plan。

## Risks And Protected Changes
是否触碰受保护文件，是否需要 novel-change。
```
