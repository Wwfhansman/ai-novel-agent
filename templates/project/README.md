# Novel Project Template

这是 AI Novel Agent 的空白小说项目模板。

使用方式：

1. 复制整个 `templates/project/` 到 `projects/<project-id>/`。
2. 使用 `novel-bootstrap` 根据用户 seed 初始化内容。
3. 写作时以项目文件为唯一长期记忆，agent 对话只是临时工作台。

核心规则：

- 正文细节保存在 `chapters/*/final.txt`。
- 当前状态保存在 `entities/`、`ledgers/`、`planning/`。
- 近期剧情以 `planning/rolling_plan.yml` 的详细章纲为权威来源。
- `planning/current_round.yml` 只是本轮三章摘录。
- `canon_delta.yml` 是章节变更日志，不是当前状态总表。
- 写作前必须生成 context pack。
- `final.txt` 正文段落之间只换行，不额外空行。
