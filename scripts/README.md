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

状态漂移检查默认随 planning 检查启用：

```powershell
python scripts/validate_novel_output.py projects/my-novel --chapters ch011 ch012 ch013
python scripts/validate_novel_output.py projects/my-novel --chapters ch013 --drift-lookback 5
python scripts/validate_novel_output.py projects/my-novel --chapters ch013 --skip-state-drift
```

受保护文件修改可见性检查：

```powershell
python scripts/validate_novel_output.py projects/my-novel --chapters ch013 --check-protected-files
```

定位 `"不是X而是Y / 不是X，是Y"` 候选句式：

```powershell
python scripts/check_not_but.py projects/my-novel --chapters ch011 ch012 ch013 --files draft.txt
python scripts/check_not_but.py projects/my-novel --chapters ch011 ch012 ch013
python scripts/check_not_but.py projects/my-novel/chapters/ch011/final.txt
```

`check_not_but.py` 只列出位置和上下文，不改正文。候选数超过 `--limit` 时返回失败码，因此可以作为 `draft.txt` → `reader_pass.md` / `final.txt` 之间的硬门禁。它的用途是让 agent 一次性看完整章候选位置，集中判断保留哪一处、改掉哪些，避免 summary/canon_delta 合并后才回头改正文。

脚本会检查：

- `final.txt` 正文段落之间是否错误空行。
- `final.txt` 是否因为误解 TXT 规则而写成少数巨大段落。
- 是否存在超过 220 中文字的超长段落，或大量超过 160 字的长段落。
- 章节结尾是否是主角复盘、计划、抽象短句、看夜色、吹灯等默认 AI 收束。
- 每章是否具备必需文件：writing_packet、draft、final、review、summary、canon_delta。
- 每章是否具备质量门文件：reader_pass、memory_update_plan（缺失先作为 warning）。
- reader_pass 是否阻止进入 final。
- reader_pass 曾要求 revise 时，是否存在 reader_recheck 且结果为 pass。
- reader_pass 是否记录冷读执行者（cold_reader_subagent / same_agent_fallback）。
- reader_pass 是否包含局部润色建议。
- review 是否与实际产物状态一致，不能仍写 summary/canon_delta/memory_update_plan 待生成。
- review 是否记录 post-merge QA / 最终 QA 结果；只在合并后跑过的 validator 才算完成门禁。
- review 中当前状态同步 checklist 不能仍未勾选；只写 canon_delta、不合入 entities/ledgers/planning 会被视为未完成。
- canon_delta 中有实质状态变化时，`state_sync` 是否以 `merged` / `updated` / `synced` 确认已合入对应当前状态文件；`n/a` 不能用于非空变化字段。
- `entities/characters.yml` 中发生实质变化的角色是否有 `last_updated` 或 `change_history` 指向对应章节。
- memory_update_plan 是否保持草案身份、使用 diff-only 格式，不能声称 archivist 或 director 已直接合并文件。
- writing_packet 是否包含读取证据、Writing Card、Pre-Draft Self Check、reader reward、cut continuity 和写后更新清单。
- Writing Card 是否包含 time_span、ending_type、position_in_flow、enters_via、opening_sensory、scene_moments、ending_gesture。
- planning/merge_previews 是否仍有 high-confidence pending 操作。
- review 是否包含 Reader Reward Check、TXT Format Check 和 Memory Update Check。
- rolling_plan 是否仍堆积 completed 章节，是否与 completed_plan_log 重叠，是否缺少 completed_plan_log / future_backlog。
- `active_flow.yml` 的 `last_cut.chapter` 是否落后于正在验证的章节批次。
- `rolling_plan.yml` 是否超过 20000 字节，过大时提示压缩远期条目到 `future_backlog.yml`。
- `--check-protected-files` 是否能看到受保护文件的变更日志入口。
- `rolling_plan.yml` / `current_round.yml` 是否残留 `bridge_to_next`、`continuity_from_previous`、`next_hook` 等旧字段。
- `summary.yml` 是否仍使用 `next_hook`。
- 项目内 YAML 文件是否可解析；关键状态文件是否存在重复 key。
- 正文是否超过"不是X而是Y / 不是X，是Y"每章最多 1 次的硬限制；如保留 1 次，review 是否说明不可替代性。
- 正文是否出现三连否定内心声明、原书/原著元叙述、箭头/编号式认知总结。
- 批次内是否连续使用 `ending_type: next_step_decision` 或 `time_span: 一天`。

未来还可以添加：

- `new_project`：从 `templates/project/` 创建新小说项目。
- `validate_project`：更完整的 schema 级必填字段校验。
- `compile_context`：根据当前任务生成 writing packet。
- `export_novel`：拼接章节 `final.txt`。
- `check_missing_updates`：检查章节写完后是否遗漏摘要、delta 或账本更新。
