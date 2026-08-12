#!/usr/bin/env node

import { cp, mkdir, readdir, rm, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const defaultProjectRoot = path.resolve(scriptDirectory, "..");

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

      const targetDirectory = path.join(distDirectory, "restaurants", entry.name);
      await mkdir(targetDirectory, { recursive: true });
      if (hasMenuImage) {
        await cp(menuImage, path.join(targetDirectory, "menu_en.png"));
      }
      if (hasMenuSite) {
        await cp(menuSite, path.join(targetDirectory, "menu_site"), { recursive: true });
      }
      publishedRestaurants.push(entry.name);
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
