---
name: android-app-website
description: Analyze an Android project from an absolute local path and generate a polished, multilingual, Cloudflare Pages-ready static app website. Use when the user provides an Android project directory and asks to create an app official website, product site, landing page, static site, or Cloudflare Pages site without first preparing app-info.yaml.
---

# Build an Android App Website

Treat the Android project path as the only required user input. Hide the internal metadata and template workflow unless an unresolved product or legal fact requires confirmation.

## Workflow

1. Resolve the supplied Android project to an existing absolute directory. Keep it read-only. Set the site root to the directory containing `app-launch-system/`; never write the website into the Android source project.
2. Read `../app-analyzer-skill/SKILL.md` and analyze the project. Write `analysis-evidence.json` and the verified `app-info.yaml` directly to the site root. Do not ask the user to prepare either file.
3. Inspect every configured image under `app-launch-system/config/assets/`. Prefer these images over repository images. Require at least one valid current screenshot; use the app icon and cover when supplied.
4. Resolve the source language from verified Android resources or explicit input. Resolve target languages from explicit input or verified app resources. Prepare complete `content/locales/<locale>.yaml` files for targets; do not copy source text as fake translation. Mark unreviewed translations `machine-draft`.
5. Read `../website-generator-skill/references/site-contract.md`, then run from the site root:

   ```powershell
   python app-launch-system/scripts/launch.py generate-website
   ```

   Use `--force` only after confirming that an existing generated site should be refreshed.
6. Verify the Cloudflare static output contract in [references/cloudflare-pages.md](references/cloudflare-pages.md). Run `python app-launch-system/scripts/launch.py validate-output .` and inspect the generated pages at mobile and desktop sizes when a browser is available.
7. Report the root `index.html`, generated locales, screenshots used, facts that still need review, and validation results. Do not deploy or modify Cloudflare unless explicitly requested.

## Required Result

Generate a dependency-free static site at the site root:

```text
<site-root>/
|-- app-launch-system/
|-- index.html
|-- privacy.html
|-- support.html
|-- 404.html
|-- _headers
|-- assets/
|-- <target-locale>/
|-- robots.txt
|-- sitemap.xml
|-- site.webmanifest
|-- static-site-manifest.json
`-- localization-status.yaml
```

Keep the source locale at the root and target locales in BCP 47 directories. Use browser language detection and a remembered manual selection. Omit unconfirmed canonical URLs, ratings, pricing, privacy claims, and store links rather than inventing them.

The site must work by opening `index.html` directly and must require no Node build, framework runtime, database, API, or server-side rendering. Treat only paths listed in `static-site-manifest.json` as deployable public files.
