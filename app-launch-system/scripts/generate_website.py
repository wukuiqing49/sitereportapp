#!/usr/bin/env python3
"""Generate a deterministic localized static website from verified app metadata."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import posixpath
import re
import shutil
import sys
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlparse

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only without the declared dependency
    print("ERROR: PyYAML is required. Run: python -m pip install -r app-launch-system/requirements.txt")
    raise SystemExit(2)

from validate_app_info import errors_for as app_info_errors
from validate_output import PLACEHOLDER, TOKEN


SYSTEM_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SYSTEM_ROOT.parent
TEMPLATE_ROOT = SYSTEM_ROOT / "templates" / "website-template"
BLOG_TEMPLATE_ROOT = SYSTEM_ROOT / "templates" / "blog-template"
IMAGE_EXTENSIONS = {".avif", ".gif", ".jpeg", ".jpg", ".png", ".webp"}
TOKEN_PATTERN = re.compile(r"\{\{[^{}]+\}\}")
LOCAL_REFERENCE = re.compile(r"(?:href|src)=[\"']([^\"']+)[\"']", re.IGNORECASE)


ENGLISH_UI = {
    "languageName": "English",
    "direction": "ltr",
    "navigation": {
        "primaryLabel": "Primary navigation",
        "footerLabel": "Footer navigation",
        "home": "Home",
        "features": "Features",
        "screenshots": "Screenshots",
        "support": "Support",
        "privacy": "Privacy",
        "about": "Company",
        "blog": "Blog",
        "language": "Language",
        "backToApp": "Back to app",
    },
    "common": {
        "skipToContent": "Skip to content",
        "googlePlayCta": "Get it on Google Play",
        "availability": "Google Play link coming soon",
        "rights": "All rights reserved.",
        "notFoundTitle": "Page not found",
        "notFoundCopy": "The requested page does not exist.",
        "returnHome": "Return home",
    },
}

CHINESE_UI = {
    "languageName": "简体中文",
    "direction": "ltr",
    "navigation": {
        "primaryLabel": "主导航",
        "footerLabel": "页脚导航",
        "home": "首页",
        "features": "功能",
        "screenshots": "应用截图",
        "support": "支持",
        "privacy": "隐私",
        "about": "公司",
        "blog": "博客",
        "language": "语言",
        "backToApp": "返回应用首页",
    },
    "common": {
        "skipToContent": "跳到主要内容",
        "googlePlayCta": "前往 Google Play",
        "availability": "Google Play 地址暂未提供",
        "rights": "保留所有权利。",
        "notFoundTitle": "页面未找到",
        "notFoundCopy": "请求的页面不存在。",
        "returnHome": "返回首页",
    },
}

REQUIRED_TARGET_PATHS = (
    "languageName",
    "direction",
    "navigation.primaryLabel",
    "navigation.footerLabel",
    "navigation.home",
    "navigation.features",
    "navigation.screenshots",
    "navigation.support",
    "navigation.privacy",
    "navigation.language",
    "navigation.backToApp",
    "common.skipToContent",
    "common.googlePlayCta",
    "common.availability",
    "common.rights",
    "common.notFoundTitle",
    "common.notFoundCopy",
    "common.returnHome",
    "home.pageTitle",
    "home.metaDescription",
    "home.category",
    "home.tagline",
    "home.shortDescription",
    "home.heroScreenshotAlt",
    "home.heroScreenshotCaption",
    "home.featuresHeading",
    "home.featuresIntro",
    "home.screenshotsHeading",
    "home.screenshotsIntro",
    "home.closingHeading",
    "home.closingCopy",
    "privacy.pageTitle",
    "privacy.metaDescription",
    "privacy.heading",
    "privacy.lastUpdatedLabel",
    "support.pageTitle",
    "support.metaDescription",
    "support.heading",
    "support.intro",
    "support.contactHeading",
    "support.contactCopy",
    "support.contactCta",
)


class GenerationError(RuntimeError):
    """A user-correctable generation failure."""


def load_yaml(path: Path) -> dict:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise GenerationError(f"cannot read YAML {path}: {error}") from error
    if not isinstance(value, dict):
        raise GenerationError(f"YAML root must be a mapping: {path}")
    return value


def nested(data: dict, dotted: str, default=None):
    value = data
    for key in dotted.split("."):
        if not isinstance(value, dict) or key not in value:
            return default
        value = value[key]
    return value


def require_string(data: dict, dotted: str, errors: list[str]) -> None:
    value = nested(data, dotted)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"missing non-empty string: {dotted}")


def merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge(result[key], value)
        else:
            result[key] = value
    return result


def load_organization(path: Path | None) -> dict:
    if path is None:
        return {}
    path = path.resolve()
    if not path.is_file():
        raise GenerationError(f"organization file does not exist: {path}")
    organization = load_yaml(path)
    errors: list[str] = []
    for field in ("legalName", "displayName", "website", "email"):
        require_string(organization, field, errors)
    website = str(organization.get("website") or "")
    if website and not re.match(r"^https://[^\s]+$", website):
        errors.append("organization.website must be an https URL")
    email = str(organization.get("email") or "")
    if email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        errors.append("organization.email must be a valid email address")
    if errors:
        raise GenerationError("organization validation failed:\n  - " + "\n  - ".join(errors))
    return organization


def localized_organization(organization: dict, locale: str) -> dict:
    localized = organization.get("localized") or {}
    if not isinstance(localized, dict):
        return {}
    exact = localized.get(locale)
    if isinstance(exact, dict):
        return exact
    language = locale.split("-")[0].lower()
    for key, value in localized.items():
        if str(key).split("-")[0].lower() == language and isinstance(value, dict):
            return value
    return {}


def organization_labels(locale: str) -> dict[str, str]:
    if locale.split("-")[0].lower() == "zh":
        return {
            "pageTitle": "公司信息",
            "metaDescription": "公司主体、联系渠道和公开信息。",
            "kicker": "公司信息",
            "heading": "关于公司",
            "details": "公开信息",
            "legalName": "公司全称",
            "developerName": "开发者名称",
            "website": "官方网站",
            "email": "联系邮箱",
            "location": "注册地址",
            "contact": "联系我们",
            "contactCopy": "如需产品支持、隐私协助或商务联系，请通过公开邮箱与我们联系。",
            "contactCta": "发送邮件",
            "operator": "运营主体",
        }
    return {
        "pageTitle": "Company information",
        "metaDescription": "Company identity, contact channels, and public information.",
        "kicker": "Company information",
        "heading": "About the company",
        "details": "Public information",
        "legalName": "Legal name",
        "developerName": "Developer name",
        "website": "Official website",
        "email": "Contact email",
        "location": "Registered address",
        "contact": "Contact",
        "contactCopy": "For product support, privacy assistance, or business inquiries, contact us through the public email address.",
        "contactCta": "Send email",
        "operator": "Operator",
    }


def organization_entity(organization: dict) -> dict:
    if not organization:
        return {}
    website = str(organization.get("website") or "").rstrip("/") + "/"
    entity: dict[str, object] = {
        "@type": "Organization",
        "@id": urljoin(website, "#organization"),
        "name": str(organization.get("legalName") or ""),
        "alternateName": str(organization.get("displayName") or ""),
        "url": website,
        "email": str(organization.get("email") or ""),
    }
    developer_url = str(nested(organization, "googlePlayDeveloper.url", "") or "")
    if developer_url and nested(organization, "googlePlayDeveloper.public", False) is True:
        entity["sameAs"] = [developer_url]
    address = organization.get("address") or {}
    if isinstance(address, dict) and address:
        entity["address"] = {
            "@type": "PostalAddress",
            "streetAddress": str(address.get("streetAddress") or ""),
            "addressLocality": str(address.get("district") or ""),
            "addressRegion": str(address.get("region") or ""),
            "postalCode": str(address.get("postalCode") or ""),
            "addressCountry": str(address.get("countryCode") or ""),
        }
    return entity


def organization_notice(organization: dict, locale: str) -> str:
    if not organization:
        return ""
    labels = organization_labels(locale)
    legal_name = esc(organization.get("legalName"))
    email = esc(organization.get("email"))
    website = esc(organization.get("website"))
    return (
        f'<section class="organization-notice" aria-labelledby="operator-title"><h2 id="operator-title">{esc(labels["operator"])}</h2>'
        f'<p>{legal_name} · <a href="mailto:{email}">{email}</a> · '
        f'<a href="{website}" rel="noopener noreferrer">{website}</a></p></section>'
    )


def verified_features(app: dict) -> list[dict]:
    features = []
    for feature in app.get("features") or []:
        if not isinstance(feature, dict):
            continue
        if feature.get("confidence") == "verified" and feature.get("evidence"):
            features.append(feature)
    return features


def content_ready_features(features: list[dict]) -> list[dict]:
    """Return only features with enough verified facts for a substantive page."""
    ready: list[dict] = []
    for feature in features:
        details = feature.get("details")
        if not isinstance(details, dict):
            continue
        required_text = isinstance(details.get("problem"), str) and bool(details["problem"].strip())
        required_lists = all(
            isinstance(details.get(key), list)
            and len([item for item in details[key] if isinstance(item, str) and item.strip()]) >= minimum
            for key, minimum in {
                "capabilities": 2,
                "supportedInputs": 1,
                "supportedOutputs": 1,
                "options": 1,
                "steps": 3,
                "limitations": 1,
            }.items()
        )
        faq = details.get("faq")
        faq_ready = isinstance(faq, list) and any(
            isinstance(item, dict)
            and isinstance(item.get("question"), str)
            and bool(item["question"].strip())
            and isinstance(item.get("answer"), str)
            and bool(item["answer"].strip())
            for item in faq
        )
        if required_text and required_lists and faq_ready:
            ready.append(feature)
    return ready


def source_content(app: dict, locale: str, features: list[dict]) -> dict:
    base_language = locale.split("-")[0].lower()
    ui = CHINESE_UI if base_language == "zh" else ENGLISH_UI if base_language == "en" else None
    if ui is None:
        raise GenerationError(
            f"source locale {locale} needs an explicit translation file because built-in UI labels support only en and zh"
        )

    name = str(app.get("name") or "").strip()
    description = app.get("description") or {}
    brand = app.get("brand") or {}
    tagline = str(brand.get("tagline") or description.get("valueProposition") or "").strip()
    short = str(description.get("short") or "").strip()
    category = str(app.get("category") or ("Android 应用" if base_language == "zh" else "Android app"))
    feature_map = {
        str(item["id"]): {
            "name": str(item.get("name") or ""),
            "description": str(item.get("description") or ""),
        }
        for item in features
    }
    feature_details = {
        str(item["id"]): item["details"]
        for item in content_ready_features(features)
    }
    practices = [item for item in (nested(app, "privacy.dataPractices", []) or []) if isinstance(item, str) and item.strip()]
    if base_language == "zh":
        privacy_content = (
            [{"heading": "数据处理说明", "paragraphs": practices}]
            if practices
            else [{"heading": "政策状态", "paragraphs": ["此应用尚未提供完整且经过审核的隐私政策内容。"]}]
        )
        localized = {
            "locale": locale,
            "reviewStatus": "source",
            "home": {
                "pageTitle": f"{name} - 官方网站",
                "metaDescription": short,
                "category": category,
                "tagline": tagline,
                "shortDescription": short,
                "fullDescription": str(description.get("full") or short),
                "heroScreenshotAlt": f"{name} 应用界面截图",
                "heroScreenshotCaption": f"{name} 的真实应用界面",
                "featuresHeading": "核心功能",
                "featuresIntro": str(description.get("valueProposition") or short),
                "features": feature_map,
                "screenshotsHeading": "查看应用界面",
                "screenshotsIntro": "来自当前应用版本的真实截图。",
                "workflowHeading": "适用场景",
                "workflowIntro": "",
                "workflowSteps": [str(item) for item in (app.get("useCases") or []) if isinstance(item, str)],
                "closingHeading": f"开始使用 {name}",
                "closingCopy": short,
            },
            "featureDetails": feature_details,
            "privacy": {
                "pageTitle": f"隐私 - {name}",
                "metaDescription": f"{name} 的隐私信息。",
                "heading": "隐私政策",
                "lastUpdatedLabel": "最后更新",
                "content": privacy_content,
            },
            "support": {
                "pageTitle": f"支持 - {name}",
                "metaDescription": f"获取 {name} 的帮助与联系信息。",
                "heading": "支持",
                "intro": f"查看 {name} 的版本信息并联系支持团队。",
                "faqHeading": "常见问题",
                "faq": [],
                "contactHeading": "联系支持",
                "contactCopy": "如需帮助，请使用已确认的支持邮箱。",
                "contactCta": "发送邮件",
            },
        }
    else:
        privacy_content = (
            [{"heading": "Data practices", "paragraphs": practices}]
            if practices
            else [{"heading": "Policy status", "paragraphs": ["A complete reviewed privacy policy has not been provided for this app."]}]
        )
        localized = {
            "locale": locale,
            "reviewStatus": "source",
            "home": {
                "pageTitle": f"{name} - official website",
                "metaDescription": short,
                "category": category,
                "tagline": tagline,
                "shortDescription": short,
                "fullDescription": str(description.get("full") or short),
                "heroScreenshotAlt": f"{name} app interface screenshot",
                "heroScreenshotCaption": f"The real {name} app interface",
                "featuresHeading": "What it does",
                "featuresIntro": str(description.get("valueProposition") or short),
                "features": feature_map,
                "screenshotsHeading": "See the app",
                "screenshotsIntro": "Real screens from the current app version.",
                "workflowHeading": "Where it fits",
                "workflowIntro": "",
                "workflowSteps": [str(item) for item in (app.get("useCases") or []) if isinstance(item, str)],
                "closingHeading": f"Start using {name}",
                "closingCopy": short,
            },
            "featureDetails": feature_details,
            "privacy": {
                "pageTitle": f"Privacy - {name}",
                "metaDescription": f"Privacy information for {name}.",
                "heading": "Privacy",
                "lastUpdatedLabel": "Last updated",
                "content": privacy_content,
            },
            "support": {
                "pageTitle": f"Support - {name}",
                "metaDescription": f"Help and contact information for {name}.",
                "heading": "Support",
                "intro": f"Find version information and contact support for {name}.",
                "faqHeading": "Common questions",
                "faq": [],
                "contactHeading": "Contact support",
                "contactCopy": "Use the confirmed support email if you need help.",
                "contactCta": "Email support",
            },
        }
    return merge(ui, localized)


def validate_target_content(content: dict, locale: str, features: list[dict], path: Path) -> None:
    errors: list[str] = []
    if content.get("locale") != locale:
        errors.append(f"locale must equal {locale}")
    for dotted in REQUIRED_TARGET_PATHS:
        require_string(content, dotted, errors)
    if content.get("direction") not in {"ltr", "rtl"}:
        errors.append("direction must be ltr or rtl")
    if content.get("reviewStatus") not in {None, "machine-draft", "reviewed", "source"}:
        errors.append("reviewStatus must be machine-draft, reviewed, or source")
    feature_content = nested(content, "home.features")
    if not isinstance(feature_content, dict):
        errors.append("home.features must be a mapping keyed by verified feature id")
    else:
        for feature in features:
            feature_id = str(feature.get("id") or "")
            translated = feature_content.get(feature_id)
            if not isinstance(translated, dict):
                errors.append(f"missing home.features.{feature_id}")
                continue
            require_string(translated, "name", errors)
            require_string(translated, "description", errors)
    translated_details = content.get("featureDetails")
    for feature in content_ready_features(features):
        feature_id = str(feature.get("id") or "")
        details = translated_details.get(feature_id) if isinstance(translated_details, dict) else None
        if not isinstance(details, dict):
            errors.append(f"missing featureDetails.{feature_id}")
            continue
        require_string(details, "problem", errors)
        for key, minimum in {
            "capabilities": 2,
            "supportedInputs": 1,
            "supportedOutputs": 1,
            "options": 1,
            "steps": 3,
            "limitations": 1,
        }.items():
            values = details.get(key)
            if not isinstance(values, list) or len(
                [item for item in values if isinstance(item, str) and item.strip()]
            ) < minimum:
                errors.append(f"featureDetails.{feature_id}.{key} must contain at least {minimum} item(s)")
        faq = details.get("faq")
        if not isinstance(faq, list) or not any(
            isinstance(item, dict) and str(item.get("question") or "").strip() and str(item.get("answer") or "").strip()
            for item in faq
        ):
            errors.append(f"featureDetails.{feature_id}.faq must contain a question and answer")
    privacy = nested(content, "privacy.content")
    if not isinstance(privacy, list) or not privacy:
        errors.append("privacy.content must contain at least one reviewed or explicitly draft section")
    else:
        for index, section in enumerate(privacy):
            paragraphs = section.get("paragraphs") if isinstance(section, dict) else None
            if not isinstance(paragraphs, list) or not any(
                isinstance(item, str) and item.strip() for item in paragraphs
            ):
                errors.append(f"privacy.content[{index}].paragraphs must contain non-empty text")
    if errors:
        detail = "\n  - ".join(errors)
        raise GenerationError(f"invalid locale content {path}:\n  - {detail}")


def resolve_locales(app: dict, locales_root: Path, features: list[dict]) -> tuple[str, list[str], dict[str, dict]]:
    languages = app.get("languages") or {}
    source = str(languages.get("source") or "").strip()
    targets = [str(item) for item in (languages.get("targets") or [])]
    source_file = locales_root / f"{source}.yaml"
    try:
        source_defaults = source_content(app, source, features)
    except GenerationError:
        if not source_file.is_file():
            raise
        source_defaults = {}
    contents = {source: merge(source_defaults, load_yaml(source_file)) if source_file.is_file() else source_defaults}
    if source_file.is_file():
        validate_target_content(contents[source], source, features, source_file)
        contents[source]["reviewStatus"] = "source"

    for locale in targets:
        path = locales_root / f"{locale}.yaml"
        if not path.is_file():
            raise GenerationError(f"missing target locale content: {path}")
        content = load_yaml(path)
        validate_target_content(content, locale, features, path)
        contents[locale] = content
    return source, targets, contents


def ensure_inside(path: Path, root: Path) -> None:
    try:
        path.relative_to(root)
    except ValueError as error:
        raise GenerationError(f"asset path escapes configured root: {path}") from error


def resolve_asset(root: Path, value: object, label: str, required: bool = False) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        if required:
            raise GenerationError(f"missing required asset: {label}")
        return None
    relative = Path(value)
    if relative.is_absolute():
        raise GenerationError(f"{label} must be relative to assets.root: {value}")
    path = (root / relative).resolve()
    ensure_inside(path, root.resolve())
    if not path.is_file():
        raise GenerationError(f"asset does not exist: {path}")
    if path.suffix.lower() not in IMAGE_EXTENSIONS:
        raise GenerationError(f"unsupported image type for {label}: {path.suffix}")
    return path


def copy_assets(app: dict, app_info_path: Path, stage: Path) -> dict:
    config = app.get("assets") or {}
    root_value = str(config.get("root") or "app-launch-system/config/assets")
    root_path = Path(root_value)
    if root_path.is_absolute():
        raise GenerationError("assets.root must be relative to the project root")
    asset_root = (app_info_path.parent / root_path).resolve()
    if not asset_root.is_dir():
        raise GenerationError(f"assets.root does not exist: {asset_root}")

    output_assets = stage / "assets"
    output_assets.mkdir(parents=True, exist_ok=True)
    for filename in ("app.js", "styles.css", "locale-router.js", "google-play-badge.png", "youtube-poster.jpg"):
        shutil.copy2(TEMPLATE_ROOT / "assets" / filename, output_assets / filename)

    copied: dict[str, object] = {
        "googlePlayBadge": "assets/google-play-badge.png",
        "youtubePoster": "assets/youtube-poster.jpg",
        "screenshots": [],
    }
    for key, output_name in (("icon", "icon"), ("coverImage", "cover"), ("socialImage", "social")):
        source = resolve_asset(asset_root, config.get(key), f"assets.{key}")
        if source:
            relative = Path("assets") / f"{output_name}{source.suffix.lower()}"
            shutil.copy2(source, stage / relative)
            copied[key] = relative.as_posix()

    screenshot_values = config.get("screenshots") or []
    if not isinstance(screenshot_values, list) or not screenshot_values:
        raise GenerationError("assets.screenshots must contain at least one real app screenshot")
    metadata = {}
    for item in app.get("screenshots") or []:
        if isinstance(item, dict) and isinstance(item.get("path"), str):
            metadata[item["path"]] = item
            metadata[Path(item["path"]).name] = item
    seen_names: set[str] = set()
    for index, item in enumerate(screenshot_values, start=1):
        value = item.get("path") if isinstance(item, dict) else item
        source = resolve_asset(asset_root, value, f"assets.screenshots[{index - 1}]", required=True)
        assert source is not None
        stem = re.sub(r"[^a-zA-Z0-9-]+", "-", source.stem).strip("-").lower() or "screen"
        name = f"{index:02d}-{stem}{source.suffix.lower()}"
        if name in seen_names:
            name = f"{index:02d}-screen{source.suffix.lower()}"
        seen_names.add(name)
        relative = Path("assets") / "screenshots" / name
        (stage / relative).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, stage / relative)
        details = item if isinstance(item, dict) else metadata.get(str(value), metadata.get(source.name, {}))
        copied["screenshots"].append(
            {
                "path": relative.as_posix(),
                "caption": str((details or {}).get("caption") or ""),
                "screen": str((details or {}).get("screen") or ""),
                "locale": str((details or {}).get("locale") or ""),
            }
        )
    return copied


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


VIDEO_LABELS = {
    "en": {
        "heading": "Watch the SiteReport walkthrough",
        "intro": "See how SiteReport turns field inspection evidence into a shareable report.",
        "title": "SiteReport video walkthrough",
        "link": "Watch on YouTube",
    },
    "zh": {
        "heading": "观看 SiteReport 视频简介",
        "intro": "快速了解 SiteReport 如何将现场巡检证据整理为可分享的报告。",
        "title": "SiteReport 视频简介",
        "link": "在 YouTube 上观看",
    },
    "es": {
        "heading": "Mira el vídeo de SiteReport",
        "intro": "Descubre cómo SiteReport convierte las evidencias de campo en un informe compartible.",
        "title": "Vídeo de presentación de SiteReport",
        "link": "Ver en YouTube",
    },
    "pt": {
        "heading": "Veja o vídeo do SiteReport",
        "intro": "Veja como o SiteReport transforma evidências de campo em um relatório compartilhável.",
        "title": "Vídeo de apresentação do SiteReport",
        "link": "Assistir no YouTube",
    },
    "fr": {
        "heading": "Voir la présentation de SiteReport",
        "intro": "Découvrez comment SiteReport transforme les preuves terrain en rapport partageable.",
        "title": "Présentation vidéo de SiteReport",
        "link": "Voir sur YouTube",
    },
    "de": {
        "heading": "SiteReport im Video ansehen",
        "intro": "Sehen Sie, wie SiteReport Außeneinsatz-Belege in einen teilbaren Bericht verwandelt.",
        "title": "SiteReport Videoeinführung",
        "link": "Auf YouTube ansehen",
    },
    "ja": {
        "heading": "SiteReport の紹介動画を見る",
        "intro": "SiteReport が現場の証拠を共有できるレポートにまとめる流れをご覧ください。",
        "title": "SiteReport 紹介動画",
        "link": "YouTube で見る",
    },
    "ko": {
        "heading": "SiteReport 소개 영상 보기",
        "intro": "SiteReport가 현장 증거를 공유 가능한 보고서로 정리하는 과정을 확인해 보세요.",
        "title": "SiteReport 소개 영상",
        "link": "YouTube에서 보기",
    },
    "ar": {
        "heading": "شاهد فيديو SiteReport التعريفي",
        "intro": "تعرّف على طريقة تحويل SiteReport لأدلة الفحص الميداني إلى تقرير قابل للمشاركة.",
        "title": "فيديو SiteReport التعريفي",
        "link": "شاهد على YouTube",
    },
}


OVERVIEW_LABELS = {
    "en": {
        "heading": "One workflow from site visit to signed report",
        "intro": "Plan the inspection, capture evidence in context, and deliver a clear report without moving between separate tools.",
    },
    "zh": {
        "heading": "从现场巡检到签字报告的一套工作流",
        "intro": "规划巡检、记录现场证据，并在一个工作流中生成清晰的报告，减少工具之间的来回切换。",
    },
}


SEO_PRIMARY_QUERIES = {
    "en": "field inspection app",
    "zh": "现场巡检报告 app",
    "es": "aplicación de inspección de campo",
    "pt": "app de inspeção de campo",
    "fr": "application d'inspection terrain",
    "de": "App für Feldinspektionen",
    "ja": "現場検査アプリ",
    "ko": "현장 검사 앱",
    "ar": "تطبيق فحص ميداني",
}


YOUTUBE_VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")


def youtube_embed_url(value: object) -> str:
    """Return a privacy-enhanced embed URL for a supported YouTube URL."""
    raw = str(value or "").strip()
    parsed = urlparse(raw)
    host = parsed.hostname.lower() if parsed.hostname else ""
    video_id = ""
    if host in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [""])[0]
        elif parsed.path.startswith("/embed/"):
            video_id = parsed.path.removeprefix("/embed/").split("/", 1)[0]
    elif host == "youtu.be":
        video_id = parsed.path.removeprefix("/").split("/", 1)[0]
    if not YOUTUBE_VIDEO_ID.fullmatch(video_id):
        raise GenerationError(
            "videoUrl must be a valid YouTube watch, youtu.be, or embed URL"
        )
    return f"https://www.youtube-nocookie.com/embed/{video_id}"


def render_video_poster(video_url: str, locale: str, base_path: str, poster_path: str) -> str:
    labels = VIDEO_LABELS.get(locale.split("-")[0].lower(), VIDEO_LABELS["en"])
    return (
        f'<a class="hero-video-poster" href="{esc(video_url)}" target="_blank" '
        f'rel="noopener noreferrer" aria-label="{esc(labels["link"])}: {esc(labels["title"])}">'
        f'<img src="{esc(base_path + poster_path)}" alt="" width="1280" height="720">'
        '<span class="video-play-icon" aria-hidden="true"></span></a>'
    )


def render_overview_section(content: dict, locale: str) -> str:
    labels = OVERVIEW_LABELS.get(locale.split("-")[0].lower(), OVERVIEW_LABELS["en"])
    translated = nested(content, "home.features", {}) or {}
    items = []
    for feature_id in ("project-management", "photo-evidence", "report-generation"):
        feature = translated.get(feature_id)
        if not isinstance(feature, dict):
            continue
        name = str(feature.get("name") or "").strip()
        description = str(feature.get("description") or "").strip()
        if name and description:
            items.append(
                f'<article class="overview-point"><h3>{esc(name)}</h3><p>{esc(description)}</p></article>'
            )
    if not items:
        return ""
    return (
        '<section class="overview-band" aria-labelledby="overview-title">'
        '<div class="section-heading">'
        f'<h2 id="overview-title">{esc(labels["heading"])}</h2>'
        f'<p>{esc(labels["intro"])}</p>'
        '</div><div class="overview-points">'
        + "".join(items)
        + "</div></section>"
    )


def seo_primary_query(locale: str, app: dict) -> str:
    language = locale.split("-")[0].lower()
    return str(
        SEO_PRIMARY_QUERIES.get(language)
        or nested(app, "keywords.primary.0", "")
        or nested(app, "name", "")
    )


def render_template(name: str, values: dict[str, str]) -> str:
    result = (TEMPLATE_ROOT / name).read_text(encoding="utf-8")
    for token, value in values.items():
        result = result.replace("{{" + token + "}}", value)
    unresolved = TOKEN_PATTERN.findall(result)
    if unresolved:
        raise GenerationError(f"unresolved tokens in {name}: {', '.join(sorted(set(unresolved)))}")
    return result


def page_relative(locale: str, source: str, page: str) -> str:
    if locale == source:
        return "" if page == "index.html" else page
    return f"{locale}/" if page == "index.html" else f"{locale}/{page}"


def page_url(base_url: str, locale: str, source: str, page: str) -> str:
    return urljoin(base_url, page_relative(locale, source, page))


def route_url(current: str, target: str, source: str, page: str, base_url: str) -> str:
    if base_url:
        return page_url(base_url, target, source, page)
    if current == source:
        if target == source:
            return "./" if page == "index.html" else page
        return f"{target}/" if page == "index.html" else f"{target}/{page}"
    if target == source:
        return "../" if page == "index.html" else f"../{page}"
    if target == current:
        return "./" if page == "index.html" else page
    return f"../{target}/" if page == "index.html" else f"../{target}/{page}"


def canonical_tags(base_url: str, current: str, source: str, locales: list[str], page: str) -> str:
    if not base_url:
        return ""
    lines = [f'<link rel="canonical" href="{esc(page_url(base_url, current, source, page))}">']
    for locale in locales:
        lines.append(
            f'<link rel="alternate" hreflang="{esc(locale)}" href="{esc(page_url(base_url, locale, source, page))}">'
        )
    lines.append(f'<link rel="alternate" hreflang="x-default" href="{esc(page_url(base_url, source, source, page))}">')
    return "\n  ".join(lines)


def locale_controls(
    current: str,
    source: str,
    locales: list[str],
    contents: dict[str, dict],
    page: str,
    base_url: str,
    aliases: dict,
    package_name: str,
    auto_detect: bool,
    remember_selection: bool,
) -> tuple[str, str]:
    routes = [
        {"code": locale, "url": route_url(current, locale, source, page, base_url)}
        for locale in locales
    ]
    config = {
        "sourceLocale": source,
        "currentLocale": current,
        "autoRedirect": current == source and auto_detect,
        "rememberSelection": remember_selection,
        "storageKey": f"{package_name}:locale",
        "aliases": aliases,
        "locales": routes,
    }
    options = "".join(
        f'<option value="{esc(locale)}">{esc(contents[locale]["languageName"])}</option>' for locale in locales
    )
    label = esc(nested(contents[current], "navigation.language"))
    switcher = (
        f'<label class="language-picker"><span class="visually-hidden">{label}</span>'
        f'<select data-locale-switcher aria-label="{label}">{options}</select></label>'
    )
    return switcher, json.dumps(config, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def render_feature_items(content: dict, features: list[dict], locale: str, source: str) -> str:
    translated = nested(content, "home.features", {})
    ready_ids = {str(feature["id"]) for feature in content_ready_features(features)}
    link_label = "查看功能详情" if locale.split("-")[0].lower() == "zh" else "Explore this feature"
    cards = []
    for feature in features:
        feature_id = str(feature["id"])
        item = translated[feature_id]
        link = ""
        if feature_id in ready_ids:
            slug = feature_slug(locale, source, content, feature)
            link = f'<a class="feature-link" href="features/{esc(slug)}/">{esc(link_label)} <span aria-hidden="true">&rarr;</span></a>'
        cards.append(
            f'<article><h3>{esc(item["name"])}</h3><p>{esc(item["description"])}</p>{link}</article>'
        )
    return "\n        ".join(cards)


def render_privacy_content(content: dict) -> str:
    sections = []
    for section in nested(content, "privacy.content", []) or []:
        if not isinstance(section, dict):
            continue
        heading = section.get("heading")
        paragraphs = [item for item in (section.get("paragraphs") or []) if isinstance(item, str) and item.strip()]
        body = "".join(f"<p>{esc(item)}</p>" for item in paragraphs)
        sections.append((f"<section><h2>{esc(heading)}</h2>{body}</section>" if heading else body))
    return "\n    ".join(sections)


def render_faq(content: dict) -> str:
    items = []
    for item in nested(content, "support.faq", []) or []:
        if not isinstance(item, dict) or not item.get("question") or not item.get("answer"):
            continue
        items.append(f'<details><summary>{esc(item["question"])}</summary><p>{esc(item["answer"])}</p></details>')
    if not items:
        return ""
    return (
        '<section aria-labelledby="faq-title"><h2 id="faq-title">'
        + esc(nested(content, "support.faqHeading", ""))
        + "</h2>"
        + "".join(items)
        + "</section>"
    )


def render_screenshots(content: dict, screenshots: list[dict], base_path: str, use_asset_captions: bool) -> str:
    figures = []
    default_caption = str(nested(content, "home.heroScreenshotCaption", ""))
    alt = str(nested(content, "home.heroScreenshotAlt", ""))
    for screenshot in screenshots:
        caption = (screenshot.get("caption") if use_asset_captions else "") or default_caption
        figures.append(
            f'<figure><img src="{esc(base_path + screenshot["path"])}" alt="{esc(alt)}" loading="lazy">'
            f'<figcaption>{esc(caption)}</figcaption></figure>'
        )
    return (
        '<section id="screenshots" class="screenshot-band" aria-labelledby="screenshots-title">'
        '<div class="section-heading"><h2 id="screenshots-title">'
        + esc(nested(content, "home.screenshotsHeading"))
        + "</h2><p>"
        + esc(nested(content, "home.screenshotsIntro"))
        + '</p></div><div class="screenshot-list">'
        + "".join(figures)
        + "</div></section>"
    )


def render_blog_template(name: str, values: dict[str, str]) -> str:
    result = (BLOG_TEMPLATE_ROOT / "pages" / name).read_text(encoding="utf-8")
    for token, value in values.items():
        result = result.replace("{{" + token + "}}", value)
    unresolved = TOKEN_PATTERN.findall(result)
    if unresolved:
        raise GenerationError(f"unresolved tokens in blog template {name}: {', '.join(sorted(set(unresolved)))}")
    return result


def slugify(value: str, fallback: str) -> str:
    slug = re.sub(r"[^\w\u3400-\u9fff]+", "-", value.strip().lower(), flags=re.UNICODE)
    slug = slug.replace("_", "-").strip("-")
    return slug or fallback


def localized_feature_details(content: dict, feature: dict) -> dict:
    feature_id = str(feature.get("id") or "")
    details = nested(content, f"featureDetails.{feature_id}", {})
    return details if isinstance(details, dict) else {}


def feature_slug(locale: str, source: str, content: dict, feature: dict) -> str:
    feature_id = str(feature.get("id") or "feature")
    if locale == source:
        return slugify(feature_id, feature_id)
    name = str(nested(content, f"home.features.{feature_id}.name", feature_id))
    return slugify(name, feature_id)


def feature_page_path(locale: str, source: str, slug: str) -> str:
    locale_part = "" if locale == source else f"{locale}/"
    return f"{locale_part}features/{slug}/index.html"


def feature_labels(locale: str) -> dict[str, str]:
    if locale.split("-")[0].lower() == "zh":
        return {
            "kicker": "已验证功能",
            "problem": "解决什么问题",
            "capabilities": "可以完成什么",
            "inputs": "支持的输入",
            "outputs": "生成的结果",
            "options": "可配置选项",
            "steps": "操作流程",
            "limitations": "使用限制",
            "faq": "常见问题",
            "evidence": "项目证据",
            "blog": "阅读相关指南",
            "breadcrumb": "面包屑导航",
        }
    return {
        "kicker": "Verified feature",
        "problem": "The problem it solves",
        "capabilities": "What you can do",
        "inputs": "Supported inputs",
        "outputs": "Outputs",
        "options": "Available options",
        "steps": "Workflow",
        "limitations": "Limitations",
        "faq": "Common questions",
        "evidence": "Project evidence",
        "blog": "Read the related guide",
        "breadcrumb": "Breadcrumb",
    }


def blog_page_path(locale: str, source: str, slug: str = "") -> str:
    locale_part = "" if locale == source else f"{locale}/"
    return f"blog/{locale_part}{slug + '/' if slug else ''}index.html"


def relative_href(current_page: str, target_page: str) -> str:
    current_dir = posixpath.dirname(current_page)
    if target_page.endswith("index.html"):
        target_dir = posixpath.dirname(target_page)
        relative = posixpath.relpath(target_dir or ".", current_dir or ".")
        return "./" if relative == "." else relative.rstrip("/") + "/"
    return posixpath.relpath(target_page, current_dir or ".")


def blog_labels(locale: str, app_name: str) -> dict[str, str]:
    if locale.split("-")[0].lower() == "zh":
        return {
            "heading": f"{app_name} 功能指南",
            "intro": "基于当前应用真实功能整理的操作方法、使用场景与注意事项。",
            "topicNav": "功能主题",
            "latest": "功能文章",
            "latestIntro": "从具体任务出发，了解每项工具如何融入完整处理流程。",
            "read": "阅读文章",
            "guide": "功能指南",
            "tutorial": "操作教程",
            "contents": "本文目录",
            "related": "相关功能",
            "viewAll": "查看全部文章",
            "breadcrumb": "面包屑导航",
            "published": "发布于",
            "author": "发布机构",
            "overview": "教程概览",
            "difficulty": "难度",
            "easy": "入门",
            "steps": "步骤",
            "requirements": "准备事项",
            "android": "Android 设备与待处理文件",
            "prerequisites": "开始之前",
            "result": "检查结果",
            "limitations": "注意事项",
            "what": "这项功能解决什么问题",
            "workflow": "如何融入处理流程",
            "review": "导出前需要检查什么",
        }
    return {
        "heading": f"{app_name} feature guides",
        "intro": "Practical workflows, use cases, and limitations based on capabilities verified in the current app.",
        "topicNav": "Feature topics",
        "latest": "Feature articles",
        "latestIntro": "Start with a task and see how each tool fits into a complete processing workflow.",
        "read": "Read article",
        "guide": "Feature guide",
        "tutorial": "Tutorial",
        "contents": "On this page",
        "related": "Related features",
        "viewAll": "View all articles",
        "breadcrumb": "Breadcrumb",
        "published": "Published",
        "author": "Publisher",
        "overview": "Tutorial overview",
        "difficulty": "Difficulty",
        "easy": "Beginner",
        "steps": "Steps",
        "requirements": "Requirements",
        "android": "Android device and files to process",
        "prerequisites": "Before you begin",
        "result": "Review the result",
        "limitations": "What to keep in mind",
        "what": "What this feature helps you do",
        "workflow": "Where it fits in the workflow",
        "review": "What to check before export",
    }


def blog_article_text(
    locale: str,
    app_name: str,
    feature_name: str,
    description: str,
    details: dict,
) -> dict[str, str]:
    def sentences(key: str) -> str:
        values = [str(item).strip() for item in (details.get(key) or []) if isinstance(item, str) and item.strip()]
        return " ".join(values)

    problem = str(details.get("problem") or description)
    capabilities = sentences("capabilities")
    steps = sentences("steps")
    options = sentences("options")
    inputs = sentences("supportedInputs")
    outputs = sentences("supportedOutputs")
    limitations = sentences("limitations")
    if locale.split("-")[0].lower() == "zh":
        return {
            "standardTitle": f"{feature_name}：在 {app_name} 中能做什么",
            "tutorialTitle": f"如何在 {app_name} 中使用{feature_name}",
            "summary": f"{description} 了解它解决的问题、具体选项、真实操作步骤和已知限制。",
            "opening": problem,
            "what": capabilities,
            "workflow": steps,
            "review": options,
            "prerequisites": f"在已安装 {app_name} 的 Android 设备上准备以下输入：{inputs}",
            "result": f"该流程生成：{outputs}",
            "limitations": limitations,
        }
    return {
        "standardTitle": f"{feature_name}: what it does in {app_name}",
        "tutorialTitle": f"How to use {feature_name} in {app_name}",
        "summary": f"{description} Learn the exact problem, options, verified steps, and known limitations.",
        "opening": problem,
        "what": capabilities,
        "workflow": steps,
        "review": options,
        "prerequisites": f"On an Android device with {app_name} installed, prepare: {inputs}",
        "result": f"The workflow produces: {outputs}",
        "limitations": limitations,
    }


def render_feature_pages(
    app: dict,
    organization: dict,
    source: str,
    locales: list[str],
    contents: dict[str, dict],
    features: list[dict],
    assets: dict,
    stage: Path,
    base_url: str,
    theme_color: str,
    aliases: dict,
    auto_detect: bool,
    remember_selection: bool,
    copyright_text: str,
) -> list[str]:
    ready = content_ready_features(features)
    app_name = str(app.get("name") or "")
    package_name = str(app.get("packageName") or "")
    icon = str(assets.get("icon") or "")
    screenshots = assets.get("screenshots") or []
    generated: list[str] = []

    def list_html(values: object, ordered: bool = False) -> str:
        items = [str(item) for item in (values or []) if isinstance(item, str) and item.strip()]
        tag = "ol" if ordered else "ul"
        return f"<{tag}>" + "".join(f"<li>{esc(item)}</li>" for item in items) + f"</{tag}>"

    for locale in locales:
        content = contents[locale]
        labels = feature_labels(locale)
        for index, feature in enumerate(ready):
            feature_id = str(feature["id"])
            name = str(nested(content, f"home.features.{feature_id}.name", feature.get("name") or feature_id))
            description = str(nested(content, f"home.features.{feature_id}.description", feature.get("description") or ""))
            details = localized_feature_details(content, feature)
            slug = feature_slug(locale, source, content, feature)
            current_page = feature_page_path(locale, source, slug)
            page_dir = stage / Path(current_page).parent
            page_dir.mkdir(parents=True, exist_ok=True)

            routes = []
            alternate_tags = []
            for target in locales:
                target_slug = feature_slug(target, source, contents[target], feature)
                target_page = feature_page_path(target, source, target_slug)
                target_url = urljoin(base_url, target_page.removesuffix("index.html")) if base_url else relative_href(current_page, target_page)
                routes.append({"code": target, "url": target_url})
                if base_url:
                    alternate_tags.append(f'<link rel="alternate" hreflang="{esc(target)}" href="{esc(target_url)}">')
            canonical_url = urljoin(base_url, current_page.removesuffix("index.html")) if base_url else ""
            canonical = ""
            if base_url:
                source_slug = feature_slug(source, source, contents[source], feature)
                source_url = urljoin(base_url, feature_page_path(source, source, source_slug).removesuffix("index.html"))
                canonical = f'<link rel="canonical" href="{esc(canonical_url)}">\n  ' + "\n  ".join(alternate_tags)
                canonical += f'\n  <link rel="alternate" hreflang="x-default" href="{esc(source_url)}">'
            route_config = {
                "sourceLocale": source,
                "currentLocale": locale,
                "autoRedirect": locale == source and auto_detect,
                "rememberSelection": remember_selection,
                "storageKey": f"{package_name}:locale",
                "aliases": aliases,
                "locales": routes,
            }
            options = "".join(
                f'<option value="{esc(target)}">{esc(contents[target]["languageName"])}</option>' for target in locales
            )
            language_label = esc(nested(content, "navigation.language", "Language"))
            switcher = (
                f'<label class="language-picker"><span class="visually-hidden">{language_label}</span>'
                f'<select data-locale-switcher aria-label="{language_label}">{options}</select></label>'
            )

            home_page = "index.html" if locale == source else f"{locale}/index.html"
            blog_index = blog_page_path(locale, source)
            privacy_page = "privacy.html" if locale == source else f"{locale}/privacy.html"
            support_page = "support.html" if locale == source else f"{locale}/support.html"
            about_page = "about.html" if locale == source else f"{locale}/about.html"
            blog_slug = slugify(feature_id if locale == source else name, feature_id)
            blog_article = blog_page_path(locale, source, blog_slug)
            screenshot = screenshots[min(index + 1, len(screenshots) - 1)] if screenshots else {}
            image_path = str(screenshot.get("path") or "")
            media = ""
            if image_path:
                media = (
                    f'<figure class="feature-media"><img src="{esc(relative_href(current_page, image_path))}" '
                    f'alt="{esc(description)}" loading="eager"><figcaption>{esc(description)}</figcaption></figure>'
                )
            faq_items = [item for item in (details.get("faq") or []) if isinstance(item, dict)]
            faq_html = "".join(
                f'<details><summary>{esc(item.get("question"))}</summary><p>{esc(item.get("answer"))}</p></details>'
                for item in faq_items
            )
            graph: list[dict[str, object]] = [
                {
                    "@type": "WebPage",
                    "name": name,
                    "description": description,
                    "mainEntity": {"@id": f"{canonical_url}#app" if canonical_url else f"#{feature_id}-app"},
                },
                {
                    "@type": "SoftwareApplication",
                    "@id": f"{canonical_url}#app" if canonical_url else f"#{feature_id}-app",
                    "name": app_name,
                    "operatingSystem": "Android",
                    "featureList": [str(item) for item in details.get("capabilities") or []],
                },
            ]
            if canonical_url:
                graph[0]["url"] = canonical_url
            if faq_items:
                graph.append({
                    "@type": "FAQPage",
                    "mainEntity": [
                        {
                            "@type": "Question",
                            "name": str(item.get("question") or ""),
                            "acceptedAnswer": {"@type": "Answer", "text": str(item.get("answer") or "")},
                        }
                        for item in faq_items
                    ],
                })
            org = organization_entity(organization)
            if org:
                graph.append(org)
            structured = '<script type="application/ld+json">' + json.dumps(
                {"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":")
            ).replace("</", "<\\/") + "</script>"
            breadcrumbs = (
                f'<a href="{esc(relative_href(current_page, home_page))}">{esc(nested(content, "navigation.home"))}</a>'
                f'<span aria-hidden="true">/</span><a href="{esc(relative_href(current_page, home_page) + "#features")}">'
                f'{esc(nested(content, "navigation.features"))}</a>'
            )
            brand_logo = f'<img src="{esc(relative_href(current_page, icon))}" alt="" width="40" height="40">' if icon else ""
            open_graph = ""
            if base_url:
                open_graph = "\n  ".join([
                    '<meta property="og:type" content="website">',
                    f'<meta property="og:title" content="{esc(name)}">',
                    f'<meta property="og:description" content="{esc(description)}">',
                    f'<meta property="og:url" content="{esc(canonical_url)}">',
                ])
            values = {
                "LANG": esc(locale), "TEXT_DIRECTION": esc(content["direction"]),
                "PAGE_TITLE": esc(f"{name} - {app_name}"), "META_DESCRIPTION": esc(description),
                "THEME_COLOR": theme_color, "CANONICAL_TAGS": canonical, "OPEN_GRAPH_TAGS": open_graph,
                "SITE_BASE_PATH": esc(relative_href(current_page, "index.html")), "STRUCTURED_DATA": structured,
                "LOCALE_ROUTES_JSON": json.dumps(route_config, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"),
                "LANGUAGE_SWITCHER": switcher, "SKIP_TO_CONTENT": esc(nested(content, "common.skipToContent")),
                "HOME_URL": esc(relative_href(current_page, home_page)), "BLOG_URL": esc(relative_href(current_page, blog_index)),
                "BLOG_NAV_ITEM": f'<a href="{esc(relative_href(current_page, blog_index))}">{esc(nested(content, "navigation.blog", "Blog"))}</a>',
                "ABOUT_URL": esc(relative_href(current_page, about_page)), "SUPPORT_URL": esc(relative_href(current_page, support_page)),
                "PRIVACY_URL": esc(relative_href(current_page, privacy_page)), "APP_NAME": esc(app_name), "BRAND_LOGO": brand_logo,
                "PRIMARY_NAV_LABEL": esc(nested(content, "navigation.primaryLabel")), "FOOTER_NAV_LABEL": esc(nested(content, "navigation.footerLabel")),
                "NAV_HOME": esc(nested(content, "navigation.home")), "NAV_BLOG": esc(nested(content, "navigation.blog", "Blog")),
                "NAV_ABOUT": esc(nested(content, "navigation.about", organization_labels(locale)["pageTitle"])),
                "NAV_SUPPORT": esc(nested(content, "navigation.support")), "NAV_PRIVACY": esc(nested(content, "navigation.privacy")),
                "BREADCRUMB_LABEL": esc(labels["breadcrumb"]), "BREADCRUMBS": breadcrumbs,
                "FEATURE_KICKER": esc(labels["kicker"]), "FEATURE_NAME": esc(name), "FEATURE_DESCRIPTION": esc(description),
                "PROBLEM_HEADING": esc(labels["problem"]), "PROBLEM": esc(details.get("problem")), "FEATURE_MEDIA": media,
                "CAPABILITIES_HEADING": esc(labels["capabilities"]), "CAPABILITIES": list_html(details.get("capabilities")),
                "OPTIONS_HEADING": esc(labels["options"]), "OPTIONS": list_html(details.get("options")),
                "INPUTS_HEADING": esc(labels["inputs"]), "INPUTS": list_html(details.get("supportedInputs")),
                "OUTPUTS_HEADING": esc(labels["outputs"]), "OUTPUTS": list_html(details.get("supportedOutputs")),
                "STEPS_HEADING": esc(labels["steps"]), "STEPS": list_html(details.get("steps"), ordered=True),
                "LIMITATIONS_HEADING": esc(labels["limitations"]), "LIMITATIONS": list_html(details.get("limitations")),
                "FAQ_HEADING": esc(labels["faq"]), "FAQ": faq_html,
                "EVIDENCE_HEADING": esc(labels["evidence"]),
                "EVIDENCE": '<ul class="evidence-list">' + "".join(f"<li><code>{esc(item)}</code></li>" for item in feature.get("evidence") or []) + "</ul>",
                "BLOG_ARTICLE_URL": esc(relative_href(current_page, blog_article)), "BLOG_LABEL": esc(labels["blog"]),
                "COPYRIGHT_TEXT": copyright_text.replace(esc(nested(contents[source], "common.rights")), esc(nested(content, "common.rights"))),
            }
            (stage / current_page).write_text(render_template("feature.html", values), encoding="utf-8")
            generated.append(current_page)
    return generated


def render_blog(
    app: dict,
    organization: dict,
    source: str,
    locales: list[str],
    contents: dict[str, dict],
    features: list[dict],
    assets: dict,
    stage: Path,
    base_url: str,
    theme_color: str,
    aliases: dict,
    auto_detect: bool,
    remember_selection: bool,
) -> list[str]:
    if not content_ready_features(features):
        content_root = stage / "content" / "blog"
        content_root.mkdir(parents=True, exist_ok=True)
        (content_root / "content-plan.yaml").write_text(
            yaml.safe_dump({"schemaVersion": "1.0", "app": str(app.get("name") or ""), "topics": []}, sort_keys=False),
            encoding="utf-8",
        )
        return []
    app_name = str(app.get("name") or "")
    package_name = str(app.get("packageName") or "")
    date = str(nested(app, "editorial.publishedAt", "") or "").strip()
    updated_date = str(nested(app, "editorial.updatedAt", "") or date).strip()
    copyright_date = str(nested(app, "analysis.validatedAt", "") or app.get("analyzedAt") or "")
    year = (re.search(r"\b(20\d{2})\b", copyright_date).group(1) if re.search(r"\b(20\d{2})\b", copyright_date) else "")
    publisher = str(organization.get("legalName") or nested(app, "developer.name", "") or app_name)
    icon = str(assets.get("icon") or "")
    screenshots = assets.get("screenshots") or []
    models: dict[str, list[dict]] = {}
    for locale in locales:
        feature_content = nested(contents[locale], "home.features", {}) or {}
        locale_models = []
        for index, feature in enumerate(content_ready_features(features)):
            feature_id = str(feature.get("id") or f"feature-{index + 1}")
            translated = feature_content.get(feature_id) or {}
            name = str(translated.get("name") or feature.get("name") or feature_id)
            description = str(translated.get("description") or feature.get("description") or "")
            details = localized_feature_details(contents[locale], feature)
            text = blog_article_text(locale, app_name, name, description, details)
            template = str(nested(feature, "blog.template", feature.get("blogTemplate", "standard-article")))
            if template not in {"standard-article", "tutorial"}:
                template = "standard-article"
            title = text["tutorialTitle"] if template == "tutorial" else text["standardTitle"]
            slug_source = feature_id if locale == source else name
            screenshot = screenshots[min(index + 1, len(screenshots) - 1)] if screenshots else {}
            locale_models.append({
                "contentId": feature_id,
                "slug": slugify(slug_source, feature_id),
                "title": title,
                "summary": text["summary"],
                "description": description,
                "template": template,
                "text": text,
                "details": details,
                "evidence": [str(item) for item in (feature.get("evidence") or [])],
                "image": str(screenshot.get("path") or ""),
            })
        models[locale] = locale_models

    def model_for(locale: str, content_id: str) -> dict:
        return next(item for item in models[locale] if item["contentId"] == content_id)

    def routes(current: str, content_id: str | None, current_page: str) -> tuple[str, str, str]:
        route_items = []
        canonical_lines = []
        for locale in locales:
            slug = model_for(locale, content_id)["slug"] if content_id else ""
            target_page = blog_page_path(locale, source, slug)
            url = urljoin(base_url, target_page.removesuffix("index.html")) if base_url else relative_href(current_page, target_page)
            route_items.append({"code": locale, "url": url})
            if base_url:
                canonical_lines.append(f'<link rel="alternate" hreflang="{esc(locale)}" href="{esc(url)}">')
        current_slug = model_for(current, content_id)["slug"] if content_id else ""
        canonical_page = blog_page_path(current, source, current_slug)
        canonical_url = urljoin(base_url, canonical_page.removesuffix("index.html")) if base_url else ""
        tags = f'<link rel="canonical" href="{esc(canonical_url)}">\n  ' + "\n  ".join(canonical_lines) if base_url else ""
        if base_url:
            source_slug = model_for(source, content_id)["slug"] if content_id else ""
            source_url = urljoin(base_url, blog_page_path(source, source, source_slug).removesuffix("index.html"))
            tags += f'\n  <link rel="alternate" hreflang="x-default" href="{esc(source_url)}">'
        config = {
            "sourceLocale": source,
            "currentLocale": current,
            "autoRedirect": current == source and auto_detect,
            "rememberSelection": remember_selection,
            "storageKey": f"{package_name}:locale",
            "aliases": aliases,
            "locales": route_items,
        }
        options = "".join(
            f'<option value="{esc(locale)}">{esc(contents[locale]["languageName"])}</option>' for locale in locales
        )
        label = esc(nested(contents[current], "navigation.language", "Language"))
        switcher = (
            f'<label class="language-picker"><span class="visually-hidden">{label}</span>'
            f'<select data-locale-switcher aria-label="{label}">{options}</select></label>'
        )
        return switcher, json.dumps(config, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"), tags

    shutil.copy2(BLOG_TEMPLATE_ROOT / "assets" / "blog.css", stage / "assets" / "blog.css")
    shutil.copy2(BLOG_TEMPLATE_ROOT / "assets" / "blog.js", stage / "assets" / "blog.js")
    generated: list[str] = []
    plan_topics = []
    localization = {"sourceLocale": source, "locales": []}

    for locale in locales:
        labels = blog_labels(locale, app_name)
        locale_models = models[locale]
        localization["locales"].append({
            "locale": locale,
            "status": "source" if locale == source else str(contents[locale].get("reviewStatus") or "machine-draft"),
        })
        index_page = blog_page_path(locale, source)
        index_dir = stage / Path(index_page).parent
        index_dir.mkdir(parents=True, exist_ok=True)
        switcher, route_json, canonical = routes(locale, None, index_page)
        home_page = "index.html" if locale == source else f"{locale}/index.html"
        privacy_page = "privacy.html" if locale == source else f"{locale}/privacy.html"
        support_page = "support.html" if locale == source else f"{locale}/support.html"
        about_page = "about.html" if locale == source else f"{locale}/about.html"
        featured = locale_models[0]
        featured_page = blog_page_path(locale, source, featured["slug"])

        def card(item: dict) -> str:
            target = blog_page_path(locale, source, item["slug"])
            image_html = ""
            if item["image"]:
                image_html = (
                    f'<a href="{esc(relative_href(index_page, target))}"><img src="{esc(relative_href(index_page, item["image"]))}" '
                    f'alt="{esc(item["title"])}" width="720" height="450" loading="lazy"></a>'
                )
            return (
                f'<article class="article-card">{image_html}<div class="article-card-content">'
                f'<p class="article-kicker">{esc(labels["tutorial"] if item["template"] == "tutorial" else labels["guide"])}</p>'
                f'<h3><a href="{esc(relative_href(index_page, target))}">{esc(item["title"])}</a></h3>'
                f'<p>{esc(item["summary"])}</p><div class="article-meta">{esc((date + " · ") if date else "")}{esc(publisher)}</div></div></article>'
            )

        collection = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": labels["heading"],
            "description": labels["intro"],
            "hasPart": [{"@type": "Article", "name": item["title"]} for item in locale_models],
        }
        index_values = {
            "LANG": esc(locale), "TEXT_DIRECTION": esc(contents[locale]["direction"]),
            "PAGE_TITLE": esc(f'{labels["heading"]} - {app_name}'), "META_DESCRIPTION": esc(labels["intro"]),
            "THEME_COLOR": theme_color, "CANONICAL_TAGS": canonical, "OPEN_GRAPH_TAGS": "",
            "SITE_BASE_PATH": relative_href(index_page, "index.html"),
            "COLLECTION_STRUCTURED_DATA": '<script type="application/ld+json">' + json.dumps(collection, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>",
            "LOCALE_ROUTES_JSON": route_json, "LANGUAGE_SWITCHER": switcher,
            "SKIP_TO_CONTENT": esc(nested(contents[locale], "common.skipToContent")),
            "HOME_URL": relative_href(index_page, home_page), "BLOG_URL": "./",
            "ABOUT_URL": relative_href(index_page, about_page), "SUPPORT_URL": relative_href(index_page, support_page),
            "PRIVACY_URL": relative_href(index_page, privacy_page), "APP_NAME": esc(app_name),
            "LOGO_PATH": esc(relative_href(index_page, icon)) if icon else "",
            "PRIMARY_NAV_LABEL": esc(nested(contents[locale], "navigation.primaryLabel")),
            "FOOTER_NAV_LABEL": esc(nested(contents[locale], "navigation.footerLabel")),
            "NAV_HOME": esc(nested(contents[locale], "navigation.home")),
            "NAV_BLOG": esc(nested(contents[locale], "navigation.blog", "Blog")),
            "NAV_ABOUT": esc(nested(contents[locale], "navigation.about", organization_labels(locale)["pageTitle"])),
            "NAV_SUPPORT": esc(nested(contents[locale], "navigation.support")),
            "NAV_PRIVACY": esc(nested(contents[locale], "navigation.privacy")),
            "BLOG_HEADING": esc(labels["heading"]), "BLOG_INTRO": esc(labels["intro"]),
            "TOPIC_NAV_LABEL": esc(labels["topicNav"]),
            "CATEGORY_LINKS": "".join(f'<a href="{esc(relative_href(index_page, blog_page_path(locale, source, item["slug"])))}">{esc(item["title"])}</a>' for item in locale_models),
            "FEATURED_IMAGE_PATH": esc(relative_href(index_page, featured["image"])) if featured["image"] else esc(relative_href(index_page, icon)),
            "FEATURED_IMAGE_ALT": esc(featured["title"]),
            "FEATURED_CATEGORY": esc(labels["tutorial"] if featured["template"] == "tutorial" else labels["guide"]),
            "FEATURED_TITLE": esc(featured["title"]), "FEATURED_SUMMARY": esc(featured["summary"]),
            "FEATURED_META": esc(f"{date} · {publisher}" if date else publisher), "FEATURED_URL": esc(relative_href(index_page, featured_page)),
            "READ_ARTICLE_LABEL": esc(labels["read"]), "LATEST_HEADING": esc(labels["latest"]),
            "LATEST_INTRO": esc(labels["latestIntro"]), "ARTICLE_CARDS": "".join(card(item) for item in locale_models[1:]),
            "PAGINATION": "", "YEAR": esc(year), "DEVELOPER_NAME": esc(publisher),
            "RIGHTS_TEXT": esc(nested(contents[locale], "common.rights")),
        }
        (stage / index_page).write_text(render_blog_template("index.html", index_values), encoding="utf-8")
        generated.append(index_page)

        for item in locale_models:
            article_page = blog_page_path(locale, source, item["slug"])
            article_dir = stage / Path(article_page).parent
            article_dir.mkdir(parents=True, exist_ok=True)
            switcher, route_json, canonical = routes(locale, item["contentId"], article_page)
            blog_index = blog_page_path(locale, source)
            screenshot_path = relative_href(article_page, item["image"]) if item["image"] else ""
            hero = (
                f'<figure class="article-hero"><img src="{esc(screenshot_path)}" alt="{esc(item["title"])}" loading="eager">'
                f'<figcaption>{esc(item["description"])}</figcaption></figure>' if screenshot_path else ""
            )
            related = [other for other in locale_models if other["contentId"] != item["contentId"]][:2]

            def related_card(other: dict) -> str:
                target = blog_page_path(locale, source, other["slug"])
                return (
                    '<article class="article-card"><div class="article-card-content">'
                    f'<p class="article-kicker">{esc(labels["guide"])}</p><h3><a href="{esc(relative_href(article_page, target))}">{esc(other["title"])}</a></h3>'
                    f'<p>{esc(other["summary"])}</p></div></article>'
                )

            meta = esc(
                f'{labels["published"]} {date} · {labels["author"]} {publisher}'
                if date else f'{labels["author"]} {publisher}'
            )
            breadcrumbs = (
                f'<a href="{esc(relative_href(article_page, home_page))}">{esc(nested(contents[locale], "navigation.home"))}</a>'
                f'<span aria-hidden="true">/</span><a href="{esc(relative_href(article_page, blog_index))}">{esc(nested(contents[locale], "navigation.blog", "Blog"))}</a>'
            )
            organization_data = organization_entity(organization)
            article_data: dict[str, object] = {
                "@context": "https://schema.org", "@type": "Article", "headline": item["title"],
                "description": item["summary"],
                "about": {"@type": "SoftwareApplication", "name": app_name, "operatingSystem": "Android"},
            }
            if date:
                article_data["datePublished"] = date
                article_data["dateModified"] = updated_date or date
            if organization_data:
                article_data["author"] = {"@id": organization_data["@id"]}
                article_data["publisher"] = {"@id": organization_data["@id"]}
            structured = (
                '<script type="application/ld+json">' + json.dumps(article_data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>"
                if date else ""
            )
            common = {
                "LANG": esc(locale), "TEXT_DIRECTION": esc(contents[locale]["direction"]),
                "PAGE_TITLE": esc(f'{item["title"]} - {app_name}'), "META_DESCRIPTION": esc(item["summary"]),
                "THEME_COLOR": theme_color, "CANONICAL_TAGS": canonical, "OPEN_GRAPH_TAGS": "",
                "SITE_BASE_PATH": relative_href(article_page, "index.html"), "LOCALE_ROUTES_JSON": route_json,
                "LANGUAGE_SWITCHER": switcher, "SKIP_TO_CONTENT": esc(nested(contents[locale], "common.skipToContent")),
                "HOME_URL": relative_href(article_page, home_page), "BLOG_URL": relative_href(article_page, blog_index),
                "ABOUT_URL": relative_href(article_page, about_page), "SUPPORT_URL": relative_href(article_page, support_page),
                "PRIVACY_URL": relative_href(article_page, privacy_page), "APP_NAME": esc(app_name),
                "LOGO_PATH": esc(relative_href(article_page, icon)) if icon else "",
                "PRIMARY_NAV_LABEL": esc(nested(contents[locale], "navigation.primaryLabel")),
                "FOOTER_NAV_LABEL": esc(nested(contents[locale], "navigation.footerLabel")),
                "NAV_HOME": esc(nested(contents[locale], "navigation.home")),
                "NAV_BLOG": esc(nested(contents[locale], "navigation.blog", "Blog")),
                "NAV_ABOUT": esc(nested(contents[locale], "navigation.about", organization_labels(locale)["pageTitle"])),
                "NAV_SUPPORT": esc(nested(contents[locale], "navigation.support")),
                "NAV_PRIVACY": esc(nested(contents[locale], "navigation.privacy")),
                "ARTICLE_TITLE": esc(item["title"]), "ARTICLE_SUMMARY": esc(item["summary"]),
                "ARTICLE_META": meta, "ARTICLE_HERO_MEDIA": hero,
                "BREADCRUMB_LABEL": esc(labels["breadcrumb"]), "BREADCRUMBS": breadcrumbs,
                "TABLE_OF_CONTENTS_LABEL": esc(labels["contents"]),
                "RELATED_HEADING": esc(labels["related"]), "VIEW_ALL_LABEL": esc(labels["viewAll"]),
                "RELATED_ARTICLE_CARDS": "".join(related_card(other) for other in related),
                "YEAR": esc(year), "DEVELOPER_NAME": esc(publisher),
                "RIGHTS_TEXT": esc(nested(contents[locale], "common.rights")),
            }
            text_data = item["text"]
            details = item["details"]
            if item["template"] == "tutorial":
                workflow_steps = [str(step) for step in (details.get("steps") or []) if str(step).strip()]
                steps_html = "".join(
                    f'<section class="tutorial-step" id="step-{number}"><span class="tutorial-step-number" aria-hidden="true">{number}</span>'
                    f'<h2>{esc(step)}</h2></section>'
                    for number, step in enumerate(workflow_steps, start=1)
                )
                toc = "".join(f'<a href="#step-{number}">{esc(step)}</a>' for number, step in enumerate(workflow_steps, start=1))
                howto = dict(article_data)
                howto["@type"] = "HowTo"
                howto["step"] = [{"@type": "HowToStep", "position": number, "name": step} for number, step in enumerate(workflow_steps, start=1)]
                tutorial_values = merge(common, {
                    "HOW_TO_STRUCTURED_DATA": (
                        '<script type="application/ld+json">' + json.dumps(howto, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>"
                        if date else ""
                    ),
                    "TUTORIAL_LABEL": esc(labels["tutorial"]), "TUTORIAL_OVERVIEW_LABEL": esc(labels["overview"]),
                    "DIFFICULTY_LABEL": esc(labels["difficulty"]), "DIFFICULTY_VALUE": esc(labels["easy"]),
                    "STEPS_LABEL": esc(labels["steps"]), "STEPS_VALUE": str(len(workflow_steps)),
                    "REQUIREMENTS_LABEL": esc(labels["requirements"]), "REQUIREMENTS_VALUE": esc(labels["android"]),
                    "PREREQUISITES_HEADING": esc(labels["prerequisites"]),
                    "PREREQUISITES_CONTENT": '<ul>' + "".join(f'<li>{esc(value)}</li>' for value in details.get("supportedInputs") or []) + '</ul>',
                    "TABLE_OF_CONTENTS": toc, "TUTORIAL_STEPS": steps_html,
                    "RESULT_HEADING": esc(labels["result"]),
                    "RESULT_CONTENT": '<ul>' + "".join(f'<li>{esc(value)}</li>' for value in details.get("supportedOutputs") or []) + '</ul>',
                    "LIMITATIONS_SECTION": f'<section id="limitations"><h2>{esc(labels["limitations"])}</h2><ul>'
                    + "".join(f'<li>{esc(value)}</li>' for value in details.get("limitations") or []) + '</ul></section>',
                })
                rendered = render_blog_template("tutorial.html", tutorial_values)
            else:
                sections = [
                    ("what", labels["what"], details.get("capabilities") or [], "ul"),
                    ("workflow", labels["workflow"], details.get("steps") or [], "ol"),
                    ("review", labels["review"], details.get("options") or [], "ul"),
                    ("limitations", labels["limitations"], details.get("limitations") or [], "ul"),
                ]
                article_values = merge(common, {
                    "ARTICLE_STRUCTURED_DATA": structured, "ARTICLE_CATEGORY": esc(labels["guide"]),
                    "TABLE_OF_CONTENTS": "".join(f'<a href="#{anchor}">{esc(heading)}</a>' for anchor, heading, _, _ in sections),
                    "ARTICLE_BODY": f'<p>{esc(text_data["opening"])}</p>' + "".join(
                        f'<section id="{anchor}"><h2>{esc(heading)}</h2><{tag}>'
                        + "".join(f'<li>{esc(value)}</li>' for value in values)
                        + f'</{tag}></section>' for anchor, heading, values, tag in sections
                    ),
                })
                rendered = render_blog_template("article.html", article_values)
            (stage / article_page).write_text(rendered, encoding="utf-8")
            generated.append(article_page)

            markdown_status = "draft" if locale == source else "machine-draft"
            frontmatter = {
                "contentId": item["contentId"], "locale": locale, "status": markdown_status,
                "title": item["title"], "description": item["summary"], "slug": item["slug"],
                "intent": "feature education", "audience": "app users", "canonical": "", "evidence": item["evidence"],
                "primaryKeyword": item["title"], "relatedPages": ["/", "/support.html"],
                "template": item["template"],
            }
            if date:
                frontmatter["publishedAt"] = date
                frontmatter["updatedAt"] = updated_date or date
            markdown = "---\n" + yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False) + "---\n\n"
            markdown += f'# {item["title"]}\n\n{item["text"]["opening"]}\n\n'
            for heading, key in ((labels["what"], "capabilities"), (labels["workflow"], "steps"), (labels["review"], "options"), (labels["limitations"], "limitations")):
                markdown += f'## {heading}\n\n' + "".join(f'- {value}\n' for value in details.get(key) or []) + "\n"
            source_path = stage / "content" / "blog" / locale / f'{item["slug"]}.md'
            source_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.write_text(markdown, encoding="utf-8")
            if locale == source:
                plan_topics.append({
                    "contentId": item["contentId"], "title": item["title"], "template": item["template"],
                    "status": "draft", "evidence": item["evidence"],
                })

    content_root = stage / "content" / "blog"
    (content_root / "content-plan.yaml").write_text(
        yaml.safe_dump({"schemaVersion": "1.0", "app": app_name, "topics": plan_topics}, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    (content_root / "localization-status.yaml").write_text(
        yaml.safe_dump(localization, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    return generated


def write_launch_artifacts(
    app: dict,
    organization: dict,
    source: str,
    locales: list[str],
    contents: dict[str, dict],
    features: list[dict],
    assets: dict,
    stage: Path,
    base_url: str,
) -> None:
    """Write editable ASO and SEO/GEO briefs plus an explicit release gate."""
    ready = content_ready_features(features)
    ready_ids = {str(feature["id"]) for feature in ready}
    app_name = str(app.get("name") or "")
    google_play_url = str(app.get("googlePlayUrl") or "").strip()
    publisher = str(organization.get("legalName") or nested(app, "developer.name", "") or app_name)
    screenshots = assets.get("screenshots") or []

    aso_root = stage / "aso"
    seo_root = stage / "seo-geo"
    aso_root.mkdir(parents=True, exist_ok=True)
    (seo_root / "structured-data").mkdir(parents=True, exist_ok=True)
    localization_rows = []
    metadata_by_locale: dict[str, dict] = {}
    page_map = []
    keyword_rows: list[list[str]] = [["locale", "page", "primary_query", "supporting_queries", "intent", "status"]]
    internal_rows: list[list[str]] = [["locale", "source", "target", "anchor", "reason"]]

    for locale in locales:
        content = contents[locale]
        locale_dir = aso_root / locale
        locale_dir.mkdir(parents=True, exist_ok=True)
        localized_features = nested(content, "home.features", {}) or {}
        detail_sections = []
        for feature in ready:
            feature_id = str(feature["id"])
            localized = localized_features[feature_id]
            details = localized_feature_details(content, feature)
            detail_sections.append(
                f'{localized["name"]}: {localized["description"]} '
                + " ".join(str(item) for item in details.get("capabilities") or [])
            )
        short_candidates = [
            str(nested(app, "description.short", "")) if locale == source else "",
            str(nested(content, "home.metaDescription", "")),
            str(nested(content, "home.shortDescription", "")),
            app_name,
        ]
        short_description = next(
            (candidate for candidate in short_candidates if candidate and len(candidate) <= 80),
            app_name,
        )
        full_description = "\n\n".join([
            str(nested(content, "home.shortDescription", "")),
            *detail_sections,
            str(nested(content, "home.closingCopy", "")),
        ])
        listing = {
            "schemaVersion": "1.0",
            "locale": locale,
            "status": "draft",
            "appName": app_name,
            "shortDescription": short_description,
            "fullDescription": full_description,
            "characterCounts": {
                "appName": len(app_name),
                "shortDescription": len(short_description),
                "fullDescription": len(full_description),
            },
            "limits": {"appName": 30, "shortDescription": 80, "fullDescription": 4000},
            "googlePlayUrl": google_play_url,
        }
        violations = [
            field for field, limit in (("appName", 30), ("shortDescription", 80), ("fullDescription", 4000))
            if len(str(listing[field])) > limit
        ]
        listing["validation"] = {"valid": not violations, "violations": violations}
        (locale_dir / "listing.yaml").write_text(
            yaml.safe_dump(listing, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
        screenshot_plan = {
            "schemaVersion": "1.0",
            "locale": locale,
            "status": "draft",
            "items": [
                {
                    "position": index,
                    "asset": str(item.get("path") or ""),
                    "screen": str(item.get("screen") or ""),
                    "caption": str(item.get("caption") or nested(content, "home.heroScreenshotCaption", "")),
                    "reviewRequired": locale != source or str(item.get("locale") or locale) != locale,
                }
                for index, item in enumerate(screenshots, start=1)
            ],
        }
        (locale_dir / "screenshots.yaml").write_text(
            yaml.safe_dump(screenshot_plan, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
        localization_rows.append({
            "locale": locale,
            "status": "source" if locale == source else str(content.get("reviewStatus") or "machine-draft"),
            "listingValid": not violations,
            "screenshotReviewRequired": any(item["reviewRequired"] for item in screenshot_plan["items"]),
        })

        locale_metadata: dict[str, dict] = {}
        home_path = "/" if locale == source else f"/{locale}/"
        locale_metadata[home_path] = {
            "title": str(nested(content, "home.pageTitle", "")),
            "description": short_description,
            "primaryQuery": seo_primary_query(locale, app),
        }
        page_map.append({"locale": locale, "path": home_path, "type": "home", "status": "blocked" if not base_url else "ready"})
        keyword_rows.append([locale, home_path, seo_primary_query(locale, app), app_name, "product discovery", "draft"])
        for feature in ready:
            feature_id = str(feature["id"])
            localized = localized_features[feature_id]
            details = localized_feature_details(content, feature)
            slug = feature_slug(locale, source, content, feature)
            feature_path = "/" + feature_page_path(locale, source, slug).removesuffix("index.html")
            blog_slug = slugify(feature_id if locale == source else str(localized["name"]), feature_id)
            article_path = "/" + blog_page_path(locale, source, blog_slug).removesuffix("index.html")
            queries = [str(item) for item in details.get("searchIntents") or feature.get("details", {}).get("searchIntents") or []]
            primary_query = queries[0] if queries else str(localized["name"])
            locale_metadata[feature_path] = {
                "title": f'{localized["name"]} - {app_name}',
                "description": str(localized["description"]),
                "primaryQuery": primary_query,
            }
            page_map.extend([
                {"locale": locale, "path": feature_path, "type": "feature", "contentId": feature_id, "status": "blocked" if not base_url else "ready"},
                {"locale": locale, "path": article_path, "type": "guide", "contentId": feature_id, "status": "draft"},
            ])
            keyword_rows.append([locale, feature_path, primary_query, " | ".join(queries[1:]), "feature evaluation", "draft"])
            internal_rows.extend([
                [locale, home_path, feature_path, str(localized["name"]), "home feature discovery"],
                [locale, feature_path, article_path, str(localized["name"]), "task education"],
                [locale, article_path, feature_path, str(localized["name"]), "feature verification"],
            ])
        metadata_by_locale[locale] = locale_metadata
        locale_seo_dir = seo_root / locale
        locale_seo_dir.mkdir(parents=True, exist_ok=True)
        (locale_seo_dir / "metadata.yaml").write_text(
            yaml.safe_dump({"schemaVersion": "1.0", "locale": locale, "pages": locale_metadata}, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        answer_lines = [f"# {app_name} answer brief ({locale})", ""]
        for feature in ready:
            feature_id = str(feature["id"])
            answer_lines.append(f'## {localized_features[feature_id]["name"]}')
            answer_lines.append("")
            answer_lines.append(str(localized_feature_details(content, feature).get("problem") or ""))
            answer_lines.append("")
            for item in localized_feature_details(content, feature).get("faq") or []:
                answer_lines.extend([f'### {item.get("question", "")}', "", str(item.get("answer") or ""), ""])
        (locale_seo_dir / "answers.md").write_text("\n".join(answer_lines), encoding="utf-8")

    (aso_root / "experiments.yaml").write_text(
        yaml.safe_dump({
            "schemaVersion": "1.0",
            "status": "planned",
            "experiments": [
                {"id": "short-description-value", "variable": "shortDescription", "metric": "store listing conversion", "requiresLiveListing": True},
                {"id": "screenshot-order", "variable": "firstThreeScreenshots", "metric": "store listing conversion", "requiresReleaseScreenshots": True},
            ],
        }, sort_keys=False), encoding="utf-8"
    )
    (aso_root / "localization-status.yaml").write_text(
        yaml.safe_dump({"schemaVersion": "1.0", "locales": localization_rows}, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    aso_status = "draft" if google_play_url else "blocked"
    (aso_root / "audit.md").write_text(
        "# ASO audit\n\n"
        f"Status: {aso_status}\n\n"
        f"- Google Play URL: {google_play_url or 'missing'}\n"
        f"- Locales: {', '.join(locales)}\n"
        f"- Content-ready features used: {len(ready)}\n"
        "- Listing text is a draft until product and language review are complete.\n",
        encoding="utf-8",
    )

    def csv_text(rows: list[list[str]]) -> str:
        buffer = io.StringIO(newline="")
        csv.writer(buffer, lineterminator="\n").writerows(rows)
        return buffer.getvalue()

    (seo_root / "keyword-map.csv").write_text(csv_text(keyword_rows), encoding="utf-8")
    (seo_root / "internal-links.csv").write_text(csv_text(internal_rows), encoding="utf-8")
    (seo_root / "page-map.yaml").write_text(
        yaml.safe_dump({"schemaVersion": "1.0", "pages": page_map}, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    entity_profile = {
        "schemaVersion": "1.0",
        "application": {
            "name": app_name,
            "packageName": str(app.get("packageName") or ""),
            "category": str(app.get("category") or ""),
            "operatingSystem": "Android",
            "verifiedFeatureIds": sorted(ready_ids),
        },
        "organization": organization,
        "claimConstraints": app.get("claimsToAvoid") or [],
    }
    (seo_root / "entity-profile.yaml").write_text(
        yaml.safe_dump(entity_profile, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    organization_json = organization_entity(organization)
    software_json = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": app_name,
        "operatingSystem": "Android",
        "applicationCategory": str(app.get("category") or "Application"),
        "description": str(nested(contents[source], "home.metaDescription", "")),
        "featureList": [str(nested(contents[source], f'home.features.{feature["id"]}.name', feature["id"])) for feature in ready],
    }
    if base_url:
        software_json["url"] = base_url
    if organization_json:
        software_json["publisher"] = {"@id": organization_json["@id"]}
        (seo_root / "structured-data" / "organization.json").write_text(
            json.dumps({"@context": "https://schema.org", **organization_json}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    (seo_root / "structured-data" / "software-application.json").write_text(
        json.dumps(software_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    seo_status = "draft" if base_url else "blocked"
    (seo_root / "audit.md").write_text(
        "# SEO and GEO audit\n\n"
        f"Status: {seo_status}\n\n"
        f"- Canonical website URL: {base_url or 'missing'}\n"
        f"- Planned pages: {len(page_map)}\n"
        f"- Content-ready features: {len(ready)}\n"
        "- Canonical, hreflang, Open Graph URLs, robots sitemap reference, and populated sitemap require websiteUrl.\n"
        "- FAQ answers and entity claims come from verified product facts; review machine-draft locales before publication.\n",
        encoding="utf-8",
    )

    locale_warnings = [
        f'{locale} content status is {contents[locale].get("reviewStatus") or "machine-draft"}'
        for locale in locales if locale != source and contents[locale].get("reviewStatus") != "reviewed"
    ]
    skipped = [str(feature.get("id") or "") for feature in features if str(feature.get("id") or "") not in ready_ids]
    warnings = []
    if not base_url:
        warnings.append("websiteUrl is missing; canonical URLs, hreflang URLs, Open Graph URLs, and sitemap locations are blocked")
    if not google_play_url:
        warnings.append("googlePlayUrl is missing; store CTA and live ASO validation are blocked")
    if not nested(app, "editorial.publishedAt", ""):
        warnings.append("editorial.publishedAt is missing; blog pages remain drafts and omit Article/HowTo date markup")
    warnings.extend(locale_warnings)
    readiness = {
        "schemaVersion": "1.0",
        "website": {"status": "generated", "entry": "index.html", "output": "."},
        "content": {"verifiedFeatures": len(features), "readyFeatures": len(ready), "skippedFeatures": skipped},
        "seoGeo": {"status": seo_status, "websiteUrl": base_url},
        "aso": {"status": aso_status, "googlePlayUrl": google_play_url},
        "localization": localization_rows,
        "publishReady": bool(base_url and google_play_url and not locale_warnings),
        "warnings": warnings,
    }
    (stage / "launch-readiness.yaml").write_text(
        yaml.safe_dump(readiness, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )


def render_site(
    app: dict,
    organization: dict,
    app_info_path: Path,
    locales_root: Path,
    stage: Path,
) -> list[str]:
    if nested(app, "analysis.status") != "verified":
        raise GenerationError("analysis.status must be verified before public website generation")
    features = verified_features(app)
    if not features:
        raise GenerationError("at least one feature with confidence: verified and evidence is required")

    source, targets, contents = resolve_locales(app, locales_root, features)
    locales = [source, *targets]
    assets = copy_assets(app, app_info_path, stage)
    aliases = nested(app, "languages.routing.aliases", {}) or {}
    if not isinstance(aliases, dict):
        raise GenerationError("languages.routing.aliases must be a mapping")
    locale_keys = {locale.lower() for locale in locales}
    for alias, destination in aliases.items():
        if not isinstance(alias, str) or not isinstance(destination, str):
            raise GenerationError("language aliases must map locale strings to locale strings")
        if destination.lower() not in locale_keys:
            raise GenerationError(f"language alias {alias} points to unavailable locale {destination}")
    if nested(app, "languages.routing.sourceAtRoot", True) is False:
        raise GenerationError("languages.routing.sourceAtRoot must be true for root-level index.html output")
    auto_detect = nested(app, "languages.routing.autoDetect", True) is not False
    remember_selection = nested(app, "languages.routing.rememberSelection", True) is not False
    website_url = str(app.get("websiteUrl") or "").strip()
    video_url = str(app.get("videoUrl") or "").strip()
    if video_url:
        youtube_embed_url(video_url)
    base_url = website_url.rstrip("/") + "/" if website_url else ""
    package_name = str(app.get("packageName") or "")
    app_name = str(app.get("name") or "")
    version_name = str(nested(app, "version.name", "") or "")
    developer_name = str(organization.get("legalName") or nested(app, "developer.name", "") or app_name)
    support_email = str(
        nested(app, "support.email", "")
        or organization.get("supportEmail")
        or nested(app, "developer.email", "")
        or organization.get("email")
        or ""
    )
    theme_color = "#006b5f"
    colors = nested(app, "brand.colors", []) or []
    if colors and isinstance(colors[0], str) and re.fullmatch(r"#[0-9a-fA-F]{6}", colors[0]):
        theme_color = colors[0]
    date = str(nested(app, "analysis.validatedAt", "") or app.get("analyzedAt") or "Not provided")
    year_match = re.search(r"\b(20\d{2})\b", date)
    copyright_text = f"&copy; {year_match.group(1)} {esc(developer_name)}. " if year_match else f"&copy; {esc(developer_name)}. "
    copyright_text += esc(nested(contents[source], "common.rights"))

    icon_relative = assets.get("icon")
    hero_relative = assets.get("coverImage") or assets["screenshots"][0]["path"]
    social_relative = assets.get("socialImage")
    generated_pages: list[str] = []
    has_blog = bool(content_ready_features(features))

    for locale in locales:
        content = contents[locale]
        locale_dir = stage if locale == source else stage / locale
        locale_dir.mkdir(parents=True, exist_ok=True)
        base_path = "" if locale == source else "../"
        brand_logo = (
            f'<img src="{esc(base_path + str(icon_relative))}" alt="" width="40" height="40">'
            if icon_relative
            else ""
        )
        primary_action = (
            f'<a class="primary-action google-play-action" href="{esc(app["googlePlayUrl"])}">'
            f'<img class="google-play-badge" src="{esc(base_path + str(assets["googlePlayBadge"]))}" '
            f'alt="{esc(nested(content, "common.googlePlayCta"))}" width="160" height="62"></a>'
            if app.get("googlePlayUrl")
            else f'<span class="availability-state">{esc(nested(content, "common.availability"))}</span>'
        )
        screenshot = assets["screenshots"][0]
        hero_caption = (
            screenshot.get("caption") if locale == source else ""
        ) or nested(content, "home.heroScreenshotCaption")
        if video_url:
            video_labels = VIDEO_LABELS.get(locale.split("-")[0].lower(), VIDEO_LABELS["en"])
            hero_media = (
                '<figure class="hero-media hero-video">'
                f'{render_video_poster(video_url, locale, base_path, str(assets["youtubePoster"]))}'
                f'<figcaption>{esc(video_labels["intro"])}<br>'
                f'<a href="{esc(video_url)}" target="_blank" rel="noopener noreferrer">'
                f'{esc(video_labels["link"])}</a></figcaption></figure>'
            )
        else:
            hero_media = (
                f'<figure class="hero-media"><img src="{esc(base_path + str(hero_relative))}" '
                f'alt="{esc(nested(content, "home.heroScreenshotAlt"))}"><figcaption>{esc(hero_caption)}</figcaption></figure>'
            )
        workflow_steps = [item for item in (nested(content, "home.workflowSteps", []) or []) if isinstance(item, str) and item.strip()]
        workflow_html = ""
        if workflow_steps:
            workflow_html = (
                '<section class="workflow" aria-labelledby="workflow-title"><div class="section-heading">'
                f'<h2 id="workflow-title">{esc(nested(content, "home.workflowHeading", ""))}</h2>'
                f'<p>{esc(nested(content, "home.workflowIntro", ""))}</p></div><ol>'
                + "".join(f"<li>{esc(item)}</li>" for item in workflow_steps)
                + "</ol></section>"
            )

        page_values = {}
        blog_url = "blog/" if locale == source else f"../blog/{locale}/"
        blog_nav_item = (
            f'<a href="{esc(blog_url)}">{esc(nested(content, "navigation.blog", "Blog"))}</a>'
            if has_blog else ""
        )
        for page in ("index.html", "privacy.html", "support.html", "about.html"):
            switcher, routes_json = locale_controls(
                locale,
                source,
                locales,
                contents,
                page,
                base_url,
                aliases,
                package_name,
                auto_detect,
                remember_selection,
            )
            page_values[page] = {
                "LANG": esc(locale),
                "TEXT_DIRECTION": esc(content["direction"]),
                "BASE_PATH": base_path,
                "APP_NAME": esc(app_name),
                "BRAND_LOGO": brand_logo,
                "HOME_URL": "./" if page == "index.html" else "./",
                "PRIVACY_URL": "privacy.html",
                "SUPPORT_URL": "support.html",
                "ABOUT_URL": "about.html",
                "BLOG_URL": blog_url,
                "BLOG_NAV_ITEM": blog_nav_item,
                "LANGUAGE_SWITCHER": switcher,
                "LOCALE_ROUTES_JSON": routes_json,
                "CANONICAL_TAGS": canonical_tags(base_url, locale, source, locales, page),
                "SKIP_TO_CONTENT": esc(nested(content, "common.skipToContent")),
                "PRIMARY_NAV_LABEL": esc(nested(content, "navigation.primaryLabel")),
                "FOOTER_NAV_LABEL": esc(nested(content, "navigation.footerLabel")),
                "NAV_HOME": esc(nested(content, "navigation.home")),
                "NAV_FEATURES": esc(nested(content, "navigation.features")),
                "NAV_SUPPORT": esc(nested(content, "navigation.support")),
                "NAV_PRIVACY": esc(nested(content, "navigation.privacy")),
                "NAV_ABOUT": esc(
                    nested(content, "navigation.about", organization_labels(locale)["pageTitle"])
                ),
                "NAV_BLOG": esc(nested(content, "navigation.blog", "Blog")),
                "BACK_TO_APP": esc(nested(content, "navigation.backToApp")),
                "COPYRIGHT_TEXT": copyright_text.replace(
                    esc(nested(contents[source], "common.rights")),
                    esc(nested(content, "common.rights")),
                ),
            }

        software_data = {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": app_name,
            "applicationCategory": str(app.get("category") or "Application"),
            "operatingSystem": "Android",
            "description": str(nested(content, "home.metaDescription")),
            "featureList": [
                str(item.get("name") or "")
                for item in (nested(content, "home.features", {}) or {}).values()
                if isinstance(item, dict) and str(item.get("name") or "").strip()
            ],
        }
        if app.get("googlePlayUrl"):
            software_data["downloadUrl"] = str(app["googlePlayUrl"])
        if base_url:
            software_data["url"] = page_url(base_url, locale, source, "index.html")
        organization_data = organization_entity(organization)
        if organization_data:
            software_data["publisher"] = {"@id": organization_data["@id"]}
        open_graph = ""
        if base_url:
            og_lines = [
                '<meta property="og:type" content="website">',
                f'<meta property="og:title" content="{esc(nested(content, "home.pageTitle"))}">',
                f'<meta property="og:description" content="{esc(nested(content, "home.metaDescription"))}">',
                f'<meta property="og:url" content="{esc(page_url(base_url, locale, source, "index.html"))}">',
            ]
            if social_relative:
                og_lines.append(f'<meta property="og:image" content="{esc(urljoin(base_url, str(social_relative)))}">')
            open_graph = "\n  ".join(og_lines)

        index_values = merge(page_values["index.html"], {
            "PAGE_TITLE": esc(nested(content, "home.pageTitle")),
            "META_DESCRIPTION": esc(nested(content, "home.metaDescription")),
            "THEME_COLOR": theme_color,
            "OPEN_GRAPH_TAGS": open_graph,
            "SOFTWARE_APPLICATION_JSON_LD": json.dumps(software_data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"),
            "BLOG_NAV_ITEM": blog_nav_item,
            "CATEGORY": esc(nested(content, "home.category")),
            "TAGLINE": esc(nested(content, "home.tagline")),
            "SHORT_DESCRIPTION": esc(
                nested(content, "home.fullDescription")
                or nested(content, "home.shortDescription")
            ),
            "PRIMARY_ACTION": primary_action,
            "HERO_MEDIA": hero_media,
            "OVERVIEW_SECTION": render_overview_section(content, locale),
            "FEATURES_HEADING": esc(nested(content, "home.featuresHeading")),
            "FEATURES_INTRO": esc(nested(content, "home.featuresIntro")),
            "FEATURE_ITEMS": render_feature_items(content, features, locale, source),
            "SCREENSHOT_SECTION": render_screenshots(
                content, assets["screenshots"], base_path, locale == source
            ),
            "WORKFLOW_SECTION": workflow_html,
            "CLOSING_HEADING": esc(nested(content, "home.closingHeading")),
            "CLOSING_COPY": esc(nested(content, "home.closingCopy")),
        })
        (locale_dir / "index.html").write_text(render_template("index.html", index_values), encoding="utf-8")

        privacy_values = merge(page_values["privacy.html"], {
            "PRIVACY_PAGE_TITLE": esc(nested(content, "privacy.pageTitle")),
            "PRIVACY_META_DESCRIPTION": esc(nested(content, "privacy.metaDescription")),
            "LAST_UPDATED_LINE": (
                f'<p class="category">{esc(nested(content, "privacy.lastUpdatedLabel"))}: {esc(date)}</p>'
                if date != "Not provided"
                else ""
            ),
            "PRIVACY_HEADING": esc(nested(content, "privacy.heading")),
            "PRIVACY_CONTENT": render_privacy_content(content),
            "ORGANIZATION_NOTICE": organization_notice(organization, locale),
        })
        (locale_dir / "privacy.html").write_text(render_template("privacy.html", privacy_values), encoding="utf-8")

        contact_action = (
            f'<a class="primary-action" href="mailto:{esc(support_email)}">{esc(nested(content, "support.contactCta"))}</a>'
            if support_email
            else ""
        )
        support_values = merge(page_values["support.html"], {
            "SUPPORT_PAGE_TITLE": esc(nested(content, "support.pageTitle")),
            "SUPPORT_META_DESCRIPTION": esc(nested(content, "support.metaDescription")),
            "VERSION_NAME": esc(version_name),
            "SUPPORT_HEADING": esc(nested(content, "support.heading")),
            "SUPPORT_INTRO": esc(nested(content, "support.intro")),
            "FAQ_SECTION": render_faq(content),
            "CONTACT_HEADING": esc(nested(content, "support.contactHeading")),
            "CONTACT_COPY": esc(nested(content, "support.contactCopy")),
            "CONTACT_ACTION": contact_action,
            "ORGANIZATION_NOTICE": organization_notice(organization, locale),
        })
        (locale_dir / "support.html").write_text(render_template("support.html", support_values), encoding="utf-8")

        about_labels = organization_labels(locale)
        localized_company = localized_organization(organization, locale)
        address = organization.get("address") or {}
        address_parts = [
            str(address.get("streetAddress") or ""),
            str(address.get("region") or ""),
            str(address.get("postalCode") or ""),
            str(localized_company.get("countryName") or address.get("countryCode") or ""),
        ] if isinstance(address, dict) else []
        details = [
            (about_labels["legalName"], str(organization.get("legalName") or developer_name)),
            (about_labels["developerName"], str(organization.get("displayName") or developer_name)),
            (about_labels["website"], str(organization.get("website") or "")),
            (about_labels["email"], str(organization.get("email") or support_email)),
            (about_labels["location"], " · ".join(item for item in address_parts if item)),
        ]
        detail_html = "".join(
            f"<div><dt>{esc(label)}</dt><dd>"
            + (
                f'<a href="{esc(value)}" rel="noopener noreferrer">{esc(value)}</a>'
                if value.startswith("https://")
                else f'<a href="mailto:{esc(value)}">{esc(value)}</a>'
                if "@" in value
                else esc(value)
            )
            + "</dd></div>"
            for label, value in details
            if value
        )
        about_description = str(
            localized_company.get("description")
            or organization.get("description")
            or about_labels["metaDescription"]
        )
        org_script = ""
        if organization_data:
            org_payload = {"@context": "https://schema.org", **organization_data}
            org_script = (
                '<script type="application/ld+json">'
                + json.dumps(org_payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
                + "</script>"
            )
        about_values = merge(page_values["about.html"], {
            "ABOUT_PAGE_TITLE": esc(f'{about_labels["pageTitle"]} - {app_name}'),
            "ABOUT_META_DESCRIPTION": esc(about_description),
            "ORGANIZATION_STRUCTURED_DATA": org_script,
            "COMPANY_KICKER": esc(about_labels["kicker"]),
            "ABOUT_HEADING": esc(about_labels["heading"]),
            "COMPANY_DESCRIPTION": esc(about_description),
            "COMPANY_DETAILS_HEADING": esc(about_labels["details"]),
            "COMPANY_DETAILS": detail_html,
            "COMPANY_CONTACT_HEADING": esc(about_labels["contact"]),
            "COMPANY_CONTACT_COPY": esc(about_labels["contactCopy"]),
            "COMPANY_CONTACT_ACTION": (
                f'<a class="primary-action" href="mailto:{esc(organization.get("email") or support_email)}">'
                f'{esc(about_labels["contactCta"])}</a>'
            ),
        })
        (locale_dir / "about.html").write_text(render_template("about.html", about_values), encoding="utf-8")
        generated_pages.extend(
            page_relative(locale, source, page) or "index.html"
            for page in ("index.html", "privacy.html", "support.html", "about.html")
        )

    generated_pages.extend(
        render_feature_pages(
            app,
            organization,
            source,
            locales,
            contents,
            features,
            assets,
            stage,
            base_url,
            theme_color,
            aliases,
            auto_detect,
            remember_selection,
            copyright_text,
        )
    )

    generated_pages.extend(
        render_blog(
            app,
            organization,
            source,
            locales,
            contents,
            features,
            assets,
            stage,
            base_url,
            theme_color,
            aliases,
            auto_detect,
            remember_selection,
        )
    )

    manifest_icons = []
    if icon_relative:
        manifest_icons.append({"src": str(icon_relative), "sizes": "any", "type": "image/" + Path(str(icon_relative)).suffix.lstrip(".")})
    manifest = {
        "name": app_name,
        "short_name": app_name[:30],
        "description": str(nested(contents[source], "home.metaDescription")),
        "lang": source,
        "start_url": "./",
        "display": "browser",
        "background_color": "#ffffff",
        "theme_color": theme_color,
        "icons": manifest_icons,
    }
    (stage / "site.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    sitemap_entries = []
    if base_url:
        for page in sorted(set(generated_pages)):
            relative_url = "" if page == "index.html" else page.removesuffix("index.html")
            sitemap_entries.append(f"  <url><loc>{esc(urljoin(base_url, relative_url))}</loc></url>")
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(sitemap_entries) + "\n</urlset>\n"
    (stage / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    robots = "User-agent: *\nAllow: /\n"
    if base_url:
        robots += f"\nSitemap: {urljoin(base_url, 'sitemap.xml')}\n"
    (stage / "robots.txt").write_text(robots, encoding="utf-8")

    status = {
        "sourceLocale": source,
        "locales": [
            {
                "locale": locale,
                "status": "source" if locale == source else str(contents[locale].get("reviewStatus") or "machine-draft"),
                "reviewer": "",
                "reviewedAt": "",
            }
            for locale in locales
        ],
    }
    (stage / "localization-status.yaml").write_text(
        yaml.safe_dump(status, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )

    write_launch_artifacts(
        app,
        organization,
        source,
        locales,
        contents,
        features,
        assets,
        stage,
        base_url,
    )

    source_content_data = contents[source]
    not_found_values = {
        "LANG": esc(source),
        "TEXT_DIRECTION": esc(source_content_data["direction"]),
        "NOT_FOUND_PAGE_TITLE": esc(
            f'{nested(source_content_data, "common.notFoundTitle")} - {app_name}'
        ),
        "NOT_FOUND_HEADING": esc(nested(source_content_data, "common.notFoundTitle")),
        "NOT_FOUND_COPY": esc(nested(source_content_data, "common.notFoundCopy")),
        "RETURN_HOME": esc(nested(source_content_data, "common.returnHome")),
    }
    (stage / "404.html").write_text(
        render_template("404.html", not_found_values), encoding="utf-8"
    )
    shutil.copy2(TEMPLATE_ROOT / "_headers", stage / "_headers")
    excluded_roots = {"content", "aso", "seo-geo"}
    excluded_files = {"launch-readiness.yaml"}
    public_files = sorted(
        path.relative_to(stage).as_posix()
        for path in stage.rglob("*")
        if path.is_file()
        and path.relative_to(stage).parts[0] not in excluded_roots
        and path.relative_to(stage).as_posix() not in excluded_files
    )
    public_files.append("static-site-manifest.json")
    public_manifest = {
        "schemaVersion": "1.0",
        "entry": "index.html",
        "files": public_files,
    }
    (stage / "static-site-manifest.json").write_text(
        json.dumps(public_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return locales


def validate_stage(stage: Path) -> None:
    errors: list[str] = []
    for path in stage.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in {".html", ".json", ".xml", ".yaml", ".txt", ".js", ".css", ".webmanifest"}:
            text = path.read_text(encoding="utf-8")
            if TOKEN.search(text):
                errors.append(f"{path.relative_to(stage)}: unresolved template token")
            if PLACEHOLDER.search(text):
                errors.append(f"{path.relative_to(stage)}: placeholder text")
            if path.suffix.lower() == ".html" and len(re.findall(r"<h1(?:\s|>)", text, re.IGNORECASE)) != 1:
                errors.append(f"{path.relative_to(stage)}: expected exactly one h1")
            if path.suffix.lower() == ".html":
                for reference in LOCAL_REFERENCE.findall(text):
                    if reference.startswith(("#", "http://", "https://", "mailto:", "data:")):
                        continue
                    target = (path.parent / reference.split("#", 1)[0].split("?", 1)[0]).resolve()
                    if reference.endswith("/"):
                        target /= "index.html"
                    if not target.exists():
                        errors.append(f"{path.relative_to(stage)}: missing local reference {reference}")
    try:
        json.loads((stage / "site.webmanifest").read_text(encoding="utf-8"))
        yaml.safe_load((stage / "localization-status.yaml").read_text(encoding="utf-8"))
    except (json.JSONDecodeError, yaml.YAMLError) as error:
        errors.append(f"invalid structured output: {error}")
    if errors:
        raise GenerationError("generated output failed validation:\n  - " + "\n  - ".join(errors))


def copy_stage(stage: Path, output: Path, force: bool) -> list[Path]:
    files = sorted((path for path in stage.rglob("*") if path.is_file()), key=lambda item: item.as_posix())
    collisions = [output / path.relative_to(stage) for path in files if (output / path.relative_to(stage)).exists()]
    if collisions and not force:
        preview = "\n  - ".join(str(path) for path in collisions[:10])
        suffix = f"\n  - ... and {len(collisions) - 10} more" if len(collisions) > 10 else ""
        raise GenerationError(f"refusing to overwrite existing website files; rerun with --force:\n  - {preview}{suffix}")
    output.mkdir(parents=True, exist_ok=True)
    copied = []
    for source in files:
        destination = output / source.relative_to(stage)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied.append(destination)
    return copied


def generate(
    app_info_path: Path,
    output: Path,
    locales_root: Path,
    force: bool = False,
    organization_path: Path | None = None,
) -> tuple[list[str], list[Path]]:
    app_info_path = app_info_path.resolve()
    output = output.resolve()
    locales_root = locales_root.resolve()
    if not app_info_path.is_file():
        raise GenerationError(f"app-info file does not exist: {app_info_path}")
    errors = app_info_errors(app_info_path)
    if errors:
        raise GenerationError("app-info validation failed:\n  - " + "\n  - ".join(errors))
    app = load_yaml(app_info_path)
    organization = load_organization(organization_path)
    with tempfile.TemporaryDirectory(prefix="app-launch-site-") as temp:
        stage = Path(temp)
        locales = render_site(app, organization, app_info_path, locales_root, stage)
        validate_stage(stage)
        copied = copy_stage(stage, output, force)
    return locales, copied


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-info", type=Path, default=PROJECT_ROOT / "app-info.yaml")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--locales", type=Path, default=PROJECT_ROOT / "content" / "locales")
    parser.add_argument("--organization", type=Path, default=SYSTEM_ROOT / "config" / "organization.yaml")
    parser.add_argument("--force", action="store_true", help="overwrite only files generated by the staged website")
    args = parser.parse_args()
    try:
        locales, files = generate(args.app_info, args.output, args.locales, args.force, args.organization)
    except GenerationError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    digest = hashlib.sha256("\n".join(str(path.relative_to(args.output.resolve())) for path in files).encode()).hexdigest()[:12]
    print(f"OK: generated {len(files)} files in {args.output.resolve()}")
    print(f"Locales: {', '.join(locales)}")
    print(f"File-set digest: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
