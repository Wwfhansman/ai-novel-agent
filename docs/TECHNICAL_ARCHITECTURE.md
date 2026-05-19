# 技术架构

## 1. 总体架构

MVP 采用 agent-native、本地文件优先架构。

```text
Agent
  ↓ reads skills
Skills
  ↓ operate project files
Novel Project
  ↓ contains memory, text, state
Files as Database
```

系统不要求固定模型或固定 agent。只要 agent 能读取文件、写入文件、遵守 skill 工作流，就可以使用本项目。

## 2. 仓库结构

```text
ai-novel-agent/
  README.md
  docs/
  skills/
  schemas/
  templates/
  scripts/
  projects/
```

### 2.1 skills

存放 agent skill：

```text
skills/
  novel-bootstrap/
    SKILL.md
  novel-write/
    SKILL.md
  novel-review/
    SKILL.md
  novel-change/
    SKILL.md
```

### 2.2 schemas

存放结构化文件的 schema 或字段说明。

MVP 可先使用 `.schema.yml` 文档化字段，后续再做自动校验。

### 2.3 templates

存放空白小说项目模板。

### 2.4 projects

存放实际小说项目。

## 3. 小说项目结构

```text
projects/my-novel/
  project.yml
  README.md
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

## 4. 核心模块

### 4.1 Bootstrap

输入：用户 seed。

输出：

- 创作宪法
- 初始全书摘要
- 读者模型
- 风格记忆
- 第一卷卷纲
- 初始实体库
- 初始动态账本
- 近期 9-15 章规划

### 4.2 Context Compiler

Context Compiler 是 MVP 的核心模块。

MVP 阶段不一定实现为代码，但必须实现为标准化 artifact。每轮和每章写作前，agent 必须产出 `context_pack.md`，记录读取清单、读取原因、关键理解、旧章节回看、风险和写后更新清单。

职责：

- 选择本轮要读的文件。
- 选择本章要读的文件。
- 决定是否回看旧章节原文。
- 输出写作前理解报告。
- 输出可复查的 context pack。

推荐位置：

```text
planning/context_packs/round_001_context_pack.md
chapters/ch001/context_pack.md
```

详细规范见 [上下文编译](CONTEXT_PACK.md)。

### 4.3 Writing Loop

每轮 3 章。

每章循环：

```text
读取上下文
→ 生成本章理解
→ 规划 scene beats
→ 写 draft
→ 审查
→ 改写为 final
→ 生成 summary
→ 生成 canon_delta
→ 更新账本和规划
```

### 4.4 Canon Update

负责将章节内容消化为长期记忆。

更新对象：

- `chapters/chXXX/summary.yml`
- `chapters/chXXX/canon_delta.yml`
- `entities/*`
- `ledgers/*`
- `planning/*`
- `volumes/*`

### 4.5 Review

负责审查质量和状态一致性。

可以在同一写作会话内执行，也可以每轮结束后用新会话冷启动执行。

### 4.6 Change Management

处理中途用户新点子和设定调整。

核心流程：

```text
接收变更
→ 分类影响级别
→ 检查 canon 冲突
→ 给出接入方案
→ 用户确认或 agent 推荐
→ 更新相关文件
```

## 5. 数据流

### 5.1 新书启动数据流

```text
User Seed
→ Bootstrap Skill
→ Project Files Initialized
→ Rolling Plan Created
```

### 5.2 写作数据流

```text
Project Files
→ Context Pack
→ Chapter Draft
→ Review
→ Final Text
→ Canon Delta
→ Ledger Updates
→ Next Chapter Context
```

### 5.3 变更数据流

```text
User Idea
→ Change Skill
→ Impact Assessment
→ Idea Pool / Outline / Ledger Updates
→ Future Writing Adjusted
```

## 6. 权限模型

MVP 采用 skill 约束、受保护文件清单、diff 摘要和 Git checkpoint 的组合。

详细规则见 [正史与安全规则](CANON_AND_SAFETY.md)。

### 6.1 novel-write 可以

- 创建章节草稿。
- 生成章节终稿。
- 更新章节摘要。
- 更新 canon delta。
- 更新人物当前状态。
- 更新动态账本。
- 提出灵感。

### 6.2 novel-write 不可以

- 静默修改创作宪法。
- 改变主角核心欲望。
- 擅自杀死主要角色。
- 擅自揭露终局秘密。
- 擅自改变当前卷目标。
- 静默修改受保护文件。
- 将未确认灵感直接写入正史。

### 6.3 novel-change 可以

- 评估用户变更。
- 修改局部设定。
- 调整人物关系。
- 调整近期规划。
- 提议修改创作宪法。

### 6.4 novel-bootstrap 可以

- 初始化新项目。
- 在明确重启时重建项目核心结构。

## 7. 版本和回滚

MVP 阶段建议使用 Git 作为文件数据库安全带：

- 每轮三章前建立 Git checkpoint。
- 每轮结束提交一次。
- 修改受保护文件前提交一次。
- 大规模变更后提交一次。
- 重大决策写入 `meta/decision_log` 或 `ledgers/decision_log.yml`。

Git 不是产品化依赖，但在 MVP 中是必要的回滚工具。

## 8. 未来演进

当文件系统流程验证成功后，可演进为：

- 本地 CLI
- 本地桌面工作台
- Web 工作台
- 数据库后端
- 多模型适配层
- 自动上下文编译器
- schema 校验器
- 章节导出器
