# 开发文档

## 1. 开发阶段

当前项目处于 MVP 设计和原型阶段。

优先级：

1. 文档和结构模板
2. 四个核心 skill
3. 小说项目模板
4. 手动跑通测试小说
5. 再考虑脚本和校验器

## 2. 第一版仓库结构

```text
ai-novel-agent/
  README.md
  docs/
  skills/
  schemas/
  templates/
  projects/
```

## 3. 推荐开发顺序

### 3.1 创建项目模板

创建：

```text
templates/project/
  book/
  volumes/vol_001/
  arcs/
  chapters/
  entities/
  ledgers/
  planning/
    context_packs/
  style/
  meta/
```

并放入空白模板文件。

### 3.2 编写 skill

先写 4 个：

```text
skills/novel-bootstrap/SKILL.md
skills/novel-write/SKILL.md
skills/novel-review/SKILL.md
skills/novel-change/SKILL.md
```

每个 skill 必须明确：

- 什么时候使用
- 什么时候不能使用
- 必须读取哪些文件
- 可以修改哪些文件
- 禁止修改哪些文件
- 输出什么结果

### 3.3 编写 schema

先写字段说明即可，不必马上做程序校验。

建议优先：

```text
chapter_summary.schema.yml
canon_delta.schema.yml
narrative_debt.schema.yml
knowledge_state.schema.yml
world_state.schema.yml
character.schema.yml
idea.schema.yml
context_pack.schema.yml
```

### 3.4 跑测试项目

创建一个测试小说：

```text
projects/test-novel/
```

测试流程：

```text
Bootstrap
→ 写第 1 轮 3 章
→ Review 冷启动检查
→ 写第 2 轮 3 章
→ Change 插入新点子
→ 持续到 30 章
```

## 4. Agent 使用原则

### 4.1 项目文件是唯一长期记忆

agent 对话不是正史。

每章写完必须落盘：

- 正文
- 章节摘要
- canon_delta
- 动态账本更新

### 4.2 同一会话可写三章

同一会话可以节省 token 和减少生硬感。

但每章必须独立结算，不允许依赖未写入文件的聊天记忆。

### 4.3 每轮建议冷启动审查

每轮 3 章结束后，建议新开会话运行 review。

目的：

- 测试文件记忆是否足够。
- 检查前一轮是否写偏。
- 检查下一轮规划是否合理。

## 5. 上下文编译规则

上下文编译必须产出文件，而不是只作为 agent 的内部思考。

推荐位置：

```text
planning/context_packs/round_001_context_pack.md
chapters/ch001/context_pack.md
```

每轮开始读取：

- 创作宪法
- 全书摘要
- 已完成卷摘要
- 当前卷纲和状态
- 当前 arc
- 最近 12-15 章摘要
- 最近 3-5 章全文
- 动态账本
- 关键旧章节原文

每章开始读取：

- 本章 brief
- 上章结尾或全文
- 本章出场人物状态
- 本章相关叙事债
- 本章相关伏笔
- 本章信息可见性
- 本章世界压力

读取完成后，agent 必须把读取清单、读取原因、关键结论、回看旧章节和不确定项写入 context pack。

## 6. 质量检查清单

每章审稿至少检查：

- 本章是否有明确事件。
- 主角是否主动行动。
- 冲突是否推进。
- 是否有读者反馈。
- 是否新增、推进或偿还叙事债。
- 角色行为是否符合意图。
- 信息可见性是否正确。
- 世界状态是否有反应。
- 伏笔是否处理得当。
- 结尾是否有追读动力。

## 7. 未来脚本

MVP 后可以增加：

```text
scripts/new_project
scripts/validate_project
scripts/compile_context
scripts/export_novel
scripts/check_missing_updates
```

### 7.1 new_project

根据模板创建新小说项目。

### 7.2 validate_project

检查 YAML 格式和必填字段。

### 7.3 compile_context

根据当前章节和任务生成 context pack。

### 7.4 export_novel

拼接 `final.txt` 导出整本小说。

### 7.5 check_missing_updates

检查写完章节后是否遗漏 summary、canon_delta 或账本更新。

## 8. 开发约束

MVP 阶段避免过早工程化：

- 不引入数据库。
- 不引入复杂 UI。
- 不引入向量检索。
- 不做多用户。
- 不做商业化功能。

先验证创作闭环，再做工具封装。

## 9. Git Checkpoint 规则

MVP 阶段建议使用 Git 作为回滚工具。

推荐节奏：

```text
每轮三章开始前 checkpoint
每轮三章结束后 commit
修改受保护文件前 checkpoint
大规模变更后 commit
```

推荐提交信息：

```text
checkpoint: before round 003
write: complete round 003 chapters 007-009
change: promote idea_014 into volume 001 outline
review: resolve knowledge_state conflict after ch012
```

Git 不属于未来商业产品的必需形态，但对 MVP 的文件数据库实验是基础安全带。
