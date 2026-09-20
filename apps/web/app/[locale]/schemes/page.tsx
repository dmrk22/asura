"use client";

import { useTranslations } from "next-intl";
import { useState } from "react";
import { api, type EligibilityResponse, type Scheme } from "@/lib/api";
import { loadOnboard } from "@/lib/session";

function safeHref(url: string): string | undefined {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "https:" || parsed.protocol === "http:"
      ? parsed.toString()
      : undefined;
  } catch {
    return undefined;
  }
}

export default function SchemesPage() {
  const t = useTranslations("schemes");
  const [query, setQuery] = useState("income");
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [eligibility, setEligibility] = useState<
    Record<string, EligibilityResponse>
  >({});
  const [error, setError] = useState<string | null>(null);

  async function search() {
    try {
      setError(null);
      const result = await api.schemes(query);
      setSchemes(result.schemes);
      if (result.error) setError(result.error);
    } catch {
      setError(t("error"));
    }
  }
  async function check(scheme: Scheme) {
    try {
      const onboard = loadOnboard();
      const result = await api.eligibility({
        source_url: scheme.source_url,
        fetched_at: scheme.fetched_at,
        persona: onboard?.persona,
      });
      setEligibility((existing) => ({ ...existing, [scheme.id]: result }));
    } catch {
      setError(t("error"));
    }
  }

  return (
    <main className="mx-auto w-full max-w-[1100px] flex-1 px-6 py-10 sm:px-16">
      <h1 className="font-display text-4xl italic">{t("title")}</h1>
      <p className="mt-2 text-graphite">{t("subtitle")}</p>
      <div className="mt-6 flex gap-2">
        <input
          aria-label={t("search")}
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          className="w-full rounded-md border border-graphite/30 bg-transparent px-3 py-2"
        />
        <button
          type="button"
          onClick={search}
          className="rounded-md bg-signal px-4 text-bone"
        >
          {t("searchButton")}
        </button>
      </div>
      {error && <p className="mt-4 text-signal text-sm">{error}</p>}
      {schemes.length === 0 && !error ? (
        <p className="mt-8 text-graphite">{t("empty")}</p>
      ) : null}
      <ul className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2">
        {schemes.map((scheme) => {
          const verdict = eligibility[scheme.id];
          const href = safeHref(scheme.source_url);
          return (
            <li
              key={scheme.id}
              className="rounded-md border border-graphite/20 p-4"
            >
              <h2>{scheme.name}</h2>
              <p className="mt-2 text-sm text-graphite">{scheme.description}</p>
              <p className="mt-3 text-xs text-graphite">{scheme.ministry}</p>
              <p className="mt-3 font-mono text-[10px] text-graphite">
                {t("source")}: {scheme.source} · {t("fetchedAt")}:{" "}
                {new Date(scheme.fetched_at).toISOString().slice(0, 16)}
              </p>
              {href ? (
                <a
                  className="mt-2 inline-block text-sm underline"
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {scheme.source_url}
                </a>
              ) : (
                <p className="mt-2 font-mono text-xs text-graphite">
                  {scheme.source}
                </p>
              )}
              <button
                type="button"
                onClick={() => check(scheme)}
                className="mt-4 block rounded-full border border-sage px-3 py-1 text-xs text-sage"
              >
                {t("eligibility")}
              </button>
              {verdict && (
                <p className="mt-3 text-sm text-amber">
                  {verdict.needs_rule_extraction ? t("unknown") : verdict.value}
                </p>
              )}
            </li>
          );
        })}
      </ul>
    </main>
  );
}
