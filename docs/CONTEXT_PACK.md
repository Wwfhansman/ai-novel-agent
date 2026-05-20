# 上下文编译

## 1. 目标

上下文编译是 MVP 的核心模块。

即使第一阶段不写代码版 compiler，也必须产出标准化 artifact：

```text
planning/context_packs/round_001_context_pack.md
chapters/ch001/context_pack.md
```

它不是 agent 心里“读过了”的隐性过程，而是可复查、可复现的写作输入记录。

## 2. 基本原则

```text
远处读摘要
近处读原文
关键旧内容回看原文
动态账本按本章涉及对象定向读取
active_flow 负责跨轮连续性
rolling_plan 全文读取，摘要输出
context_pack 只记录必要结论，不复制资料库
所有读取决策写入 context_pack.md
关键结论必须写 source_refs
```

上下文编译的目标不是塞最多材料，而是让 agent 明确：

- 这本书现在在哪里。
- 当前卷正在解决什么。
- 最近剧情的情绪、节奏和因果承接是什么。
- 当前连续剧情流从哪里来，压力要滚向哪里。
- 本批次必须推进哪些债务、伏笔、人物和世界状态。
- `planning/rolling_plan.yml` 中本批次章节的详细章纲是什么。
- 哪些旧章节需要回看原文。
- 哪些信息仍然不确定。
- 是否使用模型切换，以及哪些任务由强模型最终确认。
- 每个关键结论来自哪个项目文件。

上下文编译应该模拟人类作者的工作记忆：

```text
清楚记得：全书核心承诺、当前卷目标、当前 active_flow、未来 rolling_plan。
精读近处：上一章正文、最近几章摘要、必要时最近 2-3 章正文。
按需翻资料：本章涉及的人物、物品、伏笔、债务、世界状态和信息可见性。
触发回看：久远伏笔、旧台词、旧道具、旧场景、久未登场人物、重大秘密。
```

不要把上下文编译理解成“每章重新阅读并复述整个项目”。

## 3. Context Budget

MVP 允许 agent 自主读文件，但必须控制 context pack 的落盘体量。

推荐预算：

```text
Round Context Pack: 3000-5000 中文字
Chapter Context Pack: 1000-2500 中文字
Old Chapter Lookback Extract: 每个旧章节只摘必要事实或短摘录
```

预算规则：

- `planning/rolling_plan.yml` 每轮必须全文读取，因为未来章纲决定本批次怎么写。
- 但 context pack 只摘录本批次章节、本章前后相邻章节、以及会影响本章选择的后续规划。
- 不要把 `rolling_plan.yml` 全文复制进 context pack。
- 不要把 `characters.yml`、`knowledge_state.yml`、`world_state.yml` 等账本全文复制进 context pack。
- 只记录本章实际需要的条目和结论。
- 如果超过预算，优先删复述、背景说明和低相关账本内容，不删 handoff、active_flow、rolling_plan 本章信息、禁止事项和写后更新清单。
- 如果使用模型切换，context pack 必须记录 `model_routing`，并说明 final prose 和 canon 更新由谁做质量门禁。
- `source_refs` 不计入铺陈，不需要长引文，但必须能说明关键结论来自哪个文件。

## 4. 两级 Context Pack

MVP 采用两级上下文包：

```text
Round Context Pack: 一个生产批次开始前生成
Chapter Context Pack: 每章正式写作前生成
```

### 4.1 Round Context Pack

位置：

```text
planning/context_packs/round_001_context_pack.md
```

作用：

让 agent 理解本批次章节所处的全书、当前卷、当前 arc、当前连续剧情流、近期剧情和详细章纲。

必须包含：

- 本批次范围，不是 round 级剧情目标
- 文件读取清单
- source_refs 读取证据
- 模型路由记录
- 全书状态理解
- 已完成卷影响
- 当前卷状态理解
- 当前 arc 状态理解
- 当前 active_flow 状态理解
- 最近剧情理解
- 最近全文语气和情绪承接
- 本批次涉及的动态账本条目摘要
- `planning/rolling_plan.yml` 中本批次章节的详细章纲
- 后续 3-6 章对本批次选择的约束或伏笔方向
- 这批章节是否开始于一个已存在 flow，是否会延续到下一批
- 本批次相关旧章节回看
- 本批次风险
- 本批次后必须更新的文件
- 未确认问题

### 4.2 Chapter Context Pack

位置：

```text
chapters/ch001/context_pack.md
```

作用：

让 agent 明确这一章要写什么剧情、承接什么压力、不能违反什么，以及写完后必须更新什么。

必须包含：

- 本章来自 `planning/rolling_plan.yml` 的详细章纲
- 本章输入文件清单
- source_refs 读取证据
- 模型路由记录
- 上一章承接点
- 当前 active_flow 位置
- 本章的 inbound pressure、chapter turn、outbound pressure、handoff_to_next_chapter
- 本章出场人物当前意图
- 本章相关叙事债
- 本章相关伏笔
- 本章信息可见性
- 本章世界压力
- 本章 reader reward check
- 本章风格和 TXT 格式约束，包括段落密度
- 本章禁止事项
- 本章写作风险
- 本章结束后必须更新的文件

格式约束必须明确：正文普通段落之间不空行，但章节仍需正常分段。2000-3500 中文字章节通常应有 25-60 个正文段落，多数段落 40-160 字；超过 220 字应考虑拆分，超过 360 字通常视为格式失败。

不要把 chapter context pack 写成固定 scene beats 模板。它是写作输入记录，不是正文结构脚手架。

## 5. 读取策略

### 5.1 每轮开始

默认读取：

```text
project.yml
book/constitution.md（重点读核心承诺和禁区，可摘要）
book/global_summary.md（摘要）
book/reader_model.yml（摘要）
book/style_memory.md（摘要）
已完成卷的 volume_summary.md
当前卷 volume_outline.md
当前卷 volume_summary.md
当前卷 volume_state.yml
当前 arc 文件
planning/active_flow.yml
planning/rolling_plan.yml（必须全文读取）
book/longform_blueprint.yml（必须全文读取）
planning/completed_plan_log.yml（只在需要审计旧计划或对照偏差时读取）
planning/future_backlog.yml（只读与本批次相关或即将 promoted 的条目）
planning/current_round.yml（如果存在）
最近 12-15 章 summary.yml
最近 1-3 章 final.txt（根据连续性需要决定）
本批次涉及的人物/势力/地点/物品条目
本批次涉及的叙事债、伏笔、knowledge_state、world_state 条目
idea_pool.yml（只读 candidate/promoted 且与本批次相关的条目）
```

如果 `planning/rolling_plan.yml` 太薄，先扩充详细章纲，再写正文。

### 5.2 每章开始

默认读取：

```text
本章 brief.md
planning/rolling_plan.yml（全文已读；本章 context pack 只摘本章、前一章、后一章和必要后续约束）
planning/current_round.yml 中本章摘录
planning/active_flow.yml
上一章 final.txt
上一章 canon_delta.yml
最近 3-5 章 summary.yml
最近 2-3 章 final.txt（仅当场景、语气或动作连续时）
本章出场人物在 entities/characters.yml 中的相关条目
本章相关势力、地点、物品条目
本章相关叙事债
本章相关伏笔
本章相关 knowledge_state
本章相关 world_state
```

`outline.md` 是可选草稿，不能作为默认强制读取项，也不能作为正文结构权威。

上一章 `canon_delta.yml` 里的 `handoff_to_next_chapter` 是硬输入。非开篇章节必须承接它，或者在 context pack 和 review 中解释为什么切换场景、时间或 POV。

### 5.3 按需读取判断

每章编译 context 前，先列出本章涉及对象：

```text
人物：谁出场、谁被提及、谁的意图会影响本章？
物品：是否涉及关键道具、功法、资源、信件、账本？
地点：地点是否有规则、历史、机关、势力控制？
债务：本章新增、推进、偿还、延迟哪些读者期待？
伏笔：本章是否埋、推进、回收伏笔？
信息可见性：本章是否改变谁知道什么？
世界状态：本章外部压力来自哪个势力、资源或危机？
```

只读取这些对象相关条目。不要为“保险”读取完整账本。

## 6. 关键旧章节回看规则

以下情况必须回看旧章节原文，而不能只读摘要：

- 要回收伏笔。
- 要偿还高权重叙事债。
- 久未登场的重要人物重新出场。
- 要呼应旧台词、旧道具、旧场景。
- 要揭露或改写重要秘密。
- 要写重大关系转折。
- 要处理用户指定的旧剧情。

回看记录必须写进 context pack：

```text
回看文件：chapters/ch012/final.txt
回看原因：伏笔 f_012 首次出现，本章将推进该伏笔。
提取结论：前文只展示了异常现象，没有说明真实原因。
```

## 7. 输出格式

Context pack 必须是 Markdown，便于人和 agent 阅读。

推荐模板见：

```text
templates/context_pack.md
```

## 8. 可复现性要求

每个 context pack 必须让新 agent 能回答：

- 本次写作基于哪些文件？
- 哪些文件是重点？
- 哪些旧章节被精读？
- 本批次或本章的详细章纲是什么？
- 本章承接了哪个外部压力，又把什么具体压力交给下一章？
- 本批次或本章的关键约束是什么？
- 哪些信息不能确定？
- 写完后需要更新哪些文件？

如果 context pack 不能回答这些问题，就视为编译不合格。

关键结论必须可追溯。例如：

```text
claim: 上一章主交接是厉康鑫走入灵兽山深处
source: planning/active_flow.yml

claim: 陈家调查员已确认石板下方为空心
source: chapters/ch008/canon_delta.yml
```
