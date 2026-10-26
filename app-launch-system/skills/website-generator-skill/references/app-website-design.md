# App Website Design

Read when creating or restyling an app website. For SiteReport, preserve the direction chosen by the user: TickTick-inspired product presentation with the visual restraint of Things. These references describe layout and hierarchy; do not copy their branding, copy, or assets. For another app, adapt the direction to its verified brand and user preferences.

## Visual direction

- Use a light background, dark readable text, generous but purposeful spacing, and one brand accent. SiteReport uses white, pale blue, navy text, and blue actions.
- Keep app branding, the value proposition, app interface, and Google Play action prominent. Use a side-by-side hero on desktop and a natural stacked flow on phones. Long translated copy may move the interface below the first mobile viewport; preserve readability rather than forcing a fixed hero height.
- A subtle pale background gradient and restrained device shadows are appropriate for the current direction. Avoid prominent decorative gradients, excessive cards, and motion that competes with the product.
- Use a clear display heading and readable body type with system fallbacks. Match hierarchy and spacing on feature, support, privacy, company, and blog pages.
- Use the verified Google Play link and badge as the main action. A secondary walkthrough action is useful when a real video exists; otherwise link to app screenshots.

## Page composition

The current SiteReport homepage flows through a product hero, concise benefits, image-and-text feature stories, a fuller feature overview, workflow steps, screenshot gallery, optional video, relevant guides, and a closing download action. Reuse this sequence where the available content supports it; omit unsupported sections and repeated filler.

Use localized feature names, descriptions, and capabilities in the stories. Link to the actual localized feature route. Keep the footer's crawlable language links alongside the language selector; a JavaScript selector alone does not expose these routes to crawlers.

## Product images

- Reuse verified app screenshots and the existing app icon. Do not invent interface screens, ratings, download counts, reviews, or customers.
- An explicit cover image remains useful, but its existence does not require it to replace the user-approved product hero. Use it where its content fits, such as an explanatory section or video poster. Keep explicit social images for Open Graph.
- `render_product_showcase` and `render_product_stories` in `scripts/generate_website.py` assemble the current display; `.product-device` and `.story-device` in the website stylesheet crop the existing promotional artwork to its phone region.
- Those crop offsets are specific to SiteReport's current 1080 × 1920 promotional images. Before replacing images or reusing the system for another app, inspect their dimensions and framing, then adjust the crop or display uncropped screens. Screenshot count alone does not establish compatible framing. Do not clip app controls or stretch screens to fit.
- Preserve the generator's simpler hero fallback when the available assets cannot support a paired showcase. Do not duplicate a single screenshot to imply multiple screens.
- Make an overflowing screenshot gallery keyboard-focusable and give it an accessible name. The gallery may scroll horizontally; the whole page must remain within the viewport.

## App icon and tab favicon

Copy the verified `assets.icon` into the output and use it for the visible brand and the browser tab. Every generated HTML page with a head, including localized pages, feature pages, blog pages, and 404, must contain one explicit `<link rel="icon" href="…">` referencing that copied icon.

Calculate the path relative to each page. Do not hardcode the root page's relative path into nested pages, a local filesystem path, or a SiteReport-specific filename into the reusable generator. A web manifest icon does not replace the HTML favicon declaration. Keep any separately supplied platform icon variants consistent with the same app identity.

Verify the reference resolves to a nonempty image with a supported browser format. If the metadata has no verified icon, report the missing asset; do not substitute a fabricated logo. Browser favicon caches can outlive a normal reload: use a fresh tab or private window after confirming deployment and the icon response.

## Preserve changes through regeneration

Edit reusable markup in `templates/website-template/` (and `templates/blog-template/` when needed), rendering logic in `scripts/generate_website.py`, and localized copy in the source locale files. Regenerate public files from those sources. Editing only root HTML or `assets/styles.css` will lose changes on the next generation.

Use the CLI's configured metadata and organization inputs. If invoking `generate()` directly for an isolated preview, pass the configured `organization_path` explicitly so publisher details survive. Generate into a temporary directory to review changes before replacing an existing site. Do not overwrite editorial, legal, or unrelated local changes.

## Review

- Run the generator tests and output validation. Check that all HTML icon references resolve, including nested routes, and that regeneration does not duplicate declarations.
- Inspect desktop, tablet, and phone layouts; include a narrow viewport, long translated copy, and RTL when supported. Check image crops, action wrapping, navigation, and page overflow.
- Verify image loading, download destination, video action, gallery keyboard access, and shared inner-page styles. Inspect lazy images in their viewport rather than treating an unscrolled full-page capture as evidence they loaded.
- Preserve confirmed canonical and alternate URLs, structured data, clean navigation URLs, sitemap entries, and indexability during visual changes. A static HTML file may keep its `.html` extension on disk while Cloudflare exposes its clean public URL.
- Deliver a local preview and screenshot for visual review. Commit, push, or deploy only when authorized in the conversation; do not introduce a second approval when the same action is already authorized.
