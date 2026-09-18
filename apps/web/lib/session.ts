/** sessionStorage-backed onboarding state — one key, one shape, no store lib needed. */
import type { Persona } from "./api";

export interface OnboardState {
  personaId: string;
  persona: Persona;
  goal: string;
  held: Record<string, number>;
  district: string | null;
  language: string;
  constraints: string;
}

const KEY = "daari.onboard";

export function saveOnboard(state: OnboardState) {
  try {
    sessionStorage.setItem(KEY, JSON.stringify(state));
  } catch {
    // private mode / blocked storage — the session just won't persist across reloads
  }
}

export function loadOnboard(): OnboardState | null {
  try {
    const raw = sessionStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as OnboardState) : null;
  } catch {
    return null;
  }
}
