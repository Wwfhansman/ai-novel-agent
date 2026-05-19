# 文件格式规范

## 1. 总体原则

```text
正文用 txt
规则和说明用 md
结构化状态用 yml
追加日志可用 jsonl
```

## 2. txt

用于：

- 章节正文
- 草稿
- 导出全文

示例：

```text
chapters/ch001/draft.txt
chapters/ch001/final.txt
```

正文文件应尽量只包含正文，不混入任务说明、审稿意见或状态字段。

可以保留章节标题：

```text
第一章 边城雪夜

寒风卷过城墙时，林照正站在粮仓门前。
```

## 3. md

用于自然语言文档：

- 创作宪法
- 全书摘要
- 卷纲
- 卷摘要
- 章节 brief
- 章节 outline
- 上下文包
- 审稿报告
- 风格说明
- 开发文档
- skill 指令

示例：

```text
book/constitution.md
volumes/vol_001/volume_outline.md
chapters/ch001/brief.md
chapters/ch001/outline.md
chapters/ch001/context_pack.md
chapters/ch001/review.md
```

## 4. yml

用于结构化状态：

- 人物状态
- 角色意图
- 世界状态
- 信息可见性
- 伏笔
- 叙事债
- 灵感池
- 章节摘要
- canon delta
- 滚动规划

示例：

```text
book/reader_model.yml
entities/characters.yml
ledgers/narrative_debts.yml
chapters/ch001/summary.yml
chapters/ch001/canon_delta.yml
planning/rolling_plan.yml
```

YAML 字段应尽量稳定，便于 agent 更新。

## 5. jsonl

用于追加型日志。

示例：

```text
meta/session_log.jsonl
meta/change_log.jsonl
```

每行一条记录。

MVP 阶段如果不想复杂化，也可以先使用 `.md` 或 `.yml` 日志。

## 6. 推荐章节目录

```text
chapters/ch001/
  brief.md
  outline.md
  draft.txt
  final.txt
  summary.yml
  canon_delta.yml
  review.md
```

### 6.1 brief.md

写作前任务说明。

包含：

- 本章目标
- 承接上一章内容
- 本章要推进的债务、伏笔、人物、世界状态
- 本章禁止事项
- 结尾方向

### 6.2 outline.md

本章 scene beats。

包含：

- 场景列表
- 出场人物
- 冲突目标
- 信息释放
- 情绪变化
- 转折

### 6.3 draft.txt

AI 初稿。

### 6.4 final.txt

确认后的正文。

### 6.5 summary.yml

章节摘要。

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
next_hook: ""
```

### 6.6 canon_delta.yml

章节状态变化。

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
next_chapter_handoff:
  - ""
```

## 7. 命名规范

章节目录：

```text
ch001
ch002
ch003
```

卷目录：

```text
vol_001
vol_002
```

章群文件：

```text
arc_001_opening.yml
arc_002_granary_crisis.yml
```

ID 建议：

```text
debt_001
f_001
k_001
idea_001
opp_001
```

## 8. 编码

所有文本文件使用 UTF-8。
