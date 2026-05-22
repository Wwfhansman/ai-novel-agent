# 章节审查

## Reader Reward Check
- 本章给了读者什么：超自然信号的首次呈现（旧灯芯残留陌生记忆）+ 一个具体的危险物证（灯芯碎片）。
- 制造了什么新期待：巡灯署为什么要回收旧灯芯？碎片如果被发现会怎样？那个声音是谁的？
- 外部变化：林栖从普通修灯人变成了藏匿线索的人——她的工作不再安全。

## TXT Format Check
- 标题格式正确："第一章 旧灯芯"。
- 标题后有一空行，正文段落之间无空行。
- 本章约 2100 字，正文段落 40 段，段落密度正常。
- 多数段落 25-80 字，最长段约 130 字，无超大段落。
- 场景切换（灯廊内→巷口→灯廊内）通过自然叙述衔接，无需分隔符。

## 叙事织入检查
- 人物日常反应：林栖紧张时默数螺丝、助手抱怨大雾费灯油。
- 场景即时质感：焦油和湿灯芯的气味、铜罩烫手、灯笼光晕在雾里模糊。
- 关系温度波动：助手从闲聊到公事公办的转变、领头的审视目光。

## Memory Update Check
- `summary.yml` 和 `canon_delta.yml` 已记录 actual_handoff。
- `planning/active_flow.yml` last_cut 已更新。
- entities/ledgers/planning 当前状态已同步。
- 注意：canon_delta 的 actual_handoff 和 rolling_plan 的 planned_handoff 在本章中一致（"巡灯署推开灯廊门，领头人索要旧灯芯"），但后续章节出现偏差时应以 canon_delta 为准。

## Post-Merge QA / 最终 QA
- 示例项目 post-merge validator 已运行：`python3 scripts/validate_novel_output.py projects/example-project --chapters ch001`。
- 结果：Validation passed with 1 warning（短氛围结尾示例保留）。
- post-merge QA 后未再修改示例 canon 或 planning 状态。
