#!/usr/bin/env python3
"""Shrink travel gallery photos in place and (re)build their thumbnails.

For every city under travel/<city>/images/:
  * full-size JPGs are resized to --max-dimension on the long side and re-saved at
    --quality (progressive, optimised). Orientation is baked in, the colour profile
    is kept, and all other metadata (camera EXIF, GPS) is dropped. A file is only
    replaced if the result is smaller, and photos already under --skip-under MB (or
    --max-dimension) are skipped, so the script is safe to re-run after adding a new city.
  * missing thumbnails are written to images/thumbnails/<stem>.JPG (--force-thumbs
    rebuilds all of them). The video poster thumbnails/video.JPG is left alone.
  * camera videos (.MOV/.MP4 from the camera, often 4K HEVC that Chrome can't play)
    are transcoded with ffmpeg to an H.264/AAC <stem>.mp4 at --video-size on the long
    side, web-optimised (+faststart). The original is deleted; point the gallery's
    data-full at the new .mp4.

Usage (from the repo root or travel/):
  python3 travel/optimize_images.py                # every city
  python3 travel/optimize_images.py faro verona    # just these
  python3 travel/optimize_images.py --dry-run      # report only

Keep Pillow < 11 (surya-ocr pins it). HEIC sources need pillow-heif.
"""

from __future__ import annotations

import argparse
import io
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageOps

TRAVEL_DIR = Path(__file__).resolve().parent
JPEG_EXTS = {".jpg", ".jpeg"}
OTHER_EXTS = {".png", ".heic", ".heif"}
VIDEO_EXTS = {".mov", ".m4v", ".mp4"}

try:  # optional HEIC support
  import pillow_heif
  pillow_heif.register_heif_opener()
except ImportError:
  pass


def parse_args() -> argparse.Namespace:
  p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
  p.add_argument("cities", nargs="*", help="City folder names (default: all).")
  p.add_argument("--max-dimension", type=int, default=2560, help="Long side of full images, px.")
  p.add_argument("--quality", type=int, default=85, help="JPEG quality for full images.")
  p.add_argument("--skip-under", type=float, default=2.0,
                 help="Skip full images that are already under this many MB (avoids re-compressing).")
  p.add_argument("--thumb-size", type=int, default=800, help="Long side of thumbnails, px.")
  p.add_argument("--thumb-quality", type=int, default=85, help="JPEG quality for thumbnails.")
  p.add_argument("--force-thumbs", action="store_true", help="Rebuild every thumbnail.")
  p.add_argument("--video-size", type=int, default=1920, help="Long side of videos, px.")
  p.add_argument("--video-crf", type=int, default=23, help="x264 CRF for videos (lower = better).")
  p.add_argument("--video-maxrate", default="8M",
                 help="Bitrate cap so busy scenes (water, foliage) don't balloon.")
  p.add_argument("--dry-run", action="store_true", help="Report what would change; write nothing.")
  return p.parse_args()


def encode(img: Image.Image, size: int, quality: int, icc: bytes | None) -> bytes:
  img = img.copy()
  img.thumbnail((size, size), Image.Resampling.LANCZOS)
  if img.mode not in ("L", "RGB"):
    img = img.convert("RGB")
  buf = io.BytesIO()
  opts = dict(format="JPEG", quality=quality, optimize=True, progressive=True)
  if icc:
    opts["icc_profile"] = icc
  img.save(buf, **opts)
  return buf.getvalue()


def write_atomic(path: Path, data: bytes) -> None:
  tmp = path.with_name(f".{path.name}.tmp")
  tmp.write_bytes(data)
  os.replace(tmp, path)


def transcode_video(path: Path, args: argparse.Namespace) -> int:
  """Re-encode a camera clip to a web-friendly MP4. Returns the resulting size."""
  size = path.stat().st_size
  out = path.with_suffix(".mp4")
  if path.suffix.lower() == ".mp4" and size <= 25e6:
    return size  # already an optimised web MP4
  if not shutil.which("ffmpeg"):
    print(f"  ! {path.name}: ffmpeg not found, video left as is")
    return size
  if size < 1024:
    print(f"  ! {path.name}: looks like a Git LFS pointer, run `git lfs pull` first")
    return size
  if args.dry_run:
    print(f"  {path.name}: {mb(size)} -> {out.name} (transcode)")
    return size
  tmp = path.with_name(f".{path.stem}.tmp.mp4")
  long = args.video_size
  subprocess.run([
      "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(path),
      "-map", "0:v:0", "-map", "0:a:0?", "-map_metadata", "-1",
      "-vf", f"scale='if(gt(iw,ih),{long},-2)':'if(gt(iw,ih),-2,{long})':flags=lanczos",
      "-c:v", "libx264", "-preset", "slow", "-crf", str(args.video_crf),
      "-maxrate", args.video_maxrate, "-bufsize", "16M",
      "-profile:v", "high", "-pix_fmt", "yuv420p",
      "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(tmp),
  ], check=True)
  os.replace(tmp, out)
  if out != path:
    path.unlink()
  new = out.stat().st_size
  print(f"  {path.name}: {mb(size)} -> {out.name} {mb(new)}")
  return new


def mb(n: int) -> str:
  return f"{n / 1e6:.1f} MB"


def process_city(city: Path, args: argparse.Namespace) -> tuple[int, int]:
  images = city / "images"
  thumbs = images / "thumbnails"
  before = after = 0
  files = sorted(p for p in images.iterdir() if p.is_file() and not p.name.startswith("."))

  for path in files:
    ext = path.suffix.lower()
    if ext in OTHER_EXTS:
      print(f"  ! {path.name}: not a JPG, left as is (convert it and update index.html)")
      continue
    if ext in VIDEO_EXTS:
      transcode_video(path, args)
      continue
    if ext not in JPEG_EXTS:
      continue

    size = path.stat().st_size
    before += size
    try:
      with Image.open(path) as raw:
        icc = raw.info.get("icc_profile")
        img = ImageOps.exif_transpose(raw)
        img.load()
    except Exception as exc:  # noqa: BLE001 - keep going
      print(f"  ! {path.name}: cannot open ({exc})", file=sys.stderr)
      after += size
      continue

    small_enough = max(img.size) <= args.max_dimension or size <= args.skip_under * 1e6
    if small_enough:
      after += size
    else:
      data = encode(img, args.max_dimension, args.quality, icc)
      if len(data) < size:
        print(f"  {path.name}: {img.width}x{img.height} {mb(size)} -> {mb(len(data))}")
        if not args.dry_run:
          write_atomic(path, data)
        after += len(data)
      else:
        after += size

    thumb = thumbs / f"{path.stem}.JPG"
    if path.stem.lower().startswith("video"):
      continue  # video posters are hand-made, not gallery photos
    if args.force_thumbs or not thumb.exists():
      print(f"  thumbnail {thumb.name}")
      if not args.dry_run:
        thumbs.mkdir(exist_ok=True)
        write_atomic(thumb, encode(img, args.thumb_size, args.thumb_quality, icc))

  return before, after


def main() -> None:
  args = parse_args()
  if args.cities:
    cities = [TRAVEL_DIR / c for c in args.cities]
  else:
    cities = sorted(p for p in TRAVEL_DIR.iterdir() if (p / "images").is_dir())

  total_before = total_after = 0
  for city in cities:
    if not (city / "images").is_dir():
      print(f"{city.name}: no images/ folder, skipped", file=sys.stderr)
      continue
    print(city.name)
    b, a = process_city(city, args)
    print(f"  {mb(b)} -> {mb(a)}")
    total_before += b
    total_after += a

  label = "would be" if args.dry_run else "now"
  print(f"\nFull-size JPGs: {mb(total_before)} -> {label} {mb(total_after)}")


if __name__ == "__main__":
  main()
