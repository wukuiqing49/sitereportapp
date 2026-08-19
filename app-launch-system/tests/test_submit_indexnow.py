from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

import sys
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from submit_indexnow import (  # noqa: E402
    build_payload,
    extract_urls_from_sitemap,
    resolve_indexnow_config,
)


class SubmitIndexNowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_extract_urls_from_sitemap(self) -> None:
        sitemap = self.root / "sitemap.xml"
        sitemap.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            '  <url><loc>https://example.com/</loc></url>\n'
            '  <url><loc>https://example.com/about</loc></url>\n'
            '</urlset>\n',
            encoding="utf-8",
        )
        urls = extract_urls_from_sitemap(sitemap)
        self.assertEqual(["https://example.com/", "https://example.com/about"], urls)

    def test_resolve_indexnow_config_from_app_info(self) -> None:
        app_info = {
            "websiteUrl": "https://sitereport-app.pages.dev/",
            "indexNow": {"key": "DC4AB582C527A7A168FC391B84B8995E"},
        }
        host, key, location = resolve_indexnow_config(app_info)
        self.assertEqual("sitereport-app.pages.dev", host)
        self.assertEqual("DC4AB582C527A7A168FC391B84B8995E", key)
        self.assertEqual("https://sitereport-app.pages.dev/DC4AB582C527A7A168FC391B84B8995E.txt", location)

    def test_resolve_indexnow_config_from_bing_token_fallback(self) -> None:
        app_info = {
            "websiteUrl": "https://example.org/",
            "bingWebmaster": {
                "verificationContent": "<users><user>1234567890ABCDEF1234567890ABCDEF</user></users>"
            },
        }
        host, key, location = resolve_indexnow_config(app_info)
        self.assertEqual("example.org", host)
        self.assertEqual("1234567890ABCDEF1234567890ABCDEF", key)
        self.assertEqual("https://example.org/1234567890ABCDEF1234567890ABCDEF.txt", location)

    def test_build_payload(self) -> None:
        payload = build_payload(
            host="sitereport-app.pages.dev",
            key="DC4AB582C527A7A168FC391B84B8995E",
            key_location="https://sitereport-app.pages.dev/DC4AB582C527A7A168FC391B84B8995E.txt",
            url_list=["https://sitereport-app.pages.dev/"],
        )
        self.assertEqual("sitereport-app.pages.dev", payload["host"])
        self.assertEqual("DC4AB582C527A7A168FC391B84B8995E", payload["key"])
        self.assertEqual(
            "https://sitereport-app.pages.dev/DC4AB582C527A7A168FC391B84B8995E.txt",
            payload["keyLocation"],
        )
        self.assertEqual(["https://sitereport-app.pages.dev/"], payload["urlList"])


if __name__ == "__main__":
    unittest.main()
