import unittest
from pathlib import Path

from main import infer_restaurant_slug, resolve_output_image


class PathTests(unittest.TestCase):
    def test_infers_restaurant_from_input_directory(self) -> None:
        input_image = Path("/Users/liyuan.hung/instant-menu/input/honoya/menu_jp.png")
        self.assertEqual(infer_restaurant_slug(input_image), "honoya")

    def test_falls_back_to_filename_stem_outside_input_tree(self) -> None:
        input_image = Path("/tmp/random_menu.png")
        self.assertEqual(infer_restaurant_slug(input_image), "random_menu")

    def test_default_output_uses_restaurant_directory(self) -> None:
        input_image = Path("/Users/liyuan.hung/instant-menu/input/honoya/menu_jp.png")
        output_image = resolve_output_image(input_image, None)
        self.assertEqual(output_image, Path("/Users/liyuan.hung/instant-menu/output/honoya/menu_en.png"))


if __name__ == "__main__":
    unittest.main()
