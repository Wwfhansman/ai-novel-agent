"""Assemble an A/B writing experiment for one chapter.

Produces an executable package that lets you fairly compare the OLD chapter-level
writing method against the NEW scene-level method on the SAME story beat, then
judge the result with the quality tools + a blind read.

It generates everything deterministic; what it cannot do — generate the prose
(LLM) and judge which reads better (human) — is exactly what the package hands
back to you.

Files written to <project>/experiments/<chapter>/:
  entering_state.json        engine-resolved state the writer enters with
  scene_plan.template.yml    scene-spec worksheet to fill (method B)
  prompt_A_chapter_level.md   old method prompt (one big chapter goal)
  prompt_B_scene_level.md     new method prompt (entering_state + scene specs)
  evaluate.md                 quality commands + blind-read rubric
  README.md                   how to run the experiment
"""

from __future__ import annotations

import json
from pathlib import Path

from .context import entering_state
from .events import load_project_events
from .legacy import adapt_project
from .yamlio import load_yaml


def _chapter_block(project: Path, chapter: str) -> dict:
    rolling = load_yaml(project / "planning" / "rolling_plan.yml")
    if isinstance(rolling, dict):
        for block in rolling.get("chapters", []) or []:
            if isinstance(block, dict) and block.get("chapter") == chapter:
                return block
    return {}


def _events_for(project: Path):
    events, _ = load_project_events(project)
    if events:
        return events
    legacy_events, _ = adapt_project(project)
    return legacy_events


def _protagonist(es: dict) -> str:
    for cid, char in es.get("characters", {}).items():
        if (char.get("role") or "").lower() == "protagonist":
            return char.get("name") or cid
    return "主角"


def _scene_plan_template(chapter: str, pov: str) -> str:
    one = (
        "  - id: {ch}_s{n}\n"
        "    pov: {pov}\n"
        "    location: TODO\n"
        "    emotional_temperature: {{from: TODO, to: TODO}}   # 情绪起点→落点（必填）\n"
        "    sensory_anchor: TODO                              # 这个地方独有的具体感官锚（必填）\n"
        "    weave_beats: [TODO, TODO]                         # 不解决任务的织入节拍\n"
        "    one_change: \"\"                                  # 这一场推进的那件小事；纯质感场景留空\n"
        "    enters_via: TODO                                  # 新信息怎么进来；禁止主角脑内总结\n"
        "    exit_on: TODO                                     # 切在外部动作/到场/代价，不切在'任务完成'\n"
    )
    body = "".join(one.format(ch=chapter, n=i, pov=pov) for i in (1, 2, 3))
    return (
        f"# Method B scene worksheet for {chapter}.\n"
        "# Fill the TODOs. Keep experiential fields rich; keep one_change small (sometimes empty).\n"
        "# This is the anti-task-feeling contract: a scene is an experience unit, not a task unit.\n"
        f"chapter: {chapter}\n"
        "scenes:\n"
        f"{body}"
    )


def build_experiment(project: Path, chapter: str) -> dict[str, str]:
    project = Path(project)
    es = entering_state(_events_for(project), chapter)
    block = _chapter_block(project, chapter)
    pov = _protagonist(es)

    title = block.get("title", "")
    synopsis = (block.get("synopsis") or "").strip()
    core = block.get("core_advance") or {}
    one_sentence = core.get("one_sentence", "")
    must_happen = core.get("must_happen") or []
    must_not = core.get("must_not_complete") or []
    handoff = block.get("planned_handoff", "")
    es_json = json.dumps(es, ensure_ascii=False, indent=2)

    must_block = "\n".join(f"  - {m}" for m in must_happen) or "  - （见 synopsis）"
    mustnot_block = "\n".join(f"  - {m}" for m in must_not) or "  - （无）"

    prompt_a = (
        f"# 写作任务（方法 A：章级，旧法）\n\n"
        f"写《{chapter} {title}》，约 2000-3000 字中文网文正文。\n\n"
        f"## 本章目标\n{one_sentence or synopsis}\n\n"
        f"## 必须发生\n{must_block}\n\n"
        f"## 必须不完成（留到后续）\n{mustnot_block}\n\n"
        f"## 章末交接\n{handoff}\n\n"
        f"## 梗概\n{synopsis}\n\n"
        "直接写正文。开头不要复述设定，结尾留外部动作交接。\n"
    )

    prompt_b = (
        f"# 写作任务（方法 B：场景级，新法）\n\n"
        f"写《{chapter} {title}》，拆成下面 scene_plan 里的 3 个场景，逐场写，最后缝合成一章。\n\n"
        "## 原则（关键）\n"
        "- 场景是经历单位，不是任务单位：先把 pov / 情绪温度 / 感官锚 / 织入节拍写足，剧情推进只是一味小料。\n"
        "- 允许零推进场景（one_change 为空）。\n"
        "- 出口切在外部动作，不切在'任务完成'。\n"
        "- 新信息按 enters_via 进入，禁止主角脑内总结。\n\n"
        "## 进入本章时的状态（引擎解析，不要和它矛盾）\n"
        f"```json\n{es_json}\n```\n\n"
        "## 场景规格（见同目录 scene_plan.template.yml，先填 TODO 再写）\n"
        "按填好的 scene_plan 逐场写，然后做一遍章级缝合，抹平场景接缝。\n\n"
        f"## 本章必须发生 / 章末交接（与方法 A 相同，保证公平对比）\n{must_block}\n章末交接：{handoff}\n"
    )

    evaluate = (
        f"# 评估 {chapter} 的 A/B\n\n"
        "把方法 A 的输出存为 `out_A.txt`，方法 B 的输出存为 `out_B.txt`（放在本目录）。\n\n"
        "## 1. 量化（引擎，客观）\n"
        "```bash\n"
        "python -m novel_engine patterns out_A.txt && python -m novel_engine patterns out_B.txt   # AI 腔\n"
        "python -m novel_engine txt out_A.txt && python -m novel_engine txt out_B.txt             # 格式/段落密度\n"
        "python -m novel_engine fingerprint out_A.txt; python -m novel_engine fingerprint out_B.txt\n"
        "python -m novel_engine compare out_A.txt out_B.txt    # 两版差多少\n"
        "```\n\n"
        "## 2. 盲读（人，主观——这一步只有你能做）\n"
        "随机打乱 A/B 顺序，不看标签读，逐项判断哪版更好：\n"
        "- [ ] 任务感更弱（不像在执行清单）？\n"
        "- [ ] 有'居住感'/体温（人物日常、场景质感、关系温度）？\n"
        "- [ ] 节奏有呼吸（不是匀速平推）？\n"
        "- [ ] 信息是被经历到的，不是被解释的？\n"
        "- [ ] 结尾留下外部动作而非反思？\n"
        "- [ ] 你更想读下一章？\n\n"
        "结论：A / B / 无差别。若 B 不优于 A，说明 scene 规格滑成了任务清单，方向要收。\n"
    )

    readme = (
        f"# {chapter} A/B 写作实验\n\n"
        "回答唯一真问题：场景级写法是否比章级写法更好看。\n\n"
        "## 步骤\n"
        "1. 把 `prompt_A_chapter_level.md` 交给写作模型 → 存 `out_A.txt`。\n"
        "2. 填好 `scene_plan.template.yml` 的 TODO，连同 `prompt_B_scene_level.md` 交给写作模型 → 存 `out_B.txt`。\n"
        "3. 按 `evaluate.md` 跑量化命令 + 做盲读。\n\n"
        "A、B 用的是同一章目标和章末交接，唯一变量是写作方法，确保对比公平。\n"
        "`entering_state.json` 是引擎解析出的进入状态，两种方法都不应与它矛盾。\n"
    )

    return {
        "entering_state.json": es_json + "\n",
        "scene_plan.template.yml": _scene_plan_template(chapter, pov),
        "prompt_A_chapter_level.md": prompt_a,
        "prompt_B_scene_level.md": prompt_b,
        "evaluate.md": evaluate,
        "README.md": readme,
    }


def write_experiment(project: Path, chapter: str) -> tuple[Path, list[str]]:
    project = Path(project)
    out_dir = project / "experiments" / chapter
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for name, content in build_experiment(project, chapter).items():
        (out_dir / name).write_text(content, encoding="utf-8")
        written.append(name)
    return out_dir, written
