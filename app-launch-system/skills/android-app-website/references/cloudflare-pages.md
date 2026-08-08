# Cloudflare Pages Static Output

The generated website must be deployable as static files without a build command.

## Public files

- `index.html` is the root entry.
- All HTML, CSS, JavaScript, images, manifests, and locale routes use relative paths.
- `404.html` is the root fallback page.
- `_headers` supplies conservative security headers and short-lived asset caching.
- `static-site-manifest.json` is the authoritative list of deployable public files.
- No local absolute path may appear in public files.
- No generated page depends on PHP, Node, a database, an API, Pages Functions, or server-side locale negotiation.

## Deployment boundary

The site source root also contains private generation inputs such as `app-launch-system/`, `app-info.yaml`, and `analysis-evidence.json`. Do not upload the entire source root blindly. When deployment is explicitly requested, stage only files listed in `static-site-manifest.json` before invoking Cloudflare tooling. Never publish Android source, analysis evidence, locale source files, or plugin configuration.

## Verification

- Open the root and localized pages through a static HTTP server.
- Confirm that direct locale URLs remain stable and source-root language detection works.
- Confirm all local links and images resolve.
- Confirm `_headers` and `404.html` are present.
- Confirm `sitemap.xml` contains absolute URLs only when `websiteUrl` is verified.
- Treat deployment and domain configuration as separate explicit operations.
