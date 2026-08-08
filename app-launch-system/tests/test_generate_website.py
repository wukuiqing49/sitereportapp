from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from generate_website import GenerationError, generate  # noqa: E402


class GenerateWebsiteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.android = self.root / "android"
        (self.android / "res" / "layout").mkdir(parents=True)
        (self.android / "res" / "layout" / "main.xml").write_text("<layout />", encoding="utf-8")
        self.inputs = self.root / "site-input"
        (self.inputs / "screenshots").mkdir(parents=True)
        (self.inputs / "icon.png").write_bytes(b"not-a-real-png-but-a-stable-test-fixture")
        (self.inputs / "screenshots" / "home.png").write_bytes(b"stable-screenshot")
        self.locales = self.root / "content" / "locales"
        self.locales.mkdir(parents=True)
        self.output = self.root / "public"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def app_data(self, targets: list[str] | None = None) -> dict:
        return {
            "schemaVersion": "1.0",
            "sourceProject": str(self.android.resolve()),
            "analyzedAt": "2026-08-08",
            "analysis": {
                "status": "verified",
                "analyzerVersion": "1.0",
                "selectedModule": "app",
                "selectedVariant": "release",
                "validatedAt": "2026-08-08",
                "errors": [],
                "warnings": [],
            },
            "name": "Pixel Notes",
            "packageName": "dev.example.pixelnotes",
            "version": {"name": "1.2.0", "code": "12", "minSdk": 26, "targetSdk": 35},
            "developer": {"name": "Example Studio", "email": "support@example.test"},
            "category": "Productivity",
            "description": {
                "short": "Organize visual notes on Android.",
                "full": "Pixel Notes organizes visual notes on Android.",
                "valueProposition": "Keep visual notes organized in one place.",
            },
            "targetUsers": [],
            "useCases": ["Capture a visual note", "Organize it into a collection"],
            "features": [
                {
                    "id": "visual-notes",
                    "name": "Visual notes",
                    "description": "Create notes with images and text.",
                    "evidence": ["res/layout/main.xml"],
                    "confidence": "verified",
                    "details": {
                        "problem": "Scattered visual notes are difficult to organize.",
                        "capabilities": ["Create image notes", "Add text to a note"],
                        "supportedInputs": ["Images and text"],
                        "supportedOutputs": ["Organized visual notes"],
                        "options": ["Collection and note title"],
                        "steps": ["Choose an image", "Add note text", "Save it to a collection"],
                        "limitations": ["Available options depend on the installed version"],
                        "searchIntents": ["visual notes Android"],
                        "faq": [{"question": "Can notes include images?", "answer": "Yes, image notes are supported."}],
                    },
                }
            ],
            "brand": {
                "productName": "Pixel Notes",
                "tagline": "Visual notes, kept in order",
                "voice": [],
                "colors": ["#126e5a"],
                "logo": "",
            },
            "assets": {
                "root": "site-input",
                "icon": "icon.png",
                "coverImage": "",
                "socialImage": "",
                "screenshots": ["screenshots/home.png"],
            },
            "languages": {
                "source": "en-US",
                "targets": targets or [],
                "availableInApp": ["en-US", *(targets or [])],
                "routing": {
                    "autoDetect": True,
                    "rememberSelection": True,
                    "sourceAtRoot": True,
                    "aliases": {"ja": "ja-JP"} if targets else {},
                },
            },
            "screenshots": [
                {"path": "screenshots/home.png", "locale": "en-US", "screen": "home", "caption": "Home screen"}
            ],
            "googlePlayUrl": "",
            "websiteUrl": "",
            "searchConsole": {},
            "support": {"email": "support@example.test", "url": ""},
            "privacy": {"policyUrl": "", "dataPractices": []},
            "evidence": [{"path": "res/layout/main.xml", "supports": ["visual-notes"]}],
            "unknowns": [],
            "claimsToAvoid": [],
        }

    def write_app_info(self, targets: list[str] | None = None) -> Path:
        path = self.root / "app-info.yaml"
        path.write_text(yaml.safe_dump(self.app_data(targets), sort_keys=False), encoding="utf-8")
        return path

    def target_content(self, locale: str = "ja-JP") -> dict:
        return {
            "locale": locale,
            "languageName": "日本語",
            "direction": "ltr",
            "reviewStatus": "machine-draft",
            "navigation": {
                "primaryLabel": "メインナビゲーション",
                "footerLabel": "フッターナビゲーション",
                "home": "ホーム",
                "features": "機能",
                "screenshots": "スクリーンショット",
                "support": "サポート",
                "privacy": "プライバシー",
                "blog": "ブログ",
                "language": "言語",
                "backToApp": "アプリに戻る",
            },
            "common": {
                "skipToContent": "本文へ移動",
                "googlePlayCta": "Google Play で入手",
                "availability": "Google Play リンクは準備中です",
                "rights": "All rights reserved.",
                "notFoundTitle": "ページが見つかりません",
                "notFoundCopy": "指定されたページは存在しません。",
                "returnHome": "ホームに戻る",
            },
            "home": {
                "pageTitle": "Pixel Notes 公式サイト",
                "metaDescription": "Android のビジュアルノートを整理します。",
                "category": "仕事効率化",
                "tagline": "ビジュアルノートを整理",
                "shortDescription": "画像とテキストのノートをまとめます。",
                "heroScreenshotAlt": "Pixel Notes の画面",
                "heroScreenshotCaption": "ホーム画面",
                "featuresHeading": "主な機能",
                "featuresIntro": "確認済みのアプリ機能です。",
                "features": {
                    "visual-notes": {"name": "ビジュアルノート", "description": "画像とテキストでノートを作成します。"}
                },
                "screenshotsHeading": "アプリ画面",
                "screenshotsIntro": "現在のアプリの実画面です。",
                "workflowHeading": "使い方",
                "workflowIntro": "",
                "workflowSteps": ["ノートを作成", "コレクションに整理"],
                "closingHeading": "Pixel Notes を始める",
                "closingCopy": "Google Play で公開予定です。",
            },
            "featureDetails": {
                "visual-notes": {
                    "problem": "画像メモが散在すると整理が難しくなります。",
                    "capabilities": ["画像メモを作成", "メモにテキストを追加"],
                    "supportedInputs": ["画像とテキスト"],
                    "supportedOutputs": ["整理されたビジュアルノート"],
                    "options": ["コレクションとタイトル"],
                    "steps": ["画像を選択", "テキストを追加", "コレクションに保存"],
                    "limitations": ["選択肢はインストール版に依存します"],
                    "faq": [{"question": "画像を追加できますか？", "answer": "はい、画像メモに対応しています。"}],
                }
            },
            "privacy": {
                "pageTitle": "プライバシー - Pixel Notes",
                "metaDescription": "Pixel Notes のプライバシー情報。",
                "heading": "プライバシー",
                "lastUpdatedLabel": "最終更新",
                "content": [{"heading": "ポリシーの状態", "paragraphs": ["審査済みの完全なポリシーは未提供です。"]}],
            },
            "support": {
                "pageTitle": "サポート - Pixel Notes",
                "metaDescription": "Pixel Notes のヘルプと連絡先。",
                "heading": "サポート",
                "intro": "アプリのサポート情報です。",
                "faqHeading": "よくある質問",
                "faq": [],
                "contactHeading": "お問い合わせ",
                "contactCopy": "サポートメールをご利用ください。",
                "contactCta": "メールを送る",
            },
        }

    def test_source_only_generation_uses_root_entry(self) -> None:
        app_info = self.write_app_info()
        locales, files = generate(app_info, self.output, self.locales)
        self.assertEqual(["en-US"], locales)
        self.assertTrue((self.output / "index.html").is_file())
        self.assertTrue((self.output / "404.html").is_file())
        self.assertTrue((self.output / "_headers").is_file())
        public_manifest = json.loads(
            (self.output / "static-site-manifest.json").read_text(encoding="utf-8")
        )
        self.assertIn("index.html", public_manifest["files"])
        self.assertIn("blog/index.html", public_manifest["files"])
        self.assertIn("features/visual-notes/index.html", public_manifest["files"])
        self.assertNotIn("app-info.yaml", public_manifest["files"])
        self.assertFalse(any(path.startswith("content/") for path in public_manifest["files"]))
        self.assertFalse(any(path.startswith("aso/") for path in public_manifest["files"]))
        self.assertFalse(any(path.startswith("seo-geo/") for path in public_manifest["files"]))
        self.assertNotIn("launch-readiness.yaml", public_manifest["files"])
        self.assertFalse(any(path.startswith("app-launch-system/") for path in public_manifest["files"]))
        self.assertTrue((self.output / "assets" / "screenshots" / "01-home.png").is_file())
        self.assertTrue((self.output / "blog" / "index.html").is_file())
        self.assertTrue((self.output / "features" / "visual-notes" / "index.html").is_file())
        self.assertTrue((self.output / "aso" / "en-US" / "listing.yaml").is_file())
        self.assertTrue((self.output / "seo-geo" / "page-map.yaml").is_file())
        readiness = yaml.safe_load((self.output / "launch-readiness.yaml").read_text(encoding="utf-8"))
        self.assertEqual("blocked", readiness["seoGeo"]["status"])
        self.assertEqual("blocked", readiness["aso"]["status"])
        self.assertTrue((self.output / "content" / "blog" / "en-US" / "visual-notes.md").is_file())
        index = (self.output / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("rel=\"canonical\"", index)
        self.assertIn("availability-state", index)
        self.assertNotIn("video-frame", index)
        self.assertFalse(any("{{" in path.read_text(encoding="utf-8") for path in files if path.suffix == ".html"))

    def test_google_play_and_youtube_links_render(self) -> None:
        data = self.app_data()
        data["googlePlayUrl"] = "https://play.google.com/store/apps/details?id=dev.example.pixelnotes"
        data["videoUrl"] = "https://www.youtube.com/watch?v=w5BVcThNpvQ"
        app_info = self.root / "app-info.yaml"
        app_info.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        generate(app_info, self.output, self.locales)
        index = (self.output / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="https://play.google.com/store/apps/details?id=dev.example.pixelnotes"', index)
        self.assertIn('class="google-play-badge"', index)
        self.assertIn('src="assets/google-play-badge.png"', index)
        self.assertIn('class="hero-video-poster"', index)
        self.assertIn('src="assets/youtube-poster.jpg"', index)
        self.assertIn('hero-video', index)
        self.assertNotIn('video-band', index)
        self.assertNotIn('<iframe', index)
        self.assertIn('href="https://www.youtube.com/watch?v=w5BVcThNpvQ"', index)

    def test_search_console_html_tag_token_renders(self) -> None:
        data = self.app_data()
        data["searchConsole"] = {
            "verificationToken": "google-site-verification=n5QG4SZ3UK5U8ajW3Q4eE7b4rxrFej-lzdzrz_E7b0A"
        }
        app_info = self.root / "app-info.yaml"
        app_info.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        generate(app_info, self.output, self.locales)
        index = (self.output / "index.html").read_text(encoding="utf-8")
        self.assertIn(
            '<meta name="google-site-verification" content="n5QG4SZ3UK5U8ajW3Q4eE7b4rxrFej-lzdzrz_E7b0A">',
            index,
        )

    def test_search_console_html_file_is_generated_and_manifested(self) -> None:
        data = self.app_data()
        data["searchConsole"] = {
            "verificationFileName": "google1234567890abcdef.html",
            "verificationContent": "google-site-verification: google1234567890abcdef.html",
        }
        app_info = self.root / "app-info.yaml"
        app_info.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        generate(app_info, self.output, self.locales)
        verification = self.output / "google1234567890abcdef.html"
        self.assertEqual("google-site-verification: google1234567890abcdef.html\n", verification.read_text(encoding="utf-8"))
        worker = (self.output / "_worker.js").read_text(encoding="utf-8")
        self.assertIn('const verificationPath = "/google1234567890abcdef.html";', worker)
        self.assertIn('const verificationContent = "google-site-verification: google1234567890abcdef.html\\n";', worker)
        manifest = json.loads((self.output / "static-site-manifest.json").read_text(encoding="utf-8"))
        self.assertIn("google1234567890abcdef.html", manifest["files"])
        self.assertIn("_worker.js", manifest["files"])
        self.assertNotIn("_redirects", manifest["files"])

    def test_invalid_search_console_html_file_configuration_stops_generation(self) -> None:
        data = self.app_data()
        data["searchConsole"] = {"verificationFileName": "google123.html"}
        app_info = self.root / "app-info.yaml"
        app_info.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        with self.assertRaisesRegex(GenerationError, "provided together"):
            generate(app_info, self.output, self.locales)
        self.assertFalse(self.output.exists())

    def test_invalid_video_url_stops_generation(self) -> None:
        data = self.app_data()
        data["videoUrl"] = "https://example.com/video"
        app_info = self.root / "app-info.yaml"
        app_info.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        with self.assertRaisesRegex(GenerationError, "valid YouTube"):
            generate(app_info, self.output, self.locales)
        self.assertFalse(self.output.exists())

    def test_multilingual_generation_creates_locale_directory_and_routes(self) -> None:
        app_info = self.write_app_info(["ja-JP"])
        (self.locales / "ja-JP.yaml").write_text(
            yaml.safe_dump(self.target_content(), allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
        locales, _ = generate(app_info, self.output, self.locales)
        self.assertEqual(["en-US", "ja-JP"], locales)
        localized = (self.output / "ja-JP" / "index.html").read_text(encoding="utf-8")
        root = (self.output / "index.html").read_text(encoding="utf-8")
        self.assertIn("ビジュアルノート", localized)
        self.assertIn('"autoRedirect":true', root)
        self.assertIn('"autoRedirect":false', localized)
        self.assertTrue((self.output / "blog" / "ja-JP" / "index.html").is_file())
        self.assertTrue((self.output / "ja-JP" / "features" / "ビジュアルノート" / "index.html").is_file())

    def test_blog_uses_feature_facts_and_omits_unconfirmed_publish_date(self) -> None:
        app_info = self.write_app_info()
        generate(app_info, self.output, self.locales)
        article = (self.output / "blog" / "visual-notes" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Create image notes", article)
        self.assertIn("Choose an image", article)
        self.assertNotIn("datePublished", article)
        self.assertNotIn("2026-08-08", article)

    def test_incomplete_feature_stays_on_homepage_without_thin_pages(self) -> None:
        data = self.app_data()
        data["features"][0].pop("details")
        app_info = self.root / "app-info.yaml"
        app_info.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        generate(app_info, self.output, self.locales)
        index = (self.output / "index.html").read_text(encoding="utf-8")
        self.assertIn("Visual notes", index)
        self.assertNotIn("Explore this feature", index)
        self.assertFalse((self.output / "features").exists())
        self.assertFalse((self.output / "blog").exists())
        readiness = yaml.safe_load((self.output / "launch-readiness.yaml").read_text(encoding="utf-8"))
        self.assertEqual(["visual-notes"], readiness["content"]["skippedFeatures"])

    def test_shared_organization_is_rendered_and_linked(self) -> None:
        app_info = self.write_app_info()
        organization = self.root / "organization.yaml"
        organization.write_text(
            yaml.safe_dump(
                {
                    "schemaVersion": "1.0",
                    "legalName": "Example Company Limited",
                    "displayName": "Example Studio",
                    "website": "https://company.test/",
                    "email": "hello@company.test",
                    "localized": {"en-US": {"description": "A reusable company description."}},
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        generate(app_info, self.output, self.locales, organization_path=organization)
        about = (self.output / "about.html").read_text(encoding="utf-8")
        index = (self.output / "index.html").read_text(encoding="utf-8")
        article = (self.output / "blog" / "visual-notes" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Example Company Limited", about)
        self.assertIn("A reusable company description.", about)
        self.assertIn("Example Company Limited", index)
        self.assertIn("Example Company Limited", article)

    def test_missing_target_translation_stops_before_writing(self) -> None:
        app_info = self.write_app_info(["ja-JP"])
        with self.assertRaisesRegex(GenerationError, "missing target locale content"):
            generate(app_info, self.output, self.locales)
        self.assertFalse(self.output.exists())

    def test_existing_files_require_force(self) -> None:
        app_info = self.write_app_info()
        generate(app_info, self.output, self.locales)
        original = (self.output / "index.html").read_text(encoding="utf-8")
        with self.assertRaisesRegex(GenerationError, "refusing to overwrite"):
            generate(app_info, self.output, self.locales)
        self.assertEqual(original, (self.output / "index.html").read_text(encoding="utf-8"))
        _, files = generate(app_info, self.output, self.locales, force=True)
        self.assertGreater(len(files), 5)


if __name__ == "__main__":
    unittest.main()
