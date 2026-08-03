#!/usr/bin/env python3

import json
import os
import subprocess
from pathlib import Path


ROOT = Path("/Users/liyuan.hung/instant-menu")
RESTAURANT_DIR = ROOT / "restaurants" / "noodle_villa_ueno"
SCREENSHOTS_DIR = RESTAURANT_DIR / "screenshots"
CROPS_DIR = RESTAURANT_DIR / "crops"
MANIFEST_PATH = CROPS_DIR / "manifest.json"

CROP_X = 50
CROP_WIDTH = 200
CROP_HEIGHT = 200


SPECS = {
    "IMG_8277.JPG": [
        {"item_name": "啤酒自选套餐", "y": 344},
        {"item_name": "油酥花生", "y": 596},
        {"item_name": "白卤毛豆", "y": 848},
    ],
    "IMG_8279.JPG": [
        {"item_name": "干拌羊肚", "y": 216},
        {"item_name": "现拉手工牛肉宽面", "y": 520},
        {"item_name": "现拉手工牛肉面条", "y": 792},
    ],
    "IMG_8281.JPG": [
        {"item_name": "原汤辣羊杂粉", "y": 338},
        {"item_name": "糊辣椒香嫩牛肉粉", "y": 591},
        {"item_name": "原汤羊大骨粉", "y": 844},
    ],
    "IMG_8283.JPG": [
        {"item_name": "香辣牛肉土豆泥拌粉", "y": 235},
        {"item_name": "番茄牛肉土豆泥拌粉", "y": 509},
        {"item_name": "麻辣虎皮鸡爪", "y": 783},
        {"item_name": "溏心炸蛋", "y": 1057},
    ],
    "IMG_8285.JPG": [
        {"item_name": "溏心炸蛋", "y": 236},
        {"item_name": "自制山楂乌梅水", "y": 508},
        {"item_name": "特惠套餐（糊辣椒香嫩牛肉粉+溏心炸蛋+健力宝）", "y": 884},
    ],
    "IMG_8287.JPG": [
        {"item_name": "特惠套餐（糊辣椒香嫩牛肉粉+溏心炸蛋+健力宝）", "y": 308},
        {"item_name": "啤酒自选套餐", "y": 582},
        {"item_name": "冷吃鸡丝拌粉(鲜辣味)", "y": 958},
    ],
    "IMG_8291.JPG": [
        {"item_name": "冷吃牛肉拌粉(番茄味)", "y": 216},
        {"item_name": "冷吃牛肉拌粉(鲜辣味)", "y": 489},
        {"item_name": "冷吃牛肉拌粉(麻辣味)", "y": 764},
    ],
    "IMG_8293.JPG": [
        {"item_name": "清炖牛肉粉", "y": 283},
        {"item_name": "红烧牛肉粉", "y": 536},
        {"item_name": "半肉半筋粉", "y": 789},
    ],
    "IMG_8295.JPG": [
        {"item_name": "红烧牛肋条粉", "y": 235},
        {"item_name": "番茄牛腩粉", "y": 508},
        {"item_name": "酸菜牛肉粉", "y": 781},
    ],
    "IMG_8297.JPG": [
        {"item_name": "椒麻牛肉粉", "y": 216},
        {"item_name": "泡椒牛肉粉", "y": 490},
        {"item_name": "糊辣椒香牛肉粉", "y": 766},
        {"item_name": "糊辣椒香嫩牛肉粉", "y": 1040},
    ],
    "IMG_8299.JPG": [
        {"item_name": "糊辣椒香嫩牛肉粉", "y": 215},
        {"item_name": "香辣牛肉土豆泥拌粉", "y": 491},
        {"item_name": "番茄牛肉土豆泥拌粉", "y": 765},
    ],
    "IMG_8301.JPG": [
        {"item_name": "原汤羊肉粉", "y": 604},
        {"item_name": "酸菜羊杂粉", "y": 858},
    ],
    "IMG_8303.JPG": [
        {"item_name": "酸菜羊杂粉", "y": 216},
        {"item_name": "原汤辣羊肉粉", "y": 489},
        {"item_name": "原汤羊杂粉", "y": 764},
        {"item_name": "原汤辣羊杂粉", "y": 1038},
    ],
    "IMG_8305.JPG": [
        {"item_name": "原汤辣羊杂粉", "y": 216},
        {"item_name": "原汤羊大骨粉", "y": 490},
        {"item_name": "红烧小羊排粉", "y": 764},
        {"item_name": "酸菜羊肉粉", "y": 1038},
    ],
    "IMG_8307.JPG": [
        {"item_name": "酸菜羊肉粉", "y": 216},
        {"item_name": "椒麻羊肉粉", "y": 490},
        {"item_name": "椒麻羊杂粉", "y": 766},
    ],
    "IMG_8309.JPG": [
        {"item_name": "椒麻羊大骨粉", "y": 215},
        {"item_name": "泡椒羊肉粉", "y": 489},
        {"item_name": "泡椒羊杂粉", "y": 764},
        {"item_name": "泡椒羊大骨粉", "y": 1038},
    ],
    "IMG_8311.JPG": [
        {"item_name": "泡椒羊大骨粉", "y": 214},
        {"item_name": "糊辣椒香羊肉粉", "y": 489},
        {"item_name": "糊辣椒香羊杂粉", "y": 764},
        {"item_name": "羊肉粉丝汤(不可续米粉)", "y": 1039},
    ],
    "IMG_8313.JPG": [
        {"item_name": "羊肉粉丝汤(不可续米粉)", "y": 214},
        {"item_name": "羊杂粉丝汤(不可续米粉)", "y": 489},
    ],
    "IMG_8315.JPG": [
        {"item_name": "素酸辣粉(不可续米粉)", "y": 286},
        {"item_name": "牛肉酸辣粉(不可续米粉)", "y": 560},
    ],
    "IMG_8317.JPG": [
        {"item_name": "炸羊肉串（2串）", "y": 290},
        {"item_name": "油酥花生", "y": 564},
        {"item_name": "白卤毛豆", "y": 838},
    ],
    "IMG_8319.JPG": [
        {"item_name": "干拌羊肚", "y": 214},
        {"item_name": "鹿茸菇锅盔", "y": 489},
        {"item_name": "白卤鸡腿", "y": 764},
        {"item_name": "芝麻香煎馍", "y": 1038},
    ],
    "IMG_8321.JPG": [
        {"item_name": "芝麻香煎馍", "y": 214},
        {"item_name": "麻辣双脆", "y": 489},
        {"item_name": "鲜椒双脆", "y": 764},
        {"item_name": "椒麻脆肠", "y": 1038},
    ],
    "IMG_8323.JPG": [
        {"item_name": "椒麻脆肠", "y": 214},
        {"item_name": "麻辣虎皮鸡爪", "y": 489},
        {"item_name": "渣渣牛肉", "y": 764},
        {"item_name": "酱肉锅盔（2个）", "y": 1038},
    ],
}


def run_crop(source: Path, out_path: Path, y: int) -> None:
    command = [
        "sips",
        "-c",
        str(CROP_HEIGHT),
        str(CROP_WIDTH),
        "--cropOffset",
        str(y),
        str(CROP_X),
        str(source),
        "--out",
        str(out_path),
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)


def main() -> None:
    CROPS_DIR.mkdir(parents=True, exist_ok=True)

    manifest = {
        "restaurant": "noodle_villa_ueno",
        "source_directory": str(SCREENSHOTS_DIR.relative_to(ROOT)),
        "crop_directory": str(CROPS_DIR.relative_to(ROOT)),
        "crop_size": {
            "width": CROP_WIDTH,
            "height": CROP_HEIGHT,
        },
        "entries": [],
    }

    for screenshot_name, items in SPECS.items():
        source = SCREENSHOTS_DIR / screenshot_name
        source_base = source.stem

        for index, item in enumerate(items, start=1):
            crop_filename = f"{source_base}_{index:02d}.jpg"
            out_path = CROPS_DIR / crop_filename
            run_crop(source, out_path, item["y"])
            manifest["entries"].append(
                {
                    "source_image": str(source.relative_to(ROOT)),
                    "crop_file": str(out_path.relative_to(ROOT)),
                    "item_name": item["item_name"],
                    "crop": {
                        "x": CROP_X,
                        "y": item["y"],
                        "width": CROP_WIDTH,
                        "height": CROP_HEIGHT,
                    },
                }
            )

    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
