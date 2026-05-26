---
name: novel-bootstrap
description: Initialize a new AI Novel Agent project from a seed idea. Use when a novel project is empty, the user explicitly asks to start a new novel, or the user explicitly requests a full reboot/rebuild of the book premise, protagonist, world, or core creative constitution.
---

# Novel Bootstrap

Use this skill to create a new novel project from a seed. Do not use it for ordinary mid-story ideas, local setting changes, character adjustments, or current-volume revisions; use `novel-change` for those.

## Anti-Contamination Rule

Treat docs, schemas, templates, examples, and previous project files as process references only. Never reuse names, places, factions, items, plot devices, crisis types, or example scenes from these files unless the user explicitly asks for them.

Before writing project content, create a short "contamination check" in `meta/session_log.md`:

- list any names or story elements that came from docs/examples and are therefore forbidden;
- confirm the generated project names and plot elements come from the user seed or fresh invention;
- if the seed is close to a documented example, intentionally choose different names, institutions, objects, and opening conflicts.

## Required Inputs

- User seed: premise, setting, protagonist image, genre, opening scene, or desired payoff.
- Target project path under `projects/<project-id>/`.
- Empty or template-based project directory.

If the target project already has canon chapters, stop and route to `novel-change` unless the user explicitly requested a reboot.

## Read First

Read:

- `templates/project/README.md`
- `docs/MEMORY_MODEL.md`
- `docs/CANON_AND_SAFETY.md`
- `docs/FILE_FORMATS.md`
- `docs/MODEL_ROUTING.md`
- `templates/project/book/chapter_rhythm_guide.md`（初始化章纲时参考网文章类型模板）
- `templates/project/style/samples.md`（占位模板——bootstrap 时不写内容，但需告知用户此文件用于后续存放文笔风格报告）

Use `templates/project/` as the required output structure.

## 工作流

1. **评估 seed**
   - 提取类型、主角、核心冲突、读者爽点和长篇潜力。
   - 如果 seed 不充分，生成 3-5 个可行方向并推荐一个。
   - 识别并排除任何可能从 docs/example/template 泄漏到新项目中的故事素材。

2. **创建创作宪法**
   - 写 `book/constitution.md`。
   - 包含类型、核心卖点、主角长期欲望、读者承诺、禁止事项和受保护边界。
   - 添加项目专属规则：禁止通用 AI 小说腔、机械日序开头、重复思考式结尾、复用框架示例。

3. **初始化长篇规模控制**
   - 写 `book/longform_blueprint.yml`。
   - 将其视为受保护的全书规模权威，而不是松散脑暴。
   - 定义目标长度、预期章节数、章节字数范围、宏观阶段/地图/卷、世界-区域-城市层级、势力规模、主角递进预算、机遇频率、重大秘密的揭示窗口。
   - 如果 seed 偏小，将其展开为长篇结构，而不是把整本书缩小到开篇地点。
   - 显式记录规模护栏，如"X 是一个世界，不是一个城市"。
   - 远景阶段保持灵活；目的是规模意识和递进预算，而不是锁死的百万字大纲。

4. **初始化全书层记忆**
   - 写 `book/global_summary.md` 作为初始全书状态。
   - 写 `book/reader_model.yml`、`book/style_memory.md`、`book/endgame_hypotheses.yml`（作为假说，不是正史）。
   - 在 `style_memory.md` 中定义段落节奏、场景连续性、章末结尾和 TXT 格式的文笔标准。

5. **初始化 vol_001**
   - 写 `volumes/vol_001/` 下的卷纲、摘要、状态、主线和债务文件。
   - 对齐当前卷与 `book/longform_blueprint.yml`：说明属于哪个宏观阶段、可以触及什么规模、不能揭示或解决什么。

6. **建立第一卷执行层设定包**
   - 在生成 `planning/rolling_plan.yml` 之前，先把第一卷和前 9-15 章会直接进入正文的执行层设定定下来。
   - 目标不是写百科，而是让 writer 拿到正文可用的专名、地点、职位、派系、人物关系和场景抓手；writer 只写 prose，不负责临时发明宗门名、长老名、地名、派系格局或制度规则。
   - 必须为当前卷核心舞台创建可写的地点链：世界/大域/当前区域/城镇或村落/核心机构驻地/关键功能地点。每个地点至少包含：名称、规模感、地理位置、视觉或生活质感、在前 9-15 章承担的剧情功能、与主角的关系。
   - 必须为当前卷核心势力创建可写的势力链：顶层秩序/区域势力/当前舞台势力/内部派系或职能部门。每个势力至少包含：名称、层级、目标、资源、内部结构、代表人物、对主角态度、当前行动。
   - 若前 9-15 章涉及宗门/学院/官署/帮派/公司/军队/家族等组织，必须提前命名该组织，并定义至少 3-6 个正文会用到的内部角色或职位：掌权者、执行者、反对者、基层管理者、同辈竞争者、潜在援手。不要用“某长老”“某师兄”“某管事”“待 writer 命名”。
   - 若章纲中需要比赛、考核、入门、审判、交易、追捕、会议、巡查等制度事件，必须提前定义执行层规则：谁主持、在哪里发生、参与规模、公开规则、潜规则、奖励或惩罚、主角能利用的缝隙。
   - 对每个新命名实体做反污染检查：名称、机构、物品、剧情功能不得来自 docs/templates/example/previous projects，除非用户 seed 明确指定。

7. **初始化实体和账本**
   - 在 `entities/` 下创建主角和初始重要实体。
   - `entities/characters.yml` 必须包含主角，以及第一卷/前 9-15 章会出场或被直接提及的关键人物。不要把“灰袍长老”“林师兄”“管事”“外门师父”这类角色留给 writer 临时命名。
   - `entities/factions.yml` 必须包含当前卷核心组织、其上级/下级关系、内部派系或职能部门、代表人物、资源和对主角态度。
   - `entities/locations.yml` 必须包含当前卷核心舞台和前 9-15 章会用到的关键地点；每个地点要有可写的场景质感，不只写“偏远小镇”“某宗门”。
   - `entities/items.yml` 必须包含前 9-15 章会反复出现、承担证据/资源/伏笔/力量递进功能的物品。
   - `entities/power_system.yml` 必须把当前阶段会实际使用的等级、测试、代价、误用后果写到可执行层，不只写宏观体系名。
   - 在 `ledgers/` 下创建空或初始条目。
   - `ledgers/world_state.yml` 记录当前外部压力和势力动作；不要把势力基本资料只写在 world_state，基本资料应在 `entities/factions.yml`。
   - `ledgers/knowledge_state.yml` 记录谁知道什么，尤其是当前卷关键秘密、误判和信息差。
   - `ledgers/narrative_debts.yml`、`foreshadowing.yml` 记录前 9-15 章已经承诺给读者的期待、伏笔和未偿还问题。
   - `idea_pool.yml` 与正史分离。

8. **初始化规划**
   - 写 `planning/active_flow.yml`：第一条连续剧情流、当前压力、灵活范围、结束条件、轮次边界不关闭 flow 的规则。
   - 写 `planning/rolling_plan.yml`：9-15 章详细章纲窗口。
   - 不要规划超过 15 章的详细章纲；远期点子、macro stage 转折点和暂不进入窗口的灵感放入 `planning/future_backlog.yml`。
   - 每章应包含 300-800 字剧情简介，以及 `flow_id`、`flow_position`、`cross_chapter_event`、`starts_mid_action`、`ends_mid_action`、`chapter_function`、`pressure_curve.position_in_flow`、`reader_question_flow`、`core_advance`、`information_release`、`chapter_turn`、`side_yield`、`叙事织入`、`density_control`、`planned_handoff` 和约束。
   - `core_advance` 应命名一个主要外部推进和本章不完成的事项。`叙事织入` 应提供人物日常反应、场景即时质感、关系温度波动，防止正文变成任务清单式的执行报告。
   - `information_release` 通常每章限制在 1-2 个读者需要记住的核心新变量。
   - `rolling_plan.yml` 中出现的组织、地点、人物、职位、制度事件和关键物品，必须能在 `entities/` 或 `ledgers/` 中找到对应定义；不得出现“待命名”“由 writer 自行命名”“某宗门”“某长老”“某师兄”“某管事”等占位表达。
   - 如果规划需要新增正文会用到的实体，先回到步骤 6-7 补齐实体和账本，再写入章纲。
   - 写 `planning/current_round.yml` 作为生产批次追踪器，只记录本轮章节、状态和起止 flow，不复制章纲，不是独立规划权威。
   - 不要在 bootstrap 阶段创建死板的 scene-beat 大纲。
   - 除非用户明确要求进入 novel-write，否则不写正文。

9. **开书完整性自检**
   - Bootstrap 结束前，检查第一卷执行层设定是否足够支撑前 9-15 章正文。
   - 检查 `entities/factions.yml`：是否有当前卷核心组织的正式名称、内部结构、代表人物、资源、目标、对主角态度。
   - 检查 `entities/locations.yml`：是否有当前卷核心舞台、组织驻地、关键功能地点和可写场景质感。
   - 检查 `entities/characters.yml`：是否有前 9-15 章会出场的导师/长老/管事/同辈竞争者/潜在盟友/压力源，且不是职能占位名。
   - 检查 `planning/rolling_plan.yml`：每个章节条目是否只引用已命名、已落库或已在账本中定义的实体。
   - 搜索并消除占位表达：`待命名`、`自行命名`、`writer 自行`、`某宗门`、`某长老`、`某师兄`、`某管事`、`暂定`、`placeholder`、`TBD`。
   - 如果发现缺口，不要把缺口留给 writer；回到实体/账本/规划文件补齐后再完成 bootstrap。

10. **写元信息**
   - 更新 `project.yml` 和 `meta/project_state.yml`。
   - 创建或更新 `meta/model_policy.yml`。
   - 在 `ledgers/decision_log.yml` 或 `meta/session_log.md` 中记录 bootstrap 决策和开书完整性自检结论。

## 输出要求

Bootstrap 完成后，项目文件必须能让一个新 agent 回答：
- 这是一本什么书？
- 本书目标长篇规模是什么？
- 开篇处于哪个宏观阶段/地图/卷？
- 什么世界/区域/城市/势力规模不能缩水？
- 当前阶段允许什么递进和揭示节奏？
- 目标读者期待什么？
- 主角是谁、想要什么？
- vol_001 试图完成什么？
- 当前活跃的连续剧情流是什么？
- 未来 9-15 章大概在做什么？
- 第一卷核心组织叫什么、在哪里、由谁运转、内部有哪些会影响前 9-15 章的角色和派系？
- 前 9-15 章会出现的关键地点、人物、职位、物品和制度事件是否已经命名并落入 `entities/` 或 `ledgers/`？
- 哪些文件受保护、不能静默修改？

## Bootstrap Quality Gate

Do not finish bootstrap if any of these are true:

- `planning/rolling_plan.yml` asks writer to invent names, factions, locations, elders, senior disciples, managers, teachers, exam rules, or tournament structure during prose drafting.
- A chapter in the initial 9-15 chapter window references an unnamed faction, location, role, institution, event, or recurring item.
- `entities/factions.yml` only contains umbrella concepts and lacks the current-volume organization that will appear in prose.
- `entities/locations.yml` only contains macro regions and lacks the concrete places where early scenes happen.
- The current-volume organization has no named internal decision makers, executors, peer rivals, low-level managers, or pressure sources despite the rolling plan needing them.
- Any entity file contains "writer should name this later", "待命名", "自行命名", "某长老", "某师兄", "某管事", "TBD", or equivalent placeholders.
- The only reason for missing names is anti-contamination caution. Anti-contamination requires fresh invention, not leaving blanks.

## 受保护文件

bootstrap 期间可以创建受保护文件。bootstrap 之后不能静默修改：
- `book/constitution.md`
- `book/longform_blueprint.yml`
- `book/reader_model.yml`
- `book/style_memory.md` 核心规则
- `volumes/vol_001/volume_outline.md` 卷目标
- `entities/characters.yml` 中主角核心欲望和底线
- `ledgers/knowledge_state.yml` 中终局级秘密

## 失败处理

以下情况应停下来寻求方向：
- 目标项目已有确认章节且用户未要求重启。
- seed 隐含相互矛盾的类型或读者承诺。
- 所需模板文件缺失。
- 无法确定是否应覆盖已有正史。
- 发现生成的人名、势力、物品或剧情节拍来自 docs/templates/example 项目。
