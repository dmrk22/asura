"use client";

import { useLocale, useTranslations } from "next-intl";
import { useEffect, useState } from "react";
import { useRouter } from "@/i18n/navigation";
import { api, type PersonaProfile, type RoleNode } from "@/lib/api";
import { saveOnboard } from "@/lib/session";

export default function OnboardPage() {
  const t = useTranslations("onboard");
  const locale = useLocale();
  const router = useRouter();

  const [personas, setPersonas] = useState<PersonaProfile[]>([]);
  const [roles, setRoles] = useState<RoleNode[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [goal, setGoal] = useState("");
  const [district, setDistrict] = useState("");
  const [language, setLanguage] = useState(locale);
  const [constraints, setConstraints] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.personas(), api.taxonomy()])
      .then(([p, tx]) => {
        setPersonas(p.personas);
        setRoles(tx.roles);
      })
      .catch(() => setError(t("loadError")));
  }, [t]);

  function selectPersona(p: PersonaProfile) {
    setSelectedId(p.id);
    setGoal(p.goal);
    setDistrict(p.district ?? "");
  }

  function roleLabel(id: string): string {
    const r = roles.find((r) => r.id === id);
    if (!r) return id;
    if (locale === "te") return r.label_te;
    if (locale === "hi") return r.label_hi;
    return r.label_en;
  }

  function submit() {
    const persona = personas.find((p) => p.id === selectedId);
    if (!persona) return;
    saveOnboard({
      personaId: persona.id,
      persona: persona.persona,
      goal,
      held: persona.held,
      district: district || null,
      language,
      constraints,
    });
    router.push("/path");
  }

  return (
    <main className="mx-auto w-full max-w-[1440px] flex-1 px-6 py-10 sm:px-16">
      <h1 className="font-display text-4xl italic">{t("title")}</h1>
      <p className="mt-2 max-w-prose text-graphite">{t("subtitle")}</p>

      {error && <p className="mt-4 text-signal text-sm">{error}</p>}

      <section aria-label={t("personaLabel")} className="mt-8">
        <h2 className="mb-3 font-mono text-graphite text-xs uppercase tracking-wide">
          {t("personaLabel")}
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {personas.map((p) => (
            <button
              key={p.id}
              type="button"
              onClick={() => selectPersona(p)}
              aria-pressed={selectedId === p.id}
              className={`rounded-md border p-4 text-left transition-colors ${
                selectedId === p.id
                  ? "border-signal bg-signal/5"
                  : "border-graphite/25 hover:border-graphite/50"
              }`}
            >
              <p className="text-base">{p.name}</p>
              <p className="mt-1 text-graphite text-xs">{roleLabel(p.goal)}</p>
              <p className="mt-2 font-mono text-[10px] text-sage uppercase tracking-wide">
                {t("synthetic")}
              </p>
            </button>
          ))}
        </div>
      </section>

      {selectedId && (
        <section className="mt-10 grid max-w-2xl grid-cols-1 gap-6 sm:grid-cols-2">
          <label className="flex flex-col gap-1.5 text-sm">
            <span className="text-graphite">{t("goal")}</span>
            <select
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              className="rounded-md border border-graphite/30 bg-transparent px-3 py-2"
            >
              {roles.map((r) => (
                <option key={r.id} value={r.id}>
                  {roleLabel(r.id)}
                </option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1.5 text-sm">
            <span className="text-graphite">{t("district")}</span>
            <input
              value={district}
              onChange={(e) => setDistrict(e.target.value)}
              className="rounded-md border border-graphite/30 bg-transparent px-3 py-2"
            />
          </label>
          <label className="flex flex-col gap-1.5 text-sm">
            <span className="text-graphite">{t("language")}</span>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="rounded-md border border-graphite/30 bg-transparent px-3 py-2"
            >
              <option value="en">English</option>
              <option value="te">తెలుగు</option>
              <option value="hi">हिन्दी</option>
            </select>
          </label>
          <label className="flex flex-col gap-1.5 text-sm">
            <span className="text-graphite">{t("constraints")}</span>
            <input
              value={constraints}
              onChange={(e) => setConstraints(e.target.value)}
              placeholder={t("constraintsPlaceholder")}
              className="rounded-md border border-graphite/30 bg-transparent px-3 py-2"
            />
          </label>

          <button
            type="button"
            onClick={submit}
            className="mt-2 rounded-md bg-signal px-5 py-2.5 text-bone sm:col-span-2 sm:w-fit"
          >
            {t("continue")}
          </button>
        </section>
      )}
    </main>
  );
}
