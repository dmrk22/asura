"use client";

import { useLocale, useTranslations } from "next-intl";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "@/i18n/navigation";
import { api, type RoleNode, type SkillNode } from "@/lib/api";
import { saveOnboard } from "@/lib/session";
import {
  conciseRecap,
  extractName,
  isAffirmative,
} from "@/lib/voice-conversation";
import { parseVoiceIntent, type VoiceIntent } from "@/lib/voice-intent";

type ConversationStage = "name" | "profile" | "confirm" | "creating";
type RecognitionResult = { 0: { transcript: string } };
type Recognition = {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  start: () => void;
  stop: () => void;
  onresult: ((event: { results: ArrayLike<RecognitionResult> }) => void) | null;
  onend: (() => void) | null;
};
type RecognitionConstructor = new () => Recognition;

export default function VoicePage() {
  const t = useTranslations("voice");
  const locale = useLocale();
  const router = useRouter();
  const recognition = useRef<Recognition | null>(null);
  const transcriptRef = useRef("");
  const [transcript, setTranscript] = useState("");
  const [roles, setRoles] = useState<RoleNode[]>([]);
  const [skills, setSkills] = useState<SkillNode[]>([]);
  const [intent, setIntent] = useState<VoiceIntent | null>(null);
  const [name, setName] = useState("");
  const [stage, setStage] = useState<ConversationStage>("name");
  const [assistantMessage, setAssistantMessage] = useState(() => t("welcome"));
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

  function voiceLanguage() {
    return locale === "te" ? "te-IN" : locale === "hi" ? "hi-IN" : "en-IN";
  }

  function preferredVoice() {
    const voices = speechSynthesis.getVoices();
    const language = voiceLanguage().toLowerCase();
    const languageVoices = voices.filter((voice) =>
      voice.lang.toLowerCase().startsWith(language.slice(0, 2)),
    );
    if (locale !== "en") return languageVoices[0] ?? null;

    const professionalVoice = [
      /microsoft (?:david|mark|guy|ryan)/i,
      /google uk english male/i,
      /daniel/i,
      /alex/i,
    ]
      .map((pattern) => voices.find((voice) => pattern.test(voice.name)))
      .find(Boolean);
    return professionalVoice ?? languageVoices[0] ?? voices[0] ?? null;
  }

  function speak(text: string, after?: () => void) {
    setAssistantMessage(text);
    speechSynthesis.cancel();
    const message = new SpeechSynthesisUtterance(text);
    message.lang = voiceLanguage();
    // A slightly faster, neutral delivery keeps the conversation professional
    // without making the assistant hard to understand.
    message.rate = 1.08;
    message.pitch = 1;
    message.volume = 1;
    message.voice = preferredVoice();
    message.onend = () => after?.();
    speechSynthesis.speak(message);
  }

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

  function beginRecognition() {
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
    instance.lang = voiceLanguage();
    instance.interimResults = true;
    instance.continuous = true;
    instance.onresult = (event) => {
      const nextTranscript = Array.from(event.results)
        .map((result) => result[0].transcript)
        .join(" ");
      transcriptRef.current = nextTranscript;
      setTranscript(nextTranscript);
    };
    instance.onend = () => setListening(false);
    recognition.current = instance;
    setStartedAt(performance.now());
    setListening(true);
    instance.start();
  }

  function speakThenListen(message: string) {
    speak(message, beginRecognition);
  }

  async function createRoadmap(confirmedIntent: VoiceIntent, userName: string) {
    if (!confirmedIntent.goal) return;
    setStage("creating");
    setAssistantMessage(t("building"));
    try {
      await api.roadmap({
        held: confirmedIntent.held,
        goal: confirmedIntent.goal,
        persona: "student",
      });
      saveOnboard({
        personaId: "voice",
        persona: "student",
        goal: confirmedIntent.goal,
        held: confirmedIntent.held,
        district: confirmedIntent.district,
        language: locale,
        constraints: "",
      });
      speak(
        t("roadmapCreated", {
          name: userName,
          goal: roleLabel(confirmedIntent.goal),
        }),
        () => router.push("/path"),
      );
    } catch {
      setStage("profile");
      speakThenListen(t("roadmapError"));
    }
  }

  function handleTurn(answer: string) {
    const reply = answer.trim();
    if (!reply || stage === "creating") return;
    if (stage === "name") {
      const detectedName = extractName(reply);
      if (!detectedName) {
        speakThenListen(t("nameRetry"));
        return;
      }
      setName(detectedName);
      setStage("profile");
      speakThenListen(t("askProfile", { name: detectedName }));
      return;
    }
    if (stage === "profile") {
      const started = performance.now();
      const detectedIntent = parseVoiceIntent(reply, roles, skills);
      setIntentMs(Math.round(performance.now() - started));
      setIntent(detectedIntent);
      if (!detectedIntent.goal) {
        speakThenListen(t("noGoal"));
        return;
      }
      setStage("confirm");
      const detectedSkills = Object.keys(detectedIntent.held)
        .map(skillLabel)
        .join(", ");
      speakThenListen(
        t("confirmRoadmap", {
          name,
          recap: conciseRecap(reply),
          goal: roleLabel(detectedIntent.goal),
          skills: detectedSkills || t("none"),
        }),
      );
      return;
    }
    if (!intent?.goal) return;
    if (isAffirmative(reply)) {
      void createRoadmap(intent, name);
      return;
    }
    setStage("profile");
    speakThenListen(t("changeRequest"));
  }

  function start() {
    if (listening) return;
    if (stage === "name") {
      speakThenListen(t("welcome"));
      return;
    }
    if (stage === "profile") {
      speakThenListen(t("askProfile", { name }));
      return;
    }
    if (stage === "confirm") {
      speakThenListen(t("askConfirmation"));
      return;
    }
  }

  function stop() {
    recognition.current?.stop();
    setListening(false);
    if (startedAt !== null) {
      setRecognitionMs(Math.round(performance.now() - startedAt));
    }
    handleTurn(transcriptRef.current);
  }

  function submitTypedAnswer() {
    transcriptRef.current = transcript;
    handleTurn(transcript);
  }

  const detectedSkills = intent ? Object.keys(intent.held) : [];
  const trace =
    stage === "name"
      ? t("traceName")
      : stage === "profile"
        ? t("traceProfile", { name: name || "—" })
        : stage === "confirm"
          ? t("traceConfirm", {
              goal: intent?.goal ? roleLabel(intent.goal) : "—",
            })
          : t("traceCreating");

  return (
    <main className="mx-auto w-full max-w-2xl flex-1 px-6 py-10 sm:px-16">
      <h1 className="font-display text-4xl italic">{t("title")}</h1>
      <p className="mt-2 text-graphite">{t("subtitle")}</p>
      {!supported && <p className="mt-4 text-amber">{t("notSupported")}</p>}

      <section
        className="mt-6 rounded-md border border-graphite/20 p-5"
        aria-live="polite"
      >
        <p className="font-mono text-xs text-graphite uppercase">
          {t("assistant")}
        </p>
        <p className="mt-2 text-lg">{assistantMessage || t("ready")}</p>
      </section>

      <div className="mt-6 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={listening ? stop : start}
          disabled={stage === "creating" || roles.length === 0}
          className="rounded-full bg-signal px-5 py-3 text-bone disabled:opacity-50"
        >
          {listening ? t("finish") : t("start")}
        </button>
        <button
          type="button"
          onClick={submitTypedAnswer}
          disabled={!transcript.trim() || stage === "creating"}
          className="rounded-full border border-graphite/30 px-5 py-3 disabled:opacity-50"
        >
          {t("submitAnswer")}
        </button>
        <button
          type="button"
          onClick={() => assistantMessage && speak(assistantMessage)}
          disabled={!assistantMessage}
          className="rounded-full border border-graphite/30 px-5 py-3 disabled:opacity-50"
        >
          {t("reply")}
        </button>
      </div>

      <textarea
        value={transcript}
        onChange={(event) => {
          transcriptRef.current = event.target.value;
          setTranscript(event.target.value);
        }}
        placeholder={t("placeholder")}
        className="mt-6 min-h-40 w-full rounded-md border border-graphite/20 bg-transparent p-4"
      />

      {intent?.goal && (
        <section className="mt-6 rounded-md border border-graphite/20 p-5">
          <p className="font-medium">
            {t("detectedGoal", { goal: roleLabel(intent.goal) })}
          </p>
          <p className="mt-2 text-sm text-graphite">
            {t("skillsDetected", {
              skills: detectedSkills.map(skillLabel).join(", ") || t("none"),
            })}
          </p>
          {intent.district && (
            <p className="mt-1 text-sm text-graphite">
              {t("districtDetected", { district: intent.district })}
            </p>
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
          <p className="mt-2 text-sm text-graphite">{trace}</p>
        </div>
      </section>
    </main>
  );
}
