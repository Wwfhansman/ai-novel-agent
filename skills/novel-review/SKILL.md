---
name: novel-review
description: Review an AI Novel Agent project, round, chapter, or memory state. Use for cold-start continuity checks, quality review, source-of-truth conflict detection, writing packet validation, narrative debt checks, information visibility checks, and run-drift diagnosis.
---

# Novel Review

Use this skill to inspect whether a project can be safely continued by a fresh agent and whether recent writing remains aligned with the book.

> ⚠️ **引擎项目（有 `events/`）**：状态/连续性/记漏由引擎门禁覆盖——跑 `python -m novel_engine check`（schema+完整性+健康+结构+记漏）、`structure`、`coverage`，正史以 `events/` + `final.txt` 为准。下文提到的 `writing_packet.md`/`canon_delta.yml`/`summary.yml`/`merge_previews` 属未迁移旧项目；引擎项目无需逐个检查这些旧产物。本 skill 对引擎项目的重点是**冷读质量、文风对齐、追读性、人物体温**这些引擎判断不了的部分。

## Read First

Read:

- `docs/ENGINE.md` 与 `docs/ENGINE_WORKFLOW.md`（引擎项目的正史/状态/门禁——默认）
- `docs/CANON_AND_SAFETY.md`（受保护文件）
- `docs/WRITING_CRAFT.md`（文笔/TXT 格式）
- Target project `project.yml`
- `meta/model_policy.yml` if present
- `style/samples.md`（如有内容，审查时对照检查文笔是否偏离项目风格）

## 审查模式

### 冷启动审查

模拟一个新 agent。只读项目文件，不读之前的对话。验证项目文件能否解释：

- 这是一本什么书。
- 本书目标长篇规模是什么。
- 当前章节处于哪个宏观阶段/地图/卷。
- 世界/区域/城市/势力/力量体系规模是否稳定。
- 递进和秘密揭示是否在当前节奏预算内。
- 当前卷目标和阶段。
- 当前主角和主要角色目标。
- 活跃的叙事债务。
- 信息可见性和秘密。
- 世界状态和压力。
- 活跃的跨轮连续剧情流。
- 下一轮写作目标。
- 模型路由是否安全，没有 fast_model 的输出未经 premium/human 确认就进入正文或正史。

### 单章审查

引擎项目：审查 `chapters/chXXX/final.txt`（正文）+ `events/chXXX.yml`（本章记了什么）+ `chapters/chXXX/_kit/`（写作输入）。状态一致性跑 `python -m novel_engine check`（含完整性/结构/记漏）；不用逐个查旧的 summary/canon_delta/merge_previews。

### 多章审查

审查最近几章的 final.txt + events，跑 `check` / `structure` / `coverage`，再人工看：批次是否产生连贯进展、关系/状态变化是否都记进了 events（`coverage` 会提示明显漏记）。

## 必查项

1. **写作输入有效性（引擎）**：本章 `_kit/` 是否齐全（entering-state + 逐场规格 + 文风范例 + events 模板）？正文是否照场景级写、没凭空发明背景？

2. **状态一致性（引擎）**：跑 `python -m novel_engine check`——schema/引用/时序/账本健康/结构/记漏。引擎保证 events 与派生状态一致；重点看 `coverage` 报的"正文里关系变了却没记"。

3. **读者与债务健康度**：识别逾期债务、过多铺垫缺少 payoff、目标读者缺少回报。检查每章是否交付了具体的读者回报，是否制造或推进了下一个期待。

4. **角色意图**：检查每个重要角色是否从当前目标出发行动，而不只是为了推动剧情。

5. **信息可见性**：检查是否有角色知道了不该知道的事，秘密是否过早揭示。

6. **世界状态**：检查势力/资源/危机/公共压力是否对最近章节做出反应。

7. **风格与类型对齐**：对照 `book/constitution.md`、`book/reader_model.yml`、`book/style_memory.md`。
   - 如果 `style/samples.md` 非空，检查本章 `_kit/scene_prompts.md` 是否注入了样本文风锚点，正文是否贴近样本的句子节奏、段落手感、描写温度、对话语感和情绪处理（用 `python -m novel_engine compare` 对照已确立章节看文风漂移）。
   - 样本只允许提供语言方法；如果正文迁移了样本人名、地名、剧情、专有设定或标志性桥段，必须标记为污染风险。

8. **长篇规模控制**：检查 `book/longform_blueprint.yml` 是否存在且为最新、当前章节是否属于预期宏观阶段、世界级名称和势力是否保持预期规模。标记规模缩水。

9. **编剧层健康度**：检查 `planning/story_architecture.yml`、`planning/thread_board.yml` 是否存在并与当前卷匹配。若最近章节出现世界缩小、连续任务推进、主角成长过密、支线沉默过久或 `rolling_plan.yml` 只剩 0-3 章，建议先运行 `novel-architect`，不要直接进入下一轮写作。

10. **详细章纲对齐**：检查 `active_flow.yml` 是否存在且与上一章兼容、`rolling_plan.yml` 是否足够驱动正文、是否只包含未来窗口章节、已完成章纲是否归档、远期点子是否在 `future_backlog.yml`。检查每个未来章节是否有 `architecture_role`：节奏模式、世界扩张、主角成长预算、信息释放边界、支线触碰、off-screen 压力和可写场景触发点。

11. **执行层设定充足度**：检查前 9-15 章写作所需的人物、地点、势力、职位、制度事件和关键物品是否已经命名并落入 `entities/` 或 `ledgers/`。
   - `entities/factions.yml` 不应只有伞概念；当前卷核心组织必须有正式名称、内部结构、代表人物、资源、目标、对主角态度。
   - `entities/locations.yml` 不应只有世界/大域/城市骨架；早期正文发生的宗门、驻地、房舍、考核场、交易地、禁地等必须有名称和可写场景质感。
   - `entities/characters.yml` 应包含前 9-15 章会出场的导师/长老/管事/同辈竞争者/潜在盟友/压力源；不能只在 rolling_plan 中出现职能占位名。
   - `rolling_plan.yml` 不得出现“待命名”“自行命名”“writer 自行”“某宗门”“某长老”“某师兄”“某管事”“TBD”等占位。
   - 如果 rolling_plan 需要某个实体但实体库没有，标记为必须修复；writer 不应在写正文时做设定决策。

12. **跨轮 flow 连续性**：检查每章是否从上一章外部交接打开或记录了有理据的转换、批次末章是否因故事赚到了收束而非因批次结束才收束。

13. **正文与 TXT 格式**：引擎项目运行 `python -m novel_engine check <project>`（状态/完整性/结构）+ `python -m novel_engine txt <chapter>/final.txt` 和 `patterns`（格式/AI 腔）。
   - 写作心法、TXT 格式、结尾规则详见 `docs/WRITING_CRAFT.md`；审查时按其中规则清单对照。
   - Treat check/validator failures as required fixes, not suggestions.
   - Check whether the chapter reads like fiction rather than a task report.
   - Check whether the chapter contains weave material around the core task: daily life, reactions, dialogue, world/system texture, relationship friction, scene objects, body/mood beats, wrong guesses, lightness, awkwardness, softness, or character habit.
   - Check whether the chapter tried to complete too many tasks, or whether it kept one primary advancement and left appropriate problems unfinished.
   - Check whether the chapter function and pressure curve vary naturally across chapters instead of repeating the same internal rhythm.
   - Check whether `time_span`、`ending_type`、`position_in_flow` are preventing one-day-one-task containers rather than merely being filled in.
   - Check whether each core information variable has `enters_via` and actually enters through scene, dialogue, object, cost, or reaction.
   - Check whether the chapter added more than 1-2 new core information variables without enough action/reaction to digest them.
   - Check whether rules, systems, institutions, power mechanics, or political facts were verified through event, cost, mistake, or reaction rather than only explained.
   - Check whether the ending collapses into protagonist recap, analysis, or next-step thinking.
   - 检查交接是否来自外部运动，而不只是主角的内心决定。
   - 检查 `final.txt` 标题后是否只有一空行、正文段落之间是否无空行。

13. **读者回报**
   - 检查每章是否在 review 或 `_kit/` 中有 Reader Reward Check。
   - 检查回报是否出现在实际正文中，而不只是计划中。
   - 标记只推进设定却没有 payoff/揭示/代价/杠杆变化/关系变化/难忘小说素材的章节。

14. **模型路由**
   - 检查 `meta/model_policy.yml` 是否存在。
   - 检查 `meta/session_log.md` 中是否记录了多模型使用情况。
   - 标记任何看起来只由 fast/cheap 模型完成的正文、active_flow、rolling_plan、受保护文件修改或正史合并。

15. **记忆工程卫生**
   - 检查所有 YAML 文件是否有重复 key（YAML 解析器静默覆盖，不会报错）。
   - 检查 `entities/characters.yml` 中每个有实质性变化的角色的 `change_history` 是否有条目。
   - 检查 `ledgers/narrative_debts.yml`、`ledgers/foreshadowing.yml` 中状态字段的拼写一致性（`paid`/`partiall_paid` 等）。
   - 引擎项目：以上一致性大多由 `commit`（派生）和 `check` 保证；重点查 `coverage` 报的漏记关系，以及本章 events 是否覆盖了正文里的状态变化。
   - 章末交接是否记进了本章 `events/`（`note` 或类型化事件），下一章 `kit` 的 entering-state 是否承接得上。

16. **文笔多样性**
   - 检查最近 3 章正文是否存在高频重复句式（硬规则："不是X而是Y / 不是X，是Y"默认禁用，确需使用每章最多 1 次且 review 必须说明不可替代性；超过即为必须修复。也检查三连否定内心声明、元叙述、箭头/编号式认知总结、连续段落以同一句式开头、大量"他/她做了A，然后做了B"的平铺直叙）。
   - 句式重复不一定是单章问题——可能是模型默认腔。标记为风险并给出替换建议。

## 输出格式

```text
审查摘要
- 总体状态：pass / pass with risks / fail
- 最大风险
- 必须修复
- 建议修复
- 陈旧或冲突的文件
- 长篇规模风险
- 模型路由风险
- 是否需要进入 novel-change
```

## 失败处理

如果项目无法安全继续：
- 不要重写正文。
- 列出阻碍性的缺失文件或矛盾。
- 推荐 `novel-change` 处理结构性变化。
- 写作输入不全时，推荐重新跑 `python -m novel_engine kit <project> --chapter chNNN`。
