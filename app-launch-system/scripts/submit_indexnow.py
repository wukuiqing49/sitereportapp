#!/usr/bin/env python3
"""Submit website URLs to IndexNow API (Bing / IndexNow)."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

import yaml

INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
BING_INDEXNOW_ENDPOINT = "https://www.bing.com/indexnow"


def extract_urls_from_sitemap(sitemap_path: Path) -> list[str]:
    """Extract public URLs from sitemap.xml."""
    if not sitemap_path.is_file():
        return []
    content = sitemap_path.read_text(encoding="utf-8")
    return re.findall(r"<loc>\s*(https?://[^\s<]+)\s*</loc>", content)


def load_app_info(app_info_path: Path) -> dict:
    """Load and parse app-info.yaml."""
    if not app_info_path.is_file():
        return {}
    return yaml.safe_load(app_info_path.read_text(encoding="utf-8")) or {}


def resolve_indexnow_config(
    app_info: dict,
    host_override: str | None = None,
    key_override: str | None = None,
    key_location_override: str | None = None,
) -> tuple[str, str, str]:
    """Resolve (host, key, keyLocation) from config and overrides."""
    website_url = str(app_info.get("websiteUrl") or "").strip()
    
    # Resolve host
    host = host_override
    if not host and website_url:
        parsed = urlparse(website_url)
        host = parsed.netloc or parsed.path
    if not host:
        raise ValueError("Host could not be determined. Provide --host or configure websiteUrl in app-info.yaml.")

    # Resolve key
    key = key_override
    if not key:
        index_now_cfg = app_info.get("indexNow")
        if isinstance(index_now_cfg, dict):
            key = str(index_now_cfg.get("key") or "").strip()
        elif isinstance(index_now_cfg, str):
            key = index_now_cfg.strip()
    if not key:
        bing_cfg = app_info.get("bingWebmaster")
        if isinstance(bing_cfg, dict):
            content = str(bing_cfg.get("verificationContent") or "")
            match = re.search(r"<user>\s*([^<\s]+)\s*</user>", content, re.IGNORECASE)
            if match:
                key = match.group(1).strip()
    if not key:
        raise ValueError("IndexNow key could not be determined. Provide --key or configure indexNow.key in app-info.yaml.")

    # Resolve keyLocation
    key_location = key_location_override
    if not key_location:
        base = website_url.rstrip("/") if website_url else f"https://{host}"
        key_location = f"{base}/{key}.txt"

    return host, key, key_location


def build_payload(
    host: str,
    key: str,
    key_location: str,
    url_list: list[str],
) -> dict:
    """Build the IndexNow JSON request payload."""
    return {
        "host": host,
        "key": key,
        "keyLocation": key_location,
        "urlList": url_list,
    }


def send_indexnow_request(
    payload: dict,
    endpoint: str = INDEXNOW_ENDPOINT,
    timeout: int = 15,
) -> tuple[int, str]:
    """Send POST request to IndexNow endpoint."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "SiteReport-IndexNow-Client/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status = response.status
            body = response.read().decode("utf-8", errors="replace")
            return status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return e.code, body
    except urllib.error.URLError as e:
        return 0, str(e.reason)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-info", type=Path, default=Path("app-info.yaml"), help="Path to app-info.yaml")
    parser.add_argument("--sitemap", type=Path, default=Path("sitemap.xml"), help="Path to sitemap.xml")
    parser.add_argument("--host", type=str, default=None, help="Website host (e.g. sitereport-app.pages.dev)")
    parser.add_argument("--key", type=str, default=None, help="IndexNow API key")
    parser.add_argument("--key-location", type=str, default=None, help="IndexNow key file URL")
    parser.add_argument("--urls", nargs="*", default=None, help="Specific URLs to submit")
    parser.add_argument("--endpoint", type=str, default=INDEXNOW_ENDPOINT, help=f"IndexNow endpoint (default: {INDEXNOW_ENDPOINT})")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of URLs to submit")
    parser.add_argument("--dry-run", action="store_true", help="Print payload without sending HTTP request")
    parser.add_argument("--verbose", action="store_true", help="Print detailed output")

    args = parser.parse_args()

    # Load app-info
    app_info_path = args.app_info
    if not app_info_path.is_file():
        alt_path = Path(__file__).resolve().parents[2] / "app-info.yaml"
        if alt_path.is_file():
            app_info_path = alt_path

    app_info = load_app_info(app_info_path) if app_info_path.is_file() else {}

    try:
        host, key, key_location = resolve_indexnow_config(
            app_info,
            host_override=args.host,
            key_override=args.key,
            key_location_override=args.key_location,
        )
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    # Collect URLs
    url_list = []
    if args.urls:
        url_list = list(args.urls)
    else:
        sitemap_path = args.sitemap
        if not sitemap_path.is_file():
            alt_sitemap = Path(__file__).resolve().parents[2] / "sitemap.xml"
            if alt_sitemap.is_file():
                sitemap_path = alt_sitemap
        url_list = extract_urls_from_sitemap(sitemap_path)

    if not url_list:
        website_url = str(app_info.get("websiteUrl") or f"https://{host}/").strip()
        url_list = [website_url]

    if args.limit and args.limit > 0:
        url_list = url_list[:args.limit]

    payload = build_payload(host, key, key_location, url_list)

    if args.dry_run or args.verbose:
        print(f"IndexNow Endpoint: {args.endpoint}")
        print(f"Host: {host}")
        print(f"Key: {key}")
        print(f"Key Location: {key_location}")
        print(f"URL Count: {len(url_list)}")
        print("\nPayload:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))

    if args.dry_run:
        print("\n[DRY RUN] Request not sent.")
        return 0

    print(f"Submitting {len(url_list)} URL(s) to IndexNow ({args.endpoint})...")
    status, body = send_indexnow_request(payload, endpoint=args.endpoint)

    if status in (200, 202):
        print(f"SUCCESS: IndexNow accepted the submission (HTTP {status}).")
        if body:
            print(body)
        return 0
    else:
        print(f"FAILED: IndexNow returned HTTP {status}", file=sys.stderr)
        if body:
            print(f"Response: {body}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
