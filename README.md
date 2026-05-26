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
  .opencode/agents/          OpenCode 多 agent 配置
  skills/                    agent 工作流：开书、写作、审查、变更
  scripts/                   校验、句式扫描、状态合并工具
  templates/                 新小说项目模板
  schemas/                   writing_packet / context_pack 结构约束
  docs/                      架构、流程、格式和安全规则
  projects/
    example-project/         脱敏示例项目
```

每本小说是一个独立项目：

```text
projects/<novel-name>/
  book/                      全书层：宪法、蓝图、读者模型、风格记忆
  planning/                  规划层：active_flow、rolling_plan、轮次上下文
  chapters/chXXX/            章节层：packet、draft、final、review、summary、delta
  entities/                  当前实体状态：人物、势力、地点、物品
  ledgers/                   动态账本：伏笔、叙事债、信息差、世界状态
  style/                     样本文风、改写规则、禁用短语
  meta/                      模型路由、项目状态、会话日志
```

## 核心流程

```text
book / entities / ledgers / planning
        │
        ▼
round context pack
        │
        ▼
writing_packet.md
        │
        ▼
draft.txt → cold read → revise
        │
        ▼
final.txt
        │
        ▼
summary.yml + canon_delta.yml + memory_update_plan.md
        │
        ▼
round_state_merge.py preview/apply
        │
        ▼
entities / ledgers / active_flow / rolling_plan 更新
        │
        ▼
post-merge QA
```

写作被分成两个闭环：

- **正文闭环**：`writing_packet.md → draft.txt → reader_pass.md → final.txt`
- **记忆闭环**：`final.txt → summary/canon_delta → memory_update_plan → merge preview → entities/ledgers/planning`

正文好不好，看正文闭环。长篇稳不稳，看记忆闭环。

## 多 Agent 分工

```text
novel-director
  ├─ novel-planner       写作前规划，生成 writing_packet.md 草案
  ├─ novel-writer        写 draft/final，不碰 canon 和状态文件
  ├─ novel-cold-reader   冷读正文体验、节奏、人物体温
  ├─ novel-archivist     生成 summary/canon/memory 草案
  └─ novel-qa            跑 validator，检查格式和流程门禁
```

推荐模型路由：

```yaml
novel-director: deepseek-v4-pro
novel-planner: deepseek-v4-pro
novel-writer: deepseek-v4-pro
novel-archivist: deepseek-v4-pro
novel-cold-reader: deepseek-v4-flash
novel-qa: deepseek-v4-flash
```

`director`、`planner`、`writer`、`archivist` 会影响剧情、正文和长期记忆，建议使用强模型。`cold-reader` 和 `qa` 主要做诊断，可以使用轻量模型。

OpenCode 配置位于：

```text
.opencode/agents/
```

在仓库根目录运行：

```bash
opencode
```

默认进入 `novel-director`。正常生产时让 director 调用其他 subagent，不需要手动反复切换。

## 事实来源

冲突时按这个顺序判断：

```text
chapters/chXXX/final.txt          正文事实最高权威
chapters/chXXX/summary.yml        本章发生了什么
chapters/chXXX/canon_delta.yml    本章造成了什么变化
entities/*.yml                    人物、势力、地点、物品当前状态
ledgers/*.yml                     伏笔、叙事债、信息差、世界状态
planning/active_flow.yml          当前连续剧情流
planning/rolling_plan.yml         未来近期章纲
agent 对话                         临时工作台，不是正史
```

`canon_delta.yml` 是变化日志，不是当前状态总表。
`active_flow.yml` 是跨章连续性的权威。
`rolling_plan.yml` 只保留未来窗口，完成章节进入 `completed_plan_log.yml`。

## 快速开始

克隆仓库：

```bash
git clone https://github.com/Wwfhansman/ai-novel-agent.git
cd ai-novel-agent
```

创建私有小说项目：

```bash
cp -r templates/project projects/my-novel
```

Windows PowerShell：

```powershell
Copy-Item -Recurse templates/project projects/my-novel
```

初始化新书：

```text
Use skills/novel-bootstrap to initialize projects/my-novel from this seed:
"一个年轻修灯人发现城市里的灯会保存被遗忘的记忆。"
```

继续写一轮：

```text
Use skills/novel-write to continue projects/my-novel.
```

审查项目：

```text
Use skills/novel-review to cold-start review projects/my-novel.
```

处理中途新点子：

```text
Use skills/novel-change to evaluate this idea for projects/my-novel:
"主角的父亲可能已经成为灯塔记忆核心的一部分。"
```

## 常用命令

校验章节：

```bash
python3 scripts/validate_novel_output.py projects/my-novel --chapters ch001
python3 scripts/validate_novel_output.py projects/my-novel --chapters ch001 --fix-format
python3 scripts/validate_novel_output.py projects/my-novel --chapters ch001 --strict
```

检查已知 AI 腔句式：

```bash
python3 scripts/check_not_but.py projects/my-novel --chapters ch001 ch002 ch003 --files draft.txt
python3 scripts/check_not_but.py projects/my-novel --chapters ch001 ch002 ch003 --files final.txt
```

生成状态合并预览：

```bash
python3 scripts/round_state_merge.py preview projects/my-novel --round round_001 --chapters ch001 ch002 ch003
```

应用安全合并项：

```bash
python3 scripts/round_state_merge.py apply projects/my-novel --preview projects/my-novel/planning/merge_previews/round_001.yml
```

## 写作规则摘要

- 每轮默认 3 章，但轮次只是生产批次，不是叙事单位。
- 每章写前必须有 `writing_packet.md`。
- `writing_packet.md` 必须包含 `Chapter Design` 和 `Writing Execution`。
- `Writing Execution` 要提供可写材料：人物语感、伏笔分量、关系温度、身体/场景质感、对话模式、scene moments、ending gesture。
- 正文先写 `draft.txt`，冷读和修订后再进入 `final.txt`。
- `final.txt` 是正史正文，不能用草稿或 review 替代。
- 章末不能靠主角复盘、总结、决定下一步收尾；要留下具体动作、后果、物件、关系变化或信息差。
- 写完后必须更新 `summary.yml`、`canon_delta.yml` 和当前状态文件。
- post-merge QA 必须在状态文件合并之后运行。

## 项目文件说明

章节目录：

```text
chapters/chXXX/
  writing_packet.md        写作输入包
  draft.txt                草稿
  final.txt                正史正文
  reader_pass.md           冷读反馈
  review.md                审查记录
  summary.yml              本章发生了什么
  canon_delta.yml          本章造成了什么变化
  memory_update_plan.md    记忆更新草案
```

规划目录：

```text
planning/
  active_flow.yml                  当前连续剧情流
  rolling_plan.yml                 未来近期章纲
  current_round.yml                当前生产批次追踪
  completed_plan_log.yml           已完成章纲归档
  context_packs/                   轮次上下文
  merge_previews/                  状态合并预览
```

长期记忆：

```text
entities/characters.yml            人物当前状态
entities/factions.yml              势力当前状态
entities/locations.yml             地点状态
entities/items.yml                 道具状态
ledgers/narrative_debts.yml        读者期待债
ledgers/foreshadowing.yml          伏笔
ledgers/knowledge_state.yml        谁知道什么
ledgers/world_state.yml            外部世界状态
ledgers/decision_log.yml           重大决策
```

## 文档入口

- [工作流设计](docs/WORKFLOWS.md)
- [OpenCode 多 Agent 配置](docs/OPENCODE_AGENTS.md)
- [文件格式规范](docs/FILE_FORMATS.md)
- [上下文编译](docs/CONTEXT_PACK.md)
- [记忆模型](docs/MEMORY_MODEL.md)
- [正史与安全规则](docs/CANON_AND_SAFETY.md)
- [模型路由策略](docs/MODEL_ROUTING.md)
- [技术架构](docs/TECHNICAL_ARCHITECTURE.md)
- [开发文档](docs/DEVELOPMENT.md)

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
