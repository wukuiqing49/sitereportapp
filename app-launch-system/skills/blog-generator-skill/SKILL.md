---
name: blog-generator-skill
description: Generate evidence-based, localized blog strategy, editable Markdown, and a polished static blog that matches an Android app website. Use when creating a blog index, product launch posts, feature education, tutorials, use-case articles, release notes, editorial calendars, internal links, multilingual blog content, or multiple reusable blog page layouts from app-info.yaml.
---

# Generate App Blog Content

Create useful editorial content that answers real user needs and supports product discovery without restating a store listing.

## Inputs

Require `app-info.yaml`. Accept a content goal, audience stage, target locales, article count, cadence, existing-site URL map, and preferred template. Default to one launch article, two evergreen use-case articles, and a 12-topic backlog. Render public pages under `<project-root>/blog/` and keep editable sources under `<project-root>/content/blog/`.

## Workflow

1. Read `app-info.yaml` and separate verified facts from inferred positioning.
2. From the `app-launch-system` root, run `python scripts/launch.py validate-app-info <app-info.yaml>` and stop on errors.
3. Read [references/editorial-policy.md](references/editorial-policy.md).
4. Read [references/template-contract.md](references/template-contract.md) before selecting layouts or output paths.
5. Build topic clusters from target-user problems, supported features, and use cases. Assign one primary intent, one funnel stage, and one supported template to each topic.
6. Create `<project-root>/content/blog/content-plan.yaml` from `../../templates/blog-template/content-plan.yaml`.
7. Draft source-locale articles from `../../templates/blog-template/article.md`. Keep evidence paths in frontmatter and public prose free of internal repository paths.
8. Render the blog index and each article with the matching file under `../../templates/blog-template/pages/`. Copy `assets/blog.css` and `assets/blog.js` beside the website assets, and reuse the website's `assets/locale-router.js`. Load the website's `assets/styles.css` first so brand variables, header, footer, buttons, and focus states stay consistent.
   When integrating with an existing website, add the localized blog navigation link without overwriting pages marked `reviewed` or `published`.
9. Use only verified logos, cover images, and screenshots. Omit the media region when no suitable visual exists; never substitute unrelated imagery.
10. Add natural internal links to product, feature, support, and related article pages. Do not invent destination URLs.
11. Transcreate approved topics for each target locale. Adapt examples and query language while preserving product facts. Generate the same native-language selector, route JSON, reciprocal `hreflang`, canonical, direction, browser detection, and remembered-selection behavior as the website.
12. From `<project-root>`, run `python app-launch-system/scripts/launch.py validate-output content/blog` and `python app-launch-system/scripts/launch.py validate-output blog` before reporting success.
13. Test the blog index and every template at mobile and desktop widths. Check keyboard navigation, overflow, local links, media paths, metadata, JSON-LD, and exactly one `h1` per page.
14. Return source and rendered paths, templates used, word counts, locales, evidence, validation results, and review items.

## Article Requirements

- Answer the search or reader intent in the opening paragraph.
- Provide concrete steps, examples, limitations, and a proportionate call to action.
- Use screenshots only when their referenced screens match the article.
- Keep the app identity visible in the header and link every article back to the official website and blog index.
- Preserve one visual system across website and blog. Reuse the website CSS variables and do not introduce a separate brand palette or unrelated typography.
- Use `standard-article`, `tutorial`, or `release-notes` according to the content structure. Do not select layouts merely for visual variety.
- Cite repository evidence in frontmatter `evidence`; do not expose internal paths in public prose.
- Label comparisons and benchmarks with method, date, and source. Omit them when proof is unavailable.
- Avoid generic AI filler, repetitive conclusions, fake quotations, fabricated statistics, and keyword stuffing.
- Never promise outcomes or imply platform endorsement.

## Localization

Keep one stable content ID across locales. Store editable articles at `<project-root>/content/blog/<locale>/<slug>.md` and rendered pages at `<project-root>/blog/<locale>/<slug>/index.html`. Localize slugs, titles, metadata, examples, calls to action, navigation, and image alt text while preserving canonical product terminology. Mark unreviewed translations as `machine-draft` and never label them `published`.
