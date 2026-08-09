import unittest

from src.models import BBox, OCRBlock
from src.structure import HeuristicMenuStructureAnalyzer


class StructureTests(unittest.TestCase):
    def test_detects_price(self) -> None:
        analyzer = HeuristicMenuStructureAnalyzer()
        blocks = [
            OCRBlock(id=1, text="980円", bbox=BBox(0, 0, 80, 20), confidence=0.99),
        ]
        structured = analyzer.analyze(blocks)
        self.assertEqual(structured[0].type, "price")
        self.assertFalse(structured[0].translate)

    def test_detects_menu_item(self) -> None:
        analyzer = HeuristicMenuStructureAnalyzer()
        blocks = [
            OCRBlock(id=1, text="特製醤油ラーメン", bbox=BBox(0, 0, 240, 28), confidence=0.99),
        ]
        structured = analyzer.analyze(blocks)
        self.assertEqual(structured[0].type, "menu_item")


if __name__ == "__main__":
    unittest.main()
