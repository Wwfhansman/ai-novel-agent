# Memory Update Plan

## Source

- chapter: ch001
- final_txt: projects/example-project/chapters/ch001/final.txt
- summary: projects/example-project/chapters/ch001/summary.yml
- canon_delta: projects/example-project/chapters/ch001/canon_delta.yml
- status: ready_for_director_merge

## Coverage Gaps

- none

## State Update Candidates

- target: entities/characters.yml
  operation: append_change_history
  value: 林栖从普通修灯人变成私下藏匿线索的人。
  evidence: ch001 final.txt 中林栖把碎片滑进袖口。
  confidence: high

## Planning Update Candidates

- target: planning/active_flow.yml
  operation: update_active_flow_cut
  value: 林栖袖口里藏着碎片，巡灯署是否察觉缺失。
  evidence: ch001 canon_delta actual_handoff。
  confidence: high

## Manual Review

- target: none
  reason: 示例项目无待审项。
  evidence: none

## Merge Boundary

- this_file_is: draft_only
- director_must_merge: true
- no_direct_file_updates_claimed: true
