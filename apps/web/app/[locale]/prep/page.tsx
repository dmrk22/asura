"use client";

import { useTranslations } from "next-intl";
import { useState } from "react";
import { api, type PrepResponse } from "@/lib/api";
import { loadOnboard } from "@/lib/session";

export default function PrepPage() {
  const t = useTranslations("prep");
  const [date, setDate] = useState("");
  const [notice, setNotice] = useState("");
  const [focus, setFocus] = useState("");
  const [plan, setPlan] = useState<PrepResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  async function create() {
    try {
      const onboard = loadOnboard();
      setPlan(
        await api.prep({
          interview_date: date,
          notice_source_url: notice,
          focus: focus
            .split(",")
            .map((value) => value.trim())
            .filter(Boolean),
          persona: onboard?.persona,
        }),
      );
      setError(null);
    } catch {
      setError(t("error"));
    }
  }
  return (
    <main className="mx-auto w-full max-w-2xl flex-1 px-6 py-10 sm:px-16">
      <h1 className="font-display text-4xl italic">{t("title")}</h1>
      <p className="mt-2 text-graphite">{t("subtitle")}</p>
      <div className="mt-8 flex flex-col gap-4">
        <label className="flex flex-col gap-1 text-sm">
          <span>{t("date")}</span>
          <input
            type="date"
            value={date}
            onChange={(event) => setDate(event.target.value)}
            className="rounded-md border border-graphite/30 bg-transparent px-3 py-2"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span>{t("notice")}</span>
          <input
            type="url"
            value={notice}
            onChange={(event) => setNotice(event.target.value)}
            className="rounded-md border border-graphite/30 bg-transparent px-3 py-2"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span>{t("focus")}</span>
          <input
            value={focus}
            onChange={(event) => setFocus(event.target.value)}
            className="rounded-md border border-graphite/30 bg-transparent px-3 py-2"
          />
        </label>
        <button
          type="button"
          onClick={create}
          className="w-fit rounded-md bg-signal px-4 py-2 text-bone"
        >
          {t("create")}
        </button>
      </div>
      {error && <p className="mt-4 text-signal">{error}</p>}
      {plan && (
        <ol className="mt-8 space-y-2">
          {plan.days.map((day) => (
            <li
              key={day.day}
              className="flex justify-between rounded-md border border-graphite/20 p-3"
            >
              <span>
                {t("day")} {day.day} · {day.focus}
              </span>
              <span className="font-mono">{day.hours}h</span>
            </li>
          ))}
        </ol>
      )}
    </main>
  );
}
