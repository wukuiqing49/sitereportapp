---
name: seo-geo-generator-skill
description: Generate localized SEO and Generative Engine Optimization assets for an Android app from verified app-info.yaml. Use when producing keyword and page maps, titles and descriptions, entity profiles, answer-first content, FAQs, structured data, AI-search citation briefs, internal-link plans, sitemaps, or audits that improve discoverability in web search and generative answer engines.
---

# Generate SEO and GEO Assets

Create a search package grounded in product evidence. Treat SEO as retrieval and page relevance; treat GEO as clear, attributable answers and entity consistency. Do not claim guaranteed ranking or AI citations.

## Inputs

Require `app-info.yaml`. Accept target locales, confirmed domain, existing URL inventory, competitor set, and available first-party research. If search-volume or competitive data is unavailable, label priorities as qualitative rather than inventing metrics.

## Workflow

1. Read all product facts, evidence, target users, use cases, languages, and excluded claims.
2. From the `app-launch-system` root, run `python scripts/launch.py validate-app-info <app-info.yaml>` and stop on errors.
3. Read [references/seo-geo-policy.md](references/seo-geo-policy.md).
4. Inventory existing URLs when a website is supplied. Preserve useful pages and avoid duplicate intent.
5. Build locale-specific intent clusters: branded, category, problem, feature, use case, and support.
6. Map one primary intent to each proposed page using `../../templates/seo-template/page-brief.yaml`.
7. Produce concise answer blocks and FAQs from verified facts using `../../templates/seo-template/geo-answer.md`.
8. Generate only applicable JSON-LD from `../../templates/seo-template/structured-data.json.tmpl`; ensure structured data matches visible page content.
9. From the `app-launch-system` root, run `python scripts/launch.py validate-output <output>/seo-geo` before reporting success.
10. Deliver the output contract below and audit every claim, URL, locale alternate, and template token.

## Deliverables

Write under `<output>/seo-geo/`:

- `keyword-map.csv`: Locale, cluster, query, intent, target page, priority basis, and evidence.
- `page-map.yaml`: Existing and proposed URLs with a single primary intent each.
- `<locale>/metadata.yaml`: Unique title, meta description, canonical, robots, and social metadata for each page.
- `<locale>/answers.md`: Answer-first definitions, workflows, selection guidance, limitations, and FAQs.
- `entity-profile.yaml`: Stable product name, developer, category, package, official URLs, and verified descriptions.
- `structured-data/`: Valid JSON-LD files for applicable visible pages.
- `internal-links.csv`: Source page, destination page, suggested anchor, and rationale.
- `audit.md`: Errors, warnings, unknowns, and recommended fixes ordered by impact.

## SEO Rules

- Write for the page's intent; never repeat keywords mechanically.
- Keep one canonical URL per content item and reciprocal locale alternates.
- Make titles and descriptions unique, accurate, and naturally localized.
- Do not create doorway pages, hidden text, fabricated locations, or thin locale variants.
- Mark estimated or tool-derived data with its source and collection date.

## GEO Rules

- State the direct answer first, then evidence, steps, limitations, and product context.
- Keep the app entity identical across website, Play listing, blog, and structured data.
- Prefer specific factual statements that can be independently checked.
- Use tables only for real comparisons with a defined basis.
- Treat `llms.txt` as optional publisher guidance, not a ranking mechanism; create it only when requested.

## Localization

Research or infer intent separately for each locale. Do not translate keyword lists literally. When no locale-specific data is available, label the keyword map `qualitative-draft` and require native review for public metadata.
