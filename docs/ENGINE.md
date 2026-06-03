# novel_engine — 确定性正史内核

`novel_engine/` 是正史一致性层的重构，采用绞杀榕（strangler-fig）策略：**新内核与旧 `scripts/` 并存，不替换、不修改旧代码**，直到迁移验证通过后再翻转。

## 1. 它修的根本问题

旧系统让 LLM **手工维护**本该被推导的状态，又用**正则**去近似校验本该有 schema 的结构：

- `canon_delta.yml`（变化）+ `entities/ledgers`（当前状态）+ `round_state_merge.py`（合并器）其实已经是一个事件溯源系统，但没承认——于是 LLM 既写事件、又手工把事件折叠进状态、再靠正则检查一致性。三份工作做一份事，最容易错的那份交给了最不可靠的执行者。
- `scripts/validators/*` 大量用正则子串匹配抽取 YAML 字段，"填个标题/占位词就能过门禁"。

`novel_engine` 把这条暗线捅破：

> **正史 = append-only 事件日志；当前状态 = 事件的投影（projection）。该推导的不手写，该 schema 的不正则。**

因为状态是**算出来的**，"`canon_delta` 说 X 但 `entities/` 是 Y" 这类漂移**构造上不可能发生**。

## 2. 新布局

```
projects/<novel>/
  events/
    ch001.yml      # 一串事件对象，或 {chapter: ch001, events: [...]}
    ch002.yml
  ...
```

`events/chXXX.yml` 是唯一可写正史。`entities/` 和 `ledgers/` 在迁移完成后降级为**只读投影**（可随时由事件重算）。

## 3. 事件词汇表

机械、可还原的变化走**类型化事件**，自动入状态。叙事性、不可机械化的变化走 `note`，挂在实体上供阅读，但**不冒充机器状态**。

| kind | 必填 | 投影效果 |
|------|------|---------|
| `fact_added` | text | 追加全局事实 |
| `character_introduced` | id, name | 创建人物实体 |
| `character_changed` | id, change | 追加 change_history，可选 `set:` 覆盖字段 |
| `relationship_changed` | a, b, to | 双向设置关系状态 |
| `knowledge_changed` | topic, holder, level | 设置信息可见性 `visibility[holder]=level` |
| `faction_introduced` / `faction_changed` | id, name / id, change | 势力实体 → `entities/factions.yml` |
| `location_introduced` / `location_changed` | id, name / id, change | 地点实体 → `entities/locations.yml` |
| `power_introduced` / `power_changed` | id, name / id, change | 力量体系 → `entities/power_system.yml` |
| `item_introduced` / `item_moved` | id, name / item, to | 道具实体/持有者 → `entities/items.yml` |
| `world_state_changed` | text | 追加世界状态变化 → `ledgers/world_state.yml` |
| `debt_opened` / `debt_advanced` / `debt_paid` | id | 债务生命周期 |
| `foreshadow_planted` / `_advanced` / `_paid` | id | 伏笔生命周期 |
| `note` | text | 自由文本，附到 scope 或全局，不入机器状态 |

`level` 枚举：`unknown / hinted / suspects / partial / knows / knows_truth`。
完整契约见 `novel_engine/schemas/event.schema.json`（真 JSON Schema，emit 期校验，不过即拒）。

## 4. 引擎命令

```bash
# 一轮收尾的统一门禁（取代 round_state_merge + validate 的收尾）
python -m novel_engine check       <project>            # schema + 引用/时序 + 健康 + 结构（只读）
python -m novel_engine commit      <project>            # 门禁通过则把状态物化为派生 entities/ledgers

# 读新 events/ 布局
python -m novel_engine validate    <project>            # schema 校验 + 引用/时序完整性
python -m novel_engine project     <project>            # 打印推导出的当前状态（JSON）
python -m novel_engine health      <project>            # 逾期债务 / 沉睡伏笔（结构引擎种子）
python -m novel_engine context     <project> --chapter chNNN   # 写某章时的 entering-state 包
python -m novel_engine materialize <project>            # 由 events 渲染出 entities/ledgers 文件
python -m novel_engine structure   <project>            # 追读性/防缩水报告（节奏/张力/世界活体/弧线）
python -m novel_engine coverage     <project>            # 记漏检测：正文里关系变了却没记 relationship_changed

# 新书：从初始 entities/ledgers 种 bootstrap 事件
python -m novel_engine init        <project>            # 写 events/bootstrap.yml（新书起点）

# 迁移旧项目（只读分析 / 一次性转换）
python -m novel_engine shadow      <project>            # 派生 vs 手写 的漂移（只读）
python -m novel_engine migrate     <project>            # 旧 canon_delta → events/（已写章节，最佳努力）

# 质量层（作用于正文文件，不依赖 events/）
python -m novel_engine patterns    <file>               # 扫 AI 腔句式（profile 驱动）
python -m novel_engine fingerprint <file>               # 文风指纹（句长节奏/对白比/标点密度…）
python -m novel_engine compare     <file_a> <file_b>    # 两段正文对比 + 单一 divergence 分数
python -m novel_engine txt         <file>               # TXT 格式/段落密度检查（profile 驱动）

# 场景级写作流水线（A/B 验证后的方法工程化）
python -m novel_engine kit         <project> --chapter chNNN   # 一章生产套件（逐场 prompt + 缝合 + events 模板 + 步骤）
python -m novel_engine scene       <project> --chapter chNNN   # 每场写作包 JSON（entering-state + 场景规格 + 检索范例 + 约束）
python -m novel_engine exemplars-init <project>                # 脚手架 style/exemplars.yml（按类型标注文风范例）
python -m novel_engine experiment  <project> --chapter chNNN   # 生成对照实验包（prompt A/B + entering-state + 评估清单）
```

一章的引擎化生产流程见 [引擎化写作流程](ENGINE_WORKFLOW.md) 和 skill `skills/novel-engine-write/`：
`kit → 逐场写 → 缝合 → final.txt → 填 events → check → commit`。

- **validate** — 每个事件按 JSON Schema 校验（`jsonschema_lite`，零依赖）；再做**引用完整性**（改一个没被引入的人物、向不存在的人揭示信息）和**时序完整性**（还一笔从没开过的债、收一个从没埋过的伏笔）。这些靠折叠事件日志计算，正则做不到。
- **project** — reducer，`project(events) → State`。确定性、可测、可重算。
- **health** — 因为债务/伏笔带着开启/埋设章节被投影出来，"这笔债超过承诺窗口还没还""这个伏笔埋了 N 章没人碰"变成**可计算事实**，而不是靠人记得检查。阈值来自 profile。
- **context** — 把状态投影到上一章为止，给 writer 一个**有界的 entering-state 包**：在场人物的当前目标/立场/关系、未偿债务（逾期会标 `overdue`）、未收伏笔、信息可见性、近期事实。这是连接一致性引擎和创作层的桥——writer 不必读全书，只拿到"目前局势"。包的体量由当前状态决定，不随书长增长。
- **materialize** — reducer 的逆向落盘：把投影状态渲染回 `entities/ledgers` 的标准文件格式。这是让这些文件**停止手工维护**的关键一步——文件是生成的，shadow 抓到的那类漂移（伏笔埋了却没进账本）从此不可能发生。默认写到 `<project>/derived/`，不覆盖手写文件；确定翻转后再用 `--in-place`。
- **shadow** — 零风险的迁移第一步：用旧 `canon_delta` 重建状态，和手写 `entities/ledgers` 对账，给出一个**漂移数字**。改动任何文件之前，先量出现状有多漂。
- **migrate** — 把旧项目一次性转换成 `events/`：从当前 `entities/ledgers` 生成 `bootstrap.yml`，从每章 `canon_delta.yml` 生成 `chXXX.yml`。最佳努力（旧格式不保留完整历史），产出的日志可通过 validate，真正的收益是此后**新章节直接追加干净的类型化事件**。

### 端到端（在脱敏示例项目上可复现）

```bash
python -m novel_engine migrate  projects/example-project   # → events/bootstrap.yml + ch001.yml
python -m novel_engine validate projects/example-project   # 通过（只有 reopen/replant 警告）
python -m novel_engine context  projects/example-project --chapter ch002
```

`context ch002` 的输出里同时包含 `f_001` 和 `f_002`——那个在旧账本里丢失的伏笔，一旦状态改为派生就自动回到 writer 的 entering-state 里。

## 5. 质量层（quality/）

质量层是"质量引擎"里**可确定性验收**的那一半。它不评判正文好不好（那仍是 LLM 的活），但它做两件可计算的事：

- **`patterns`** — profile 驱动的 AI 腔扫描（`不是X而是Y`、三连否定、箭头式认知、元叙述）。句式和上限来自 `profiles/`，不写死在代码里，因此可按体裁/语言切换。
- **`fingerprint` / `compare`** — 文风指纹：句长均值/方差、对白占比、段落形态、破折号/省略号密度。两个用途：(1) **A/B**——用一个 `divergence_score` 量化"场景级新写法 vs 旧章级写法"的差别，而不是只靠主观盲读；(2) **长篇漂移**——ch200 还像不像 ch5。指纹一致≠文笔好，但指纹漂移=声音变了。

创作层的两个契约 `schemas/scene_spec.schema.json` 和 `schemas/editor_verdict.schema.json` 用同一套 emit 期校验（`contracts.py`）：

- **scene_spec** 把"场景=经历单位而非任务单位"写进契约——经历字段（pov、情绪温度、感官锚、织入节拍、外部动作出口）必填且排在前，剧情推进 `one_change` **可为空**（纯质感场景合法）。这是从结构上压制"任务感"。
- **editor_verdict** 把冷读裁决结构化（`verdict / blockers[location,severity,why] / keepers`），编排器按字段判定能否进 final，writer 只修被点名处——取代"grep 正文里有没有 pass 这个词"。

## 6. 结构引擎（structure/）

把旧系统散落在 `cross_chapter.py` / `planning_audit.py` 里的正则检查（next_step 链、一天一任务链、world_expansion 单薄、pacing loop、成长过密）**抬成一个类型化、可计算的模型**。输入是每章结构记录（schema 校验），阈值来自 profile，全部是正向计算信号而非正则。

`structure` 命令读原生 `structure/chXXX.yml`，没有则回退从 `planning/rolling_plan.yml` 抽取（`legacy_structure.py`），并结合事件日志算弧线。它计算：

- **节奏/章型重复**（`PACING_LOOP` / `FUNCTION_LOOP`）：连续 N 章同一 pacing_mode / chapter_function。
- **世界活体干旱**（`WORLD_EXPANSION_DROUGHT` / `OFFSCREEN_PRESSURE_DROUGHT`）：连续 N 章不扩张世界、或台下势力不动——**世界缩成主角任务链**的预警。
- **张力平台**（`TENSION_FLATLINE`）：连续 N 章停在低张力位置（opening/aftermath_trough）。
- **成长过密**（`GROWTH_TOO_DENSE`）：成长章占比超预算。
- **弧线沉睡**（`ARC_STALL`，来自事件）：主要角色 N 章没有任何 `character_changed`。

在脱敏示例项目上 `structure` 报告 **clean**（节奏多变、世界每章扩张、张力曲线 2→3→3→5→1→3 有起伏）——验证它不对构造良好的章纲误报。

> 世界活体**模拟**（让 LLM 生成"主角不动时各势力做什么"）仍需 LLM；结构引擎现在负责**检测干旱并报警**，把"该跑世界 pass 了"变成可计算信号。

## 7. 体裁/语言解耦

所有体裁特定的阈值和禁用句式（段落字数、体裁段数、AI 腔正则、债务/伏笔时效）都在 `novel_engine/profiles/zh-webnovel.yml`。引擎代码体裁中立；换 profile 即可重定向到别的体裁/语言。

## 8. 真实验证：连示例项目都在漂

在脱敏的 `example-project` 上跑 `shadow`，立刻抓到一处真实漂移：

```
[unmerged]
  - FORESHADOW_NOT_IN_LEDGER: events plant/touch f_002 but ledgers/foreshadowing.yml has no entry.
```

`chapters/ch001/canon_delta.yml` 声明 ch001 埋下伏笔 `f_002`（父亲的旧修灯刀），但手写的 `ledgers/foreshadowing.yml` 里**只有 f_001、没有 f_002**。旧的正则 validator 抓不到这类跨文件派生漏项；reducer 自动抓到了。这正是整套重构论点的具体证据。

## 9. 绞杀榕迁移状态

**已交付（确定性可验收）：**

- 事件 schema + 零依赖校验器（`schemas/`、`jsonschema_lite.py`）
- 投影 reducer（`projection.py`，含 `project_through` 章节定点投影）
- 引用/时序完整性（`integrity.py`）
- 债务/伏笔时效（`ledger_health.py`，结构引擎种子）
- entering-state 上下文编译（`context.py`，连接创作层）
- 状态落盘 materialize（`materialize.py`，让 entities/ledgers 可派生）
- 旧 `canon_delta` → 事件适配器与影子对账（`legacy.py`、`diff.py`）
- 旧项目一次性迁移（`migrate.py`）
- 体裁 profile（`profiles/`）
- 质量层（`quality/`）：profile 驱动的 AI 腔扫描、文风指纹与 A/B 对比
- 创作层契约（`schemas/scene_spec`、`schemas/editor_verdict` + `contracts.py`）
- 结构引擎（`structure/`）：节奏/章型重复、世界活体干旱、张力平台、成长密度、弧线沉睡；含 rolling_plan 适配器
- 统一门禁 `check` / `commit`（`gate.py`）：一轮收尾的引擎主干，取代 round_state_merge + validate 收尾；见 [引擎化写作流程](ENGINE_WORKFLOW.md)
- TXT 格式/段落密度检查 profile 化（`quality/txt_format.py`）：旧 `txt_format` 的格式半边迁出代码、由 profile 驱动
- 文档契约测试（`tests/test_docs_contract.py`）：CLI 子命令与 `docs/ENGINE.md` 不同步即 CI 失败——防 `agents.md` 那类协议漂移
- A/B 实验包 `experiment`（`experiment.py`）：把"场景级 vs 章级"打包成可执行对照实验
- 场景级写作流水线 `scene`（`scene/`）：A/B 验证后把场景法工程化——按 `rolling_plan` 起草场景骨架、按场景类型检索文风范例、组装"每场写作包"(entering-state + 场景规格 + 范例 + 约束)
- 一章生产套件 `kit`（`kit.py`）+ `exemplars-init` + skill `skills/novel-engine-write/`：把场景法渲染成可直接写的逐场 prompt + 缝合 + events 模板 + 步骤，一条命令开箱即用（门槛 B）
- 87 个单元/集成测试，全绿；旧 `scripts/` 全程未动、无回归

**质量层尚缺（需 LLM + 人）：** 场景级 writer 实际生成正文、按类型检索范例、editor 定点修订循环，以及**新旧盲读 A/B**——这是回答"是否更好看"的唯一一步，目前可用 `compare` 给出量化信号辅助。

**后续路径（按风险递增）：**

确定性可做的部分已基本完成：一致性内核、收尾门禁、质量度量、结构检测、**场景级生产套件**和引擎驱动 skill 全部就位，一章的引擎化生产是 `kit → 逐场写 → 缝合 → 填 events → check → commit`。

**仅剩内在需要 LLM + 人的工作（引擎替不了）：**

1. **每章实际写正文**——`kit` 把材料备齐，正文仍需 LLM 逐场写、人拍板。
2. **世界活体生成**（M3）——结构引擎已能检测干旱并报警；生成"主角不动时各势力做什么"需 LLM。
3. **范例语料标注**（可选，提升文笔）——`exemplars-init` 起草骨架，按类型填真实正文需人/LLM。

完整设计动机见仓库根 `README.md` 的"重构方向"一节。

## 10. 运行测试

```bash
python3 -m unittest discover -s novel_engine/tests -t .
```
