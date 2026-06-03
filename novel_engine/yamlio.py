"""YAML load/dump with a PyYAML-or-ruby fallback.

Mirrors the no-hard-dependency convention already used in
scripts/round_state_merge.py so the engine runs on the same machines the legacy
tooling does.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


def _yaml_module():
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        return None
    return yaml


def _load_with_ruby(path: Path) -> Any:
    ruby = shutil.which("ruby")
    if not ruby:
        raise RuntimeError(
            "Neither PyYAML nor ruby is available; cannot parse YAML. "
            "Install PyYAML (pip install pyyaml) or ruby."
        )
    code = "require 'yaml'; require 'json'; puts JSON.generate(YAML.load_file(ARGV[0]))"
    result = subprocess.run([ruby, "-e", code, str(path)], text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout).strip())
    return json.loads(result.stdout) if result.stdout.strip() else None


def load_yaml(path: Path) -> Any:
    """Load a YAML file. Returns None for a missing/empty file."""
    path = Path(path)
    if not path.exists():
        return None
    yaml = _yaml_module()
    if yaml is None:
        return _load_with_ruby(path)
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def dump_yaml(path: Path, data: Any) -> None:
    path = Path(path)
    yaml = _yaml_module()
    path.parent.mkdir(parents=True, exist_ok=True)
    if yaml is None:
        ruby = shutil.which("ruby")
        if not ruby:
            raise RuntimeError("Neither PyYAML nor ruby is available; cannot write YAML.")
        code = "require 'json'; require 'yaml'; puts YAML.dump(JSON.parse(STDIN.read))"
        result = subprocess.run(
            [ruby, "-e", code],
            input=json.dumps(data, ensure_ascii=False),
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError((result.stderr or result.stdout).strip())
        path.write_text(result.stdout, encoding="utf-8")
        return
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )
