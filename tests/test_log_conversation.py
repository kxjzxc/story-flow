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

    def test_start_and_summarize_replaces_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "story"
            project.mkdir()
            started = self.run_script(
                "start", "--project", str(project), "--title", "World rules"
            )
            self.assertEqual(started.returncode, 0, started.stderr)
            session = Path(started.stdout.strip())

            first = Path(temp_dir) / "first.txt"
            first.write_text("第一版总结。\n", encoding="utf-8")
            second = Path(temp_dir) / "second.txt"
            second.write_text("第二版总结（压缩后）。\n", encoding="utf-8")

            result = self.run_script(
                "summarize", "--session", str(session), "--content-file", str(first)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            result = self.run_script(
                "summarize", "--session", str(session), "--content-file", str(second)
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            archive = session.read_text(encoding="utf-8")
            self.assertIn("kind: session-summary", archive)
            self.assertIn("read_policy: explicit-only", archive)
            self.assertIn("## Summary -", archive)
            self.assertIn("第二版总结（压缩后）。", archive)
            self.assertNotIn("第一版总结。", archive)
            self.assertEqual(archive.count("## Summary -"), 1)

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

    def test_has_no_read_or_append_command(self) -> None:
        for command in ("read", "append"):
            result = self.run_script(command)
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
