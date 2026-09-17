import * as fs from "node:fs";
import path from "node:path";
import { expect, test } from "@playwright/test";

const root = path.resolve(__dirname, "../..");

// Banned OKLCH hue band per docs/UI_BRIEF.md: no hue in 250-320 (purple/violet/navy).
const BANNED_HUE_MIN = 250;
const BANNED_HUE_MAX = 320;

function readdirRecursive(dir: string, exts: string[]): string[] {
  const results: string[] = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === "node_modules" || entry.name.startsWith(".")) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results.push(...readdirRecursive(full, exts));
    } else if (exts.some((ext) => entry.name.endsWith(ext))) {
      results.push(full);
    }
  }
  return results;
}

// Real source files that can carry colour values or gradients — excludes
// tests/ itself (this file's own prose mentions "gradient").
const styleAndComponentDirs = ["styles", "app", "components"];
const sourceFiles = styleAndComponentDirs
  .map((d) => path.join(root, d))
  .filter((d) => {
    try {
      return fs.statSync(d).isDirectory();
    } catch {
      return false;
    }
  })
  .flatMap((d) => readdirRecursive(d, [".css", ".tsx", ".ts"]));

test("no OKLCH hue in the banned 250-320 band, parsed from real token values", () => {
  const cssFiles = sourceFiles.filter((f) => f.endsWith(".css"));
  expect(cssFiles.length).toBeGreaterThan(0);

  const hues: { file: string; hue: number }[] = [];
  for (const file of cssFiles) {
    const css = fs.readFileSync(file, "utf8");
    const oklchPattern = /oklch\(\s*[\d.]+\s+[\d.]+\s+([\d.]+)/gi;
    for (const match of css.matchAll(oklchPattern)) {
      hues.push({ file, hue: Number.parseFloat(match[1]) });
    }
  }

  expect(hues.length).toBeGreaterThan(0);
  for (const { file, hue } of hues) {
    expect(
      hue >= BANNED_HUE_MIN && hue <= BANNED_HUE_MAX,
      `${file} defines oklch hue ${hue}, inside the banned ${BANNED_HUE_MIN}-${BANNED_HUE_MAX} band`,
    ).toBe(false);
  }
});

test("no gradient anywhere in CSS or components", () => {
  expect(sourceFiles.length).toBeGreaterThan(0);
  for (const file of sourceFiles) {
    const content = fs.readFileSync(file, "utf8");
    expect(
      /gradient/i.test(content),
      `${file} contains the word "gradient"`,
    ).toBe(false);
  }
});
