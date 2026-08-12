async function loadMenu() {
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
