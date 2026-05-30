# 上下文编译与 Writing Packet

## 目标

新项目 v2 保留三类工作记忆：

```text
planning/context_packs/architect_context_pack_XXX.md
planning/context_packs/round_XXX_context_pack.md
chapters/chXXX/writing_packet.md
```

architect context pack 负责编剧层开发前的全局压缩输入；只在运行 `novel-architect` 时生成。
round context pack 负责批次级共识；chapter writing packet 是每章唯一写作前输入，合并旧 `brief.md`、`context_pack.md`、`prompt.md`，但保留可审计来源和正文 Writing Card。

## 基本原则

- 远处读摘要，近处读原文，关键旧内容回看原文。
- `planning/rolling_plan.yml` 每轮必须全文读取，但只摘录本批次、本章相邻章节和必要后续约束。
- 不复制全量 `characters.yml`、`knowledge_state.yml`、`world_state.yml`；只记录本章实际涉及的对象。
- 关键结论必须写 `Source References`。
- `style/samples.md` 非空时，Writing Card 必须提取 3-5 条正向样本文风锚点。
- Longform Scale Check、Cut Continuity、Reader Reward Check 是质量门，不得为了省事删除。

## 预算

```text
Architect Context Pack: 8000-15000 中文字
Round Context Pack: 3000-5000 中文字
Chapter Writing Packet: 1000-2500 中文字
Writing Card: 保持紧凑；分离 Chapter Design / Writing Execution
```

超过预算时，优先删复述、背景说明和低相关账本内容；不要删上一章 `actual_handoff`、active_flow、rolling_plan 本章信息、样本文风锚点、读者回报和写后更新清单。

## Architect Context Pack

位置：

```text
planning/context_packs/architect_context_pack_XXX.md
```

只在触发 `novel-architect` 时生成。必须包含：

- 当前全书类型承诺、禁区和读者承诺。
- `longform_blueprint.yml` 中当前宏观阶段、规模递进、力量节奏和秘密释放边界。
- 当前卷目标、当前卷不可提前完成的事项。
- `active_flow.last_cut` 和当前连续压力。
- `rolling_plan.yml` 当前剩余窗口和薄弱点。
- `story_architecture.yml` 和 `thread_board.yml` 的现状。
- 最近 6-9 章 summary 的压缩理解。
- 需要精确回看的最近 1-2 章正文片段。
- 相关 entities/ledgers 摘要，尤其是势力、地点、配角、信息差、世界压力、叙事债和伏笔。
- 当前故事健康诊断：世界是否缩小、节奏是否过快、主角成长是否过密、支线是否沉默太久。

不要把全量项目数据库复制进 architect context pack。它是给编剧层的高密度输入，不是备份。

## Round Context Pack

位置：

```text
planning/context_packs/round_XXX_context_pack.md
```

必须包含：

- 本批次范围，不是 round 级剧情目标。
- 文件读取清单和 source refs。
- `Director Directive`：本轮必须推进什么、必须保持未闭合什么、不可触碰什么、writer 可自由发挥到哪里。
- 当前 active_flow、rolling_plan、长篇尺度和当前卷目标。
- 最近剧情理解和必要全文回看。
- 本批次 3 章的功能、压力曲线、信息释放、读者回报和风险。
- 本批次相关旧章节回看和动态账本摘录。
- 模型路由记录。

## Chapter Writing Packet

位置：

```text
chapters/chXXX/writing_packet.md
```

固定标题：

- `Read Files`
- `Source References`
- `Longform Scale Check`
- `Cut Continuity`
- `Reader Reward Check`
- `Writing Card`
- `Pre-Draft Self Check`
- `Required Updates After Writing`

`Writing Card` 是正文生成时的抬头纸。它必须把设计面和执行面分开：

- `Chapter Design`：one_line_goal、chapter_function、time_span、ending_type、pressure_curve.position_in_flow、architecture_role、must_happen / must_not_complete、information_release、narrative_weave。
- `Writing Execution`：opening_sensory、voice_examples、foreshadowing_weight、relationship_temperature、body_scene_texture、dialogue_mode、scene_moments、ending_gesture、sample_style_anchors、prose_constraints。

它不是任务清单。正文写作时优先盯住 `Writing Execution` 的可写瞬间、人物语感、伏笔分量、关系温度、身体/场景质感和对话模式；`Chapter Design` 用来防止跑偏，不用逐条翻译。

`information_release` 的核心变量必须写 `enters_via`。如果只能靠主角脑内总结传达，说明场景还没设计好。

## 承接规则

上一章 `canon_delta.yml` 的 `actual_handoff` 是硬输入。非开篇章节必须承接它，或者在 `writing_packet.md` 和 `review.md` 中解释为什么切换场景、时间或 POV。

`draft_handoff_note.md` 只用于连续 draft 的热态承接，不是正史，不替代 `actual_handoff`。
