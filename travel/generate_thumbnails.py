#!/usr/bin/env python3
"""Generate scaled thumbnails for the Naples gallery images."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageOps


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(
      description=(
          "Create thumbnails for the Naples gallery while preserving aspect ratio."
      ))
  parser.add_argument(
      "--source-dir",
      type=Path,
      default=Path("./naples/images"),
      help="Directory containing the original images.",
  )
  parser.add_argument(
      "--output-dir",
      type=Path,
      default=Path("./naples/images/thumbnails"),
      help="Directory where thumbnails will be written.",
  )
  parser.add_argument(
      "--max-dimension",
      type=int,
      default=800, #3213
      help="Maximum width/height (in px) for the thumbnail's longest side.",
  )
  parser.add_argument(
      "--quality",
      type=int,
      default=85,
      help="JPEG quality for saved thumbnails.",
  )
  parser.add_argument(
      "--force",
      action="store_true",
      help="Recreate thumbnails even if they already exist.",
  )
  parser.add_argument(
      "--suffix",
      default="",
      help="Text appended to the original filename before the extension.",
  )
  return parser.parse_args()


def ensure_dirs(source_dir: Path, output_dir: Path) -> None:
  if not source_dir.exists():
    raise FileNotFoundError(f"Source directory not found: {source_dir}")
  output_dir.mkdir(parents=True, exist_ok=True)
  if source_dir.resolve() == output_dir.resolve():
    raise ValueError("Output directory must be different from the source directory.")


def thumbnail_path(
    original: Path,
    output_dir: Path,
    suffix: str,
) -> Path:
  return output_dir / f"{original.stem}{suffix}.JPG"


def create_thumbnail(
    source_file: Path,
    dest_file: Path,
    max_dimension: int,
    quality: int,
) -> None:
  with Image.open(source_file) as img:
    img = ImageOps.exif_transpose(img)
    img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
    if img.mode not in ("L", "RGB"):
      img = img.convert("RGB")
    img.save(dest_file, format="JPEG", quality=quality, optimize=True)


def generate_thumbnails(
    source_dir: Path,
    output_dir: Path,
    max_dimension: int,
    quality: int,
    force: bool,
    suffix: str,
) -> None:
  ensure_dirs(source_dir, output_dir)

  image_files = sorted(
      [
          path for path in source_dir.iterdir()
          if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".heic", ".heif"}
      ])

  if not image_files:
    print(f"No supported image files found in {source_dir}", file=sys.stderr)
    return

  for path in image_files:
    dest = thumbnail_path(path, output_dir, suffix)
    if dest.exists() and not force:
      print(f"Skipping existing thumbnail: {dest}")
      continue
    try:
      create_thumbnail(path, dest, max_dimension, quality)
      print(f"Created {dest}")
    except Exception as exc:  # noqa: BLE001 - want to keep going
      print(f"Failed to process {path}: {exc}", file=sys.stderr)


def main() -> None:
  args = parse_args()
  generate_thumbnails(
      source_dir=args.source_dir,
      output_dir=args.output_dir,
      max_dimension=args.max_dimension,
      quality=args.quality,
      force=args.force,
      suffix=args.suffix,
  )


if __name__ == "__main__":
  main()
