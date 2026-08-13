from __future__ import annotations

import json
import re
from pathlib import Path

from .models import TranslationBlock


PRICE_ONLY_RE = re.compile(r"^\s*[¥]?\s*[\d,]+(?:\.\d+)?\s*(?:円|yen)?\s*$", re.IGNORECASE)
TRAILING_PRICE_RE = re.compile(
    r"^(?P<name>.*?)(?:\s*[,/]\s*|\s+)(?P<price>[¥]?\s*[\d,]+(?:\.\d+)?\s*(?:円|yen))\s*$",
    re.IGNORECASE,
)


def build_menu_site(
    restaurant_slug: str,
    translated_blocks: list[TranslationBlock],
    output_dir: Path,
) -> Path:
    site_dir = output_dir / "menu_site"
    site_dir.mkdir(parents=True, exist_ok=True)

    restaurant_metadata = _load_restaurant_metadata(output_dir / "restaurant.json")
    menu_data = _build_menu_data(restaurant_slug, translated_blocks, restaurant_metadata)
    _write_menu_data(site_dir / "menu_data.json", menu_data)
    restaurant_name = str(menu_data["restaurant"]["name_en"])
    _write_index_html(site_dir / "index.html", restaurant_name)
    _write_styles(site_dir / "styles.css")
    _write_script(site_dir / "script.js")

    return site_dir


def _build_menu_data(
    restaurant_slug: str,
    translated_blocks: list[TranslationBlock],
    restaurant_metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    metadata = restaurant_metadata or {}
    restaurant_name = str(metadata.get("name_en") or _humanize_slug(restaurant_slug))
    public_slug = str(metadata.get("public_slug") or restaurant_slug)
    sections: list[dict[str, object]] = []
    current_section = _new_section("Menu", "メニュー")
    sections.append(current_section)
    pending_item: dict[str, object] | None = None

    for index, block in enumerate(translated_blocks):
        text_en = block.translation.strip()
        text_ja = block.original.strip()
        if not text_en:
            continue

        if block.type == "label":
            continue

        if block.type == "section_title" and _looks_like_section_heading(block, translated_blocks, index):
            current_section = _new_section(
                _clean_section_title(text_en),
                _clean_section_title(text_ja),
            )
            sections.append(current_section)
            pending_item = None
            continue

        if block.type == "price":
            if pending_item is not None and not pending_item.get("price"):
                pending_item["price"] = _normalize_price(text_en)
                pending_item = None
            continue

        item_name_en, inline_price = _split_inline_price(text_en)
        item_name_ja, _ = _split_inline_price(text_ja)
        if block.type == "description" and pending_item is not None and not pending_item.get("description"):
            pending_item["description_en"] = item_name_en
            pending_item["description_ja"] = item_name_ja
            if inline_price and not pending_item.get("price"):
                pending_item["price"] = inline_price
                pending_item = None
            continue

        item = {
            "name_en": item_name_en,
            "name_ja": item_name_ja,
            "price": inline_price,
            "description_en": "",
            "description_ja": "",
        }
        current_section["items"].append(item)
        pending_item = item

    filtered_sections = [section for section in sections if section["items"]]
    if not filtered_sections:
        filtered_sections = sections[:1]

    restaurant = {
        "slug": public_slug,
        "name_en": restaurant_name,
        "name_ja": str(metadata.get("name_ja") or restaurant_name),
        "tagline_en": "English Menu",
        "tagline_ja": "英語メニュー",
    }
    if metadata.get("id"):
        restaurant["id"] = str(metadata["id"])

    return {
        "restaurant": restaurant,
        "sections": filtered_sections,
    }


def _load_restaurant_metadata(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Restaurant metadata must be a JSON object: {path}")
    return payload


def _new_section(title_en: str, title_ja: str) -> dict[str, object]:
    return {
        "id": _slugify(title_en),
        "title_en": title_en,
        "title_ja": title_ja,
        "items": [],
    }


def _clean_section_title(text: str) -> str:
    cleaned = text.strip().strip("[]").strip("【】")
    return cleaned or "Menu"


def _looks_like_section_heading(
    block: TranslationBlock,
    translated_blocks: list[TranslationBlock],
    index: int,
) -> bool:
    text = block.translation.strip()
    original = block.original.strip()

    if original.startswith("【") or text.startswith("["):
        return True

    normalized = text.lower().strip("[]")
    if normalized in {"menu", "whisky", "sours", "cocktails", "soft drinks", "bottled beer"}:
        return True

    next_block = translated_blocks[index + 1] if index + 1 < len(translated_blocks) else None
    if next_block is not None and next_block.type == "price":
        return False

    return len(text) >= 14


def _split_inline_price(text: str) -> tuple[str, str]:
    match = TRAILING_PRICE_RE.match(text)
    if not match:
        return text, ""

    name = match.group("name").strip(" ,/")
    price = _normalize_price(match.group("price"))
    return name or text, price


def _normalize_price(text: str) -> str:
    cleaned = text.strip()
    cleaned = cleaned.replace(" ", "")
    if PRICE_ONLY_RE.match(cleaned):
        if "円" in cleaned or "¥" in cleaned:
            return cleaned
        return f"¥{cleaned}"
    return cleaned


def _humanize_slug(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.replace("-", "_").split("_"))


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "menu"


def _write_menu_data(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_index_html(path: Path, restaurant_name: str) -> None:
    html = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{restaurant_name} Menu</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;500;700&display=swap"
      rel="stylesheet"
    />
    <link rel="stylesheet" href="styles.css" />
  </head>
  <body>
    <div class="app-shell">
      <header class="topbar">
        <div class="brand">
          <h1 id="restaurant-name">Loading menu...</h1>
        </div>
        <div class="language-switch" aria-label="Language switch">
          <button id="lang-en" class="language-option is-active" type="button">EN</button>
          <button id="lang-ja" class="language-option" type="button">JP</button>
        </div>
      </header>
      <main class="menu-layout">
        <aside class="sidebar">
          <div id="section-nav" class="section-nav"></div>
        </aside>
        <section id="menu-sections" class="content"></section>
      </main>
    </div>
    <script src="script.js"></script>
  </body>
</html>
"""
    path.write_text(html, encoding="utf-8")


def _write_styles(path: Path) -> None:
    css = """* {
  box-sizing: border-box;
}

:root {
  --bg: #f6f1ea;
  --panel: #fffdf9;
  --sidebar: #f4ede4;
  --ink: #261a14;
  --muted: #6d5a50;
  --accent: #cb6d21;
  --accent-soft: #f7d8bf;
  --line: #eadbcc;
  --shadow: 0 18px 48px rgba(65, 44, 28, 0.08);
  font-family: "Outfit", "Noto Sans JP", sans-serif;
  color: var(--ink);
  background: radial-gradient(circle at top, #fffaf3 0%, var(--bg) 55%, #efe4d8 100%);
}

body {
  margin: 0;
  min-height: 100vh;
}

.app-shell {
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
}

.topbar h1 {
  margin: 0;
  font-size: clamp(1.8rem, 4vw, 3rem);
  line-height: 1;
}

.menu-layout {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  gap: 20px;
  align-items: start;
}

.sidebar {
  position: sticky;
  top: 24px;
  background: color-mix(in srgb, var(--sidebar) 92%, white);
  border: 1px solid var(--line);
  border-radius: 28px;
  padding: 18px 14px;
  box-shadow: var(--shadow);
  max-height: calc(100vh - 48px);
  overflow: auto;
}

.section-nav {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.nav-link {
  display: block;
  padding: 12px 12px 12px 16px;
  border-left: 4px solid transparent;
  border-radius: 14px;
  color: var(--ink);
  text-decoration: none;
  font-weight: 600;
  line-height: 1.2;
  background: transparent;
}

.nav-link:hover,
.nav-link.is-active {
  border-left-color: var(--accent);
  background: var(--accent-soft);
}

.content {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.menu-section {
  background: color-mix(in srgb, var(--panel) 94%, white);
  border: 1px solid var(--line);
  border-radius: 30px;
  padding: 24px;
  box-shadow: var(--shadow);
}

.menu-section-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.menu-section-header h2 {
  margin: 0;
  font-size: 1.45rem;
}

.item-count {
  color: var(--muted);
  font-size: 0.92rem;
}

.menu-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.menu-card {
  background: white;
  border: 1px solid #efe4d7;
  border-radius: 22px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 140px;
}

.menu-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.menu-card h3 {
  margin: 0;
  font-size: 1.1rem;
  line-height: 1.25;
}

.price {
  white-space: nowrap;
  color: var(--accent);
  font-weight: 700;
  font-size: 1rem;
}

.description {
  margin: 0;
  color: var(--muted);
  line-height: 1.5;
  font-size: 0.94rem;
}

.lang-frame {
  display: grid;
  width: 100%;
  min-width: 0;
}

.lang-text {
  display: block;
  grid-area: 1 / 1;
  min-width: 0;
}

.lang-text.is-hidden {
  visibility: hidden;
  pointer-events: none;
}

.language-switch {
  position: fixed;
  left: 18px;
  bottom: 18px;
  z-index: 30;
  border-radius: 999px;
  background: white;
  border: 1px solid var(--line);
  box-shadow: 0 16px 34px rgba(91, 45, 8, 0.22);
  display: inline-flex;
  align-items: center;
  padding: 4px;
}

.language-option {
  border: none;
  background: transparent;
  color: var(--muted);
  font: inherit;
  font-weight: 700;
  padding: 10px 14px;
  border-radius: 999px;
  min-width: 96px;
}

.language-option.is-active {
  background: var(--accent);
  color: white;
}

.language-option:not(.is-active) {
  cursor: pointer;
}

@media (max-width: 900px) {
  .app-shell {
    padding: 12px;
  }

  .menu-layout {
    grid-template-columns: 96px minmax(0, 1fr);
    gap: 12px;
  }

  .sidebar {
    top: 12px;
    border-radius: 20px;
    padding: 12px 8px;
  }

  .nav-link {
    padding: 10px 8px 10px 12px;
    font-size: 0.95rem;
    word-break: break-word;
  }

  .menu-section {
    border-radius: 22px;
    padding: 18px;
  }

  .menu-cards {
    grid-template-columns: 1fr;
  }

  .menu-card {
    min-height: 0;
  }

  .menu-card-header {
    flex-direction: column;
    gap: 8px;
  }

  .language-switch {
    left: 12px;
    bottom: 12px;
  }

  .language-option {
    min-width: 0;
    padding: 10px 12px;
  }
}
"""
    path.write_text(css, encoding="utf-8")


def _write_script(path: Path) -> None:
    script = """async function loadMenu() {
  const response = await fetch("menu_data.json");
  const data = await response.json();

  const nav = document.getElementById("section-nav");
  const content = document.getElementById("menu-sections");
  const englishButton = document.getElementById("lang-en");
  const japaneseButton = document.getElementById("lang-ja");
  let currentLanguage = "en";
  const visibility = new Map();
  const setActiveLink = (targetId) => {
    const normalized = targetId ? `#${targetId.replace(/^#/, "")}` : "";
    document.querySelectorAll(".nav-link").forEach((link) => {
      link.classList.toggle("is-active", link.getAttribute("href") === normalized);
    });
  };
  const setLanguage = (language) => {
    currentLanguage = language;
    document.documentElement.lang = language === "ja" ? "ja" : "en";
    document.querySelectorAll("[data-lang-frame]").forEach((frame) => {
      const en = frame.querySelector(".lang-en");
      const ja = frame.querySelector(".lang-ja");
      if (en) {
        en.classList.toggle("is-hidden", language !== "en");
      }
      if (ja) {
        ja.classList.toggle("is-hidden", language !== "ja");
      }
    });
    englishButton.classList.toggle("is-active", language === "en");
    japaneseButton.classList.toggle("is-active", language === "ja");
  };
  document.getElementById("restaurant-name").innerHTML = `
    <span class="lang-frame" data-lang-frame>
      <span class="lang-text lang-en">${data.restaurant.name_en}</span>
      <span class="lang-text lang-ja is-hidden">${data.restaurant.name_ja}</span>
    </span>
  `;
  data.sections.forEach((section, index) => {
    const navLink = document.createElement("a");
    navLink.href = `#${section.id}`;
    navLink.className = "nav-link";
    navLink.innerHTML = `
      <span class="lang-frame" data-lang-frame>
        <span class="lang-text lang-en">${section.title_en}</span>
        <span class="lang-text lang-ja is-hidden">${section.title_ja}</span>
      </span>
    `;
    if (index === 0) {
      navLink.classList.add("is-active");
    }
    navLink.addEventListener("click", () => {
      setActiveLink(section.id);
    });
    nav.appendChild(navLink);

    const wrapper = document.createElement("section");
    wrapper.className = "menu-section";
    wrapper.id = section.id;

    const header = document.createElement("div");
    header.className = "menu-section-header";
    header.innerHTML = `
      <h2>
        <span class="lang-frame" data-lang-frame>
          <span class="lang-text lang-en">${section.title_en}</span>
          <span class="lang-text lang-ja is-hidden">${section.title_ja}</span>
        </span>
      </h2>
      <span class="item-count">${section.items.length} items</span>
    `;
    wrapper.appendChild(header);

    const cards = document.createElement("div");
    cards.className = "menu-cards";

    section.items.forEach((item) => {
      const card = document.createElement("article");
      card.className = "menu-card";
      card.innerHTML = `
        <div class="menu-card-header">
          <h3>
            <span class="lang-frame" data-lang-frame>
              <span class="lang-text lang-en">${item.name_en}</span>
              <span class="lang-text lang-ja is-hidden">${item.name_ja}</span>
            </span>
          </h3>
          <span class="price">${item.price || ""}</span>
        </div>
        ${(item.description_en || item.description_ja) ? `<p class="description"><span class="lang-frame" data-lang-frame><span class="lang-text lang-en">${item.description_en || ""}</span><span class="lang-text lang-ja is-hidden">${item.description_ja || ""}</span></span></p>` : ""}
      `;
      cards.appendChild(card);
    });

    wrapper.appendChild(cards);
    content.appendChild(wrapper);
  });

  const navLinks = Array.from(document.querySelectorAll(".nav-link"));
  const sections = Array.from(document.querySelectorAll(".menu-section"));
  const updateActiveFromVisibility = () => {
    let bestId = "";
    let bestRatio = -1;

    sections.forEach((section) => {
      const ratio = visibility.get(section.id) || 0;
      if (ratio > bestRatio) {
        bestRatio = ratio;
        bestId = section.id;
      }
    });

    if (bestId) {
      setActiveLink(bestId);
    }
  };

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        visibility.set(entry.target.id, entry.isIntersecting ? entry.intersectionRatio : 0);
      });
      updateActiveFromVisibility();
    },
    { rootMargin: "-12% 0px -55% 0px", threshold: [0, 0.15, 0.35, 0.55, 0.75, 1] }
  );

  sections.forEach((section, index) => {
    visibility.set(section.id, index === 0 ? 1 : 0);
    observer.observe(section);
  });
  setLanguage(currentLanguage);
  if (window.location.hash) {
    setActiveLink(window.location.hash);
  }
  window.addEventListener("hashchange", () => {
    setActiveLink(window.location.hash);
  });
  englishButton.addEventListener("click", () => setLanguage("en"));
  japaneseButton.addEventListener("click", () => setLanguage("ja"));
}

loadMenu().catch((error) => {
  document.getElementById("restaurant-name").textContent = "Menu load failed";
  document.getElementById("lang-en").textContent = "Error";
  document.getElementById("lang-ja").remove();
  console.error(error);
});
"""
    path.write_text(script, encoding="utf-8")
