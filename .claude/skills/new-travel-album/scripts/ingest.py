#!/usr/bin/env python3
"""Copy a folder of camera photos/videos into travel/<slug>/images/, in shooting order.

Photos become 1.JPG, 2.JPG, ... sorted by EXIF DateTimeOriginal (falling back to
file mtime). HEIC/PNG are converted to JPG. Videos keep their camera name
(e.g. DSCF2031.MOV) and are left for optimize_images.py to transcode. Prints a
manifest (number, original name, capture time) so captions can be traced back.

Usage (repo root):
  python3 .claude/skills/new-travel-album/scripts/ingest.py <source-dir> <slug> [--dry-run]
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image

try:
  import pillow_heif
  pillow_heif.register_heif_opener()
except ImportError:
  pillow_heif = None

PHOTO = {".jpg", ".jpeg", ".heic", ".heif", ".png"}
VIDEO = {".mov", ".mp4", ".m4v"}
REPO = Path(__file__).resolve().parents[4]


def taken(path: Path) -> datetime:
  if path.suffix.lower() in PHOTO:
    try:
      with Image.open(path) as im:
        raw = im.getexif().get_ifd(0x8769).get(36867) or im.getexif().get(306)
        if raw:
          return datetime.strptime(str(raw).strip(), "%Y:%m:%d %H:%M:%S")
    except Exception:  # noqa: BLE001 - fall back to mtime
      pass
  return datetime.fromtimestamp(path.stat().st_mtime)


def main() -> None:
  ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
  ap.add_argument("source", type=Path)
  ap.add_argument("slug")
  ap.add_argument("--dry-run", action="store_true")
  a = ap.parse_args()

  dest = REPO / "travel" / a.slug / "images"
  if dest.exists() and any(dest.iterdir()):
    sys.exit(f"{dest} is not empty; refusing to overwrite. Remove it or pick another slug.")

  files = [p for p in a.source.iterdir() if p.is_file() and p.suffix.lower() in PHOTO | VIDEO]
  files.sort(key=lambda p: (taken(p), p.name))
  if not files:
    sys.exit(f"No photos or videos in {a.source}")

  if not a.dry_run:
    dest.mkdir(parents=True, exist_ok=True)
  n = 0
  for p in files:
    ext = p.suffix.lower()
    if ext in VIDEO:
      target = dest / p.name
      if not a.dry_run:
        shutil.copy2(p, target)
    else:
      n += 1
      target = dest / f"{n}.JPG"
      if not a.dry_run:
        if ext in {".jpg", ".jpeg"}:
          shutil.copy2(p, target)
        else:
          if ext in {".heic", ".heif"} and pillow_heif is None:
            sys.exit("HEIC found but pillow-heif is not installed. Install a version that "
                     "works with Pillow < 11 and check pip doesn't upgrade Pillow.")
          with Image.open(p) as im:
            icc = im.info.get("icc_profile")
            im.convert("RGB").save(target, "JPEG", quality=95, exif=im.getexif(),
                                   **({"icc_profile": icc} if icc else {}))
    print(f"{target.name:>14}  <- {p.name:<20} {taken(p):%Y-%m-%d %H:%M}")
  print(f"\n{n} photos, {len(files) - n} videos -> {dest.relative_to(REPO)}"
        + (" (dry run)" if a.dry_run else ""))


if __name__ == "__main__":
  main()
