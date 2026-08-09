This directory stores generated debug artifacts and rendered English menu images.

Each restaurant should have its own output directory.

Recommended layout:

```text
output/
  honoya/
    ocr_result.json
    corrected_ocr_result.json
    structure_result.json
    translation_result.json
    debug_ocr.png
    menu_en.png
  another_restaurant/
    ...
```

Typical files inside each restaurant directory:

- `ocr_result.json`
- `corrected_ocr_result.json`
- `structure_result.json`
- `translation_result.json`
- `debug_ocr.png`
- `menu_en.png`
- `menu_site/index.html`
- `menu_site/menu_data.json`
- `menu_site/script.js`
- `menu_site/styles.css`
