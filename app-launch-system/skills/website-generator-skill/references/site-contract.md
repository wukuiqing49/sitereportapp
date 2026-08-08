# Website Output Contract

## Required files

- `index.html`: Product overview with a real screenshot, value proposition, features, use cases, and Google Play action.
- `privacy.html`: Confirmed privacy policy or a clearly labeled draft with unresolved fields.
- `support.html`: Confirmed support route, common questions, app version, and contact details.
- `404.html`: Source-locale static not-found page with a root-home link and `noindex`.
- `_headers`: Cloudflare Pages-compatible security and cache headers.
- `styles.css`: Responsive, accessible styling with no external runtime dependency by default.
- `app.js`: Progressive enhancement only; core content must work without JavaScript.
- `locale-router.js`: Browser-language matching and remembered manual locale selection.
- `robots.txt`, `sitemap.xml`, and `site.webmanifest`.
- `localization-status.yaml`: Locale, source, generation status, reviewer, and review date.

Generate `features/<slug>/index.html` and localized equivalents only for content-ready verified features. A content-ready feature requires a stated problem, at least two capabilities, supported input and output, configurable options, at least three real steps, a limitation, a question and answer, and source evidence. A verified feature that does not meet this gate may remain as a homepage summary, but must not produce a thin feature page or blog article.

Keep editorial and audit files outside the public deploy manifest:

- `content/blog/`
- `aso/`
- `seo-geo/`
- `launch-readiness.yaml`

## Deterministic generator

Install the declared Python dependency from `app-launch-system/requirements.txt`, then run from the project root:

```powershell
python app-launch-system/scripts/launch.py generate-website
```

Defaults are `app-info.yaml`, the current project root, and `content/locales/`. Use `--force` only for an explicitly approved refresh of existing generated files. Every target in `languages.targets` requires `content/locales/<locale>.yaml`; missing or incomplete target content is a hard failure, not a translation fallback.

## URL model

Keep the source locale at the root for both single- and multi-locale sites. Put each non-source locale in a stable BCP 47 directory such as `/en-US/` or `/ja-JP/`. Root pages are also `x-default`; do not duplicate the source locale in another directory.

Every localized page must include:

- A self-referencing canonical URL.
- Reciprocal `hreflang` links for every locale where the equivalent page exists, plus `x-default` to the root equivalent.
- Matching `lang` and `dir` attributes.
- A native-language locale menu using `<select data-locale-switcher>`.
- A `locale-routes` JSON block containing `sourceLocale`, `currentLocale`, `autoRedirect`, `storageKey`, optional aliases, and `{code, url}` routes for equivalent pages.

Set `autoRedirect: true` only on source-locale root pages. Localized directory pages must set it to `false`, so direct links and search visits remain stable. The static router uses a remembered explicit choice or browser languages; it is progressive enhancement and must not replace visible source content, server-side negotiation, canonical URLs, or `hreflang`.

Use a product-specific storage key derived from the verified package name. A page-level route block follows this shape:

```json
{
  "sourceLocale": "en-US",
  "currentLocale": "en-US",
  "autoRedirect": true,
  "storageKey": "com.example.app:locale",
  "aliases": {"zh-HK": "zh-TW"},
  "locales": [
    {"code": "en-US", "url": "/"},
    {"code": "zh-CN", "url": "/zh-CN/"}
  ]
}
```

Render the language picker with native labels rather than translating every language name into the current locale:

```html
<label class="language-picker">
  <span class="visually-hidden">LANGUAGE_LABEL</span>
  <select data-locale-switcher aria-label="LANGUAGE_LABEL">
    <option value="en-US">English</option>
    <option value="zh-CN">简体中文</option>
  </select>
</label>
```

## Structured data

Use `SoftwareApplication` for the product and `Organization` only when the developer identity is verified. Add `FAQPage` only when the questions and visible answers are present on the page. Never add rating, price, offer, or review properties without matching verified content.

## Validation gates

- No unresolved template tokens.
- No broken local links or missing local media.
- Exactly one descriptive `h1` per page.
- Unique title and meta description per indexable page.
- Valid JSON-LD and manifest JSON.
- No horizontal scrolling at 320 CSS pixels.
- Interactive elements work by keyboard and expose accessible names.
- `websiteUrl` is required before SEO/GEO can be marked ready.
- `googlePlayUrl` is required before ASO can move beyond draft/blocked.
- Machine-generated target locales remain drafts until human review.
- Project analysis dates must never be reused as article publication dates.
