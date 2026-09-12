from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "init_project.py"


class InitProjectTests(unittest.TestCase):
    def test_initializes_daoverse_project(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "novel"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(project), "--title", "Test Story"],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((project / "STORYFLOW.md").is_file())
            self.assertTrue((project / "ideas" / "index.md").is_file())
            self.assertTrue((project / "draft" / "index.md").is_file())
            self.assertTrue((project / "graph" / "index.md").is_file())
            self.assertFalse((project / "setting").exists())
            self.assertFalse((project / "_storyflow").exists())
            self.assertTrue(
                (
                    project
                    / ".codex"
                    / "skills"
                    / "story-flow"
                    / "SKILL.md"
                ).is_file()
            )
            manifest = (project / "STORYFLOW.md").read_text(encoding="utf-8")
            self.assertIn('title: "Test Story"', manifest)
            self.assertIn("idea_roots:", manifest)
            self.assertIn("graph_index:", manifest)
            self.assertNotIn("conversation_root:", manifest)

    def test_preserves_existing_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "novel"
            ideas = project / "ideas" / "index.md"
            ideas.parent.mkdir(parents=True)
            ideas.write_text("# Existing\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(project)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(ideas.read_text(encoding="utf-8"), "# Existing\n")
            self.assertIn("已保留：", result.stdout)

    def test_can_skip_local_skill_install(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "novel"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(project), "--no-install-skill"],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((project / "STORYFLOW.md").is_file())
            self.assertFalse((project / ".codex" / "skills" / "story-flow").exists())


if __name__ == "__main__":
    unittest.main()
