from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .models import LayoutBlock, OCRBlock

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover - import guard
    raise RuntimeError(
        "Pillow is required for rendering. Install dependencies with `pip install -r requirements.txt`."
    ) from exc


FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Supplemental/Helvetica.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]


class PillowMenuRenderer:
    def render(self, input_image: Path, blocks: list[LayoutBlock], output_image: Path) -> None:
        image = Image.open(input_image).convert("RGBA")
        overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        for block in blocks:
            if not block.translate or not block.lines:
                continue

            if block.type == "price" or block.translation == block.original:
                continue

            fill = self._estimate_background(image, block.bbox.x, block.bbox.y, block.bbox.width, block.bbox.height)
            padding = max(4, int(block.font_size * 0.25))
            draw.rectangle(
                [
                    block.bbox.x - padding,
                    block.bbox.y - padding,
                    block.bbox.x + block.bbox.width + padding,
                    block.bbox.y + block.bbox.height + padding,
                ],
                fill=fill,
            )

            font = self._load_font(block.font_size)
            text = "\n".join(block.lines)
            draw.multiline_text(
                (block.bbox.x, block.bbox.y),
                text,
                fill=(28, 24, 20, 255),
                font=font,
                spacing=max(2, int(block.font_size * 0.15)),
            )

        rendered = Image.alpha_composite(image, overlay).convert("RGB")
        output_image.parent.mkdir(parents=True, exist_ok=True)
        rendered.save(output_image)

    def render_debug_ocr(self, input_image: Path, blocks: list[OCRBlock], output_image: Path) -> None:
        image = Image.open(input_image).convert("RGB")
        draw = ImageDraw.Draw(image)
        font = self._load_font(16)

        for block in blocks:
            x = block.bbox.x
            y = block.bbox.y
            w = block.bbox.width
            h = block.bbox.height
            draw.rectangle([x, y, x + w, y + h], outline=(220, 20, 60), width=2)
            label = f"{block.id}: {block.text[:20]}"
            draw.rectangle([x, max(0, y - 20), x + 180, y], fill=(255, 250, 205))
            draw.text((x + 4, max(0, y - 18)), label, fill=(20, 20, 20), font=font)

        output_image.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_image)

    def _estimate_background(self, image: Image.Image, x: int, y: int, width: int, height: int) -> tuple[int, int, int, int]:
        left = max(0, x - 4)
        top = max(0, y - 4)
        right = min(image.width, x + width + 4)
        bottom = min(image.height, y + height + 4)
        crop = image.crop((left, top, right, bottom)).convert("RGB")
        pixels = list(crop.getdata())
        if not pixels:
            return (255, 255, 255, 240)
        r = sum(pixel[0] for pixel in pixels) // len(pixels)
        g = sum(pixel[1] for pixel in pixels) // len(pixels)
        b = sum(pixel[2] for pixel in pixels) // len(pixels)
        return (r, g, b, 235)

    def _load_font(self, font_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        for candidate in FONT_CANDIDATES:
            path = Path(candidate)
            if path.exists():
                try:
                    return ImageFont.truetype(str(path), font_size)
                except OSError:
                    continue
        return ImageFont.load_default()
