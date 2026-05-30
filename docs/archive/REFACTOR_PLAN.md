# 工程重构计划

> 目标：消除文档层信息熵增，降低规则变更的同步成本，同时不破坏已有写作流程和项目。

## 设计原则

1. 规则只在一个地方完整定义（docs/），其他地方可以保留紧凑摘要但不展开解释。
2. Agent 执行上下文（agents.md、SKILL.md、.opencode/agents/*.md）中的规则条目不删除，只压缩表述——因为 LLM 不能可靠地跟踪交叉引用。
3. 人读文档（README.md、DEVELOPMENT.md 等）可以大幅去重，人类能跟链接。
4. 已有项目文件结构、validator CLI 接口、template 结构不做破坏性变更。

## 分层模型

```text
┌─────────────────────────────────────────────────────────────┐
│  docs/ — 规则正本                                            │
│  每条规则在这里有唯一完整定义（含解释、边界案例、示例）          │
│  改规则只需要改这一处                                         │
└────────────────────────────┬────────────────────────────────┘
                             │ 紧凑摘要（保留可执行规则条目，删除解释）
┌────────────────────────────┼────────────────────────────────┐
│  agents.md — agent 冷启动协议（注入 system prompt）           │
│  skills/SKILL.md — skill 操作手册（agent 执行 skill 时读取）  │
│  .opencode/agents/*.md — agent 角色配置                      │
│  保留所有规则条目，但不展开细节                                │
└────────────────────────────┬────────────────────────────────┘
                             │ 架构概览 + 文档导航
┌────────────────────────────┼────────────────────────────────┐
│  README.md — 人类入口                                        │
│  只做快速开始、架构图和文档链接导航                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 0：删除废弃文件

**风险：零。耗时：5 分钟。**

| 操作 | 理由 |
|------|------|
| 删除 `docs/novel_write_optimization_proposal.md` | 过程性文档，已无价值，用户确认可删 |
| 删除 `skills/novel-bootstrap/agents/openai.yaml` | 4 行空壳，无消费者 |
| 删除 `skills/novel-write/agents/openai.yaml` | 同上 |
| 删除 `skills/novel-review/agents/openai.yaml` | 同上 |
| 删除 `skills/novel-change/agents/openai.yaml` | 同上 |

**验证**：删除后对 example-project 跑 validator，确认输出无变化。

---

## Phase 1：人读文档整理

**风险：零（不影响 agent 行为）。耗时：2 小时。**

### 1.1 归档历史文档

新建 `docs/archive/` 目录，移入：

| 文件 | 说明 |
|------|------|
| `CHANGE_PLAN_2025.md` | 已实施的改动提案，在文件头部加 `> ⚠️ 历史文档，仅供参考` |
| `MULTI_AGENT_IMPROVEMENT_PLAN.md` | 已实施的多 agent 规划，同上 |

### 1.2 合并冗余人读文档

将 `MVP_SCOPE.md` 的内容合入 `REQUIREMENTS.md`：

- REQUIREMENTS.md 保留：项目背景、目标用户、产品定位、核心用户故事、功能需求、非功能需求、成功标准
- 从 MVP_SCOPE.md 补入：MVP 包含/不包含内容、第一轮实验目标（作为 REQUIREMENTS.md 新增 §8 MVP 边界）
- 合并完成后删除 `MVP_SCOPE.md`

### 1.3 DEVELOPMENT.md 去重

删除以下与其他 docs 完全重复的段落：

| 删除段落 | 重复来源 |
|---------|---------|
| §5 上下文编译规则（§5 全部，约 40 行） | 与 CONTEXT_PACK.md 完全重复 |
| §6 质量检查清单（约 15 行） | 与 novel-review/SKILL.md 和 WRITING_CRAFT.md 重复 |
| §9 Git Checkpoint 规则（约 20 行） | 与 CANON_AND_SAFETY.md §9 重复 |

保留：§1-4 开发阶段/仓库结构/推荐开发顺序/Agent使用原则、§7 未来脚本、§8 开发约束。

在被删除的位置加一行链接：

```markdown
详见 [上下文编译](CONTEXT_PACK.md)。
详见 [写作心法](WRITING_CRAFT.md) 和 [novel-review SKILL](../skills/novel-review/SKILL.md)。
详见 [正史与安全](CANON_AND_SAFETY.md) §9。
```

### 1.4 TECHNICAL_ARCHITECTURE.md 去重

删除 §5 数据流（约 25 行的 3 个流程图）——与 WORKFLOWS.md §2-4 重复。替换为：

```markdown
## 5. 数据流

详见 [工作流文档](WORKFLOWS.md) §2-4。
```

### 1.5 README.md 瘦身

当前 297 行，目标 ~150 行。

| 删除内容 | 理由 |
|---------|------|
| "核心流程"段的文字描述（保留流程图） | 与 WORKFLOWS.md 重复 |
| 唯一事实来源表的完整内容 | 与 CANON_AND_SAFETY.md §3 重复；改为一句话 + 链接 |
| 写作规则摘要（约 25 行） | 与 WRITING_CRAFT.md 重复 |
| 项目文件说明的完整列表（约 40 行） | 与 FILE_FORMATS.md、MEMORY_MODEL.md 重复；保留精简树状图 |
| 多 Agent 分工的完整描述 | 与 OPENCODE_AGENTS.md 重复；改为 6 行表格 + 链接 |

保留：项目一句话介绍、架构图、快速开始、常用命令、文档导航表。

### 1.6 新建规则索引

新建 `docs/RULE_INDEX.md`：

```markdown
# 规则索引

本索引列出每条核心规则的唯一权威定义位置。修改规则时只需改对应文件。

| 规则 | 权威文件 | 章节 |
|------|---------|------|
| 受保护文件清单 | CANON_AND_SAFETY.md | §6 |
| 唯一事实来源表 | CANON_AND_SAFETY.md | §3 |
| 受保护文件修改流程 | CANON_AND_SAFETY.md | §7-8 |
| 变更分级 Level 1-5 | WORKFLOWS.md | §5.2 |
| TXT 正文格式规则 | WRITING_CRAFT.md | §TXT格式规则 |
| 结尾规则 | WRITING_CRAFT.md | §结尾规则 |
| 禁用句式（不是X而是Y） | WRITING_CRAFT.md | §避免的写法 |
| Draft Self-Check | WRITING_CRAFT.md | §Draft Self-Check |
| 网文节奏规则 | WRITING_CRAFT.md | §网文节奏规则 |
| Writing Packet 结构 | CONTEXT_PACK.md | §Chapter Writing Packet |
| Writing Card 字段 | CONTEXT_PACK.md | §Writing Card |
| 上下文预算 | CONTEXT_PACK.md | §预算 |
| 交接字段语义 | CONTEXT_PACK.md | §承接规则 |
| 模型路由任务分级 | MODEL_ROUTING.md | §3 |
| 模型路由禁止降级 | MODEL_ROUTING.md | §5 |
| 记忆分层 | MEMORY_MODEL.md | §3 |
| Rolling Plan 字段 | FILE_FORMATS.md + schemas/rolling_plan.schema.yml | — |
| Summary/Canon Delta 格式 | FILE_FORMATS.md | §5.7-5.8 |
| Background Completion Gate | WORKFLOWS.md | §3.3 |
```

**验证**：人工确认每条规则在指定文件中有完整定义。

---

## Phase 2：Agent 上下文精简

**风险：低→中。耗时：2 小时。需在下一轮写作前做冷启动验证。**

### 核心策略

不删除任何规则条目。只做两件事：

1. **压缩解释**：把"为什么这条规则存在""怎么判断边界案例"的段落删除，只保留可执行的一行式规则。
2. **删除跨层重复的流程描述**：director.md 不需要复制 SKILL.md 的完整工作流步骤。

### 2.1 agents.md 精简（184 行 → ~120 行）

**删除**：

| 删除内容 | 理由 |
|---------|------|
| "核心工作流 → 新书启动"完整流程（约 5 行） | bootstrap SKILL.md 有完整版本 |
| "核心工作流 → 日常写作"完整 8 步描述（约 15 行） | novel-write SKILL.md 有完整版本 |
| 模型路由段落（约 10 行） | .opencode/agents/*.md 的 frontmatter 已指定模型 |
| 各规则的解释段落 | 只保留规则本身 |

**保留**（这些是冷启动必须直接可见的）：

- 四个 Skill 触发表
- 项目结构树
- 唯一事实来源表（紧凑版）
- 交接字段语义表（3 行）
- 关键写作约束（结尾规则、段落密度、叙事织入、信息释放——每条一行）
- 常用命令
- 注意事项 5 条

### 2.2 novel-write/SKILL.md 精简（263 行 → ~180 行）

**压缩方式示例**：

当前（约 15 行）：
```markdown
## TXT 格式规则

`draft.txt` 和 `final.txt` 必须像正常 TXT 小说正文：
- 章节标题后保留一个空行。
- 正文普通段落之间不空行，只换行。额外空行只用于明确的场景切换。
- 不要在 draft.txt 或 final.txt 中放入审稿意见...
- 仍需正常分段。段落间不空行不等于把多个动作合并成巨大段落。
- 2000-3500 中文字章节的段落数按章节类型有所不同...
- 在动作变化、说话人变化、反应落点...
- 避免没有叙事功能的密集碎行...
```

压缩为（4 行 + 链接）：
```markdown
### TXT 格式硬规则
- 标题后一空行，正文段落间不空行，场景切换可空行
- 多数段落 40-160 字，超 220 字视为格式失败
- 章末禁止空泛复盘、抽象规划、纯氛围短句
- 完整规则和推荐切分点见 docs/WRITING_CRAFT.md
```

**类似压缩的段落**：

| 段落 | 当前行数 | 目标行数 |
|------|---------|---------|
| Hard Rules 中 TXT 格式 | ~15 | 4+链接 |
| Background Completion Gate 详细 5 步 | ~20 | 5+链接 |
| Rolling Synopsis 完整字段列表 | ~15 | 5+链接 |
| Draft Self-Check 完整规则正文 | ~12 | 5+链接 |
| Cold Reader Gate 输出格式 | ~15 | 移到 FILE_FORMATS.md，此处 3 行摘要 |

**不动的部分**：

- Core Model 4 层规划权威说明
- Round Workflow 6 步骤（skill 核心）
- Writable / Protected 文件清单
- Failure Handling
- Context Budget Policy

### 2.3 novel-bootstrap/SKILL.md 精简（168 行 → ~130 行）

| 压缩内容 | 方式 |
|---------|------|
| 步骤 6-7 "必须包含"详细实体清单 | 压缩为要点 + `最低标准见 schemas/character.schema.yml` |
| Quality Gate 中的占位表达搜索列表 | 压缩为 3 行 + 链接 |

### 2.4 novel-review/SKILL.md（140 行 → ~110 行）

- 16 条必查项中，部分展开了完整判断逻辑 → 压缩为一行检查点

### 2.5 novel-change/SKILL.md（145 行 → ~130 行）

- 改动最少。交接字段语义表删除（只在 agents.md 和 CONTEXT_PACK.md 保留）

### 2.6 .opencode/agents/novel-director.md 精简（219 行 → ~150 行）

| 删除/压缩 | 方式 |
|-----------|------|
| "批量生产流程" Phase 1-4 完整步骤展开（~60 行） | 保留 Phase 标题和关键约束，删除每步细节。director 执行时读 SKILL.md |
| 受保护文件完整列表 | 压缩为一行枚举 |

**不动**：
- 核心职责列表
- 必须遵守列表
- 其他 5 个 agent 配置文件（已经精简，暂不动）

### 验证方法

1. 对 example-project 跑一次 validator，确认无影响
2. 在新 OpenCode session 中冷启动 novel-director，验证它能：
   - 正确识别当前项目状态
   - 正确调用 novel-planner 生成 writing_packet
   - 正确识别受保护文件
3. 对比改前改后的 agents.md，人工确认没有删除任何"可执行规则"

---

## Phase 3：工具链改进

**风险：低。耗时：3-4 小时。**

### 3.1 validator 模块化拆分

**关键约束**：CLI 接口完全不变。`python scripts/validate_novel_output.py` 的所有参数和输出格式保持兼容。

目标结构：

```text
scripts/
  validate_novel_output.py       ← 入口，保留 argparse 和 main()
  check_not_but.py               ← 不变
  validators/
    __init__.py
    txt_format.py                ← TXT 空行、段落密度、结尾检测
    yaml_health.py               ← YAML 解析、重复 key、旧字段残留
    chapter_completeness.py      ← 必需文件、质量门文件、reader_pass 逻辑
    planning_audit.py            ← rolling_plan 容量、active_flow 同步、completed_plan_log
    state_drift.py               ← canon_delta → entities/ledgers 漂移检测
    protected_files.py           ← 受保护文件变更可见性
    writing_packet.py            ← packet 固定标题、Writing Card 字段检查
    prose_patterns.py            ← 不是X而是Y、三连否定、元叙述、箭头/编号式
```

拆分原则：
- `validate_novel_output.py` 的 `main()` 只做 CLI 解析和结果汇总
- 每个子模块导出一个 `check_xxx(project, chapters, ...) -> (errors, warnings)` 函数
- 旧函数签名通过 import 桥接保持兼容

### 3.2 schema 校验（可选，warning-only）

新增 `--check-schema` 选项：

```bash
python scripts/validate_novel_output.py projects/xxx --chapters ch001 --check-schema
```

- 默认不启用
- 启用时只产生 warning，不产生 error
- 读取 `schemas/*.schema.yml`，检查对应 YAML 文件的 required 字段是否存在
- 不影响任何已有项目的 validator 结果

### 3.3 template 同步检查

新增独立命令：

```bash
python scripts/validate_novel_output.py --check-template
```

检查 `templates/project/` 的文件结构是否与文档声明一致。不检查已有项目。

### 3.4 smoke test

新建 `scripts/smoke_test.py`：

```python
"""
从 templates/project/ 创建临时项目
→ 注入一组最小化模拟数据（一章的 final/summary/canon_delta 等）
→ 运行 validator
→ 确认 0 errors
→ 清理临时目录
"""
```

不调用 LLM，只验证 schema/template/validator 三者一致。

### 验证

- 拆分前后对 example-project 跑 validator，diff 输出必须为空
- smoke_test.py 通过
- `--check-schema` 和 `--check-template` 不加参数时不触发

---

## Phase 4：规范化

**风险：零。耗时：30 分钟。**

### 4.1 语言策略

在 `DEVELOPMENT.md` 末尾新增：

```markdown
## 文档语言规范

- 规则正文和说明使用中文
- 文件名、字段名、目录名、CLI 命令保持英文原样
- YAML 字段值：中文叙述内容用中文，枚举值用英文
- Python 代码注释使用英文
- Skill/Agent 的 frontmatter 使用英文
```

### 4.2 未来新增文档命名

docs/ 下新增文件统一使用 `UPPER_CASE.md` 命名。已有文件不重命名。

---

## 已有项目影响评估

| Phase | 是否影响 projects/ 下已有项目 | 是否影响 agent 行为 |
|-------|-------------------------------|-------------------|
| Phase 0 删除废弃文件 | ❌ | ❌ |
| Phase 1 人读文档整理 | ❌ | ❌ |
| Phase 2 Agent 上下文精简 | ❌ | ⚠️ 轻微（压缩表述，不删规则） |
| Phase 3 工具链改进 | ❌ | ❌ |
| Phase 4 规范化 | ❌ | ❌ |

Phase 2 的风险控制：
- 所有可执行规则条目保留
- 只删除规则解释和流程细节展开
- 冷启动验证通过后才开始下一轮写作

---

## 预期效果

| 指标 | 当前 | 目标 |
|------|------|------|
| docs 文件数 | 15 | 11（1 删 + 2 归档 + 1 合并 + 1 新建索引） |
| agents.md 行数 | 184 | ~120（-35%） |
| README.md 行数 | 297 | ~150（-50%） |
| SKILL.md 总行数 | ~716 | ~540（-25%） |
| novel-director.md 行数 | 219 | ~150（-32%） |
| validator 结构 | 1×76KB | 1 入口 + 8 模块 |
| 修改一条规则需同步的文件数 | 5-7 | 1（docs）+ 可选更新摘要 |

---

## 执行顺序

```text
Phase 0  删除废弃文件                 ⏱ 5 min     → validator 回归
Phase 1  人读文档整理                 ⏱ 2 h       → 人工确认
Phase 2  Agent 上下文精简             ⏱ 2 h       → 冷启动验证 + 写作测试
Phase 3  工具链改进                   ⏱ 3-4 h     → validator 回归 + smoke test
Phase 4  规范化                       ⏱ 30 min    → 完成
```

每个 Phase 完成后提交一次 Git，保留回滚点。
