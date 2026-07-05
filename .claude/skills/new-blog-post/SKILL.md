---
name: new-blog-post
description: Convert a Markdown blog post into a fully styled HTML page for sajith.me — generates a bespoke SVG hero, a matching index thumbnail, a 1200x627 LinkedIn/OG preview image, wires up all Open Graph + Twitter meta tags, and adds the post card to blog/index.html. Use when the user has written a new .md post under blog/ and wants it published, or says "convert this post", "publish this blog post", "add this post to the blog". Accepts the Markdown file path as input.
---

# New Blog Post Publisher

Turns a Markdown draft into a published post on `sajith.me`, matching the exact
look of the existing posts. The domain is **https://sajith.me** and posts live at
`blog/<year>/<slug>.html`.

## Input

The Markdown file path, e.g. `blog/2026/my_new_post.md`. If not given, ask for it.

## Step 0 — Gather metadata (ask interactively)

Read the Markdown file first. Then ask the user for these, showing a sensible
suggestion derived from the content that they can accept or override:

- **Title** — default: the top-level `# H1` in the Markdown.
- **Date** — the publish date (e.g. "Jul 5, 2026"). No default; ask.
- **Kicker** — short uppercase category shown above the title on the OG card and
  as the eyebrow, e.g. "Essay", "Developer Workflow", "Notes". Suggest one.
- **Description** — one compelling sentence, **≤ 155 characters**, for the meta
  description / OG description / index excerpt. Suggest a draft from the intro.
- **Reading time** — default: estimate at ~200 words/min, rounded up ("3 min read").

Derive the **slug** from the Markdown filename (without extension). Derive the
**year** from the folder the `.md` sits in (e.g. `blog/2026/`). The HTML output
path is the same folder + `<slug>.html`.

## Step 1 — Design a bespoke hero SVG

Create a unique 1200×400 `viewBox` SVG themed to the post's topic (like the
looping arcs for "Hedonic Treadmill" or the IDE mockup for the Claude Code post).
Guidelines:

- Use the brand gradient `#ff8a00 → #ff3e55 → #9145ff → #32c8ff` for arcs/accents,
  or the purple set `#c4bfff → #a29bfe → #6c5ce7` for UI-style scenes.
- Background rect uses `fill="var(--card-bg)"` so it adapts to light/dark themes.
- Keep it abstract or lightly illustrative; readable at small sizes.
- Also design a **matching mini thumbnail** as a 100×100 `viewBox` SVG (simplified
  version of the hero motif) for the index card. Use a unique gradient id per post
  (e.g. `t3`, `t4`, …) so ids don't collide on the index page.

See `reference/post-template.html` for exactly where the hero SVG goes.

## Step 2 — Convert Markdown body to HTML

Convert the Markdown body (everything after the H1) into the `.post-body` markup:

- Paragraphs → `<p>…</p>`.
- Links `[text](url)` → `<a href="url" target="_blank" rel="noreferrer">text</a>`.
- Inline code `` `x` `` → `<code>x</code>` (add the `.post-body code` style block
  from `reference/optional-styles.css` only if the post uses inline code).
- Images `![alt](path)` → a `<figure class="post-figure"><img …></figure>` (add the
  `.post-figure` styles + the lightbox markup/JS from `reference/optional-styles.css`
  and `reference/lightbox.html` only if the post has images).
- Lists → `<ol>`/`<ul>`. For a numbered process/workflow, consider the scroll
  timeline pattern, but a plain list is fine — keep it simple unless asked.
- Preserve the author's wording verbatim; do not rewrite prose.

## Step 3 — Assemble the HTML page

Copy `reference/post-template.html` verbatim and fill the `{{PLACEHOLDERS}}`:

- `{{TITLE}}` — post title (used in `.post-title`, `<title>` as `SE: {{TITLE}}`,
  `og:title`, `twitter:title`).
- `{{DESCRIPTION}}` — the ≤155-char description (meta description, og/twitter desc).
- `{{CANONICAL_URL}}` — `https://sajith.me/blog/<year>/<slug>.html`.
- `{{OG_IMAGE_URL}}` — `https://sajith.me/blog/<year>/images/og-<slug>.png`.
- `{{META}}` — the eyebrow line, e.g. `Jul 5, 2026 &middot; 4 min read`.
- `{{HERO_SVG}}` — the hero SVG from Step 1.
- `{{BODY}}` — the converted body from Step 2.

Write the result to `blog/<year>/<slug>.html`.

## Step 4 — Generate the OG / LinkedIn preview image (1200×627)

Use the helper script — it builds an OG source HTML from the hero SVG + a title
band, rasterizes it with headless Chrome (waiting for the webfont), and writes the
PNG. Run:

```
scripts/make-og-image.sh <year> <slug> "<title>" "<kicker>" "<subtitle-or-empty>"
```

- `<subtitle>` is optional flavor text under the title (the Claude Code card used
  "How my developer workflow changed"). Pass `""` for none.
- Output: `blog/<year>/images/og-<slug>.png`, exactly 1200×627.
- The script needs the hero SVG. Before running it, write the hero SVG (the inner
  markup, using gradient id `heroGrad`) to `blog/<year>/images/.hero-<slug>.svg`;
  the script injects it. The script deletes this temp file and the temp source HTML
  when done.

After it runs, verify the PNG is 1200×627 (`sips -g pixelWidth -g pixelHeight`) and
Read it to confirm the title rendered in the Dancing Script cursive (not a serif
fallback). If it fell back, the font didn't load — re-run; the script already uses
`--virtual-time-budget`.

## Step 5 — Add the post to blog/index.html

Insert a new `<li class="post-item">` as the **first** child of the `.post-list`
(newest first) inside the correct `.year-section`. If a `.year-section` for the
post's year doesn't exist yet, create one (copy the existing `<section
class="year-section">` structure with the new `<h2 class="year-label">YEAR</h2>`).

Use `reference/index-card.html` as the card template and fill:

- `{{HREF}}` — `./<year>/<slug>.html`.
- `{{THUMB_SVG}}` — the 100×100 thumbnail SVG from Step 1 (unique gradient id).
- `{{DATE_SHORT}}` — short date + reading time, e.g. `Jul 5, 2026 &middot; 4 min`.
- `{{TITLE}}` — post title.
- `{{EXCERPT}}` — the description (can reuse the ≤155-char description).

## Step 6 — Verify

- Open the new post and the index in the browser (`open blog/<year>/<slug>.html
  blog/index.html`) and confirm hero, body, and the new index card render.
- Confirm the OG PNG looks right (Step 4).
- Report the file paths created/changed and remind the user: OG tags only take
  effect once pushed live to sajith.me — re-scrape via LinkedIn Post Inspector
  (https://www.linkedin.com/post-inspector/).

## Constraints

- Match the existing posts' styling exactly (self-contained inline `<style>` per
  page — do not extract a shared stylesheet).
- Titles are Dancing Script; body is Lora; code is monospace.
- Keep OG title text short so nothing truncates; description ≤155 chars.
- Do not push to git or commit unless the user asks.
