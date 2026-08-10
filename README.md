# MenuInbound

**Make your menu ready for the world.**

**飲食店のインバウンド対応を、メニューから。**

## Overview

MenuInbound helps small and independent restaurants in Japan become more accessible to international customers.

This repository currently contains a small Python proof-of-concept for one focused task:

> Take a photo or image of a Japanese restaurant menu and automatically generate an English menu image while preserving the original layout as much as possible.

The purpose of this POC is to validate whether a restaurant owner could realistically use an automatically generated English menu image for places like Google Maps or social media.

This is intentionally not a mobile app, not a menu editor, and not a production system.

## Vision

The goal is not simply to build an AI menu translator.

The longer-term vision is to use multilingual menu creation as the entry point for helping restaurants improve their overall inbound readiness.

> We are not just translating menus. We are lowering the barrier for local restaurants to serve customers from around the world.

## Positioning

MenuInbound is for small restaurants in Japan that want to become easier for international customers to understand without redesigning their operations.

It should help restaurants become more accessible without requiring them to:

- redesign their menus
- hire a translation agency
- maintain another complicated system
- learn new software
- spend significant time managing multilingual content

The product direction is to make this process extremely simple.

## Core Problem

Many small restaurants in Japan still have:

- Japanese-only paper menus
- Japanese-only menu photos on Google Maps
- no multilingual website
- no easy-to-read digital menu for international customers

International visitors may discover these restaurants through Google Maps, but still cannot easily understand:

- what the restaurant serves
- how much dishes cost
- how to order

This gap is where MenuInbound starts.

## Current POC

The first technical POC has already successfully demonstrated:

```text
Japanese Menu Photo
        ↓
OCR
        ↓
Menu Structure Analysis & AI correcting OCR result
        ↓
AI Restaurant Translation
        ↓
Layout / Rendering
        ↓
Translated English Menu Image
```

A usable English menu image can now be automatically generated from an existing Japanese menu photo.

The generated image does not need to reach professional print-design quality.

That is no longer the primary goal.

Instead, the translated image is intended primarily for digital use, such as:

- Google Maps menu photos
- Google Business Profile
- restaurant websites
- social media
- digital reference for international visitors

The current POC is intentionally narrow:

- take one Japanese menu image
- generate one readable English menu image
- generate one simple English/Japanese menu website
- keep the workflow lightweight enough for fast iteration and restaurant feedback

## Product Direction

MenuInbound should generate two main outputs from the same restaurant menu data.

### 1. Multilingual Menu Images

Convert existing Japanese menu photos into translated versions.

Initial languages:

- Japanese
- English

Future languages:

- Traditional Chinese
- Simplified Chinese
- Korean

The translated images should preserve the original menu structure and approximate layout.

The goal is readability and familiarity rather than print-quality graphic design.

Primary use case:

```text
Before visiting the restaurant

International visitor
        ↓
Google Maps
        ↓
Restaurant profile
        ↓
Translated menu image
        ↓
Understand food and prices
        ↓
Decide whether to visit
```

### 2. Static Multilingual Web Menu

The same OCR and structured menu data should also be rendered into a clean, mobile-friendly static website.

Example:

```text
menuinbound.com/hano-ya
```

The web menu should prioritize readability rather than preserving the original paper-menu layout.

Example interface:

```text
Hano-ya

日本語 | English | 中文 | 한국어

--------------------

Beer

Draft Beer
Medium                    ¥600
Small                     ¥350


Whisky

Super Nikka

Highball                  ¥480
Single                    ¥480
Bottle                  ¥7,000
```

Each restaurant receives:

- a dedicated static menu URL
- a QR code pointing to that URL
- a mobile-friendly multilingual menu

The restaurant can place the QR code:

- on tables
- on the existing paper menu
- near the entrance
- near the register

Primary use case:

```text
After arriving at the restaurant

Customer sits down
        ↓
Scans QR code
        ↓
Selects language
        ↓
Reads multilingual menu
```

This is not an ordering system.

It is intentionally a simple multilingual digital menu.

## MVP Business Model

Do not decide yet whether menu images or QR web menus are the main product.

Test both with real restaurant owners.

Potential initial packages:

### Menu Images

Multilingual digital menu images for Google Maps and other online platforms.

Example test price:

**¥980**

### QR Web Menu

Mobile-friendly multilingual web menu with dedicated URL and QR code.

Example test price:

**¥1,480**

### Complete Package

Both multilingual menu images and QR web menu.

Example test price:

**¥1,980**

These prices are experiments, not final pricing.

The immediate goal is to measure willingness to pay.

## Customer Acquisition Strategy

Do not wait for restaurant owners to discover MenuInbound.

Use proactive outreach.

Identify small restaurants that:

- have good Google Maps ratings
- receive international visitors
- have Japanese-only menus
- have Japanese-only menu photos
- do not already provide strong multilingual support

Create a free sample for the restaurant.

For example:

```text
Original Japanese Menu
        ↓
MenuInbound
        ↓
English Menu Sample
        +
QR Web Menu Demo
```

Then contact the restaurant owner with an already-working demonstration.

The sales message should effectively be:

> We noticed that your menu is currently mainly available in Japanese, so we created a free English sample for your restaurant. You can see the translated menu and mobile web version here.

This is preferable to selling the concept before showing the result.

The product itself becomes the sales material.

## Future Business Opportunities

MenuInbound should not become a POS or ordering-system company.

However, the menu service can become a customer-acquisition entry point for broader restaurant digitalization.

For example:

```text
Free / Paid Multilingual Menu
            ↓
Relationship with Restaurant Owner
            ↓
Discover additional needs
            ↓
Mobile Ordering
POS
Cashless Payment
Wi-Fi
Other Inbound Services
            ↓
Partner / Referral Revenue
```

If a restaurant already has a suitable mobile-order or POS system, no additional product should be pushed.

If the restaurant needs one, MenuInbound may introduce appropriate third-party services through official referral or partner programs.

The goal is to generate qualified referrals rather than becoming an installation and technical-support company.

MenuInbound should remain focused on:

**Restaurant inbound enablement.**

## What Not to Build Yet

Do not build:

- iOS app
- Android app
- restaurant account system
- complex authentication
- restaurant dashboard
- CMS
- Canva-style menu editor
- POS
- ordering system
- reservation system
- payment system for restaurant customers
- analytics dashboard
- complex SaaS administration

These features should only be considered after real restaurant demand has been validated.

## Public Website Hosting

The public MenuInbound website is deployed as a Cloudflare Worker with static assets.

`website/` remains the editable landing-page source. Before every Wrangler deployment, the configured build command creates a clean `dist/` directory containing the landing page and only the restaurant assets intended for public access.

The public landing page files live in their own directory:

```text
website/
  index.html
  styles.css
```

The landing page references restaurant samples with public paths such as `/output/honoya/menu_en.png` and `/output/honoya/menu_site/`.
It remains separate from the generated restaurant menu output under `output/<restaurant>/menu_site/`.
It is a concise Japanese-only landing page that introduces the two outputs, shows the current Honoya sample, and presents the experimental pricing. Customer-facing labels use readable Japanese typography without extra-small explanatory text.

The generated deployment structure is:

```text
dist/
  index.html
  styles.css
  output/
    honoya/
      menu_en.png
      menu_site/
```

OCR results, translation JSON, debug images, and other internal files are not copied into `dist/`.

Deploy with the existing command:

```bash
npx wrangler deploy
```

Wrangler reads `wrangler.jsonc`, runs `python3 scripts/build_public_site.py`, and uploads `dist/` as the Worker's static assets. No separate build command is required.

No Cloudflare dashboard asset-directory change is required when deploying with this Wrangler configuration. Keep the custom domain attached to the existing Worker. If the existing Worker service is not named `menuinbound`, update the `name` field in `wrangler.jsonc` to match it before deploying so Wrangler updates the correct Worker.

## Current Technical Flow

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

Primary output:

```text
menu_en.png
```

The immediate technical goal is to preserve the original photos, colors, prices, and approximate layout while replacing Japanese text with readable English.

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

This repo has been pivoted away from the earlier menu website experiment and is now aligned with the MenuInbound POC.

The current codebase focuses on:

- One menu image at a time
- Japanese -> English only
- OCR with bounding boxes
- Structure tagging
- Restaurant-aware translation
- Programmatic text replacement
- PNG output
- Static menu website output
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
- A static menu website generator for restaurant-specific output directories
- Debug artifact output for OCR inspection

This keeps the system small and swappable while still matching the intended architecture.

## Project Structure

```text
instant-menu/
├── README.md
├── requirements.txt
├── main.py
├── wrangler.jsonc
├── website/
│   ├── index.html
│   └── styles.css
├── scripts/
│   └── build_public_site.py
├── input/
│   ├── README.md
│   └── honoya/
│       └── menu_jp.png
├── output/
│   ├── README.md
│   └── honoya/
│       ├── corrected_ocr_result.json
│       ├── menu_site/
│       │   ├── index.html
│       │   ├── menu_data.json
│       │   ├── script.js
│       │   └── styles.css
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
    menu_site/
      index.html
      menu_data.json
      script.js
      styles.css
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
output/honoya/menu_site/index.html
```

`translation_result.json` is now an intentional handoff file, not just a debug artifact. The normal flow is:

1. Generate it with `TODO` placeholders.
2. Paste it into an AI chatbot and manually fill the `translation` fields.
3. Rerun the CLI so the renderer uses the completed JSON directly.

When the translation JSON is complete, the output phase now generates both:

- the English menu image
- a static menu website directory under `output/<restaurant>/menu_site/`

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

## Static Menu Website Output

The output phase now also generates a static menu website under each restaurant directory.

Example:

```text
output/honoya/menu_site/
  index.html
  menu_data.json
  script.js
  styles.css
```

Current website behavior:

- uses the translated JSON as the data source
- builds a left sidebar of menu sections
- renders menu cards with title and price
- omits image blocks when no food photo is available
- includes a bottom-left English / Japanese segmented switch labeled `EN` and `JP`
- preserves the page layout when switching languages so scroll position stays consistent
- is optimized for mobile-first browsing similar to QR ordering menus

This website output is intentionally simple and static so it can be previewed or hosted without additional tooling.

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
