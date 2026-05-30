# Novel Write 工作流优化需求报告

> **实施状态**：连续 draft + 工程后置已提升为 `skills/novel-write/SKILL.md` 默认流程；`check_not_but.py` 已实现并作为 draft 阶段硬门禁；archivist 权限、短输入协议和落盘检查已合并。本文保留作为实测数据和设计背景。

> 基于 round_003（ch007-009）实际生产数据。耗时 ~50 分钟。prose 占比 17%，工程摩擦占比 53%，其余为 I/O 和子 agent 等待。

---

## 一、当前问题

### 1.1 正文僵硬——冷得不自然

**现象**：章节读起来像 Morse 电码——句句 6-15 字、破折号密度过高、缺少呼吸感。与同类网文（古代权谋女频）对比：人家的冷是有节奏的克制，我们的冷是像被规则清单压着写的。

**根因**：
- `style_memory.md` 中"叙述偏冷"被 agent 执行成"每句不超过 15 字 + 拒绝任何温度"——从风格引导变成了施工指令
- prompt.md 给出的"文笔约束"全部是禁止性规则（"不要暧昧""不要连续 3 段纯推理"），正面方向不足——虽然有 samples.md 作为风格锚点，但 agent 在执行时仍然倾向于用排除法写 prose（不要 X→不要 Y→剩下被压扁的短句串），对"对标样本的节奏"这一指令的权重不够

**影响**：ch007-009 的冷读虽然全部 pass，但读者（你）感觉"很累很刻意"。这是一个真实的读者体验问题——不是 validator 能检测的。

### 1.2 `不是X` 校验消耗 22% 总时间——往返轮次多

**现象**：每章 draft 写完 → validator 报 7-9 个 `不是X` error → agent 打开文件逐处找 → 改完再跑 validator → 又报 2-3 个 → 再找再改。循环 3-4 轮 / 章。三章合计 ~12 分钟。

**根因**：
- agent 改完之后不知道还有没有漏的——只能再跑一次 validator
- 每次 validator 返回的报错是分散的（"第 7 行""第 19 行""第 42 行"），agent 需要手动逐行定位
- 没有工具一次性列出所有 `不是X` 位置——agent 在"改→查→发现还有→再改"的循环里反复切换

**数据**：ch007 原文"不是X"出现 ~15 次 → 修到 ≤1 次共经历 3 轮 validator 往返。每轮 ~1.5 分钟（定位 + 修改 + 验证）。60% 的时间花在"找位置"上，不是花在"判断怎么改"上。

### 1.3 章节间 prose 温度断裂

**现象**：ch007 结尾"手背水珠没洗 / 晚一点再说"→ ch008 开头"采苓端早饭进来"——两者之间的衔接在叙事上是对的，但在 prose 温度上有微小的重启感。

**根因**：当前流程强制"写完 ch007 final → 生成 5 个后处理文件 → 写 ch008 context_pack → 切换工程脑子 → 写 ch008 draft"。ch007 结尾和 ch008 开头之间隔了 ~8 分钟的工程操作，prose 的余温已经散了。

### 1.4 Archivist 产出手动中继

**现象**：三个 novel-archivist 子 agent 并行调用输出分析结果到 task output → 但 memory_update_plan.md 没有自动写入磁盘 → agent 需要手动从 task output 提取摘要再写盘。耗时 ~4 分钟（不含子 agent 运行时间）。

### 1.5 context_pack 部分 section 写作中未被使用

**现象**：chapter context_pack 的"本章相关伏笔""本章世界压力"等 section——在 prose 写作时几乎不被参考。agent 写作时真实在用的只有："上一章实际交接""must_happen/must_not_complete""叙事织入""本章禁止事项"。

**影响**：context_pack 长度 ~1500 字，其中 ~500 字不进入 prose 写作决策，消费了上下文预算但没有产出。

---

## 二、当前做法

```
逐章循环（每章）：
  读取 entities/ledgers/planning
  → 写 chapter context_pack.md（多个 section）
  → 写 prompt.md
  → 写 draft.txt
  → 冷读（novel-cold-reader 子 agent）
  → 修 draft（冷读反馈 + 不是X 修复）
  → 写 final.txt
  → validator（--fix-format）
  → 修 final（不是X 继续修）
  → 写 summary.yml + canon_delta.yml + reader_pass.md + review.md + brief.md
  → ⚠️ 切换工程模式
  → 下一章 context_pack 读取（包括刚写的上一章文件）

Post-round（三章结束后）：
  → 更新 active_flow.yml + rolling_plan.yml + completed_plan_log.yml
  → 调用 archivist × 3（子 agent 并行）
  → 手动从 task output 提取 archivist 结果写入 memory_update_plan.md
  → 更新 volume_state + project_state
  → post-merge QA
```

**核心特征**：工程模式和 prose 模式在每章之间交替。prose 写完后立刻进入 YAML/校验模式，prose 热态在切换中消散。

---

## 三、解决方向

### 3.1 核心原则

| 原则 | 含义 |
|------|------|
| **Prose 优先** | prose 生成阶段——不阻塞、不打断、不受 validator 后座力影响 |
| **工程后置** | YAML / 校验 / 归档——全部推到三章 prose 完成之后批量做 |
| **跨章连续叙事** | 三章 prose 连续写——不在章间做工程切换，保留 prose 温度 |

### 3.2 不做的事

- **不合并 prose 文件为一个万字段落再截断**——原因：分章需要特定的 pressure_curve 和 cut point，写完后截断返工成本可能高于省下的时间；冷读子 agent 在 10000 字输入下会稀释分析精度
- **不删除任何质检门禁**——cold-reader、archivist、validator 全部保留，只是调整它们的执行时机和阻塞级别

---

## 四、具体方案

### 4.1 调整 prose 生产模式：连续 draft → 批量工程（P0）

**改为以下流程**：

```
Phase 1: 准备（一次性）
  读取 entities/ledgers/planning
  → 写 round context_pack.md
  → 在心里跑完 3 章叙事流（不分别规划——一次想完三条线怎么交叉）

Phase 2: 连续 draft（不中断）
  → 写 ch007 context_pack（精简版，见 4.4）
  → 写 ch007 draft
  → ⚠️ 不修、不冷读、不 validator——立刻写 ch008
  → 写 ch008 context_pack → ch008 draft
  → 写 ch009 context_pack → ch009 draft
  → 此时 3 章 draft 全部热态完成

Phase 3: 批量冷读 + 修文（3 章并行）
  → 调用 novel-cold-reader × 3（并行）
  → 收集 3 份冷读反馈
  → 统一修 3 章 draft（冷读反馈 + 不是X 统一 pass）

Phase 4: 批量 final + YAML（3 章合并产出）
  → 写 final.txt × 3
  → 写 summary.yml × 3 + canon_delta.yml × 3
  → 写 reader_pass.md × 3 + review.md × 3
  → 裁掉 brief.md（或改为 3 行以内的交接条保留在 context_pack 中）

Phase 5: 批量归档（一次性）
  → 批量 validator --fix-format
  → 调用 archivist × 3（并行——自动写盘）
  → 更新 planning/entities/ledgers/volumes
  → post-merge QA
```

**关键变化**：
- Phase 2（3 章 draft 连续写）不穿插任何工程操作——prose 温度不断
- Phase 3-5（全部工程操作）在 prose 冷下来之后批量做——不打断叙事流
- cold-reader 并行调用——不浪费时间等待

**效果预期**：
- prose 连贯性：ch007→ch008→ch009 之间的温度重启消失
- 时间：从 ~50 min → 预计 ~30-35 min（省掉的是章间模式切换 ~8 min + 文件格式化的重复劳动 ~5 min + archivist 手动中继 ~4 min）

---

### 4.2 增加 `不是X` 检测脚本——一次定位，统一修改（P0）

**当前**：`不是X` 保持 error 级别（不降级）。但 agent 每次修完都要重新跑 validator 确认有没有漏的——往返 3-4 轮。

**改为**：增加脚本 `scripts/fix_not_but.py`，功能：
- 扫描指定章节的 final.txt，一次性列出所有 `不是X` 出现位置（行号 + 上下文）
- agent 拿到完整列表后，一次性判断每一处：保留（≤1 处/章）还是修改
- 全部改完之后跑一次 validator 确认

**脚本行为**：
```
$ python3 scripts/fix_not_but.py projects/chuanshu/chapters/ch007/final.txt
L7:  ...水痕——不是昨天的水珠...
L10: ...不是从侧院外的小路。是从竹林深处...
L10: ...没有钟声。不是晚课...
...
共 15 处。当前限额：1 处/章。需修改：14 处。
```

**效果预期**：
- 往返从 3-4 轮 → 1 轮（一次定位 + 一次修改 + 一次验证）
- `不是X` 修复时间从 ~12 min → ~3 min
- 不改变 validator 的 error 级别——质量门禁强度不变
- agent 拿到完整列表后可以集中判断（而不是逐句被 validator 打断），减少"修了 A 忘了 B"的漏检

**工作量**：写一个 ~30 行的 Python 脚本（扫描 `不是` 关键词 + 排除固定搭配如"是不是""岂不是"）。不影响现有 validator。

---

### 4.3 精简 chapter context_pack（P1）

**改为**：只保留 prose 写作时实际用到的 section：

| 保留 | 去掉 |
|------|------|
| 上一章实际交接 | 读取文件表 |
| must_happen / must_not_complete | 本章相关伏笔（写前无法确定） |
| 叙事织入（3 个节拍） | 本章世界压力（大部分不进入 prose 决策） |
| 本章禁止事项 | 本章信息可见性 |
| 风格约束（1-2 条） | Longform Scale Check（放到 round pack） |

**效果预期**：context_pack 从 ~1500 字 → ~800 字。注意力更集中在 prose 生成上。

---

### 4.4 Archivist 自动写盘（P1）

**改为**：novel-archivist 子 agent 直接输出 `memory_update_plan.md` 到磁盘（不是只返回文字到 task output）。文件头标注 `draft` 身份。Director 审核后再合并进 entities/ledgers。

**效果预期**：省掉手动中继 ~4 min。Archivist 的分析精度不变——只是输出通道从 task output → 文件。

---

## 五、实施优先级建议

| 序号 | 方案 | 优先级 | 工作量 | 预期收益 |
|------|------|--------|--------|----------|
| 1 | prose 连续 draft + 工程后置 | P0 | 中（改流程不涉及代码） | 连贯性 + ~8 min 时间节省 |
| 2 | `不是X` 检测脚本 | P0 | 中（写 ~30 行脚本） | ~9 min 时间节省 |
| 3 | 精简 context_pack | P1 | 低（改模板） | 注意力聚焦 prose |
| 4 | archivist 自动写盘 | P1 | 低（改 SKILL.md 调用指令） | ~4 min 时间节省 |

**如果做 1+2：预计下一轮耗时 ~33 min，prose 温度连贯性有可感知的提升。**

---

## 六、不做的事（已评估并排除）

| 提议 | 排除原因 |
|------|----------|
| 合并多章为一个万字段落再截断 | 分章返工 + 冷读稀释 > 省下的时间 |
| 删除 cold-reader 子 agent | 冷读是 prose 质量最有效的门禁——三次冷读每次都找到了真实问题 |
| 用 fast_model 写 prose | prose 质量不可妥协——premium 必须管正文 |
| 砍掉 summary.yml / canon_delta.yml | 这两个文件是记忆系统的输入——archivist 依赖它们做跨章追踪 |
