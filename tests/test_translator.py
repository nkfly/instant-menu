import unittest

from src.models import BBox, StructuredBlock
from src.translator import FallbackMenuTranslator, ManualPreparationTranslator, is_translation_complete


class TranslatorTests(unittest.TestCase):
    def test_preserves_price(self) -> None:
        translator = FallbackMenuTranslator()
        blocks = [
            StructuredBlock(
                id=1,
                text="980円",
                type="price",
                bbox=BBox(0, 0, 40, 12),
                confidence=0.99,
                translate=False,
            )
        ]
        translated = translator.translate(blocks)
        self.assertEqual(translated[0].translation, "980円")

    def test_translates_known_menu_term(self) -> None:
        translator = FallbackMenuTranslator()
        blocks = [
            StructuredBlock(
                id=1,
                text="唐揚げ",
                type="menu_item",
                bbox=BBox(0, 0, 80, 20),
                confidence=0.99,
                translate=True,
            )
        ]
        translated = translator.translate(blocks)
        self.assertEqual(translated[0].translation, "Japanese Fried Chicken")

    def test_manual_preparation_uses_todo_placeholder(self) -> None:
        translator = ManualPreparationTranslator()
        blocks = [
            StructuredBlock(
                id=1,
                text="特製醤油ラーメン",
                type="menu_item",
                bbox=BBox(0, 0, 120, 24),
                confidence=0.99,
                translate=True,
            )
        ]
        translated = translator.translate(blocks)
        self.assertEqual(translated[0].translation, "TODO")
        self.assertFalse(is_translation_complete(translated))

    def test_translation_completion_ignores_prices(self) -> None:
        translator = ManualPreparationTranslator()
        blocks = [
            StructuredBlock(
                id=1,
                text="980円",
                type="price",
                bbox=BBox(0, 0, 40, 12),
                confidence=0.99,
                translate=False,
            )
        ]
        translated = translator.translate(blocks)
        self.assertTrue(is_translation_complete(translated))


if __name__ == "__main__":
    unittest.main()
