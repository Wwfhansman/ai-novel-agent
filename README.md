# AI Novel Agent

AI Novel Agent 是一套面向长篇小说创作的 agent-native 写作框架。

它不是网页应用，也不是一键生成小说的工具。它把一本小说组织成一个文件系统项目：正文、规划、人物状态、伏笔、读者期待、信息差、世界状态和模型路由都落在可审计的文件里。Agent 负责执行工作流，项目文件负责保存长期记忆。

核心目标：

- 长篇连续写作不失忆。
- 人物、伏笔、道具、势力和世界状态不漂移。
- 每轮写作都有明确输入、输出、审查和记忆合并。
- 正文质量和工程状态分开验证。

## 架构

```text
ai-novel-agent/
  novel_engine/              ★引擎核心：状态投影、门禁、生产套件、度量（默认主干）
  skills/                    LLM 工作流：开书、写作、编剧、审查、变更
  templates/                 新小说项目模板
  scripts/                   compile_architect_context（编剧层上下文包，引擎未覆盖）
  docs/                      ENGINE / ENGINE_WORKFLOW + 编剧/安全/写作心法
  projects/
    example-project/         脱敏示例项目
```

每本小说是一个独立项目：

```text
projects/<novel-name>/
  book/                      全书层：宪法、蓝图、读者模型、风格记忆
  planning/                  规划层：编剧控制、active_flow、rolling_plan、轮次上下文
  chapters/chXXX/            章节层：packet、draft、final、review、summary、delta
  entities/                  当前实体状态：人物、势力、地点、物品
  ledgers/                   动态账本：伏笔、叙事债、信息差、世界状态
  style/                     样本文风、改写规则、禁用短语
  meta/                      模型路由、项目状态、会话日志
```

## 核心流程

正史是事件日志 `events/`，当前状态由事件**派生**。写一章的流程：

```text
events/  （append-only 正史）
   │  投影（reducer，确定性）
   ▼
当前状态（entities/ledgers，派生、只读）
   │
   ▼  kit：给 writer 一份 entering-state + 逐场规格 + 文风范例
逐场写正文 → 缝合 → chapters/chNNN/final.txt
   │
   ▼  把本章 canon 变化记成事件
events/chNNN.yml
   │
   ▼
check（schema + 引用/时序完整性 + 账本健康 + 结构）
   │
   ▼
commit（门禁通过 → 物化派生 entities/ledgers）
```

因为状态是算出来的，"变化日志说 X 但当前状态是 Y" 这类漂移**构造上不可能发生**。长篇靠望远镜结构维持（远处摘要、近处原文、按需检索），每写一章引擎都从文件重新算出 entering-state，长对话也不会记混。

## 引擎做记账，skill 做创作

新版本的分工很简单：

- **`novel_engine`（确定性代码）** 负责一切机械活——状态投影、连续性、门禁、度量、生产套件。不写正文、不判断好坏。
- **skill（LLM）** 负责创作判断：
  - `novel-bootstrap`——从一句 seed 生成故事 DNA（宪法/蓝图/初始人物/第一卷章纲）。
  - `novel-engine-write`——**默认写作流程**：场景级正文 + events 正史 + check/commit。
  - `novel-architect`——编剧层：撑大世界、安排支线、控制节奏和成长预算。
  - `novel-review`——质量与连续性审查。
  - `novel-change`——中途改设定/加反转/变更管理。

模型路由按角色分（见 [模型路由](docs/MODEL_ROUTING.md)）：正文、剧情方向、canon 决策用强模型；机械诊断可用轻量模型。

## 事实来源（引擎模型）

冲突时按这个顺序判断：

```text
chapters/chXXX/final.txt          正文事实最高权威（原文细节）
events/chXXX.yml                  本章造成的 canon 变化（append-only 正史）
entities/*.yml + ledgers/*.yml    当前状态——★由 events 派生（commit 物化），不手写
planning/rolling_plan.yml         未来近期章纲（编剧层维护）
agent 对话                         临时工作台，不是正史
```

- **`events/` 是变化的权威**；当前状态是它的投影，不存在独立的"当前状态权威"需要手工同步。
- `entities/`、`ledgers/` 是**派生产物**：`commit` 从 events 算出来写盘，手工改会被覆盖。
- 进入每章的状态由 `kit` / `context` 从 events 现算，不靠对话记忆。
- 旧项目里的 `summary.yml` / `canon_delta.yml` 仍可作为人类可读记录，但**引擎以 `events/` 为准**。

## 怎么用（在 agent 工作台里，对它说话就行）

**你不用敲任何命令。** 你只跟 agent 说人话，它在后台读章纲、写正文、存文件、记账、跑校验。你只管读它写出来的章节，满意就继续，不满意就告诉它怎么改。

常见的几句话：

| 你想做什么 | 对 agent 说 |
|-----------|------------|
| 开一本新书 | `用这个点子开一本新书：「一个年轻修灯人发现城市里的灯会保存被遗忘的记忆」` |
| 写下一章 | `写下一章`（或 `继续写` / `写 ch004`） |
| 检查质量 | `检查一下最近三章` |
| 加反转 / 改设定 | `我想给主角加个反转——他父亲其实还活着` |
| 开发后续剧情、扩展世界 | `帮我把后面 10 章的剧情和世界铺开` |

就这些。第一次开书时 agent 会问你几个方向让你挑，之后每次说"写下一章"它就接着往下写。

> 想自己跑命令、或了解底层怎么运转的，看下面的"引擎核心"和 [docs/ENGINE_WORKFLOW.md](docs/ENGINE_WORKFLOW.md)。**正常写作完全用不到。**

## 进阶：手动命令（正常写作用不到，agent 会自己跑）

以下命令给开发者或想手动操作的人。普通写作只要对 agent 说话即可。完整命令表见下文"引擎核心"。

```bash
python -m novel_engine init   projects/my-novel                  # 新书：种初始状态
python -m novel_engine kit    projects/my-novel --chapter chNNN  # 一章生产套件
python -m novel_engine check  projects/my-novel                  # 统一门禁（schema+完整性+健康+结构）
python -m novel_engine commit projects/my-novel                  # 通过则物化派生状态
python -m novel_engine structure projects/my-novel               # 追读性/防缩水报告
python3 -m unittest discover -s novel_engine/tests -t .          # 跑内核测试
```

编剧层仍用脚本编译上下文包（architect 用）：

```bash
python3 scripts/compile_architect_context.py projects/my-novel --init-missing
```

## 写作规则摘要

- 当近期规划变薄、世界缩小、支线断供或主角成长过密时，先运行 `novel-architect`，不要让 writer 临时发明关键背景。
- 每章用 `kit` 取 entering-state + 逐场规格再写，不靠对话记忆。
- 正文场景级写：先写够感官/情绪/织入，`one_change` 只是小料；章末留外部动作交接，不靠主角复盘收尾。
- `final.txt` 是正史正文。本章 canon 变化记进 `events/chNNN.yml`（机械变化用类型化事件，叙事性用 note）。
- 写完跑 `check`（schema+完整性+健康+结构+记漏）→ 通过后 `commit` 物化派生状态。
- 不手写 `entities/`、`ledgers/`——它们由 `commit` 从 events 派生。

## 项目文件说明（引擎模型）

```text
events/                  ★正史：append-only 事件日志
  bootstrap.yml          初始人物/势力/地点/物品/债务/伏笔/信息差
  chXXX.yml              本章造成的 canon 变化
chapters/chXXX/
  final.txt              正史正文
  _kit/                  kit 生成的逐场写作套件（prompt/缝合/events 模板/步骤）
entities/ + ledgers/     ★派生产物（commit 物化）：characters/factions/locations/items/
                         power_system + narrative_debts/foreshadowing/knowledge_state/world_state
planning/                编剧层（手维护）：rolling_plan / story_architecture / thread_board /
                         development_packs / context_packs / future_backlog
book/ style/ meta/       全书设定、文风、模型路由（开书时由 novel-bootstrap 建）
```

## 文档入口

新版本（引擎）：

- [确定性正史内核 novel_engine](docs/ENGINE.md)
- [引擎化写作流程](docs/ENGINE_WORKFLOW.md)

引擎未覆盖的层（开书/编剧/改设定/审查，仍在用）：

- [编剧层设计](docs/STORY_ARCHITECTURE.md)
- [正史与安全规则](docs/CANON_AND_SAFETY.md)
- [写作心法](docs/WRITING_CRAFT.md)
- [模型路由策略](docs/MODEL_ROUTING.md)

历史/已归档（描述被引擎取代的旧流程，勿照其执行）：

- [工作流设计（旧）](docs/WORKFLOWS.md)
- [历史方案归档](docs/archive/README.md)（含旧记忆模型、旧文件格式）

## 引擎核心（novel_engine）

`novel_engine/` 是新版本的**生产主干与一致性内核**（默认流程即基于它，见上文"快速开始"）。它与旧 `scripts/` 以**绞杀榕**方式并存：旧代码零回归，未迁移项目仍可用旧流程。

它修的根本问题是：旧系统让 LLM **手工维护**本该被推导的状态（`canon_delta` 写变化，又手工折叠进 `entities/ledgers`，再用正则检查一致性），而那套正则只能检查"格式齐不齐"，检查不了"内容对不对"。内核的判断是：

> **正史 = append-only 事件日志；当前状态 = 事件的投影。该推导的不手写，该 schema 的不正则。**

因为状态是算出来的，"`canon_delta` 说 X 但 `entities/` 是 Y" 这类漂移**构造上不可能发生**。

命令：

```bash
python -m novel_engine check        <project>                 # 一轮收尾统一门禁（schema+完整性+健康+结构）
python -m novel_engine commit       <project>                 # 门禁通过则物化派生 entities/ledgers
python -m novel_engine validate    <project>                  # 事件 schema 校验 + 引用/时序完整性
python -m novel_engine project     <project>                  # 打印由事件推导出的当前状态
python -m novel_engine health      <project>                  # 逾期债务 / 沉睡伏笔（结构引擎种子）
python -m novel_engine context     <project> --chapter chNNN  # 写某章时 writer 拿到的 entering-state
python -m novel_engine materialize <project>                  # 由事件渲染出 entities/ledgers 文件
python -m novel_engine structure   <project>                  # 追读性/防缩水报告（节奏/张力/世界/弧线）
python -m novel_engine init        <project>                  # 新书：种 events/bootstrap.yml（初始状态）
python -m novel_engine shadow      <project>                  # 派生 vs 手写 的漂移（只读）
python -m novel_engine migrate     <project>                  # 旧项目(已写章节)一次性转成 events/
python -m novel_engine patterns    <file>                     # 扫 AI 腔句式（profile 驱动）
python -m novel_engine compare     <file_a> <file_b>          # 两段正文文风对比 + divergence 分数
python -m novel_engine txt         <file>                     # TXT 格式/段落密度检查（profile 驱动）
python -m novel_engine kit         <project> --chapter chNNN  # 一章生产套件（逐场 prompt+缝合+events 模板+步骤）
python -m novel_engine scene       <project> --chapter chNNN  # 每场写作包（entering-state+场景规格+检索范例+约束）
python -m novel_engine experiment  <project> --chapter chNNN  # 场景级 vs 章级 A/B 实验包
```

开新书 / 逐章生产的完整流程见上文"快速开始"、[引擎化写作流程](docs/ENGINE_WORKFLOW.md) 与 skill `skills/novel-engine-write/`。

`shadow` 在脱敏示例项目上立刻抓到一处真实漂移：ch001 的 `canon_delta` 声明埋下伏笔 `f_002`，但手写的 `ledgers/foreshadowing.yml` 里从没记录它——旧 validator 抓不到的跨文件派生漏项，reducer 自动抓到。`migrate` 之后再跑 `context --chapter ch002`，`f_002` 会自动回到 writer 的 entering-state——因为状态改为派生，漏项不复存在。

运行内核测试：

```bash
python3 -m unittest discover -s novel_engine/tests -t .
```

完整设计、事件词汇表和迁移路径见 [确定性正史内核](docs/ENGINE.md)；引擎化的一轮写作流程见 [引擎化写作流程](docs/ENGINE_WORKFLOW.md)。

## 仓库安全

这个仓库保存创作系统，不保存你的私人小说。

默认 `.gitignore` 会忽略真实项目：

```gitignore
/projects/*
!/projects/.gitkeep
!/projects/example-project/
!/projects/example-project/**
```

如果真实小说需要 Git checkpoint，建议放在单独的私有仓库，或明确调整 ignore 规则。

## License

当前尚未选择开源许可证。

在添加许可证之前，本仓库是 public source-available，但还不是正式开源授权项目。如果希望外部用户复用或贡献，建议先选择 MIT、Apache-2.0 或其他许可证。
