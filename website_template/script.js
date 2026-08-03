const DATA_URL = "../restaurants/noodle_villa_ueno/menu.json";
const CROP_MANIFEST_URL = "../restaurants/noodle_villa_ueno/crops/manifest.json";

const currencyFormatter = new Intl.NumberFormat("ja-JP", {
  style: "currency",
  currency: "JPY",
  maximumFractionDigits: 0
});

const titleEl = document.querySelector("#restaurant-name");
const subtitleEl = document.querySelector("#restaurant-subtitle");
const categoryCountEl = document.querySelector("#stat-categories");
const itemCountEl = document.querySelector("#stat-items");
const statusBannerEl = document.querySelector("#status-banner");
const notesListEl = document.querySelector("#extraction-notes");
const categoryNavEl = document.querySelector("#category-nav");
const menuSectionsEl = document.querySelector("#menu-sections");

const categoryLinkTemplate = document.querySelector("#category-link-template");
const menuSectionTemplate = document.querySelector("#menu-section-template");
const menuItemTemplate = document.querySelector("#menu-item-template");

async function loadMenu() {
  const response = await fetch(DATA_URL);

  if (!response.ok) {
    throw new Error(`Unable to load menu data from ${DATA_URL}`);
  }

  return response.json();
}

async function loadCropManifest() {
  const response = await fetch(CROP_MANIFEST_URL);

  if (!response.ok) {
    throw new Error(`Unable to load crop manifest from ${CROP_MANIFEST_URL}`);
  }

  return response.json();
}

function slugifyCategoryName(name) {
  return name
    .toLowerCase()
    .trim()
    .replace(/\s+/g, "-")
    .replace(/[^\w\u4e00-\u9fff-]/g, "");
}

function summarizeCategory(category) {
  const soldOutCount = category.items.filter((item) => item.sold_out).length;
  const inferredCount = category.items.filter((item) => item.price_inferred).length;
  const parts = [`${category.items.length} items`];

  if (soldOutCount > 0) {
    parts.push(`${soldOutCount} sold out`);
  }

  if (inferredCount > 0) {
    parts.push(`${inferredCount} inferred`);
  }

  return parts.join(" · ");
}

function createTag(text, variant) {
  const tag = document.createElement("span");
  tag.className = `tag ${variant}`;
  tag.textContent = text;
  return tag;
}

function buildCropIndex(manifest) {
  const cropIndex = new Map();

  for (const entry of manifest.entries ?? []) {
    const existing = cropIndex.get(entry.item_name) ?? [];
    existing.push(`../${entry.crop_file}`);
    cropIndex.set(entry.item_name, existing);
  }

  return cropIndex;
}

function consumeCropPath(cropIndex, itemName) {
  const available = cropIndex.get(itemName);

  if (!available || available.length === 0) {
    return null;
  }

  return available.shift();
}

function renderNotes(notes = []) {
  notesListEl.replaceChildren();

  notes.forEach((note) => {
    const item = document.createElement("li");
    item.textContent = note;
    notesListEl.appendChild(item);
  });
}

function renderCategoryNavigation(categories) {
  categoryNavEl.replaceChildren();

  categories.forEach((category) => {
    const fragment = categoryLinkTemplate.content.cloneNode(true);
    const link = fragment.querySelector(".category-link");
    const linkName = fragment.querySelector(".category-link__name");
    const linkCount = fragment.querySelector(".category-link__count");
    const sectionId = `category-${slugifyCategoryName(category.name)}`;

    link.href = `#${sectionId}`;
    linkName.textContent = category.name;
    linkCount.textContent = category.items.length;

    categoryNavEl.appendChild(fragment);
  });
}

function renderCategories(categories, cropIndex) {
  menuSectionsEl.replaceChildren();

  categories.forEach((category, sectionIndex) => {
    const fragment = menuSectionTemplate.content.cloneNode(true);
    const section = fragment.querySelector(".menu-section");
    const title = fragment.querySelector(".menu-section__title");
    const summary = fragment.querySelector(".menu-section__summary");
    const grid = fragment.querySelector(".menu-grid");
    const sectionId = `category-${slugifyCategoryName(category.name)}`;

    section.id = sectionId;
    title.textContent = category.name;
    summary.textContent = summarizeCategory(category);

    category.items.forEach((item, itemIndex) => {
      const itemFragment = menuItemTemplate.content.cloneNode(true);
      const card = itemFragment.querySelector(".menu-card");
      const media = itemFragment.querySelector(".menu-card__media");
      const image = itemFragment.querySelector(".menu-card__image");
      const name = itemFragment.querySelector(".menu-card__name");
      const price = itemFragment.querySelector(".menu-card__price");
      const description = itemFragment.querySelector(".menu-card__description");
      const tags = itemFragment.querySelector(".menu-card__tags");
      const cropPath = consumeCropPath(cropIndex, item.name);

      card.style.animationDelay = `${sectionIndex * 70 + itemIndex * 30}ms`;
      name.textContent = item.name;
      price.textContent = currencyFormatter.format(item.price_jpy);
      description.textContent = item.description ?? "";

      if (cropPath) {
        image.src = cropPath;
        image.alt = item.name;
      } else {
        card.classList.add("menu-card--no-image");
        media.replaceChildren();
      }

      if (item.sold_out) {
        tags.appendChild(createTag("Sold out", "tag--muted"));
      }

      if (item.price_inferred) {
        tags.appendChild(createTag("Price inferred", "tag--warning"));
      }

      grid.appendChild(itemFragment);
    });

    menuSectionsEl.appendChild(fragment);
  });
}

function renderMenu(menu, cropManifest) {
  const restaurantName = menu.restaurant.display_name || menu.restaurant.internal_name;
  const totalItems = menu.categories.reduce((sum, category) => sum + category.items.length, 0);
  const cropIndex = buildCropIndex(cropManifest);

  titleEl.textContent = restaurantName;
  subtitleEl.textContent =
    `${menu.restaurant.internal_name} · ${menu.source.image_count} screenshots · ${cropManifest.entries.length} dish crops · first-pass menu website generated from JSON`;
  categoryCountEl.textContent = String(menu.categories.length);
  itemCountEl.textContent = String(totalItems);

  if (menu.extraction.review_required) {
    statusBannerEl.hidden = false;
    statusBannerEl.textContent =
      "This menu is generated from extracted screenshots and still needs human review before publishing.";
  }

  renderNotes(menu.extraction.notes);
  renderCategoryNavigation(menu.categories);
  renderCategories(menu.categories, cropIndex);
}

async function bootstrap() {
  try {
    const [menu, cropManifest] = await Promise.all([loadMenu(), loadCropManifest()]);
    renderMenu(menu, cropManifest);
  } catch (error) {
    titleEl.textContent = "Menu preview unavailable";
    subtitleEl.textContent =
      "Serve this folder from a local web server so the template can load JSON data.";
    statusBannerEl.hidden = false;
    statusBannerEl.textContent = error.message;
    console.error(error);
  }
}

bootstrap();
