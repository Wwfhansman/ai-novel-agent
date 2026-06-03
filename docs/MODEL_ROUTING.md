# 模型路由策略

> 本文的 premium/fast 角色划分仍然适用。文中举的若干"机械任务"例子（`canon_delta` 初稿、`writing_packet` 初稿等）属旧流程；引擎模型下机械任务是 `events` 编写、`check`/`patterns`/`txt` 报错整理。

## 1. 目标

模型路由的目标是降低长篇写作成本，同时不牺牲正文质量和长篇一致性。

本项目不绑定具体模型厂商。所有 skill 只使用模型角色：

```text
premium_model: 高质量、强推理、长上下文模型
fast_model: 快速、便宜、适合机械任务的模型
```

例如你可以把 `premium_model` 映射为 DeepSeek V4 Pro，把 `fast_model` 映射为 DeepSeek V4 Flash；也可以换成其他供应商的强/弱模型组合。

## 2. 基本原则

不要为了省钱让便宜模型负责决定小说方向。

可以降级的任务通常有三个特征：

- 输出可以被脚本或人类快速检查。
- 不直接决定正文审美。
- 出错后容易回滚或重跑。

不能随便降级的任务通常有三个特征：

- 会影响人物动机、剧情方向、伏笔兑现或读者期待。
- 会写入 `final.txt` 或改变 canon。
- 需要综合长上下文做审美判断。

## 3. 任务分级

### 3.1 必须使用 premium_model

以下任务默认使用 `premium_model`：

- 新书启动时的创作方向选择。
- `book/constitution.md`、核心读者承诺、主角核心欲望的创建或修改。
- `planning/active_flow.yml` 的创建、重构和关键转折判断。
- `planning/rolling_plan.yml` 的创建、扩写和重大调整。
- `planning/story_architecture.yml` 和 `planning/thread_board.yml` 的创建、重构和战略判断。
- `planning/development_packs/` 中未来 10-30 章世界运营、支线、信息释放和成长预算设计。
- 每章正文 `draft.txt` 的初稿。
- 每章正文 `final.txt` 的文学性修订。
- 章节结尾重写，尤其是解决割裂、复盘式结尾、短句氛围结尾。
- 重大变更评估：Level 3-5 的 `novel-change`。
- 冷启动审查中的质量判断和跑偏判断。

### 3.2 可以使用 fast_model

以下任务可以使用 `fast_model`：

- YAML 格式检查和字段补齐。
- `python -m novel_engine check` / `patterns` / `txt` 报错整理。
- TXT 空行修复。
- 章节摘要初稿整理，但必须由 `premium_model` 或当前写作 agent 检查是否改变事实。
- `canon_delta.yml` 初稿整理，但必须由当前写作 agent 对照正文确认。
- context pack 的读取清单表格整理。
- session log、diff 摘要、文件变更清单整理。
- 低风险 typo、标点、格式修复。

### 3.3 可选 hybrid

以下任务可以先用 `fast_model` 产出草案，再由 `premium_model` 做最终判断：

- round context pack 初稿。
- chapter writing_packet 初稿。
- 最近章节摘要压缩。
- 动态账本候选更新。
- review checklist 初稿。

但最终写作前，`premium_model` 必须确认：

- active_flow 是否准确。
- rolling_plan 是否足够驱动正文。
- 本章 handoff 是否具体。
- 本章禁止事项是否完整。
- 不存在会导致正文跑偏的误读。

## 4. 写作推荐路由

一轮三章写作推荐流程：

```text
premium_model:
  当 rolling_plan 接近耗尽或世界变窄时，运行 novel-architect / story development
  读取 rolling_plan 全文
  刷新 active_flow
  刷新/扩写 rolling_plan
  确认本轮剧情方向

fast_model 可选:
  整理 round context pack 表格
  检查 YAML 和旧字段

premium_model:
  审定 round context pack
  逐章写 draft/final
  决定章节结尾和 handoff

fast_model 可选:
  运行格式检查
  整理 summary/canon_delta 初稿
  整理 session log

premium_model:
  对照正文确认 summary/canon_delta/current state
  确认 active_flow 和 rolling_plan 已正确更新
```

## 5. 禁止降级

以下情况不要切到 `fast_model`：

- 正文质量已经出现模板感、流水账、章节割裂。
- 最近章节结尾反复出现主角思考、总结、规划。
- 本章需要回收久远伏笔或处理复杂信息差。
- 本章包含高潮、转折、反转、主要人物关系变化。
- 本轮要修改 protected files。
- `fast_model` 的输出会直接写入 `final.txt`。

## 6. 记录要求

如果一次写作中使用了模型切换，必须在对应 context pack 或 session log 中记录：

```text
model_routing:
  premium_model: "<actual model or agent>"
  fast_model: "<actual model or agent>"
  premium_tasks:
    - ...
  fast_tasks:
    - ...
  final_quality_gate_by: "<premium model or human>"
```

如果 agent 不支持真正切换模型，也应把这个字段当成任务风险记录：说明哪些任务原本可以交给便宜模型，但当前由同一模型完成。

## 7. 质量风险

模型切换不会天然降低写作质量，前提是：

- 便宜模型不写正文终稿。
- 便宜模型不决定剧情方向。
- 便宜模型不单独更新正史状态。
- 所有会进入 canon 的内容都经过 premium_model 或人类确认。

真正会降低质量的是：为了省 token，把前文理解、rolling_plan、active_flow、章节 handoff 和正文修订交给弱模型草率处理。
