# 记忆模型

## 1. 设计目标

本项目的记忆系统模拟人类作者的长篇记忆方式：

```text
大概记得全书
清楚当前卷
熟悉最近剧情
知道关键旧事在哪里
需要细节时回看原文
```

因此，本项目不以向量相似度检索作为主记忆方式，而采用分层文件记忆。

## 2. 核心原则

```text
正文保存细节
摘要保存理解
canon_delta 保存变化
账本保存活变量
规划保存未来方向
创作宪法保存最高约束
```

同一事实不能拥有多个互相竞争的权威来源。冲突时必须按照唯一事实来源规则处理，见 [正史与安全规则](CANON_AND_SAFETY.md)。

## 3. 记忆分层

### 3.1 全书层

位置：

```text
book/
```

回答：

```text
这本书是什么？到目前为止讲成了什么？
```

文件：

```text
book/constitution.md
book/global_summary.md
book/reader_model.yml
book/style_memory.md
book/endgame_hypotheses.yml
```

内容：

- 作品类型
- 核心卖点
- 主角长期欲望
- 读者承诺
- 风格基调
- 全书压缩摘要
- 远景假说
- 不可随意修改的边界

### 3.2 卷层

位置：

```text
volumes/vol_001/
```

回答：

```text
这一卷承担什么功能？当前卷推进到哪里？
```

文件：

```text
volume_outline.md
volume_summary.md
volume_state.yml
volume_threads.yml
volume_debts.yml
```

内容：

- 本卷目标
- 本卷主矛盾
- 本卷关键对手
- 本卷阶段划分
- 当前卷状态
- 本卷主线和支线
- 本卷叙事债

### 3.3 章群层

位置：

```text
arcs/
```

回答：

```text
最近这个 3-10 章的小事件链是什么？
```

内容：

- arc 名称
- 覆盖章节
- 小目标
- 核心冲突
- 起因
- 过程
- 结果
- 涉及人物
- 涉及伏笔
- 产生和偿还的叙事债
- 对卷主线的贡献

### 3.4 章节层

位置：

```text
chapters/ch001/
```

文件：

```text
brief.md
outline.md
draft.txt
final.txt
summary.yml
canon_delta.yml
review.md
```

回答：

```text
这一章发生了什么？改变了什么？留下了什么？
```

关键文件：

- `final.txt`：正文细节。
- `summary.yml`：这一章发生了什么。
- `canon_delta.yml`：这一章改变了什么。

### 3.5 实体层

位置：

```text
entities/
```

文件：

```text
characters.yml
factions.yml
locations.yml
items.yml
power_system.yml
```

实体层不只是百科，还要保存当前状态。

人物需要记录：

- 固定设定
- 当前目标
- 当前立场
- 角色意图
- 信息状态
- 关系
- 重要变化历史

势力需要记录：

- 目标
- 资源
- 盟友和敌人
- 当前行动
- 对主角态度

### 3.6 动态账本层

位置：

```text
ledgers/
```

文件：

```text
narrative_debts.yml
foreshadowing.yml
knowledge_state.yml
world_state.yml
idea_pool.yml
opportunity_ledger.yml
decision_log.yml
```

回答：

```text
故事中有哪些活变量正在等待处理？
```

## 4. 动态账本说明

### 4.1 叙事债务

叙事债务记录读者正在等待什么。

示例：

```yaml
- id: debt_001
  type: humiliation_payback
  created_in: ch003
  description: 角色A当众压制主角，读者期待主角反击。
  urgency: high
  expected_payoff_window: ch006-ch009
  status: open
```

### 4.2 信息可见性

信息可见性记录谁知道什么。

示例：

```yaml
- id: k_001
  topic: 道具A真正来源
  truth: 道具A来自势力B，不是普通物品。
  visibility:
    reader: hinted
    protagonist: suspects
    character_a: unknown
    character_b: knows_truth
```

### 4.3 世界状态

世界状态记录主角之外的外部系统。

示例：

```yaml
current_period: vol_001_stage_02
active_crises:
  - food_shortage
  - refugee_influx
factions:
  - name: 势力A
    current_goal: 控制关键资源，压制主角声望
    next_action: 散布对主角不利的信息
```

### 4.4 灵感池

灵感池保存未进入正史的可能性。

状态：

```text
candidate
incubating
promoted
rejected
merged
expired
```

灵感不是伏笔。只有晋升后，才进入大纲、伏笔或正文。

## 5. 章节记忆流转

每章写完后，内容应被消化为：

```text
final.txt
→ summary.yml
→ canon_delta.yml
→ entities update
→ ledgers update
→ planning update
```

其中：

- `final.txt` 保存章节原文细节。
- `summary.yml` 保存该章发生了什么。
- `canon_delta.yml` 保存该章造成了什么变化。
- `entities/`、`ledgers/`、`planning/` 保存合并后的当前权威状态。

`canon_delta.yml` 不能替代当前状态文件。agent 冷启动时应以当前状态文件为准，再按需回看 delta 和正文。

## 6. 上下文读取策略

```text
远处读摘要
近处读原文
关键旧内容回看原文
动态账本优先读取
```

推荐默认读取：

- 创作宪法
- 全书摘要
- 已完成卷摘要
- 当前卷纲和状态
- 当前 arc
- 最近 12-15 章详细摘要
- 最近 3-5 章全文
- 关键旧章节原文
- 动态账本
- 本章任务

每次读取结果必须写入 context pack。上下文编译不是隐性过程，见 [上下文编译](CONTEXT_PACK.md)。

## 7. 正史边界

建议区分：

```text
canon: 已确认正史
draft: 草稿
proposal: 提案
idea: 未确认灵感
retcon: 对旧正史的修订计划
```

MVP 自用阶段可以简化，但概念必须保留。
