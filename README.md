# AI Menu Generator (POC)

## Overview

This project aims to build an AI-powered system that converts an existing restaurant mobile ordering menu into a beautiful, editable, and multilingual menu website and printable PDF.

The initial target is restaurants using QR-code ordering systems such as AirREGI Order and similar platforms.

Instead of replacing the ordering system, this project focuses on creating a Menu Content Hub that generates customer-facing menus from existing menu data.

## Problem

Many restaurants already maintain their menu inside a mobile ordering system, but they still need to manually maintain:

- Paper menus
- Website menus
- Google Maps menu images
- Instagram menu posts
- Tourist-friendly multilingual menus

Every menu update requires updating multiple places manually.

## Vision

Maintain the menu once, publish it everywhere.

```text
QR Ordering System
        |
        v
   AI Menu Import
        |
        v
 Standard Menu Database
        |
        +-------- Website Menu
        +-------- Printable PDF
        +-------- Multilingual Menu
        +-------- QR Menu
        +-------- Future Integrations
```

## POC Strategy

Instead of building a QR crawler or mobile app first, validate the business value first.

### Input

Visit a restaurant and record the menu using screenshots or, preferably, screen recording.

Capture:

- Every category or tab
- Every menu item
- Item detail pages
- Options and modifiers
- Prices
- Images

### AI Processing

AI extracts the menu into structured JSON.

Example:

```text
Restaurant
 ├── Category
 │     ├── Item
 │     ├── Item
 │     └── Item
 ├── Category
 └── Category
```

Each item includes:

- Name
- Price
- Description
- Category
- Image reference
- Options
- Confidence score

Human review is performed before publishing.

### Output

Generate:

#### Website

- Mobile friendly
- Beautiful design
- Multi-language
- QR code
- Searchable categories

#### Printable Menu

- A4 PDF
- Restaurant-ready layout
- Multiple templates
- Bilingual or multilingual versions

## Why Not Build the Mobile App First?

The biggest unknown is not the technology.

The biggest unknown is:

> Will restaurants actually find value in the generated menu?

Building an Android or iOS app, QR import, crawler, and API integrations before validating demand introduces unnecessary risk.

The POC should answer:

- Can AI reconstruct a menu accurately?
- Does the generated menu look professional?
- Would restaurant owners actually use it?
- Would they pay for it?

## Recommended MVP Workflow

```text
Restaurant
    ↓
Screen Recording
    ↓
AI Vision
    ↓
Structured Menu JSON
    ↓
Human Review
    ↓
Website Generator
    ↓
PDF Generator
```

No mobile app required.

## Future Roadmap

### Phase 1

POC

- Screen recording
- AI extraction
- Manual review
- Website
- PDF

### Phase 2

Android App

- QR Scanner
- Import workflow
- AI extraction
- Menu editor

### Phase 3

iOS App

Same workflow as Android.

### Phase 4

Official Integrations

Support:

- AirREGI
- Smaregi
- Square
- Other POS systems

Use official APIs where available.

## Key Design Principles

- Validate the business before building complex integrations.
- AI should extract structured data, not directly generate final menus.
- Human review is mandatory before publishing.
- The Menu Database is the source of truth.
- QR import is an onboarding method, not the core product.
- The real value is maintaining one menu and publishing it everywhere.

## Long-term Goal

Build the "Canva + GitHub for restaurant menus."

Restaurants should be able to import an existing menu in minutes and automatically generate:

- Beautiful websites
- Printable menus
- Multilingual menus
- Marketing assets
- Future integrations

All from a single source of truth.

## Current POC Status

The first restaurant POC is now set up in this repository.

### Restaurant

- `noodle_villa_ueno`
- Source restaurant name in the screenshots: `黔莊 - 上野`

### What Has Been Done

- Created a restaurant-specific directory at `noodle_villa_ueno/`
- Stored the screenshot set under `noodle_villa_ueno/screenshots/`
- Read 23 screenshots from the restaurant's mobile ordering menu
- Extracted a first-pass structured menu JSON
- Saved the generated file in the repo at `noodle_villa_ueno/menu.json`

### Current Extraction Coverage

The current JSON includes these visible categories from the screenshots:

- `新品推荐`
- `进店必点`
- `套餐`
- `夏季限定`
- `牛肉粉`
- `羊肉粉`
- `酸辣粉`
- `小吃`

### Known Limitations

- This is a first-pass extraction and still requires human review.
- Some tabs appear to exist beyond the captured screenshots, especially `另加` and `经典`.
- Some items appear in multiple categories, which may be intentional merchandising rather than duplicates.
- At least one partially visible item price was inferred from nearby items.

## Repository Structure

```text
instant-menu/
├── README.md
└── noodle_villa_ueno/
    ├── menu.json
    └── screenshots/
```

## Sample Generated Menu JSON

Full file:

- `noodle_villa_ueno/menu.json`

Example excerpt:

```json
{
  "restaurant": {
    "slug": "noodle_villa_ueno",
    "display_name": "黔莊 - 上野",
    "internal_name": "Noodle Villa Ueno"
  },
  "source": {
    "type": "screenshots",
    "language": "zh-CN",
    "image_count": 23,
    "image_directory": "screenshots"
  },
  "extraction": {
    "status": "first_pass",
    "review_required": true
  },
  "categories": [
    {
      "name": "新品推荐",
      "items": [
        {
          "name": "啤酒自选套餐",
          "price_jpy": 1380,
          "description": null
        },
        {
          "name": "油酥花生",
          "price_jpy": 320,
          "description": null
        }
      ]
    }
  ]
}
```

## Next Steps

- Review the extracted menu JSON against the screenshots
- Normalize the schema for reusable ingestion across restaurants
- Add item IDs, image references, and confidence scores per item
- Generate the first menu webpage from the structured JSON
- Generate the first printable PDF from the same source data
