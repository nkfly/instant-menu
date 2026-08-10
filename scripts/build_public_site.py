#!/usr/bin/env python3
"""Build the Cloudflare Workers static asset directory."""

from __future__ import annotations

import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def build_public_site(project_root: Path = PROJECT_ROOT) -> list[str]:
    project_root = project_root.resolve()
    website_dir = project_root / "website"
    restaurant_output_dir = project_root / "output"
    dist_dir = project_root / "dist"

    required_files = (website_dir / "index.html", website_dir / "styles.css")
    missing = [str(path) for path in required_files if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing website source files: {', '.join(missing)}")

    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()

    for source in required_files:
        shutil.copy2(source, dist_dir / source.name)

    published_restaurants: list[str] = []
    if restaurant_output_dir.is_dir():
        for restaurant_dir in sorted(restaurant_output_dir.iterdir()):
            if not restaurant_dir.is_dir():
                continue

            public_files = [restaurant_dir / "menu_en.png"]
            menu_site_dir = restaurant_dir / "menu_site"
            if not any(path.is_file() for path in public_files) and not menu_site_dir.is_dir():
                continue

            target_dir = dist_dir / "output" / restaurant_dir.name
            target_dir.mkdir(parents=True, exist_ok=True)
            for source in public_files:
                if source.is_file():
                    shutil.copy2(source, target_dir / source.name)
            if menu_site_dir.is_dir():
                shutil.copytree(menu_site_dir, target_dir / "menu_site")
            published_restaurants.append(restaurant_dir.name)

    return published_restaurants


def main() -> None:
    restaurants = build_public_site()
    names = ", ".join(restaurants) if restaurants else "none"
    print(f"Built dist/ with public restaurant assets: {names}")


if __name__ == "__main__":
    main()
