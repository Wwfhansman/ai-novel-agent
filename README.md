# AI Novel Agent

AI Novel Agent 是一套面向长篇小说创作的 agent-native 系统设计。

它的目标不是做一个普通的“AI 写作助手”，而是让 AI agent 能够从一个创作种子出发，建立小说记忆、滚动规划剧情、连续写作章节、维护人物和世界状态，并在创作过程中捕捉灵感、处理变更、复盘质量。

第一阶段不做 UI、不做 SaaS、不做复杂数据库。MVP 采用纯文件项目结构，供 Codex、DeepSeek-TUI、Claude Code 等 agent 读取和写入。

## 核心理念

传统 AI 小说写作常见问题是：单章看起来通顺，但长篇会失忆、跑偏、伏笔丢失、人物降智、读者期待无人管理。

本项目的核心假设是：

> 让 AI 写长篇小说，不能只依赖聊天上下文或向量相似度检索，而应该用结构化、半结构化的项目记忆来承载小说状态。

因此，本项目采用：

- 文件即数据库
- 结构化记忆优先
- 正文用于回看细节
- 远处读摘要，近处读原文，关键节点回看全文
- 三章一轮滚动创作
- 每章独立规划、写作、审稿、状态更新
- agent skill 约束工作流

## MVP 范围

MVP 只验证一件事：

> 结构化记忆 + agent 工作流，是否能让 AI 稳定写出可连续发展的长篇小说。

MVP 包含：

- 小说启动流程：从一个 seed 初始化新书。
- 三章一轮写作流程：每轮写 3 章。
- 分层记忆系统：全书、卷、章群、章节、实体、动态账本。
- 动态账本：叙事债务、信息可见性、角色意图、世界状态、伏笔、灵感池。
- 上下文编译：写作前产出标准化 `context_pack.md`，记录读取清单、关键理解和缺口。
- 变更管理：处理中途新想法、设定修改、大纲调整。
- 审查流程：检查节奏、人物、信息、债务、世界反应和记忆完整性。

MVP 暂不包含：

- 图形化工作台
- 多用户账号系统
- 云端同步
- 商业化付费系统
- 向量数据库
- 自动发布平台
- 读者评论反馈系统

## 文档目录

- [需求文档](docs/REQUIREMENTS.md)
- [MVP 边界](docs/MVP_SCOPE.md)
- [技术架构](docs/TECHNICAL_ARCHITECTURE.md)
- [记忆模型](docs/MEMORY_MODEL.md)
- [上下文编译](docs/CONTEXT_PACK.md)
- [正史与安全规则](docs/CANON_AND_SAFETY.md)
- [工作流设计](docs/WORKFLOWS.md)
- [文件格式规范](docs/FILE_FORMATS.md)
- [开发文档](docs/DEVELOPMENT.md)

## 推荐项目结构

```text
ai-novel-agent/
  skills/
    novel-bootstrap/
    novel-write/
    novel-review/
    novel-change/
  schemas/
  templates/
  docs/
  projects/
    my-novel/
```

每本小说项目采用独立文件夹：

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

## 关键原则

项目文件是正史，agent 对话只是临时工作台。

正文保留细节，结构化账本保存状态，滚动规划保存未来方向，灵感池保存尚未成为正史的可能性。

同一个事实出现冲突时，以明确的唯一事实来源为准：实体当前状态看 `entities/`，动态活变量看 `ledgers/`，未来意图看 `planning/`，章节事实回看 `chapters/*/final.txt` 和 `canon_delta.yml`。agent 不能用旧摘要覆盖当前状态。

上下文编译不是口头步骤。每轮写作前必须生成可复查的 context pack，写明本轮读取了哪些文件、为什么读取、哪些关键旧章节被回看、哪些信息仍不确定。

写作时不能只问“这一章是否通顺”，还要问：

- 读者还在等什么？
- 人物是否有自己的目标？
- 谁知道什么，谁不知道什么？
- 世界是否对主角行动产生反应？
- 本章是否推进、偿还或新增了叙事债务？

## 当前阶段

当前项目已经具备 MVP 文件协议骨架：

1. `skills/` 包含 4 个核心写作 skill。
2. `templates/project/` 包含可复制的空白小说项目模板。
3. `schemas/` 包含核心结构化文件字段说明。
4. `projects/example-project/` 展示脱敏示例项目。

下一步建议用一个私有项目跑通：

```text
Bootstrap 初始化
→ 第 1 轮 3 章
→ Review 冷启动检查
→ Change 插入一个中途点子
→ 持续测试到 30 章
```
