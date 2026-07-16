#!/usr/bin/env python3
"""Reject retired naming in repository file contents and paths."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _joined(*parts: str) -> str:
    return "".join(parts)


FORBIDDEN = (
    ("retired acronym", re.compile(_joined("a", "wgp"), re.IGNORECASE)),
    (
        "retired expanded name",
        re.compile(
            _joined("agent", r"[ _-]+", "workgroup", r"[ _-]+", "protocol"),
            re.IGNORECASE,
        ),
    ),
    (
        "retired protocol repository slug",
        re.compile(_joined("MissionWeave", "Protocol")),
    ),
    (
        "retired Python repository slug",
        re.compile(_joined("MissionWeave", "Python")),
    ),
    (
        "architectural-decision abbreviation",
        re.compile(_joined(r"\b", "a", "dr", r"s?\b"), re.IGNORECASE),
    ),
    (
        "architectural-decision directory",
        re.compile(_joined("docs/", "a", "dr"), re.IGNORECASE),
    ),
    (
        "mixed-case underscore prefix",
        re.compile(_joined("Mission", "Weave", "_")),
    ),
)


def _repository_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(ROOT).parts
    )


def main() -> int:
    violations: list[str] = []

    for path in _repository_files():
        relative = path.relative_to(ROOT).as_posix()
        path_text = relative
        content = path.read_bytes().decode("utf-8", errors="ignore")

        for label, pattern in FORBIDDEN:
            if match := pattern.search(path_text):
                violations.append(f"path: {relative}: {label}: {match.group(0)!r}")

            for match in pattern.finditer(content):
                line = content.count("\n", 0, match.start()) + 1
                violations.append(
                    f"content: {relative}:{line}: {label}: {match.group(0)!r}"
                )

    if violations:
        print("Repository policy violations:", file=sys.stderr)
        for violation in violations:
            print(f"- {violation}", file=sys.stderr)
        return 1

    print(f"Repository policy passed for {len(_repository_files())} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
