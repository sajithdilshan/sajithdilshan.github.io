#!/usr/bin/env bash
# Generate a 1200x627 LinkedIn/OG preview PNG for a blog post.
#
# Usage:
#   make-og-image.sh <year> <slug> "<title>" "<kicker>" "<subtitle-or-empty>"
#
# Prerequisite: write the hero SVG inner markup (using gradient id "heroGrad")
# to blog/<year>/images/.hero-<slug>.svg BEFORE running. The script injects it
# into an OG source page (hero on top, title band below), rasterizes it with
# headless Chrome (waiting for the Dancing Script webfont), writes
# blog/<year>/images/og-<slug>.png, and removes the temp files.
#
# Run from the repo root.
set -euo pipefail

YEAR="${1:?year required}"
SLUG="${2:?slug required}"
TITLE="${3:?title required}"
KICKER="${4:?kicker required}"
SUBTITLE="${5:-}"

IMG_DIR="blog/${YEAR}/images"
HERO_SVG_FILE="${IMG_DIR}/.hero-${SLUG}.svg"
SRC_HTML="${IMG_DIR}/.og-${SLUG}-src.html"
OUT_PNG="${IMG_DIR}/og-${SLUG}.png"

if [[ ! -f "$HERO_SVG_FILE" ]]; then
  echo "ERROR: expected hero SVG at $HERO_SVG_FILE (write it before running)." >&2
  exit 1
fi

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if [[ ! -x "$CHROME" ]]; then
  echo "ERROR: Google Chrome not found at expected path." >&2
  exit 1
fi

HERO_SVG_CONTENT="$(cat "$HERO_SVG_FILE")"

# Optional subtitle line (only rendered when non-empty).
SUB_HTML=""
if [[ -n "$SUBTITLE" ]]; then
  SUB_HTML="<div class=\"sub\">${SUBTITLE}</div>"
fi

cat > "$SRC_HTML" <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Lora:wght@400;600&display=swap" rel="stylesheet" />
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body { width: 1200px; height: 627px; }
    body { font-family: "Lora", serif; background: #0f0f1a; overflow: hidden; }
    .hero { width: 1200px; height: 400px; display: block; }
    .hero svg { width: 1200px; height: 400px; display: block; }
    .band {
      height: 227px; background: #0f0f1a;
      display: flex; flex-direction: column;
      align-items: center; justify-content: center; text-align: center;
      border-top: 1px solid #2a2745;
    }
    .kicker {
      font-size: 20px; font-weight: 600; text-transform: uppercase;
      letter-spacing: 0.2em; color: #a0a0b8; margin-bottom: 14px;
    }
    .title {
      font-family: "Dancing Script", cursive; font-size: 84px; font-weight: 700;
      line-height: 1; color: #ffffff;
    }
    .sub { font-size: 24px; color: #a0a0b8; margin-top: 12px; }
  </style>
</head>
<body>
  <div class="hero">${HERO_SVG_CONTENT}</div>
  <div class="band">
    <div class="kicker">${KICKER}</div>
    <div class="title">${TITLE}</div>
    ${SUB_HTML}
  </div>
</body>
</html>
EOF

ABS_SRC="file://$(cd "$(dirname "$SRC_HTML")" && pwd)/$(basename "$SRC_HTML")"

"$CHROME" --headless --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=1 --window-size=1200,627 \
  --virtual-time-budget=10000 \
  --screenshot="$OUT_PNG" "$ABS_SRC" 2>/dev/null

rm -f "$SRC_HTML" "$HERO_SVG_FILE"

if command -v sips >/dev/null 2>&1; then
  echo "Generated $OUT_PNG"
  sips -g pixelWidth -g pixelHeight "$OUT_PNG" 2>/dev/null | grep -E "pixel" || true
else
  echo "Generated $OUT_PNG"
fi
