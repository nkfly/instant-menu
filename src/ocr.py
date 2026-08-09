from __future__ import annotations

import os
from pathlib import Path

from .models import BBox, OCRBlock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PADDLE_CACHE_DIR = PROJECT_ROOT / ".paddlex"
os.environ.setdefault("PADDLE_PDX_CACHE_HOME", str(DEFAULT_PADDLE_CACHE_DIR))

try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None  # type: ignore[assignment]


class PaddleOCRProvider:
    def __init__(self, language: str = "japan") -> None:
        self.language = language
        self._ocr = None

    def run(self, image_path: Path) -> list[OCRBlock]:
        if PaddleOCR is None:
            raise RuntimeError(
                "PaddleOCR is not installed. Install dependencies with "
                "`pip install -r requirements.txt` before running OCR."
            )

        if self._ocr is None:
            self._ocr = PaddleOCR(
                use_angle_cls=True,
                lang=self.language,
            )

        raw_result = self._ocr.predict(str(image_path))
        page_result = raw_result[0] if raw_result else None
        if page_result is None:
            return []

        polygons = page_result["dt_polys"]
        texts = page_result["rec_texts"]
        scores = page_result["rec_scores"]
        blocks: list[OCRBlock] = []

        for index, (quad_points, text, confidence) in enumerate(
            zip(polygons, texts, scores),
            start=1,
        ):
            text = str(text).strip()
            confidence = float(confidence)

            if not text:
                continue

            xs = [int(point[0]) for point in quad_points]
            ys = [int(point[1]) for point in quad_points]
            x_min = min(xs)
            y_min = min(ys)
            x_max = max(xs)
            y_max = max(ys)

            blocks.append(
                OCRBlock(
                    id=index,
                    text=text,
                    bbox=BBox(
                        x=x_min,
                        y=y_min,
                        width=max(1, x_max - x_min),
                        height=max(1, y_max - y_min),
                    ),
                    confidence=confidence,
                )
            )

        blocks.sort(key=lambda block: (block.bbox.y, block.bbox.x))
        return [
            OCRBlock(
                id=index,
                text=block.text,
                bbox=block.bbox,
                confidence=block.confidence,
            )
            for index, block in enumerate(blocks, start=1)
        ]
