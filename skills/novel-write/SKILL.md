---
name: novel-write
description: Continue an existing AI Novel Agent project by writing the next chapter or next three-chapter round. Use for daily novel production, active narrative flow maintenance, detailed rolling synopsis updates, context pack generation, prose drafting, chapter review, canon delta creation, and memory updates.
---

# Novel Write

Use this skill for normal production writing. Default execution unit: one round of 3 chapters.

Important distinction:

- **Narrative Flow** is the story continuity unit.
- **Round** is only a production batch.
- **Chapter** is only a serial cut point inside a larger flow.

Never let the round size decide the story shape. A narrative flow may span 2, 5, 9, or more chapters, and may cross round boundaries.

## Core Model

Use three planning layers:

0. `book/longform_blueprint.yml`
   - The protected whole-book scale authority.
   - Tracks target length, macro stages, world/region/city hierarchy, faction scale, progression budget, opportunity cadence, and secret reveal windows.
   - It prevents the agent from shrinking a world into a city, treating the opening map as the whole book, or spending late-book power/reveal budget too early.

1. `planning/active_flow.yml`
   - The current continuous story flow.
   - Tracks the ongoing pressure, scene chain, last visible cut, and next opening.
   - It is allowed to span across multiple rounds.

2. `planning/rolling_plan.yml`
   - The detailed 6-15 chapter synopsis.
   - It is the current future window only.
   - Completed chapter plans should be moved to `planning/completed_plan_log.yml`.
   - Distant ideas should live in `planning/future_backlog.yml`.
   - Each chapter should link to a flow and identify its entry/pickup and cut point.

3. `planning/current_round.yml`
   - A lightweight production-batch tracker.
   - It records only which chapters are being written, status, and where the batch starts/ends inside the active flow.
   - It must not copy chapter synopsis fields or become a second planning source.

## Hard Rules

- Never write `draft.txt` or `final.txt` before generating:
  - `planning/context_packs/round_XXX_context_pack.md`
  - `chapters/chXXX/context_pack.md`
- `planning/active_flow.yml`, `planning/rolling_plan.yml`, and `planning/current_round.yml` must be valid YAML before drafting.
- Do not translate a plan, synopsis, outline, or checklist directly into prose.
- Do not treat one chapter or one round as a complete narrative box.
- Round boundaries are production boundaries, not story boundaries. Do not make ch003/ch006/ch009 feel like cleanup, recap, reset, or phase closure unless `planning/active_flow.yml` and `planning/rolling_plan.yml` explicitly say the story has earned payoff.
- 如果上一章的 `canon_delta.yml` 中有 `actual_handoff`，本章开头必须承接，除非在 context pack 和 review 中记录了有理有据的切换理由。
- 承接后，在本章的 `brief.md`、`context_pack.md` 和 `planning/rolling_plan.yml` 条目中体现该交接。
- Do not use docs, schemas, templates, examples, sample novels, or other projects as creative source material. They are process references only.
- Do not silently change protected canon. Route major changes to `novel-change`.
- Before accepting any `final.txt`, run `python scripts/validate_novel_output.py <project> --chapters chXXX` from the repository root when the script exists. If it fails, fix the listed issues and rerun. Do not call the chapter complete until validation passes.
- Read `planning/rolling_plan.yml` in full before each round. It is the future-planning authority.
- Do not copy full project files or the full rolling plan into context packs. Context packs are working memory, not a duplicated database.
- Follow `meta/model_policy.yml` when it exists. A fast or cheap model may assist mechanical tasks, but final prose, active_flow, rolling_plan, canon merges, and protected-file decisions must be confirmed by a premium model or human.
- Key context-pack claims must include source refs. Do not rely on "I remember reading it."
- Read `book/longform_blueprint.yml` before refreshing planning and before drafting. Treat it as protected. If it is missing, create a stop/fix task instead of guessing long-form scale.
- Every round and chapter context pack must include a `Longform Scale Check`.
- Do not silently change target length, macro stages, world scale, faction scale, power pacing, or secret reveal windows. Route those changes to `novel-change`.

## Context Budget Policy

Use working-memory context, like a human writer:

- remember the whole-book promise, current volume goal, active flow, and full future rolling plan;
- remember the long-form blueprint: current macro stage, scale level, progression budget, and reveal limits;
- keep recent chapters sharp: previous chapter full text, recent summaries, and recent full text when continuity needs it;
- read entity and ledger entries by relevance, not by default full dump;
- reread old chapter originals only when a concrete trigger exists.

Recommended context pack budgets:

- round context pack: 3000-5000 Chinese characters;
- chapter context pack: 1000-2500 Chinese characters.

`planning/rolling_plan.yml` is the exception to the lean-read rule: read it in full each round, because future planning decides how the current chapter should be written. But summarize only the batch chapters, adjacent chapters, and later constraints that affect this task.

## 结尾规则

以下结尾模式应避免，除非项目风格明确要求且在 review 中说明理由：

**空泛反思式结尾（应避免）：**
- 章末主角独自坐下，空泛思考，没有外部动作落地。
- 主角在章末以"他明白了""他知道了"收束全章教训。
- 主角抽象地规划下一步："接下来他打算……""他知道该怎么做了……"。
- 用夜景、窗户、烛火、远望、空房间作为情绪按钮收尾——如果前面全是动作和对白，最后突然"安静下来看窗外"。
- 最后一段是纯氛围短句，没有任何具体信息、动作或物件落地。
- 章末的唯一功能是告诉读者"下一章会很重要"。

**区分：以下情况不应被误判为反思式结尾：**
- 主角在章末做出了具体决策，且这个决策在下一章开头被执行（例如"他决定赌一把"然后下一章直接进入行动）。
- 主角的思考揭示了新信息或对前文的反转理解（例如"他忽然意识到那个人从未提过自己的姓氏"——这是信息释放）。
- 主角在章末推演策略、分析局面，且推演内容包含新变量或新风险（权谋/修仙/悬疑文的核心爽点）。
- 用环境收束情绪但环境本身是情节的一部分（例如"雨停了"紧跟在战斗结束之后）。

**推荐的切分点：**
- 一个动作刚刚开始，还没完成。
- 对话被打断或故意没说完。
- 有人到场、离场、闯入。
- 一个代价刚刚落地、一道命令被下达、一件物品被打碎或交到手中。
- 一个选择被当众做出，无法收回。
- 压力在主角来得及完全消化之前就已经向前移动了。
- 新的信息、物件、声音、伤口改变了局面。

## Read First

Read once per session or when uncertain:

- `docs/CONTEXT_PACK.md`
- `docs/CANON_AND_SAFETY.md`
- `docs/MEMORY_MODEL.md`
- `docs/FILE_FORMATS.md`
- Current project `project.yml`
- `book/constitution.md`
- `book/longform_blueprint.yml`
- `book/reader_model.yml`
- `book/style_memory.md`
- `book/chapter_rhythm_guide.md`（本章类型对应的节奏模板）
- `style/rewrite_rules.md`
- `style/samples.md`（本项目文笔风格报告——如果有内容，本章正文必须遵守其文笔指令）
- `planning/active_flow.yml`
- `planning/rolling_plan.yml`
- `planning/current_round.yml` if it exists
- `meta/model_policy.yml` if it exists

Do not paste these files into context packs. Extract only the operational conclusions needed for the current task.

## Model Routing

Use `docs/MODEL_ROUTING.md` and project `meta/model_policy.yml` when available.

Default:

- Use `premium_model` for active_flow, rolling_plan, chapter concept, draft prose, final prose revision, ending rewrite, canon merge, and quality gate.
- Use `fast_model` only for YAML/TXT formatting, validator error summaries, diff summaries, session logs, and other mechanical tasks whose output can be checked.
- Hybrid context pack drafting is allowed, but the writing agent must confirm the final context pack before drafting.
- Never let `fast_model` directly write or approve `final.txt`.
- Never let `fast_model` make Level 3-5 change decisions or protected-file edits.

If model routing is used, record it in the round context pack or `meta/session_log.md`.

## Source Of Truth

- `final.txt` is chapter canon text.
- `summary.yml` records what happened in that chapter.
- `canon_delta.yml` records what changed in that chapter. It is a change log, not current state.
- Current character state lives in `entities/characters.yml`.
- Current world state lives in `ledgers/world_state.yml`.
- Current knowledge visibility lives in `ledgers/knowledge_state.yml`.
- Current continuous flow lives in `planning/active_flow.yml`.
- Long-form scale, map hierarchy, progression budget, and reveal windows live in `book/longform_blueprint.yml`.
- Future 6-15 chapter synopsis lives in `planning/rolling_plan.yml`.
- Completed planning history lives in `planning/completed_plan_log.yml`.
- Distant future ideas live in `planning/future_backlog.yml`.
- Current round tracker lives in `planning/current_round.yml`.

When files conflict, follow `docs/CANON_AND_SAFETY.md`. Do not merge contradictions casually.

## Narrative Flow Requirements

Before each round, ensure `planning/active_flow.yml` describes the current continuous story flow.

A flow should include:

- flow id and status;
- intended chapter span or flexible range;
- current pressure already in motion;
- story question or practical problem driving the flow;
- scene chain, not chapter boxes;
- last cut from the previous chapter;
- required next opening if one exists;
- conditions for ending this flow;
- whether this round continues, turns, or ends the flow.

Start a new flow only when the story genuinely changes subject, location, POV, objective, or dramatic mode. Do not start a new flow merely because a new round begins.

## Rolling Synopsis Requirements

Before each round, ensure `planning/rolling_plan.yml` contains a detailed 6-15 chapter forward window.

Each planned chapter should include:

- chapter id and provisional title;
- status;
- macro stage or part id from `book/longform_blueprint.yml`;
- intended scale level for this chapter: local / family / city / region / world / upper_world / other project-specific level;
- `flow_id`;
- `flow_position`: opening / pressure_rising / turn / fallout / payoff / transition;
- `chapter_function`: crisis / cultivation / travel / trade / social_conflict / reveal / aftermath / investigation / operation / relationship / domestic_management / dungeon_rule / transition, or a project-specific equivalent;
- `pressure_curve`: how pressure rises, delays, releases, or transfers across the chapter;
- `reader_question_flow`: the visible reader expectation entering and leaving the chapter (`enters_with`, `leaves_with`);
- 300-800 Chinese characters of story synopsis;
- `entry_from_previous`: the concrete pickup from the prior cut;
- `core_advance`: one primary external advancement, required beats, and what must deliberately remain unfinished;
- `information_release`: 1-2 new core variables, deferred information, rule/system pressure, and any planned misdirection or partial understanding;
- important characters and what they want;
- pressure, obstacle, or complication;
- `chapter_turn`：本章造成的不可逆外部变化；
- 预期 payoff、揭示或读者回报；
- `side_yield`：除核心推进外进入长期记忆的世界/系统质感、关系变化、资源/地位变化或可复用伏笔；
- `叙事织入`：人物日常反应、场景即时质感、关系温度波动——让人物、场景和系统有"居住感"、但不需要解决章节任务的织入材料；
- `density_control`：要求的织入节拍数、是否允许闲笔停顿；
- `cut_point`：章节在何处切分而不关闭叙事；
- `planned_handoff`：下一章必须承接的首要可见时刻、外部压力、物件、后果或未完成的动作；
- 禁止事项或正史约束。
- scale/pacing constraints: what this chapter must not shrink, over-reveal, or over-advance.

This is story-content planning, not an intra-chapter prose template.

If the rolling synopsis is too thin, expand it before drafting. Do not compensate for a thin synopsis by inventing a rigid `outline.md`.

## Round Workflow

1. **Establish checkpoint**
   - If Git is available and the project tracks real content, create or recommend a checkpoint before the round.

2. **Validate planning YAML**
   - Parse `planning/active_flow.yml`, `planning/rolling_plan.yml`, and `planning/current_round.yml` if present.
   - Stop if any of them are invalid YAML.
   - Run `python scripts/validate_novel_output.py <project> --chapters <recent chapters> --skip-planning` only for TXT checks when validating old chapters, then run without `--skip-planning` before drafting the new batch.
   - If planning validation reports stale fields such as `bridge_to_next`, `continuity_from_previous`, or `next_hook`, rewrite planning files into the active-flow format before drafting.

3. **Refresh active flow and rolling synopsis**
   - Read current canon and planning files.
   - Read `book/longform_blueprint.yml` and identify the current macro stage, allowed scale level, progression budget, opportunity cadence, and reveal limits.
   - Update `planning/active_flow.yml` so the ongoing flow continues across the round boundary when appropriate.
   - Update `planning/rolling_plan.yml` so the next 6-15 chapters are detailed enough to drive prose.
   - Ensure `planning/rolling_plan.yml` does not collapse global scale, does not spend future-stage reveals, and does not accelerate protagonist progression beyond the current stage budget.
   - Move completed chapter plan entries into `planning/completed_plan_log.yml`; do not keep completed chapters in the future window.
   - Move distant or not-yet-actionable ideas into `planning/future_backlog.yml`.
   - Do not leave future chapters repeating decisions already made.

4. **Compile round context**
   - Read according to `docs/CONTEXT_PACK.md`.
   - Read `meta/model_policy.yml` if present and record the model routing plan.
   - Always read `book/longform_blueprint.yml` in full.
   - Always read `planning/rolling_plan.yml` in full.
   - Read recent 12-15 chapter summaries when available.
   - Read recent 1-3 chapter `final.txt` files when continuity needs exact prose, scene carryover, or tone.
   - Read only relevant entity and ledger entries for this batch.
   - Read key old chapter originals when old foreshadowing, debts, objects, relationships, rules, or lines become relevant.
   - Write `planning/context_packs/round_XXX_context_pack.md`。**必须按照 `templates/project/planning/context_packs/round_001_context_pack.md` 的 section 结构填写。**
   - Keep the round pack within the context budget unless the project is at a major transition or user explicitly asks for a fuller audit.

5. **Create current round tracker**
   - Plan exactly 3 chapters unless the user asks otherwise.
   - Record only `round`, `chapters`, `source`, `status`, `batch_edges.starts_inside_flow`, `batch_edges.ends_inside_flow`, and optional operational `notes`.
   - Do not copy `flow_id`, `chapter_function`, `pressure_curve`, `core_advance`, `planned_handoff`, `叙事织入`, or other per-chapter planning fields into this file.
   - Do not add `batch_tasks` or round-level story goals.
   - Treat `planning/rolling_plan.yml` as the only detailed near-future chapter plan.
   - Write `planning/current_round.yml`.

6. **Write each chapter as a cut from the flow**
   - Create or update `chapters/chXXX/brief.md` from the detailed synopsis and flow continuity.
   - Generate `chapters/chXXX/context_pack.md`。**必须按照 `templates/project/chapters/ch001/context_pack.md` 的 section 结构填写，section 名可用中文或英文，但结构需完整。**
   - Chapter context must include the applicable macro stage, scale level, power pacing, opportunity budget, and reveal limits from `book/longform_blueprint.yml`.
   - Chapter context must include `Source References` for the primary handoff, character states, active debts, knowledge visibility, world pressure, and reader reward.
   - Chapter context must include `Source References` for long-form scale claims.
   - Treat `planning/active_flow.yml` `last_cut.current_handoff` as the primary handoff authority unless `novel-change` explicitly changes it.
   - Keep the chapter pack within the context budget unless the chapter is paying off old material.
   - Optionally write `outline.md` only as freeform notes if useful. Do not make it a required scene-beat checklist.
   - Draft `draft.txt` as novel prose.
   - Revise for continuity, concreteness, anti-reporting, and cut-point behavior.
   - Write confirmed text to `final.txt`.
   - If a cheaper model assisted formatting or summaries, confirm no unreviewed cheap-model prose entered `final.txt` or canon state.
   - Run `python scripts/validate_novel_output.py <project> --chapters chXXX --fix-format`.
   - If validation reports a reflective ending, short atmosphere ending, or protagonist thought ending, rewrite the ending and rerun validation.
   - Write `review.md`。**必须按照 `templates/project/chapters/ch001/review.md` 的 section 结构填写，section 名可用中文或英文，但结构需完整。审查是诊断性的，不是自我表扬。必须至少指出一个弱点或风险并给出具体的修改建议。**
   - Merge current state into `entities/`, `ledgers/`, `volumes/`, and `planning/`.
   - Update `planning/active_flow.yml` with the chapter's actual last visible cut and handoff.

7. **End round**
   - Do not close the narrative flow just because the round ended.
   - Do not generate a round-level story conclusion.
   - Update current volume summary/state and active arc.
   - Evaluate idea pool and narrative debts.
   - Refresh `planning/rolling_plan.yml` so the next round picks up the active flow.
   - Archive completed plan entries to `planning/completed_plan_log.yml`.
   - Keep only the next 6-15 upcoming chapters in `planning/rolling_plan.yml`.
   - Record a session summary in `meta/session_log.md`.

## 写作心法

写作时聚焦"此刻正在发生什么"，而不是"这段应该完成什么任务"。

好写法：
- 尽量从上一章留下的压力切口开局——上一章的物件、动作、对话、后果，而不是"第二天"。
- 让人物在场景里追逐自己的欲望，而不是站在场景里解释自己的立场。
- 让信息因为"有人需要""有人隐瞒""有人误读""有人交易""有人拿来当武器"而浮现，而不是靠旁白介绍。
- 允许小的局部即兴发挥——只要不破坏正史。
- 给读者一个具体的回报：爽点兑现、真相揭示、局面反转、代价落地、关系变化、新能力展示、危险升级，或者一段难忘的小说画面。
- 制造或推进读者的期待，而不只是让人物走完任务流程。
- 在局势仍在运动时切分，不要在一切都安静下来后才收尾。
- 让下一章的第一句话像这口气还没喘完——而不是一个新任务的开始。

## 网文节奏规则

一章只有一个任务，但不是每一段、每一句都围绕这个任务。

写作前先明确：
- 本章唯一的那个核心推进是什么。
- 本章刻意不完成什么（收编/摊牌/解释/证据引爆/关系确认）。
- 本章功能和压力曲线——不同章类型要有不同的节奏形状，不要在每章重复同一种内部节拍。
- 进入和离开本章的读者疑问。
- 本章只释放 1-2 个读者必须记住的新信息变量，其余延后。
- 至少一个进入长期记忆的 side yield（世界质感/关系变化/资源变化/可复用伏笔）。
- 3-5 个叙事织入节拍——围绕核心人物、世界、系统或社会结构产生生活感。

叙事织入可以包括：日常琐事、小不便、轻松斗嘴、误读反应、食物、衣物、房间、天气作为生活质感、旁人反应、人物习惯、行动前的停顿、非策略性的情感对话、世界质感、制度流程、资源账目、修炼或系统操作、副本规则反应、家族运转、旁观者的后果、一个小小错误猜测。

不要把这些织入当成水文废话。它们的作用是让人物、盟友、对手、场景、系统和社会结构有"居住感"，但它们不需要揭秘、不需要推进势力逻辑、不需要解决章节任务。

连续两页都是计划/推理/派系分析/任务执行/未来安排——必须重写或放松节奏。
连续两段解释规则/势力/计划/推论/功法——下一段必须是行动、反应、对话、误读、冲突、感官质感、代价、或场景移动。

对于悬疑/副本/规则/修仙/权谋/经营章，优先用"事件验证"的信息：规则被测试、代价落地、人物做出反应、有人误用了系统、某种制度改变了行为。

### 不同类型章节的节奏参考

不要对所有章节用同一个节奏比例。以下按四种基本节奏类型分述：

**推进型（打脸/战斗/突破/比试/展示）：**
主线推进是主体，但保留对话交锋和世界质感的间隙。不要让打脸章的"众人震惊"只用一句话带过——围观者反应是爽点兑现的核心组件。

**建制型（种田/经营/赶路/交易/拍卖）：**
主线推进和日常运转交替出现。建制型章节的力量来自"积累感"——小投入→小收获→扩大→阻力→质变。数字、资源、流程本身就是叙事材料，但要通过人物的反应和摩擦来消化。

**推理型（悬疑/副本/权谋试探/调查/揭秘）：**
对话和反应密度高，但一章只放 1-2 个读者需要记住的新信息变量。让规则和真相通过事件、代价、误用、冲突进入正文，不要连续多段旁白解释。连续反转不要超过一次——给读者消化空间。

**日常型（关系拉扯/余波回收/过渡/家庭）：**
主线压力低，但情绪温度高。用人物互动、对话摩擦、身体反应和场景质感来填充。注意：日常不是水——日常段要有人物反应、关系温度变化或世界质感的自然呈现。

### 避免以下写法：
- 无视上一章切口的重启式开头。
- 用主角内心复盘来收束全章。
- 正文里出现"第一……第二……第三……"式的条理化总结——除非人物在写文书。
- "不是X而是Y / 不是X，是Y"每章最多 1 次。写之前必须确认它是本章唯一值得保留的概念反转或认知切分；其他地方改成直接描写、动作、对话、物件、后果或肯定句。
- 把所有章节或所有轮次都写成同一个内部节拍。
- 因为批次结束而让每轮第三章变得更"干净"、更"反思"、更"总结"。
- 重复出现"到达→观察→分析→安排→思考"的章节奏。

## TXT Format Rule

`draft.txt` and `final.txt` must look like normal TXT novel text:

```text
第八章 章名

正文第一段。
正文第二段。
正文第三段。
```

- 章节标题后保留一个空行。
- 正文普通段落之间不空行，只换行。额外空行只用于明确的场景切换。
- 不要在 `draft.txt` 或 `final.txt` 中放入审稿意见、YAML、Markdown 标题或清单语言。
- 仍需正常分段。"段落间不空行"不等于把多个动作合并成巨大段落。
- 2000-3500 中文字章节的段落数按章节类型有所不同，短段落在手机上恰是优点。核心规则是防"一大坨"：多数段落 40-160 字，超过 220 字视为格式失败（除非 review 中说明是刻意的长镜头段落）。
- 在动作变化、说话人变化、反应落点、新信息出现、镜头变化、节奏停顿时主动分段。
- 避免没有叙事功能的密集碎行——短段要有真正的节拍承载。

## 审查清单

在写 `final.txt` 之前，创建或更新 `review.md`。审查必须是诊断性的，不是自我表扬。必须至少指出一个弱点或风险，并说明是否已修复。

检查：

### 连续性与容器检查
- 本章是 active flow 上的一个切分，还是一个独立的故事容器？
- 开头是否承接了上一章的切口？如果没有，转换是否在 context pack 和 review 中说明了理由？
- 本章是否跟随了详细章纲，但没有写成章纲翻译？
- 如果是本批次最后一章，是否避免了因批次结束而变成总结/复盘/暂停？

### 规模与节奏检查
- 本章是否保持在当前宏观阶段和规模层级内？
- 是否避免了把世界级/区域级概念缩小为本地概念？
- 是否遵守了力量递进节奏、机遇频率和秘密揭示窗口？
- 本章功能与压力曲线是什么？（不要每章都用同一种节拍）
- 是否控制了信息密度——本章新增核心变量是否超过 1-2 个？

### 叙事织入检查
- 本章除核心推进外，是否有围绕任务的织入材料：日常细节、人物反应、对话摩擦、世界/制度质感、关系温度波动、场景物件、身体/情绪节拍、误读、轻松感、尴尬、柔软或人物习惯？
- 是否连续两页每一段都在功能性推进剧情/传递信息？
- 是否有两段连续解释规则/势力/计划/推论/功法，而没有紧跟行动、反应、对话、冲突或场景移动？
- 规则、制度、功法、政治事实是否通过事件、代价、误用或人物反应验证，而不只是旁白说明？
- "不是X而是Y / 不是X，是Y"是否超过 1 次？如果超过，必须在 `final.txt` 前重写。保留的唯一一次必须在 review 中说明为什么非用不可。

### 回报与期待检查
- 本章给了读者什么具体回报？
- 推进或制造了什么新期待？
- 是否有角色做出了选择、付出了代价、获得了杠杆、失去了什么、暴露了什么或改变了关系？
- 读者回报是否足够（考虑当前类型和债务窗口）？

### 结尾检查
- 结尾是否避免了空泛反思/复盘式收束？
- 结尾是否产生了基于外部运动的、可以被下一章直接承接的交接？
- 如果结尾是短句氛围收束——它有没有具体的内容落地支撑？没有具体内容的短句氛围结尾应该重写。

### TXT 格式检查
- 正文普通段落之间是否无空行？
- 段落密度是否适合手机阅读？（不是 7-9 个巨大段落；也不应该全是碎行的假节奏）
- 是否有超过 220 字的大段落？
- `python scripts/validate_novel_output.py` 是否通过？

### 记忆更新检查
- `summary.yml`、`canon_delta.yml`、`entities/`、`ledgers/`、`volumes/`、`planning/` 是否已更新？
- `active_flow.yml` 的 `last_cut` 是否记录了本章实际交接？
- `rolling_plan.yml` 是否滑动了未来窗口（已完成章纲归档到 completed_plan_log.yml）？

## Do Not Silently Modify

Route to `novel-change` if writing would:

- modify the creative constitution;
- change protagonist core desire;
- kill or permanently remove a major character;
- reveal an endgame-level secret;
- change the current volume goal;
- promote a major idea into mainline canon;
- perform a large retcon.

## Writable Files

During normal writing, this skill may modify:

- `planning/active_flow.yml`
- `planning/context_packs/*`
- `planning/current_round.yml`
- `planning/rolling_plan.yml`
- `chapters/chXXX/*`
- `entities/*` when current state changes
- `ledgers/*`
- `volumes/*`
- `arcs/*`
- `book/global_summary.md`
- `book/style_memory.md` only for observed style memory, not constitution changes
- `meta/session_log.md`

Protected or confirmation-required:

- `book/constitution.md`
- `book/longform_blueprint.yml`
- endgame-level secrets
- protagonist core motive
- current volume goal
- major character permanent removal
- large retcons

## Failure Handling

Stop before drafting if:

- planning YAML is invalid;
- context packs cannot identify required current state;
- source-of-truth files conflict and cannot be resolved;
- a protected file must change;
- `book/longform_blueprint.yml` is missing, stale, or contradicted by planning;
- required prior chapter files are missing;
- the chapter depends on an unconfirmed idea as if it were canon;
- `planning/active_flow.yml` is missing or stale;
- `planning/rolling_plan.yml` is too thin to drive prose.
- planning files still contain stale old-format fields that encourage chapter containers: `bridge_to_next`, `continuity_from_previous`, `next_hook`, `结尾方向`, `情绪节奏`, `本轮需要`.

Stop before finalizing if:

- the draft reads like an expanded outline or task report;
- the chapter behaves as an independent container;
- the ending is mainly internal reflection, analysis, or next-step planning;
- the ending lacks a concrete next-chapter pickup;
- no external state changes;
- ordinary body paragraphs are separated by blank lines;
- the chapter has too few body paragraphs or contains giant paragraphs that should be split;
- `scripts/validate_novel_output.py` reports failure;
- `draft.txt`, `review.md`, `summary.yml`, or `canon_delta.yml` is missing;
- current state files, `active_flow.yml`, or `rolling_plan.yml` are stale after writing.
