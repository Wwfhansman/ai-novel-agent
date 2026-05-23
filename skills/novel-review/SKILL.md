---
name: novel-review
description: Review an AI Novel Agent project, round, chapter, or memory state. Use for cold-start continuity checks, quality review, source-of-truth conflict detection, writing packet validation, narrative debt checks, information visibility checks, and run-drift diagnosis.
---

# Novel Review

Use this skill to inspect whether a project can be safely continued by a fresh agent and whether recent writing remains aligned with the book.

## Read First

Read:

- `docs/CANON_AND_SAFETY.md`
- `docs/CONTEXT_PACK.md`
- `docs/MEMORY_MODEL.md`
- `docs/WORKFLOWS.md`
- `docs/WRITING_CRAFT.md`
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

审查特定章节的 `writing_packet.md`、`draft.txt`/`final.txt`、`summary.yml`、`canon_delta.yml`、`memory_update_plan.md`、`planning/merge_previews/*` 以及受影响的 `entities/`、`ledgers/`、`planning/`。检查最终状态文件是否在章节完成后更新。

### 轮次审查

审查最近 3 章：round context pack、所有 chapter writing packet、所有章节摘要和 delta、merge preview、更新后的账本和滚动章纲。检查批次是否产生了连贯的进展而没有变成人工的三章故事单元。

## 必查项

1. **Writing packet 有效性**：是否列出了读取文件、原因、关键收获、旧章节回看、不确定项、分离 Chapter Design / Writing Execution 的 Writing Card、Pre-Draft Self Check 和必须更新项？

2. **唯一事实来源一致性**：如果 summary、delta、entity state、ledger 和 planning 不一致，识别权威文件。

3. **读者与债务健康度**：识别逾期债务、过多铺垫缺少 payoff、目标读者缺少回报。检查每章是否交付了具体的读者回报，是否制造或推进了下一个期待。

4. **角色意图**：检查每个重要角色是否从当前目标出发行动，而不只是为了推动剧情。

5. **信息可见性**：检查是否有角色知道了不该知道的事，秘密是否过早揭示。

6. **世界状态**：检查势力/资源/危机/公共压力是否对最近章节做出反应。

7. **风格与类型对齐**：对照 `book/constitution.md`、`book/reader_model.yml`、`book/style_memory.md`。
   - 如果 `style/samples.md` 非空，检查 `writing_packet.md` 的 Writing Card 是否提取了 3-5 条正向样本文风锚点，`reader_pass.md` 是否检查样本文风对齐，正文是否贴近样本的句子节奏、段落手感、描写温度、对话语感和情绪处理。
   - 样本只允许提供语言方法；如果正文迁移了样本人名、地名、剧情、专有设定或标志性桥段，必须标记为污染风险。

8. **长篇规模控制**：检查 `book/longform_blueprint.yml` 是否存在且为最新、当前章节是否属于预期宏观阶段、世界级名称和势力是否保持预期规模。标记规模缩水。

9. **详细章纲对齐**：检查 `active_flow.yml` 是否存在且与上一章兼容、`rolling_plan.yml` 是否足够驱动正文、是否只包含未来窗口章节、已完成章纲是否归档、远期点子是否在 `future_backlog.yml`。

10. **跨轮 flow 连续性**：检查每章是否从上一章外部交接打开或记录了有理据的转换、批次末章是否因故事赚到了收束而非因批次结束才收束。

11. **正文与 TXT 格式**：运行 `python scripts/validate_novel_output.py <project> --chapters <reviewed chapters>`。
   - 写作心法、TXT 格式、结尾规则和 draft self-check 详见 `docs/WRITING_CRAFT.md`；审查时按其中规则清单对照。
   - Treat validator failures as required fixes, not suggestions.
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

12. **读者回报**
   - 检查每章是否在 review 或 writing_packet 中有 Reader Reward Check。
   - 检查回报是否出现在实际正文中，而不只是计划中。
   - 标记只推进设定却没有 payoff/揭示/代价/杠杆变化/关系变化/难忘小说素材的章节。

13. **模型路由**
   - 检查 `meta/model_policy.yml` 是否存在。
   - 检查 writing_packet / round context pack / session log 中是否记录了多模型使用情况。
   - 标记任何看起来只由 fast/cheap 模型完成的正文、active_flow、rolling_plan、受保护文件修改或正史合并。

## 输出格式

14. **记忆工程卫生**
   - 检查所有 YAML 文件是否有重复 key（YAML 解析器静默覆盖，不会报错）。
   - 检查 `entities/characters.yml` 中每个有实质性变化的角色的 `change_history` 是否有条目。
   - 检查 `ledgers/narrative_debts.yml`、`ledgers/foreshadowing.yml` 中状态字段的拼写一致性（`paid`/`partiall_paid` 等）。
   - 检查 `ledgers/world_state.yml` 的资源/危机/势力条目是否与最近章节事件同步。
   - 检查 `canon_delta.yml` 和 `summary.yml` 的 `actual_handoff` 是否存在、是否与 `active_flow.yml` 的 `last_cut.current_handoff` 一致。
   - 如果发现 YAML 错误或数据不一致 → 列入必须修复项，不是可接受的弱点。

15. **文笔多样性**
   - 检查最近 3 章正文是否存在高频重复句式（硬规则："不是X而是Y / 不是X，是Y"默认禁用，确需使用每章最多 1 次且 review 必须说明不可替代性；超过即为必须修复。也检查三连否定内心声明、元叙述、箭头/编号式认知总结、连续段落以同一句式开头、大量"他/她做了A，然后做了B"的平铺直叙）。
   - 句式重复不一定是单章问题——可能是模型默认腔。标记为风险并给出替换建议。

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
- 推荐重新生成 writing_packet——如果写作输入记录不完整。
