---
name: cloudflare-search-console
description: Configure an existing production website on Cloudflare Pages for Google Search Console. Use when the website already exists and the task is limited to Pages deployment settings, live HTTP checks, Search Console verification, robots.txt, sitemap submission, canonical readiness, or indexing follow-up. Do not use this skill to design or generate the website itself.
---

# Cloudflare Search Console

Connect an already-produced website to Google Search Console from deployment to indexing readiness. Treat the website files as an existing product. Do not redesign pages, rewrite product copy, analyze the Android source, or invent Google verification data.

## Usage

Use this Skill when the website already exists and the request is about connecting or checking Cloudflare Pages with Google Search Console:

```text
Use $cloudflare-search-console to connect my existing Cloudflare Pages site to Google Search Console.
Site root: C:\work\AI\sitereportapp
Live URL: https://site.pages.dev/
```

For HTML-file verification, provide Google's exact values:

```text
Filename: google1234567890abcdef.html
Body: google-site-verification: google1234567890abcdef.html
```

For this project, the normal local checks are:

```powershell
python app-launch-system/scripts/launch.py validate-app-info app-info.yaml
python app-launch-system/scripts/launch.py generate-website --force
python app-launch-system/scripts/launch.py validate-output .
```

After local validation, authorize the Git push or direct Cloudflare deployment separately. Then check the exact live verification URL, open the URL-prefix property in Search Console, click Verify, submit `sitemap.xml`, and request indexing for the homepage.

## Workflow

1. Identify the website root, Cloudflare Pages project, production branch, build command, output directory, and public URL. Preserve unrelated user changes.
2. Inspect the existing deployment contract. If the repository has `static-site-manifest.json`, deploy only its listed public files. Never upload Android source, `app-info.yaml`, analysis evidence, locale sources, internal reports, or Skill files.
3. Confirm the public URL exactly. For `https://name.pages.dev/`, use a Google Search Console **URL-prefix property** with the trailing slash. Use a Domain property only when the user controls that domain's DNS zone.
4. Choose the user's verification method: HTML tag, HTML file, or DNS TXT. Preserve Google's exact values. Never derive or fabricate a token, filename, or file body.
5. Handle Cloudflare Pages Clean URLs. The official Google `.html` file must return `200` at its exact URL without redirecting to an extensionless path. If Pages redirects it, use the supported `_worker.js` handler described in [references/cloudflare-pages.md](references/cloudflare-pages.md).
6. Regenerate or stage deployment output using the existing project command. Confirm `robots.txt` allows crawling and points to the correct absolute sitemap URL, and that `sitemap.xml` contains real URLs.
7. Validate locally: exact verification body, no unresolved tokens, manifest inclusion, no private files, canonical URL, sitemap URL, and local links. Run the project's existing tests and output validators.
8. Deploy only when explicitly authorized. For Git-connected Pages, commit generated public changes and push the configured production branch. For direct Wrangler deployment, confirm `npx wrangler whoami` and deploy only a clean public output directory.
9. Verify the live deployment over HTTP. Check status, redirects, body, content type, robots, sitemap, homepage canonical, and the verification URL. A browser showing a fallback page is not proof that the official verification URL works.
10. Complete the Google-side workflow manually: add/choose the URL-prefix property, click Verify, submit `sitemap.xml`, inspect the homepage, and request indexing for the homepage and key pages.

## Scope Boundaries

- Existing website work is out of scope. Do not modify layout, copy, screenshots, routes, ASO, or Android code unless explicitly requested.
- Cloudflare authentication, Git push, Pages settings, DNS, and Search Console clicks are external actions. Ask for authorization or provide the exact next action.
- `pages.dev` does not require a custom domain for URL-prefix verification.
- `google-site-verification=TOKEN` is a DNS record value, not HTML file content.
- A file that returns `200` only after a redirect is not verification-ready.

## Completion Criteria

- Cloudflare production deployment contains the intended commit/output.
- `https://site/`, `robots.txt`, and `sitemap.xml` return `200`.
- The exact Google HTML file URL returns `200` with the exact body, or the exact HTML tag is present in the homepage response.
- Search Console property type matches the verification method.
- The remaining manual Search Console action is clearly stated.

## Handoff

Return the live URL, property type, verification method, deployment status, HTTP check results, sitemap path, and one next manual action. Distinguish local configuration, deployed configuration, and Google-processed data; indexing reports may take hours or days.
