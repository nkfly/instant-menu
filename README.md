# Japanese Menu Image -> English Menu Image POC

## Overview

This repository is now a small Python proof-of-concept for one focused task:

> Take a photo or image of a Japanese restaurant menu and automatically generate an English menu image while preserving the original layout as much as possible.

The purpose of this POC is to validate whether a restaurant owner could realistically use an automatically generated English menu image for places like Google Maps or social media.

This is intentionally not a mobile app, not a menu editor, and not a production system.

## Core Goal

Input:

```text
menu_jp.jpg
```

Pipeline:

```text
Japanese Menu Image
        ↓
OCR
        ↓
Text + Bounding Boxes
        ↓
AI / OCR Correction Pass
        ↓
Menu Structure Analysis
        ↓
Japanese -> Restaurant-friendly English Translation
        ↓
Cover Original Japanese Text
        ↓
Layout English Text into Original Positions
        ↓
Render Final Image
```

Output:

```text
menu_en.png
```

The goal is to preserve the original photos, colors, prices, and approximate layout while replacing Japanese text with readable English.

## Important Technical Principle

The final English menu should be rendered programmatically.

Preferred architecture:

```text
OCR -> structured text -> LLM translation -> layout engine -> image renderer
```

Not:

```text
Original Image -> AI Image Generation -> New Menu Image
```

This keeps text more controllable, easier to debug, and cheaper to iterate on.

## Current Repository Direction

This repo has been pivoted away from the earlier menu website experiment.

The current codebase now focuses on:

- One menu image at a time
- Japanese -> English only
- OCR with bounding boxes
- Structure tagging
- Restaurant-aware translation
- Programmatic text replacement
- PNG output
- Intermediate JSON files for debugging

## Current Implementation

The current scaffold includes:

- A command-line entry point
- A PaddleOCR-based OCR adapter with Japanese text detection and bounding boxes
- An OCR correction pass that improves raw OCR text before structure analysis
- Heuristic structure analysis as the default baseline
- A manual translation handoff mode that creates `TODO` JSON for chatbot-assisted translation
- Optional automatic translation only when explicitly requested
- A simple layout engine for fitting English text inside the original text boxes
- A Pillow-based renderer
- Debug artifact output for OCR inspection

This keeps the system small and swappable while still matching the intended architecture.

## Project Structure

```text
instant-menu/
├── README.md
├── requirements.txt
├── main.py
├── input/
│   ├── README.md
│   └── honoya/
│       └── menu_jp.png
├── output/
│   ├── README.md
│   └── honoya/
│       ├── corrected_ocr_result.json
│       ├── menu_en.png
│       ├── ocr_result.json
│       ├── structure_result.json
│       └── translation_result.json
├── src/
│   ├── __init__.py
│   ├── correction.py
│   ├── layout.py
│   ├── models.py
│   ├── ocr.py
│   ├── renderer.py
│   ├── structure.py
│   └── translator.py
└── tests/
    ├── test_structure.py
    └── test_translator.py
```

## Installation

Create a Python environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The requirements intentionally include both:

- `PaddleOCR`
- `paddlepaddle`

because PaddleOCR needs the Paddle runtime for actual OCR inference.

## Recommended CLI

Basic usage:

```bash
python main.py input/honoya/menu_jp.png
```

If no translated JSON exists yet, the command will create `output/honoya/translation_result.json` with `TODO` placeholders and stop before rendering. This is the default workflow.

Specify an output path:

```bash
python main.py input/honoya/menu_jp.png --output output/honoya/manual_flow/menu_en.png
```

Generate OCR debug output:

```bash
python main.py input/honoya/menu_jp.png --debug
```

Prepare the manual translation JSON explicitly:

```bash
python main.py input/honoya/menu_jp.png --prepare-translation-json
```

Use a specific translation JSON path:

```bash
python main.py input/honoya/menu_jp.png --translation-json output/honoya/translation_result.json
```

Allow automatic translation explicitly:

```bash
python main.py input/honoya/menu_jp.png --auto-translate
```

Expected console flow:

```text
Reading image...
Running OCR...
Detected 23 text blocks.
Running OCR correction pass...
Corrected 6 OCR blocks.
Analyzing menu structure...
No translation JSON found. Preparing translation JSON with TODO placeholders...
Saved output/honoya/translation_result.json
Translate the TODO entries in that JSON, then rerun the command to render the English menu image.
```

## Restaurant Directory Convention

Each restaurant now has its own directory under both `input/` and `output/`.

Recommended layout:

```text
input/
  honoya/
    menu_jp.png

output/
  honoya/
    ocr_result.json
    corrected_ocr_result.json
    structure_result.json
    translation_result.json
    debug_ocr.png
    menu_en.png
```

If you keep the input image under `input/<restaurant>/`, the CLI now defaults to rendering into `output/<restaurant>/menu_en.png`.

## Intermediate Files

The POC saves intermediate outputs so OCR, structure, translation, and rendering can be debugged independently.

Typical files:

```text
output/honoya/ocr_result.json
output/honoya/corrected_ocr_result.json
output/honoya/structure_result.json
output/honoya/translation_result.json
output/honoya/debug_ocr.png
output/honoya/menu_en.png
```

`translation_result.json` is now an intentional handoff file, not just a debug artifact. The normal flow is:

1. Generate it with `TODO` placeholders.
2. Paste it into an AI chatbot and manually fill the `translation` fields.
3. Rerun the CLI so the renderer uses the completed JSON directly.

Example shape:

```json
[
  {
    "id": 1,
    "original": "特製醤油ラーメン",
    "translation": "TODO",
    "type": "menu_item",
    "bbox": [120, 350, 300, 48],
    "confidence": 0.97,
    "translate": true,
    "translation_source": "todo"
  }
]
```

## OCR Strategy

The default OCR adapter uses PaddleOCR because it is a practical POC choice for Japanese printed menu text and returns:

- recognized text
- bounding boxes
- confidence scores

The current implementation converts PaddleOCR quadrilateral detections into axis-aligned bounding boxes for downstream structure analysis and rendering.

If OCR confidence is low, the CLI logs warnings rather than silently inventing text.

## OCR Correction Pass

The repo now includes a second-pass OCR correction stage between raw OCR and menu structure analysis.

Current behavior:

- Save the raw OCR result to `output/<restaurant>/ocr_result.json`
- Run a correction pass over the recognized text while keeping the same coordinates
- Save the corrected result to `output/<restaurant>/corrected_ocr_result.json`
- Use the corrected text for structure analysis, translation, and rendering

This stage is intended to improve practical recognition quality for menu-specific text such as:

- broken katakana
- spacing around prices
- common menu vocabulary OCR mistakes
- small formatting artifacts

The correction pass currently supports:

- an optional OpenAI-based correction mode when `OPENAI_API_KEY` is set
- a local heuristic menu-aware correction fallback when no API key is configured

This makes the OCR pipeline closer to:

```text
Image -> PaddleOCR -> corrected_ocr.json -> structure -> translation -> render
```

## Structure Analysis Strategy

The current baseline structure analyzer is heuristic-first so the system can run without an external LLM dependency.

It classifies OCR blocks into categories such as:

- `section_title`
- `menu_item`
- `description`
- `price`
- `label`
- `promotion`
- `other`

This is intended to be easy to replace with a stronger LLM-based analyzer later.

Once a block is classified as `price`, the renderer preserves the original text in the image instead of covering and redrawing it. This helps keep numeric pricing visually stable even when other nearby text is translated.

## Translation Strategy

The translation module is designed around restaurant-friendly English, not literal word-for-word translation.

Examples of desired output:

- `唐揚げ` -> `Japanese Fried Chicken`
- `親子丼` -> `Oyakodon (Chicken & Egg Rice Bowl)`
- `ネギトロ` -> `Minced Tuna with Green Onion`

The repo currently supports:

- A default manual-preparation mode that emits `TODO` placeholders for chatbot-assisted translation
- An optional OpenAI-based translator when `OPENAI_API_KEY` is set and `--auto-translate` is used
- A fallback dictionary/heuristic translator when `--auto-translate` is used without an API key

Prices are generally preserved rather than translated.

In rendering terms, `price` blocks are treated as keep-original regions. Even if a translated JSON includes an English price string, the current renderer leaves the original price text untouched in the final menu image.

## Manual Translation Workflow

This repo now supports a practical low-cost workflow before API integration:

1. Run OCR and structure analysis.
2. Save `translation_result.json` with `TODO` placeholders.
3. Paste that JSON into an external AI chatbot.
4. Replace the `TODO` fields with English menu text.
5. Rerun the CLI to render the English menu image from the completed JSON.

Normal render behavior is now:

1. If `translation_result.json` exists and all translatable entries are filled in, the renderer uses it directly.
2. If the JSON exists but still contains `TODO`, the app stops and waits for manual translation.
3. Automatic translation is used only when `--auto-translate` is passed explicitly.

This keeps API usage opt-in and makes the OCR, translation, and rendering stages independently testable.

## Rendering Strategy

The renderer currently follows the simple POC-friendly replacement approach:

1. detect the Japanese text bounding box
2. estimate a local background color
3. cover the original text area
4. fit English text back into the same approximate region
5. export PNG

The current objective is readability and structural correctness, not perfect typography or perfect background reconstruction.

## Debugging

Use `--debug` to create an OCR inspection image:

```text
output/debug_ocr.png
```

This outlines detected text boxes and labels them by ID so OCR and layout problems are easy to inspect.

## Environment Variables

Optional environment variables:

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `PADDLE_PDX_CACHE_HOME`

If no API key is configured, the app can still:

- prepare `TODO` translation JSON for manual completion
- or use the local heuristic translator when `--auto-translate` is requested

By default, this repo sets `PADDLE_PDX_CACHE_HOME` to a local `.paddlex/` directory inside the project so PaddleOCR can run cleanly in restricted environments.

## POC Success Criteria

This POC does not need perfect results.

It is successful if roughly 7-8 out of 10 normal printed restaurant menus produce an English image that is:

- readable
- structurally correct
- reasonably translated
- visually understandable
- usable without manual editing

The key question is:

> Would a small restaurant owner consider uploading the generated image to Google Maps?

## Current Limitations

- PaddleOCR setup may require additional local runtime dependencies depending on the environment
- The baseline structure analysis is heuristic, not full LLM reasoning yet
- The fallback translator is useful for development but not high-quality enough for production
- Pillow rendering is intentionally simple and not a full layout engine
- Background reconstruction is intentionally basic

## Next Steps

- Test with around 10 real Japanese menu images
- Improve structure analysis with a stronger LLM pass
- Improve menu-specific translation quality
- Tighten text fitting for dense layouts
- Add better handling for dark or textured backgrounds
- Add optional perspective correction and preprocessing

## Long-term Product Vision

This is not just a translation toy.

The longer-term vision is a restaurant menu publishing tool that helps restaurant owners turn an existing local-language paper menu into a professional multilingual digital menu from a single photo.

For the POC, the focus stays deliberately narrow:

> Take one Japanese menu image and automatically generate one usable English menu image.
