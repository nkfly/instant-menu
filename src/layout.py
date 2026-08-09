from __future__ import annotations

from textwrap import wrap

from .models import LayoutBlock, TranslationBlock


class LayoutEngine:
    def layout(self, blocks: list[TranslationBlock]) -> list[LayoutBlock]:
        return [self._layout_block(block) for block in blocks]

    def _layout_block(self, block: TranslationBlock) -> LayoutBlock:
        if not block.translate or block.translation == block.original or block.type == "price":
            font_size = max(12, int(block.bbox.height * 0.7))
            return LayoutBlock(
                id=block.id,
                original=block.original,
                translation=block.translation,
                type=block.type,
                bbox=block.bbox,
                confidence=block.confidence,
                lines=[block.translation],
                font_size=font_size,
                translate=block.translate,
                warning=block.warning,
            )

        best_lines, best_size = self._fit_text(block.translation, block.bbox.width, block.bbox.height)
        return LayoutBlock(
            id=block.id,
            original=block.original,
            translation=block.translation,
            type=block.type,
            bbox=block.bbox,
            confidence=block.confidence,
            lines=best_lines,
            font_size=best_size,
            translate=block.translate,
            warning=block.warning,
        )

    def _fit_text(self, text: str, width: int, height: int) -> tuple[list[str], int]:
        font_size = max(12, int(height * 0.72))

        while font_size >= 10:
            chars_per_line = max(1, int(width / max(font_size * 0.58, 1)))
            wrapped = wrap(text, width=chars_per_line, break_long_words=False, break_on_hyphens=False) or [text]
            line_height = int(font_size * 1.2)
            if len(wrapped) * line_height <= max(height, line_height):
                return wrapped, font_size
            font_size -= 1

        return wrap(text, width=max(1, int(width / 6)), break_long_words=True) or [text], 10
