#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.correction import OCRCorrectorFactory
from src.layout import LayoutEngine
from src.models import BBox, CorrectedOCRBlock, OCRBlock, StructuredBlock, TranslationBlock
from src.ocr import PaddleOCRProvider
from src.structure import HeuristicMenuStructureAnalyzer
from src.translator import (
    ManualPreparationTranslator,
    TranslatorFactory,
    is_translation_complete,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an English restaurant menu image from a Japanese menu image."
    )
    parser.add_argument("input_image", help="Path to the Japanese menu image.")
    parser.add_argument(
        "--output",
        default=None,
        help="Path to the rendered English menu image. Default: output/<restaurant>/menu_en.png",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Generate OCR debug output with bounding boxes.",
    )
    parser.add_argument(
        "--translation-json",
        default=None,
        help="Path to the translation JSON file. Default: alongside the output image as translation_result.json",
    )
    parser.add_argument(
        "--prepare-translation-json",
        action="store_true",
        help="Create translation_result.json with TODO placeholders and stop before rendering.",
    )
    parser.add_argument(
        "--auto-translate",
        action="store_true",
        help="Allow automatic translation with API or fallback translator instead of stopping for manual translation.",
    )
    return parser.parse_args()


def infer_restaurant_slug(input_image: Path) -> str:
    try:
        input_index = input_image.parts.index("input")
    except ValueError:
        return input_image.stem

    if input_index + 1 < len(input_image.parts) - 1:
        return input_image.parts[input_index + 1]

    return input_image.stem


def resolve_output_image(input_image: Path, output_arg: str | None) -> Path:
    if output_arg:
        return Path(output_arg).expanduser().resolve()

    restaurant_slug = infer_restaurant_slug(input_image)
    return (Path.cwd() / "output" / restaurant_slug / "menu_en.png").resolve()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def save_json(path: Path, payload: object) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def serialize_ocr(blocks: list[OCRBlock]) -> list[dict[str, object]]:
    return [block.to_dict() for block in blocks]


def serialize_corrected_ocr(blocks: list[CorrectedOCRBlock]) -> list[dict[str, object]]:
    return [block.to_dict() for block in blocks]


def serialize_structure(blocks: list[StructuredBlock]) -> list[dict[str, object]]:
    return [block.to_dict() for block in blocks]


def serialize_translation(blocks: list[TranslationBlock]) -> list[dict[str, object]]:
    return [block.to_dict() for block in blocks]


def load_translation_blocks(path: Path) -> list[TranslationBlock]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    blocks: list[TranslationBlock] = []
    for item in payload:
        bbox = BBox(*item["bbox"])
        blocks.append(
            TranslationBlock(
                id=int(item["id"]),
                original=str(item["original"]),
                translation=str(item["translation"]),
                type=str(item["type"]),
                bbox=bbox,
                confidence=float(item.get("confidence", 0.0)),
                translate=bool(item.get("translate", True)),
                translation_source=str(item.get("translation_source", "manual")),
                warning=item.get("warning"),
            )
        )
    return blocks


def prepare_translation_json(
    structured_blocks: list[StructuredBlock],
    translation_json: Path,
) -> list[TranslationBlock]:
    translator = ManualPreparationTranslator()
    translated_blocks = translator.translate(structured_blocks)
    save_json(translation_json, serialize_translation(translated_blocks))
    return translated_blocks


def print_manual_translation_instructions(translation_json: Path) -> None:
    print(f"Saved {translation_json}")
    print("Translate the TODO entries in that JSON, then rerun the command to render the English menu image.")


def main() -> int:
    args = parse_args()
    input_image = Path(args.input_image).expanduser().resolve()
    output_image = resolve_output_image(input_image, args.output)
    output_dir = output_image.parent

    ocr_json = output_dir / "ocr_result.json"
    corrected_ocr_json = output_dir / "corrected_ocr_result.json"
    structure_json = output_dir / "structure_result.json"
    translation_json = (
        Path(args.translation_json).expanduser().resolve()
        if args.translation_json
        else output_dir / "translation_result.json"
    )
    debug_image = output_dir / "debug_ocr.png"

    if not input_image.exists():
        raise SystemExit(f"Input image not found: {input_image}")

    print("Reading image...")
    print("Running OCR...")
    ocr_provider = PaddleOCRProvider()
    ocr_blocks = ocr_provider.run(input_image)
    print(f"Detected {len(ocr_blocks)} text blocks.")

    low_confidence_blocks = [block for block in ocr_blocks if block.confidence < 0.6]
    for block in low_confidence_blocks:
        print(f'WARNING: Low-confidence OCR detected: "{block.text}" confidence={block.confidence:.2f}')

    save_json(ocr_json, serialize_ocr(ocr_blocks))

    print("Running OCR correction pass...")
    corrector = OCRCorrectorFactory.from_environment()
    corrected_ocr_blocks = corrector.correct(ocr_blocks)
    corrected_count = sum(1 for block in corrected_ocr_blocks if block.changed)
    save_json(corrected_ocr_json, serialize_corrected_ocr(corrected_ocr_blocks))
    print(f"Corrected {corrected_count} OCR blocks.")

    print("Analyzing menu structure...")
    structure_analyzer = HeuristicMenuStructureAnalyzer()
    structured_blocks = structure_analyzer.analyze([block.to_ocr_block() for block in corrected_ocr_blocks])
    save_json(structure_json, serialize_structure(structured_blocks))

    if args.prepare_translation_json:
        print("Preparing translation JSON with TODO placeholders...")
        prepare_translation_json(structured_blocks, translation_json)
        print_manual_translation_instructions(translation_json)
        return 0

    if translation_json.exists():
        translated_blocks = load_translation_blocks(translation_json)
        if is_translation_complete(translated_blocks):
            print("Using existing translated JSON...")
        elif args.auto_translate:
            print("Translation JSON is incomplete. Running automatic translation...")
            translator = TranslatorFactory.from_environment()
            translated_blocks = translator.translate(structured_blocks)
            save_json(translation_json, serialize_translation(translated_blocks))
            print(f"Updated {translation_json}")
        else:
            print("Translation JSON is incomplete. Waiting for manual translation.")
            print_manual_translation_instructions(translation_json)
            return 0
    else:
        print("No translation JSON found. Preparing translation JSON with TODO placeholders...")
        prepare_translation_json(structured_blocks, translation_json)
        print_manual_translation_instructions(translation_json)
        return 0

    print("Computing layout...")
    layout_engine = LayoutEngine()
    layout_blocks = layout_engine.layout(translated_blocks)

    print("Rendering English menu...")
    from src.renderer import PillowMenuRenderer

    renderer = PillowMenuRenderer()
    renderer.render(input_image, layout_blocks, output_image)

    if args.debug:
        renderer.render_debug_ocr(input_image, ocr_blocks, debug_image)
        print(f"Saved {debug_image}")

    print(f"Saved {output_image}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
