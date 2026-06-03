"""Turnkey chapter production kit.

Assembles everything needed to produce one chapter with the validated
scene-level method, rendered ready-to-use (no JSON wrangling):

  scene_prompts.md     one ready writer prompt per scene (spec + entering-state
                       summary + retrieved exemplars + constraints)
  stitch_prompt.md     chapter-level stitch/polish instruction
  events.template.yml  events skeleton to fill after writing (stubbed from the
                       chapter's core_advance / information_release / handoff)
  PRODUCE.md           the exact step list: write -> stitch -> save final.txt ->
                       fill events -> check -> commit

This is the operational form of "门槛 B": producing a chapter becomes
`kit -> write scenes -> stitch -> commit`.
"""

from __future__ import annotations

from pathlib import Path

from .scene.packet import build_scene_packets
from .yamlio import load_yaml


def _chapter_block(project: Path, chapter: str) -> dict:
    rolling = load_yaml(project / "planning" / "rolling_plan.yml")
    if isinstance(rolling, dict):
        for block in rolling.get("chapters", []) or []:
            if isinstance(block, dict) and block.get("chapter") == chapter:
                return block
    return {}


def _es_summary(es: dict) -> str:
    lines: list[str] = []
    chars = es.get("characters", {})
    if chars:
        lines.append("在场/相关人物:")
        for cid, c in chars.items():
            bits = [c.get("name", cid)]
            if c.get("current_goal"):
                bits.append(f"目标:{c['current_goal']}")
            if c.get("current_stance"):
                bits.append(f"立场:{c['current_stance']}")
            rels = c.get("relationships") or {}
            if rels:
                bits.append("关系:" + ",".join(f"{k}={v}" for k, v in rels.items()))
            lines.append("  - " + "；".join(bits))
    debts = [d for d in es.get("open_debts", [])]
    if debts:
        lines.append("未偿债务(读者在等):")
        for d in debts:
            flag = " [逾期]" if d.get("overdue") else ""
            lines.append(f"  - {d.get('description')}{flag}")
    fore = es.get("live_foreshadowing", [])
    if fore:
        lines.append("未收伏笔:")
        lines.extend(f"  - {f.get('content')}" for f in fore)
    if es.get("recent_facts"):
        lines.append("近期事实: " + "；".join(es["recent_facts"][-3:]))
    return "\n".join(lines) if lines else "（无已解析状态——可能是开篇）"


def _render_scene_prompt(index: int, packet: dict) -> str:
    s = packet["scene"]
    temp = s.get("emotional_temperature") or {}
    exemplars = packet.get("exemplars") or []
    ex_block = "\n".join(f"> {e}" for e in exemplars) if exemplars else "（无样本，沿用全书既有文风）"
    constraints = "\n".join(f"- {c}" for c in packet.get("prose_constraints", []))
    weave = "、".join(s.get("weave_beats") or []) or "TODO"
    return (
        f"## 场景 {index}：{s.get('id')}\n\n"
        f"- pov：{s.get('pov')}\n"
        f"- 地点/时间：{s.get('location','TODO')} / {s.get('time','')}\n"
        f"- 情绪温度：{temp.get('from','TODO')} → {temp.get('to','TODO')}\n"
        f"- 感官锚（先写够）：{s.get('sensory_anchor','TODO')}\n"
        f"- 织入节拍（不解决任务）：{weave}\n"
        f"- 这一场推进的小事 one_change：{s.get('one_change') or '（无，纯质感场景）'}\n"
        f"- 新信息怎么进 enters_via：{s.get('enters_via','TODO')}\n"
        f"- 出口（外部动作，别切在'任务完成'）：{s.get('exit_on','TODO')}\n\n"
        f"文风范例（模仿语感，别照抄内容）：\n{ex_block}\n\n"
        f"约束：\n{constraints}\n\n"
        f"请写这一场（经历优先，先把感官/情绪/织入写足，推进只是小料）。\n"
    )


def _events_template(project: Path, chapter: str) -> str:
    block = _chapter_block(project, chapter)
    core = block.get("core_advance") or {}
    info = block.get("information_release") or {}
    handoff = block.get("planned_handoff", "")
    stubs: list[str] = []
    for v in (info.get("new_core_variables") or []):
        topic = v.get("info") if isinstance(v, dict) else v
        stubs.append(f"  # 新信息：{topic}\n  # - {{kind: knowledge_changed, topic: TODO_id, holder: TODO, level: hinted}}")
    for m in (core.get("must_happen") or [])[:3]:
        stubs.append(f"  # 必发生：{m}\n  # - {{kind: fact_added, text: TODO}}")
    if handoff:
        stubs.append(f"  # 章末交接：{handoff[:40]}...\n  # - {{kind: note, text: TODO}}")
    stub_block = "\n".join(stubs) if stubs else "  # - {kind: fact_added, text: TODO}"
    return (
        f"# 写完 {chapter} 后填这个（机械变化用类型化事件，叙事性变化用 note）。\n"
        f"# 完整词汇表见 novel_engine/schemas/event.schema.json / docs/ENGINE.md。\n"
        f"chapter: {chapter}\n"
        "events:\n"
        f"{stub_block}\n"
    )


def build_kit(project: Path, chapter: str) -> tuple[dict[str, str], list[str]]:
    project = Path(project)
    packets, notes = build_scene_packets(project, chapter)
    block = _chapter_block(project, chapter)
    title = block.get("title", "")

    es_summary = _es_summary(packets[0]["entering_state"]) if packets else "（无场景）"
    scene_prompts = (
        f"# {chapter} {title} — 逐场写作 prompt（场景级方法）\n\n"
        f"## 进入本章时的状态（引擎解析，别和它矛盾）\n{es_summary}\n\n"
        + "\n".join(_render_scene_prompt(i, p) for i, p in enumerate(packets, start=1))
    )

    stitch = (
        f"# {chapter} 章级缝合\n\n"
        "把上面各场连成一章：\n"
        "- 抹平场景接缝，保证时间/空间/情绪连续。\n"
        "- 全章只有一个核心推进，其余是织入。\n"
        "- 开头不复述设定；结尾留外部动作交接（见章纲 planned_handoff）。\n"
        "- 检查节奏有呼吸，不是匀速平推。\n"
        "- 存成 chapters/" + chapter + "/final.txt（标题行 + 空行 + 正文，段落间不空行）。\n"
    )

    produce = (
        f"# 生产 {chapter} 的步骤\n\n"
        "1. 按 `scene_prompts.md` 逐场写正文。\n"
        "2. 按 `stitch_prompt.md` 缝合成整章，存 `chapters/" + chapter + "/final.txt`。\n"
        "3. 质量自检：\n"
        f"   `python -m novel_engine txt chapters/{chapter}/final.txt`\n"
        f"   `python -m novel_engine patterns chapters/{chapter}/final.txt`\n"
        "4. 按 `events.template.yml` 把本章 canon 变化填进 `events/" + chapter + ".yml`。\n"
        "5. 收尾门禁：`python -m novel_engine check <project>`，"
        "通过后 `python -m novel_engine commit <project>`。\n"
    )

    files = {
        "scene_prompts.md": scene_prompts,
        "stitch_prompt.md": stitch,
        "events.template.yml": _events_template(project, chapter),
        "PRODUCE.md": produce,
    }
    return files, notes


def write_kit(project: Path, chapter: str) -> tuple[Path, list[str], list[str]]:
    project = Path(project)
    out_dir = project / "chapters" / chapter / "_kit"
    out_dir.mkdir(parents=True, exist_ok=True)
    files, notes = build_kit(project, chapter)
    written: list[str] = []
    for name, content in files.items():
        (out_dir / name).write_text(content, encoding="utf-8")
        written.append(name)
    return out_dir, written, notes
