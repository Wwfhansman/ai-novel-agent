# 引擎化写作流程（M1 接入）

本文描述**新模型下一轮写作怎么走**：写作产出**事件**而非手写 `canon_delta`，当前状态由引擎**派生**，收尾由统一门禁 `check` / `commit` 把关。它取代旧的 `round_state_merge.py` + `validate_novel_output.py` 收尾。

旧 skill 流程仍可用（绞杀榕）；本文是迁移到引擎主干的目标流程。

## 开新书（从零到第一章）

引擎**不负责生成故事 DNA**（创作宪法、长篇蓝图、初始人物、第一卷章纲）——那仍是 `novel-bootstrap`（LLM）或手填模板的活。引擎在项目骨架就绪后接管。

```
0. 故事 DNA   用 novel-bootstrap 从 seed 生成，或 cp -r templates/project 后手填
              产出：book/ 设定、entities/、ledgers/、planning/rolling_plan.yml
1. 种初始事件 python -m novel_engine init <project>      # 写 events/bootstrap.yml（把初始人物/债务/伏笔/信息差变成事件）
2. 门禁       python -m novel_engine check <project>     # 确认初始状态干净
3. 写第一章   python -m novel_engine kit <project> --chapter ch001
              → 按 _kit/ 逐场写 → 缝合 → chapters/ch001/final.txt → 填 events/ch001.yml
4. 收尾       python -m novel_engine check <project> && python -m novel_engine commit <project>
5. 继续       ch002、ch003…… 重复第 3–4 步（见下方"一轮的形状"）
```

要点：`init` 只种 `bootstrap.yml`（新书没有已写章节可转）；`migrate` 是给**已经写了章节**的旧项目用的。新书别用 migrate。

## 一轮的形状

```
1. 取上下文      python -m novel_engine context <project> --chapter chNNN
                 → writer 拿到 entering-state（在场人物当前态、未偿债务、未收伏笔、信息可见性）
2. 写正文        writer 按 entering-state + 场景规格写 draft → cold-read → final（创作层，LLM）
3. 产出事件      把本章造成的 canon 变化写成 events/chNNN.yml（见下方模板）
4. 门禁          python -m novel_engine check <project>     # schema + 引用/时序 + 健康 + 结构
5. 提交          python -m novel_engine commit <project>    # 门禁通过则把状态物化为派生 entities/ledgers
```

关键区别：**没有"手工把变化合并进 entities/ledgers"这一步**。状态是 `events` 算出来的；`commit` 负责物化。`canon_delta` 与 `entities` 不一致这一类漂移在构造上消失。

## 事件文件模板

`events/chNNN.yml` —— 一章造成的 canon 变化。机械变化用类型化事件（自动入状态），叙事性变化用 `note`。

```yaml
chapter: ch012
events:
  - {kind: character_changed, id: char_lin_qi, change: 决定连夜赶往西角塔, set: {current_goal: 进塔取证}}
  - {kind: relationship_changed, a: char_lin_qi, b: char_shen_yan, to: 暂时结盟}
  - {kind: knowledge_changed, topic: k_001, holder: char_lin_qi, level: knows_truth}
  - {kind: debt_advanced, id: debt_001, note: 拿到第一件物证}
  - {kind: foreshadow_paid, id: f_002, note: 父亲修灯刀的来历揭开}
  - {kind: item_moved, item: 父亲修灯刀, to: char_lin_qi}
  - {kind: fact_added, text: 西角塔在子夜被重新点亮。}
  - {kind: note, scope: char_lin_qi, text: 对父亲的怨意第一次松动}
```

完整事件词汇表和字段见 [`docs/ENGINE.md`](ENGINE.md) 第 3 节与 `novel_engine/schemas/event.schema.json`。`check` 会在写入后按 schema 校验每个事件、并做引用/时序完整性检查——**填错字段或还一笔没开过的债会被当场拒绝**。

## 把旧项目搬上来

```
python -m novel_engine shadow  <project>   # 先看现状漂移有多少（只读）
python -m novel_engine migrate <project>   # 旧 canon_delta → events/（最佳努力，需 review bootstrap.yml）
python -m novel_engine check   <project>   # 跑门禁
python -m novel_engine commit  <project>   # 物化派生状态（此后 entities/ledgers 不再手写）
```

迁移后，每写一章只需追加 `events/chNNN.yml`，再 `commit`。

## 与旧工具的关系

- `scripts/round_state_merge.py`、`scripts/validate_novel_output.py` 对**未迁移**项目仍然有效。
- 项目一旦 `commit` 过（entities/ledgers 变成派生产物），就以引擎门禁为准，不要再手工编辑 entities/ledgers——手工改动会在下次 `commit` 被覆盖。
- 仍需 LLM 的部分：写正文、世界活体**生成**、冷读裁决。引擎只负责状态、门禁和度量。
