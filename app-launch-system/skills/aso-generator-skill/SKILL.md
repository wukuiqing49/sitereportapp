---
name: aso-generator-skill
description: Generate localized Google Play App Store Optimization content from verified app-info.yaml. Use when creating or auditing app titles, short and full descriptions, keyword strategy, screenshot captions, feature-graphic briefs, release notes, custom store listing variants, localization, store experiments, or Google Play listing compliance for Android apps.
---

# Generate Google Play ASO Content

Create conversion-focused store copy that accurately represents the shipped app. Optimize each locale for its own language and intent rather than translating keyword lists.

## Inputs

Require `app-info.yaml`. Accept target markets, target locales, current listing exports, known search data, experiment goals, and Google Play policy constraints. Confirm current field limits and policy before final delivery when live documentation is available.

## Workflow

1. Read all of `app-info.yaml`, especially evidence, unknowns, claims to avoid, supported languages, and screenshots.
2. From the `app-launch-system` root, run `python scripts/launch.py validate-app-info <app-info.yaml>` and stop on errors.
3. Read [references/google-play-listing.md](references/google-play-listing.md).
4. Audit any current listing for accuracy, duplication, localization quality, claim risk, and conversion gaps.
5. Build a locale-specific term map by user problem, category, feature, and use case. Label qualitative terms when search data is unavailable.
6. Draft title, short description, and full description. Count characters with Unicode code points and report counts beside every field.
7. Map verified screenshots to a logical story and write captions that describe the visible screen and benefit.
8. Produce experiment hypotheses with one variable per test and a measurable Play Console outcome.
9. From the `app-launch-system` root, run `python scripts/launch.py validate-output <output>/aso` after writing files.
10. Validate field limits, claims, URLs, formatting, locale naturalness, and unresolved placeholders.

## Deliverables

Write under `<output>/aso/`:

- `<locale>/listing.yaml`: Title, short description, full description, counts, term map, and evidence.
- `<locale>/screenshots.yaml`: Ordered source files, visible screen, caption, and review status.
- `<locale>/release-notes.txt`: Only when verified change data exists.
- `experiments.yaml`: Hypothesis, audience, single variable, variants, metric, and stop condition.
- `audit.md`: Current issues, policy risks, unknowns, and prioritized actions.
- `localization-status.yaml`: Source locale, target locale, machine-draft status, reviewer, and review date.

## Copy Rules

- Lead with the primary user outcome and differentiate through supported capabilities.
- Use natural repetitions only; do not add keyword lists or competitor trademarks.
- Keep title branding stable across locales unless an approved localized brand exists.
- Avoid ranking, award, price, discount, download, rating, endorsement, and superlative claims without current proof and policy eligibility.
- Do not use emoji, all caps, repeated punctuation, or urgency as a substitute for value.
- Never infer data safety answers from permissions or dependencies.
- Do not describe dormant, experimental, region-blocked, or paywalled features as universally available.

## Localization

Transcreate within the field limits. Preserve product facts and claim strength, adapt term order to local usage, and have a native reviewer check high-value markets. Do not publish machine drafts or mark them reviewed.
