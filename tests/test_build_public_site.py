import tempfile
import unittest
from pathlib import Path

from scripts.build_public_site import build_public_site


class PublicSiteBuildTests(unittest.TestCase):
    def test_builds_only_public_restaurant_assets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            website = root / "website"
            restaurant = root / "output" / "honoya"
            menu_site = restaurant / "menu_site"
            website.mkdir()
            menu_site.mkdir(parents=True)

            (website / "index.html").write_text("<h1>MenuInbound</h1>", encoding="utf-8")
            (website / "styles.css").write_text("body {}", encoding="utf-8")
            (restaurant / "menu_en.png").write_bytes(b"png")
            (restaurant / "ocr_result.json").write_text("{}", encoding="utf-8")
            (menu_site / "index.html").write_text("<h1>Honoya</h1>", encoding="utf-8")

            published = build_public_site(root)

            self.assertEqual(published, ["honoya"])
            self.assertTrue((root / "dist" / "index.html").is_file())
            self.assertTrue((root / "dist" / "styles.css").is_file())
            self.assertTrue((root / "dist" / "output" / "honoya" / "menu_en.png").is_file())
            self.assertTrue((root / "dist" / "output" / "honoya" / "menu_site" / "index.html").is_file())
            self.assertFalse((root / "dist" / "output" / "honoya" / "ocr_result.json").exists())


if __name__ == "__main__":
    unittest.main()
