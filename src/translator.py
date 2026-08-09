from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request

from .models import StructuredBlock, TranslationBlock


PRICE_RE = re.compile(r"^\s*[\d,]+(?:\.\d+)?\s*(?:円|yen|¥)?\s*$", re.IGNORECASE)
TODO_TRANSLATION = "TODO"

TRANSLATION_PROMPT = """You are a professional Japanese restaurant menu translator.

Translate Japanese menu content into concise, natural English suitable for restaurant menus.

Preserve Japanese culinary terms when they are commonly recognized.
Do not translate prices.
Avoid literal translations that sound unnatural in English.
Prefer concise translations because the English text must fit inside the original menu layout.

Return strict JSON with this shape:
{
  "items": [
    {
      "id": 1,
      "translation": "Special Shoyu Ramen"
    }
  ]
}
"""

DIRECT_TRANSLATIONS = {
    "唐揚げ": "Japanese Fried Chicken",
    "親子丼": "Oyakodon (Chicken & Egg Rice Bowl)",
    "ネギトロ": "Minced Tuna with Green Onion",
    "お通し": "Otoshi (Table Charge Appetizer)",
    "おすすめ": "Recommended",
    "ランチ": "Lunch",
    "ディナー": "Dinner",
    "定食": "Set Meals",
    "ドリンク": "Drinks",
    "ビール": "Beer",
    "焼き鳥": "Yakitori",
    "ラーメン": "Ramen",
    "味噌ラーメン": "Miso Ramen",
    "醤油ラーメン": "Shoyu Ramen",
    "特製醤油ラーメン": "Special Shoyu Ramen",
    "塩ラーメン": "Shio Ramen",
    "豚骨ラーメン": "Tonkotsu Ramen",
    "チャーシュー": "Chashu",
    "餃子": "Gyoza",
    "焼売": "Shumai",
    "炒飯": "Fried Rice",
    "枝豆": "Edamame",
    "刺身": "Sashimi",
    "寿司": "Sushi",
    "うどん": "Udon",
    "そば": "Soba",
    "天ぷら": "Tempura",
    "牛丼": "Gyudon",
    "からあげ": "Japanese Fried Chicken",
    "味噌汁": "Miso Soup",
}

WORD_SUBSTITUTIONS = {
    "特製": "Special",
    "醤油": "Shoyu",
    "味噌": "Miso",
    "塩": "Shio",
    "豚骨": "Tonkotsu",
    "ラーメン": "Ramen",
    "丼": "Rice Bowl",
    "定食": "Set Meal",
    "焼き": "Grilled",
    "鶏": "Chicken",
    "牛": "Beef",
    "豚": "Pork",
    "海老": "Shrimp",
    "天ぷら": "Tempura",
    "寿司": "Sushi",
    "刺身": "Sashimi",
    "うどん": "Udon",
    "そば": "Soba",
}


class TranslatorFactory:
    @staticmethod
    def from_environment() -> "BaseTranslator":
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            return OpenAIChatTranslator(api_key=api_key, model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))
        return FallbackMenuTranslator()


class BaseTranslator:
    def translate(self, blocks: list[StructuredBlock]) -> list[TranslationBlock]:
        raise NotImplementedError


class ManualPreparationTranslator(BaseTranslator):
    def translate(self, blocks: list[StructuredBlock]) -> list[TranslationBlock]:
        results: list[TranslationBlock] = []
        for block in blocks:
            if not block.translate or block.type == "price" or PRICE_RE.match(block.text):
                translation = block.text
                source = "preserved"
            else:
                translation = TODO_TRANSLATION
                source = "todo"

            results.append(
                TranslationBlock(
                    id=block.id,
                    original=block.text,
                    translation=translation,
                    type=block.type,
                    bbox=block.bbox,
                    confidence=block.confidence,
                    translate=block.translate,
                    translation_source=source,
                )
            )
        return results


class OpenAIChatTranslator(BaseTranslator):
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def translate(self, blocks: list[StructuredBlock]) -> list[TranslationBlock]:
        translatable = [block for block in blocks if block.translate and block.type != "price"]
        fallback = FallbackMenuTranslator()
        fallback_map = {item.id: item for item in fallback.translate(blocks)}

        if not translatable:
            return [fallback_map[block.id] for block in blocks]

        try:
            translated_map = self._request_translations(translatable)
        except Exception:
            return [fallback_map[block.id] for block in blocks]

        results: list[TranslationBlock] = []
        for block in blocks:
            if not block.translate or block.type == "price":
                results.append(
                    TranslationBlock(
                        id=block.id,
                        original=block.text,
                        translation=block.text,
                        type=block.type,
                        bbox=block.bbox,
                        confidence=block.confidence,
                        translate=block.translate,
                        translation_source="preserved",
                    )
                )
                continue

            translated_text = translated_map.get(block.id)
            if not translated_text:
                results.append(fallback_map[block.id])
                continue

            results.append(
                TranslationBlock(
                    id=block.id,
                    original=block.text,
                    translation=translated_text,
                    type=block.type,
                    bbox=block.bbox,
                    confidence=block.confidence,
                    translate=block.translate,
                    translation_source=f"openai:{self.model}",
                )
            )
        return results

    def _request_translations(self, blocks: list[StructuredBlock]) -> dict[int, str]:
        payload = {
            "model": self.model,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": TRANSLATION_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "items": [
                                {
                                    "id": block.id,
                                    "text": block.text,
                                    "type": block.type,
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
        return {int(item["id"]): str(item["translation"]).strip() for item in parsed["items"]}


class FallbackMenuTranslator(BaseTranslator):
    def translate(self, blocks: list[StructuredBlock]) -> list[TranslationBlock]:
        results: list[TranslationBlock] = []
        for block in blocks:
            if not block.translate or block.type == "price" or PRICE_RE.match(block.text):
                results.append(
                    TranslationBlock(
                        id=block.id,
                        original=block.text,
                        translation=block.text,
                        type=block.type,
                        bbox=block.bbox,
                        confidence=block.confidence,
                        translate=block.translate,
                        translation_source="preserved",
                    )
                )
                continue

            translation = self._translate_text(block.text, block.type)
            results.append(
                TranslationBlock(
                    id=block.id,
                    original=block.text,
                    translation=translation,
                    type=block.type,
                    bbox=block.bbox,
                    confidence=block.confidence,
                    translate=block.translate,
                    translation_source="fallback",
                )
            )
        return results

    def _translate_text(self, text: str, block_type: str) -> str:
        stripped = text.strip()
        if stripped in DIRECT_TRANSLATIONS:
            return DIRECT_TRANSLATIONS[stripped]

        translated = stripped
        for source, target in WORD_SUBSTITUTIONS.items():
            translated = translated.replace(source, f"{target} ")

        translated = re.sub(r"\s+", " ", translated).strip(" -")
        if translated != stripped:
            return translated

        if block_type == "section_title":
            return f"{stripped} (Section)"

        return stripped


def is_translation_complete(blocks: list[TranslationBlock]) -> bool:
    for block in blocks:
        if not block.translate or block.type == "price":
            continue
        if block.translation.strip() == TODO_TRANSLATION:
            return False
        if not block.translation.strip():
            return False
    return True
