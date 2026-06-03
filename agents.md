# AI Novel Agent — Agent 使用指南

## 项目概述

AI Novel Agent 是一套面向长篇小说创作的 agent-native 写作框架。它不是应用、不是 SaaS、不是"一键生成小说"的工具——而是一套基于文件系统的创作操作系统。每本小说是一个独立项目目录，项目文件是正史和长期记忆，agent 对话只是临时工作台。

**新版本以 `novel_engine` 为生产主干（默认，唯一现行流程）。** 正史是事件日志 `events/`，当前状态由事件**派生**（`entities/ledgers` 不手写、构造上不漂），写作走场景级、收尾走 `check`/`commit`。旧的写作 skill（`novel-write`）、旧校验/合并脚本均已删除——**未迁移的旧项目先 `python -m novel_engine migrate <project>` 上引擎，再按引擎流程写**。详见 [`docs/ENGINE.md`](docs/ENGINE.md) 与 [`docs/ENGINE_WORKFLOW.md`](docs/ENGINE_WORKFLOW.md)。

## 常用命令（引擎为默认）

```bash
# 新书：故事 DNA 就绪后种初始事件 → 门禁 → 逐章生产
python -m novel_engine init   projects/<name>                  # 种 events/bootstrap.yml（初始人物/债务/伏笔/信息差）
python -m novel_engine check  projects/<name>                  # 统一门禁：schema + 引用/时序 + 健康 + 结构
python -m novel_engine kit    projects/<name> --chapter chNNN  # 一章生产套件（逐场 prompt + 缝合 + events 模板 + 步骤）
python -m novel_engine commit projects/<name>                  # 门禁通过 → 物化派生 entities/ledgers
python -m novel_engine structure projects/<name>               # 追读性/防缩水报告
python -m novel_engine migrate projects/<name>                 # 旧项目(已写章节)一次性转成 events/

# 编剧层上下文包（architect 用）
python3 scripts/compile_architect_context.py projects/<name> --init-missing
```

## 核心架构

### 五个 Skill

| Skill | 用途 | 触发条件 |
|-------|------|---------|
| `novel-bootstrap` | 从 seed 初始化新书的故事 DNA（宪法/蓝图/初始实体/第一卷章纲） | 项目为空 / 用户明确开新书 / 要求重启作品 DNA |
| `novel-engine-write` | **默认写作流程**：场景级正文 + events 正史 + check/commit 门禁 | 日常写作、写下一章 |
| `novel-architect` | 编剧层：世界运营、卷节奏、支线、未来 10-30 章剧情开发 | rolling_plan 接近耗尽 / 世界缩小 / 支线断供 / 主角成长过快 / 用户要求开发后续剧情 |
| `novel-review` | 冷启动审查、质量检查、连续性验证 | 每轮结束后 / 用户要求检查质量 / 长篇出现跑偏迹象 |
| `novel-change` | 中途新点子、设定调整、变更管理 | 用户想加反转/改设定/调人物关系/改大纲 |

写作用 `novel-engine-write`（新书 `novel-bootstrap` 生成故事 DNA 后跑 `init` 再写）。`novel-architect` 编剧层、`novel-change` 变更管理仍是引擎未覆盖的层，按需使用。

### 小说项目结构

```
projects/<novel-name>/
  project.yml
  book/                           # 全书层——这本书是什么
    constitution.md               # 创作宪法（类型、卖点、读者承诺、禁止事项）★受保护
    longform_blueprint.yml        # 长篇规模蓝图（目标长度、宏观阶段、力量递进、爽点频率）★受保护
    global_summary.md             # 全书摘要
    reader_model.yml              # 读者模型
    style_memory.md               # 风格记忆（段落节奏、禁止倾向、写作常量）
    endgame_hypotheses.yml        # 终局假说（不是正史）
    chapter_rhythm_guide.md       # 网文章类型节奏参考
  volumes/vol_001/                # 卷层——这一卷承担什么功能
    volume_outline.md
    volume_summary.md
    volume_state.yml
    volume_threads.yml
    volume_debts.yml
  arcs/                           # 章群层——3-10 章小事件链
  events/                         # ★引擎正史——append-only 事件日志（当前状态由它派生）
    bootstrap.yml                 # 初始人物/势力/地点/物品/债务/伏笔/信息差（init 生成）
    ch001.yml                     # 本章造成的 canon 变化（类型化事件 + note）
  chapters/ch001/                 # 章节层
    final.txt                     # 终稿（正史正文）★唯一正文权威
    _kit/                         # kit 生成的生产套件（逐场 prompt/缝合/events 模板/步骤）
                                  # （旧项目可能还有 writing_packet/draft/summary/canon_delta 等，引擎不再产出）
  entities/                       # 实体层——人物/势力/地点/物品/力量体系
                                  # ★引擎下为派生产物（commit 物化），不要手写
    characters.yml
    factions.yml
    locations.yml
    items.yml
    power_system.yml
  ledgers/                        # 动态账本——故事中的活变量（★引擎下同为派生产物）
    narrative_debts.yml           # 叙事债务（读者正在等待什么）
    foreshadowing.yml             # 伏笔
    knowledge_state.yml           # 信息可见性（谁知道什么）
    world_state.yml               # 世界状态（外部系统的当前压力）
    idea_pool.yml                 # 灵感池（未进入正史的可能性）
    decision_log.yml              # 重大决策记录
  planning/                       # 规划层
    story_architecture.yml        # 编剧层控制台：当前卷节奏、成长、信息释放、世界扩张
    thread_board.yml              # 活跃支线、off-screen 行动、冲突网络
    active_flow.yml               # 当前跨轮连续剧情流
    rolling_plan.yml              # 未来 6-15 章详细章纲 ★唯一近期规划权威
    completed_plan_log.yml        # 已完成章纲归档
    completed_threads_log.yml     # 已完成支线归档
    future_backlog.yml            # 远期点子
    development_packs/            # novel-architect 开发包（建议快照，不是正史）
    context_packs/                # 轮次上下文编译
  style/                          # 风格层
    rewrite_rules.md              # 改写规则
    samples.md                    # 文笔风格样本
    sample_prompt.md              # 文笔风格报告生成提示词
    banned_phrases.yml            # 禁用短语
  meta/                           # 元信息
    model_policy.yml              # 模型路由策略
    project_state.yml
    session_log.md
```

### 唯一事实来源（冲突时按此判断）

引擎项目（有 `events/`）：正史是 `events/`，当前状态由其派生；下表的 `entities/ledgers` 为**派生产物**（由 `commit` 物化，不手写）。旧项目仍按下表手写。

| 事实类型 | 权威来源 | 说明 |
|---------|---------|------|
| 已发生的正文事实 | `final.txt` | 原文细节以 final.txt 为准 |
| 某章造成了什么变化 | `events/chNNN.yml` | ★append-only 事件日志，当前状态由它派生 |
| 人物/势力/地点/物品当前状态 | `entities/*.yml` | ★由 events 派生（`commit` 物化），不手写 |
| 世界局势/信息差/伏笔/债务 | `ledgers/*.yml` | ★同为派生产物 |
| 当前卷编剧控制 | `planning/story_architecture.yml` | 当前卷节奏、成长、信息释放计划；不覆盖 longform_blueprint |
| 活跃支线调度 | `planning/thread_board.yml` | 支线生命周期和 off-screen 行动计划 |
| 近期未来计划 | `planning/rolling_plan.yml` | 6-15 章详细章纲（编剧层维护） |
| 长篇规模递进 | `book/longform_blueprint.yml` | ★受保护 |

## 核心工作流

### 默认：引擎流程（新版本）

**开新书：**
```
1. 故事 DNA   novel-bootstrap 从 seed 生成（或 cp -r templates/project 手填）
2. 种事件     python -m novel_engine init <project>      → events/bootstrap.yml
3. 门禁       python -m novel_engine check <project>     → 确认初始状态干净
4. 逐章生产   见下
```

**逐章生产（引擎默认）：**
```
1. 套件   python -m novel_engine kit <project> --chapter chNNN   → chapters/chNNN/_kit/
2. 写     按 _kit/scene_prompts.md 逐场写（经历优先；one_change 小、可空；出口切外部动作）
3. 缝合   按 _kit/stitch_prompt.md 连成整章 → chapters/chNNN/final.txt
4. 自检   python -m novel_engine txt / patterns chapters/chNNN/final.txt
5. 事件   按 _kit/events.template.yml 把本章 canon 变化写进 events/chNNN.yml（类型化事件 + note）
6. 门禁   python -m novel_engine check <project>
7. 提交   python -m novel_engine commit <project>        → 物化派生 entities/ledgers
```
不要手写 `entities/ledgers`（引擎下是派生产物，commit 会覆盖）；canon 变化只记成 events。
### 旧项目搬迁（已写章节、无 events/）

旧的写作 skill 和校验/合并脚本已删除，没有"旧流程 fallback"。旧项目先上引擎再写：

```
python -m novel_engine shadow  <project>   # 看现状漂移（只读）
python -m novel_engine migrate <project>   # 旧 canon_delta → events/
python -m novel_engine check   <project>   # 验收
python -m novel_engine commit  <project>   # 物化派生状态
# 之后按引擎流程逐章写
```

### 交接字段语义（重要）

| 字段 | 位置 | 语义 |
|------|------|------|
| `planned_handoff` | `rolling_plan.yml` | 规划中期望的交接 |
| `actual_handoff` | `events/chNNN.yml`（`note` 或类型化事件） | 写完后实际造成的交接 |
| `current_handoff` | 引擎从 events 派生（`context`/`kit` 的 entering-state） | 当前最新的实际交接 |

写作时：从 `kit` 拿到上一章 entering-state（含 current_handoff）→ 参考 `planned_handoff`（本章规划）→ 写完把实际交接记进 `events/chNNN.yml`。

## 关键写作约束

### 结尾规则
- 禁止空泛反思式结尾（章末主角独自坐下空想、总结教训、抽象规划下一步）。
- 区分：主角做出具体可执行决策、推演策略揭示新信息、思考伴随外部动作——这些不在此列。
- 推荐：动作刚开始、对话被打断、有人到场、代价落地、物件易手、选择被当众做出。

### 段落密度
- TXT 正文段落间不空行。"不空行"不等于"不分段"。
- 核心规则是防"一大坨"：多数段落 40-160 字，超过 220 字视为格式失败。
- 短段落在手机上恰是优点——不要为了凑段数而合并段落。
- 按章节类型参考：打脸/战斗章通常段更短更多，种田/经营章段稍长。

### 叙事织入（对抗"每句都在推进任务"）
- 一章只有一个核心推进，但不是每一段都围绕它。
- 每章至少 3 个织入节拍：人物日常反应、场景即时质感、关系温度波动。
- 不是水文——要有人物/场景/关系的"居住感"，不需要解决章节任务。
- 连续两页纯计划/推理/分析/任务执行 → 必须放松节奏。

### 信息释放
- 每章 1-2 个读者必须记住的新核心变量，其余延后到后续章节。
- 规则/制度/功法通过事件、代价、误用或反应验证，不连续多段旁白解释。

### 受保护文件（写作时不能静默修改）
- `book/constitution.md`、`book/longform_blueprint.yml`、`book/reader_model.yml`
- `book/style_memory.md` 核心规则
- 主角核心欲望和底线（`entities/characters.yml`）
- 终局级秘密（`ledgers/knowledge_state.yml`）
- 当前卷目标（`volumes/vol_XXX/volume_outline.md`）

涉及以上修改 → 进入 `novel-change`，输出 diff 摘要，建立 checkpoint。

## 模型路由

`meta/model_policy.yml` 定义角色分工：
- **premium_model**：正文、章纲、active_flow、canon 决策、质量门禁、受保护文件修改。绝不能让弱模型写 final.txt 或决定剧情方向。
- **fast_model**：YAML/TXT 格式、validator 报错整理、diff 摘要、session log。不能写正文、不能改正史。

## 注意事项

- **默认走引擎**：项目有 `events/` 即用 `novel-engine-write`；写正文前用 `kit`/`context` 取引擎解析的 entering-state，不要手抄全量文件。`entities/ledgers` 是派生产物，canon 变化只记进 `events/`。
- **轮次是生产批次，不是叙事单位**。active_flow 可以跨越多轮，不要在每轮第三章强行总结或收束。
- **写正文前必须有可审计的写作输入**。引擎下是 `kit` 生成的 entering-state + 场景规格；旧流程下是 `writing_packet.md`。两者都不是项目资料库的全文复制。
- **example-project 是协议示范**，不是真实小说。它的风格文件（samples.md）是占位模板，它的章节（最后只有 ~2100 字）只展示格式。真实项目不要复用其中人名、地名、剧情。
- **不要用模板/examples/docs 中的人名、地名、势力名、道具名和剧情素材**——这些属于反污染规则。
- **校验脚本是诊断工具，不是写作警察**——warning 不等于必须重写，但 error 必须修。
