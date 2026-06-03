"""Documentation contract test (anti-drift governance).

Guards against the agents.md-style drift the original project suffered: every
CLI subcommand must be documented in docs/ENGINE.md, and the docs must not list
commands that no longer exist. Drift fails CI instead of rotting silently.
"""

import re
import unittest
from pathlib import Path

from novel_engine.cli import subcommand_names

REPO = Path(__file__).resolve().parents[2]
ENGINE_MD = REPO / "docs" / "ENGINE.md"


class DocsContractTest(unittest.TestCase):
    def setUp(self):
        self.commands = set(subcommand_names())
        self.doc_text = ENGINE_MD.read_text(encoding="utf-8")

    def test_every_command_is_documented(self):
        missing = [c for c in self.commands if f"novel_engine {c}" not in self.doc_text]
        self.assertEqual(missing, [], f"Commands missing from docs/ENGINE.md: {missing}")

    def test_docs_list_no_phantom_commands(self):
        documented = set(re.findall(r"novel_engine\s+([a-z][a-z_-]*)", self.doc_text))
        phantom = [c for c in documented if c not in self.commands]
        self.assertEqual(phantom, [], f"docs/ENGINE.md references unknown commands: {phantom}")


if __name__ == "__main__":
    unittest.main()
