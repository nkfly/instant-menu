# Website Template

This directory contains the first reusable static website template for rendering restaurant menu JSON into a customer-facing website.

Current files:

- `index.html`
- `styles.css`
- `script.js`

Current behavior:

- Loads menu data from `../restaurants/noodle_villa_ueno/menu.json`
- Loads crop metadata from `../restaurants/noodle_villa_ueno/crops/manifest.json`
- Renders the restaurant name, extraction notes, category navigation, and menu items
- Shows cropped dish photos inside menu cards when a matching crop is available
- Shows sold-out and inferred-price flags when present in the JSON
- Uses a static HTML, CSS, and JavaScript stack so the template is easy to host anywhere

To preview locally, serve the repository with a static web server and open `website_template/index.html`.
