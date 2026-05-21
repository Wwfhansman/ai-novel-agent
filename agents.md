# AI Novel Agent — Agent 使用指南

## 项目概述

AI Novel Agent 是一套面向长篇小说创作的 agent-native 写作框架。它不是应用、不是 SaaS、不是"一键生成小说"的工具——而是一套基于文件系统的创作操作系统。每本小说是一个独立项目目录，项目文件是正史和长期记忆，agent 对话只是临时工作台。

## 常用命令

```bash
# 校验章节输出
python3 scripts/validate_novel_output.py projects/<project-name> --chapters ch001
python3 scripts/validate_novel_output.py projects/<project-name> --chapters ch001 --fix-format
python3 scripts/validate_novel_output.py projects/<project-name> --chapters ch001 --strict

# 跳过规划检查（仅检查 TXT 格式和章节文件完整性）
python3 scripts/validate_novel_output.py projects/<project-name> --chapters ch001 --skip-planning
```

## 核心架构

### 四个 Skill

| Skill | 用途 | 触发条件 |
|-------|------|---------|
| `novel-bootstrap` | 从 seed 初始化新书 | 项目为空 / 用户明确开新书 / 要求重启作品 DNA |
| `novel-write` | 日常写作，默认每轮 3 章 | 继续写作、写下一章 |
| `novel-review` | 冷启动审查、质量检查、连续性验证 | 每轮结束后 / 用户要求检查质量 / 长篇出现跑偏迹象 |
| `novel-change` | 中途新点子、设定调整、变更管理 | 用户想加反转/改设定/调人物关系/改大纲 |

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
  chapters/ch001/                 # 章节层——这章发生了什么、改变了什么
    brief.md                      # 写作前交接说明
    context_pack.md               # 本章上下文编译（读取了什么、关键结论）★写作前必生成
    draft.txt                     # 草稿
    final.txt                     # 终稿（正史正文）★唯一正文权威
    review.md                     # 审查报告
    summary.yml                   # 章节摘要
    canon_delta.yml               # 章节变化记录（不是当前状态总表）
  entities/                       # 实体层——人物/势力/地点/物品当前状态
    characters.yml
    factions.yml
    locations.yml
    items.yml
    power_system.yml
  ledgers/                        # 动态账本——故事中的活变量
    narrative_debts.yml           # 叙事债务（读者正在等待什么）
    foreshadowing.yml             # 伏笔
    knowledge_state.yml           # 信息可见性（谁知道什么）
    world_state.yml               # 世界状态（外部系统的当前压力）
    idea_pool.yml                 # 灵感池（未进入正史的可能性）
    decision_log.yml              # 重大决策记录
  planning/                       # 规划层
    active_flow.yml               # 当前跨轮连续剧情流 ★唯一连续性权威
    rolling_plan.yml              # 未来 6-15 章详细章纲 ★唯一近期规划权威
    current_round.yml             # 本批次生产追踪（轻量，不复制章纲）
    completed_plan_log.yml        # 已完成章纲归档
    future_backlog.yml            # 远期点子
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

| 事实类型 | 权威来源 | 说明 |
|---------|---------|------|
| 已发生的正文事实 | `final.txt` | 原文细节以 final.txt 为准 |
| 某章发生了什么 | `summary.yml` | 冲突时回看 final.txt |
| 某章造成了什么变化 | `canon_delta.yml` | 变更日志，不代表当前最终状态 |
| 人物当前状态 | `entities/characters.yml` | 当前目标/立场/关系/意图 |
| 当前世界局势 | `ledgers/world_state.yml` | 主角之外的外部系统 |
| 谁知道什么 | `ledgers/knowledge_state.yml` | 信息差 |
| 读者期待债 | `ledgers/narrative_debts.yml` | 全局债务 |
| 当前连续剧情流 | `planning/active_flow.yml` | 跨轮连续性的权威 |
| 近期未来计划 | `planning/rolling_plan.yml` | 6-15 章详细章纲 |
| 本批次执行计划 | `planning/current_round.yml` | 只是生产摘录 |
| 长篇规模递进 | `book/longform_blueprint.yml` | ★受保护 |

## 核心工作流

### 新书启动
```
用户 seed → novel-bootstrap → 初始化全项目文件 → 生成 9-15 章滚动章纲
```

### 日常写作（一轮 3 章）
```
1. 读取 book/longform_blueprint.yml + planning/active_flow.yml + planning/rolling_plan.yml
2. 刷新 active_flow + rolling_plan
3. 生成 round context pack（3000-5000 字）
4. 生成 current_round.yml（仅记录本批次章节列表）
5. 逐章：
   a. 写 brief.md + context_pack.md（1000-2500 字）
   b. 写 draft.txt → 审稿 → final.txt
   c. 写 review.md
   d. 生成 summary.yml + canon_delta.yml
   e. 更新 entities/ + ledgers/ + planning/
6. 滑动 rolling_plan.yml 未来窗口
```

### 交接字段语义（重要）

三个字段名字不同，语义不同，不要混淆：

| 字段 | 位置 | 语义 |
|------|------|------|
| `planned_handoff` | `rolling_plan.yml` | 规划中期望的交接 |
| `actual_handoff` | `canon_delta.yml`、`summary.yml` | 写完后实际造成的交接 |
| `current_handoff` | `active_flow.yml` → `last_cut` | 当前最新的实际交接 |

写作时：读 `current_handoff`（上一章实际）→ 参考 `planned_handoff`（本章规划）→ 写完后记录 `actual_handoff`（本章实际）。

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

### 受保护文件（novel-write 不能静默修改）
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

- **轮次是生产批次，不是叙事单位**。active_flow 可以跨越多轮，不要在每轮第三章强行总结或收束。
- **context_pack.md 必须在写正文前生成**。它是可审计的写作输入记录，不是项目资料库的全文复制。
- **example-project 是协议示范**，不是真实小说。它的风格文件（samples.md）是占位模板，它的章节（最后只有 ~2100 字）只展示格式。真实项目不要复用其中人名、地名、剧情。
- **不要用模板/examples/docs 中的人名、地名、势力名、道具名和剧情素材**——这些属于反污染规则。
- **校验脚本是诊断工具，不是写作警察**——warning 不等于必须重写，但 error 必须修。
