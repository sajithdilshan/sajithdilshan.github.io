#!/usr/bin/env python3
"""Build numbered contact sheets from travel/<slug>/images/thumbnails/ for review.

Writes /tmp/<slug>-sheet-1.jpg, -2.jpg, ... (20 frames each, 5 x 4, numbered by
file stem) so a whole album can be looked at in a few images instead of one Read
per photo.

Usage (repo root):
  python3 .claude/skills/new-travel-album/scripts/contact_sheet.py <slug>
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[4]
CELL, COLS, ROWS = 300, 5, 4


def key(p: Path):
  return (0, int(p.stem)) if p.stem.isdigit() else (1, p.stem)


def main() -> None:
  slug = sys.argv[1]
  thumbs = sorted((REPO / "travel" / slug / "images" / "thumbnails").glob("*.JPG"), key=key)
  if not thumbs:
    sys.exit("No thumbnails yet; run travel/optimize_images.py first.")
  try:
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
  except OSError:
    font = ImageFont.load_default()
  per = COLS * ROWS
  for i in range(0, len(thumbs), per):
    sheet = Image.new("RGB", (COLS * CELL, ROWS * CELL), "white")
    draw = ImageDraw.Draw(sheet)
    for j, t in enumerate(thumbs[i:i + per]):
      with Image.open(t) as im:
        im.thumbnail((CELL - 10, CELL - 10))
        x, y = (j % COLS) * CELL, (j // COLS) * CELL
        sheet.paste(im, (x + (CELL - im.width) // 2, y + (CELL - im.height) // 2))
      draw.rectangle((x + 4, y + 4, x + 90, y + 40), fill="black")
      draw.text((x + 10, y + 7), t.stem[:6], fill="white", font=font)
    out = Path(f"/tmp/{slug}-sheet-{i // per + 1}.jpg")
    sheet.save(out, quality=80)
    print(out)


if __name__ == "__main__":
  main()
