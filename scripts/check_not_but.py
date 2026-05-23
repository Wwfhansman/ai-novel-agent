#!/usr/bin/env python3
"""Locate overused Chinese "不是X而是Y / 不是X，是Y" prose patterns.

This helper is intentionally read-only. It lists candidate positions so the
writing agent can revise them in one pass before final.txt. It exits non-zero
when a file exceeds the limit, so it can be used as a draft-stage gate.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


# Match contrast constructions, not every "不是":
#   不是……而是……
#   不是……，是…… / 不是……。是……
# Avoid "是不是", "岂不是", and "不是A，也不是B".
NOT_BUT_PATTERN = re.compile(r"(?<![是岂])不是(?:(?!不是).){0,30}(?:而是|[，,。；;\s]+是)")


def _line_col(text: str, index: int) -> tuple[int, int]:
    line = text.count("\n", 0, index) + 1
    last_newline = text.rfind("\n", 0, index)
    col = index + 1 if last_newline < 0 else index - last_newline
    return line, col


def _context(line: str, start_col: int, match_len: int, width: int = 28) -> str:
    start = max(0, start_col - 1 - width)
    end = min(len(line), start_col - 1 + match_len + width)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(line) else ""
    return f"{prefix}{line[start:end]}{suffix}"


def find_candidates(path: Path) -> list[tuple[int, int, str, str]]:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    lines = text.splitlines()
    results: list[tuple[int, int, str, str]] = []

    for match in NOT_BUT_PATTERN.finditer(text):
        line_no, col = _line_col(text, match.start())
        line_text = lines[line_no - 1] if line_no - 1 < len(lines) else ""
        results.append((line_no, col, match.group(0), _context(line_text, col, len(match.group(0)))))
    return results


def resolve_files(args: argparse.Namespace) -> list[Path]:
    target = args.target
    if target.is_file():
        return [target]

    if not target.exists():
        raise SystemExit(f"Target not found: {target}")

    if args.chapters:
        files: list[Path] = []
        for chapter in args.chapters:
            chapter_dir = target / "chapters" / chapter
            for name in args.files:
                path = chapter_dir / name
                if path.exists():
                    files.append(path)
        return files

    if target.name.startswith("ch") and target.is_dir():
        return [target / name for name in args.files if (target / name).exists()]

    raise SystemExit("Pass a TXT file, a chapter directory, or a project path with --chapters.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=Path, help="TXT file, chapter directory, or project path")
    parser.add_argument("--chapters", nargs="*", help="Chapter ids when target is a project path")
    parser.add_argument("--files", nargs="+", default=["final.txt"], help="Files to scan in each chapter")
    parser.add_argument("--limit", type=int, default=1, help="Allowed candidate count per file")
    args = parser.parse_args()

    files = resolve_files(args)
    if not files:
        print("No files to scan.")
        return 0

    total = 0
    over_limit = 0
    for path in files:
        candidates = find_candidates(path)
        total += len(candidates)
        print(f"{path}: {len(candidates)} candidate(s), limit {args.limit}")
        for line_no, col, match_text, context in candidates:
            print(f"  L{line_no}:C{col}: {context}")
            print(f"    match: {match_text}")
        if len(candidates) > args.limit:
            print(f"  needs review: revise or justify {len(candidates) - args.limit} candidate(s)")
            over_limit += 1
        print()

    print(f"Total candidates: {total}")
    if over_limit:
        print(f"Files over limit: {over_limit}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
