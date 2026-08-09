import unittest

from src.correction import HeuristicMenuOCRCorrector
from src.models import BBox, OCRBlock


class CorrectionTests(unittest.TestCase):
    def test_corrects_common_menu_ocr_errors(self) -> None:
        corrector = HeuristicMenuOCRCorrector()
        blocks = [
            OCRBlock(id=1, text="はの家ドリンクメニユー", bbox=BBox(0, 0, 100, 20), confidence=0.9),
            OCRBlock(id=2, text="【ンフトドリンク】", bbox=BBox(0, 20, 100, 20), confidence=0.9),
        ]

        corrected = corrector.correct(blocks)

        self.assertEqual(corrected[0].corrected_text, "はの家ドリンクメニュー")
        self.assertEqual(corrected[1].corrected_text, "【ソフトドリンク】")
        self.assertTrue(corrected[0].changed)
        self.assertTrue(corrected[1].changed)

    def test_normalizes_price_spacing(self) -> None:
        corrector = HeuristicMenuOCRCorrector()
        blocks = [
            OCRBlock(id=1, text="600 円", bbox=BBox(0, 0, 50, 20), confidence=0.9),
        ]

        corrected = corrector.correct(blocks)

        self.assertEqual(corrected[0].corrected_text, "600円")


if __name__ == "__main__":
    unittest.main()
