#!/usr/bin/env python3
"""Pre-publish checks for the Bian Lab static site.

Errors make the command exit 1. Warnings are informational.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlparse

from lxml import html
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}


def local_target(base: Path, url: str) -> Path | None:
    url = (url or "").strip()
    if not url or url.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    parsed = urlparse(url)
    if parsed.scheme or parsed.netloc:
        return None
    clean = unquote(parsed.path)
    if not clean:
        return None
    return (base / clean).resolve()


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    pages = sorted(ROOT.rglob("*.html"))
    referenced_images: dict[Path, str] = {}

    for page in pages:
        rel = page.relative_to(ROOT).as_posix()
        raw = page.read_text(encoding="utf-8", errors="replace")
        tree = html.fromstring(raw)

        if not tree.xpath(".//meta[@name='viewport']"):
            errors.append(f"{rel}: missing viewport meta")
        desc = tree.xpath(".//meta[@name='description']/@content")
        if not desc or "One page parallax" in desc[0]:
            errors.append(f"{rel}: missing or placeholder meta description")
        if not tree.xpath(".//link[@rel='canonical']"):
            warnings.append(f"{rel}: no canonical URL")
        if not tree.xpath(".//meta[@property='og:title']"):
            warnings.append(f"{rel}: no Open Graph title")

        ids = [el.get("id") for el in tree.xpath(".//*[@id]")]
        for item, count in Counter(ids).items():
            if count > 1:
                errors.append(f"{rel}: duplicate id {item!r}")

        for el in tree.xpath(".//*[@src or @href]"):
            for attr in ("src", "href"):
                value = el.get(attr)
                if value is None:
                    continue
                if value != value.strip():
                    warnings.append(f"{rel}: whitespace in {attr}={value!r}")
                target = local_target(page.parent, value)
                if target is not None and not target.exists():
                    errors.append(f"{rel}: missing local {attr} target {value!r}")

        # Inline background images (the homepage slider uses these).
        for style in tree.xpath(".//@style"):
            for match in re.finditer(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", style):
                value = match.group(1).strip()
                target = local_target(page.parent, value)
                if target is not None and not target.exists():
                    errors.append(f"{rel}: missing local background image {value!r}")
                if target and target.exists() and target.suffix.lower() in IMAGE_EXT:
                    referenced_images[target] = rel

        for img in tree.xpath(".//img"):
            src = (img.get("src") or "").strip()
            target = local_target(page.parent, src)
            if target and target.exists() and target.suffix.lower() in IMAGE_EXT:
                referenced_images[target] = rel
            if img.get("alt") is None:
                warnings.append(f"{rel}: img has no alt attribute: {src}")

        for anchor in tree.xpath(".//a[@target='_blank']"):
            rel_attr = (anchor.get("rel") or "").lower()
            if "noopener" not in rel_attr and "noreferrer" not in rel_attr:
                warnings.append(f"{rel}: target=_blank without rel=noopener: {anchor.get('href', '')}")

    print(f"pages={len(pages)} referenced_images={len(referenced_images)}")
    print(f"errors={len(errors)} warnings={len(warnings)}")

    for message in errors:
        print(f"ERROR   {message}")
    for message in warnings:
        print(f"WARNING {message}")

    large: list[tuple[int, Path]] = []
    for path in referenced_images:
        if path.stat().st_size >= 2 * 1024 * 1024:
            large.append((path.stat().st_size, path))
    if large:
        print("\nLarge referenced images (consider a web-sized copy):")
        for size, path in sorted(large, reverse=True):
            try:
                with Image.open(path) as image:
                    dimensions = f"{image.width}x{image.height}"
            except Exception:
                dimensions = "unknown"
            print(f"  {size / 1024 / 1024:6.2f} MB  {dimensions:>10}  {path.relative_to(ROOT).as_posix()}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
