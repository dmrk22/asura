import { expect, test } from "@playwright/test";
import {
  conciseRecap,
  extractName,
  isAffirmative,
} from "@/lib/voice-conversation";

test("extracts a spoken name without keeping the introduction", () => {
  expect(extractName("Hello, my name is mehul kedia.")).toBe("Mehul Kedia");
});

test("recognises a spoken confirmation", () => {
  expect(isAffirmative("Yes, please create my roadmap.")).toBe(true);
  expect(isAffirmative("No, I want to change my goal.")).toBe(false);
});

test("keeps a spoken recap short enough to read aloud", () => {
  expect(conciseRecap("a ".repeat(200)).length).toBeLessThanOrEqual(240);
});
