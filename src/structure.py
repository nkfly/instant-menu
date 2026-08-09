from __future__ import annotations

import re
from statistics import median

from .models import OCRBlock, StructuredBlock


PRICE_RE = re.compile(r"^\s*[\d,]+(?:\.\d+)?\s*(?:円|yen|¥)?\s*$", re.IGNORECASE)
SECTION_HINTS = {
    "おすすめ",
    "お品書き",
    "ランチ",
    "ディナー",
    "ドリンク",
    "一品",
    "定食",
    "セット",
    "前菜",
    "寿司",
    "丼",
    "麺",
    "飯",
}
PROMOTION_HINTS = {"限定", "おすすめ", "人気", "新作", "フェア", "特価"}
LABEL_HINTS = {"税込", "税抜", "お持ち帰り", "店内", "数量限定"}


class HeuristicMenuStructureAnalyzer:
    def analyze(self, blocks: list[OCRBlock]) -> list[StructuredBlock]:
        if not blocks:
            return []

        median_height = median(block.bbox.height for block in blocks)
        analyzed: list[StructuredBlock] = []

        for block in blocks:
            text = block.text.strip()
            block_type = self._classify(text, block.bbox.height, median_height)
            translate = block_type not in {"price", "other"}
            analyzed.append(
                StructuredBlock(
                    id=block.id,
                    text=text,
                    type=block_type,
                    bbox=block.bbox,
                    confidence=block.confidence,
                    translate=translate,
                )
            )
        return analyzed

    def _classify(self, text: str, bbox_height: int, median_height: float) -> str:
        if not text:
            return "other"

        if PRICE_RE.match(text):
            return "price"

        if any(hint in text for hint in LABEL_HINTS):
            return "label"

        if any(hint in text for hint in PROMOTION_HINTS) and len(text) <= 18:
            if bbox_height >= median_height * 1.1:
                return "section_title"
            return "promotion"

        if text in SECTION_HINTS or (len(text) <= 10 and bbox_height >= median_height * 1.25):
            return "section_title"

        if len(text) >= 18:
            return "description"

        if re.search(r"[ぁ-んァ-ン一-龯]", text):
            return "menu_item"

        return "other"
