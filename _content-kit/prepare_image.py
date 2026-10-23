#!/usr/bin/env python3
"""Create web-ready copies of lab photos without retouching them.

The original file is never modified. Replacing an existing output writes a
timestamped .bak copy next to it first.

Examples:
  python prepare_image.py photo.jpg --preset member --output images/team/newmember.jpg
  python prepare_image.py photo.jpg --preset news --output images/news/20261023/photo.jpg
  python prepare_image.py figure.png --preset gallery-figure --output images/gallery/science/figure.png
  python prepare_image.py photo.jpg --preset hero --focus 0.5,0.4 --output /tmp/hero.jpg
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageOps

PRESETS = {
    # 3:4 portrait used by the team card and the member detail page.
    "member": {"width": 1200, "height": 1600, "fit": "cover", "focus": (0.5, 0.40), "quality": 86},
    "member-card": {"width": 900, "height": 1200, "fit": "cover", "focus": (0.5, 0.40), "quality": 86},
    # 4:3 landscape used by news and Life gallery cards.
    "news": {"width": 1600, "height": 1200, "fit": "cover", "focus": (0.5, 0.5), "quality": 85},
    "gallery-life": {"width": 1600, "height": 1200, "fit": "cover", "focus": (0.5, 0.5), "quality": 85},
    # Scientific/art figures: never crop; fit inside a 1600 px box.
    "gallery-figure": {"width": 1600, "height": 1600, "fit": "contain", "quality": 90},
    "publication": {"width": 1200, "height": 1200, "fit": "contain", "quality": 90},
    # Homepage slider/header background.
    "hero": {"width": 2400, "height": 1350, "fit": "cover", "focus": (0.5, 0.5), "quality": 82},
    "social": {"width": 1200, "height": 630, "fit": "cover", "focus": (0.5, 0.5), "quality": 82},
}

FORMAT_BY_SUFFIX = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".webp": "WEBP"}


def parse_focus(value: str) -> tuple[float, float]:
    try:
        x_text, y_text = value.split(",", 1)
        x, y = float(x_text), float(y_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("focus must be two numbers: X,Y") from exc
    if not (0 <= x <= 1 and 0 <= y <= 1):
        raise argparse.ArgumentTypeError("focus values must be between 0 and 1")
    return x, y


def crop_cover(image: Image.Image, width: int, height: int, focus: tuple[float, float]) -> Image.Image:
    source_width, source_height = image.size
    target_ratio = width / height
    source_ratio = source_width / source_height

    if source_ratio > target_ratio:
        crop_height = source_height
        crop_width = int(round(crop_height * target_ratio))
        left = int(round((source_width - crop_width) * focus[0]))
        top = 0
    else:
        crop_width = source_width
        crop_height = int(round(crop_width / target_ratio))
        left = 0
        top = int(round((source_height - crop_height) * focus[1]))

    left = max(0, min(left, source_width - crop_width))
    top = max(0, min(top, source_height - crop_height))
    return image.crop((left, top, left + crop_width, top + crop_height))


def resize_cover(image: Image.Image, width: int, height: int, allow_upscale: bool) -> Image.Image:
    if not allow_upscale and image.width <= width and image.height <= height:
        return image
    return image.resize((width, height), Image.Resampling.LANCZOS)


def resize_contain(image: Image.Image, width: int, height: int, allow_upscale: bool) -> Image.Image:
    if image.width <= width and image.height <= height and not allow_upscale:
        return image
    copy = image.copy()
    copy.thumbnail((width, height), Image.Resampling.LANCZOS)
    return copy


def flatten_for_jpeg(image: Image.Image) -> Image.Image:
    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        rgba = image.convert("RGBA")
        background = Image.new("RGB", rgba.size, "white")
        background.paste(rgba, mask=rgba.getchannel("A"))
        return background
    return image.convert("RGB")


def backup_existing(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = path.with_name(f"{path.stem}.bak-{stamp}{path.suffix}")
    shutil.copy2(path, backup)
    return backup


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--preset", choices=sorted(PRESETS), default="member")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, help="override preset width")
    parser.add_argument("--height", type=int, help="override preset height")
    parser.add_argument("--fit", choices=("cover", "contain"), help="override preset fit mode")
    parser.add_argument("--focus", type=parse_focus, help="crop focus X,Y in 0..1; default from preset")
    parser.add_argument("--quality", type=int, choices=range(60, 96), metavar="60-95")
    parser.add_argument("--force", action="store_true", help="replace output after making a .bak copy")
    parser.add_argument("--allow-upscale", action="store_true")
    parser.add_argument("--keep-metadata", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"input not found: {args.input}")
    if args.output.resolve() == args.input.resolve():
        parser.error("output must differ from input; the original is never modified")
    output_suffix = args.output.suffix.lower()
    if output_suffix not in FORMAT_BY_SUFFIX:
        parser.error("output must end in .jpg, .jpeg, .png, or .webp")
    if args.output.exists() and not args.force:
        parser.error(f"output already exists (use --force to keep a .bak): {args.output}")

    preset = PRESETS[args.preset]
    width = args.width or preset["width"]
    height = args.height or preset["height"]
    fit = args.fit or preset.get("fit", "cover")
    focus = args.focus or preset.get("focus", (0.5, 0.5))
    quality = args.quality or preset.get("quality", 85)

    with Image.open(args.input) as opened:
        source_size = opened.size
        image = ImageOps.exif_transpose(opened)
        image.load()

        if fit == "cover":
            image = crop_cover(image, width, height, focus)
            image = resize_cover(image, width, height, args.allow_upscale)
        else:
            image = resize_contain(image, width, height, args.allow_upscale)

        target_format = FORMAT_BY_SUFFIX[output_suffix]
        if target_format == "JPEG":
            image = flatten_for_jpeg(image)
        elif target_format == "PNG" and image.mode not in ("RGB", "RGBA", "L", "LA", "P"):
            image = image.convert("RGBA")

        result = {
            "input": str(args.input),
            "source_size": f"{source_size[0]}x{source_size[1]}",
            "output": str(args.output),
            "output_size": f"{image.width}x{image.height}",
            "fit": fit,
            "focus": list(focus),
            "format": target_format,
        }
        if args.dry_run:
            result["written"] = False
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        args.output.parent.mkdir(parents=True, exist_ok=True)
        if args.output.exists():
            backup = backup_existing(args.output)
            result["backup"] = str(backup)

        save_kwargs = {"optimize": True}
        if args.keep_metadata and "exif" in image.info:
            save_kwargs["exif"] = image.info["exif"]
        if target_format == "JPEG":
            save_kwargs.update({"quality": quality, "progressive": True})
        elif target_format == "WEBP":
            save_kwargs.update({"quality": quality, "method": 6})
        elif target_format == "PNG":
            save_kwargs.update({"compress_level": 9})

        image.save(args.output, format=target_format, **save_kwargs)
        result["bytes"] = args.output.stat().st_size
        result["written"] = True
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0


if __name__ == "__main__":
    sys.exit(main())
