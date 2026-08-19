#!/usr/bin/env python3
"""Validate the launch system's app-info.yaml without third-party dependencies."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


LOCALE = re.compile(r"^[a-z]{2,3}(?:-[A-Z][a-z]{3})?(?:-(?:[A-Z]{2}|[0-9]{3}))?$")
PACKAGE = re.compile(r"^[a-zA-Z_][\w]*(?:\.[a-zA-Z_][\w]*)+$")
URL = re.compile(r"^https?://[^\s]+$")
TOKEN = re.compile(r"\{\{[^{}]+\}\}")
INDEX_NOW_KEY = re.compile(r"^[a-zA-Z0-9-]{8,128}$")
ANALYSIS_STATUSES = {"draft", "verified", "blocked"}


def scalar(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^\s*{re.escape(key)}:\s*(.*?)\s*$", text)
    if not match:
        return None
    value = match.group(1).strip().strip('"\'')
    return value if value not in {"", "null", "~"} else None


def section(text: str, key: str) -> str:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(?:\n|$)", text)
    if not match:
        return ""
    remainder = text[match.end():]
    # A top-level YAML sequence may start at column zero ("- id: ...").
    # Only an identifier-like mapping key ends the current top-level section.
    next_section = re.search(r"(?m)^[A-Za-z_][^:]*:\s*", remainder)
    return remainder[: next_section.start()] if next_section else remainder


def list_scalars(text: str, key: str) -> list[str]:
    match = re.search(rf"(?m)^([ \t]*){re.escape(key)}:[ \t]*(.*?)[ \t]*$", text)
    if not match:
        return []
    inline = match.group(2).strip()
    if inline:
        if inline == "[]":
            return []
        if inline.startswith("[") and inline.endswith("]"):
            return [item.strip().strip("\"'") for item in inline[1:-1].split(",") if item.strip()]
        return []

    indent = match.group(1)
    remainder = text[match.end():]
    next_key = re.search(rf"(?m)^{re.escape(indent)}\S[^:]*:\s*", remainder)
    block = remainder[: next_key.start()] if next_key else remainder
    return [
        value.strip().strip("\"'")
        for value in re.findall(r"(?m)^\s*-\s+(.+?)\s*$", block)
        if value.strip().strip("\"'")
    ]


def errors_for(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    if TOKEN.search(text):
        errors.append("contains unresolved template token(s)")

    for key in ("schemaVersion", "sourceProject", "name", "packageName"):
        if scalar(text, key) is None:
            errors.append(f"missing required scalar: {key}")

    analysis = section(text, "analysis")
    if not analysis:
        errors.append("missing required mapping: analysis")
    else:
        analysis_status = scalar(analysis, "status")
        if analysis_status not in ANALYSIS_STATUSES:
            errors.append(f"analysis.status must be one of: {', '.join(sorted(ANALYSIS_STATUSES))}")
        for key in ("analyzerVersion", "selectedModule", "selectedVariant"):
            if scalar(analysis, key) is None:
                errors.append(f"missing analysis.{key}")

    package = scalar(text, "packageName")
    if package and not PACKAGE.fullmatch(package):
        errors.append(f"invalid packageName: {package}")

    for key in ("description",):
        if not re.search(rf"(?m)^{re.escape(key)}:\s*$", text):
            errors.append(f"missing required mapping: {key}")
    for key in ("short", "full", "valueProposition"):
        if scalar(section(text, "description"), key) is None:
            errors.append(f"missing description.{key}")

    feature_block = section(text, "features")
    feature_names = re.findall(r"(?m)^\s*-\s+id:\s*['\"]?([^'\"\s]+)", feature_block)
    if not feature_names:
        errors.append("features must contain at least one item")
    if any(name == "" for name in feature_names):
        errors.append("features contains an empty example item")
    if re.search(r"(?m)^\s*-\s+id:\s*['\"]?['\"]?\s*$", feature_block):
        errors.append("features contains a blank id")
    evidence_entries = len(re.findall(r"(?m)^\s+evidence:\s*$", feature_block))
    if evidence_entries < len(feature_names):
        errors.append("every feature must include an evidence list")

    source_project = scalar(text, "sourceProject")
    project: Path | None = None
    if source_project:
        project = Path(source_project)
        if not project.is_absolute():
            project = (path.parent / project).resolve()
        if not project.exists():
            errors.append(f"sourceProject does not exist: {source_project}")

    language_block = section(text, "languages")
    for key in ("source",):
        value = scalar(language_block, key)
        if value and not LOCALE.fullmatch(value):
            errors.append(f"invalid languages.{key}: {value}")
    source_locale = scalar(language_block, "source")
    for key in ("targets", "availableInApp"):
        locales = list_scalars(language_block, key)
        for locale in locales:
            if not LOCALE.fullmatch(locale):
                errors.append(f"invalid languages.{key} locale: {locale}")
        if len(locales) != len(set(locales)):
            errors.append(f"languages.{key} contains duplicate locales")
        if key == "targets" and source_locale in locales:
            errors.append("languages.targets must not repeat languages.source")

    for key in ("googlePlayUrl", "videoUrl", "websiteUrl"):
        value = scalar(text, key)
        if value and not URL.fullmatch(value):
            errors.append(f"invalid {key}: {value}")

    index_now_block = section(text, "indexNow")
    if index_now_block:
        index_now_key = scalar(index_now_block, "key")
        if index_now_key and not INDEX_NOW_KEY.fullmatch(index_now_key):
            errors.append(f"invalid indexNow.key: {index_now_key}")

    evidence_block = section(text, "evidence")
    evidence_paths = re.findall(r"(?m)^\s*-\s+path:\s*['\"]?([^'\"\s]+)", evidence_block)
    for evidence_path in evidence_paths:
        if Path(evidence_path).is_absolute():
            errors.append(f"evidence path must be relative: {evidence_path}")
        elif project is not None and project.exists() and not (project / evidence_path).exists():
            errors.append(f"evidence path does not exist under sourceProject: {evidence_path}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("app_info", type=Path)
    args = parser.parse_args()
    if not args.app_info.is_file():
        print(f"ERROR: file does not exist: {args.app_info}")
        return 2
    errors = errors_for(args.app_info)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {args.app_info}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
