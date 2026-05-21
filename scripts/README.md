# Scripts

MVP 最初不依赖自动化脚本，但写作测试显示：TXT 空行、段落密度失衡、复盘式结尾、旧规划字段这几类问题只靠 skill 文档很容易漏掉。

因此当前加入一个轻量质检脚本：

```powershell
python scripts/validate_novel_output.py projects/my-novel --chapters ch011 ch012 ch013
```

自动修正文段空行：

```powershell
python scripts/validate_novel_output.py projects/my-novel --chapters ch011 ch012 ch013 --fix-format
```

脚本会检查：

- `final.txt` 正文段落之间是否错误空行。
- `final.txt` 是否因为误解 TXT 规则而写成少数巨大段落。
- 是否存在超过 220 中文字的超长段落，或大量超过 140 字的长段落。
- 章节结尾是否是主角复盘、计划、抽象短句、看夜色、吹灯等默认 AI 收束。
- 每章是否具备必需文件：brief、context_pack、draft、final、review、summary、canon_delta。
- context pack 是否包含读取证据、reader reward、cut continuity 和写后更新清单。
- review 是否包含 Reader Reward Check、TXT Format Check 和 Memory Update Check。
- rolling_plan 是否仍堆积 completed 章节，是否缺少 completed_plan_log / future_backlog。
- `rolling_plan.yml` / `current_round.yml` 是否残留 `bridge_to_next`、`continuity_from_previous`、`next_hook` 等旧字段。
- `summary.yml` 是否仍使用 `next_hook`。

未来还可以添加：

- `new_project`：从 `templates/project/` 创建新小说项目。
- `validate_project`：检查 YAML 格式和必填字段。
- `compile_context`：根据当前任务生成 context pack。
- `export_novel`：拼接章节 `final.txt`。
- `check_missing_updates`：检查章节写完后是否遗漏摘要、delta 或账本更新。
