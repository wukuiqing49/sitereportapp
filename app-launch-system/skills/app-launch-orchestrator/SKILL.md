---
name: app-launch-orchestrator
description: Coordinate the Android app launch pipeline across app analysis, website, SEO/GEO, ASO, and blog generation. Use when the user asks for a complete launch package, wants to decide which launch asset workflow to run, or needs existing root-level launch assets audited and resumed.
---

# Orchestrate an Android Launch Package

Coordinate the specialist skills through one shared `app-info.yaml` and one output manifest. Do not generate public content from unverified facts.

Read [../../references/review-policy.md](../../references/review-policy.md) before routing any public-facing work.

Run all deterministic commands from the `app-launch-system` root through `scripts/launch.py`; do not invoke skill-local scripts by relative path.

## Input resolution

1. Resolve the absolute Android project path from explicit user input. The source project may be outside the skill directory.
2. Find `app-info.yaml` in this order: explicit user path, `<project-root>/app-info.yaml`, then the Android source project only when the user explicitly asks for it.
3. If multiple candidates exist, report them and ask for selection.
4. If no valid metadata exists, run `$app-analyzer-skill` first.

## Task routing

- Analysis or metadata refresh: `$app-analyzer-skill`
- Official website: `$website-generator-skill`
- Search and AI-answer assets: `$seo-geo-generator-skill`
- Google Play listing: `$aso-generator-skill`
- Editorial content: `$blog-generator-skill`
- Complete launch package: run analyzer if needed, then website, SEO/GEO, ASO, and blog in that order.

For the website stage, prepare all required `content/locales/<locale>.yaml` files and run `python scripts/launch.py generate-website` from the `app-launch-system` root. The command resolves its defaults to the parent project root. Use `--force` only after the user approves replacing existing generated website files.

## Shared output contract

Use `<project-root>/` by default, where `<project-root>` is the directory containing `app-launch-system`. Keep the Android source project read-only and place the public website entry directly at the project root:

```text
<project-root>/
|-- app-launch-system/
|-- index.html
|-- privacy.html
|-- support.html
|-- assets/
|-- <target-locale>/
|-- localization-status.yaml
|-- blog/
|-- content/blog/
|-- launch-readiness.yaml
|-- app-info.yaml
|-- analysis-evidence.json
|-- launch-manifest.yaml
|-- seo-geo/
`-- aso/
```

Do not delete existing user files. Before overwriting an existing artifact, report the path and preserve files marked `reviewed` or `published`.

## State management

Create or update `launch-manifest.yaml` after every stage. Each stage must be one of `pending`, `running`, `completed`, `blocked`, or `skipped`. Set `blocked` when validation fails or required user information is missing. Keep the last error and validation timestamp.

Do not report the package as publishable unless `app-info.yaml` is valid, `launch-readiness.yaml` reports `publishReady: true`, all requested stages are completed, target locales are reviewed, and no blocking unknowns remain. A missing `websiteUrl` blocks SEO/GEO readiness; a missing `googlePlayUrl` blocks ASO readiness.

## Handoff

Return the output root, completed and blocked stages, validation commands and results, review-required items, and the exact next action. Never deploy, publish, upload, or modify external services without an explicit request.
