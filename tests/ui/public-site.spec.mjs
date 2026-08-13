import { expect, test } from "@playwright/test";

function monitorBrowserErrors(page) {
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error") {
      errors.push(message.text());
    }
  });
  return errors;
}

async function expectHealthyPage(page, request, path) {
  const browserErrors = monitorBrowserErrors(page);
  const response = await page.goto(path, { waitUntil: "domcontentloaded" });

  expect(response, `${path} did not return a document response`).not.toBeNull();
  expect(response.ok(), `${path} returned HTTP ${response.status()}`).toBeTruthy();

  await expect(page.locator("body")).toBeVisible();

  const internalUrls = await page.locator("a[href], img[src], link[href], script[src]").evaluateAll(
    (elements) =>
      [...new Set(
        elements
          .map((element) => element.getAttribute("href") || element.getAttribute("src"))
          .filter(Boolean)
          .map((value) => new URL(value, window.location.href))
          .filter((url) => url.origin === window.location.origin && !url.hash)
          .map((url) => url.href)
      )]
  );

  for (const url of internalUrls) {
    const assetResponse = await request.get(url);
    expect(assetResponse.ok(), `${url} returned HTTP ${assetResponse.status()}`).toBeTruthy();
  }

  const brokenImages = await page.locator("img").evaluateAll((images) =>
    images
      .filter((image) => !image.complete || image.naturalWidth === 0)
      .map((image) => image.currentSrc || image.src)
  );
  expect(brokenImages, `Broken images on ${path}`).toEqual([]);

  const layout = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
  }));
  expect(
    layout.scrollWidth,
    `${path} has horizontal overflow: ${layout.scrollWidth}px > ${layout.clientWidth}px`
  ).toBeLessThanOrEqual(layout.clientWidth + 1);

  expect(browserErrors, `Browser errors on ${path}`).toEqual([]);
}

test("landing page has no broken routes, assets, or horizontal overflow", async ({ page, request }) => {
  await expectHealthyPage(page, request, "/");
  await expect(page.locator("main#top")).toBeVisible();
  await expect(page.locator("#benefits")).toBeVisible();
  await expect(page.locator(".benefit-card")).toHaveCount(3);
  await expect(page.locator(".hero .actions")).toHaveCount(0);
  await expect(page.locator(".hero-preview")).toHaveCount(0);
  await expect(page.locator("img[src='/restaurants/honoya-7k3m2q/menu_en.png']")).toHaveCount(1);

  const sectionOrder = await page.evaluate(() =>
    Array.from(document.querySelectorAll("main#top > section[id]"), (section) => section.id)
  );
  expect(sectionOrder).toEqual(["service", "sample", "benefits", "flow", "pricing"]);

  const navigationOrder = await page.evaluate(() =>
    Array.from(document.querySelectorAll(".site-nav a"), (link) => link.hash.slice(1))
  );
  expect(navigationOrder).toEqual(sectionOrder);
});

test("restaurant menu loads and language switching preserves layout", async ({ page, request }) => {
  await expectHealthyPage(page, request, "/restaurants/honoya-7k3m2q/");
  await expect(page.locator(".menu-card").first()).toBeVisible();
  await page.evaluate(() => document.fonts.ready);

  const before = await page.evaluate(() => ({
    height: document.documentElement.scrollHeight,
    scrollY: window.scrollY,
  }));

  await page.locator("#lang-ja").click();
  await expect(page.locator("#lang-ja")).toHaveClass(/is-active/);

  const after = await page.evaluate(() => ({
    height: document.documentElement.scrollHeight,
    scrollY: window.scrollY,
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  }));

  expect(after.height).toBe(before.height);
  expect(after.scrollY).toBe(before.scrollY);
  expect(after.overflow).toBeLessThanOrEqual(1);
});
