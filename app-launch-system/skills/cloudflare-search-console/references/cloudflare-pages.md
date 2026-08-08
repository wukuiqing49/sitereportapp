# Cloudflare Pages Deployment

## Git-connected Pages

Inspect Pages settings before changing them:

- Production branch must match the branch being pushed.
- Build command must generate the site, or be empty when committed output is already final.
- Output directory must contain only public deployment files.
- If a build runs in the repository root, do not upload `.` when private source files are present. Stage files listed in `static-site-manifest.json` into a clean output directory.

After a push, wait for Pages to finish and check the deployed commit in Cloudflare. A successful Git push does not prove Pages built the new commit.

## Direct Wrangler deployment

Only run this when authorized and authenticated:

```powershell
npx wrangler whoami
npx wrangler pages deploy <public-output> --project-name <pages-project>
```

Do not deploy the repository root. The output must contain only manifest-listed files, including required `_headers`, `_worker.js`, verification file, assets, routes, `robots.txt`, and `sitemap.xml`.

## Live checks

Keep redirects visible:

```powershell
curl.exe -sS -D - -o NUL https://site.pages.dev/
curl.exe -sS -D - -o NUL https://site.pages.dev/robots.txt
curl.exe -sS -D - -o NUL https://site.pages.dev/sitemap.xml
curl.exe -sS -D - -o - https://site.pages.dev/google1234567890abcdef.html
```

For a Google HTML file, require HTTP `200`, the exact official path including `.html`, and the exact body. Treat `301`, `302`, `307`, `308`, `403`, `404`, fallback content, or an extensionless URL as failed.

## Clean URLs and `_worker.js`

Cloudflare Pages can redirect `file.html` to `file`; `_redirects` may not override this built-in cleanup. When HTML-file verification is required, use a Pages `_worker.js` handler for the exact path:

```javascript
const verificationPath = "/google1234567890abcdef.html";
const verificationContent = "google-site-verification: google1234567890abcdef.html\n";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === verificationPath) {
      return new Response(verificationContent, {
        status: 200,
        headers: { "content-type": "text/html; charset=UTF-8" }
      });
    }
    return env.ASSETS.fetch(request);
  }
};
```

Generate this from the exact user-provided Google values. Never paste a guessed token.

