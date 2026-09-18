import type { ScamInfo } from "@/lib/api";

/** Scam Shield badge (safety.md guard 3): "a badge without reasons is a
 * bug", so this renders nothing rather than a bare number when `scam` is
 * absent or clear — every reason shown carries the quoted substring that
 * triggered it, straight from `daari_core.scam`. */
export function ScamBadge({ scam }: { scam?: ScamInfo }) {
  if (!scam || scam.band === "clear") return null;

  const cls =
    scam.band === "red"
      ? "border-signal/40 bg-signal/10 text-signal"
      : "border-amber/50 bg-amber/15 text-ink";

  return (
    <div className={`rounded-md border px-3 py-2 text-xs ${cls}`}>
      <p className="font-medium">
        {scam.band === "red" ? "Scam risk" : "Check this"}{" "}
        <span className="font-mono tabular-nums">{scam.score.toFixed(2)}</span>
      </p>
      <ul className="mt-1 list-inside list-disc space-y-0.5">
        {scam.reasons.map((r) => (
          <li key={r.rule}>
            {r.rule}: &ldquo;{r.quote}&rdquo;
          </li>
        ))}
      </ul>
    </div>
  );
}
