import { defineConfig } from "@playwright/test";

// Runs the two P1 unit checks (tokens.spec.ts, i18n.spec.ts) as plain
// assertions — no `page` fixture requested, so no browser is launched.
export default defineConfig({
  testDir: "./tests/unit",
  fullyParallel: true,
  reporter: "list",
});
