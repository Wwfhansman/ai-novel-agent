# 文件格式规范

## 1. 总体原则

```text
正文用 txt
说明、brief、review、context pack 用 md
结构化状态用 yml
追加日志可用 md / yml / jsonl
```

## 2. TXT 正文格式

详细写作心法、结尾规则、段落节奏和 draft self-check 见 `docs/WRITING_CRAFT.md`。本节只规定文件格式。

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
- 段落数按章节类型浮动：打脸/战斗章通常更短更密，种田/日常章可以稍长，悬疑/副本章按信息释放切段。面向手机阅读时宁可略密分段。
- 多数正文段落建议 40-160 中文字；超过 220 字视为格式失败，除非 review 明确说明这是刻意保留的长镜头或完整动作链。
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
  prompt.md
  draft.txt
  reader_pass.md
  final.txt
  memory_update_plan.md
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
- 上一章 `actual_handoff`（写完后记录的实际交接）
- 本章 chapter_function、pressure_curve、reader_question_flow
- 本章 current_handoff、pressure_curve、chapter_turn、planned_handoff
- 本章 core_advance：唯一核心推进、必须发生的剧情内容、必须不完成的事项
- 本章 information_release：本章只释放哪些核心新变量，哪些信息、规则、身份、资源或关系必须延后
- 本章 side_yield：除核心推进外，进入长期记忆的世界/系统质感、关系变化、资源/地位/账本变化或可复用伏笔
- 本章 叙事织入：人物日常反应、场景即时质感、关系温度波动
- 本章 density_control：织入节拍数要求、是否允许闲笔停顿
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

### 5.3 prompt.md

正文生成前的抬头纸，控制在 500 字以内。它不是审计记录，只放写作时必须盯住的即时约束：本章一句话目标、chapter_function、pressure_curve、must_happen、must_not_complete、1-2 个信息释放点、3 个叙事织入点、2-3 条文笔约束和必须避开的模型腔。

`prompt.md` 不能替代 `context_pack.md`。context pack 仍是写前证据包，负责记录读取来源、关键结论和可审计上下文。

如果 `style/samples.md` 非空，`prompt.md` 必须包含 3-5 条正向样本文风锚点，覆盖句子节奏、段落手感、描写温度、对话语感或情绪处理。样本只提供语言方法，不允许迁移样本人名、地名、剧情、专有设定或标志性桥段。不要让 prompt 只有禁止项；正向风格锚点应与禁止模型腔并列出现。

连续 draft 模式下，允许在下一章 `prompt.md` 或 `context_pack.md` 的写作自由笔记中临时记录 3-5 行 `draft_handoff_note`。它只用于保持 prose 热态承接，不是正史，不替代 `summary.yml` / `canon_delta.yml` 的 `actual_handoff`。

### 5.4 draft.txt

AI 初稿。格式遵守 TXT 正文格式。

### 5.5 reader_pass.md

draft 到 final 之间的冷读质量门，通常 300-800 字。它只看读者体验、文笔自然度、节奏松紧、人物体温和对白是否像人说话；不检查 YAML、账本或工程同步。

必须包含：

- reader：`cold_reader_subagent` / `same_agent_fallback`。如果 fallback，说明原因。
- 最值得保留的一段。如果没有，写"没有"。
- 最生硬的 3 处。
- 局部润色建议：3-5 条，只看断句、描写自然度、对话呼吸、转场和句式重复；可以给短句级改法，不整段代写，不改变剧情事实。
- 必须重写的 1-2 个局部。
- 是否允许进入 final：`pass` / `revise required`。

如果 `reader_pass.md` 输出 `revise required`，或找不到值得保留的一段，不能写入 `final.txt`。

如果 `style/samples.md` 非空，reader pass 还应检查 draft 是否贴近样本的句子节奏、段落手感、描写温度和对话语感；发现偏离时，只给局部修文建议，不改变剧情事实。

### 5.6 final.txt

确认后的正文。格式遵守 TXT 正文格式。

`final.txt` 不是 `draft.txt` 的格式整理版，而是 draft 经过自检、冷读和必要改写后的确认版。

### 5.7 memory_update_plan.md

final 确认后的记忆更新草案。它不是正史，不是当前状态文件，只用于让主控 agent 审核并合并 `summary.yml`、`canon_delta.yml`、`entities/`、`ledgers/`、`planning/` 更新。

如果由 `novel-archivist` 生成，必须包含 evidence 和 confidence；不确定项必须写入 Open Questions，不得静默猜测。

`novel-archivist` 可以直接把草案写入 `chapters/chXXX/memory_update_plan.md`，但只能写这个草案文件。它不能直接修改 `summary.yml`、`canon_delta.yml`、`entities/`、`ledgers/`、`planning/` 或任何受保护文件。

`memory_update_plan.md` 永远是草案，不得写“本章已完成的更新”“以下文件已直接更新”“已在 director 监督下直接更新”。主控合并后的结果写入 `review.md` 的工程同步段。

它也不得写“合并判断”“已合并文件”或用 ✅ 表示状态文件已经更新。archivist 只能写建议和证据；执行结果属于 `review.md`。

### 5.8 summary.yml

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
actual_handoff: ""
```

### 5.9 canon_delta.yml

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
actual_handoff:
  - ""
```

## 6. 连续剧情流与近期详细章纲

`planning/active_flow.yml` 是当前跨轮连续剧情流的权威来源。

它描述的不是三章结构，而是持续推进的事件压力：从哪里承接、本章如何改变局面、下一章必须继承什么。一个 flow 可以跨过多个 round。

`planning/rolling_plan.yml` 是未来 6-15 章的权威详细章纲。

它只保存当前未来窗口，不长期保留已完成章节。已完成章纲归档到 `planning/completed_plan_log.yml`，更远期灵感和未来可能放入 `planning/future_backlog.yml`。

### rolling_plan.yml 容量规则

`rolling_plan.yml` 只保留未来窗口，目标不超过 6000 字节。当前活跃窗口不超过 15 章条目。

容量管理策略：

- 已完成章纲立即归档到 `completed_plan_log.yml`，不要在 `rolling_plan.yml` 中保留 `status: completed` 条目。
- 活跃窗口超过 15 章时，最远端条目压缩为 100 字以内摘要，移入 `future_backlog.yml`。
- 每章 `synopsis` 应控制在 300-800 字。如果 `rolling_plan.yml` 膨胀到超过 10000 字节，validator 会发出 `ROLLING_PLAN_SIZE_LARGE` warning。
- `future_backlog.yml` 存储远期重要节拍、尚未进入 6-15 章窗口的灵感和 macro stage 转折点预期。

它不只是任务清单。每章应有 300-800 字剧情简介，并说明 `flow_id`、`flow_position`、`chapter_function`、`pressure_curve`、`reader_question_flow`、`core_advance`、`information_release`、`chapter_turn`、`side_yield`、`叙事织入`、`density_control`、`planned_handoff` 和限制。

每章应尽量只有一个核心外部推进，并明确 `must_not_complete`。`叙事织入` 用来保留人物、世界、系统和社会结构周围的织入材料：生活细节、人物反应、对话摩擦、关系温度、世界/制度/规则质感、场景物件、轻微误读、停顿、尴尬、柔软、小幽默或人物习惯。正文可以有无直接剧情功能的段落，只要它们增强人物和场景的自然感。

一般章节的 `information_release.new_core_variables` 不宜超过 1-2 个。更多真相、规则、身份、资源收益、关系变化应写入 `deferred_information` 或后续章节。

`planning/current_round.yml` 只是生产批次追踪器，只记录本轮写哪几章、状态和起止 flow；详细章纲仍以 `rolling_plan.yml` 为唯一权威。它不应复制章节规划、不应另起一套互相冲突的计划，也不应包含 round 级剧情目标。

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
