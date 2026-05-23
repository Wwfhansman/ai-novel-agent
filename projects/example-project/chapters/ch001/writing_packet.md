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

## Writing Card

- one_line_goal: 林栖修理三号灯时听见旧灯芯里的陌生声音，并私藏碎片。
- chapter_function: opening / mystery
- pressure_curve: 雾夜日常维修 → 灯芯异常 → 巡灯署回收施压 → 她藏下碎片。
- must_happen:
  - 林栖触碰灯芯灰，听见“别把灯交出去”。
  - 巡灯署领头人回收旧灯芯。
  - 林栖把碎片藏进袖口。
- must_not_complete:
  - 不解释声音身份。
  - 不解释巡灯署真实目的。
- information_release:
  - new_core_variables: 旧灯芯异常；巡灯署回收。
  - deferred_information: 碎片划痕含义；声音主人。
- narrative_weave:
  - 人物日常反应: 数螺丝压住紧张。
  - 场景即时质感: 大雾、焦油、湿灯芯、铜罩热度。
  - 关系温度波动: 林栖与巡灯署从日常协作转入隐瞒。
- sample_style_anchors:
  - 暂无真实样本文风时，以项目 style_memory 为准。
- prose_constraints:
  - 不把设定解释成报告。
  - 让异常通过物件和动作出现。

## Required Updates After Writing

- summary.yml: 记录旧灯芯异常和林栖私藏碎片。
- canon_delta.yml: 记录新事实、角色变化、世界状态变化和 actual_handoff。
- entities: 更新林栖状态。
- ledgers: 更新 world_state、knowledge_state、narrative_debts。
- planning: 更新 active_flow、completed_plan_log、rolling_plan。
- merge_preview: round_001 preview/apply 后无 high-confidence pending。

## Risks And Open Questions

- 声音身份和碎片划痕必须延后，不在 ch001 解释。
