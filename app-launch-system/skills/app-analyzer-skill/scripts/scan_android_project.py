#!/usr/bin/env python3
"""Collect bounded, structured evidence from an Android project."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKIP_DIRS = {
    ".git",
    ".gradle",
    ".idea",
    ".kotlin",
    "build",
    "generated",
    "node_modules",
    "out",
}
IMAGE_EXTENSIONS = {".avif", ".gif", ".jpeg", ".jpg", ".png", ".webp"}
DOC_EXTENSIONS = {".md", ".mdx", ".rst", ".txt"}
ANDROID_NS = "{http://schemas.android.com/apk/res/android}"
SAFE_STRING_KEYS = re.compile(
    r"(app_name|title|subtitle|description|tagline|feature|onboarding|welcome|about|"
    r"menu|action|screen|permission|privacy|support|error|empty)",
    re.IGNORECASE,
)
SENSITIVE_KEYS = re.compile(r"(api.?key|secret|token|password|credential)", re.IGNORECASE)


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def read_text(path: Path, limit: int = 1_000_000) -> str:
    with path.open("rb") as handle:
        data = handle.read(limit + 1)
    if len(data) > limit:
        data = data[:limit]
    return data.decode("utf-8", errors="replace")


def discover(root: Path) -> list[Path]:
    files: list[Path] = []
    for current, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith("."))
        for name in sorted(names):
            path = Path(current) / name
            try:
                if path.is_file():
                    files.append(path)
            except OSError:
                continue
    return files


def first_match(patterns: list[str], text: str) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            return match.group(1).strip().strip('"\'')
    return None


def parse_gradle(path: Path, root: Path) -> dict[str, Any]:
    text = read_text(path)
    plugin_matches = re.findall(
        r"\bid\s*(?:\(\s*)?[\"']([^\"']+)[\"']|"
        r"\balias\s*\(\s*libs\.plugins\.([\w.\-]+)",
        text,
    )
    plugins = sorted({value for match in plugin_matches for value in match if value})
    is_application = bool(
        re.search(r"com\.android\.application|android\.application", text)
    )
    return {
        "path": relative(path, root),
        "applicationModule": is_application,
        "plugins": plugins[:30],
        "namespace": first_match(
            [r"\bnamespace\s*(?:=\s*)?[\"']([^\"']+)", r"\bnamespace\s+([^\s{]+)"],
            text,
        ),
        "applicationId": first_match(
            [r"\bapplicationId\s*(?:=\s*)?[\"']([^\"']+)", r"\bapplicationId\s+([^\s{]+)"],
            text,
        ),
        "versionName": first_match(
            [r"\bversionName\s*(?:=\s*)?[\"']([^\"']+)", r"\bversionName\s+([^\s{]+)"],
            text,
        ),
        "versionCode": first_match(
            [r"\bversionCode\s*(?:=\s*)?([0-9]+)", r"\bversionCode\s+([^\s{]+)"],
            text,
        ),
        "minSdk": first_match(
            [r"\bminSdk(?:Version)?\s*(?:=\s*)?([0-9]+)", r"\bminSdk(?:Version)?\s+([^\s{]+)"],
            text,
        ),
        "targetSdk": first_match(
            [r"\btargetSdk(?:Version)?\s*(?:=\s*)?([0-9]+)", r"\btargetSdk(?:Version)?\s+([^\s{]+)"],
            text,
        ),
    }


def android_attr(element: ET.Element, name: str) -> str | None:
    return element.attrib.get(ANDROID_NS + name)


def parse_manifest(path: Path, root: Path) -> dict[str, Any]:
    result: dict[str, Any] = {"path": relative(path, root)}
    try:
        tree = ET.parse(path)
        manifest = tree.getroot()
    except (ET.ParseError, OSError) as exc:
        result["error"] = str(exc)
        return result

    application = manifest.find("application")
    result.update(
        {
            "package": manifest.attrib.get("package"),
            "permissions": sorted(
                {
                    android_attr(node, "name")
                    for node in manifest.findall("uses-permission")
                    if android_attr(node, "name")
                }
            ),
            "features": sorted(
                {
                    android_attr(node, "name")
                    for node in manifest.findall("uses-feature")
                    if android_attr(node, "name")
                }
            ),
            "application": {
                "label": android_attr(application, "label") if application is not None else None,
                "icon": android_attr(application, "icon") if application is not None else None,
                "theme": android_attr(application, "theme") if application is not None else None,
            },
            "launcherActivities": [],
        }
    )
    if application is not None:
        for node in list(application.findall("activity")) + list(application.findall("activity-alias")):
            for intent_filter in node.findall("intent-filter"):
                actions = {android_attr(item, "name") for item in intent_filter.findall("action")}
                categories = {android_attr(item, "name") for item in intent_filter.findall("category")}
                if "android.intent.action.MAIN" in actions and "android.intent.category.LAUNCHER" in categories:
                    result["launcherActivities"].append(android_attr(node, "name"))
    return result


def resource_locale(path: Path) -> str:
    folder = path.parent.name
    if folder == "values":
        return "default"
    qualifier = folder.removeprefix("values-")
    match = re.search(r"b\+([A-Za-z]{2,3})(?:\+([A-Za-z]{2}|[0-9]{3}))?", qualifier)
    if match:
        return "-".join(part for part in match.groups() if part)
    match = re.search(r"(?:^|-)r?([a-z]{2,3})(?:-r([A-Z]{2}|[0-9]{3}))?", qualifier)
    if match:
        return "-".join(part for part in match.groups() if part)
    return qualifier


def parse_strings(path: Path, root: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": relative(path, root),
        "locale": resource_locale(path),
        "strings": {},
    }
    try:
        resources = ET.parse(path).getroot()
        selected: dict[str, str] = {}
        for node in resources.findall("string"):
            key = node.attrib.get("name", "")
            if not key or SENSITIVE_KEYS.search(key) or not SAFE_STRING_KEYS.search(key):
                continue
            value = "".join(node.itertext()).strip()
            if value and len(value) <= 500:
                selected[key] = value
            if len(selected) >= 200:
                break
        result["strings"] = selected
    except (ET.ParseError, OSError) as exc:
        result["error"] = str(exc)
    return result


def doc_metadata(path: Path, root: Path) -> dict[str, Any]:
    text = read_text(path, 200_000)
    headings = [
        match.group(1).strip()
        for match in re.finditer(r"^#{1,3}\s+(.+?)\s*$", text, re.MULTILINE)
    ]
    return {"path": relative(path, root), "headings": headings[:40]}


def image_metadata(path: Path, root: Path) -> dict[str, Any]:
    lowered = relative(path, root).lower()
    screenshot = any(token in lowered for token in ("screenshot", "screen_shot", "store-listing", "fastlane"))
    try:
        size = path.stat().st_size
    except OSError:
        size = None
    return {"path": relative(path, root), "bytes": size, "likelyScreenshot": screenshot}


def build_report(root: Path) -> dict[str, Any]:
    files = discover(root)
    gradle_files = [
        path
        for path in files
        if path.name in {"build.gradle", "build.gradle.kts"}
        or path.name.endswith(".versions.toml")
    ]
    manifests = [path for path in files if path.name == "AndroidManifest.xml"]
    strings = [
        path
        for path in files
        if path.name == "strings.xml" and path.parent.name.startswith("values")
    ]
    docs = [
        path
        for path in files
        if path.suffix.lower() in DOC_EXTENSIONS
        and (path.name.lower().startswith("readme") or "doc" in {part.lower() for part in path.parts})
    ]
    images = [path for path in files if path.suffix.lower() in IMAGE_EXTENSIONS]

    gradle_data = [parse_gradle(path, root) for path in gradle_files]
    return {
        "schemaVersion": "1.0",
        "projectPath": str(root),
        "scannedAt": datetime.now(timezone.utc).isoformat(),
        "applicationModules": [
            item["path"] for item in gradle_data if item.get("applicationModule")
        ],
        "gradle": gradle_data,
        "manifests": [parse_manifest(path, root) for path in manifests],
        "stringResources": [parse_strings(path, root) for path in strings],
        "documents": [doc_metadata(path, root) for path in docs[:100]],
        "images": [image_metadata(path, root) for path in images[:1000]],
        "sourceInventory": {
            "kotlinFiles": sum(path.suffix.lower() == ".kt" for path in files),
            "javaFiles": sum(path.suffix.lower() == ".java" for path in files),
            "composeMentions": sum(
                "compose" in relative(path, root).lower()
                for path in files
                if path.suffix.lower() in {".kt", ".kts"}
            ),
            "totalFiles": len(files),
        },
        "warnings": [
            warning
            for warning, condition in (
                ("No AndroidManifest.xml found", not manifests),
                ("No application module detected", not any(item.get("applicationModule") for item in gradle_data)),
                ("No default strings.xml found", not any(path.parent.name == "values" for path in strings)),
            )
            if condition
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_path", help="Android project directory")
    parser.add_argument("--output", help="Write JSON evidence to this path; otherwise print it")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.project_path).expanduser().resolve()
    if not root.is_dir():
        print(f"error: project directory does not exist: {root}", file=sys.stderr)
        return 2

    report = build_report(root)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        output = Path(args.output).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
        print(output)
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
