"use client";

import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";
import { api, type EvidenceResponse } from "@/lib/api";

export default function EvidencePage() {
  const t = useTranslations("evidence");
  const [data, setData] = useState<EvidenceResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .evidence()
      .then(setData)
      .catch(() => setError(t("loadError")));
  }, [t]);

  return (
    <main className="mx-auto w-full max-w-[1440px] flex-1 px-6 py-10 sm:px-16">
      <h1 className="font-display text-4xl italic">{t("title")}</h1>
      {error && <p className="mt-4 text-signal text-sm">{error}</p>}

      {data && (
        <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2">
          <section className="rounded-md border border-graphite/20 p-4">
            <h2 className="mb-2 font-mono text-graphite text-xs uppercase tracking-wide">
              {t("importGraph")}
            </h2>
            <p className="font-mono text-sm">{data.shared_engine.package}</p>
            <p className="mt-1 text-graphite text-xs">
              {data.shared_engine.note}
            </p>
          </section>

          <section className="rounded-md border border-graphite/20 p-4">
            <h2 className="mb-2 font-mono text-graphite text-xs uppercase tracking-wide">
              {t("callsByPersona")}
            </h2>
            {Object.entries(data.shared_engine.calls_by_persona).map(
              ([persona, calls]) => (
                <div key={persona} className="mb-2">
                  <p className="text-sm">{persona}</p>
                  <dl className="grid grid-cols-2 gap-1 font-mono text-xs tabular-nums">
                    {Object.entries(calls).map(([fn, n]) => (
                      <div key={fn} className="flex justify-between gap-2">
                        <dt className="text-graphite">{fn}</dt>
                        <dd>{n}</dd>
                      </div>
                    ))}
                  </dl>
                </div>
              ),
            )}
          </section>

          <section className="rounded-md border border-graphite/20 p-4">
            <h2 className="mb-2 font-mono text-graphite text-xs uppercase tracking-wide">
              {t("taxonomy")}
            </h2>
            <dl className="grid grid-cols-2 gap-1 font-mono text-sm tabular-nums">
              <div className="flex justify-between gap-2">
                <dt className="text-graphite">skills</dt>
                <dd>{data.taxonomy.skills}</dd>
              </div>
              <div className="flex justify-between gap-2">
                <dt className="text-graphite">roles</dt>
                <dd>{data.taxonomy.roles}</dd>
              </div>
            </dl>
          </section>

          <section className="rounded-md border border-graphite/20 p-4">
            <h2 className="mb-2 font-mono text-graphite text-xs uppercase tracking-wide">
              {t("leads")}
            </h2>
            <dl className="grid grid-cols-2 gap-1 font-mono text-sm tabular-nums">
              <div className="flex justify-between gap-2">
                <dt className="text-graphite">count</dt>
                <dd>{data.leads.count}</dd>
              </div>
              <div className="flex justify-between gap-2">
                <dt className="text-graphite">live</dt>
                <dd>{String(data.leads.live)}</dd>
              </div>
            </dl>
          </section>
        </div>
      )}
    </main>
  );
}
