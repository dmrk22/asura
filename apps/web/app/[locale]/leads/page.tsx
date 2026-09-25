"use client";

import { useLocale, useTranslations } from "next-intl";
import { useEffect, useState } from "react";
import { ScamBadge } from "@/components/ScamBadge";
import { useRouter } from "@/i18n/navigation";
import { api, type Candidate, type SkillNode } from "@/lib/api";
import { loadOnboard } from "@/lib/session";

/** Fetcher-sourced URLs are external input, not a trusted constant — refuse
 * anything that isn't http(s) before it ever reaches an href (e.g. `javascript:`). */
function safeHref(url: string): string | undefined {
  try {
    const u = new URL(url);
    return u.protocol === "https:" || u.protocol === "http:"
      ? u.toString()
      : undefined;
  } catch {
    return undefined;
  }
}

function skillLabel(skills: SkillNode[], id: string, locale: string): string {
  const s = skills.find((s) => s.id === id);
  if (!s) return id;
  if (locale === "te") return s.label_te;
  if (locale === "hi") return s.label_hi;
  return s.label_en;
}

export default function LeadsPage() {
  const t = useTranslations("leads");
  const locale = useLocale();
  const router = useRouter();

  const [skills, setSkills] = useState<SkillNode[]>([]);
  const [matches, setMatches] = useState<Candidate[] | null>(null);
  const [provenanceNote, setProvenanceNote] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [live, setLive] = useState(false);
  const [liveErrors, setLiveErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    const ob = loadOnboard();
    if (!ob) {
      router.replace("/onboard");
      return;
    }
    setMatches(null);
    Promise.all([
      api.taxonomy(),
      api.match({
        held: ob.held,
        districts: ob.district ? [ob.district] : [],
        persona: ob.persona,
        live,
      }),
    ])
      .then(([tx, res]) => {
        setSkills(tx.skills);
        setMatches(res.matches);
        setProvenanceNote(res.provenance_note);
        setLiveErrors(res.live_errors);
      })
      .catch(() => setError(t("loadError")));
  }, [router, t, live]);

  return (
    <main className="mx-auto w-full max-w-[1440px] flex-1 px-6 py-10 sm:px-16">
      <h1 className="font-display text-4xl italic">{t("title")}</h1>
      <div className="mt-3 flex items-center gap-3">
        <label className="flex items-center gap-2 text-graphite text-xs">
          <input
            type="checkbox"
            checked={live}
            onChange={(e) => setLive(e.target.checked)}
            className="accent-signal"
          />
          {t("liveToggle")}
        </label>
      </div>
      {provenanceNote && (
        <p className="mt-2 max-w-prose text-graphite text-xs">
          {provenanceNote}
        </p>
      )}
      {Object.entries(liveErrors).map(([src, msg]) => (
        <p key={src} className="mt-1 font-mono text-[11px] text-amber">
          {src}: {msg}
        </p>
      ))}
      {error && <p className="mt-4 text-signal text-sm">{error}</p>}

      {matches && matches.length === 0 && (
        <p className="mt-8 text-graphite text-sm">
          {t(live ? "emptyLive" : "empty")}
        </p>
      )}

      <ul className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2">
        {matches?.map((c) => (
          <li key={c.id} className="rounded-md border border-graphite/20 p-4">
            <div className="flex items-baseline justify-between gap-3">
              <h2 className="text-base">{c.title}</h2>
              <span className="font-mono text-sm tabular-nums">
                {Math.round(c.match_score * 100)}%
              </span>
            </div>
            <p className="mt-0.5 text-graphite text-xs">
              {c.org} &middot; {c.location} {c.pay ? `· ${c.pay}` : ""}
            </p>

            <details className="mt-3 text-xs">
              <summary className="cursor-pointer text-graphite">
                {t("components")}
              </summary>
              <dl className="mt-2 grid grid-cols-2 gap-1 font-mono tabular-nums">
                {Object.entries(c.components).map(([k, v]) => (
                  <div key={k} className="flex justify-between gap-2">
                    <dt className="text-graphite">{k}</dt>
                    <dd>{typeof v === "number" ? v.toFixed(2) : String(v)}</dd>
                  </div>
                ))}
              </dl>
            </details>

            {c.missing_skills.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-1.5">
                {c.missing_skills.map((s) => (
                  <span
                    key={s}
                    className="rounded-full bg-amber/25 px-2 py-0.5 text-[11px] text-ink"
                  >
                    {skillLabel(skills, s, locale)}
                  </span>
                ))}
              </div>
            )}

            <div className="mt-3">
              <ScamBadge scam={c.scam} />
            </div>

            <div className="mt-3 flex items-center justify-between gap-3 border-graphite/10 border-t pt-3">
              <span className="font-mono text-[10.5px] text-graphite tabular-nums">
                {t("source")}: {c.source} &middot; {t("fetchedAt")}:{" "}
                {new Date(c.fetched_at)
                  .toISOString()
                  .slice(0, 16)
                  .replace("T", " ")}
              </span>
              {(() => {
                const href = safeHref(c.source_url);
                return href ? (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="whitespace-nowrap rounded-full border border-graphite/40 px-3 py-1 text-xs hover:bg-ink hover:text-bone"
                  >
                    {t("viewListing")}
                  </a>
                ) : (
                  <span
                    className="whitespace-nowrap text-[10.5px] text-graphite"
                    title={c.source_url}
                  >
                    {t("noListing")}
                  </span>
                );
              })()}
            </div>
          </li>
        ))}
      </ul>
    </main>
  );
}
