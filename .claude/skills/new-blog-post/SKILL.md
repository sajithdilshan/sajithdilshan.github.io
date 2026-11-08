---
name: new-blog-post
description: Convert a Markdown blog post into a fully styled HTML page for sajith.me — generates a bespoke theme-aware SVG hero, a 1200x627 LinkedIn/OG preview image, wires up Open Graph + Twitter meta tags, links it into the older post's prev/next nav, and adds it to the "What I've written" list on the root index.html. Use when the user has written a new .md post under blog/ and wants it published, or says "convert this post", "publish this blog post", "add this post to the blog". Accepts the Markdown file path as input.
---

# New Blog Post Publisher

Turns a Markdown draft into a published post on `https://sajith.me`. Posts live at `blog/<year>/<slug>.html`. The site shares one stylesheet (`assets/css/main.css`) and small JS files (`assets/js/`), so posts contain markup only — no inline `<style>` blocks. Typeface is Source Serif 4 throughout; light/dark is handled by CSS variables plus the theme toggle.

The most recent post (newest `blog/<year>/*.html`) is the ground truth for structure. If it disagrees with these references, follow the post and update the references.

## Input

The Markdown file path, e.g. `blog/2026/my_new_post.md`. If not given, ask for it.

## Step 0 — Metadata

Read the Markdown. It may start with a list-style header (`- title: …`, `- date: YYYY-MM-DD`); otherwise use the `# H1`. Ask only for what's missing, offering a suggestion:

- **Title**, **Date** (shown as `8 Nov 2026`).
- **Kicker** for the OG card, e.g. "Essay", "Developer Workflow", "Side Project" (rendered as `KICKER · YEAR`).
- **Description** — one sentence, **≤ 155 chars**, used for meta/OG/Twitter.
- **Excerpt** for the index list — one short sentence (may differ from the description).
- **Reading time** — ~200 words/min, rounded up.

Slug = filename without extension; year = the folder.

## Step 1 — Hero SVG

A unique `viewBox="0 0 1200 400"` SVG with `preserveAspectRatio="xMidYMid slice"`, a `role="img"` and `aria-label`. It's displayed 160–260px tall, so keep the subject inside roughly y 70–330 and x 250–950.

- Make it theme-aware: background `<rect fill="var(--wash)">`, strokes/fills with `var(--accent)`, `var(--ink)`, `var(--paper)`, `var(--rule)` and opacity for tints (see `hedonic_treadmill.html`, `first_ios_app.html`). Hard-coded colours are fine for a dark "screenshot" scene (see `six_months_with_claude_code.html`).
- Abstract or lightly illustrative; readable small. No thumbnail is needed.

## Step 2 — Body

Convert the body to `.post-body` markup using `reference/body-snippets.html` (paragraphs, links with `target="_blank" rel="noreferrer"`, figures, linked figures, phone videos, lightbox, workflow timeline). Preserve the author's wording verbatim; use `&rsquo;` for apostrophes. Load `gallery.js` / `workflow.js` only when the post uses them.

## Step 3 — Page

Copy `reference/post-template.html`, fill the `{{PLACEHOLDERS}}` (canonical URL `https://sajith.me/blog/<year>/<slug>.html`, OG image `https://sajith.me/blog/<year>/images/og-<slug>.png`, meta line `8 Nov 2026 &middot; 3 min read`) and write `blog/<year>/<slug>.html`. The post nav links to the previous newest post as "Older post".

## Step 4 — OG / LinkedIn image

```
.claude/skills/new-blog-post/scripts/make-og-image.sh blog/<year>/<slug>.html blog/<year>/images/og-<slug>.png "<Kicker> · <year>" ["<short title>"]
```

The script takes the hero and title straight from the HTML and renders them in the dark palette. Pass a short title override if the H1 is long. Read the PNG to confirm it's 1200×627, the title fits on one or two lines, and the font is Source Serif (not a fallback; re-run if so).

## Step 5 — Link it in

- Root `index.html`: insert `reference/index-card.html` as the first `<li>` of `<ul class="entries">`.
- The previous newest post: add a "Newer post" link in its `<nav class="post-nav">` (after any "Older post" link).

## Step 6 — Verify

- Check every relative `href`/`src`/`poster` in the new page resolves.
- Screenshot the page with headless Chrome (`--window-size=900,2600 --virtual-time-budget=5000`) and Read it.
- Report files created/changed. Remind the user that OG tags only work once pushed; re-scrape via https://www.linkedin.com/post-inspector/.

## Constraints

- No inline `<style>`; add any new shared rule to `assets/css/main.css`.
- Description ≤ 155 chars; keep the OG title short.
- Do not commit or push unless asked.
