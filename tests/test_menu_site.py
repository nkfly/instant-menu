import unittest

from src.menu_site import _build_menu_data
from src.models import BBox, TranslationBlock


class MenuSiteTests(unittest.TestCase):
    def test_builds_sectioned_menu_data(self) -> None:
        blocks = [
            TranslationBlock(
                id=1,
                original="【ウイスキー】",
                translation="[Whisky]",
                type="section_title",
                bbox=BBox(0, 0, 100, 20),
                confidence=0.99,
                translate=True,
                translation_source="manual",
            ),
            TranslationBlock(
                id=2,
                original="ハイボール",
                translation="Highball",
                type="menu_item",
                bbox=BBox(0, 20, 100, 20),
                confidence=0.99,
                translate=True,
                translation_source="manual",
            ),
            TranslationBlock(
                id=3,
                original="480円",
                translation="480円",
                type="price",
                bbox=BBox(100, 20, 50, 20),
                confidence=0.99,
                translate=False,
                translation_source="preserved",
            ),
            TranslationBlock(
                id=4,
                original="カシスソーダ",
                translation="Cassis Soda",
                type="section_title",
                bbox=BBox(0, 40, 100, 20),
                confidence=0.99,
                translate=True,
                translation_source="manual",
            ),
            TranslationBlock(
                id=5,
                original="450円",
                translation="450円",
                type="price",
                bbox=BBox(100, 40, 50, 20),
                confidence=0.99,
                translate=False,
                translation_source="preserved",
            ),
        ]

        menu = _build_menu_data("honoya", blocks)

        self.assertEqual(menu["restaurant"]["name_en"], "Honoya")
        self.assertEqual(len(menu["sections"]), 1)
        self.assertEqual(menu["sections"][0]["title_en"], "Whisky")
        self.assertEqual(menu["sections"][0]["title_ja"], "ウイスキー")
        self.assertEqual(menu["sections"][0]["items"][0]["name_en"], "Highball")
        self.assertEqual(menu["sections"][0]["items"][0]["name_ja"], "ハイボール")
        self.assertEqual(menu["sections"][0]["items"][0]["price"], "480円")
        self.assertEqual(menu["sections"][0]["items"][1]["name_en"], "Cassis Soda")
        self.assertEqual(menu["sections"][0]["items"][1]["price"], "450円")

        public_menu = _build_menu_data(
            "honoya",
            blocks,
            {
                "id": "019ffb69-bcff-7f7b-be96-e9656088b606",
                "public_slug": "honoya-7k3m2q",
                "name_en": "Honoya",
                "name_ja": "はの家",
            },
        )
        self.assertEqual(public_menu["restaurant"]["id"], "019ffb69-bcff-7f7b-be96-e9656088b606")
        self.assertEqual(public_menu["restaurant"]["slug"], "honoya-7k3m2q")
        self.assertEqual(public_menu["restaurant"]["name_ja"], "はの家")


if __name__ == "__main__":
    unittest.main()
