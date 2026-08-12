# MenuInbound

**Make your menu ready for the world.**

**飲食店のインバウンド対応を、メニューから。**

MenuInbound helps small and independent restaurants in Japan make their menus understandable to international customers.

The current proof of concept turns one Japanese restaurant menu image into:

1. A translated English menu image that preserves the original layout as much as practical.
2. A mobile-friendly English/Japanese static menu website generated from the same structured menu data.

The public website is available at [menuinbound.com](https://menuinbound.com/).

## Language Convention

- Project communication, source documentation, and development discussion are in English.
- The public MenuInbound landing page is in Japanese because restaurant owners in Japan are its primary audience.
- Generated restaurant menu sites currently support English and Japanese.
- The product direction is multilingual, with English and Chinese as initial customer-facing translation targets.

## Vision

MenuInbound is not only an AI translation tool.

The long-term goal is to use multilingual menu creation as the entry point for helping restaurants improve their overall inbound readiness.

> We are not just translating menus. We are lowering the barrier for local restaurants to serve customers from around the world.

MenuInbound should remain focused on **restaurant inbound enablement**, rather than becoming a POS or ordering-system company.

## Core Problem

Many small restaurants in Japan still have:

- Japanese-only paper menus
- Japanese-only menu photos on Google Maps
- no multilingual website
- no simple digital menu for international customers

International visitors may discover these restaurants online but still cannot confidently understand what they serve, what dishes cost, or whether to visit.

Restaurant owners often do not want to redesign their menus, hire a translation agency, learn new software, or maintain another complicated system.

MenuInbound should make the process as simple as providing existing menu photos.

## Current POC

The technical POC has demonstrated this workflow:

```text
Japanese Menu Image
        ↓
PaddleOCR + Bounding Boxes
        ↓
AI / Heuristic OCR Correction
        ↓
Menu Structure Analysis
        ↓
Restaurant-aware English Translation
        ↓
Human Translation Expert Review
        ↓
Programmatic Image Rendering
        ↓
English Menu Image + Bilingual Web Menu
```

The first POC restaurant is **Honoya (はの家)**.

The generated image is intended mainly for digital use:

- Google Maps menu photos
- Google Business Profile
- restaurant websites
- social media
- digital reference for international visitors

The goal is readability and practical usefulness, not professional print-design quality.

## Product Outputs

### 1. Multilingual Menu Images

MenuInbound replaces Japanese menu text with concise, restaurant-friendly translations while preserving the original food photos, prices, colors, and approximate layout. The current POC renders English, with Chinese planned as an initial additional language.

Primary use case:

```text
Before the visit

International visitor
        ↓
Finds the restaurant online
        ↓
Views a translated menu image
        ↓
Understands the food and prices
        ↓
Decides whether to visit
```

### 2. Static Multilingual Web Menus

The same structured menu data is rendered into a clean, mobile-friendly static website.

Current behavior:

- dedicated output directory per restaurant
- English/Japanese language switch labeled `EN` and `JP`
- bottom-left floating language control
- stable layout and scroll position when switching languages
- left sidebar with menu categories and active-section tracking
- menu items with names and prices
- no placeholder image area when an item has no photo
- static files that can be hosted without an application server

Primary use case:

```text
At the restaurant

Customer sits down
        ↓
Opens or scans the menu URL
        ↓
Selects a language
        ↓
Reads the menu
```

This is intentionally not an ordering system.

## Business Validation

The initial offers are experiments for measuring restaurant demand and willingness to pay:

| Package | Experimental price |
| --- | ---: |
| Multilingual menu images | ¥980 |
| QR web menu | ¥1,480 |
| Images + web menu | ¥1,980 |

The current acquisition strategy is proactive outreach:

1. Find well-reviewed restaurants with Japanese-only menus and international visitors.
2. Create a free multilingual image and web-menu sample.
3. Show the owner a working result instead of selling an abstract concept.
4. Measure whether the restaurant would use and pay for it.

The product itself becomes the sales material.

## What Not to Build Yet

Do not build these until real restaurant demand has been validated:

- iOS or Android apps
- restaurant accounts or dashboards
- complex authentication
- CMS or Canva-style editor
- POS or ordering system
- reservation system
- restaurant-customer payments
- analytics dashboard
- complex SaaS administration

## Technical Principles

- The structured menu data is the source of truth.
- AI extracts, corrects, classifies, and translates text; it does not regenerate the entire menu image.
- The final image is rendered programmatically with Pillow.
- A human translation expert reviews translated menu content before delivery.
- Prices are preserved from the original image instead of being covered and redrawn.
- OCR, correction, structure, translation, layout, and rendering remain independently debuggable.
- Automatic paid API usage is opt-in.

Preferred architecture:

```text
OCR -> structured text -> translation -> layout engine -> image renderer
```

Not:

```text
Original image -> generative image model -> recreated menu
```

## Repository Structure

```text
instant-menu/
├── README.md
├── requirements.txt
├── main.py
├── package.json
├── playwright.config.mjs
├── website/
│   ├── index.html
│   └── styles.css
├── deploy/
│   ├── build.mjs
│   ├── wrangler.jsonc
│   └── dist/                  # generated and gitignored
├── input/
│   └── honoya/
│       └── menu_jp.png
├── output/
│   └── honoya/
│       ├── ocr_result.json
│       ├── corrected_ocr_result.json
│       ├── structure_result.json
│       ├── translation_result.json
│       ├── debug_ocr.png
│       ├── menu_en.png
│       └── menu_site/
│           ├── index.html
│           ├── menu_data.json
│           ├── script.js
│           └── styles.css
├── src/
│   ├── correction.py
│   ├── layout.py
│   ├── menu_site.py
│   ├── models.py
│   ├── ocr.py
│   ├── renderer.py
│   ├── structure.py
│   └── translator.py
└── tests/
    ├── ui/
    │   └── public-site.spec.mjs
    └── test_*.py
```

## Local Installation

Create an isolated Python environment and install the OCR application dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The requirements include both `PaddleOCR` and `paddlepaddle`, because PaddleOCR needs the Paddle runtime for inference.

These Python packages are required only for the local menu-processing application. They are not required for deploying the public static website.

## Restaurant Directory Convention

Each restaurant has its own directory under both `input/` and `output/`:

```text
input/<restaurant>/menu_jp.png
output/<restaurant>/...
```

For example:

```text
input/honoya/menu_jp.png
output/honoya/menu_en.png
```

When the input follows this convention, the CLI automatically uses the matching restaurant output directory.

## Running the POC

Basic command:

```bash
python main.py input/honoya/menu_jp.png
```

Useful options:

```bash
# Produce the OCR bounding-box debug image
python main.py input/honoya/menu_jp.png --debug

# Explicitly prepare the manual translation handoff JSON
python main.py input/honoya/menu_jp.png --prepare-translation-json

# Use a specific completed translation JSON
python main.py input/honoya/menu_jp.png \
  --translation-json output/honoya/translation_result.json

# Explicitly allow automatic translation
python main.py input/honoya/menu_jp.png --auto-translate

# Override the rendered image path
python main.py input/honoya/menu_jp.png \
  --output output/honoya/menu_en.png
```

## Default Manual Translation Workflow

The default workflow avoids paid translation API usage:

1. Run PaddleOCR.
2. Save `ocr_result.json` with text, coordinates, and confidence values.
3. Run the OCR correction pass and save `corrected_ocr_result.json`.
4. Analyze menu structure and save `structure_result.json`.
5. Create `translation_result.json` with `TODO` translation fields.
6. Ask an AI chatbot to translate each `original` field into the matching `translation` field without changing the JSON structure.
7. Save the completed JSON in the same restaurant output directory.
8. Rerun the same CLI command.
9. Render `menu_en.png` and generate `menu_site/`.

Translation decision logic:

```text
Completed translation_result.json exists?
        │
        ├── Yes -> render directly
        │
        └── No / contains TODO
                ├── --auto-translate -> use configured API or fallback
                └── default -> stop and wait for manual translation
```

If one translation fails, the pipeline preserves the original text and continues rather than crashing the entire menu.

## Intermediate Files

The pipeline keeps intermediate files so each stage can be reviewed independently.

### `ocr_result.json`

Raw PaddleOCR output with detected text, bounding boxes, and confidence scores.

### `corrected_ocr_result.json`

Second-pass corrected text using the same coordinates. The correction stage can use OpenAI when configured or local menu-aware heuristics without an API key.

### `structure_result.json`

Blocks classified as values such as:

- `section_title`
- `menu_item`
- `description`
- `price`
- `label`
- `promotion`
- `other`

### `translation_result.json`

The manual or automatic translation handoff file. Example:

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

Blocks classified as `price` use `translate: false` and remain untouched in the rendered image.

## OCR and Correction

PaddleOCR is the default OCR engine because it supports Japanese printed text and returns coordinates and confidence scores.

The adapter converts PaddleOCR quadrilaterals into axis-aligned bounding boxes for downstream processing.

Low-confidence detections produce warnings instead of silently inventing text.

The correction pass improves common menu OCR problems while preserving coordinates, including:

- broken katakana
- spacing around prices
- common restaurant vocabulary errors
- small formatting artifacts

## Translation

Translations should optimize for:

```text
correctness + natural restaurant English + layout friendliness
```

Examples:

- `唐揚げ` -> `Japanese Fried Chicken`
- `親子丼` -> `Oyakodon (Chicken & Egg Rice Bowl)`
- `ネギトロ` -> `Minced Tuna with Green Onion`

The application supports:

- manual chatbot-assisted translation by default
- optional OpenAI translation when `OPENAI_API_KEY` is set and `--auto-translate` is passed
- a local dictionary/heuristic fallback for development

## Rendering

The image renderer:

1. estimates the local background around each translated text block
2. covers the original Japanese text
3. wraps and scales the English translation to fit
4. draws the English text in approximately the same position
5. preserves price blocks
6. exports PNG

Basic background reconstruction is acceptable for the POC. Advanced inpainting and perfect font matching are intentionally deferred.

## Public Landing Page

The editable public landing page source is under `website/`.

It is:

- written in Japanese for restaurant owners in Japan
- intentionally concise
- responsive on desktop and mobile
- uses compact vertical spacing so sections remain clearly separated without feeling stretched
- keeps the opening hero focused on the core message, with samples in a dedicated section
- presents service, sample, benefits, usage flow, and pricing in that order
- visually based on the MenuInbound orange palette
- explicitly explains that multilingual output includes English and Chinese
- explains how multilingual menus can improve Google Maps discovery, ordering confidence, and revenue opportunities
- connected to the Honoya menu image and web-menu samples

The source uses public URLs such as:

```text
/restaurants/honoya/menu_en.png
/restaurants/honoya/menu_site/
```

## Cloudflare Workers Deployment

The public site is deployed as a Cloudflare Worker with static assets.

The deployment project is isolated under `deploy/`. This prevents Cloudflare Workers Builds from detecting the repository-level `requirements.txt` and downloading PaddleOCR or other Python packages during website deployment.

Configure **Cloudflare Workers > Settings > Build** as follows:

| Setting | Value |
| --- | --- |
| Root directory | `deploy` |
| Build command | `node build.mjs` |
| Deploy command | `npx wrangler deploy` |

After changing these settings, trigger a new deployment. A successful build should include log lines similar to:

```text
Built deploy/dist/ with public restaurant assets: honoya
Read 7 files from the assets directory .../deploy/dist
```

The exact file count may increase as more public restaurant assets are added.

Keep the existing custom domain attached to the Worker.

If the Cloudflare Worker is not named `menuinbound`, update the `name` field in `deploy/wrangler.jsonc` before deploying.

### Deployment Build

`deploy/build.mjs` uses only built-in Node.js modules. It creates a clean `deploy/dist/` containing:

```text
deploy/dist/
├── index.html
├── styles.css
└── restaurants/
    └── <restaurant>/
        ├── menu_en.png
        └── menu_site/
```

Only public restaurant assets are copied. These files are excluded:

- OCR results
- corrected OCR results
- structure and translation JSON outside the public menu-site data
- debug images
- input menu images
- Python source and dependencies

The generated `deploy/dist/` directory is gitignored.

For local deployment testing from `deploy/`:

```bash
cd deploy
npx wrangler deploy --dry-run
```

The verified dry run executes `node build.mjs`, reads the static assets from `deploy/dist/`, and does not install the OCR application dependencies.

If Cloudflare still runs automatic dependency installation because of an existing build configuration, set the build variable `SKIP_DEPENDENCY_INSTALL=1`.

If the deployment log instead reports `Output Directory: website` or reads only two files from `website/`, Cloudflare did not apply the `deploy` root directory. In that case, recheck the Worker's build settings and redeploy. That incorrect configuration publishes only the landing-page HTML and CSS, causing URLs such as `/restaurants/honoya/menu_en.png` and `/restaurants/honoya/menu_site/` to return `404 Not Found`.

## Tests

Install the UI test dependency and Chromium once:

```bash
npm install
npx playwright install chromium
```

After every code change, run the complete regression suite before committing:

```bash
npm test
```

`npm test` runs the Python unit tests and Playwright UI regression tests. The suite covers:

- OCR correction, layout, menu-site data generation, path inference, structure classification, and translation behavior
- isolated construction of the public `deploy/dist/` bundle
- successful HTTP responses for the landing page, restaurant menu, images, scripts, styles, and internal links
- broken-image and browser-error detection
- horizontal-overflow checks on desktop and mobile viewports
- restaurant-menu rendering and stable page height/scroll position while switching between English and Japanese

The UI suite starts a temporary local server for `deploy/dist/`, so it tests the same public directory structure that Cloudflare deploys. A failed regression must be fixed or explicitly documented before a change is committed.

## Environment Variables

Optional local application variables:

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `PADDLE_PDX_CACHE_HOME`

Without an OpenAI API key, the default manual translation workflow remains fully usable.

The application defaults `PADDLE_PDX_CACHE_HOME` to the repository-local `.paddlex/` directory for predictable PaddleOCR behavior in restricted environments.

## Current Limitations

- Printed horizontal Japanese text is the primary OCR target.
- OCR quality still varies with dense, dark, textured, angled, or handwritten menus.
- Structure analysis is heuristic-first rather than fully LLM-driven.
- Manual chatbot translation still requires a human handoff.
- Rendering uses basic background estimation rather than advanced inpainting.
- The current web menu does not include cropped dish photos unless image data is available.
- Japanese and English are the only implemented menu-site languages.

## POC Success Criteria

The POC is successful if roughly 7-8 out of 10 normal printed restaurant menus produce an English result that is:

- readable
- structurally correct
- reasonably translated
- visually understandable
- usable without extensive manual editing

The key business question is:

> Would a small restaurant owner consider publishing the generated result on Google Maps or using the web menu in the restaurant?

## Next Steps

- Test approximately 10 real Japanese menu styles.
- Improve OCR correction using menu context.
- Improve restaurant-aware structure analysis and translation.
- Tighten text fitting for dense layouts.
- Add perspective correction and stronger preprocessing where useful.
- Validate the menu-image and QR web-menu offers with restaurant owners.
- Add Traditional Chinese, Simplified Chinese, and Korean only after demand is validated.

## Longer-Term Opportunity

MenuInbound should use multilingual menus to build trusted relationships with restaurant owners and discover broader inbound needs.

Where appropriate, it may introduce third-party services such as mobile ordering, POS, cashless payments, or Wi-Fi through official partner and referral programs. It should not become the installation and technical-support provider for those systems.

The long-term product vision is a **restaurant menu publishing tool** that turns an existing local-language menu into professional multilingual digital assets from a single source of truth.
