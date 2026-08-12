#!/usr/bin/env python3
"""Create and update StoryFlow session summaries; a session file keeps only a rolling summary."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import unicodedata
from datetime import datetime
from pathlib import Path


DEFAULT_CONVERSATION_ROOT = Path("_storyflow/conversations")


def now() -> datetime:
    return datetime.now().astimezone()


def validate_single_line(value: str, field: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError(f"{field} must not be empty")
    if "\n" in value or "\r" in value:
        raise ValueError(f"{field} must be a single line")
    return value


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower()
    return slug[:48] or "conversation"


def safe_conversation_dir(project: Path, relative: Path) -> Path:
    project = project.expanduser().resolve()
    if relative.is_absolute():
        raise ValueError("conversation root must be relative to the project")
    directory = (project / relative).resolve()
    if not directory.is_relative_to(project):
        raise ValueError("conversation root must stay inside the project")
    return directory


def start_session(
    project: Path, conversation_root: Path, title: str, session_id: str | None
) -> Path:
    directory = safe_conversation_dir(project, conversation_root)
    directory.mkdir(parents=True, exist_ok=True)
    title = validate_single_line(title, "title")
    timestamp = now()
    identifier = (
        slugify(session_id) if session_id else f"conversation-{timestamp:%Y%m%d-%H%M%S}"
    )
    base_name = f"{timestamp:%Y%m%d-%H%M%S}-{slugify(title)}"
    path = directory / f"{base_name}.md"
    suffix = 2
    while path.exists():
        path = directory / f"{base_name}-{suffix}.md"
        suffix += 1

    document = (
        "---\n"
        "storyflow:\n"
        "  kind: session-summary\n"
        f"  id: {json.dumps(identifier)}\n"
        f"  created_at: {json.dumps(timestamp.isoformat(timespec='seconds'))}\n"
        "  read_policy: explicit-only\n"
        "---\n\n"
        f"# {title}\n"
    )
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(document)
    return path


def read_input(path: str) -> str:
    if path == "-":
        content = sys.stdin.read()
    else:
        content = Path(path).expanduser().read_text(encoding="utf-8")
    if not content.strip():
        raise ValueError("content must not be empty")
    return content.rstrip("\n")


def validate_session(path: Path) -> Path:
    raw_path = path.expanduser()
    if raw_path.is_symlink():
        raise ValueError("session path must not be a symbolic link")
    path = raw_path.resolve()
    if path.suffix.lower() != ".md" or not path.is_file():
        raise ValueError(f"session is not an existing Markdown file: {path}")
    return path


def replace_summary(path: Path, content: str) -> None:
    """Replace the session body after the title with a fresh summary block."""
    path = validate_session(path)
    timestamp = now().isoformat(timespec="seconds")
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    header_end = None
    for index, line in enumerate(lines):
        if line.startswith("# "):
            header_end = index + 1
            break
    if header_end is None:
        raise ValueError("session file has no title heading")
    header = "\n".join(lines[:header_end]).rstrip() + "\n"
    document = header + f"\n## Summary - {timestamp}\n\n{content.rstrip()}\n"

    descriptor, temporary = tempfile.mkstemp(
        prefix=".session-", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(document)
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write StoryFlow session summaries; sessions keep only a rolling summary."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start", help="Create a session summary file")
    start.add_argument("--project", type=Path, required=True)
    start.add_argument(
        "--conversation-root", type=Path, default=DEFAULT_CONVERSATION_ROOT
    )
    start.add_argument("--title", required=True)
    start.add_argument("--session-id")

    summarize = subparsers.add_parser(
        "summarize", help="Replace the session summary (re-summarize the previous one)"
    )
    summarize.add_argument("--session", type=Path, required=True)
    summarize.add_argument(
        "--content-file", required=True, help="UTF-8 file or - for stdin"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "start":
            path = start_session(
                args.project, args.conversation_root, args.title, args.session_id
            )
            print(path)
        elif args.command == "summarize":
            replace_summary(args.session, read_input(args.content_file))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
