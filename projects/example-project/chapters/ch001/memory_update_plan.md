# Memory Update Plan

## Source

- chapter: ch001
- final_txt: projects/example-project/chapters/ch001/final.txt
- prior_state_files:
  - projects/example-project/planning/active_flow.yml
  - projects/example-project/planning/rolling_plan.yml

## Confidence

status: ready_for_director_merge
reason: 示例项目只展示协议格式；本章 summary.yml 和 canon_delta.yml 已有对应示范。

## Chapter Summary Draft

```yaml
chapter: ch001
title: ""
status: final
one_line_summary: "林栖接触旧灯芯，巡灯署到场索要灯芯。"
detailed_summary: []
characters_present: []
locations: []
key_events: []
emotional_result: ""
external_result: "旧灯芯成为巡灯署可见索要目标。"
actual_handoff:
  - "巡灯署推开灯廊门，领头人索要旧灯芯。"
```

## Canon Delta Draft

```yaml
chapter: ch001
new_facts: []
character_changes: []
relationship_changes: []
world_state_changes: []
knowledge_changes: []
foreshadowing_added: []
foreshadowing_advanced: []
foreshadowing_paid: []
narrative_debts_added: []
narrative_debts_advanced: []
narrative_debts_paid: []
ideas_added: []
actual_handoff:
  - "巡灯署推开灯廊门，领头人索要旧灯芯。"
```

## Entities Update Draft

- file: projects/example-project/entities/characters.yml
- existing_state: 示例项目占位。
- proposed_change: 无新增强制变更。
- evidence: ch001 final.txt 示例正文。
- confidence: medium

## Ledgers Update Draft

- file: projects/example-project/ledgers/narrative_debts.yml
- existing_state: 示例项目占位。
- proposed_change: 保留旧灯芯相关期待债。
- evidence: ch001 final.txt 末尾巡灯署索要旧灯芯。
- confidence: medium

## Planning Update Draft

- active_flow.last_cut.current_handoff: "巡灯署推开灯廊门，领头人索要旧灯芯。"
- rolling_plan changes needed: ch002 应承接巡灯署索要旧灯芯。
- completed_plan_log changes needed: ch001 章纲可在完成后归档。
- evidence: ch001 final.txt 结尾。
- confidence: medium

## Merge Boundary

- this_file_is: draft_only
- director_must_merge: true
- no_direct_file_updates_claimed: true

## Open Questions

- 示例项目不作为真实小说质量样板。

## Must Not Change

- protected files not touched: true
- uncertain items left for director: true
