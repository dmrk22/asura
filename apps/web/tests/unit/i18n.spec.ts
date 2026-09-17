import * as fs from "node:fs";
import path from "node:path";
import { expect, test } from "@playwright/test";

const messagesDir = path.resolve(__dirname, "../../messages");
const locales = ["en", "te", "hi"];

// biome-ignore lint/suspicious/noExplicitAny: recursively walking arbitrary JSON
function flattenKeys(obj: any, prefix = ""): string[] {
  return Object.entries(obj).flatMap(([key, value]) => {
    const path = prefix ? `${prefix}.${key}` : key;
    if (value !== null && typeof value === "object" && !Array.isArray(value)) {
      return flattenKeys(value, path);
    }
    return [path];
  });
}

test("en.json, te.json and hi.json have identical key sets", () => {
  const keysByLocale = new Map<string, Set<string>>();
  for (const locale of locales) {
    const raw = fs.readFileSync(
      path.join(messagesDir, `${locale}.json`),
      "utf8",
    );
    keysByLocale.set(locale, new Set(flattenKeys(JSON.parse(raw))));
  }

  const [firstLocale, ...rest] = locales;
  const reference = keysByLocale.get(firstLocale) as Set<string>;
  expect(reference.size).toBeGreaterThan(0);

  for (const locale of rest) {
    const keys = keysByLocale.get(locale) as Set<string>;
    const missing = [...reference].filter((k) => !keys.has(k));
    const extra = [...keys].filter((k) => !reference.has(k));
    expect(
      missing,
      `${locale}.json is missing keys present in ${firstLocale}.json`,
    ).toEqual([]);
    expect(
      extra,
      `${locale}.json has keys not present in ${firstLocale}.json`,
    ).toEqual([]);
  }
});
