#!/usr/bin/env node

import { cp, mkdir, readFile, readdir, rm, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const defaultProjectRoot = path.resolve(scriptDirectory, "..");
const publicSlugPattern = /^[a-z0-9]+(?:-[a-z0-9]+)*-[a-z0-9]{6}$/;
const uuidV7Pattern = /^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

async function isFile(filePath) {
  try {
    return (await stat(filePath)).isFile();
  } catch {
    return false;
  }
}

async function isDirectory(directoryPath) {
  try {
    return (await stat(directoryPath)).isDirectory();
  } catch {
    return false;
  }
}

async function loadRestaurantMetadata(metadataPath) {
  let metadata;
  try {
    metadata = JSON.parse(await readFile(metadataPath, "utf8"));
  } catch (error) {
    throw new Error(`Missing or invalid restaurant metadata: ${metadataPath}`, { cause: error });
  }

  if (!uuidV7Pattern.test(metadata.id || "")) {
    throw new Error(`Restaurant metadata requires a valid UUIDv7 id: ${metadataPath}`);
  }
  if (!publicSlugPattern.test(metadata.public_slug || "")) {
    throw new Error(
      `Restaurant metadata requires a public_slug ending in a six-character suffix: ${metadataPath}`
    );
  }
  return metadata;
}

export async function buildPublicSite(projectRoot = defaultProjectRoot) {
  const resolvedRoot = path.resolve(projectRoot);
  const websiteDirectory = path.join(resolvedRoot, "website");
  const restaurantOutputDirectory = path.join(resolvedRoot, "output");
  const distDirectory = path.join(resolvedRoot, "deploy", "dist");
  const websiteFiles = ["index.html", "styles.css"];

  const missingFiles = [];
  for (const filename of websiteFiles) {
    if (!(await isFile(path.join(websiteDirectory, filename)))) {
      missingFiles.push(path.join(websiteDirectory, filename));
    }
  }
  if (missingFiles.length > 0) {
    throw new Error(`Missing website source files: ${missingFiles.join(", ")}`);
  }

  await rm(distDirectory, { recursive: true, force: true });
  await mkdir(distDirectory, { recursive: true });

  for (const filename of websiteFiles) {
    await cp(path.join(websiteDirectory, filename), path.join(distDirectory, filename));
  }

  const publishedRestaurants = [];
  const publishedIds = new Set();
  const publishedSlugs = new Set();
  if (await isDirectory(restaurantOutputDirectory)) {
    const entries = await readdir(restaurantOutputDirectory, { withFileTypes: true });
    const restaurantDirectories = entries
      .filter((entry) => entry.isDirectory())
      .sort((left, right) => left.name.localeCompare(right.name));

    for (const entry of restaurantDirectories) {
      const restaurantDirectory = path.join(restaurantOutputDirectory, entry.name);
      const menuImage = path.join(restaurantDirectory, "menu_en.png");
      const menuSite = path.join(restaurantDirectory, "menu_site");
      const hasMenuImage = await isFile(menuImage);
      const hasMenuSite = await isDirectory(menuSite);
      if (!hasMenuImage && !hasMenuSite) {
        continue;
      }

      const metadata = await loadRestaurantMetadata(path.join(restaurantDirectory, "restaurant.json"));
      if (publishedIds.has(metadata.id)) {
        throw new Error(`Duplicate restaurant id: ${metadata.id}`);
      }
      if (publishedSlugs.has(metadata.public_slug)) {
        throw new Error(`Duplicate public restaurant slug: ${metadata.public_slug}`);
      }
      publishedIds.add(metadata.id);
      publishedSlugs.add(metadata.public_slug);

      const targetDirectory = path.join(distDirectory, "restaurants", metadata.public_slug);
      await mkdir(targetDirectory, { recursive: true });
      if (hasMenuSite) {
        await cp(menuSite, targetDirectory, { recursive: true });
      }
      if (hasMenuImage) {
        await cp(menuImage, path.join(targetDirectory, "menu_en.png"));
      }
      publishedRestaurants.push(metadata.public_slug);
    }
  }

  return publishedRestaurants;
}

function projectRootFromArguments() {
  const optionIndex = process.argv.indexOf("--project-root");
  if (optionIndex === -1) {
    return defaultProjectRoot;
  }
  const value = process.argv[optionIndex + 1];
  if (!value) {
    throw new Error("--project-root requires a directory path");
  }
  return value;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const restaurants = await buildPublicSite(projectRootFromArguments());
  const names = restaurants.length > 0 ? restaurants.join(", ") : "none";
  console.log(`Built deploy/dist/ with public restaurant assets: ${names}`);
}
