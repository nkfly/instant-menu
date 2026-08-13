This directory stores generated debug artifacts and rendered English menu images.

Each restaurant should have its own output directory.

Recommended layout:

```text
output/
  honoya/
    restaurant.json
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
  another_restaurant/
    ...
```

Typical files inside each restaurant directory:

- `ocr_result.json`
- `restaurant.json` with the immutable UUIDv7, unique public slug, and display names
- `corrected_ocr_result.json`
- `structure_result.json`
- `translation_result.json`
- `debug_ocr.png`
- `menu_en.png`
- `menu_site/index.html`
- `menu_site/menu_data.json`
- `menu_site/script.js`
- `menu_site/styles.css`

`restaurant.json` is required for public deployment. The deployment build publishes the contents of `menu_site/` directly to `/restaurants/<public_slug>/`; `menu_site` remains only an internal generated-artifact directory.
