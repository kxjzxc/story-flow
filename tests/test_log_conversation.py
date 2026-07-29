from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "log_conversation.py"


class ConversationLogTests(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_start_append_and_summarize(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "story"
            project.mkdir()
            started = self.run_script(
                "start", "--project", str(project), "--title", "World rules"
            )
            self.assertEqual(started.returncode, 0, started.stderr)
            session = Path(started.stdout.strip())

            user_text = Path(temp_dir) / "user.txt"
            user_text.write_text("Does the rule still apply?\n", encoding="utf-8")
            assistant_text = Path(temp_dir) / "assistant.txt"
            assistant_text.write_text("Yes, according to the setting.\n", encoding="utf-8")
            summary_text = Path(temp_dir) / "summary.txt"
            summary_text.write_text("The rule remains active.\n", encoding="utf-8")

            for command in (
                ("append", "--role", "user", "--content-file", str(user_text)),
                (
                    "append",
                    "--role",
                    "assistant",
                    "--content-file",
                    str(assistant_text),
                ),
                ("summarize", "--content-file", str(summary_text)),
            ):
                result = self.run_script(*command, "--session", str(session))
                self.assertEqual(result.returncode, 0, result.stderr)

            archive = session.read_text(encoding="utf-8")
            self.assertIn("read_policy: explicit-only", archive)
            self.assertIn("## User -", archive)
            self.assertIn("Does the rule still apply?", archive)
            self.assertIn("## Assistant -", archive)
            self.assertIn("Yes, according to the setting.", archive)
            self.assertIn("## Summary -", archive)
            self.assertIn("The rule remains active.", archive)

    def test_rejects_conversation_root_outside_project(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "story"
            project.mkdir()
            result = self.run_script(
                "start",
                "--project",
                str(project),
                "--conversation-root",
                "../outside",
                "--title",
                "Unsafe",
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("must stay inside", result.stderr)

    def test_has_no_read_command(self) -> None:
        result = self.run_script("read")
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
