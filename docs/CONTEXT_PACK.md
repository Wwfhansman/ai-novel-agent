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
动态账本优先读当前状态
详细章纲驱动剧情
所有读取决策写入 context_pack.md
```

上下文编译的目标不是塞最多材料，而是让 agent 明确：

- 这本书现在在哪里。
- 当前卷正在解决什么。
- 最近剧情的情绪、节奏和因果承接是什么。
- 本轮必须推进哪些债务、伏笔、人物和世界状态。
- `planning/rolling_plan.yml` 中本轮三章的详细章纲是什么。
- 哪些旧章节需要回看原文。
- 哪些信息仍然不确定。

## 3. 两级 Context Pack

MVP 采用两级上下文包：

```text
Round Context Pack: 一轮三章开始前生成
Chapter Context Pack: 每章正式写作前生成
```

### 3.1 Round Context Pack

位置：

```text
planning/context_packs/round_001_context_pack.md
```

作用：

让 agent 理解本轮三章所处的全书、当前卷、当前 arc、近期剧情和详细章纲。

必须包含：

- 本轮目标
- 文件读取清单
- 全书状态理解
- 已完成卷影响
- 当前卷状态理解
- 当前 arc 状态理解
- 最近剧情理解
- 最近全文语气和情绪承接
- 动态账本摘要
- `planning/rolling_plan.yml` 中本轮三章的详细章纲
- 本轮相关旧章节回看
- 本轮风险
- 本轮后必须更新的文件
- 未确认问题

### 3.2 Chapter Context Pack

位置：

```text
chapters/ch001/context_pack.md
```

作用：

让 agent 明确这一章要写什么剧情、承接什么压力、不能违反什么，以及写完后必须更新什么。

必须包含：

- 本章来自 `planning/rolling_plan.yml` 的详细章纲
- 本章输入文件清单
- 上一章承接点
- 本章出场人物当前意图
- 本章相关叙事债
- 本章相关伏笔
- 本章信息可见性
- 本章世界压力
- 本章禁止事项
- 本章写作风险
- 本章结束后必须更新的文件

不要把 chapter context pack 写成固定 scene beats 模板。它是写作输入记录，不是正文结构脚手架。

## 4. 默认读取清单

### 4.1 每轮开始

默认读取：

```text
book/constitution.md
book/global_summary.md
book/reader_model.yml
book/style_memory.md
已完成卷的 volume_summary.md
当前卷 volume_outline.md
当前卷 volume_summary.md
当前卷 volume_state.yml
当前 arc 文件
最近 12-15 章 summary.yml
最近 3-5 章 final.txt
entities/characters.yml
entities/factions.yml
entities/locations.yml
entities/items.yml
ledgers/narrative_debts.yml
ledgers/foreshadowing.yml
ledgers/knowledge_state.yml
ledgers/world_state.yml
ledgers/idea_pool.yml
planning/rolling_plan.yml
```

如果 `planning/rolling_plan.yml` 太薄，先扩充详细章纲，再写正文。

### 4.2 每章开始

默认读取：

```text
本章 brief.md
planning/rolling_plan.yml 中本章详细章纲
planning/current_round.yml 中本章摘录
上一章 final.txt
上一章 canon_delta.yml
最近 3-5 章 final.txt
本章出场人物在 entities/characters.yml 中的条目
本章相关势力、地点、物品条目
本章相关叙事债
本章相关伏笔
本章相关 knowledge_state
本章相关 world_state
```

`outline.md` 是可选草稿，不能作为默认强制读取项，也不能作为正文结构权威。

## 5. 关键旧章节回看规则

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

## 6. 输出格式

Context pack 必须是 Markdown，便于人和 agent 阅读。

推荐模板见：

```text
templates/context_pack.md
```

## 7. 可复现性要求

每个 context pack 必须让新 agent 能回答：

- 本次写作基于哪些文件？
- 哪些文件是重点？
- 哪些旧章节被精读？
- 本轮或本章的详细章纲是什么？
- 本轮或本章的关键约束是什么？
- 哪些信息不能确定？
- 写完后需要更新哪些文件？

如果 context pack 不能回答这些问题，就视为编译不合格。
