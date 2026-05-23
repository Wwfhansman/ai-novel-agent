# 上下文编译与 Writing Packet

## 目标

新项目 v2 保留两层工作记忆：

```text
planning/context_packs/round_XXX_context_pack.md
chapters/chXXX/writing_packet.md
```

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
Round Context Pack: 3000-5000 中文字
Chapter Writing Packet: 1000-2500 中文字
Writing Card: 保持紧凑；分离 Chapter Design / Writing Execution
```

超过预算时，优先删复述、背景说明和低相关账本内容；不要删上一章 `actual_handoff`、active_flow、rolling_plan 本章信息、样本文风锚点、读者回报和写后更新清单。

## Round Context Pack

位置：

```text
planning/context_packs/round_XXX_context_pack.md
```

必须包含：

- 本批次范围，不是 round 级剧情目标。
- 文件读取清单和 source refs。
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

- `Chapter Design`：one_line_goal、chapter_function、time_span、ending_type、pressure_curve.position_in_flow、must_happen / must_not_complete、information_release、narrative_weave。
- `Writing Execution`：opening_sensory、scene_moments、ending_gesture、sample_style_anchors、prose_constraints。

它不是任务清单。正文写作时优先盯住 `Writing Execution` 的可写瞬间；`Chapter Design` 用来防止跑偏，不用逐条翻译。

`information_release` 的核心变量必须写 `enters_via`。如果只能靠主角脑内总结传达，说明场景还没设计好。

## 承接规则

上一章 `canon_delta.yml` 的 `actual_handoff` 是硬输入。非开篇章节必须承接它，或者在 `writing_packet.md` 和 `review.md` 中解释为什么切换场景、时间或 POV。

`draft_handoff_note.md` 只用于连续 draft 的热态承接，不是正史，不替代 `actual_handoff`。
