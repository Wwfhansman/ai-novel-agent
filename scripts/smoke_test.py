#!/usr/bin/env python3
"""Run a lightweight template/validator smoke test.

This does not call an LLM. It copies the project template into a temporary
directory, fills only the minimum files needed for the current validator
contract, and verifies that the validator can run without crashing. The goal is
to catch template/validator drift during protocol refactors.
"""

from __future__ import annotations

import argparse
import difflib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "project"
VALIDATOR = ROOT / "scripts" / "validate_novel_output.py"
GOLDEN = ROOT / "scripts" / "golden" / "smoke_test.out"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def seed_minimal_chapter(project: Path) -> None:
    chapter = project / "chapters" / "ch001"
    chapter.mkdir(parents=True, exist_ok=True)

    write(
        chapter / "draft.txt",
        "第一章 烟火\n\n他推开门，看见院里灯还亮着。\n有人把一只旧木盒放在石阶上，盒盖半开，里面压着一张湿纸。\n他没有立刻伸手，只先听见墙外脚步停了下来。\n",
    )
    shutil.copyfile(chapter / "draft.txt", chapter / "final.txt")
    write(
        chapter / "reader_pass.md",
        "reader: same_agent_fallback\n"
        "fallback_reason: smoke test\n"
        "最值得保留的一段: 石阶上的旧木盒有外部压力。\n"
        "局部润色建议:\n"
        "- 保留脚步停下作为外部交接。\n"
        "verdict: pass\n",
    )
    write(
        chapter / "memory_update_plan.md",
        "# Memory Update Plan\n\n"
        "status: ready_for_director_merge\n"
        "evidence: final.txt contains the handoff.\n\n"
        "## Coverage Gaps\n\nnone\n\n"
        "## State Update Candidates\n\nnone\n\n"
        "## Planning Update Candidates\n\nnone\n\n"
        "## Manual Review\n\nnone\n\n"
        "## Merge Boundary\n\nsmoke test only\n",
    )
    write(
        chapter / "summary.yml",
        "chapter: ch001\nstatus: final\nactual_handoff: 墙外脚步停下。\n",
    )
    write(
        chapter / "canon_delta.yml",
        "chapter: ch001\nactual_handoff: 墙外脚步停下。\nstate_sync: []\n",
    )
    write(
        chapter / "review.md",
        "# Review\n\n"
        "## Reader Reward Check\n\npass\n\n"
        "## TXT Format Check\n\npass\n\n"
        "## Memory Update Check\n\npass\n\n"
        "## Post-Merge QA\n\nvalidator: pass\n",
    )
    write(
        project / "planning" / "active_flow.yml",
        "current_flow:\n"
        "  id: smoke_flow\n"
        "  status: active\n"
        "  last_cut:\n"
        "    chapter: ch001\n"
        "    current_handoff: 墙外脚步停下。\n"
        "completed_flows: []\n",
    )
    write(
        project / "planning" / "rolling_plan.yml",
        "current_window: ch002-ch002\n"
        "status: active\n"
        "source_of_truth: smoke test\n"
        "chapters:\n"
        "- chapter: ch002\n"
        "  status: planned\n"
        "  macro_stage: smoke\n"
        "  scale_level: room\n"
        "  cross_chapter_event: smoke handoff\n"
        "  starts_mid_action: true\n"
        "  ends_mid_action: true\n"
        "  chapter_function: investigation\n"
        "  pressure_curve:\n"
        "    position_in_flow: opening\n"
        "  reader_question_flow: {}\n"
        "  core_advance: {}\n"
        "  information_release: {}\n"
        "  chapter_turn: smoke turn\n"
        "  side_yield: []\n"
        "  planned_handoff: smoke handoff\n"
        "  叙事织入: {}\n"
        "  background_dependencies: {}\n",
    )
    write(
        project / "planning" / "merge_previews" / "round_001.yml",
        "project: smoke-project\n"
        "round: round_001\n"
        "chapters:\n"
        "- ch001\n"
        "operations: []\n"
        "manual_review: []\n"
        "apply_log: []\n",
    )


def run_smoke() -> tuple[int, str]:
    if not TEMPLATE.exists():
        return 2, f"Missing template: {TEMPLATE}\n"

    with tempfile.TemporaryDirectory(prefix="ai-novel-smoke-") as tmp:
        project = Path(tmp) / "smoke-project"
        shutil.copytree(TEMPLATE, project)
        seed_minimal_chapter(project)

        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(project), "--chapters", "ch001"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        return result.returncode, result.stdout


def normalize_output(text: str) -> str:
    # Validator output includes temporary paths when warnings/errors fire. The
    # smoke fixture is expected to pass cleanly, but normalize defensively so a
    # future warning remains reviewable instead of machine-specific.
    text = text.replace(str(ROOT), "<repo>")
    text = re_sub_temp_paths(text)
    return text


def re_sub_temp_paths(text: str) -> str:
    import re

    return re.sub(r"/(?:private/)?var/folders/[^\s:]+/ai-novel-smoke-[^/\s:]+", "<tmp>", text)


def compare_golden(actual: str) -> tuple[bool, str]:
    if not GOLDEN.exists():
        return False, f"Missing golden file: {GOLDEN}. Run scripts/smoke_test.py --update-golden.\n"
    expected = GOLDEN.read_text(encoding="utf-8")
    if actual == expected:
        return True, ""
    diff = "".join(
        difflib.unified_diff(
            expected.splitlines(keepends=True),
            actual.splitlines(keepends=True),
            fromfile=str(GOLDEN),
            tofile="actual",
        )
    )
    return False, diff


def main() -> int:
    parser = argparse.ArgumentParser(description="Run template/validator smoke test with golden output.")
    parser.add_argument("--update-golden", action="store_true", help="Rewrite scripts/golden/smoke_test.out with current output")
    args = parser.parse_args()

    code, output = run_smoke()
    normalized = normalize_output(output)

    if args.update_golden:
        GOLDEN.parent.mkdir(parents=True, exist_ok=True)
        GOLDEN.write_text(normalized, encoding="utf-8")
        print(f"Updated {GOLDEN}")
        print(normalized, end="")
        return code

    print(normalized, end="")
    if code != 0:
        return code

    ok, diff = compare_golden(normalized)
    if ok:
        return 0
    print("\nGOLDEN_MISMATCH: smoke test output changed.", file=sys.stderr)
    print(diff, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
