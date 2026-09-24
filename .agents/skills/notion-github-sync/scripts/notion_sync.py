#!/usr/bin/env python3
"""Deterministic helpers for publishing Notion notes as GitHub Markdown."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


TEMPORARY_IMAGE_HOSTS = (
    "prod-files-secure.s3.",
    "secure.notion-static.com",
)
NOTION_BLOCK_TAGS = (
    "table",
    "tr",
    "td",
    "th",
    "details",
    "summary",
    "callout",
    "table_of_contents",
    "empty-block",
)
README_START_MARKER = "<!-- NOTES_INDEX:START -->"
README_END_MARKER = "<!-- NOTES_INDEX:END -->"
SHELL_COMMAND_RE = re.compile(
    r"^(?:git|ssh|scp|rsync|conda|python|pip|tmux|screen|cd|ls|pwd|"
    r"mkdir|rm|cp|mv|chmod|chown|ps|kill|top|df|du|nvidia-smi|sudo)\b",
    re.MULTILINE,
)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    line: int | None = None


def _plain_inline(value: str) -> str:
    value = re.sub(r"<br\s*/?>", "<br>", value, flags=re.IGNORECASE)
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value)
    value = re.sub(r"\s*\n\s*", "<br>", value.strip())
    return value.replace("|", "\\|")


def _convert_tables(text: str) -> str:
    table_re = re.compile(r"<table(?P<attrs>[^>]*)>(?P<body>.*?)</table>", re.DOTALL)
    row_re = re.compile(r"<tr[^>]*>(.*?)</tr>", re.DOTALL)
    cell_re = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.DOTALL)

    def replace_table(match: re.Match[str]) -> str:
        rows = []
        for row_html in row_re.findall(match.group("body")):
            cells = [_plain_inline(cell) for cell in cell_re.findall(row_html)]
            if cells:
                rows.append(cells)
        if not rows:
            return ""
        width = max(len(row) for row in rows)
        rows = [row + [""] * (width - len(row)) for row in rows]
        rendered = [
            "| " + " | ".join(rows[0]) + " |",
            "| " + " | ".join(["---"] * width) + " |",
        ]
        rendered.extend("| " + " | ".join(row) + " |" for row in rows[1:])
        return "\n" + "\n".join(rendered) + "\n"

    return table_re.sub(replace_table, text)


def _quote_lines(title: str | None, body: str, icon: str | None = None) -> str:
    output = []
    heading = " ".join(part for part in (icon, title) if part)
    if heading:
        output.append(f"> **{heading}**" if title else f"> {heading}")
    body_lines = body.strip().splitlines()
    if heading and body_lines:
        output.append(">")
    for line in body_lines:
        output.append(">" if not line.strip() else f"> {line.strip()}")
    return "\n".join(output)


def _convert_details(text: str) -> str:
    details_re = re.compile(r"<details[^>]*>(.*?)</details>", re.DOTALL)
    summary_re = re.compile(r"<summary[^>]*>(.*?)</summary>", re.DOTALL)

    def replace_details(match: re.Match[str]) -> str:
        block = match.group(1)
        summary_match = summary_re.search(block)
        title = _plain_inline(summary_match.group(1)) if summary_match else "补充内容"
        body = summary_re.sub("", block, count=1)
        return "\n" + _quote_lines(title, body) + "\n"

    return details_re.sub(replace_details, text)


def _convert_callouts(text: str) -> str:
    callout_re = re.compile(r"<callout(?P<attrs>[^>]*)>(?P<body>.*?)</callout>", re.DOTALL)

    def replace_callout(match: re.Match[str]) -> str:
        icon_match = re.search(r'icon="([^"]+)"', match.group("attrs"))
        icon = html.unescape(icon_match.group(1)) if icon_match else None
        body = match.group("body").strip()
        if "\n" not in body:
            prefix = f"{icon} " if icon else ""
            return f"\n> {prefix}{body}\n"
        return "\n" + _quote_lines(None, body, icon=icon) + "\n"

    return callout_re.sub(replace_callout, text)


def _normalize_fences(lines: list[str]) -> list[str]:
    output: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if (
            line.strip().lower() in {"bash", "sh", "shell", "text", "lua", "csharp", "css", "sql"}
            and index + 1 < len(lines)
            and lines[index + 1].lstrip().startswith("```")
        ):
            index += 1
            line = lines[index]
        if line.lstrip().startswith("```") and line.strip() != "```":
            language = line.strip()[3:].strip().lower()
            closing = index + 1
            while closing < len(lines) and lines[closing].strip() != "```":
                closing += 1
            code = "\n".join(lines[index + 1 : closing])
            if language in {"lua", "csharp", "css", "sql", "text"} and SHELL_COMMAND_RE.search(code):
                line = "```bash"
        output.append(line)
        index += 1
    return output


def _space_blocks(lines: list[str]) -> list[str]:
    output: list[str] = []
    in_fence = False
    previous_kind = "blank"

    def add_blank() -> None:
        if output and output[-1] != "":
            output.append("")

    for raw_line in lines:
        line = raw_line.rstrip()
        if line.endswith("\\"):
            line = line[:-1].rstrip() + "  "

        if line.lstrip().startswith("```"):
            if not in_fence:
                add_blank()
                output.append(line.strip())
                in_fence = True
            else:
                output.append("```")
                in_fence = False
                output.append("")
            previous_kind = "fence"
            continue

        if in_fence:
            output.append(raw_line.rstrip("\r\n"))
            continue

        stripped = line.strip()
        if not stripped:
            add_blank()
            previous_kind = "blank"
            continue

        if re.match(r"^#{1,6}\s+", stripped):
            add_blank()
            output.append(stripped)
            output.append("")
            previous_kind = "heading"
            continue

        kind = "paragraph"
        if stripped.startswith("|"):
            kind = "table"
        elif stripped.startswith(">"):
            kind = "quote"
        elif re.match(r"^(?:[-*+] |\d+\. )", stripped):
            kind = "list"
        elif re.match(r"^!\[[^]]*\]\([^)]+\)$", stripped):
            kind = "image"

        if kind in {"table", "quote", "list", "image"} and previous_kind not in {
            kind,
            "blank",
        }:
            add_blank()
        if kind == "paragraph" and previous_kind in {
            "table",
            "quote",
            "list",
            "image",
        }:
            add_blank()

        output.append(stripped if kind != "paragraph" else line)
        if kind == "image":
            output.append("")
        previous_kind = kind

    while output and output[-1] == "":
        output.pop()
    collapsed: list[str] = []
    for line in output:
        if line == "" and collapsed and collapsed[-1] == "":
            continue
        collapsed.append(line)
    return collapsed


def normalize_markdown(text: str, title: str | None = None) -> str:
    """Convert the supported Notion Markdown subset to stable GitHub Markdown."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")
    normalized = re.sub(r"<table_of_contents\b[^>]*/>", "", normalized)
    normalized = re.sub(r"<empty-block\b[^>]*/>", "", normalized)
    normalized = _convert_tables(normalized)
    normalized = _convert_details(normalized)
    normalized = _convert_callouts(normalized)
    normalized = html.unescape(normalized)
    lines = _normalize_fences(normalized.splitlines())
    spaced = _space_blocks(lines)
    result = "\n".join(spaced).strip() + "\n"
    if title:
        expected = f"# {title}"
        first = next((line for line in result.splitlines() if line.strip()), "")
        if first != expected:
            result = expected + "\n\n" + result
    return result


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def validate_markdown(
    text: str,
    *,
    document_path: Path | None = None,
    repo_root: Path | None = None,
) -> list[ValidationIssue]:
    """Return publication-blocking Markdown issues."""
    issues: list[ValidationIssue] = []
    fence_lines = [
        number
        for number, line in enumerate(text.splitlines(), start=1)
        if line.lstrip().startswith("```")
    ]
    if len(fence_lines) % 2:
        issues.append(
            ValidationIssue(
                "unbalanced-fence",
                "Code fences are not balanced.",
                fence_lines[-1] if fence_lines else None,
            )
        )

    for host in TEMPORARY_IMAGE_HOSTS:
        match = re.search(re.escape(host), text)
        if match:
            issues.append(
                ValidationIssue(
                    "temporary-image-url",
                    "A temporary Notion image URL must be downloaded into the repository.",
                    _line_number(text, match.start()),
                )
            )

    tag_pattern = r"</?(?:" + "|".join(map(re.escape, NOTION_BLOCK_TAGS)) + r")\b"
    tag_match = re.search(tag_pattern, text, flags=re.IGNORECASE)
    if tag_match:
        issues.append(
            ValidationIssue(
                "notion-tag",
                "Unsupported Notion block markup remains.",
                _line_number(text, tag_match.start()),
            )
        )

    lines = text.splitlines()
    in_fence = False
    for index, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if re.match(r"^#{1,6}\s+", line):
            if index > 0 and lines[index - 1] != "":
                issues.append(
                    ValidationIssue(
                        "heading-spacing",
                        "Heading must have a blank line before it.",
                        index + 1,
                    )
                )
            if index + 1 < len(lines) and lines[index + 1] != "":
                issues.append(
                    ValidationIssue(
                        "heading-spacing",
                        "Heading must have a blank line after it.",
                        index + 1,
                    )
                )

    if text and not text.endswith("\n"):
        issues.append(
            ValidationIssue(
                "missing-final-newline",
                "Markdown file must end with a newline.",
            )
        )

    if document_path is not None and repo_root is not None:
        root = repo_root.resolve()
        for match in re.finditer(r"!\[[^]]*\]\(([^)]+)\)", text):
            target = match.group(1).strip().split()[0].strip("<>")
            if re.match(r"^(?:https?://|data:|#)", target):
                continue
            resolved = (document_path.parent / target).resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                issues.append(
                    ValidationIssue(
                        "image-outside-repository",
                        f"Image path escapes repository: {target}",
                        _line_number(text, match.start()),
                    )
                )
                continue
            if not resolved.is_file():
                issues.append(
                    ValidationIssue(
                        "missing-image",
                        f"Referenced image does not exist: {target}",
                        _line_number(text, match.start()),
                    )
                )

    return issues


def load_entries(payload: str) -> list[dict[str, str]]:
    """Load and validate README note-index entries from JSON."""
    decoded = json.loads(payload)
    entries = decoded.get("notes") if isinstance(decoded, dict) else decoded
    if not isinstance(entries, list):
        raise ValueError("Entries JSON must be a list or an object with a 'notes' list.")

    validated: list[dict[str, str]] = []
    seen_paths: set[str] = set()
    for position, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"Entry {position} must be an object.")
        values = {}
        for key in ("section", "title", "path"):
            value = entry.get(key)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Entry {position} requires a non-empty '{key}'.")
            values[key] = value.strip()
        values["path"] = values["path"].replace("\\", "/")
        if values["path"] in seen_paths:
            raise ValueError(f"Duplicate note path: {values['path']}")
        seen_paths.add(values["path"])
        validated.append(values)
    return validated


def normalize_repo_path(value: str) -> str:
    """Normalize a Notion rich-text path while rejecting unsafe locations."""
    path = value.strip().replace("\\", "/")
    path = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", path)
    path = re.sub(r"/+", "/", path)
    while path.startswith("./"):
        path = path[2:]
    candidate = PurePosixPath(path)
    if (
        not path
        or candidate.is_absolute()
        or ".." in candidate.parts
        or re.match(r"^[A-Za-z]:", path)
        or "://" in path
    ):
        raise ValueError("Repository path must be a safe relative path.")
    if candidate.suffix.lower() != ".md":
        raise ValueError("Repository note path must end in .md.")
    return candidate.as_posix()


def _escape_link_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def update_readme_index(
    readme: str,
    entries: Sequence[dict[str, str]],
    *,
    start_marker: str = README_START_MARKER,
    end_marker: str = README_END_MARKER,
) -> str:
    """Replace only the generated note-index region in README."""
    if readme.count(start_marker) != 1 or readme.count(end_marker) != 1:
        raise ValueError("README markers must each appear exactly once.")
    start = readme.index(start_marker)
    end = readme.index(end_marker)
    if start >= end:
        raise ValueError("README markers are in the wrong order.")

    groups: dict[str, list[dict[str, str]]] = {}
    for entry in entries:
        section = entry["section"].strip()
        groups.setdefault(section, []).append(entry)

    rendered: list[str] = []
    for section, notes in groups.items():
        if rendered:
            rendered.append("")
        rendered.extend((f"### {section}", ""))
        for note in notes:
            label = _escape_link_label(note["title"].strip())
            path = note["path"].strip().replace("\\", "/")
            rendered.append(f"- [{label}]({path})")

    replacement = (
        start_marker
        + "\n"
        + "\n".join(rendered).rstrip()
        + "\n"
        + end_marker
    )
    updated = readme[:start] + replacement + readme[end + len(end_marker) :]
    return updated.replace("\r\n", "\n").replace("\r", "\n")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize and validate Notion notes for GitHub publication."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    normalize_parser = subparsers.add_parser("normalize")
    normalize_parser.add_argument("input", type=Path)
    normalize_parser.add_argument("--output", type=Path)
    normalize_parser.add_argument("--title")

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("input", type=Path)
    validate_parser.add_argument("--repo-root", type=Path)

    readme_parser = subparsers.add_parser("update-readme")
    readme_parser.add_argument("readme", type=Path)
    readme_parser.add_argument("--entries", type=Path, required=True)
    readme_parser.add_argument("--output", type=Path)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.command == "normalize":
        result = normalize_markdown(_read_text(args.input), title=args.title)
        if args.output:
            _write_text(args.output, result)
        else:
            sys.stdout.write(result)
        return 0

    if args.command == "validate":
        markdown = _read_text(args.input)
        repo_root = args.repo_root.resolve() if args.repo_root else None
        issues = validate_markdown(
            markdown,
            document_path=args.input.resolve() if repo_root else None,
            repo_root=repo_root,
        )
        for issue in issues:
            location = f":{issue.line}" if issue.line else ""
            print(f"{args.input}{location}: {issue.code}: {issue.message}")
        return 1 if issues else 0

    if args.command == "update-readme":
        entries = load_entries(_read_text(args.entries))
        result = update_readme_index(_read_text(args.readme), entries)
        _write_text(args.output or args.readme, result)
        return 0

    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
