"use client";

import { useLocale, useTranslations } from "next-intl";
import { useRef, useState } from "react";

type Recognition = {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  start: () => void;
  stop: () => void;
  onresult:
    | ((event: { results: ArrayLike<{ 0: { transcript: string } }> }) => void)
    | null;
  onend: (() => void) | null;
};
type RecognitionConstructor = new () => Recognition;

export default function VoicePage() {
  const t = useTranslations("voice");
  const locale = useLocale();
  const recognition = useRef<Recognition | null>(null);
  const [transcript, setTranscript] = useState("");
  const [listening, setListening] = useState(false);
  const [supported, setSupported] = useState(true);
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const [elapsed, setElapsed] = useState<number | null>(null);

  function start() {
    const speechWindow = window as typeof window & {
      SpeechRecognition?: RecognitionConstructor;
      webkitSpeechRecognition?: RecognitionConstructor;
    };
    const Constructor =
      speechWindow.SpeechRecognition ?? speechWindow.webkitSpeechRecognition;
    if (!Constructor) {
      setSupported(false);
      return;
    }
    const instance = new Constructor();
    instance.lang =
      locale === "te" ? "te-IN" : locale === "hi" ? "hi-IN" : "en-IN";
    instance.interimResults = true;
    instance.continuous = true;
    instance.onresult = (event) =>
      setTranscript(
        Array.from(event.results)
          .map((result) => result[0].transcript)
          .join(" "),
      );
    instance.onend = () => setListening(false);
    recognition.current = instance;
    setStartedAt(performance.now());
    setListening(true);
    instance.start();
  }
  function stop() {
    recognition.current?.stop();
    setListening(false);
    if (startedAt !== null)
      setElapsed(Math.round(performance.now() - startedAt));
  }
  function speak() {
    if (!transcript.trim()) return;
    speechSynthesis.cancel();
    const message = new SpeechSynthesisUtterance(transcript);
    message.lang =
      locale === "te" ? "te-IN" : locale === "hi" ? "hi-IN" : "en-IN";
    speechSynthesis.speak(message);
  }

  return (
    <main className="mx-auto w-full max-w-2xl flex-1 px-6 py-10 sm:px-16">
      <h1 className="font-display text-4xl italic">{t("title")}</h1>
      <p className="mt-2 text-graphite">{t("subtitle")}</p>
      {!supported && <p className="mt-4 text-amber">{t("notSupported")}</p>}
      <div className="mt-8 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={listening ? stop : start}
          className="rounded-full bg-signal px-5 py-3 text-bone"
        >
          {listening ? t("stop") : t("start")}
        </button>
        <button
          type="button"
          onClick={speak}
          className="rounded-full border border-graphite/30 px-5 py-3"
        >
          {t("reply")}
        </button>
      </div>
      <textarea
        value={transcript}
        onChange={(event) => setTranscript(event.target.value)}
        placeholder={t("placeholder")}
        className="mt-6 min-h-40 w-full rounded-md border border-graphite/20 bg-transparent p-4"
      />
      <section className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="rounded-md border border-graphite/20 p-4">
          <h2 className="font-mono text-xs text-graphite uppercase">
            {t("hud")}
          </h2>
          <p className="mt-2 font-mono text-sm">
            browser ASR {elapsed === null ? "—" : `${elapsed}ms`}
          </p>
        </div>
        <div className="rounded-md border border-graphite/20 p-4">
          <h2 className="font-mono text-xs text-graphite uppercase">
            {t("agent")}
          </h2>
          <p className="mt-2 text-sm text-graphite">
            ASR → transcript → browser TTS
          </p>
        </div>
      </section>
    </main>
  );
}
