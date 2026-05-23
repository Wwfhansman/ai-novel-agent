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

6. **初始化实体和账本**
   - 在 `entities/` 下创建主角和初始重要实体。
   - 在 `ledgers/` 下创建空或初始条目。
   - `idea_pool.yml` 与正史分离。

7. **初始化规划**
   - 写 `planning/active_flow.yml`：第一条连续剧情流、当前压力、灵活范围、结束条件、轮次边界不关闭 flow 的规则。
   - 写 `planning/rolling_plan.yml`：9-15 章详细章纲窗口。
   - 不要规划超过 15 章的详细章纲；远期点子、macro stage 转折点和暂不进入窗口的灵感放入 `planning/future_backlog.yml`。
   - 每章应包含 300-800 字剧情简介，以及 `flow_id`、`flow_position`、`chapter_function`、`pressure_curve`、`reader_question_flow`、`core_advance`、`information_release`、`chapter_turn`、`side_yield`、`叙事织入`、`density_control`、`planned_handoff` 和约束。
   - `core_advance` 应命名一个主要外部推进和本章不完成的事项。`叙事织入` 应提供人物日常反应、场景即时质感、关系温度波动，防止正文变成任务清单式的执行报告。
   - `information_release` 通常每章限制在 1-2 个读者需要记住的核心新变量。
   - 写 `planning/current_round.yml` 作为生产批次追踪器，只记录本轮章节、状态和起止 flow，不复制章纲，不是独立规划权威。
   - 不要在 bootstrap 阶段创建死板的 scene-beat 大纲。
   - 除非用户明确要求进入 novel-write，否则不写正文。

8. **写元信息**
   - 更新 `project.yml` 和 `meta/project_state.yml`。
   - 创建或更新 `meta/model_policy.yml`。
   - 在 `ledgers/decision_log.yml` 或 `meta/session_log.md` 中记录 bootstrap 决策。

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
- 哪些文件受保护、不能静默修改？

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
