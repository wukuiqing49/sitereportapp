#!/usr/bin/env python3
"""Find unresolved template tokens and obvious broken references in generated output."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


TOKEN = re.compile(r"\{\{[^{}]+\}\}")
PLACEHOLDER = re.compile(r"\b(?:TODO|FIXME|PLACEHOLDER|example\.com)\b", re.IGNORECASE)
SKIP_DIRS = {".git", ".idea", "app-launch-system", "node_modules"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if not args.output.is_dir():
        print(f"ERROR: directory does not exist: {args.output}")
        return 2
    errors: list[str] = []
    for path in args.output.rglob("*"):
        relative_parts = path.relative_to(args.output).parts
        if any(part in SKIP_DIRS for part in relative_parts[:-1]):
            continue
        if not path.is_file() or path.suffix.lower() not in {".html", ".md", ".yaml", ".yml", ".json", ".xml", ".txt", ".js", ".css"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if TOKEN.search(text):
            errors.append(f"{path}: unresolved template token")
        if PLACEHOLDER.search(text):
            errors.append(f"{path}: placeholder text")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
