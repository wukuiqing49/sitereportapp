---
name: website-generator-skill
description: Generate a production-ready, responsive, localized official website for an Android app from a verified app-info.yaml and repository assets. Use when creating or refreshing an app product website, feature pages, privacy and support pages, localized web copy, app download calls to action, or a static launch site based on Android project facts.
---

# Generate an Android App Website

Build the actual product website from verified metadata and real app visuals. Do not create a marketing plan in place of working files.

## Inputs

Require `app-info.yaml` and the absolute Android project path recorded in `sourceProject`. Accept an output directory, preferred framework, domain, and target locales. Default website output to `<project-root>`, where `<project-root>` is the directory containing `app-launch-system`, and use a dependency-free static site based on `../../templates/website-template/`; reuse an existing project framework only when requested or already established.

## Workflow

1. Read all of `app-info.yaml`. Stop and report schema errors or a missing product name, description, source locale, and at least one verified feature. Resolve target locales from explicit user input, then `languages.targets`, then verified `languages.availableInApp`; when multilingual output is requested and none are available, request locales instead of inventing them.
2. From the `app-launch-system` root, run `python scripts/launch.py validate-app-info <app-info.yaml>` and stop on errors.
3. Read [references/site-contract.md](references/site-contract.md).
4. Inspect every referenced logo and screenshot. Use actual app screens as primary visuals; do not invent UI or use unrelated stock images.
5. Inspect `<app-launch-system>/config/assets/` when present. Use explicit `assets.icon`, `assets.coverImage`, `assets.socialImage`, and every item in `assets.screenshots` first; fall back to verified Android project assets only when these fields are empty. Copy selected assets into `<project-root>/assets` and preserve their purpose. Never assume screenshots is singular.
6. Prepare one complete `<project-root>/content/locales/<locale>.yaml` for every non-source locale, following `../../templates/website-template/locale-content.yaml`. Translate both `home.features` and every content-ready feature's structured `featureDetails`. Never satisfy this requirement by copying source text. A source-locale file is optional for `en` and `zh`; provide a complete source-locale file for other source languages.
7. From `<project-root>`, run `python app-launch-system/scripts/launch.py generate-website`. This renders into a temporary directory, validates it, then writes `index.html` and the other public files directly to `<project-root>`. It does not create `launch-output/` or another wrapper. Existing website files are protected unless the user explicitly approves `--force`.
8. Confirm source-locale pages are at the root and every target locale is under its BCP 47 directory. Keep brand names, package names, URLs, and legal identifiers unchanged. Confirm reciprocal route data exists for the same page in every complete locale.
9. Confirm metadata, canonical and alternate locale links, Open Graph data, JSON-LD, `robots.txt`, `sitemap.xml`, and the web manifest use confirmed URLs only. The generator deliberately omits canonical and Open Graph URL tags when `websiteUrl` is unknown.
10. From `<project-root>`, run `python app-launch-system/scripts/launch.py validate-output .` before reporting success.
11. Test keyboard navigation, contrast, responsive layouts, internal links, missing assets, structured data syntax, and text overflow at mobile and desktop widths.
12. Return the output path, locale list, selected asset paths, validation results, and unresolved deployment values. Do not deploy unless explicitly requested.

The generator also writes `aso/`, `seo-geo/`, and `launch-readiness.yaml`. Treat these as editable internal artifacts, not public website files. Read the readiness report before describing SEO, GEO, ASO, localization, or publication as complete.

## Content Rules

- Make the app name and actual interface visible in the first viewport.
- Use `assets.coverImage` for the homepage hero when supplied; use `assets.socialImage` for Open Graph when supplied. Never use a phone screenshot as a social image if an explicit social image exists.
- State a literal value proposition in the supporting copy and keep headings specific.
- Tie each feature claim to `features[].evidence`.
- Generate a feature page and blog only when structured feature details pass the content-ready gate. Keep incomplete verified features as homepage summaries and report them in `launch-readiness.yaml`.
- Link the primary action to `googlePlayUrl`; render a non-clickable availability state when the URL is unknown.
- Never emit an empty or placeholder `href` for an unknown `googlePlayUrl`; use visible availability text instead.
- Include privacy and support pages. Include terms only when legal text or a policy owner is provided.
- Do not fabricate reviews, user counts, ratings, awards, certifications, customers, pricing, guarantees, or data practices.
- Use semantic HTML, visible focus states, descriptive alt text, and reduced-motion support.
- Avoid decorative gradients, nested cards, oversized empty hero areas, and visuals that obscure the app.

## Localization

Use the source locale as factual ground truth and keep it at the project root. Transcreate for local search intent and natural phrasing instead of literal translation. Preserve meaning and claim strength. Format dates, punctuation, numbers, and reading direction by locale; set `dir="rtl"` for right-to-left languages.

For every page, generate `LOCALE_ROUTES_JSON` and a native-language `<select data-locale-switcher>` using only locales where that page exists. Enable automatic detection only on source-locale root pages. Match a saved explicit choice first, then `navigator.languages`, configured aliases, base language, and finally the source locale. Store explicit selection locally, never overwrite it with automatic detection, and never redirect localized subdirectory pages automatically. Mark every non-reviewed locale as `machine-draft` in `<project-root>/localization-status.yaml`.
