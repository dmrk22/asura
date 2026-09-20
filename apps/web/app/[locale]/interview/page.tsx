"use client";

import { useTranslations } from "next-intl";
import { useState } from "react";
import { api, type InterviewReview } from "@/lib/api";
import { loadOnboard } from "@/lib/session";

export default function InterviewPage() {
  const t = useTranslations("interview");
  const [question, setQuestion] = useState("");
  const [source, setSource] = useState("");
  const [transcript, setTranscript] = useState("");
  const [review, setReview] = useState<InterviewReview | null>(null);
  const [error, setError] = useState<string | null>(null);
  async function submit() {
    try {
      const onboard = loadOnboard();
      setReview(
        await api.interviewReview({
          question,
          transcript,
          question_source_url: source,
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
      <div className="mt-8 flex flex-col gap-4">
        <label className="flex flex-col gap-1 text-sm">
          <span>{t("question")}</span>
          <input
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            className="rounded-md border border-graphite/30 bg-transparent px-3 py-2"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span>{t("source")}</span>
          <input
            type="url"
            value={source}
            onChange={(event) => setSource(event.target.value)}
            className="rounded-md border border-graphite/30 bg-transparent px-3 py-2"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span>{t("transcript")}</span>
          <textarea
            value={transcript}
            onChange={(event) => setTranscript(event.target.value)}
            className="min-h-40 rounded-md border border-graphite/30 bg-transparent px-3 py-2"
          />
        </label>
        <button
          type="button"
          onClick={submit}
          className="w-fit rounded-md bg-signal px-4 py-2 text-bone"
        >
          {t("review")}
        </button>
      </div>
      {error && <p className="mt-4 text-signal">{error}</p>}
      {review && (
        <section className="mt-8 rounded-md border border-graphite/20 p-4">
          <h2 className="font-display text-2xl italic">{t("feedback")}</h2>
          <p className="mt-2 font-mono text-xs">{review.word_count} words</p>
          <ul className="mt-4 space-y-3">
            {review.feedback.map((item) => (
              <li key={item.area}>
                <p className="text-sm">{item.guidance}</p>
                <blockquote className="mt-1 border-signal border-l-2 pl-3 text-graphite text-sm">
                  “{item.quote}”
                </blockquote>
              </li>
            ))}
          </ul>
          <h3 className="mt-5 font-mono text-xs text-graphite uppercase">
            {t("followUp")}
          </h3>
          <p className="mt-1">{review.follow_up}</p>
        </section>
      )}
    </main>
  );
}
