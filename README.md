# AI Novel Agent

AI Novel Agent 是一套面向长篇小说创作的 agent-native 写作框架。

它不是网页应用，不是 SaaS，也不是“一键生成小说”的玩具。它是一套基于文件系统的创作操作系统，让 AI agent 可以围绕一部长篇小说持续完成启动、规划、写作、审稿、记忆更新和中途变更管理。

当前版本是 MVP 协议骨架，包含 skills、templates、schemas、文档和一个脱敏示例项目。

## 为什么需要这个项目

普通 AI 小说写作很容易遇到这些问题：

- 单章看起来通顺，但长篇连续写作会失忆。
- 人物状态漂移，角色行为变成服务剧情的工具。
- 伏笔、反转、读者期待没人长期管理。
- 世界只在主角出现时才运转。
- 聊天记录变成隐形记忆层，换一个会话就断。
- 基于相似度的 RAG 很容易检索到“文字相似但叙事无关”的内容。

AI Novel Agent 的核心想法是：

> 小说项目本身就是记忆系统。

与其把前文当成一大坨文本去检索，不如把长篇小说拆成分层项目文件：全书约束、卷状态、章节摘要、章节变化、人物状态、叙事债务、信息可见性、世界状态、滚动规划和灵感池。

## 核心理念

### 文件即数据库

每本小说都是一个独立项目目录。项目文件是正史和长期记忆，agent 对话只是临时工作台。

```text
projects/my-novel/
  book/
  volumes/
  arcs/
  chapters/
  entities/
  ledgers/
  planning/
  style/
  meta/
```

### 结构化记忆优先

本项目不把向量相似度检索作为主记忆方式，而是优先使用结构化和半结构化文件：

- `entities/characters.yml` 记录人物当前目标、意图、信息状态和关系。
- `ledgers/narrative_debts.yml` 记录读者正在等待什么。
- `ledgers/knowledge_state.yml` 记录谁知道什么、谁误解什么。
- `ledgers/world_state.yml` 记录世界压力、势力行动、资源和后果。
- `planning/active_flow.yml` 记录当前跨轮连续剧情流，是章节连贯性的权威来源。
- `planning/rolling_plan.yml` 记录未来 6-15 章的详细章纲，是近期剧情规划的权威来源。
- `meta/model_policy.yml` 记录强模型/快模型的任务分工，避免为了省钱牺牲正文和正史质量。

章节正文仍然完整保存，但主要用于需要精确细节时回看，而不是作为唯一记忆来源。

### 写作前必须生成 Context Pack

agent 正式写正文之前，必须先生成可复查的 `context_pack.md`。

Context Pack 记录：

- 读取了哪些文件
- 为什么读取
- 读出了什么
- 哪些旧章节需要回看
- 当前叙事债务
- 角色意图
- 信息可见性
- 世界压力
- 本章禁止事项
- 写完后必须更新哪些文件

这让写作输入变得可审计、可复现，也方便判断问题到底出在“前文理解”还是“正文生成”。

Context Pack 不是把项目资料全文复制一遍。正确方式是：

```text
rolling_plan.yml 每轮全文读取
active_flow.yml 每章读取
上一章 final.txt 精读
最近几章 summary 快速回顾
人物、物品、伏笔、债务、知识状态按本章涉及对象定向读取
久远章节只在回收伏笔、旧台词、旧物品、重大秘密时回看原文
```

推荐预算：

```text
round context pack: 3000-5000 中文字
chapter context pack: 1000-2500 中文字
```

也就是说，agent 应该像人类作者一样拥有“工作记忆”，而不是每章重新复制整个资料库。

### Active Flow：连续剧情流

默认一轮仍然可以写 3 章，但 **3 章只是生产批次，不是叙事单位**。

真正决定章节如何连续的是：

```text
planning/active_flow.yml
```

`active_flow.yml` 记录当前正在运动的剧情压力、上一章留下的可见切口、本章应继承的外部压力，以及下一章必须接住的具体交接。

因此章节不应该写成：

```text
本章发生了一些事
主角思考总结
主角决定下一步
本章结束
下一章重新开头
```

而应该写成：

```text
上一章的外部压力仍在
本章让局面发生不可逆变化
压力没有被主角复盘消化掉
下一章从一个具体动作、后果、物件、关系变化或信息差继续
```

每章规划必须关注四个连续性字段：

- `inbound_pressure`：这一章从上一章继承了什么外部压力。
- `chapter_turn`：这一章让局面发生了什么不可逆变化。
- `outbound_pressure`：这一章结束后还有什么压力没有消失。
- `handoff_to_next_chapter`：下一章必须承接的具体时刻、后果、动作、物件、关系变化或信息差。

### 正史安全规则

本项目定义了唯一事实来源规则。

例如：

- 章节正文事实看 `chapters/chXXX/final.txt`。
- 单章变化记录看 `canon_delta.yml`。
- 人物当前状态看 `entities/characters.yml`。
- 世界当前状态看 `ledgers/world_state.yml`。
- 当前连续剧情流看 `planning/active_flow.yml`。
- 未来详细章纲看 `planning/rolling_plan.yml`。
- 本生产批次只看 `current_round.yml` 作为执行摘录，不把它当作叙事单位。

`canon_delta.yml` 是章节变化日志，不是当前状态总表。

### 模型路由：把钱花在刀刃上

长篇写作的 token 成本很高，所以本项目支持模型角色分工：

```text
premium_model: 创意、长上下文理解、章纲、正文、重大变更、最终质量门禁
fast_model: YAML 检查、TXT 格式修复、脚本报错整理、session log、diff 摘要
```

`fast_model` 可以帮你省成本，但不能直接决定剧情方向、修改 protected files、写 `final.txt`，也不能单独把内容合并进 canon。

项目级配置放在：

```text
meta/model_policy.yml
```

详细规则见 [模型路由策略](docs/MODEL_ROUTING.md)。

## 项目包含什么

```text
ai-novel-agent/
  docs/                 项目设计和协议文档
  skills/               agent 写作工作流
  schemas/              结构化记忆字段说明
  templates/            空白小说项目模板
  projects/
    example-project/    最小脱敏示例项目
  scripts/              未来自动化脚本入口
```

### 四个核心 Skill

- `novel-bootstrap`：从一个创作 seed 初始化新书。
- `novel-write`：按三章一轮生产文件，但以跨轮 active flow 驱动连续剧情，生成 context pack、正文、摘要、canon delta，并更新记忆。
- `novel-review`：冷启动审查、连续性检查、唯一事实来源检查和质量审稿。
- `novel-change`：处理中途新点子、设定修改、大纲调整和 retcon。

### 小说项目模板

`templates/project/` 提供完整空白项目结构，包括：

- 全书层记忆
- 卷层记忆
- 章群/事件链
- 章节文件
- 实体状态
- 动态账本
- 滚动规划
- 风格记忆
- 模型路由策略
- 元信息和 checkpoint 占位

### 示例项目

`projects/example-project/` 是一个极小的脱敏示例项目，用来展示文件协议，不承载真实长篇内容。

真实小说项目默认不应该提交到公开仓库。当前 `.gitignore` 会忽略 `/projects/*`，只保留 `projects/example-project/`。

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/Wwfhansman/ai-novel-agent.git
cd ai-novel-agent
```

### 2. 创建一个私有小说项目

复制空白模板：

```bash
cp -r templates/project projects/my-novel
```

Windows PowerShell：

```powershell
Copy-Item -Recurse templates/project projects/my-novel
```

`projects/my-novel` 默认会被 Git 忽略。

### 3. 让 agent 使用对应 Skill

初始化新书：

```text
Use skills/novel-bootstrap to initialize projects/my-novel from this seed:
"一个年轻修灯人发现城市里的灯会保存被遗忘的记忆。"
```

继续写作：

```text
Use skills/novel-write to write round 001 for projects/my-novel.
```

冷启动审查：

```text
Use skills/novel-review to cold-start review projects/my-novel.
```

处理中途新点子：

```text
Use skills/novel-change to evaluate this idea and integrate it safely:
"主角的父亲可能已经成为灯塔记忆核心的一部分。"
```

## 常用提示词模板

下面的模板可以直接复制给支持文件读写的 agent 使用。把 `projects/my-novel` 换成你的真实项目路径。

### 初始化新书

```text
Use skills/novel-bootstrap to initialize projects/my-novel from this seed:

【类型/题材】
填写小说类型，例如都市异能、玄幻升级、科幻悬疑、古代权谋。

【初始设定】
填写一句或几句话的故事种子。

【主角印象】
填写主角身份、欲望、困境或一个你喜欢的人物画面。

【读者爽点】
填写希望读者持续追读的核心快感。

要求：
- 不要复用 templates、docs、example-project 里的任何人名、地名、组织、道具或剧情。
- 初始化 book、volumes、entities、ledgers、planning、style、meta。
- 创建或更新 meta/model_policy.yml；如果我没指定模型，就使用 premium_model / fast_model 占位符。
- 必须创建 planning/active_flow.yml。
- 必须创建 planning/rolling_plan.yml，覆盖未来 9-15 章。
- planning/current_round.yml 只能是生产批次摘录，不能写 round 级剧情目标。
- 不写正文，除非我明确要求继续进入 novel-write。
```

### 写下一轮 3 章

```text
Use skills/novel-write to continue projects/my-novel.

目标：
- 写下一个生产批次，默认 3 章。
- 遵守 meta/model_policy.yml：正文、active_flow、rolling_plan、canon 最终合并必须由 premium_model 或人类确认。
- fast_model 只可用于 YAML 检查、TXT 空行修复、脚本报错整理、session log、diff 摘要等低风险任务。
- 先编译 round context pack，再逐章编译 chapter context pack。
- 每轮必须全文读取 planning/rolling_plan.yml，但 context pack 只摘录本批次、相邻章节和影响本批次的后续约束。
- round context pack 控制在 3000-5000 中文字；chapter context pack 控制在 1000-2500 中文字。
- 人物、物品、伏笔、债务、knowledge_state、world_state 按本章涉及对象定向读取，不要整份复述。
- 每章都必须从上一章 handoff_to_next_chapter 或 active_flow 的外部压力中长出来。
- 不要把这一轮 3 章写成一个独立小故事。
- 不要让最后一章因为 round 结束而复盘、总结、收束或战略规划。

写作要求：
- 正文写入每章 final.txt。
- TXT 正文标题后空一行，正文普通段落之间不要空行。
- 正文必须正常分段：2000-3500 中文字章节通常 25-60 个正文段落，多数段落 40-160 字；超过 220 字应考虑拆分，超过 360 字通常视为格式失败。
- 结尾避免主角总结、分析、决定下一步。
- 结尾必须留下具体的 handoff_to_next_chapter。
- 每章写完必须运行：`python scripts/validate_novel_output.py projects/my-novel --chapters chXXX --fix-format`。
- 如果脚本报告 reflective ending、short atmosphere ending、protagonist thought ending，必须重写结尾后重新运行。
- 写完每章后更新 summary.yml、canon_delta.yml、entities、ledgers、volumes、planning/active_flow.yml、planning/rolling_plan.yml。
```

### 只写下一章

```text
Use skills/novel-write to write only the next chapter for projects/my-novel.

要求：
- 读取 planning/active_flow.yml。
- 确认本轮已经全文读取 planning/rolling_plan.yml；本章 context pack 只摘本章条目、前后相邻条目和必要后续约束。
- 读取上一章 final.txt、summary.yml、canon_delta.yml。
- 按需读取本章涉及的人物、物品、伏笔、债务和信息可见性条目。
- 如果上一章有 handoff_to_next_chapter，本章开头必须承接；如果不承接，必须在 context_pack.md 和 review.md 说明原因。
- 写作时不要机械翻译章纲，不要生成固定三段式或任务报告式正文。
- 写完必须运行：`python scripts/validate_novel_output.py projects/my-novel --chapters chXXX --fix-format`。
- 写完后更新本章记忆和 active_flow。
```

### 冷启动审查

```text
Use skills/novel-review to cold-start review projects/my-novel.

请只依靠项目文件判断：
- 新 agent 能否理解当前故事讲到哪里。
- active_flow 是否能说明当前连续剧情流。
- rolling_plan 是否足够支撑下一批次写作。
- current_round 是否只是生产摘录，没有隐藏 round 级剧情目标。
- 最近章节是否像独立容器，尤其是否在章末主角复盘、总结、规划。
- final.txt 是否遵守 TXT 格式。
- entities、ledgers、volumes、planning 是否与最近章节同步。

输出：
- Overall status: pass / pass with risks / fail
- Biggest risks
- Required fixes
- Suggested fixes
- Stale or conflicting files
- Whether model routing was safe: did any fast_model output enter final prose or canon without premium/human confirmation?
```

### 迁移旧项目到 Active Flow 格式

如果项目是在旧版协议下写过的，先跑这个，不要直接进入下一轮写作：

```text
Use skills/novel-review and skills/novel-change to migrate projects/my-novel to the current active-flow writing protocol.

任务：
- 先运行：python scripts/validate_novel_output.py projects/my-novel --chapters <latest chapters>
- 清理 planning/rolling_plan.yml 中的旧字段：goal、continuity_from_previous、bridge_to_next、next_hook、结尾方向、情绪节奏、本轮目标。
- 把未来章节全部改成 active-flow 字段：flow_id、flow_position、inbound_pressure、chapter_turn、outbound_pressure、handoff_to_next_chapter、external_state_at_end。
- 把 planning/current_round.yml 改成生产批次摘录，不写 round 级剧情目标。
- 把最近 summary.yml 中的 next_hook 改成 handoff_to_next_chapter。
- 检查最近 3 章 final.txt 的 TXT 空行、复盘式结尾、短句氛围结尾。
- 不要继续写新章节，直到迁移和验证通过。
```

### 接入中途新点子

```text
Use skills/novel-change to evaluate this idea for projects/my-novel:

【新点子】
填写你的新反转、新人物、新设定、新爽点或想改的内容。

要求：
- 先判断 Level 1-5 影响级别。
- 不要默认重启全书。
- 不要直接改 protected files。
- 判断它应该进入 idea_pool、foreshadowing、rolling_plan、active_flow、entities、ledgers，还是需要用户确认。
- 如果会影响已写正文，列出影响范围和是否需要补铺垫。
```

### 针对正文质量重写

```text
Use skills/novel-review to inspect the latest written chapters in projects/my-novel, then propose concrete fixes.

重点检查：
- 是否像流水账或大纲扩写。
- 是否每章独立开头、独立结尾，缺少跨章连续性。
- 是否章末总是主角思考、总结、规划。
- 是否最后一段是空泛氛围句或短句钩子。
- 是否段落之间错误地空行。
- 是否因为误解 TXT 规则而把正文写成 7-9 个巨大段落。
- 是否缺少外部状态变化和 reader reward。
- 运行 `python scripts/validate_novel_output.py projects/my-novel --chapters <latest chapters> --fix-format`，并把失败项作为必须修复项。

如果需要重写，请先说明问题，再用 skills/novel-write 的规则重写对应章节，并同步更新记忆文件。
```

## 推荐工作流

```text
从 seed 启动
→ 初始化项目记忆
→ 建立 active_flow 连续剧情流
→ 规划未来 9-15 章
→ 写一轮 3 章
→ 生成 round/chapter context pack
→ 写 draft/final 正文
→ 生成 summary 和 canon_delta
→ 合并当前状态到 entities、ledgers、planning
→ 冷启动审查
→ 继续写作或进入变更管理
```

默认生产批次是一轮三章，但三章不是叙事单位。每一章都必须从上一章外部交接里长出来，并把具体压力交给下一章；每一章都必须独立生成 context pack 并独立更新记忆。

## 文档

- [需求文档](docs/REQUIREMENTS.md)
- [MVP 边界](docs/MVP_SCOPE.md)
- [技术架构](docs/TECHNICAL_ARCHITECTURE.md)
- [记忆模型](docs/MEMORY_MODEL.md)
- [上下文编译](docs/CONTEXT_PACK.md)
- [模型路由策略](docs/MODEL_ROUTING.md)
- [正史与安全规则](docs/CANON_AND_SAFETY.md)
- [工作流设计](docs/WORKFLOWS.md)
- [文件格式规范](docs/FILE_FORMATS.md)
- [开发文档](docs/DEVELOPMENT.md)

## 仓库安全

这个仓库开源的是创作系统，不是你的私人小说。

默认 `.gitignore`：

```gitignore
/projects/*
!/projects/.gitkeep
!/projects/example-project/
!/projects/example-project/**
```

如果你希望真实小说也使用 Git checkpoint，建议把真实小说项目放到单独的私有仓库，或者有意识地调整 ignore 规则。

## 当前状态

MVP 文件协议已经实现：

- `skills/` 下有四个核心 skill。
- `templates/project/` 下有空白项目模板。
- `schemas/` 下有结构化记忆字段说明。
- `projects/example-project/` 下有脱敏示例项目。
- `docs/` 下有需求、架构、记忆模型、工作流、context pack 和正史安全规则。

暂未包含：

- CLI 自动化
- Web 或桌面 UI
- 数据库后端
- 向量检索
- 多用户协作
- 发布平台集成

## 路线图

近期：

- 用私有项目跑通 30 章实验。
- 增加 YAML 结构和必需文件校验脚本。
- 增加项目创建助手。
- 增加 context pack 编译助手。
- 增加模型路由日志和成本统计模板。

后续：

- 本地工作台 UI。
- 小说导出工具。
- 可选数据库后端。
- 读者反馈接入。
- 多模型适配。

## License

当前尚未选择开源许可证。

在添加许可证之前，本仓库是 public source-available，但还不是正式开源授权项目。如果希望外部用户复用或贡献，建议先选择 MIT、Apache-2.0 或其他许可证。
