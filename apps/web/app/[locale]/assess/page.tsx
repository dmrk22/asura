"use client";

import { useTranslations } from "next-intl";
import { useCallback, useEffect, useState } from "react";
import { type AssessItem, type AssessState, api } from "@/lib/api";
import { loadOnboard } from "@/lib/session";

export default function AssessPage() {
  const t = useTranslations("assess");
  const [state, setState] = useState<AssessState | null>(null);
  const [item, setItem] = useState<AssessItem | null>(null);
  const [answer, setAnswer] = useState("");
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (nextState?: AssessState) => {
    const onboard = loadOnboard();
    const response = await api.assessNext({
      state: nextState,
      persona: onboard?.persona,
    });
    setState(response.state);
    setItem(response.item);
    setDone(response.done);
  }, []);

  useEffect(() => {
    load().catch(() => setError(t("error")));
  }, [load, t]);

  async function submit() {
    if (!state || !item || !answer.trim()) return;
    setError(null);
    try {
      const onboard = loadOnboard();
      const response = await api.assessAnswer({
        state,
        item_id: item.id,
        given_answer: answer,
        persona: onboard?.persona,
      });
      setAnswer("");
      setState(response.state);
      if (response.done) setDone(true);
      else await load(response.state);
    } catch {
      setError(t("error"));
    }
  }

  return (
    <main className="mx-auto w-full max-w-2xl flex-1 px-6 py-10 sm:px-16">
      <h1 className="font-display text-4xl italic">{t("title")}</h1>
      <p className="mt-2 text-graphite">{t("subtitle")}</p>
      {state && (
        <p className="mt-6 font-mono text-sm tabular-nums">
          {t("ability")}: {state.theta.toFixed(2)} · SE {state.se.toFixed(2)} ·{" "}
          {state.answered.length}/6
        </p>
      )}
      {error && <p className="mt-4 text-signal text-sm">{error}</p>}
      {done ? (
        <section className="mt-8 rounded-md border border-sage/50 p-5">
          <h2 className="font-display text-2xl italic">{t("complete")}</h2>
        </section>
      ) : item ? (
        <section className="mt-8 rounded-md border border-graphite/20 p-5">
          <p className="text-lg">{item.text}</p>
          <p className="mt-2 font-mono text-[11px] text-graphite">
            {item.source}
          </p>
          <label className="mt-6 flex flex-col gap-1.5 text-sm">
            <span>{t("answer")}</span>
            <input
              value={answer}
              onChange={(event) => setAnswer(event.target.value)}
              onKeyDown={(event) => event.key === "Enter" && submit()}
              className="rounded-md border border-graphite/30 bg-transparent px-3 py-2"
            />
          </label>
          <button
            type="button"
            onClick={submit}
            className="mt-4 rounded-md bg-signal px-4 py-2 text-bone"
          >
            {t("submit")}
          </button>
        </section>
      ) : null}
    </main>
  );
}
