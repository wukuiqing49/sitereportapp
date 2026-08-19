#!/usr/bin/env python3
"""Stable command entry point for the Android app launch system."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def absolute(path: Path) -> str:
    return str(path.expanduser().resolve())


def run_script(script: str, arguments: list[str]) -> int:
    command = [sys.executable, str(ROOT / "scripts" / script), *arguments]
    return subprocess.run(command, cwd=ROOT).returncode


def main() -> int:
    parser = argparse.ArgumentParser(prog="launch.py")
    subparsers = parser.add_subparsers(dest="command", required=True)

    info = subparsers.add_parser("validate-app-info")
    info.add_argument("app_info", type=Path)

    output = subparsers.add_parser("validate-output")
    output.add_argument("output", type=Path)

    scan = subparsers.add_parser("scan")
    scan.add_argument("project", type=Path)
    scan.add_argument("--output", type=Path)

    website = subparsers.add_parser("generate-website")
    website.add_argument("--app-info", type=Path)
    website.add_argument("--output", type=Path)
    website.add_argument("--locales", type=Path)
    website.add_argument("--organization", type=Path)
    website.add_argument("--force", action="store_true")

    indexnow = subparsers.add_parser("submit-indexnow")
    indexnow.add_argument("--app-info", type=Path)
    indexnow.add_argument("--sitemap", type=Path)
    indexnow.add_argument("--host", type=str)
    indexnow.add_argument("--key", type=str)
    indexnow.add_argument("--key-location", type=str)
    indexnow.add_argument("--urls", nargs="*")
    indexnow.add_argument("--endpoint", type=str)
    indexnow.add_argument("--limit", type=int)
    indexnow.add_argument("--dry-run", action="store_true")
    indexnow.add_argument("--verbose", action="store_true")

    args = parser.parse_args()
    if args.command == "validate-app-info":
        return run_script("validate_app_info.py", [absolute(args.app_info)])
    if args.command == "validate-output":
        return run_script("validate_output.py", [absolute(args.output)])
    if args.command == "scan":
        command_args = [absolute(args.project)]
        if args.output:
            command_args.extend(["--output", absolute(args.output)])
        return run_script(
            str(Path("..") / "skills" / "app-analyzer-skill" / "scripts" / "scan_android_project.py"),
            command_args,
        )
    if args.command == "generate-website":
        command_args = []
        if args.app_info:
            command_args.extend(["--app-info", absolute(args.app_info)])
        if args.output:
            command_args.extend(["--output", absolute(args.output)])
        if args.locales:
            command_args.extend(["--locales", absolute(args.locales)])
        if args.organization:
            command_args.extend(["--organization", absolute(args.organization)])
        if args.force:
            command_args.append("--force")
        return run_script("generate_website.py", command_args)
    if args.command == "submit-indexnow":
        command_args = []
        if args.app_info:
            command_args.extend(["--app-info", absolute(args.app_info)])
        if args.sitemap:
            command_args.extend(["--sitemap", absolute(args.sitemap)])
        if args.host:
            command_args.extend(["--host", args.host])
        if args.key:
            command_args.extend(["--key", args.key])
        if args.key_location:
            command_args.extend(["--key-location", args.key_location])
        if args.urls:
            command_args.extend(["--urls", *args.urls])
        if args.endpoint:
            command_args.extend(["--endpoint", args.endpoint])
        if args.limit:
            command_args.extend(["--limit", str(args.limit)])
        if args.dry_run:
            command_args.append("--dry-run")
        if args.verbose:
            command_args.append("--verbose")
        return run_script("submit_indexnow.py", command_args)
    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
