# 多 Agent 改进规划方案

本文档规划 AI Novel Agent 从“主控 agent 承担大多数工作”升级为“专属强 agent 协作流水线”的路线。核心目标不是增加 agent 数量，而是降低心智切换、减少上下文污染，并保持长篇小说的连续性、文风稳定性和正史一致性。

## 1. 结论

当前 `novel-director` 承担了过多职责：

- 读取项目状态；
- 刷新 `active_flow.yml` / `rolling_plan.yml`；
- 生成 `writing_packet.md`；
- 写 `draft.txt`；
- 处理冷读反馈；
- 写 `final.txt`；
- 生成 summary / canon delta / memory plan；
- 合并 `entities/`、`ledgers/`、`planning/`；
- 跑 QA 和 validator。

这会让同一个上下文在导演、作者、编辑、档案员、QA 工程师之间反复切换。长篇小说最怕的不是单次失败，而是连续生产中风格、记忆和规划逐轮漂移。

改进方向：

- 先使用 OpenCode 原生 subagent，暂不把 oh-my-opencode 放进主路径。
- 第一阶段只新增 `novel-writer`，验证最关键假设：writer 能否仅凭高质量 `writing_packet.md` 写出合格 draft。
- 第二阶段再新增 `novel-planner`，让规划和正文写作分离。
- 第三阶段再决定是否把 summary / canon_delta 交给 `novel-archivist` 扩展处理，或继续由 director 生成。
- `novel-merger` 暂不新增。工程合并先保持脚本化：由 director 调用 `round_state_merge.py preview/apply`。
- 最终稳定形态优先控制在 6 个核心角色：director、planner、writer、cold-reader、archivist、qa。

## 2. 外部资料依据

OpenCode 官方文档确认：

- OpenCode 有 primary agent 和 subagent；
- subagent 可通过 `@agent-name` 手动调用，也可由 primary agent 通过 task 工具调用；
- `permission.task` 可控制 primary agent 能调用哪些 subagent；
- agent 级 `permission` 可以覆盖全局权限；
- 权限支持 `allow` / `ask` / `deny`。

参考：

- [OpenCode Agents](https://opencode.ai/docs/agents/)
- [OpenCode Permissions](https://opencode.ai/docs/permissions/)

oh-my-opencode 公开仓库显示它是面向 OpenCode 的多 agent / MCP / LSP / AST / Claude Code 兼容层增强项目，偏代码工程编排。仓库 README 同时明确警告：`ohmyopencode.com` 不是该项目官方站点，官方下载应以 GitHub releases 为准。

参考：

- [opensoft/oh-my-opencode](https://github.com/opensoft/oh-my-opencode)

工程判断：

- OpenCode 原生能力足够先做小说领域 agent 分工。
- oh-my-opencode 的价值在外层调度、后台 agent、工具集成，不在小说正史协议本身。
- 过早引入 oh-my-opencode 会增加依赖、权限、安全和配置成本，不能自动解决小说记忆、伏笔、文风和 canon 问题。

## 3. 设计原则

### 3.1 每个 agent 都强，但不全知

强 agent 的定义不是读得多，而是：

- 输入干净；
- 任务边界窄；
- 判断标准明确；
- 输出可审计；
- 不能越权修改别的层。

不要把全书、全规则、全 YAML、全历史都广播给每个 agent。那会导致 token 过载、理解不一致和噪声放大。

### 3.2 director 是唯一全局叙事决策者

只有 director 或人类可以决定：

- 当前 flow 是否改变方向；
- `rolling_plan.yml` 是否重构；
- 是否接受 final；
- 是否合并 canon；
- 是否修改 protected files；
- 是否允许跳过 warning 继续。

其他 agent 只产出草案、诊断、正文候选或候选操作。

### 3.3 文件 artifact 是交接，不靠聊天上下文继承

多 agent 协作必须通过项目文件交接：

- `planning/context_packs/round_XXX_context_pack.md`：本轮导演共识和上下文编译；
- `writing_packet.md`：本章写作输入；
- `draft.txt`：作者初稿；
- `reader_pass.md` / `reader_recheck.md`：冷读门；
- `final.txt`：正文正史；
- `summary.yml`：章节摘要；
- `canon_delta.yml`：章节变化日志；
- `memory_update_plan.md`：记忆更新草案；
- `merge_preview.yml`：工程合并预览；
- `review.md`：质量和工程最终记录。

agent 对话只是工作台，项目文件才是长期记忆。

### 3.4 writer 的上下文要少，但要浓

writer 不应该读 20 个工程文件。writer 应主要读：

- 本章 `writing_packet.md`；
- 上一章结尾片段；
- `style/samples.md` 的本章风格锚点；
- 必要的 1-2 句前情；
- 修稿阶段读取 `reader_pass.md`。

但 `writing_packet.md` 必须足够浓。除了已有 `Chapter Design` / `Writing Execution`，还应明确纳入：

- 人物语感示例：本章关键人物如何说话、如何停顿、如何回避；
- 伏笔分量感：本章涉及的道具、旧事、承诺、债务在读者心里的重量；
- 关系温度：本章角色之间是试探、亲近、疏离、敌意还是误读；
- 身体和场景质感：混合状态、伤病、紧张、疲惫等不能只写概念；
- 权谋或社交话术样式：重要对话不能只写信息交换。

writer 不全知，但必须拿到足够可写的材料。

## 4. 目标架构

### 4.1 稳定形态：6 个核心角色

| Agent | 类型 | 核心职责 | 是否写正文 | 是否改正史状态 |
| --- | --- | --- | --- | --- |
| `novel-director` | primary | 编排、最终决策、canon 接受、冲突处理 | fallback 才写 | 可最终确认 |
| `novel-planner` | subagent | 规划草案、rolling plan 细化、writing packet 草案 | 否 | 否 |
| `novel-writer` | subagent | 写 draft，按反馈修 draft/final | 是 | 否 |
| `novel-cold-reader` | subagent | 冷读体验、文笔、人物体温 | 否 | 否 |
| `novel-archivist` | subagent | summary/canon/memory 草案或 diff-only 记忆建议 | 否 | 否 |
| `novel-qa` | subagent | validator、格式、流程、状态同步门禁 | 否 | 否 |

### 4.2 暂不新增的角色

`novel-merger` 暂不新增。

原因：

- 它本质上是 `scripts/round_state_merge.py preview/apply` 的封装；
- 多一个 agent 会增加 prompt、输出审查和权限维护成本；
- 合并阶段更适合先脚本化，再决定是否 agent 化。

`novel-summarizer` 暂不单独新增。

原因：

- summary / canon_delta 与 memory_update_plan 都是 final 后的 canon extraction；
- 单独拆出 summarizer 会增加一次 agent 调用和一次审核；
- 可先扩展 `novel-archivist`，让它在受限模式下产出 summary/canon_delta 草案，或继续由 director 做。

### 4.3 planner 的边界

`novel-planner` 不是另一个全局 director。它不应该拿到和 director 一样大的上下文后重新判断全书方向。

推荐边界：

- Phase 1b 初期，planner 只生成 `writing_packet.md` 草案；
- 如果稳定，再让 planner 协助细化 `rolling_plan.yml` 的未来章节；
- `active_flow.yml` 的方向改变仍由 director 决定；
- director 必须审核 planner 产物。

## 5. Agent 职责细则

### 5.1 novel-director

职责：

- 读取全局权威状态；
- 判断本轮 active flow；
- 生成或确认 round context pack；
- 分配任务给 planner / writer / cold-reader / archivist / qa；
- 审核 `writing_packet.md` 是否足以写作；
- 审核 final 是否可接受；
- 审核 summary / canon_delta / memory_update_plan；
- 调用 `round_state_merge.py preview/apply`；
- 处理 manual review、protected file、retcon 和重大设定变更。

禁止：

- 默认亲自写 `draft.txt`；
- 默认亲自冷读；
- 默认亲自手工维护所有 YAML；
- 把全量状态文件塞给每个子 agent。

失败处理：

- 子 agent 空返回：重试一次，输入缩短到必须文件和任务；
- 子 agent 输出越权：丢弃输出，记录到 `review.md` 或 session log；
- 子 agent 与正史冲突：以 `final.txt`、当前状态文件和 director 判断为准；
- 连续两次失败：director fallback，但必须在 `review.md` 记录 fallback 原因。

### 5.2 novel-writer

职责：

- 根据 `writing_packet.md` 写 `draft.txt`；
- 根据 `reader_pass.md` 修改 draft；
- 在 reader_pass / reader_recheck 通过后生成 `final.txt`；
- 保持文风、场景、人物体温、对话自然度。

输入：

- `writing_packet.md`；
- 上一章结尾 500-1000 字；
- 本章风格锚点；
- 必要前情；
- 修稿阶段的 `reader_pass.md`。

禁止：

- 修改 summary / canon_delta；
- 修改 entities / ledgers / planning；
- 重构大纲；
- 自己判断工程完成；
- 用 reader_pass 或 draft_handoff_note 替代 actual_handoff。

失败处理：

- draft 明显机械翻译 packet：退回 writer，要求重写 scene_moments 而不是改小句子；
- draft 偏离 must_happen：director 判断是 packet 错还是 writer 错，必要时先改 packet；
- 文风不贴 samples：补充 3-5 条样本文风锚点后重写局部；
- 连续两次 draft 不合格：换强模型或 director fallback。

权限建议：

```yaml
permission:
  read: allow
  edit:
    "projects/*/chapters/*/draft.txt": allow
    "projects/*/chapters/*/final.txt": ask
    "projects/*/chapters/*/draft_handoff_note.md": allow
    "*": deny
  bash:
    "python scripts/check_not_but.py *": allow
    "python3 scripts/check_not_but.py *": allow
    "*": deny
```

### 5.3 novel-planner

职责：

- 根据 director 的 round context pack 生成 `writing_packet.md` 草案；
- 必要时细化 `rolling_plan.yml` 的章节条目；
- 检查 `time_span`、`ending_type`、`position_in_flow`、`enters_via`、`scene_moments` 是否可写；
- 确保人物语感、伏笔分量、关系温度进入 packet。

输入：

- round context pack；
- `active_flow.yml`；
- `rolling_plan.yml`；
- `longform_blueprint.yml`；
- 相关 entities / ledgers；
- 最近摘要；
- 必要旧章片段。

禁止：

- 写正文；
- 决定 final 是否通过；
- 合并当前状态；
- 修改 protected files；
- 单独改变 active flow 方向。

失败处理：

- packet 像任务清单：director 退回，要求补 `Writing Execution` 和 scene moments；
- packet 漏掉关键伏笔/人物语感：补相关旧章片段后重做；
- packet 与 rolling_plan 冲突：director 仲裁，planner 不自行覆盖；
- packet 过长：保留 writer 必需信息，细节转入 source refs。

权限建议：

```yaml
permission:
  read: allow
  edit:
    "projects/*/planning/rolling_plan.yml": ask
    "projects/*/planning/context_packs/*.md": ask
    "projects/*/chapters/*/writing_packet.md": allow
    "*": deny
  bash: deny
```

### 5.4 novel-cold-reader

保持现有职责。

输入：

- `draft.txt`
- `Writing Card`
- 样本文风锚点
- 必要前情 1-2 句

禁止：

- 读取 rolling_plan；
- 读取 YAML 账本；
- 判断 canon；
- 修工程文件；
- 输出大段代写。

失败处理：

- 输出太泛：要求重审，只列最生硬 3 处和必须重写 1-2 处；
- 输出涉及工程判断：忽略工程部分；
- revise required 后必须有 `reader_recheck.md`。

### 5.5 novel-archivist

第一阶段保持现有 diff-only 记忆草案职责。

第三阶段可选扩展：

- 产出 `summary.yml` 草案；
- 产出 `canon_delta.yml` 草案；
- 同时产出 `memory_update_plan.md`；
- 仍不得直接合并 `entities/`、`ledgers/`、`planning/`。

禁止：

- 不读 draft；
- 不读 reader_pass；
- 不把推测写成事实；
- 不把计划写成已发生；
- 不输出完整数据库重写。

失败处理：

- 把推测写成事实：director 驳回，对应项改为 `needs_director_review`；
- 输出过长：要求 diff-only 重写；
- 文件未落盘：检查返回值，有内容则写入草案，无内容则短输入重试；
- 找不到实体 ID：写 Manual Review，不自行创建。

### 5.6 novel-qa

保持现有机械 QA 职责，并逐步增加 agent ownership 检查。

新增检查方向：

- writer 不应修改 `entities/`；
- archivist 不应声称已合并；
- planner 不应写 final；
- cold-reader 不应判断 YAML；
- director fallback 必须在 review 中说明。

失败处理：

- QA 失败：不得标记 completed；
- post-merge QA 后又改 canon/state/planning：必须重跑；
- warning 可接受时，必须写入 `review.md`。

## 6. 工作流设计

### 6.1 Phase 1a：只新增 novel-writer

目标：验证最关键假设，writer 能否仅凭 `writing_packet.md` 写出合格 draft。

流程：

```text
director 读全局状态
→ director 生成 round context pack
→ director 生成 writing_packet
→ writer 读取 writing_packet + 上章结尾 + 风格锚点
→ writer 写 draft
→ check_not_but
→ cold-reader
→ writer 修 draft
→ director 审核 final
→ 后续工程流程暂由 director 按旧方式完成
```

验收：

- writer 不读取 rolling_plan 全文；
- writer 不读取 entities / ledgers；
- writer 不改 YAML；
- draft 能自然承接上一章；
- cold-reader 不因“任务报告感”要求大重写；
- director 对 prose 的返工量下降。

失败则不继续拆 planner。

### 6.2 Phase 1b：新增 novel-planner

目标：把 planning / packet 编译从 director 身上拆出去。

流程：

```text
director 生成 round context pack
→ planner 生成 writing_packet 草案
→ director 审核 packet
→ writer 写 draft
→ cold-reader
→ writer 修稿
→ director 审核 final
```

验收：

- planner 生成的 packet 能被 writer 直接使用；
- packet 包含人物语感示例、伏笔分量感、关系温度、场景质感；
- director 不需要大幅重写 packet；
- writer 输出质量不下降。

### 6.3 Phase 1c：扩展 archivist 或保留 director 提取 canon

目标：降低 final 后 YAML / canon extraction 的切换成本。

优先方案：

- 暂不新增 summarizer；
- 让 director 继续生成 summary / canon_delta；
- 观察这一步是否仍是瓶颈。

如果仍然痛，再扩展 `novel-archivist`：

```text
archivist 读取 final + writing_packet + 相关状态
→ 输出 summary.yml 草案
→ 输出 canon_delta.yml 草案
→ 输出 memory_update_plan.md
→ director 审核并修正
```

验收：

- 草案忠于 final；
- 不把推测写成事实；
- director 审核成本低于亲自从零写；
- validator 通过率不下降。

### 6.4 工程合并继续脚本化

暂不新增 merger agent。

流程：

```text
director 运行 round_state_merge.py preview
→ director review preview
→ director 运行 round_state_merge.py apply
→ director 处理 manual_review
→ novel-qa post_merge
```

后续只有在以下条件满足时才考虑 agent 化 merger：

- `round_state_merge.py` safe ops 已足够稳定；
- manual_review 数量很高；
- director 在合并阶段仍然明显卡住；
- agent 能稳定解释冲突而不是制造新冲突。

## 7. 上下文与 artifact

### 7.1 不新增 round_directive 文件

review 指出 `round_directive.md` 和 round context pack 重叠，这个判断成立。

调整：

- 不新增 `planning/round_directives/`；
- 在现有 `planning/context_packs/round_XXX_context_pack.md` 中增加 `Director Directive` section；
- 该 section 承担原 round_directive 职责。

`Director Directive` 应包含：

- 本轮 active flow；
- 本轮不要闭合什么；
- 本轮必须推进什么；
- 本轮不能碰的 protected / endgame 内容；
- 本轮涉及的主要角色、道具、伏笔、债务；
- 三章之间的连续事件；
- 允许 writer 自由发挥的范围；
- 禁止模式。

### 7.2 writing_packet 必须更适合 writer

在当前模板基础上增加或强调以下字段：

- `voice_examples`：关键人物语气、停顿、回避方式；
- `foreshadowing_weight`：本章涉及伏笔/道具/旧事的分量；
- `relationship_temperature`：关系温度和误读；
- `body_scene_texture`：身体状态和场景质感；
- `dialogue_mode`：权谋、社交、试探、亲密、冲突等对话模式。

这些不一定都要作为顶层字段，也可以放进 `Writing Execution`，但 writer 必须能直接看见。

## 8. 人机协作点

用户不应该被每个中间文件打断，但必须能在关键点介入。

建议介入点：

- Round Planning Gate：director 生成 round context pack 后，用户可审本轮方向；
- Packet Gate：前 1-2 轮新流程中，用户可抽查 `writing_packet.md`；
- Final Gate：用户可选择抽查 final，尤其是新 writer 首轮；
- Merge Gate：如果 merge preview 有 manual_review 或 protected 相关项，必须让用户确认；
- Change Gate：任何 protected file、主角底线、终局级秘密变化必须用户确认。

默认：

- 普通章节不需要用户每章确认；
- 有 manual_review、protected change、retcon、重大质量下降时才打断用户。

## 9. Token 与成本控制

拆 agent 可能增加总 token。不能假设多 agent 一定更省。

预估：

- 现状单 director：约 50k tokens / 轮；
- 盲目 8 agent：可能到 70k-90k tokens / 轮；
- 渐进 6 agent：目标控制在 55k-65k tokens / 轮，并减少返工。

控制策略：

- Phase 1a 只新增 writer，不增加 planner / summarizer；
- writer 输入限制在 packet + 上章结尾 + 风格锚点；
- cold-reader 不读工程文件；
- archivist 输入短而结构化；
- 每轮记录：agent 调用次数、估算 token、失败次数、validator 重跑次数、正文返工次数。

是否继续拆分，不看理论，只看两轮数据。

## 10. 测试策略

### 10.1 最小端到端测试

先用 1 章测试，不直接在真实长篇主线大规模切换。

测试方式：

- 选一个已有 `writing_packet.md` 的章节；
- 让 `novel-writer` 只读 packet、上章结尾、风格锚点；
- 输出 `draft.txt`；
- 运行 `check_not_but.py`；
- 调用 cold-reader；
- 比较 director 亲自写时的返工量。

通过条件：

- draft 不像任务报告；
- 核心信息没有靠脑内总结硬塞；
- 人物语感不崩；
- 前后承接自然；
- cold-reader 不要求全章重写。

### 10.2 回放测试

可选用已有 round 数据回放：

- 固定已有 final 不动；
- 用当时的 packet 重新让 writer 生成 draft；
- 对比原 final 的风格、信息进入方式、结尾类型。

回放测试不进入 canon，只用于判断 writer 能力。

### 10.3 两轮试运行

Phase 1a 和 Phase 1b 分别至少跑：

- 1 个单章测试；
- 1 个 3 章 round 测试。

记录：

- 调用次数；
- 失败/空返回次数；
- validator 重跑次数；
- cold-reader revise 次数；
- director 手工修正文/修 YAML 时间；
- 用户主观阅读质量。

## 11. 回滚机制

### 11.1 配置回滚

agent 定义、skill、docs 都应单独提交。出现问题时：

- git revert agent 配置提交；
- `novel-director` 回到旧流程；
- 保留已生成章节文件，不自动删除。

### 11.2 章节回滚

如果新 writer 生成的章节质量差：

- 不接受 `final.txt`；
- 保留 `draft.txt` 作为失败样本；
- director 重新写 draft 或换模型重写；
- `summary.yml` / `canon_delta.yml` / state merge 不进入下一阶段。

如果已经写入 final 但未 merge：

- 重写 final；
- 重新生成 summary / canon_delta；
- 重新 QA。

如果已经 post-merge：

- 不静默改历史；
- 走 `novel-change` 或建立 checkpoint；
- 写清楚 retcon / correction。

### 11.3 Artifact 兼容

旧流程和新流程共用：

- `writing_packet.md`
- `draft.txt`
- `final.txt`
- `reader_pass.md`
- `summary.yml`
- `canon_delta.yml`
- `memory_update_plan.md`
- `merge_preview.yml`
- `review.md`

因此回滚时不需要迁移章节目录结构。

## 12. 主要风险与对策

### 风险 1：agent 割裂，前文理解断裂

对策：

- director / planner 保持全局理解；
- writer 只接收高密度 writing packet；
- round context pack 增加 `Director Directive`；
- writing_packet 明确人物语感、伏笔分量和关系温度。

### 风险 2：agent 数量增加导致协调成本上升

对策：

- Phase 1a 只新增 writer；
- Phase 1b 再新增 planner；
- summarizer / merger 不作为第一阶段必需品；
- 每轮记录 token 和返工数据。

### 风险 3：writer 变成机械执行 packet

对策：

- Writing Card 保持 `Chapter Design` / `Writing Execution` 分离；
- writer 优先看 scene_moments、voice_examples、body_scene_texture；
- cold-reader 专门检查任务报告感；
- director 不把 full rolling_plan 给 writer。

### 风险 4：archivist 把推测写成事实

对策：

- 输入只给 final 和相关状态；
- 每个变化必须有 evidence；
- 不确定写 `needs_director_review`；
- director 审核后才合并。

### 风险 5：oh-my-opencode 增加复杂度

对策：

- 不作为 Phase 1 依赖；
- 只在测试项目试；
- 只采纳明确节省成本的部分；
- 只从 GitHub 项目和 release 获取。

## 13. 实施路线

### Phase 1a：新增 novel-writer

预计 1-2 天。

改动：

- 新增 `.opencode/agents/novel-writer.md`；
- 更新 `novel-director.md` task 权限；
- 更新 `docs/OPENCODE_AGENTS.md`；
- 更新 `skills/novel-write/SKILL.md`；
- 在 `writing_packet.md` 模板中补足 writer 所需字段。

验收：

- writer 能仅凭 packet 写出合格 draft；
- director 不亲自写 draft；
- writer 不碰 YAML 状态；
- cold-reader 不因任务报告感要求全章重写。

### Phase 1b：新增 novel-planner

预计 1-2 天。

改动：

- 新增 `.opencode/agents/novel-planner.md`；
- round context pack 增加 `Director Directive` section；
- planner 生成 writing_packet 草案；
- director 审核 packet。

验收：

- planner 生成的 packet 能被 writer 直接使用；
- packet 不漏人物语感、伏笔分量、关系温度；
- director 不需要大幅重写 packet。

### Phase 1c：评估 archivist 扩展

预计 2-3 天。

改动：

- 先不新增 summarizer；
- 评估是否让 archivist 产出 summary / canon_delta 草案；
- 如果扩展，更新 archivist 权限和输出格式；
- 增加 QA 检查推测事实和 evidence。

验收：

- summary / canon_delta 忠于 final；
- director 审核成本下降；
- state drift 不增加；
- validator 通过率不下降。

### Phase 2：工程自动化增强

改动：

- 扩展 `round_state_merge.py` 支持更多 safe ops；
- 增加 agent ownership 检查；
- 增加 token / 调用次数 / 失败次数记录模板；
- 增强 QA 对越权写入的检查。

### Phase 3：小范围试用 oh-my-opencode

前提：

- Phase 1a / 1b 已跑通；
- 原生 OpenCode 编排仍然明显痛；
- 有测试项目可承受失败。

范围：

- 只让 oh-my-opencode 做外层 orchestrator；
- 不替代 novel agents；
- 不绕过 `round_state_merge.py`；
- 不打开全局 allow 权限；
- 不从非官方站点下载安装。

验收：

- 每轮总耗时下降；
- 子 agent 卡死率下降；
- summary / canon_delta / state merge 错误不增加；
- 文风和连续性不下降；
- 配置维护成本可接受。

## 14. 成功指标

质量指标：

- 连续 2 轮内无 state drift error；
- 连续 2 轮内无 stale review status；
- 连续 2 轮内无 not-but 超限；
- cold-reader revise 后必须有 recheck；
- final 后不再大规模回头修正文；
- `active_flow.last_cut` 始终追上最新完成章节。

效率指标：

- director 亲自写正文时间下降；
- director 手工 YAML 时间不增加；
- 每轮 validator 重跑次数下降；
- 子 agent prompt 长度下降；
- 每轮 agent 卡死 / 空返回次数下降。

连续性指标：

- writer 能仅凭 `writing_packet.md` 写出自然承接；
- planner 能正确带入伏笔、人物、道具、债务；
- archivist 不把推测写成事实；
- review 能让新 agent 冷启动理解本轮结果。

## 15. 最终建议

这份 review 的主要意见应采纳：不要一次性上 8 个 agent。

最终推荐路线：

1. Phase 1a 只新增 `novel-writer`，验证 writer 能否只凭 packet 写好正文。
2. Phase 1b 再新增 `novel-planner`，验证 packet 是否可由 planner 稳定生产。
3. Phase 1c 再评估是否扩展 `novel-archivist` 处理 summary / canon_delta。
4. `novel-merger` 暂不做，工程合并继续脚本化。
5. `round_directive` 不新增文件，合并进 round context pack 的 `Director Directive` section。
6. oh-my-opencode 只作为 Phase 3 外层编排实验。

这条路线更慢一点，但风险低。它先验证最关键的质量假设，再扩大拆分范围，避免为了降低心智切换而制造新的协调成本。

## 16. 当前落地状态

本轮已按上述路线完成原生 OpenCode 第一阶段落地：

- 已新增 `novel-writer`，专责 `draft.txt` / `final.txt` / `draft_handoff_note.md`，禁止修改 summary、canon、entities、ledgers、planning。
- 已新增 `novel-planner`，专责写前 `writing_packet.md` 草案和局部 planning 建议，禁止写正文和合并状态。
- 已扩展 `novel-archivist`，默认仍只写 diff-only `memory_update_plan.md`；只有 director 明确指定 `mode: canon_draft` / `mode: full_chapter_memory_draft` 时，才可生成 `summary.yml` / `canon_delta.yml` 草案。
- 未新增 `novel-merger`，工程合并继续走 `round_state_merge.py` preview/apply，由 director 或人类审核。
- 未新增独立 `round_directive` 文件；导演边界合并进 round context pack 的 `Director Directive` section。
- `writing_packet.md` 模板已补足 writer 所需的 `voice_examples`、`foreshadowing_weight`、`relationship_temperature`、`body_scene_texture`、`dialogue_mode`。
- validator 已增加 `WRITER_CONTEXT_THIN` 和 `ROUND_CONTEXT_DIRECTIVE_MISSING` 提醒，避免 planner/writer 在上下文太薄时硬写。

下一步真实验收不看“文件是否存在”，而看一轮新书生产：

- planner 生成的 packet 是否不用 director 大改就能给 writer 使用；
- writer 是否能只凭 packet、上一章结尾和样本文风锚点写出自然正文；
- cold-reader revise 后是否能快速重检；
- archivist 草案是否短、准、可合并；
- 一轮 3 章结束后 validator error 为 0，state drift 不增加。
