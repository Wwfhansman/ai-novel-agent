# 规则索引

本索引列出核心规则的权威定义位置。修改规则时，优先修改对应权威文件；`agents.md`、`skills/*/SKILL.md` 和 agent 配置可以保留执行摘要，但不应成为唯一完整定义。

| 规则 | 权威文件 | 位置 |
|------|---------|------|
| 唯一事实来源 | `docs/CANON_AND_SAFETY.md` | Source-of-truth table |
| 受保护文件清单 | `docs/CANON_AND_SAFETY.md` | Protected canon |
| 受保护文件修改流程 | `docs/CANON_AND_SAFETY.md` | Change Summary / checkpoint |
| 变更分级 Level 1-5 | `docs/WORKFLOWS.md` | 变更管理流程 |
| 中途变更接入 | `skills/novel-change/SKILL.md` | Mid-Story Idea Intake |
| active_flow / rolling_plan 权威关系 | `docs/CANON_AND_SAFETY.md` | Planning authority |
| handoff 字段语义 | `docs/CANON_AND_SAFETY.md` | actual_handoff / planned_handoff / current_handoff |
| Background Completion Gate | `skills/novel-write/SKILL.md` | Background Completion Gate |
| 背景落库审查 | `skills/novel-review/SKILL.md` | 执行层设定充足度 |
| 开书执行层设定包 | `skills/novel-bootstrap/SKILL.md` | 建立第一卷执行层设定包 |
| Context Pack 结构 | `docs/CONTEXT_PACK.md` | Round Context Pack |
| Writing Packet 结构 | `docs/CONTEXT_PACK.md` | Chapter Writing Packet |
| Writing Card 字段 | `templates/project/chapters/ch001/writing_packet.md` | Writing Card |
| Rolling Plan 字段 | `templates/project/planning/rolling_plan.yml` | chapter_shape_template |
| TXT 正文格式 | `docs/WRITING_CRAFT.md` | TXT / 段落规则 |
| 章末结尾规则 | `docs/WRITING_CRAFT.md` | 结尾规则 |
| 叙事织入规则 | `docs/WRITING_CRAFT.md` | 叙事织入 |
| 信息释放规则 | `docs/WRITING_CRAFT.md` | 信息释放 |
| 禁用句式和模型腔 | `docs/WRITING_CRAFT.md` | 避免的写法 |
| 模型路由 | `docs/MODEL_ROUTING.md` | 任务分工 |
| 多 agent 边界 | `docs/OPENCODE_AGENTS.md` | Agent roles |
| 记忆分层 | `docs/MEMORY_MODEL.md` | 项目记忆层 |
| 文件格式说明 | `docs/FILE_FORMATS.md` | File formats |
| validator 使用 | `scripts/README.md` | validate_novel_output |

## 维护原则

- `docs/` 保留完整解释、边界案例和设计理由。
- `skills/` 和 agent 配置保留执行时必须直接看见的硬规则摘要。
- `templates/` 保留结构契约，不能只靠文档描述。
- `scripts/validate_novel_output.py` 只覆盖可机检子集，不能替代人工审查。
