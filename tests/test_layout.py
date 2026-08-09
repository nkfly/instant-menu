import unittest

from src.layout import LayoutEngine
from src.models import BBox, TranslationBlock


class LayoutTests(unittest.TestCase):
    def test_price_blocks_are_not_reflowed(self) -> None:
        engine = LayoutEngine()
        block = TranslationBlock(
            id=1,
            original="980円",
            translation="980 yen",
            type="price",
            bbox=BBox(10, 20, 80, 24),
            confidence=0.99,
            translate=True,
            translation_source="manual",
        )

        layout = engine.layout([block])[0]

        self.assertEqual(layout.type, "price")
        self.assertEqual(layout.lines, ["980 yen"])


if __name__ == "__main__":
    unittest.main()
