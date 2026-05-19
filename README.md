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
- `planning/rolling_plan.yml` 记录未来 9-15 章的近期路线。

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

### 正史安全规则

本项目定义了唯一事实来源规则。

例如：

- 章节正文事实看 `chapters/chXXX/final.txt`。
- 单章变化记录看 `canon_delta.yml`。
- 人物当前状态看 `entities/characters.yml`。
- 世界当前状态看 `ledgers/world_state.yml`。
- 未来计划看 `planning/rolling_plan.yml`。

`canon_delta.yml` 是章节变化日志，不是当前状态总表。

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
- `novel-write`：按三章一轮写作，生成 context pack、正文、摘要、canon delta，并更新记忆。
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

## 推荐工作流

```text
从 seed 启动
→ 初始化项目记忆
→ 规划未来 9-15 章
→ 写一轮 3 章
→ 生成 round/chapter context pack
→ 写 draft/final 正文
→ 生成 summary 和 canon_delta
→ 合并当前状态到 entities、ledgers、planning
→ 冷启动审查
→ 继续写作或进入变更管理
```

默认写作单位是一轮三章，但每一章都必须独立生成 context pack 并独立更新记忆。

## 文档

- [需求文档](docs/REQUIREMENTS.md)
- [MVP 边界](docs/MVP_SCOPE.md)
- [技术架构](docs/TECHNICAL_ARCHITECTURE.md)
- [记忆模型](docs/MEMORY_MODEL.md)
- [上下文编译](docs/CONTEXT_PACK.md)
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

后续：

- 本地工作台 UI。
- 小说导出工具。
- 可选数据库后端。
- 读者反馈接入。
- 多模型适配。

## License

当前尚未选择开源许可证。

在添加许可证之前，本仓库是 public source-available，但还不是正式开源授权项目。如果希望外部用户复用或贡献，建议先选择 MIT、Apache-2.0 或其他许可证。

