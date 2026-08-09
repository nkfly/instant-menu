from __future__ import annotations

import json
import os
import re
import urllib.request

from .models import CorrectedOCRBlock, OCRBlock


CORRECTION_PROMPT = """You are correcting OCR output from a Japanese restaurant menu.

Your task:
1. Correct obvious OCR mistakes using menu context.
2. Preserve prices and numbers unless the OCR error is obvious.
3. Keep corrected text concise and close to the source image.
4. Do not invent missing dishes or missing text.
5. Return strict JSON with this shape:
{
  "items": [
    {
      "id": 1,
      "corrected_text": "ドリンクメニュー"
    }
  ]
}
"""

COMMON_REPLACEMENTS = {
    "メニユー": "メニュー",
    "スーバー": "スーパー",
    "ンフト": "ソフト",
    "ビーチ": "ピーチ",
    "グレーブ": "グレープ",
    "グレープフルーツ": "グレープフルーツ",
    "ウィスキー": "ウイスキー",
}


class OCRCorrectorFactory:
    @staticmethod
    def from_environment() -> "BaseOCRCorrector":
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
            return OpenAIOCRCorrector(api_key=api_key, model=model)
        return HeuristicMenuOCRCorrector()


class BaseOCRCorrector:
    def correct(self, blocks: list[OCRBlock]) -> list[CorrectedOCRBlock]:
        raise NotImplementedError


class OpenAIOCRCorrector(BaseOCRCorrector):
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def correct(self, blocks: list[OCRBlock]) -> list[CorrectedOCRBlock]:
        fallback = HeuristicMenuOCRCorrector()
        fallback_map = {block.id: block for block in fallback.correct(blocks)}

        try:
            corrected_map = self._request_corrections(blocks)
        except Exception:
            return [fallback_map[block.id] for block in blocks]

        corrected_blocks: list[CorrectedOCRBlock] = []
        for block in blocks:
            corrected_text = corrected_map.get(block.id, block.text).strip() or block.text
            changed = corrected_text != block.text
            corrected_blocks.append(
                CorrectedOCRBlock(
                    id=block.id,
                    original_text=block.text,
                    corrected_text=corrected_text,
                    bbox=block.bbox,
                    confidence=block.confidence,
                    correction_source=f"openai:{self.model}",
                    changed=changed,
                )
            )
        return corrected_blocks

    def _request_corrections(self, blocks: list[OCRBlock]) -> dict[int, str]:
        payload = {
            "model": self.model,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": CORRECTION_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "items": [
                                {
                                    "id": block.id,
                                    "text": block.text,
                                    "bbox": block.bbox.to_list(),
                                    "confidence": round(block.confidence, 4),
                                }
                                for block in blocks
                            ]
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
        }
        request = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))

        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return {int(item["id"]): str(item["corrected_text"]).strip() for item in parsed["items"]}


class HeuristicMenuOCRCorrector(BaseOCRCorrector):
    def correct(self, blocks: list[OCRBlock]) -> list[CorrectedOCRBlock]:
        corrected: list[CorrectedOCRBlock] = []
        for block in blocks:
            normalized = self._normalize(block.text)
            source = "heuristic"
            corrected.append(
                CorrectedOCRBlock(
                    id=block.id,
                    original_text=block.text,
                    corrected_text=normalized,
                    bbox=block.bbox,
                    confidence=block.confidence,
                    correction_source=source,
                    changed=normalized != block.text,
                )
            )
        return corrected

    def _normalize(self, text: str) -> str:
        corrected = text.strip()
        corrected = re.sub(r"\s+", " ", corrected)
        corrected = corrected.replace("（ ", "（").replace(" ）", "）")
        corrected = corrected.replace("( ", "(").replace(" )", ")")
        corrected = corrected.replace("【 ", "【").replace(" 】", "】")
        corrected = corrected.replace("／ ", "／")
        corrected = re.sub(r"(?<=\d)\s+円", "円", corrected)
        corrected = re.sub(r"円\s+", "円 ", corrected)
        corrected = corrected.replace("or", "or")

        for source, target in COMMON_REPLACEMENTS.items():
            corrected = corrected.replace(source, target)

        corrected = corrected.replace("びんビール()", "びんビール")
        corrected = corrected.replace("冷or温", "冷 or 温")

        return corrected
