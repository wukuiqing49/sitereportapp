# Blog Template Contract

## Template selection

| Template ID | Source file | Use for | Required structure |
| --- | --- | --- | --- |
| `blog-index` | `pages/index.html` | Blog landing and locale archive | Featured item, article list, categories |
| `standard-article` | `pages/article.html` | Launch, feature, use-case, and educational posts | Answer-first introduction, body, limitations, related content |
| `tutorial` | `pages/tutorial.html` | Ordered workflows and how-to guides | Prerequisites, numbered steps, result, limitations |
| `release-notes` | `pages/release-notes.html` | Verified version or change summaries | Version, release date, grouped changes, compatibility notes |

Do not use `release-notes` without verified version and change evidence. Use `standard-article` when a tutorial has no executable sequence.

## Output layout

Write public pages directly under the project root and keep editable content separate:

```text
<project-root>/
|-- assets/
|   |-- styles.css
|   |-- blog.css
|   |-- blog.js
|   `-- locale-router.js
|-- blog/
|   |-- index.html
|   `-- <locale>/<slug>/index.html
`-- content/blog/
    |-- content-plan.yaml
    |-- localization-status.yaml
    `-- <locale>/<slug>.md
```

When the root website does not exist, still render public blog pages under `<project-root>/blog/`, copy the website base stylesheet to `<project-root>/assets/styles.css`, and preserve the same relative URL structure.

For a single locale, the index may live at `blog/index.html` and articles at `blog/<slug>/index.html`. For multiple locales, use BCP 47 locale directories consistently for both indexes and articles.

Keep the source-locale blog index at `blog/index.html` and source articles at `blog/<slug>/index.html`. Put non-source indexes at `blog/<locale>/index.html` and their articles at `blog/<locale>/<localized-slug>/index.html`. Generate per-page route JSON only for equivalents that exist. Enable automatic detection on the source index and source articles, but never on locale-directory pages.

## Shared visual contract

Load the website's `assets/styles.css` before `assets/blog.css`. Keep these shared variables unchanged unless the generated website changes them too:

- `--ink`, `--muted`, `--surface`, `--soft`, and `--line`
- `--accent`, `--accent-strong`, and `--focus`
- `--max`

Use the same brand header, logo, navigation order, footer links, button treatment, 8px maximum corner radius, focus treatment, and reduced-motion behavior as the website. Use real product screenshots as editorial evidence, with an aspect ratio and descriptive localized alt text. Omit an unsupported image instead of leaving an empty container.

## Rendering rules

- Replace every `{{TOKEN}}`; remove optional blocks that have no verified content.
- Emit exactly one descriptive `h1` per page.
- Keep article reading width near 46rem and use the wide column only for verified media, tables, or step layouts.
- Generate a visible table of contents only for pages with at least three `h2` sections.
- Add `Article` JSON-LD only when author and date fields match visible content. Omit unknown author properties.
- Add `HowTo` JSON-LD only when the tutorial exposes the same complete steps and requirements. Remove the entire JSON-LD script when it is not eligible.
- Use `<time datetime="...">` with an ISO value and localized visible date.
- Keep category names factual and avoid empty filter controls.
- Render related items only when their target pages exist.
- Do not add newsletter forms, comments, ratings, reading counts, or social proof unless the project supplies a real service and verified data.
- Build every article from the feature's structured `details`; do not expand `feature.name` and a one-line description into generic select/configure/process/review prose.
- Skip article generation when the feature lacks a verified problem, capabilities, inputs, outputs, options, executable steps, limitations, or FAQ.
- Treat `analysis.validatedAt` and `analyzedAt` as analysis metadata only. Use explicit `editorial.publishedAt`/`updatedAt`, or keep the article as a dateless draft and omit `Article`/`HowTo` date markup.

## Repeated blocks

Render index and related items as individual cards:

```html
<article class="article-card">
  <a href="ARTICLE_URL"><img src="IMAGE_PATH" alt="IMAGE_ALT" width="720" height="450"></a>
  <div class="article-card-content">
    <p class="article-kicker">CATEGORY</p>
    <h3><a href="ARTICLE_URL">TITLE</a></h3>
    <p>SUMMARY</p>
    <div class="article-meta">DATE_AND_TYPE</div>
  </div>
</article>
```

Render tutorial steps with stable IDs used by the table of contents:

```html
<section class="tutorial-step" id="step-1">
  <span class="tutorial-step-number" aria-hidden="true">1</span>
  <h2>STEP_TITLE</h2>
  <p>STEP_INSTRUCTIONS</p>
  VERIFIED_STEP_MEDIA
</section>
```

Render each release category as a section with a factual list:

```html
<section class="change-group" id="improvements">
  <h2>GROUP_TITLE</h2>
  <ul>VERIFIED_CHANGE_ITEMS</ul>
</section>
```
