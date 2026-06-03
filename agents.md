# AI Novel Agent — Agent 指南

## 这是什么

面向长篇小说创作的 agent-native 框架。每本小说是一个文件系统项目；项目文件是正史和长期记忆，agent 对话只是临时工作台。

**生产主干是 `novel_engine`（唯一现行流程）：** 正史是只增不改的事件日志 `events/`，当前状态由事件**派生**（`commit` 物化进 `entities/`、`ledgers/`）。机械变化记成类型化事件，写作走场景级，收尾走 `check` / `commit`。旧的写作 skill 和校验/合并脚本已删除——**旧项目（无 `events/`）先 `python -m novel_engine migrate <project>` 上引擎再写**。

完整设计见 [`docs/ENGINE.md`](docs/ENGINE.md) 与 [`docs/ENGINE_WORKFLOW.md`](docs/ENGINE_WORKFLOW.md)。

## 铁律（最重要）

1. **不手写 `entities/`、`ledgers/`。** 它们是派生产物，`commit` 会用 events 重算覆盖。canon 变化只记进 `events/`。
2. **机械变化用类型化事件**——`relationship_changed` / `character_changed` / `faction_changed` / `location_changed` / `knowledge_changed` / `debt_*` / `foreshadow_*` / `item_*`——不塞进 `fact_added` 或 `note`。**最常漏的是关系**。
3. **进入本章的状态从引擎取**（`kit` / `context` 的 entering-state），不凭对话记忆，也不与它矛盾。这是长对话不记混的原因。
4. **场景级写正文**：先写够感官/情绪/织入，`one_change` 只是小料、可为空；信息按 `enters_via` 进入，禁止主角脑内总结；结尾切在外部动作。
5. **受保护文件**（`book/constitution.md`、`book/longform_blueprint.yml`、卷目标、主角核心欲望/底线、终局秘密）不静默改——走 `novel-change`。

## Skill / Agent 分工

| 名 | 用途 | 何时用 |
|---|---|---|
| `novel-bootstrap` | 从 seed 生成故事 DNA，再 `init` | 开新书 |
| `novel-engine-write`（默认） | 逐章场景级写作 | 写下一章 |
| `novel-architect` | 编剧层：未来 10-30 章世界/支线/节奏/成长 | rolling_plan 快空、世界缩、支线断、成长过密 |
| `novel-review` | 冷读质量、文风、追读性、人物体温 | 每几章 / 用户要查 |
| `novel-change` | 改设定 / 加反转 / 变更管理 | 中途变更 |
| `novel-memory-recheck`（subagent） | 补漏记的关系/状态（含潜文本） | 每章记完 events 后 |

OpenCode 默认进 `novel-engine-write`；开新书切 `novel-bootstrap`。

## 项目结构

```
projects/<novel>/
  events/                ★正史：bootstrap.yml + chXXX.yml（本章造成的变化）
  chapters/chXXX/         final.txt（正文）+ _kit/（生产套件）
  entities/              ★派生：characters / factions / locations / items / power_system
  ledgers/              ★派生：narrative_debts / foreshadowing / knowledge_state / world_state
  planning/              编剧层（手维护）：rolling_plan / story_architecture / thread_board / development_packs / future_backlog
  book/                  全书：宪法、长篇蓝图（受保护）、读者模型、风格记忆
  style/  meta/          文风样本、模型路由、会话日志
```

## 唯一事实来源（冲突时按此判断）

| 事实 | 权威来源 |
|---|---|
| 正文原文 | `chapters/chXXX/final.txt` |
| 本章造成了什么变化 | `events/chXXX.yml` ★ |
| 人物/势力/地点/物品/力量当前态 | `entities/*.yml`（events 派生，不手写） |
| 世界局势/信息差/伏笔/读者期待债 | `ledgers/*.yml`（同为派生） |
| 近期未来计划 | `planning/rolling_plan.yml`（编剧层维护） |
| 长篇规模递进 | `book/longform_blueprint.yml`（受保护） |

## 写作流程

### 开新书

```
1. novel-bootstrap 从 seed 生成 book/ entities/ ledgers/ planning/（含 9-15 章 rolling_plan）
2. python -m novel_engine init  <project>   # 从初始 entities/ledgers 种 events/bootstrap.yml
3. python -m novel_engine check <project>   # 验收初始状态
4. 切到 novel-engine-write，逐章写
```

### 逐章

```
1. 套件   python -m novel_engine kit <project> --chapter chNNN   → chapters/chNNN/_kit/
2. 写     按 _kit/scene_prompts.md 逐场写（经历优先；one_change 小、可空；出口切外部动作）
3. 缝合   按 _kit/stitch_prompt.md 连成整章 → chapters/chNNN/final.txt（标题+空行+正文，段落间不空行）
4. 自检   python -m novel_engine txt / patterns chapters/chNNN/final.txt
5. 事件   按 _kit/events.template.yml 把本章 canon 变化写进 events/chNNN.yml
6. 复核   调 novel-memory-recheck 补漏（尤其关系/潜文本）
7. 门禁   python -m novel_engine check <project>   # 有 error 先修；warning（含 coverage 记漏）尽量处理
8. 提交   python -m novel_engine commit <project>  # 物化派生 entities/ledgers
```

### 写后记忆自查（commit 前必做）

对照正文逐条问，漏了就补事件：

- 本章**新建或改变了哪些关系**？每一个都进了 `relationship_changed` 吗？（最常漏，别写成 fact）
- 谁的目标/立场/意图变了？进了 `character_changed` 吗？谁知道了新东西？`knowledge_changed`？
- 开/收了债务或伏笔？势力/地点状态变了？
- 跑 `python -m novel_engine project <project>` 看派生态里这些变化在不在。**关系字段空的，多半就是漏了 `relationship_changed`。**

## 命令速查

```bash
init / kit / check / commit                # 开书与逐章主干
structure / coverage / health / project    # 体检（追读性/记漏/逾期/当前态）
txt / patterns / compare / fingerprint     # 文风与格式（作用于 final.txt）
shadow / migrate / materialize             # 旧项目搬迁与物化
```

## 记忆模型

正史 = `events/`；当前状态 = events 的投影。每章 `commit` 把状态物化进 `entities/`、`ledgers/`，"变化"与"当前状态"构造上不漂移。每写一章，引擎从 events 算出 entering-state 递给 writer——所以换不换对话、对话多长，记忆都一致。事件词汇表见 `novel_engine/schemas/event.schema.json`。

## 模型路由

`meta/model_policy.yml` 分 premium / fast。正文、剧情方向、`events` 确认、受保护文件由 premium 或人确认；YAML 格式、`check`/`patterns`/`txt` 报错整理、session log 可用 fast。绝不让弱模型写 `final.txt` 或决定剧情方向。

## 注意事项

- **example-project 是协议示范**，不是真实小说；不要复用其中人名、地名、剧情。
- 不要用模板、docs、示例里的人名/地名/势力名/道具名当创作素材（反污染）。
- 引擎门禁是诊断：`error` 必修，`warning`（结构/记漏/账本健康）是建议，不等于必须重写。
