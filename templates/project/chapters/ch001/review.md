# 章节审查

## Final 前质量门

- `prompt.md` 是否存在且控制在 500 字以内？
- draft self-check 是否发现并修复了连续解释、连续任务执行、连续无动作/无对话/无感官输入的问题？
- `python scripts/check_not_but.py <project> --chapters ch001 --files draft.txt` 是否在 final 前通过？如果超过 1 次，draft 如何改过？
- 是否搜索并清除了正文里的工程/元引用（如 `ch00`、`上一章`、`本章`、`读者`、`章纲`、Markdown/YAML 痕迹）？
- `reader_pass.md` 是否给出 `pass`？
- 如果 `reader_pass.md` 曾给出 `revise required`，draft 如何改过？
- 本章最值得保留的一段是哪一段？

## 章纲贴合度

本章是否跟随了详细章纲，但没有写成章纲翻译？

## 连续性

是否自然地从上一章延续？开头是否承接了上一章的 actual_handoff，或者记录了有理据的切换？

## 虚构素材

什么具体的场景、动作、物件、对话或后果让这读起来像小说而不是报告？

## 叙事织入检查

- 本章唯一核心推进是什么？
- 本章是否试图完成太多任务？
- 哪些叙事织入节拍主要用于人物日常反应、场景即时质感、关系温度波动？
- 是否连续两页每一段都在功能性推进剧情/传递信息？
- 主角在这里是一个活人，还是只是一个决策引擎？

## 网文节奏检查

- 本章功能：crisis / cultivation / travel / trade / social_conflict / reveal / aftermath / investigation / operation / relationship / building / transition / face_slap / breakthrough / auction / showing_off / competition / dungeon_rule
- 用了什么压力曲线？压力是否被延迟、释放或转移——而不只是"完成"？
- 本章承接和留下的读者疑问是什么？
- 本章新增核心信息变量是否超过 1-2 个？
- Side yield 是否进入长期记忆？
- 规则/系统/制度/功法如果出现——是否通过事件、代价、误用或反应验证，而不只是解释？

## Reader Reward Check

- 本章给了读者什么具体回报？
- 推进或偿还了什么已有期待/债务/承诺？
- 制造了什么新期待？
- 外部代价/杠杆变化/揭示/关系变化是什么？
- 什么画面/台词/动作/物件是难忘的？

## Sample Alignment Check

- 如果 `style/samples.md` 非空，本章是否贴近样本的句子节奏、段落手感、描写温度和对话语感？
- `prompt.md` 是否写入了 3-5 条正向样本文风锚点，而不是只有禁止性规则？
- 本章是否误迁移了样本人名、地名、剧情、专有设定或标志性桥段？
- 如果文风偏离，final 前已如何局部修正？

## 结尾检查

- 是否避免了主角复盘/分析/"下一步"思考？
- 结尾是否通过行动、代价、到场、暴露、压力、关系变化或信息可见性变化在世界中留下运动？
- 如果最后一段是短句氛围收束——有没有具体内容支撑？

## 轮次容器检查

- 本章没有因为三章批次而强制打开/重置/关闭。
- 如果是批次末章，没有因批次结束变成总结——除非 active flow 确实赚到了 payoff。
- 交接指向具体的外部延续。

## TXT 格式检查

- 标题后一空行，正文段落间无空行。
- 额外空行只用于场景切换。
- 段落密度适合手机阅读——不是几个巨大段落。
- 多数段落 40-160 字，超过 220 字视为格式失败（除非 review 中说明理由）。
- `python scripts/validate_novel_output.py <project> --chapters ch001 --fix-format` 通过。

## 弱点或风险

至少指出一个弱点或风险。**必须给出具体的修改建议，不能只说"可接受"或"后续观察"。** 如果已修改，描述修改方式。

### 建议修改

如果重写，具体怎么改？不重写的话，下一章如何弥补？

## 记忆工程卫生检查

- [ ] YAML 无重复 key（`grep -c` 同名 key 在同一个 YAML 文档中不超过 1 次）。
- [ ] 所有有实质性变化的角色的 `change_history` 非空。
- [ ] `narrative_debts.yml` 状态字段拼写正确（`open`/`in_progress`/`paid`/`abandoned`）。
- [ ] `world_state.yml` 资源/危机/势力条目与本章事件同步。
- [ ] `canon_delta.yml` 的 `actual_handoff` 与 `active_flow.yml` 的 `last_cut.current_handoff` 一致。
- [ ] 没有重复的 YAML key 覆盖问题。

## 记忆更新检查

- [ ] `summary.yml` 已更新。
- [ ] `canon_delta.yml` 已更新（含 actual_handoff）。
- [ ] `canon_delta.yml` 已填写 `state_sync`，所有实质变化都指向对应当前状态文件或标注 N/A。
- [ ] `entities/` 当前状态变化已同步（含 change_history）。
- [ ] `ledgers/` 当前状态变化已同步。
- [ ] `planning/active_flow.yml` 已更新 last_cut 和 current_handoff。
- [ ] `planning/rolling_plan.yml` 已刷新。
- [ ] 未把 `canon_delta.yml` 当作当前状态替代品；如本章无相关 state 变化，已明确标注 N/A。

## Post-Merge QA / 最终 QA

- [ ] post-merge QA 在 director 合并全部记忆和 planning 更新之后运行。
- [ ] 运行命令：`python scripts/validate_novel_output.py <project> --chapters ch001`
- [ ] 结果：Validation passed / Validation passed with warnings / failed。
- [ ] 如果有 warning，列出 warning 和处理理由。
- [ ] post-merge QA 之后没有再修改 `entities/`、`ledgers/`、`planning/`、`summary.yml` 或 `canon_delta.yml`；如果改过，已重新运行 QA。
