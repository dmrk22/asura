"use client";

import { useLocale, useTranslations } from "next-intl";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "@/i18n/navigation";
import { api, type RoleNode, type SkillNode } from "@/lib/api";
import { saveOnboard } from "@/lib/session";
import { parseVoiceIntent, type VoiceIntent } from "@/lib/voice-intent";

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
  const router = useRouter();
  const recognition = useRef<Recognition | null>(null);
  const [transcript, setTranscript] = useState("");
  const [roles, setRoles] = useState<RoleNode[]>([]);
  const [skills, setSkills] = useState<SkillNode[]>([]);
  const [intent, setIntent] = useState<VoiceIntent | null>(null);
  const [listening, setListening] = useState(false);
  const [supported, setSupported] = useState(true);
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const [recognitionMs, setRecognitionMs] = useState<number | null>(null);
  const [intentMs, setIntentMs] = useState<number | null>(null);

  useEffect(() => {
    api.taxonomy().then((taxonomy) => {
      setRoles(taxonomy.roles);
      setSkills(taxonomy.skills);
    });
  }, []);

  function roleLabel(id: string): string {
    const role = roles.find((candidate) => candidate.id === id);
    if (!role) return id;
    if (locale === "te") return role.label_te;
    if (locale === "hi") return role.label_hi;
    return role.label_en;
  }

  function skillLabel(id: string): string {
    const skill = skills.find((candidate) => candidate.id === id);
    if (!skill) return id;
    if (locale === "te") return skill.label_te;
    if (locale === "hi") return skill.label_hi;
    return skill.label_en;
  }

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
    if (startedAt !== null) {
      setRecognitionMs(Math.round(performance.now() - startedAt));
    }
  }

  function understand() {
    if (!transcript.trim()) return;
    const started = performance.now();
    setIntent(parseVoiceIntent(transcript, roles, skills));
    setIntentMs(Math.round(performance.now() - started));
  }

  function speak() {
    if (!intent?.goal) return;
    speechSynthesis.cancel();
    const message = new SpeechSynthesisUtterance(
      t("spokenGuidance", { goal: roleLabel(intent.goal) }),
    );
    message.lang =
      locale === "te" ? "te-IN" : locale === "hi" ? "hi-IN" : "en-IN";
    speechSynthesis.speak(message);
  }

  function createRoadmap() {
    if (!intent?.goal) return;
    saveOnboard({
      personaId: "voice",
      persona: "student",
      goal: intent.goal,
      held: intent.held,
      district: intent.district,
      language: locale,
      constraints: "",
    });
    router.push("/path");
  }

  const detectedSkills = intent ? Object.keys(intent.held) : [];

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
          onClick={understand}
          disabled={!transcript.trim() || roles.length === 0}
          className="rounded-full border border-graphite/30 px-5 py-3 disabled:opacity-50"
        >
          {t("understand")}
        </button>
        <button
          type="button"
          onClick={speak}
          disabled={!intent?.goal}
          className="rounded-full border border-graphite/30 px-5 py-3 disabled:opacity-50"
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

      {intent && (
        <section className="mt-6 rounded-md border border-graphite/20 p-5">
          {intent.goal ? (
            <>
              <p className="font-medium">
                {t("detectedGoal", { goal: roleLabel(intent.goal) })}
              </p>
              <p className="mt-2 text-sm text-graphite">
                {t("skillsDetected", {
                  skills:
                    detectedSkills.map(skillLabel).join(", ") || t("none"),
                })}
              </p>
              {intent.district && (
                <p className="mt-1 text-sm text-graphite">
                  {t("districtDetected", { district: intent.district })}
                </p>
              )}
              <button
                type="button"
                onClick={createRoadmap}
                className="mt-5 rounded-md bg-signal px-5 py-2.5 text-bone"
              >
                {t("createRoadmap")}
              </button>
            </>
          ) : (
            <p className="text-amber">{t("noGoal")}</p>
          )}
        </section>
      )}

      <section className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="rounded-md border border-graphite/20 p-4">
          <h2 className="font-mono text-xs text-graphite uppercase">
            {t("hud")}
          </h2>
          <p className="mt-2 font-mono text-sm">
            {t("asrTiming", { ms: recognitionMs ?? "—" })}
            {" · "}
            {t("intentTiming", { ms: intentMs ?? "—" })}
          </p>
        </div>
        <div className="rounded-md border border-graphite/20 p-4">
          <h2 className="font-mono text-xs text-graphite uppercase">
            {t("agent")}
          </h2>
          <p className="mt-2 text-sm text-graphite">
            {intent?.goal
              ? t("traceReady", {
                  goal: roleLabel(intent.goal),
                  count: detectedSkills.length,
                })
              : t("traceIdle")}
          </p>
        </div>
      </section>
    </main>
  );
}
