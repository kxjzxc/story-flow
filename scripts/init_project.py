#!/usr/bin/env python3
"""Initialize the minimal StoryFlow Markdown project structure."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "project-template"
LOCAL_SKILL_ROOT = Path(".codex") / "skills" / "story-flow"
SKILL_FILES = (
    Path("SKILL.md"),
    Path("agents") / "openai.yaml",
    Path("assets") / "project-template" / "STORYFLOW.md",
    Path("assets") / "project-template" / "graph" / "index.md",
    Path("assets") / "project-template" / "draft" / "index.md",
    Path("assets") / "project-template" / "ideas" / "index.md",
    Path("scripts") / "init_project.py",
    Path("scripts") / "log_conversation.py",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize a StoryFlow project without overwriting existing files."
    )
    parser.add_argument("project", type=Path, help="Project directory to initialize")
    parser.add_argument("--title", help="Story title; defaults to the directory name")
    parser.add_argument(
        "--no-install-skill",
        action="store_true",
        help="Only create Markdown project files; do not install the local StoryFlow skill",
    )
    return parser.parse_args()


def validate_title(title: str) -> str:
    title = title.strip()
    if not title:
        raise ValueError("title must not be empty")
    if "\n" in title or "\r" in title:
        raise ValueError("title must be a single line")
    return title


def render_manifest(title: str) -> str:
    template = (TEMPLATE_ROOT / "STORYFLOW.md").read_text(encoding="utf-8")
    return template.replace("{{TITLE_YAML}}", json.dumps(title, ensure_ascii=False)).replace(
        "{{TITLE_HEADING}}", title
    )


def write_new(path: Path, content: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
    except FileExistsError:
        return False
    return True


def copy_new(source: Path, destination: Path) -> bool:
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with source.open("rb") as source_handle, destination.open("xb") as destination_handle:
            shutil.copyfileobj(source_handle, destination_handle)
    except FileExistsError:
        return False
    shutil.copymode(source, destination)
    return True


def install_local_skill(project: Path) -> tuple[list[Path], list[Path]]:
    created: list[Path] = []
    skipped: list[Path] = []
    for relative in SKILL_FILES:
        source = SKILL_ROOT / relative
        destination = project / LOCAL_SKILL_ROOT / relative
        (created if copy_new(source, destination) else skipped).append(destination)
    return created, skipped


def initialize(
    project: Path, title: str, install_skill: bool
) -> tuple[list[Path], list[Path]]:
    project = project.expanduser().resolve()
    if project.exists() and not project.is_dir():
        raise ValueError(f"project path is not a directory: {project}")

    project.mkdir(parents=True, exist_ok=True)
    conversation_dir = project / "_storyflow" / "conversations"
    conversation_dir.mkdir(parents=True, exist_ok=True)

    sources = {
        project / "STORYFLOW.md": render_manifest(title),
        project / "draft" / "index.md": (
            TEMPLATE_ROOT / "draft" / "index.md"
        ).read_text(encoding="utf-8"),
        project / "ideas" / "index.md": (
            TEMPLATE_ROOT / "ideas" / "index.md"
        ).read_text(encoding="utf-8"),
        project / "graph" / "index.md": (
            TEMPLATE_ROOT / "graph" / "index.md"
        ).read_text(encoding="utf-8"),
    }

    created: list[Path] = []
    skipped: list[Path] = []
    for path, content in sources.items():
        (created if write_new(path, content) else skipped).append(path)
    if install_skill:
        skill_created, skill_skipped = install_local_skill(project)
        created.extend(skill_created)
        skipped.extend(skill_skipped)
    return created, skipped


def main() -> int:
    args = parse_args()
    default_title = args.project.expanduser().resolve().name or "Untitled Story"
    try:
        title = validate_title(args.title or default_title)
        created, skipped = initialize(args.project, title, not args.no_install_skill)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    for path in created:
        print(f"created: {path}")
    for path in skipped:
        print(f"preserved: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
