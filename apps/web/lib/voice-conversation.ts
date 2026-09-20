const YES_PATTERN =
  /\b(yes|yeah|yep|sure|please|create|go ahead|proceed)\b|అవును|సృష్టించు|हाँ|हां|बनाएं/u;

export function extractName(transcript: string): string | null {
  const direct = transcript.match(
    /(?:my name is|i am|i'm|this is)\s+([A-Za-z][A-Za-z '-]{0,48})/i,
  )?.[1];
  const candidate = (direct ?? transcript.split(/[,.!?]/)[0] ?? "")
    .replace(/^(?:hello|hi|hey)\s+/i, "")
    .trim();
  if (!candidate || candidate.split(/\s+/).length > 4) return null;
  return candidate
    .split(/\s+/)
    .map(
      (part) => `${part[0]?.toUpperCase() ?? ""}${part.slice(1).toLowerCase()}`,
    )
    .join(" ");
}

export function isAffirmative(transcript: string): boolean {
  return YES_PATTERN.test(transcript);
}

export function conciseRecap(transcript: string): string {
  const clean = transcript.replace(/\s+/g, " ").trim();
  return clean.length > 240 ? `${clean.slice(0, 237).trimEnd()}…` : clean;
}
