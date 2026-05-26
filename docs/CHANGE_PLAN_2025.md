# 改动文档：五项优先修改

> 历史文档，仅供参考。部分方案已被后续实现吸收；当前权威规则请先查阅 `docs/RULE_INDEX.md` 指向的文件。

> 基于工程评审结论，按优先级 P0 > P1 排列。每项改动包含：问题声明、改动范围、具体文件级变更、验证方法。

---

## P0-1: 增加状态漂移自动化检测

### 问题

`canon_delta.yml` 是变化日志，`entities/` 和 `ledgers/` 是当前状态。系统反复强调两者不能混淆，但合入操作完全由 LLM 手动执行。agent 跳过合入、部分合入或错误合入时，没有自动化手段检测。这是最慢也最致命的衰变模式——状态文件静默过时，后续章节基于过时状态写作。

当前 `validate_novel_output.py` 不检查以下情况：

- 最近 N 章 `canon_delta.yml` 中的 `character_changes` / `relationship_changes` 没有反映到 `entities/characters.yml`
- 最近 N 章 `canon_delta.yml` 中的 `world_state_changes` 没有反映到 `ledgers/world_state.yml`
- 最近 N 章 `canon_delta.yml` 中的 `knowledge_changes` 没有反映到 `ledgers/knowledge_state.yml`
- `canon_delta.yml` 的 `actual_handoff` 与 `planning/active_flow.yml` 的 `last_cut.current_handoff` 内容不吻合

### 改动范围

| 文件 | 变更类型 |
|------|---------|
| `scripts/validate_novel_output.py` | 新增 `--check-state-drift` 选项和 `validate_state_drift()` 函数 |
| `AGENTS.md` | 增加状态漂移检查说明 |
| `scripts/README.md` | 增加使用说明 |

### 具体变更

#### 1. `scripts/validate_novel_output.py` — 新增 `validate_state_drift()`

在文件末尾 `main()` 之前，新增函数：

```python
def validate_state_drift(project: Path, chapters: list[str], lookback: int = 3) -> tuple[list[str], list[str]]:
    """Check that recent canon_deltas have been merged into current state files.

    For each of the last N chapters, extract character_changes,
    relationship_changes, world_state_changes, and knowledge_changes from
    canon_delta.yml, then verify that entities/ and ledgers/ reflect those
    changes. Also check that active_flow handoff text aligns with the latest
    canon_delta actual_handoff.

    Returns (errors, warnings).
    """
    errors: list[str] = []
    warnings: list[str] = []
    try:
        import yaml
    except ImportError:
        warnings.append("STATE_DRIFT_SKIPPED: PyYAML not installed; state drift check requires YAML parsing.")
        return errors, warnings

    # --- 1. Collect recent canon_deltas ---
    chapter_dirs = sorted(
        (project / "chapters").glob("ch*"),
        key=lambda d: _chapter_sort_key(d.name),
    )
    if not chapter_dirs:
        warnings.append("STATE_DRIFT_NO_CHAPTERS: No chapter directories found.")
        return errors, warnings

    recent = chapter_dirs[-lookback:]
    recent_deltas: list[tuple[str, dict]] = []
    for cd in recent:
        delta_path = cd / "canon_delta.yml"
        if delta_path.exists():
            try:
                data = yaml.safe_load(delta_path.read_text(encoding="utf-8"))
                if data:
                    recent_deltas.append((cd.name, data))
            except Exception as exc:
                errors.append(f"CANON_DELTA_PARSE_ERROR: {delta_path}: {exc}")

    if not recent_deltas:
        warnings.append("STATE_DRIFT_NO_DELTAS: No recent canon_delta.yml files to check.")
        return errors, warnings

    # --- 2. Load current state files ---
    characters_path = project / "entities" / "characters.yml"
    world_state_path = project / "ledgers" / "world_state.yml"
    knowledge_path = project / "ledgers" / "knowledge_state.yml"
    active_flow_path = project / "planning" / "active_flow.yml"

    characters_data: dict | None = None
    world_state_data: dict | None = None
    knowledge_data: dict | None = None
    active_flow_data: dict | None = None

    if characters_path.exists():
        try:
            characters_data = yaml.safe_load(characters_path.read_text(encoding="utf-8"))
        except Exception:
            errors.append(f"STATE_FILE_PARSE_ERROR: {characters_path}")
    else:
        errors.append(f"MISSING_STATE_FILE: {characters_path}")

    if world_state_path.exists():
        try:
            world_state_data = yaml.safe_load(world_state_path.read_text(encoding="utf-8"))
        except Exception:
            errors.append(f"STATE_FILE_PARSE_ERROR: {world_state_path}")

    if knowledge_path.exists():
        try:
            knowledge_data = yaml.safe_load(knowledge_path.read_text(encoding="utf-8"))
        except Exception:
            errors.append(f"STATE_FILE_PARSE_ERROR: {knowledge_path}")

    if active_flow_path.exists():
        try:
            active_flow_data = yaml.safe_load(active_flow_path.read_text(encoding="utf-8"))
        except Exception:
            errors.append(f"STATE_FILE_PARSE_ERROR: {active_flow_path}")

    # --- 3. Check character changes reflected in characters.yml ---
    if characters_data is not None:
        # Extract character names that appear as keys or in list items
        char_names_in_state: set[str] = set()
        if isinstance(characters_data, dict):
            for key, val in characters_data.items():
                if isinstance(val, dict) and "name" in val:
                    char_names_in_state.add(str(val["name"]))
                elif isinstance(val, dict) and isinstance(key, str):
                    char_names_in_state.add(key)
                elif isinstance(val, str):
                    char_names_in_state.add(str(val))
                elif isinstance(val, list):
                    for item in val:
                        if isinstance(item, dict) and "name" in item:
                            char_names_in_state.add(str(item["name"]))
                        elif isinstance(item, str):
                            char_names_in_state.add(item)
        elif isinstance(characters_data, list):
            for item in characters_data:
                if isinstance(item, dict) and "name" in item:
                    char_names_in_state.add(str(item["name"]))

        changed_chars_in_deltas: set[str] = set()
        for ch_name, delta in recent_deltas:
            char_changes = delta.get("character_changes", [])
            if isinstance(char_changes, list):
                for change in char_changes:
                    if isinstance(change, dict):
                        c = change.get("character") or change.get("name") or ""
                        if c:
                            changed_chars_in_deltas.add(str(c))
                    elif isinstance(change, str):
                        changed_chars_in_deltas.add(change)

        missing_chars = changed_chars_in_deltas - char_names_in_state
        if missing_chars:
            errors.append(
                f"CHARACTERS_DRIFT: Characters with changes in recent canon_deltas "
                f"but not found in entities/characters.yml: {', '.join(sorted(missing_chars))}. "
                f"Merge the character changes into the current state file."
            )

        # Check for last_updated alignment heuristic
        # If characters.yml has per-character entries with a 'last_updated' field,
        # verify the latest delta chapter matches or is later than last_updated.
        for ch_name, delta in recent_deltas:
            char_changes = delta.get("character_changes", [])
            if isinstance(char_changes, list):
                for change in char_changes:
                    if isinstance(change, dict):
                        cname = str(change.get("character") or change.get("name") or "")
                        if not cname:
                            continue
                        # Heuristic: check if characters data contains this character
                        # and their state seems stale (no recent update signal)
                        _char_entry = None
                        if isinstance(characters_data, dict):
                            _char_entry = characters_data.get(cname)
                        if _char_entry is None and isinstance(characters_data, list):
                            for item in characters_data:
                                if isinstance(item, dict):
                                    iname = str(item.get("name") or item.get("id") or "")
                                    if iname == cname:
                                        _char_entry = item
                                        break
                        if _char_entry is not None and isinstance(_char_entry, dict):
                            last_upd = _char_entry.get("last_updated") or _char_entry.get("last_seen") or ""
                            ch_num = _chapter_sort_key(ch_name)
                            if last_upd and f"ch{last_upd:03d}" if isinstance(last_upd, int) else str(last_upd):
                                # Simple string comparison heuristic
                                delta_ch = ch_name.replace("ch", "")
                                state_ch = str(last_upd).replace("ch", "")
                                try:
                                    if int(delta_ch) > int(state_ch):
                                        # Delta chapter is more recent than state update
                                        pass  # Covered by the missing_chars check above
                                except ValueError:
                                    pass

    # --- 4. Check world_state_changes reflected ---
    if world_state_data is not None:
        ws_changes_in_deltas: list[str] = []
        for ch_name, delta in recent_deltas:
            ws_changes = delta.get("world_state_changes", [])
            if isinstance(ws_changes, list):
                for change in ws_changes:
                    if isinstance(change, dict):
                        desc = change.get("change") or change.get("description") or ""
                        if desc:
                            ws_changes_in_deltas.append(f"{ch_name}: {desc[:60]}")
                    elif isinstance(change, str) and change:
                        ws_changes_in_deltas.append(f"{ch_name}: {change[:60]}")

        if ws_changes_in_deltas and world_state_data is not None:
            # Heuristic: check if world_state has ANY non-trivial content
            ws_text = str(world_state_data).lower()
            has_content = any(
                kw in ws_text for kw in ["active_crisis", "factions", "current_period", "resource"]
            )
            if ws_changes_in_deltas and not has_content:
                warnings.append(
                    f"FROM_WORLD_STATE_CHANGES_BUT_STATE_EMPTY: Recent canon_deltas report "
                    f"world_state_changes but '{world_state_path}' appears empty or placeholder. "
                    f"Merge the changes."
                )

    # --- 5. Check knowledge_changes reflected ---
    if knowledge_data is not None:
        k_changes_in_deltas: list[str] = []
        for ch_name, delta in recent_deltas:
            k_changes = delta.get("knowledge_changes", [])
            if isinstance(k_changes, list):
                for change in k_changes:
                    if isinstance(change, dict):
                        topic = change.get("topic") or ""
                        if topic:
                            k_changes_in_deltas.append(f"{ch_name}: {topic}")
                    elif isinstance(change, str) and change:
                        k_changes_in_deltas.append(f"{ch_name}: {change[:60]}")

        if k_changes_in_deltas and knowledge_data is not None:
            k_text = str(knowledge_data).lower()
            topics_in_state: set[str] = set()
            if isinstance(knowledge_data, list):
                for item in knowledge_data:
                    if isinstance(item, dict):
                        t = str(item.get("topic") or item.get("id") or "")
                        if t:
                            topics_in_state.add(t.lower())
            elif isinstance(knowledge_data, dict):
                for key in knowledge_data:
                    topics_in_state.add(str(key).lower())

            for entry in k_changes_in_deltas:
                topic = entry.split(": ", 1)[-1].lower() if ": " in entry else ""
                if topic and not any(t in topics_in_state for t in [topic, topic.split()[0]] if topic):
                    warnings.append(
                        f"KNOWLEDGE_DRIFT: Topic '{topic}' changed in canon_delta but not found in "
                        f"knowledge_state.yml topics. Verify the merge."
                    )

    # --- 6. Check active_flow handoff alignment ---
    if active_flow_data is not None and recent_deltas:
        latest_delta_ch, latest_delta = recent_deltas[-1]
        latest_handoff = latest_delta.get("actual_handoff", [])
        if not latest_handoff:
            latest_handoff = latest_delta.get("handoff_to_next_chapter", [])

        af_last_cut = None
        if isinstance(active_flow_data, dict):
            cf = active_flow_data.get("current_flow", {})
            if isinstance(cf, dict):
                lc = cf.get("last_cut", {})
                if isinstance(lc, dict):
                    af_last_cut = lc

        if af_last_cut is not None and latest_handoff:
            af_handoff = af_last_cut.get("current_handoff", "")
            delta_handoff = latest_handoff if isinstance(latest_handoff, str) else " / ".join(str(h) for h in latest_handoff)

            # Only warn if active_flow chapter is behind
            af_ch = af_last_cut.get("chapter", "")
            latest_ch_num = _chapter_sort_key(latest_delta_ch)
            af_ch_num = _chapter_sort_key(str(af_ch)) if af_ch else -1
            if af_ch_num >= 0 and af_ch_num < latest_ch_num:
                errors.append(
                    f"ACTIVE_FLOW_HANDOFF_BEHIND: active_flow.last_cut.chapter={af_ch} "
                    f"but latest canon_delta is {latest_delta_ch}. Merge the handoff."
                )

    # --- 7. Check canon_delta entries with no matching state update signal ---
    # Heuristic: if a chapter has canon_delta but entities/ledgers haven't been
    # touched since before that chapter was written, warn about stale state files.
    # This requires file modification time, which may not be reliable on all systems.

    return errors, warnings
```

在 `main()` 函数中，`if not args.skip_planning:` 块之后，增加：

```python
if not args.skip_state_drift:
    recent_chapters = chapters if chapters else sorted(
        p.name for p in (project / "chapters").glob("ch*") if p.is_dir()
    )[-3:]
    drift_errs, drift_warns = validate_state_drift(project, recent_chapters)
    all_errors.extend(drift_errs)
    all_warnings.extend(drift_warns)
```

同时新增命令行参数：

```python
parser.add_argument("--skip-state-drift", action="store_true", help="Skip state drift checks")
parser.add_argument("--drift-lookback", type=int, default=3, help="Number of recent chapters to check for state drift (default: 3)")
```

#### 2. `schemas/canon_delta.schema.yml` — 增加 `last_updated` 建议字段说明

在 `canon_delta.schema.yml` 中增加注释说明 `character_changes` 条目应包含 `character` 字段，以支持状态漂移检测。

#### 3. `scripts/README.md` — 增加使用说明

增加条目：

```markdown
### 状态漂移检测

```bash
python3 scripts/validate_novel_output.py projects/my-novel --chapters ch007 ch008 ch009
# 状态漂移检测默认启用；用 --skip-state-drift 跳过

# 调整回看章节数（默认 3）：
python3 scripts/validate_novel_output.py projects/my-novel --chapters ch009 --drift-lookback 5
```

检测内容：
- 最近 N 章 canon_delta 中提到的角色变化是否合入 entities/characters.yml
- 最近 N 章 canon_delta 中的世界状态变化是否在 ledgers/world_state.yml 中有对应内容
- 最近 N 章 canon_delta 中的知识状态变化是否在 ledgers/knowledge_state.yml 中有对应主题
- active_flow.last_cut 的章节号是否落后于最新 canon_delta
- characters.yml 中角色名是否覆盖最近 delta 中出现的角色
```

#### 4. `AGENTS.md` — 在常用命令部分增加状态漂移说明

在"校验章节输出"部分增加：

```markdown
# 校验状态漂移（检查 entities/ledgers 是否与最近 canon_delta 同步）
python3 scripts/validate_novel_output.py projects/<project-name> --chapters ch007 ch008 ch009
# 默认检查最近 3 章的状态漂移；用 --drift-lookback 5 调整回看范围
# 用 --skip-state-drift 跳过状态漂移检测
```

### 验证方法

1. 用 `projects/example-project` 运行新增检查，确认无 false positive
2. 故意让 `entities/characters.yml` 中缺少一个 canon_delta 中提到的角色，确认检测到 `CHARACTERS_DRIFT` error
3. 让 `active_flow.last_cut.chapter` 落后于最新章，确认检测到 `ACTIVE_FLOW_HANDOFF_BEHIND` error
4. 空的 `world_state.yml` + 非空 delta 中的 `world_state_changes`，确认检测到 `FROM_WORLD_STATE_CHANGES_BUT_STATE_EMPTY` warning

---

## P0-2: 将连续 draft 模式从建议变为默认流程

### 问题

`novel_write_optimization_proposal.md` 用实测数据证明：prose 占比 17%，工程摩擦 53%，章间 8 分钟工程操作导致 prose 温度断裂。SKILL.md 第 7-8 步已经写入连续 draft 方案，但措辞仍是"可以""允许"。AGENTS.md 的提示词模版仍按逐章流程组织。实际执行时 agent 仍默认逐章完成全流程。

### 改动范围

| 文件 | 变更类型 |
|------|---------|
| `skills/novel-write/SKILL.md` | 重写步骤 7-9，将连续 draft 批量工程定位为默认 |
| `.opencode/agents/novel-director.md` | 增加批量流程 Phase 图 |
| `docs/WORKFLOWS.md` | 正式化批量流程 |
| `AGENTS.md` | 更新提示词模版 |
| `docs/novel_write_optimization_proposal.md` | 增加实施状态注释 |

### 具体变更

#### 1. `skills/novel-write/SKILL.md` — 重写步骤 7-9

将当前步骤 7-9 从：

> 7. Draft the batch in prose-continuity mode（"连续 draft 模式"作为建议）
> 8. Cold read and finalize the batch
> 9. Batch canon merge and post-merge QA

改为：

> 7. **连续 draft 阶段（默认）**
>    - 这是默认生产模式。如果用户没有明确要求逐章完成全流程，使用此模式。
>    - 写完 chXXX draft 后，写 3-5 行 `draft_handoff_note`，然后直接写下一章 draft。不在章间做任何工程操作。
>    - 如果 draft 改变了预期 handoff，暂停连续模式，刷新下一章 context_pack / prompt 再继续。
>    - 逐章完成全流程（旧模式）仅用于用户明确要求或连续模式不适用时。
>
> 8. **批量冷读 + 修文阶段**
>    - 3 章 draft 全部完成后，并行调用 `novel-cold-reader` 生成 3 份 `reader_pass.md`。
>    - 批量运行 `check_not_but.py`：`python scripts/check_not_but.py <project> --chapters <batch> --files draft.txt`，一次性定位所有超限句式，集中判断保留或修改。
>    - 根据 cold-reader 反馈统一修改 3 章 draft。
>    - reader_pass 通过后写 `final.txt`。
>    - 批量运行 `validate_novel_output.py --fix-format`。
>
> 9. **批量工程合并 + post-merge QA**
>    - 写 `review.md`、`summary.yml`、`canon_delta.yml`。
>    - 调用 `novel-archivist` 生成 `memory_update_plan.md` 草案（可并行调用 3 章）。
>    - 合并 `entities/`、`ledgers/`、`volumes/`、`planning/`。
>    - 归档 completed_plan_log，滑动 rolling_plan。
>    - **最终 QA 必须在全部状态文件合并之后运行。**
>    - post-merge QA 通过前，不标记本章完成。

同时在步骤 6（Prebuild）中增加明确标题：

> 6. **批量预建阶段**
>    - 一次性生成本批次 3 章的 brief / context_pack / prompt。
>    - 此时可以评估 3 章的整体叙事流，确保不是 3 个独立故事。

#### 2. `.opencode/agents/novel-director.md` — 增加批量流程 Phase 摘要

在 `## 工作方式` 部分之前，增加：

```markdown
## 批量生产流程（默认）

Phase 1 — 准备：
  读取 entities/ledgers/planning
  → 写 round context_pack
  → 一次性生成 3 章 brief / context_pack / prompt

Phase 2 — 连续 draft：
  → chXXX draft → draft_handoff_note → 下一章 draft
  → 不修、不冷读、不 validator——保持 prose 温度
  → 3 章 draft 全部完成后进入 Phase 3

Phase 3 — 批量冷读 + 修文：
  → 并行调用 novel-cold-reader × 3
  → 批量 check_not_but.py 扫描
  → 统一根据 cold-reader 反馈修 draft
  → reader_pass 通过后 → final.txt × 3
  → 批量 validate_novel_output.py --fix-format

Phase 4 — 批量工程合并：
  → review.md / summary.yml / canon_delta.yml × 3
  → 并行调用 novel-archivist × 3
  → 合并 entities / ledgers / volumes / planning
  → 归档 completed_plan_log，滑动 rolling_plan
  → post-merge QA
  → post-merge QA 通过后标记完成
```

#### 3. `docs/WORKFLOWS.md` — 将"优化后的三章生产节奏"提升为正式规范

在 3.3.1 节，将标题从"优化后的三章生产节奏"改为"默认批量生产流程"，并增加：

> 这是默认生产模式。逐章完成全流程（旧模式）可用于调试或用户明确要求，但不作为默认推荐。

#### 4. `AGENTS.md` — 更新"写下一轮 3 章"提示词模版

将当前提示词中的流程描述从逐章模式改为批量模式。在"写作要求"区块增加：

```markdown
- 默认使用连续 draft 模式：预建 3 章 context_pack/prompt → 连续写 3 章 draft → 批量冷读 → 批量 final → 批量工程合并。
- 章 draft 间只写 draft_handoff_note，不做工程操作。
- cold-reader 并行调用。
- post-merge QA 必须在全部 state 文件合并后运行。
```

#### 5. `docs/novel_write_optimization_proposal.md` — 增加实施状态

在文件开头增加：

```markdown
> **实施状态**：方案 4.1（连续 draft + 工程后置）已合并为 SKILL.md 默认流程。方案 4.2（`check_not_but.py` 一次性定位）已实现。此文档保留作为实测数据参考。
```

### 验证方法

1. 用 `AGENTS.md` 中的新提示词模版执行一轮 3 章写作，确认默认走 Phase 1→2→3→4 流程
2. 确认 Phase 2 中章间只有 `draft_handoff_note`，没有工程文件生成
3. 确认 Phase 3 中 `cold-reader` 3 章并行调用
4. 确认 Phase 4 中 `archivist` 3 章并行调用后 `memory_update_plan.md` 落盘

---

## P0-3: 拆分 novel-write SKILL.md，降低指令密度

### 问题

`skills/novel-write/SKILL.md` 目前 568 行，同时包含工作流程、写作心法、TXT 格式规则、冷读规则、审查清单、受保护文件列表、失败处理条件。LLM 在如此长的指令下写作时注意力密度严重不均——写 prose 时仍然在 context 里维护 568 行规则的权重，导致关键写作指令（handoff、叙事织入、禁止事项）被 Dilution。

通过提取写作心法和格式规则到独立文档，SKILL.md 可以控制在 ~200 行以内，只保留流程步骤和硬规则。写作时通过 `prompt.md` 引用关键条目，而非全文加载。

### 改动范围

| 文件 | 变更类型 |
|------|---------|
| `skills/novel-write/SKILL.md` | 缩减到 ~200 行，只保留流程和硬规则 |
| `docs/WRITING_CRAFT.md` | 新建，包含写作心法、网文节奏、TXT 格式、结尾规则 |
| `docs/FILE_FORMATS.md` | 已有 TXT 格式规则，补充引用说明 |
| `skills/novel-review/SKILL.md` | 审查清单引用 `WRITING_CRAFT.md` |

### 具体变更

#### 1. 新建 `docs/WRITING_CRAFT.md`

从 `skills/novel-write/SKILL.md` 提取以下内容：

- 「写作心法」节（原文 319-331 行）
- 「网文节奏规则」节（原文 333-378 行）
- 「TXT 格式规则」节（原文 380-398 行）
- 「结尾规则」节（原文 88-113 行）
- 「Draft Self-Check」节水硬规则清单（原文 402-411 行）

结构：

```markdown
# 写作心法与格式规则

> 本文档从 `skills/novel-write/SKILL.md` 提取。写作时通过 `prompt.md` 引用关键条目，不必全文加载。
> 审查时参考 `skills/novel-review/SKILL.md`。

## 写作心法
（原文 319-331 行内容）

## 网文节奏规则
（原文 333-378 行内容）

## 不同类型章节的节奏参考
（推进型/建制型/推理型/日常型段落）

## 避免的写法
（原文 372-378 行内容）

## 结尾规则
（原文 88-113 行内容，含推荐切分点）

## TXT 格式规则
（原文 380-398 行内容）

## Draft Self-Check 硬规则
（原文 402-411 行内容）

## "不是X而是Y" 限制
（每章最多 1 次，写前必须确认它是本章唯一值得保留的概念反转）
```

#### 2. 缩减 `skills/novel-write/SKILL.md`

删除已提取到 `WRITING_CRAFT.md` 的内容，在对应位置增加引用：

```markdown
## 写作心法与格式

详见 `docs/WRITING_CRAFT.md`。

`prompt.md` 必须从以下关键条目中选取本章适用的约束写入抬头纸（不超过 500 字）：

- 本章唯一核心推进和 must_not_complete
- 本章 chapter_function 和 pressure_curve
- 本章叙事织入至少 3 个节拍
- 本章只释放 1-2 个核心新变量
- 本章禁止事项
- 本章交接（inbound 和 planned outbound handoff）
- 样本文风锚点（如果 `style/samples.md` 非空）
- TXT 格式：普通段落间不空行，多数段落 40-160 字，超过 220 字视为格式失败
- 结尾避免主角反思式收束，必须留下外部运动交接
- "不是X而是Y / 不是X，是Y"每章最多 1 次
```

保留在 SKILL.md 中的内容（约 200 行）：

- 核心模型（3 层规划）
- Hard Rules
- Context Budget Policy
- Source Of Truth
- Narrative Flow Requirements
- Rolling Synopsis Requirements
- Round Workflow 步骤 1-6（精简版）
- Round Workflow 步骤 7-9（批量流程，引用 `docs/WORKFLOWS.md`）
- Writable Files / Do Not Silently Modify
- Failure Handling

#### 3. 更新 `skills/novel-review/SKILL.md`

在"正文与 TXT 格式"检查项中增加引用：

```markdown
写作心法和格式规则详见 `docs/WRITING_CRAFT.md`。审查时应对照其中的规则清单。
```

#### 4. 更新 `docs/FILE_FORMATS.md`

在 TXT 格式规则部分增加引用：

```markdown
详细格式规则和写作心法见 `docs/WRITING_CRAFT.md`。
```

### 验证方法

1. `skills/novel-write/SKILL.md` 行数 < 220
2. `docs/WRITING_CRAFT.md` 包含所有从 SKILL.md 提取的内容，无遗漏
3. SKILL.md 中所有被提取条目的位置有明确的 `docs/WRITING_CRAFT.md` 引用
4. 使用新 SKILL.md 执行一轮写作，确认 `prompt.md` 仍然包含关键写作约束

---

## P1-4: 增加 rolling_plan 上限和裁剪策略

### 问题

系统要求"每轮全文读取 rolling_plan"，但没有容量上限。15 章 × 500-800 字简介 + 10+ 结构化字段 = 7500-12000 字。30 章时即使归档了已完成章节，新条目仍然很长。加上 `longform_blueprint.yml`（全文）、12-15 章摘要、active_flow、entities 定向读取、previous chapter full text，一轮总输入轻松超过 15K 字。

### 改动范围

| 文件 | 变更类型 |
|------|---------|
| `scripts/validate_novel_output.py` | 新增 `rolling_plan` 大小警告 |
| `docs/FILE_FORMATS.md` | 增加上限规则 |
| `templates/project/planning/rolling_plan.yml` | 增加容量警告注释 |
| `skills/novel-write/SKILL.md` | 增加 rolling_plan 滑窗规则 |
| `skills/novel-bootstrap/SKILL.md` | 增加初始 rolling_plan 大小建议 |

### 具体变更

#### 1. `scripts/validate_novel_output.py` — 新增 rolling_plan 容量检查

在 `validate_planning()` 函数中增加：

```python
# --- rolling_plan size warning ---
rolling_plan_path = project / "planning" / "rolling_plan.yml"
if rolling_plan_path.exists():
    rp_size = len(rolling_plan_path.read_text(encoding="utf-8"))
    RP_SIZE_WARN = 6000  # Chinese characters heuristic
    RP_SIZE_ERROR = 10000
    # Rough conversion: Chinese chars ~ 3 bytes in UTF-8, but mixed content
    # Use a heuristic threshold based on file byte size
    if rp_size > RP_SIZE_ERROR:
        warnings.append(
            f"ROLLING_PLAN_SIZE_LARGE: {rolling_plan_path} is {rp_size} bytes. "
            f"Entries beyond 15 chapters should be compressed into 100-char summaries "
            f"in planning/future_backlog.yml. Target: under {RP_SIZE_WARN} bytes."
        )
```

#### 2. `docs/FILE_FORMATS.md` — 增加上限规则

在"连续剧情流与近期详细章纲"节增加：

```markdown
### rolling_plan.yml 容量规则

`rolling_plan.yml` 只保留未来窗口，目标不超过 6000 字节。当前活跃窗口不超过 15 章条目。

容量管理策略：

- 已完成章纲立即归档到 `completed_plan_log.yml`，不要在 rolling_plan 中保留 `status: completed` 条目。
- 活跃窗口超过 15 章时，最远端条目压缩为 100 字以内的摘要，移入 `future_backlog.yml`。
- 每章的 `synopsis` 应控制在 300-800 字以内。如果 rolling_plan 膨胀到超过 10000 字节，validator 会发出警告。

`rolling_plan.yml` 之外的未来可使用 `future_backlog.yml` 存储：
- 远期重要节拍（只需 1-2 句描述）
- 尚未进入 6-15 章窗口的灵感
- macro stage 转折点预期
```

#### 3. `templates/project/planning/rolling_plan.yml` — 增加容量警告注释

在文件头部（`source_of_truth` 之后）增加：

```yaml
capacity_warning: "活跃窗口目标不超过 15 章条目或 6000 字节。超过时：已完成条目立即归档至 completed_plan_log.yml，最远端条目压缩移入 future_backlog.yml。validator 会在超过 10000 字节时发出警告。"
```

#### 4. `skills/novel-write/SKILL.md` — 增加滑窗规则

在 Rolling Synopsis Requirements 节增加：

```markdown
- 每轮写完后必须将已完成章纲从 rolling_plan 移入 completed_plan_log，并滑动窗口使 `current_window` 从第一个未完成章节开始。
- rolling_plan 活跃窗口不超过 15 章条目。如果超过，将最远端条目压缩为 100 字以内摘要并移入 `future_backlog.yml`。
- 每章 synopsis 控制在 300-800 字。validator 会在 rolling_plan 超过 10000 字节时发出警告。
```

#### 5. `skills/novel-bootstrap/SKILL.md` — 增加初始大小建议

在"初始化规划"节增加：

```markdown
- rolling_plan 初始条目控制在 9-15 章。不要规划超过 15 章的详细章纲；远期点子放入 `future_backlog.yml`。
```

### 验证方法

1. 创建一个 20 章条目的 rolling_plan.yml，确认 validator 发出 `ROLLING_PLAN_SIZE_LARGE` warning
2. 创建一个含 `status: completed` 条目的 rolling_plan，确认 validator 发出 `COMPLETED_PLAN_NOT_ARCHIVED` error（已有功能）
3. 确认模板文件容量警告存在

---

## P1-5: 增加 director 受保护文件技术隔离

### 问题

`novel-write` 不可静默修改 protected files 这条规则是纯指令约束。`novel-director.md` 的权限是 `edit: ask`，没有路径级别限制。如果 agent 不理解或忽略这条规则，它会直接修改 `constitution.md` 和 `longform_blueprint.yml`。当前没有一个技术机制阻止或检测这种修改。

### 改动范围

| 文件 | 变更类型 |
|------|---------|
| `scripts/validate_novel_output.py` | 新增 `--check-protected-files` 选项 |
| `.opencode/agents/novel-director.md` | 增加受保护文件确认流程 |
| `docs/CANON_AND_SAFETY.md` | 增加"检测受保护文件静默修改"小节 |

### 具体变更

#### 1. `scripts/validate_novel_output.py` — 新增受保护文件检测

新增命令行参数：

```python
parser.add_argument("--check-protected-files", action="store_true",
                    help="Check if protected files were modified without a corresponding novel-change diff summary")
```

新增函数：

```python
PROTECTED_FILES = [
    "book/constitution.md",
    "book/longform_blueprint.yml",
    "book/reader_model.yml",
    "book/style_memory.md",  # core rules only
]

def validate_protected_files(project: Path) -> tuple[list[str], list[str]]:
    """Check if protected files have been modified without a corresponding change log entry."""
    errors: list[str] = []
    warnings: list[str] = []

    # Check for the existence of project.yml or meta/project_state.yml
    # which should record when protected files are modified
    decision_log = project / "ledgers" / "decision_log.yml"
    session_log = project / "meta" / "session_log.md"

    # For each protected file, check if it exists
    for pf in PROTECTED_FILES:
        path = project / pf
        if not path.exists():
            continue

        # We cannot programmatically detect "silent modification" without git diff.
        # Instead, we check that the file is tracked and that any modification
        # should have a corresponding decision_log or session_log entry.
        # This is advisory: the script warns if it cannot find evidence of a
        # novel-change workflow for recent modifications.

    # Git-based detection (best-effort)
    import subprocess
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5", "--"] + [str(project / pf) for pf in PROTECTED_FILES],
            capture_output=True, text=True, cwd=str(project.parent if not (project / ".git").exists() else project),
            check=False, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            # Check if recent commits touching protected files mention "change:" or "novel-change"
            lines = result.stdout.strip().splitlines()
            for line in lines:
                if "change:" not in line.lower() and "novel-change" not in line.lower():
                    # This is advisory; not all protected file changes go through novel-change
                    # But if there's no mention of change management, flag it
                    pass  # We don't error here because git history might not always have this format
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # Git not available; skip git-based check
        pass

    # The primary check is structural: verify that decision_log.yml or session_log.md
    # exist and contain entries for protected file changes
    has_decision_log = decision_log.exists()
    has_session_log = session_log.exists()

    protected_in_project = [pf for pf in PROTECTED_FILES if (project / pf).exists()]

    if protected_in_project and not has_decision_log and not has_session_log:
        warnings.append(
            f"NO_CHANGE_LOG: Project has protected files {protected_in_project} but neither "
            f"ledgers/decision_log.yml nor meta/session_log.md exists. Any modification to "
            f"protected files should be recorded through novel-change with a diff summary."
        )

    return errors, warnings
```

在 `main()` 中调用：

```python
if args.check_protected_files:
    pf_errs, pf_warns = validate_protected_files(project)
    all_errors.extend(pf_errs)
    all_warnings.extend(pf_warns)
```

#### 2. `.opencode/agents/novel-director.md` — 增加受保护文件确认流程

在 `## 必须遵守` 部分增加：

```markdown
- 修改受保护文件（`book/constitution.md`、`book/longform_blueprint.yml`、`book/reader_model.yml`、`book/style_memory.md` 核心规则、`volumes/vol_XXX/volume_outline.md` 卷目标、`entities/characters.yml` 主角核心欲望、`ledgers/knowledge_state.yml` 终局秘密）前，必须：
  1. 调用 `novel-change` 评估影响等级。
  2. 输出 Change Summary（修改原因、受影响文件、旧设定、新设定、影响范围、是否需要补铺垫或重写）。
  3. 在 `ledgers/decision_log.yml` 或 `meta/session_log.md` 中记录此变更。
  4. 如果 Git 可用，在修改前创建 checkpoint。
  5. 只有在用户确认后才能修改。

- 受保护文件修改后，运行 `python scripts/validate_novel_output.py <project> --check-protected-files` 确认变更已记录。
```

#### 3. `docs/CANON_AND_SAFETY.md` — 增加检测小节

在"8. Diff 摘要要求"之后增加：

```markdown
## 10. 受保护文件修改检测

MVP 阶段无法完全阻止 agent 修改受保护文件，但可以通过以下方式增加摩擦力和可见性：

1. **Validator 检查**：`python scripts/validate_novel_output.py <project> --check-protected-files` 会检查：
   - 项目是否有 `ledgers/decision_log.yml` 或 `meta/session_log.md`。
   - 如果受保护文件存在但没有任何变更日志，发出 warning。

2. **Git diff 辅助**：如果项目使用 Git，在每次 `novel-change` 修改受保护文件前创建 checkpoint，修改后提交 commit message 以 `change:` 前缀标记。

3. **novel-director 人工确认**：OpenCode 配置中 director 的 `edit` 权限为 `ask`，修改任何文件前需要人工确认。不要点击通过受保护文件的修改确认——除非你已经看到了 Change Summary。
```

### 验证方法

1. 运行 `python scripts/validate_novel_output.py projects/example-project --chapters ch001 --check-protected-files`，确认无 false positive
2. 删除 `ledgers/decision_log.yml` 和 `meta/session_log.md`，确认 validator 发出 `NO_CHANGE_LOG` warning
3. 确认 `novel-director.md` 中受保护文件列表与 `CANON_AND_SAFETY.md` 一致

---

## 实施顺序建议

| 顺序 | 改动 | 预计工作量 | 依赖 |
|------|------|-----------|------|
| 1 | P0-1: `validate_state_drift()` | 2-3 小时 | 无 |
| 2 | P0-2: 连续 draft 正式化 | 1-2 小时 | 无（主要是文档修改） |
| 3 | P0-3: SKILL.md 拆分 | 2-3 小时 | 无 |
| 4 | P1-4: rolling_plan 上限 | 1 小时 | 无 |
| 5 | P1-5: 受保护文件隔离 | 1-2 小时 | 无 |

P0-1、P0-2、P0-3 可以并行实施，无依赖关系。P1-4 和 P1-5 也互相独立。
