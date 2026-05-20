# 文件格式规范

## 1. 总体原则

```text
正文用 txt
说明、brief、review、context pack 用 md
结构化状态用 yml
追加日志可用 md / yml / jsonl
```

## 2. TXT 正文格式

用于：

- 章节草稿：`chapters/ch001/draft.txt`
- 章节终稿：`chapters/ch001/final.txt`
- 导出全文

正文文件只包含小说正文，不混入任务说明、审稿意见、状态字段或 Markdown 标题。

推荐格式：

```text
第一章 边城雪夜

寒风卷过城墙时，主角站在一处关键地点前。
第二段正文继续，不在普通段落之间空行。
第三段正文继续。
```

规则：

- 章节标题后保留一个空行。
- 正文普通段落之间只换行，不额外空一行。
- 只有明确场景切换时，才允许额外空行或使用一行分隔符。
- 不要在 TXT 正文中写 `##`、清单、审稿意见、YAML 或流程字段。
- 仍然要正常分段。禁止把多个动作、对话、说明和情绪反应压进一个巨大自然段。
- 2000-3500 中文字章节通常应有 25-60 个正文段落。
- 多数正文段落建议 40-160 中文字；超过 220 字应考虑拆分，超过 360 字通常视为格式失败。
- 动作变化、说话人变化、反应落点、新信息出现、视角/镜头变化、节奏停顿时，应主动分段。

## 3. Markdown

用于自然语言文档：

- `book/constitution.md`
- `book/longform_blueprint.yml`
- `book/global_summary.md`
- `volumes/vol_001/volume_outline.md`
- `chapters/ch001/brief.md`
- `chapters/ch001/outline.md`
- `chapters/ch001/context_pack.md`
- `chapters/ch001/review.md`
- `style/rewrite_rules.md`

`outline.md` 是可选创作草稿，不是强制 scene beats。它可以记录灵感、可能的画面、台词碎片、局部细节，但不能成为固定章节模板。

## 4. YAML

用于结构化状态：

- 人物当前状态
- 世界当前状态
- 信息可见性
- 伏笔
- 叙事债
- 灵感池
- 章节摘要
- canon delta
- 当前连续剧情流
- 近期详细章纲
- 模型路由策略

示例：

```text
book/reader_model.yml
meta/model_policy.yml
entities/characters.yml
ledgers/narrative_debts.yml
chapters/ch001/summary.yml
chapters/ch001/canon_delta.yml
planning/active_flow.yml
planning/rolling_plan.yml
planning/current_round.yml
planning/completed_plan_log.yml
planning/future_backlog.yml
```

YAML 字段应尽量稳定，便于 agent 更新。

## 5. 推荐章节目录

```text
chapters/ch001/
  brief.md
  outline.md
  draft.txt
  final.txt
  summary.yml
  canon_delta.yml
  review.md
  context_pack.md
```

### 5.1 brief.md

写作前的本章交接说明。

包含：

- 来自 `planning/rolling_plan.yml` 的本章详细章纲摘录
- 当前 `planning/active_flow.yml` 位置
- 上一章 `handoff_to_next_chapter`
- 本章 inbound pressure、chapter turn、outbound pressure
- 本章必须发生的剧情内容
- 重要人物意图
- 禁止事项
- 下一章必须承接的外部压力或具体可见动作

### 5.2 outline.md

可选草稿。

允许记录：

- 可能的开场画面
- 对话碎片
- 局部细节
- 临时灵感
- 需要避免的写法

不允许把它写成固定结构清单并机械翻译为正文。

### 5.3 draft.txt

AI 初稿。格式遵守 TXT 正文格式。

### 5.4 final.txt

确认后的正文。格式遵守 TXT 正文格式。

### 5.5 summary.yml

章节摘要。用于快速理解章节内容；冲突时回看 `final.txt`。

建议字段：

```yaml
chapter: ch001
title: 边城雪夜
status: final
one_line_summary: ""
detailed_summary:
  - ""
characters_present:
  - ""
locations:
  - ""
key_events:
  - ""
emotional_result: ""
external_result: ""
handoff_to_next_chapter: ""
```

### 5.6 canon_delta.yml

章节造成的状态变化记录。它不是当前状态总表。

建议字段：

```yaml
chapter: ch001
new_facts:
  - ""
character_changes:
  - character: ""
    change: ""
relationship_changes:
  - pair: ""
    change: ""
world_state_changes:
  - ""
knowledge_changes:
  - topic: ""
    change: ""
foreshadowing_added:
  - id: ""
    content: ""
foreshadowing_advanced:
  - id: ""
    change: ""
foreshadowing_paid:
  - id: ""
narrative_debts_added:
  - id: ""
    description: ""
narrative_debts_advanced:
  - id: ""
    change: ""
narrative_debts_paid:
  - id: ""
ideas_added:
  - id: ""
    title: ""
handoff_to_next_chapter:
  - ""
```

## 6. 连续剧情流与近期详细章纲

`planning/active_flow.yml` 是当前跨轮连续剧情流的权威来源。

它描述的不是三章结构，而是持续推进的事件压力：从哪里承接、本章如何改变局面、下一章必须继承什么。一个 flow 可以跨过多个 round。

`planning/rolling_plan.yml` 是未来 6-15 章的权威详细章纲。

它只保存当前未来窗口，不长期保留已完成章节。已完成章纲归档到 `planning/completed_plan_log.yml`，更远期灵感和未来可能放入 `planning/future_backlog.yml`。

它不只是任务清单。每章应有 300-800 字剧情简介，并说明 `flow_id`、`flow_position`、`inbound_pressure`、`chapter_turn`、必须发生的剧情、人物意图、阻力或意外、读者回报、`outbound_pressure`、`handoff_to_next_chapter`、`external_state_at_end` 和限制。

`planning/current_round.yml` 只是从 `rolling_plan.yml` 抽取生产批次，不应另起一套互相冲突的计划，也不应包含 round 级剧情目标。

## 7. 命名规范

章节目录：

```text
chapters/ch001/
chapters/ch002/
```

卷目录：

```text
volumes/vol_001/
volumes/vol_002/
```

轮次 context pack：

```text
planning/context_packs/round_001_context_pack.md
```
