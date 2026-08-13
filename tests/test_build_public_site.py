import json
import subprocess
import tempfile
import unittest
from pathlib import Path


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
            (restaurant / "restaurant.json").write_text(
                json.dumps(
                    {
                        "id": "019ffb69-bcff-7f7b-be96-e9656088b606",
                        "public_slug": "honoya-7k3m2q",
                        "name_en": "Honoya",
                        "name_ja": "はの家",
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                ["node", "deploy/build.mjs", "--project-root", str(root)],
                check=True,
                capture_output=True,
                text=True,
            )

            dist = root / "deploy" / "dist"
            self.assertIn("honoya-7k3m2q", result.stdout)
            self.assertTrue((dist / "index.html").is_file())
            self.assertTrue((dist / "styles.css").is_file())
            public_restaurant = dist / "restaurants" / "honoya-7k3m2q"
            self.assertTrue((public_restaurant / "menu_en.png").is_file())
            self.assertTrue((public_restaurant / "index.html").is_file())
            self.assertFalse((public_restaurant / "menu_site").exists())
            self.assertFalse((public_restaurant / "ocr_result.json").exists())

    def test_rejects_public_restaurant_without_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            website = root / "website"
            restaurant = root / "output" / "honoya"
            website.mkdir()
            restaurant.mkdir(parents=True)

            (website / "index.html").write_text("<h1>MenuInbound</h1>", encoding="utf-8")
            (website / "styles.css").write_text("body {}", encoding="utf-8")
            (restaurant / "menu_en.png").write_bytes(b"png")

            result = subprocess.run(
                ["node", "deploy/build.mjs", "--project-root", str(root)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing or invalid restaurant metadata", result.stderr)


if __name__ == "__main__":
    unittest.main()
