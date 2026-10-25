#!/usr/bin/env python3
"""Validate Agentdots' small portable skill format; print active directories.

The header is deliberately a YAML subset: name and description strings,
using plain, single-quoted, JSON double-quoted, or literal/folded block values.
No YAML package, tags, aliases, collections, or implicit conversions are used.
"""

import html
import json
import re
import sys
import textwrap
from pathlib import Path
from urllib.parse import unquote


class InvalidSkill(ValueError):
    pass


def scalar(raw):
    if raw.startswith('"'):
        try:
            value = json.loads(raw)
        except ValueError as error:
            raise InvalidSkill("invalid double-quoted string; use JSON escapes") from error
        if not isinstance(value, str):
            raise InvalidSkill("metadata values must be strings")
        return value
    if raw.startswith("'"):
        if not re.fullmatch(r"'(?:[^']|'')*'", raw):
            raise InvalidSkill("invalid single-quoted string")
        return raw[1:-1].replace("''", "'")
    if not raw or raw[0] in "[]{}&*!|>'\"%@`#" or re.search(r":(?:\s|$)|\s#|^[?:-](?:\s|$)", raw):
        raise InvalidSkill("unsupported plain value; quote the text or use a block scalar")
    if raw.lower() in {"null", "~", "true", "false", "yes", "no", "on", "off"} or re.fullmatch(
        r"[+-]?(?:(?:[0-9][0-9_]*(?:\.[0-9_]*)?|\.[0-9_]+)(?:[eE][+-]?[0-9]+)?|0[xob][0-9a-fA-F_]+|\.(?:inf|nan))",
        raw, re.IGNORECASE,
    ):
        raise InvalidSkill("metadata values must be strings; quote numeric or boolean text")
    return raw


def frontmatter(text, directory_name):
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise InvalidSkill("SKILL.md must begin with --- frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise InvalidSkill("frontmatter is missing its closing ---") from error
    values = {}
    index = 1
    while index < end:
        line = lines[index]
        index += 1
        if not line.strip() or line.startswith("#"):
            continue
        match = re.fullmatch(r"([a-z][a-z0-9_-]*):(?:[ \t]+(.*))?", line)
        if not match:
            raise InvalidSkill("use top-level name: and description: string fields")
        key, raw = match.group(1), (match.group(2) or "").strip()
        if key not in {"name", "description"}:
            raise InvalidSkill(f"unsupported metadata key: {key}; only name and description are allowed")
        if key in values:
            raise InvalidSkill(f"duplicate metadata key: {key}")
        if raw in {"|", "|-", "|+", ">", ">-", ">+"}:
            block = []
            while index < end and (not lines[index].strip() or lines[index].startswith(" ")):
                block.append(lines[index])
                index += 1
            if any("\t" in value[:len(value) - len(value.lstrip())] for value in block):
                raise InvalidSkill("block scalar indentation must use spaces")
            nonempty = [value for value in block if value.strip()]
            indent = len(nonempty[0]) - len(nonempty[0].lstrip(" ")) if nonempty else 0
            if any(len(value) - len(value.lstrip(" ")) < indent for value in nonempty):
                raise InvalidSkill("block scalar indentation must match its first content line")
            value = textwrap.dedent("\n".join(block)).strip()
            if raw.startswith(">"):
                value = " ".join(value.splitlines())
        else:
            value = scalar(raw)
        if not value.strip():
            raise InvalidSkill(f"{key} must be a non-empty string")
        values[key] = value
    if set(values) != {"name", "description"}:
        raise InvalidSkill("both name and description are required")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", values["name"]) or len(values["name"]) > 64:
        raise InvalidSkill("name must be at most 64 lowercase letters, digits, and single hyphens")
    if values["name"] != directory_name:
        raise InvalidSkill(f"name must match directory: {directory_name}")
    body = "\n".join(lines[end + 1:])
    if not body.strip():
        raise InvalidSkill("SKILL.md must contain instructions after the frontmatter")
    return body


def prose(text):
    """Exclude fenced examples, inline code, and HTML comments from link checks."""
    output, fence = [], None
    for line in text.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if fence:
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*", line):
                fence = None
            continue
        if marker:
            fence = marker.group(1)
            continue
        output.append(line)
    text = re.sub(r"<!--.*?-->", "", "\n".join(output), flags=re.DOTALL)
    return re.sub(r"(`+).*?\1", "", text, flags=re.DOTALL)


def destination(contents):
    contents = contents.strip()
    if contents.startswith("<"):
        end = contents.find(">")
        return contents[1:end] if end != -1 else ""
    match = re.match(r"(?:\\.|[^\s])+", contents)
    return match.group(0) if match else ""


def markdown_links(text):
    text = prose(text)
    for match in re.finditer(r"(?<!\\)!?\[[^\]\n]*\]\(", text):
        start, index, depth, angled = match.end(), match.end(), 1, False
        while index < len(text):
            char = text[index]
            if char == "\\":
                index += 2
                continue
            if char == "<":
                angled = True
            elif char == ">":
                angled = False
            elif not angled:
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                    if depth == 0:
                        yield destination(text[start:index])
                        break
            index += 1
    for match in re.finditer(r"(?m)^ {0,3}\[[^\]\n]+\]:[ \t]*(.+)$", text):
        yield destination(match.group(1))


def check_references(skill_dir, body):
    root = skill_dir.resolve()
    pending = [(skill_dir / "SKILL.md", body)]
    visited = set()
    while pending:
        document, text = pending.pop()
        if document.resolve() in visited:
            continue
        visited.add(document.resolve())
        for href in markdown_links(text):
            href = html.unescape(re.sub(r"\\([ ()\\])", r"\1", href))
            if href.lower().startswith("file:"):
                raise InvalidSkill(f"{document.name}: use a relative bundled path instead of a file URI: {href}")
            if not href or href.startswith("#") or href.startswith("//") or re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", href):
                continue
            path = unquote(href.split("#", 1)[0].split("?", 1)[0])
            if path.startswith(("/", "~")):
                raise InvalidSkill(f"{document.name}: local reference must be relative: {href}")
            resolved = (document.parent / path).resolve()
            try:
                resolved.relative_to(root)
            except ValueError as error:
                raise InvalidSkill(f"{document.name}: reference escapes the skill directory: {href}") from error
            if not resolved.exists():
                raise InvalidSkill(f"{document.name}: missing local reference: {href}")
            if resolved.is_file() and resolved.suffix.lower() == ".md":
                pending.append((resolved, resolved.read_text(encoding="utf-8")))


def validate(directory):
    definition = directory / "SKILL.md"
    if directory.is_symlink() or not directory.is_dir():
        raise InvalidSkill("skill source must be a real directory")
    if not definition.is_file():
        raise InvalidSkill("missing SKILL.md; restore it or move this draft outside skills/")
    try:
        definition.resolve().relative_to(directory.resolve())
    except ValueError as error:
        raise InvalidSkill("SKILL.md must stay inside its skill directory") from error
    body = frontmatter(definition.read_text(encoding="utf-8"), directory.name)
    check_references(directory, body)


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/validate-skills.py <skills-directory>", file=sys.stderr)
        return 64
    root = Path(sys.argv[1]).absolute()
    if not root.exists() and not root.is_symlink():
        return 0
    if not root.is_dir() or root.is_symlink():
        print(f"Invalid skills root: {root}", file=sys.stderr)
        return 1
    active, errors = [], []
    for entry in sorted(root.iterdir()):
        if not entry.is_dir() and not entry.is_symlink():
            continue
        try:
            validate(entry)
            active.append(str(entry))
        except (InvalidSkill, OSError, UnicodeError, RuntimeError) as error:
            errors.append(f"Invalid skill {entry.name}: {error}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    for entry in active:
        print(entry)
    return 0


if __name__ == "__main__":
    sys.exit(main())
