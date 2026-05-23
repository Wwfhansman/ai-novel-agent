# OpenCode 多 Agent 配置

本项目采用 1 个 primary agent + 3 个 subagent：

- `novel-director`：主控 / 导演 agent。
- `novel-cold-reader`：冷读责编 subagent。
- `novel-qa`：机械 QA subagent。
- `novel-archivist`：严格记忆档案员 subagent。

## 模型配置

`novel-cold-reader` 和 `novel-qa` 当前配置为：

```yaml
model: opencode-go/deepseek-v4-flash
```

`novel-archivist` 当前配置为更强一点的：

```yaml
model: opencode-go/deepseek-v4-pro
```

OpenCode 的模型写法是 `provider/model-id`。OpenCode Go 官方套餐的 provider 机器名是 `opencode-go`，不是 `opencode`，也不是带空格的 `OpenCode Go`。

如果你使用 OpenCode Go 套餐，先确认可用模型：

```text
/models
```

如果你的 OpenCode 模型列表里显示的模型 ID 和本项目配置不同，直接修改：

```text
.opencode/agents/novel-cold-reader.md
.opencode/agents/novel-qa.md
.opencode/agents/novel-archivist.md
```

里的 `model:` 行。

## 为什么这两个可以用轻量模型

可以。

`novel-cold-reader` 不做剧情决策、不改正史、不更新账本，只判断 draft 的读者体验和文笔自然度。轻量模型足够用于发现明显的生硬、任务报告感、对话信息交换、节奏过密等问题。

`novel-qa` 只做机械检查、validator 解释、格式和流程漏项检查，也适合轻量模型。

`novel-archivist` 只生成记忆更新草案，不直接合并正史。它可以使用轻量模型，但必须严格保守：所有 proposed_change 都要有 final.txt 证据；不确定就标记 `needs_director_review`，由主控 agent 或人类确认。

不建议用轻量模型承担：

- `final.txt` 正文最终修订；
- `planning/active_flow.yml` 重构；
- `planning/rolling_plan.yml` 重大改动；
- canon 合并；
- protected files 修改；
- 终局级设定判断。

这些仍应由主控 agent 使用强模型或人类确认。

## 使用方式

进入 OpenCode 后默认 agent 是 `novel-director`，由 `opencode.json` 指定：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "default_agent": "novel-director"
}
```

你也可以手动调用 subagent：

```text
@novel-cold-reader 请冷读 projects/<name>/chapters/chXXX/draft.txt
@novel-qa phase: pre_merge，请检查 projects/<name> chXXX 的质量门和 validator
@novel-archivist
project: projects/<name>
chapter: chXXX
output: projects/<name>/chapters/chXXX/memory_update_plan.md

只读取：
- chapters/chXXX/final.txt
- chapters/chXXX/summary.yml
- chapters/chXXX/canon_delta.yml
- chapters/chXXX/writing_packet.md
- planning/active_flow.yml
- planning/rolling_plan.yml
- 本章明确涉及的 entities/ledgers 条目

写入 diff-only memory_update_plan.md 草案。不要修改其他文件。
@novel-qa phase: post_merge，请在 director 合并 summary/canon_delta/entities/ledgers/planning/volume 后检查 projects/<name> chXXX
```

正常生产时建议让 `novel-director` 调用它们，而不是手动反复切换。

`novel-cold-reader` 可以给局部润色建议，但只站在读者视角指出断句、描写、对话呼吸、转场和句式重复问题；它不接管正文改写，也不检查工程文件。

如果 `style/samples.md` 非空，`novel-director` 应把本章样本文风锚点交给 `novel-cold-reader`。冷读需要检查句子节奏、段落手感、描写温度、对话语感和情绪处理是否贴近样本，但不能迁移样本素材。

`novel-archivist` 只能输出 diff-only 草案，或直接写入 `projects/<name>/chapters/chXXX/memory_update_plan.md` 草案。权限同时兼容仓库根下的 `chapters/chXXX/memory_update_plan.md`。它不能声称“已直接更新文件”或“已在 director 监督下合并”，也不能直接修改 summary、canon_delta、entities、ledgers 或 planning。真正合并前，director 先生成 `planning/merge_previews/round_XXX.yml`，review 后再 apply 安全更新。

调用 archivist 时要保持短输入：不要粘贴完整字段说明，不要要求它读取全量 entities、全量 ledgers、上一章全部文件或 volume state，除非本章有明确冲突必须对照。director 在 archivist 返回后必须确认草案已落盘：

```bash
test -s projects/<name>/chapters/chXXX/memory_update_plan.md
```

如果文件缺失或为空，先检查 subagent 返回值，再决定写入返回草案或用更短输入重试。

`novel-qa` 必须区分 `phase: pre_merge` 和 `phase: post_merge`。pre-merge QA 只是预检查；post-merge QA 必须在 director 合并 `summary.yml`、`canon_delta.yml`、`entities/`、`ledgers/`、`planning/` 并清理 merge preview 的 high-confidence pending 操作之后运行。只有 post-merge QA 通过，本章才能标记完成。

post-merge QA 之后不要再改 canon 或 planning 文件。若必须改，重新运行 post-merge QA。

## 当前阶段边界

当前拆出：

- 冷读；
- 机械 QA。
- 记忆更新草案。

暂不拆：

- writer agent；

`novel-archivist` 不直接写 `summary.yml`、`canon_delta.yml`、`entities/`、`ledgers/` 或 `planning/`。它只产出草案，最终合并由 `novel-director` 完成。
