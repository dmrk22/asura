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
    const state = raw ? (JSON.parse(raw) as OnboardState) : null;
    // Discard the retired demo profiles from existing browser sessions.
    if (
      state &&
      state.personaId !== "new-profile" &&
      state.personaId !== "voice"
    ) {
      sessionStorage.removeItem(KEY);
      return null;
    }
    return state;
  } catch {
    return null;
  }
}
