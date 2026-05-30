# Chapter Writing Packet

## Metadata

- project: example-project
- round: round_001
- chapter: ch001
- generated_at: example
- agent: template

## Read Files

| file | read_mode | reason | key_takeaway |
| --- | --- | --- | --- |
| planning/rolling_plan.yml | excerpt | 本章章纲来源 | ch001 是旧灯芯异常开局。 |
| planning/active_flow.yml | excerpt | 当前连续剧情流 | 第一章需要留下可承接的外部压力。 |

## Source References

| claim | source |
| --- | --- |
| 林栖听见旧灯芯里的声音 | chapters/ch001/final.txt |
| 巡灯署回收旧灯芯 | chapters/ch001/final.txt |

## Longform Scale Check

- current_macro_stage: opening
- scale_level: local_city_mystery
- progression_budget: 只展示异常，不解释系统全貌。
- reveal_limits: 不揭示声音身份，不解释巡灯署真实目的。
- scale_drift_risks: 不把第一章写成设定百科。

## Cut Continuity

- previous_actual_handoff: none
- current_opening_anchor: 大雾、旧城区、三号灯异常。
- justified_cut_shift: none
- planned_handoff: 林栖私藏碎片，巡灯署是否察觉留下悬念。

## Reader Reward Check

- concrete_reward: 第一章给出旧灯芯会残留声音的异常。
- existing_debt_advanced: none
- new_question_created: 声音是谁，巡灯署为何回收旧灯芯。
- external_change: 林栖从普通修灯人变成私藏线索的人。
- memorable_image_or_action: 碎片滑进袖口，贴着脉搏发凉。

## Background Use Audit

| 背景项 | 类型 | 权威来源 | 本章用途 | writer 可微调 | writer 禁止发明 |
| --- | --- | --- | --- | --- | --- |
| 林栖 | character | entities/characters.yml | 修灯人主角，执行私藏动作 | 小动作、维修习惯 | 核心欲望和父亲线真相 |
| 巡灯署 | faction | entities/factions.yml / ledgers/world_state.yml | 现场回收旧灯芯，形成机构压力 | 现场人员姿态 | 真实动机和上级秘密 |
| 外环灯巷 | location | entities/locations.yml | 雾夜修灯现场 | 雾、金属、灯油质感 | 扩大成全城规则解释 |
| 旧灯芯碎片 | item | entities/items.yml / foreshadowing.yml | 异常声音和私藏证据 | 触感、温度、袖口动作 | 碎片完整规则 |

- newly_completed_background: none
- missing_background: # none
- local_texture_allowed: 雾、灯油味、铜罩余热、巡灯署靴声、路人短反应。
- hard_background_limits: 不解释巡灯署真实目的，不揭示声音身份，不补全旧灯芯规则。

## Writing Card

**Chapter Design**

- one_line_goal: 林栖修理三号灯时听见旧灯芯里的陌生声音，并私藏碎片。
- chapter_function: opening / mystery
- time_span: 半夜
- ending_type: action_cut
- pressure_curve:
  - position_in_flow: opening
  - chapter_internal_motion: 雾夜日常维修 → 灯芯异常 → 巡灯署回收施压 → 私藏动作切断。
- architecture_role:
  - pacing_mode: mystery
  - world_expansion: 外环灯巷的夜间维修秩序和巡灯署现场回收流程进入正文。
  - protagonist_growth_budget: 不获得能力成长，只获得异常线索并承担私藏风险。
  - information_reveal: 只释放旧灯芯有陌生声音、巡灯署正在回收旧灯芯，不解释规则和身份。
  - side_thread_touch:
    - old_wick_voice
  - offscreen_pressure:
    - 巡灯署已在执行旧灯芯回收。
  - recurring_assets:
    - 旧灯芯碎片
    - 巡灯署回收铜盒
  - must_not_resolve:
    - 声音身份
    - 巡灯署真实目的
  - writable_scene_seed: 林栖在雾夜修灯时听见灯芯灰里的声音，巡灯署随后按流程回收旧灯芯，她只能在铜盒合上前藏下一角碎片。
- must_happen:
  - 林栖触碰灯芯灰，听见“别把灯交出去”。
  - 巡灯署领头人回收旧灯芯。
  - 林栖把碎片藏进袖口。
- must_not_complete:
  - 不解释声音身份。
  - 不解释巡灯署真实目的。
- information_release:
  - new_core_variables:
    - info: 旧灯芯异常。
      enters_via: 林栖触碰灯芯灰时听见陌生声音。
      forbidden_entry_modes:
        - 主角脑内总结
        - 旁白式陈述
    - info: 巡灯署回收旧灯芯。
      enters_via: 巡灯署领头人现场到场并收走灯芯。
      forbidden_entry_modes:
        - 旁白式制度解释
  - deferred_information: 碎片划痕含义；声音主人。
- narrative_weave:
  - 人物日常反应: 数螺丝压住紧张。
  - 场景即时质感: 大雾、焦油、湿灯芯、铜罩热度。
  - 关系温度波动: 林栖与巡灯署从日常协作转入隐瞒。

**Writing Execution**

- opening_sensory: 雾、焦油味、铜灯罩的余热先进入，不用设定开场。
- voice_examples:
  - 林栖说话短，紧张时先报工具名或工序名，不直接说害怕。
  - 巡灯署领头人语气客气，但句子里不给选择。
- foreshadowing_weight: 旧灯芯碎片是第一章最重的物件伏笔；写它时要有冷、贴脉搏、不能交出的重量。
- relationship_temperature: 林栖与巡灯署从熟悉的维修协作滑向隐瞒和防备。
- body_scene_texture: 手指沾灰、铜罩余热、袖口贴住脉搏的凉意承担紧张感。
- dialogue_mode: 表面例行问答，实际是机构压力下的试探。
- scene_moments:
  - 林栖数螺丝，试图把异常当成普通故障。
  - 巡灯署的人伸手要灯芯，铜盒盖子压住灯灰。
  - 碎片滑进袖口，贴着脉搏发凉。
- ending_gesture: 碎片在袖口里贴住脉搏，声音被雾压回去。
- sample_style_anchors:
  - 暂无真实样本文风时，以项目 style_memory 为准。
- prose_constraints:
  - 不把设定解释成报告。
  - 让异常通过物件和动作出现。
  - 禁止默认使用"不是X而是Y / 不是X，是Y"。
  - 禁止元叙述和箭头式认知总结。

## Pre-Draft Self Check

- time_span_check: 本章只覆盖一个雾夜，不默认写成一天一章。
- ending_type_check: 结尾停在私藏动作，不写成"她决定下一步"。
- information_entry_check: 两个核心信息都通过现场动作进入。
- architecture_role_check: 本章承担 mystery/opening，不解释规则，只让世界压力进场。
- world_expansion_check: 展示外环灯巷维修秩序和巡灯署回收流程。
- growth_budget_check: 林栖只获得物证线索，不获得能力突破。
- weave_insertion_check: 数螺丝、雾和铜灯罩用于降低任务清单感。
- scene_not_checklist_check: 正文围绕三个可写瞬间展开，不逐条翻译 must_happen。

## Required Updates After Writing

- summary.yml: 记录旧灯芯异常和林栖私藏碎片。
- canon_delta.yml: 记录新事实、角色变化、世界状态变化和 actual_handoff。
- entities: 更新林栖状态。
- ledgers: 更新 world_state、knowledge_state、narrative_debts。
- planning: 更新 active_flow、completed_plan_log、rolling_plan。
- merge_preview: round_001 preview/apply 后无 high-confidence pending。

## Risks And Open Questions

- 声音身份和碎片划痕必须延后，不在 ch001 解释。
