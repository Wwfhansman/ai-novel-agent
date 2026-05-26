"""Protected-file visibility checks."""

from __future__ import annotations

import re
from pathlib import Path


PROTECTED_FILES = [
    "book/constitution.md",
    "book/longform_blueprint.yml",
    "book/reader_model.yml",
    "book/style_memory.md",
    "book/endgame_hypotheses.yml",
]


def validate_protected_files(project: Path) -> tuple[list[str], list[str]]:
    """Best-effort visibility check for protected-file change logging."""
    errors: list[str] = []
    warnings: list[str] = []
    protected_present = [path for path in PROTECTED_FILES if (project / path).exists()]
    if not protected_present:
        return errors, warnings

    decision_log = project / "ledgers" / "decision_log.yml"
    session_log = project / "meta" / "session_log.md"
    if not decision_log.exists() and not session_log.exists():
        warnings.append(
            f"NO_CHANGE_LOG: Protected files exist ({', '.join(protected_present)}) but neither "
            f"{decision_log} nor {session_log} exists. Protected-file changes must go through "
            "novel-change and record a Change Summary."
        )
        return errors, warnings

    log_text = ""
    for path in (decision_log, session_log):
        if path.exists():
            log_text += "\n" + path.read_text(encoding="utf-8", errors="ignore")
    if not re.search(r"(Change Summary|novel-change|受保护|protected|change:)", log_text, re.IGNORECASE):
        warnings.append(
            "PROTECTED_CHANGE_LOG_WEAK: A decision/session log exists, but it does not mention "
            "Change Summary / novel-change / protected-file handling. This is advisory; verify "
            "any protected-file edits were explicitly approved."
        )
    return errors, warnings
