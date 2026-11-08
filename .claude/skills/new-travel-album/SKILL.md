---
name: new-travel-album
description: Add a new travel photo/video album to sajith.me — copies camera photos and clips into travel/<city>/images in shooting order, shrinks photos and transcodes videos with travel/optimize_images.py, builds thumbnails and video posters, writes a chaptered gallery page (travel/<city>/index.html) with captions, and links it into the "Where I've been" strip and the "Next city" ring. Use when the user says "add a new travel album", "add photos from <city>", "new gallery", or points at a folder of trip photos.
---

# New Travel Album

Turns a folder of camera photos/videos into a gallery at `travel/<slug>/index.html`. All styling and the lightbox live in `assets/css/main.css` and `assets/js/gallery.js`; the page is markup only. **`travel/faro/index.html` is the reference layout** (chaptered reels with captions) — copy its structure. The older cities use a plain grid; don't use that for new albums.

## Step 0 — Ask

Ask for what you can't infer (suggest defaults):

- **Source folder** of originals (e.g. `~/Pictures/Lisbon`), and the **city**. Slug = lowercase, hyphenated (`amalfi-coast`).
- **Title** — a short line like "Faro, the beaches and good food". **Place** ("Faro, Portugal"), **camera** (default: read EXIF `Model`, e.g. "Fujifilm X-E5"), **month and year** (default: from EXIF).
- Any **notes or stories** from the trip — the lead and chapter text should sound like the user, not a travel brochure. If they give none, keep the text short and factual about what's in the photos.
- **Position** in the "Where I've been" strip on the root `index.html` (default: first).

## Step 1 — Ingest

```
python3 .claude/skills/new-travel-album/scripts/ingest.py <source-dir> <slug>
```

Copies photos as `1.JPG … N.JPG` sorted by capture time (HEIC/PNG converted to JPG) and videos under their camera names. It refuses to overwrite a non-empty folder. Keep the printed manifest; it maps numbers back to original filenames.

## Step 2 — Optimise

```
python3 travel/optimize_images.py <slug>
```

Photos → 2560px long side, q85, metadata (incl. GPS) stripped. Thumbnails → `images/thumbnails/<n>.JPG` at 800px. Videos → 1080p H.264/AAC `<stem>.mp4` (original MOV deleted) plus a poster `images/thumbnails/<stem>.JPG`. Requires ffmpeg (`/opt/homebrew/bin/ffmpeg`). Keep Pillow < 11. Check no file in `travel/<slug>` is over ~3 MB.

## Step 3 — Look and plan chapters

```
python3 .claude/skills/new-travel-album/scripts/contact_sheet.py <slug>
```

Read each `/tmp/<slug>-sheet-*.jpg` (20 numbered frames per sheet; far cheaper than reading photos one by one). Then:

- Group the frames into 3–7 **chapters** that follow the trip (a place, a day, a theme). Shooting order is the default; small reorders are fine. Drop near-duplicates or weak frames only if the user agrees.
- For each chapter write a title (2–4 words) and 1–2 sentences of text.
- For each frame write a short caption (3–6 words, sentence case, no full stop) describing what's actually in it. It's used for both `alt` and `figcaption`.
- Put each video in the chapter where it was shot.

Show the plan (chapters → frame numbers, titles, text) and get a quick OK before writing HTML.

## Step 4 — Write the page

Copy `travel/faro/index.html` to `travel/<slug>/index.html` and replace the content, keeping head, bar, lightbox and footer exactly as they are. Fill in `<title>` (`<Title> &mdash; Sajith Edirisinghe`), the meta description (≤155 chars), `h1.page-title`, `p.lead`, and the three `hero__meta` spans. Then one block per chapter:

```html
    <section class="chapter up">
      <div class="chapter__head">
        <h2 class="chapter__title">Chapter title</h2>
        <p class="chapter__text">One or two sentences.</p>
      </div>
      <div class="reel">
        <div class="reel__frames">
          <figure class="gallery-item" data-full="./images/1.JPG">
            <img loading="lazy" src="./images/thumbnails/1.JPG" alt="Caption" />
            <figcaption>Caption</figcaption>
          </figure>
          <figure class="gallery-item gallery-item--video" data-type="video" data-full="./images/DSCF1234.mp4">
            <img src="./images/thumbnails/DSCF1234.JPG" alt="Caption" />
            <span class="play-badge" aria-hidden="true">&#9654;</span>
            <figcaption>Caption</figcaption>
          </figure>
        </div>
      </div>
    </section>
```

Give the first two sections `up d2` and `up d3` (as in faro), the rest just `up`. Use `gallery-item--45` for frames that should crop to 4:5. Escape text as HTML entities (`&rsquo;`, `&mdash;`, `&amp;`).

## Step 5 — Link it in

- **Root `index.html`**, the `.strip` under "Where I've been": add `<a href="travel/<slug>/index.html"><img src="travel/<slug>/images/thumbnails/<n>.JPG" alt="" loading="lazy" /><span>City</span></a>` at the chosen position. Pick a strong, recognisable frame for `<n>`.
- **"Next city" ring**: each city's `nav.post-nav` links to the next city in strip order, and the last one wraps to the first. Point the new page at the city after it, and change the city before it to point at the new one.

## Step 6 — Verify

- Check every `href`/`src`/`data-full` in the new page and root `index.html` resolves to a file.
- Screenshot the page with headless Chrome (`--window-size=1300,2400 --virtual-time-budget=5000`) and Read it; check the chapters, reels and captions look right.
- `git add travel/<slug> index.html <previous city>/index.html` and show the user the total size (`du -sh travel/<slug>`). Don't commit or push unless asked.
