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
    model_policy.yml
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

三章一轮只是生产批次，不是叙事单位。跨章连续性以 `planning/active_flow.yml` 为权威，章节必须承接上一章外部交接并留下下一章可继承的具体压力。

### 4.3 每轮建议冷启动审查

每轮 3 章结束后，建议新开会话运行 review。

目的：

- 测试文件记忆是否足够。
- 检查前一轮是否写偏。
- 检查下一轮规划是否合理。

## 5. 上下文编译规则

上下文编译规则以 [CONTEXT_PACK.md](CONTEXT_PACK.md) 为准。

关键开发原则：

- 上下文编译必须产出文件，而不是只作为 agent 的内部思考。
- round context pack 和 chapter writing packet 是可审计的写作输入记录。
- 不要把项目资料库全文复制进 packet；只摘取本轮/本章需要的操作结论。
- 背景补全和落库门禁见 [WORKFLOWS.md](WORKFLOWS.md) 与 [novel-write skill](../skills/novel-write/SKILL.md)。

## 6. 质量检查清单

质量检查以 [WRITING_CRAFT.md](WRITING_CRAFT.md)、[CANON_AND_SAFETY.md](CANON_AND_SAFETY.md)、[novel-review skill](../skills/novel-review/SKILL.md) 和 `scripts/validate_novel_output.py` 为准。

开发时只需确认：新增流程是否有人工审查入口、可机检部分是否进入 validator、写后状态是否合并到 `entities/` / `ledgers/` / `planning/`。

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

根据当前章节和任务生成 writing packet。

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

Git checkpoint 规则以 [CANON_AND_SAFETY.md](CANON_AND_SAFETY.md) 为准。MVP 阶段仍建议在每轮生产批次、受保护文件修改和大规模变更前后建立可回滚点。

## 10. 文档语言规范

- 规则正文和说明使用中文。
- 文件名、字段名、目录名、CLI 命令保持英文原样。
- YAML 字段值：中文叙述内容用中文，枚举值用英文。
- Python 代码注释使用英文。
- Skill / agent frontmatter 使用英文。
- `docs/` 下新增文档优先使用 `UPPER_CASE.md` 命名；已有文件不强制重命名。
