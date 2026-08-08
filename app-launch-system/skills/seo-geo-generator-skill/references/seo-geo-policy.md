# SEO and GEO Policy

## Evidence classes

- Product facts: Use only `verified` app metadata or explicit user input.
- Search data: Cite the tool or dataset, locale, market, and collection date.
- Editorial inference: Label qualitative prioritization and explain its basis.
- Third-party facts: Record a stable source URL and access date.

## Entity consistency

Use the same app name, package name, developer, category, official domain, Google Play URL, support URL, and concise definition in all machine-readable assets. Do not create an `Organization` entity when the legal developer is unknown.

## Page eligibility

Propose an indexable page only when it has a distinct user intent and enough verified content to satisfy it. Consolidate overlapping feature, use-case, and locale pages. Use `noindex` for drafts, internal search results, and thin generated pages.

## Structured data eligibility

- `SoftwareApplication`: Verified app identity and visible app content.
- `Organization`: Verified developer identity and visible organization details.
- `FAQPage`: Questions and complete answers visible on that page.
- `Article`: Visible editorial content with accurate author and dates.
- `BreadcrumbList`: Visible or structurally accurate breadcrumb hierarchy.

Never add ratings, reviews, prices, offers, availability, or author details that are missing from the visible page and product evidence.

## Audit severity

- Error: Broken canonical, invalid schema, blocked key page, contradictory entity, unsupported public claim, or missing indexable content.
- Warning: Duplicate metadata, weak intent match, missing alternate, orphan page, thin answer, or unreviewed localization.
- Note: Optional enhancement with no current correctness impact.
