# OpenCode 多 Agent 配置

本项目当前采用 1 个 primary agent + 6 个 subagent：

- `novel-director`：主控 / 导演 agent。
- `novel-architect`：主编剧 / 世界大脑 subagent。
- `novel-planner`：写作前规划编译 subagent。
- `novel-writer`：正文作者 subagent。
- `novel-cold-reader`：冷读责编 subagent。
- `novel-qa`：机械 QA subagent。
- `novel-archivist`：严格记忆档案员 subagent。

## 模型配置

`novel-cold-reader` 和 `novel-qa` 当前配置为：

```yaml
model: deepseek/deepseek-v4-flash
```

`novel-architect`、`novel-planner`、`novel-writer` 和 `novel-archivist` 当前配置为更强一点的：

```yaml
model: opencode-go/deepseek-v4-pro
```

OpenCode 的模型写法是 `provider/model-id`。请以 `/models` 输出为准；如果你的提供商 ID 不同，同步修改 README 和 `.opencode/agents/*.md` 中的 `model:` 行。

如果你使用 OpenCode Go 套餐，先确认可用模型：

```text
/models
```

如果你的 OpenCode 模型列表里显示的模型 ID 和本项目配置不同，直接修改：

```text
.opencode/agents/novel-cold-reader.md
.opencode/agents/novel-qa.md
.opencode/agents/novel-planner.md
.opencode/agents/novel-architect.md
.opencode/agents/novel-writer.md
.opencode/agents/novel-archivist.md
```

里的 `model:` 行。

## 模型路由理由

可以。

`novel-cold-reader` 不做剧情决策、不改正史、不更新账本，只判断 draft 的读者体验和文笔自然度。轻量模型足够用于发现明显的生硬、任务报告感、对话信息交换、节奏过密等问题。

`novel-qa` 只做机械检查、validator 解释、格式和流程漏项检查，也适合轻量模型。

`novel-architect` 负责未来 10-30 章的世界运营、卷节奏、支线生命周期、信息释放、主角成长预算和可写素材开发。它需要综合全书约束、当前卷目标、active_flow、rolling_plan、entities/ledgers 和近章推进，必须使用强模型。

`novel-planner` 会把全局方向压缩成可写的 `writing_packet.md`，必须理解 active_flow、rolling_plan、伏笔分量、人物语感和章节切分，建议使用强模型。

`novel-writer` 直接生成正文 draft/final，必须使用强模型。

`novel-archivist` 只生成记忆更新草案，不直接合并正史。它可以使用轻量模型，但必须严格保守：所有 proposed_change 都要有 final.txt 证据；不确定就标记 `needs_director_review`，由主控 agent 或人类确认。

不建议用轻量模型承担：

- `final.txt` 正文最终修订；
- `draft.txt` 正文生成；
- `planning/active_flow.yml` 重构；
- `planning/rolling_plan.yml` 重大改动；
- `planning/story_architecture.yml` 或 `planning/thread_board.yml` 的战略调整；
- `planning/development_packs/` 中的未来 10-30 章开发判断；
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
@novel-planner 请根据 round context pack 为 projects/<name> chXXX 生成 writing_packet.md
@novel-architect
project: projects/<name>
context_pack: projects/<name>/planning/context_packs/architect_context_pack_001.md
output: projects/<name>/planning/development_packs/dev_001.md

请基于当前正史、当前卷目标、active_flow、rolling_plan、story_architecture、thread_board 和近 6-9 章推进，开发未来 10-30 章的世界扩张、支线、势力行动、节奏和 rolling_plan 插入建议。只写 development pack，不合并正史文件。
@novel-writer 请根据 projects/<name>/chapters/chXXX/writing_packet.md 和上一章结尾写 draft.txt
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

`novel-architect` 只负责写作前的故事开发和世界运营。它可以生成 `planning/development_packs/dev_XXX.md`，并建议如何更新 `story_architecture.yml`、`thread_board.yml`、`future_backlog.yml`、`rolling_plan.yml`、`entities/` 和 `ledgers/`。它不能写正文，不能合并当前状态，不能直接修改受保护文件。architect 的建议必须由 director 审核后才能进入项目正史或近期规划。

当 `rolling_plan.yml` 接近耗尽、世界变窄、连续任务推进、主角成长过快、支线断供、进入新地图/新势力/新卷，或用户要求开发后续剧情时，director 应先调用 `novel-architect`，再让 `novel-planner` 生成单章 writing packet。

`novel-planner` 只负责写作前规划编译。它可以生成 `writing_packet.md` 草案，必要时提出 `rolling_plan.yml` 局部细化建议；它不能写正文、不能改 summary/canon、不能合并状态。planner 发现缺少人物语感、伏笔分量、旧章证据或可复用背景落库时，应返回缺口清单，而不是猜。可复用背景包括会影响行动、对白、冲突、移动、身份、代价或后续期待的人物、势力、地点、职位、制度规则、功法代价、历史来历、资源来源、传闻和关键物品。

`novel-writer` 只负责 `draft.txt`、根据 `reader_pass.md` 修 draft，以及质量门通过后的 `final.txt`。它不能修改 `summary.yml`、`canon_delta.yml`、`entities/`、`ledgers/` 或 `planning/`。调用时不要给全量 rolling_plan、账本或 validator 输出；writer 应主要读 `writing_packet.md`、上一章结尾、样本文风锚点和必要前情。

如果 `novel-writer` 返回 packet 缺少人物语感、伏笔分量、关系温度、身体/场景质感、对话模式或背景硬边界，director 应先修 `writing_packet.md`，必要时先补 `entities/` / `ledgers/`，不要让 writer 硬写。

`novel-cold-reader` 可以给局部润色建议，但只站在读者视角指出断句、描写、对话呼吸、转场和句式重复问题；它不接管正文改写，也不检查工程文件。

如果 `style/samples.md` 非空，`novel-director` 应把本章样本文风锚点交给 `novel-cold-reader`。冷读需要检查句子节奏、段落手感、描写温度、对话语感和情绪处理是否贴近样本，但不能迁移样本素材。

`novel-archivist` 默认只能输出 diff-only 草案，或直接写入 `projects/<name>/chapters/chXXX/memory_update_plan.md` 草案。权限同时兼容仓库根下的 `chapters/chXXX/memory_update_plan.md`。当 director 明确指定 `mode: canon_draft` 或 `mode: full_chapter_memory_draft` 时，它可以产出 `summary.yml` / `canon_delta.yml` 草案，但仍不能合并 entities、ledgers 或 planning。真正合并前，director 先生成 `planning/merge_previews/round_XXX.yml`，review 后再 apply 安全更新。

调用 archivist 时要保持短输入：不要粘贴完整字段说明，不要要求它读取全量 entities、全量 ledgers、上一章全部文件或 volume state，除非本章有明确冲突必须对照。director 在 archivist 返回后必须确认草案已落盘：

```bash
test -s projects/<name>/chapters/chXXX/memory_update_plan.md
```

如果文件缺失或为空，先检查 subagent 返回值，再决定写入返回草案或用更短输入重试。

`novel-qa` 必须区分 `phase: pre_merge` 和 `phase: post_merge`。pre-merge QA 只是预检查；post-merge QA 必须在 director 合并 `summary.yml`、`canon_delta.yml`、`entities/`、`ledgers/`、`planning/` 并清理 merge preview 的 high-confidence pending 操作之后运行。只有 post-merge QA 通过，本章才能标记完成。

post-merge QA 之后不要再改 canon 或 planning 文件。若必须改，重新运行 post-merge QA。

## 当前阶段边界

当前拆出：

- 正文 draft/final 写作；
- 编剧层 development pack；
- 写作前 planning packet 编译；
- 冷读；
- 机械 QA。
- 记忆更新草案；
- 可选 summary/canon_delta 草案。

暂不拆：

- summarizer agent；
- merger agent；

`novel-archivist` 不直接写 `entities/`、`ledgers/` 或 `planning/`。它只产出草案，最终合并由 `novel-director` 完成。
