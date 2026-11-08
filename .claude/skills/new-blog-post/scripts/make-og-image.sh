#!/usr/bin/env bash
# Generate a 1200x627 LinkedIn/OG preview PNG for a blog post.
#
# Usage (from the repo root):
#   make-og-image.sh <post.html> <out.png> "<kicker>" ["<title override>"]
#
# Pulls the hero <svg> out of the post's .post-hero block and the text of its
# h1.post-title, lays them out as hero (1200x400) over a title band (1200x227) in
# the site's dark palette (Source Serif 4), and screenshots it with headless
# Chrome. CSS vars used by heroes (--wash, --accent, --ink, ...) are defined, so
# theme-aware heroes render in their dark-mode colours.
set -euo pipefail

POST="${1:?post html required}"
OUT="${2:?output png required}"
KICKER="${3:?kicker required}"
TITLE_OVERRIDE="${4:-}"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[[ -x "$CHROME" ]] || { echo "ERROR: Google Chrome not found." >&2; exit 1; }

SRC="$(mktemp -t og-src).html"
trap 'rm -f "$SRC"' EXIT

python3 - "$POST" "$SRC" "$KICKER" "$TITLE_OVERRIDE" <<'PY'
import re, sys, html
post, src, kicker, title = sys.argv[1:5]
s = open(post, encoding="utf-8").read()
hero = re.search(r'<div class="post-hero[^"]*">\s*(<svg.*?</svg>)', s, re.S)
if not hero:
    sys.exit("ERROR: no .post-hero <svg> found in " + post)
if not title:
    m = re.search(r'<h1 class="post-title">(.*?)</h1>', s, re.S)
    title = html.unescape(re.sub(r"\s+", " ", m.group(1)).strip()) if m else ""
page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8" />
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet" />
<style>
  :root {{ --paper:#0f141e; --ink:#e7eaf0; --soft:#98a0ae; --faint:#6d7684; --rule:#1e2530;
          --accent:#9bb8e0; --wash:#151c28; --ring:rgba(255,255,255,.09); }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html, body {{ width:1200px; height:627px; overflow:hidden; background:var(--paper); }}
  body {{ font-family:"Source Serif 4", Georgia, serif; }}
  .hero, .hero svg {{ width:1200px; height:400px; display:block; }}
  .band {{ height:227px; display:flex; flex-direction:column; align-items:center; justify-content:center;
          text-align:center; border-top:1px solid var(--rule); padding:0 60px; }}
  .kicker {{ font-size:20px; font-weight:600; letter-spacing:.18em; text-transform:uppercase;
            color:var(--faint); margin-bottom:16px; }}
  .title {{ font-size:66px; font-weight:600; line-height:1.08; color:var(--ink); letter-spacing:-.01em; }}
</style></head><body>
<div class="hero">{hero.group(1)}</div>
<div class="band"><div class="kicker">{html.escape(kicker)}</div><div class="title">{html.escape(title)}</div></div>
</body></html>"""
open(src, "w", encoding="utf-8").write(page)
PY

"$CHROME" --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --window-size=1200,627 --virtual-time-budget=10000 \
  --screenshot="$OUT" "file://$SRC" 2>/dev/null

echo "Generated $OUT"
sips -g pixelWidth -g pixelHeight "$OUT" 2>/dev/null | grep pixel || true
