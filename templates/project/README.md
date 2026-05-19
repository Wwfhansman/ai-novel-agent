# Novel Project Template

这是 AI Novel Agent 的空白小说项目模板。

使用方式：

1. 复制整个 `templates/project/` 到 `projects/<project-id>/`。
2. 使用 `novel-bootstrap` 根据用户 seed 初始化内容。
3. 写作时以项目文件为唯一长期记忆，agent 对话只是临时工作台。
4. 根据实际模型填写 `meta/model_policy.yml`。如果暂时不切换模型，保留角色占位符也可以。

核心规则：

- 正文细节保存在 `chapters/*/final.txt`。
- 当前状态保存在 `entities/`、`ledgers/`、`planning/`。
- 当前连续剧情流以 `planning/active_flow.yml` 为权威来源。
- 近期剧情以 `planning/rolling_plan.yml` 的详细章纲为权威来源。
- `planning/current_round.yml` 只是生产批次摘录，不是叙事单位。
- `canon_delta.yml` 是章节变更日志，不是当前状态总表。
- 写作前必须生成 context pack。
- `meta/model_policy.yml` 决定哪些任务可以交给快模型，哪些必须由强模型或人类确认。
- `final.txt` 正文段落之间只换行，不额外空行；但必须正常分段，不能把一章压成少数巨大段落。
