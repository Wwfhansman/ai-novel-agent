# 章节审查

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

至少指出一个弱点或风险。如果已修改，描述修改方式。

## 记忆更新检查

- `summary.yml` 已更新。
- `canon_delta.yml` 已更新（含 actual_handoff）。
- `entities/` 当前状态变化已同步。
- `ledgers/` 当前状态变化已同步。
- `planning/active_flow.yml` 已更新 last_cut 和 current_handoff。
- `planning/rolling_plan.yml` 已刷新，未来章节不再重复已完成选择。
