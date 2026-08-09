from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BBox:
    x: int
    y: int
    width: int
    height: int

    def to_list(self) -> list[int]:
        return [self.x, self.y, self.width, self.height]

    def to_dict(self) -> dict[str, int]:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        }


@dataclass(frozen=True)
class OCRBlock:
    id: int
    text: str
    bbox: BBox
    confidence: float

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "text": self.text,
            "bbox": self.bbox.to_list(),
            "confidence": round(self.confidence, 4),
        }


@dataclass(frozen=True)
class CorrectedOCRBlock:
    id: int
    original_text: str
    corrected_text: str
    bbox: BBox
    confidence: float
    correction_source: str
    changed: bool
    warning: str | None = None

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "id": self.id,
            "original_text": self.original_text,
            "corrected_text": self.corrected_text,
            "bbox": self.bbox.to_list(),
            "confidence": round(self.confidence, 4),
            "correction_source": self.correction_source,
            "changed": self.changed,
        }
        if self.warning:
            payload["warning"] = self.warning
        return payload

    def to_ocr_block(self) -> OCRBlock:
        return OCRBlock(
            id=self.id,
            text=self.corrected_text,
            bbox=self.bbox,
            confidence=self.confidence,
        )


@dataclass(frozen=True)
class StructuredBlock:
    id: int
    text: str
    type: str
    bbox: BBox
    confidence: float
    translate: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "text": self.text,
            "type": self.type,
            "bbox": self.bbox.to_list(),
            "confidence": round(self.confidence, 4),
            "translate": self.translate,
        }


@dataclass(frozen=True)
class TranslationBlock:
    id: int
    original: str
    translation: str
    type: str
    bbox: BBox
    confidence: float
    translate: bool
    translation_source: str
    warning: str | None = None

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "id": self.id,
            "original": self.original,
            "translation": self.translation,
            "type": self.type,
            "bbox": self.bbox.to_list(),
            "confidence": round(self.confidence, 4),
            "translate": self.translate,
            "translation_source": self.translation_source,
        }
        if self.warning:
            payload["warning"] = self.warning
        return payload


@dataclass(frozen=True)
class LayoutBlock:
    id: int
    original: str
    translation: str
    type: str
    bbox: BBox
    confidence: float
    lines: list[str]
    font_size: int
    translate: bool
    warning: str | None = None
