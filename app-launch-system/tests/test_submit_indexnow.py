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

    def test_bing_verification_token_is_not_an_indexnow_key(self) -> None:
        app_info = {
            "websiteUrl": "https://example.org/",
            "bingWebmaster": {
                "verificationContent": "<users><user>1234567890ABCDEF1234567890ABCDEF</user></users>"
            },
        }
        with self.assertRaisesRegex(ValueError, "IndexNow key"):
            resolve_indexnow_config(app_info)

    def test_sitemap_decodes_xml_entities_and_deduplicates_urls(self) -> None:
        sitemap = self.root / "sitemap.xml"
        sitemap.write_text(
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            '<url><loc>https://example.com/?a=1&amp;b=2</loc></url>'
            '<url><loc>https://example.com/?a=1&amp;b=2</loc></url>'
            '</urlset>', encoding="utf-8",
        )
        self.assertEqual(["https://example.com/?a=1&b=2"], extract_urls_from_sitemap(sitemap))

    def test_sitemap_index_is_not_submitted_as_page_urls(self) -> None:
        sitemap = self.root / "sitemap.xml"
        sitemap.write_text(
            '<sitemapindex><sitemap><loc>https://example.com/pages.xml</loc></sitemap></sitemapindex>',
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "sitemap index"):
            extract_urls_from_sitemap(sitemap)

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
