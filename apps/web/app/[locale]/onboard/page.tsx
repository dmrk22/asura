"use client";

import { useLocale, useTranslations } from "next-intl";
import { useEffect, useState } from "react";
import { useRouter } from "@/i18n/navigation";
import { api, type Persona, type RoleNode } from "@/lib/api";
import { INDIA_DISTRICTS } from "@/lib/india-districts";
import { saveOnboard } from "@/lib/session";

export default function OnboardPage() {
  const t = useTranslations("onboard");
  const locale = useLocale();
  const router = useRouter();

  const [roles, setRoles] = useState<RoleNode[]>([]);
  const [goal, setGoal] = useState("");
  const [persona, setPersona] = useState<Persona>("student");
  const [selectedState, setSelectedState] = useState("");
  const [district, setDistrict] = useState("");
  const [language, setLanguage] = useState(locale);
  const [constraints, setConstraints] = useState("");
  const [error, setError] = useState<string | null>(null);
  const districts =
    INDIA_DISTRICTS.find((entry) => entry.state === selectedState)?.districts ??
    [];

  useEffect(() => {
    api
      .taxonomy()
      .then((tx) => setRoles(tx.roles))
      .catch(() => setError(t("loadError")));
  }, [t]);

  function roleLabel(id: string): string {
    const r = roles.find((r) => r.id === id);
    if (!r) return id;
    if (locale === "te") return r.label_te;
    if (locale === "hi") return r.label_hi;
    return r.label_en;
  }

  function submit() {
    if (!goal) return;
    saveOnboard({
      personaId: "new-profile",
      persona,
      goal,
      held: {},
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

      <section className="mt-8 grid max-w-2xl grid-cols-1 gap-6 sm:grid-cols-2">
        <fieldset className="flex flex-col gap-1.5 text-sm">
          <legend className="text-graphite">{t("pathType")}</legend>
          <div className="flex gap-4 pt-1">
            <label className="flex items-center gap-2">
              <input
                type="radio"
                name="path-type"
                checked={persona === "student"}
                onChange={() => setPersona("student")}
              />
              {t("studentPath")}
            </label>
            <label className="flex items-center gap-2">
              <input
                type="radio"
                name="path-type"
                checked={persona === "rural"}
                onChange={() => setPersona("rural")}
              />
              {t("workPath")}
            </label>
          </div>
        </fieldset>
        <label className="flex flex-col gap-1.5 text-sm">
          <span className="text-graphite">{t("goal")}</span>
          <select
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            className="rounded-md border border-graphite/30 bg-transparent px-3 py-2"
          >
            <option value="" disabled>
              {t("goalPlaceholder")}
            </option>
            {roles.map((r) => (
              <option key={r.id} value={r.id}>
                {roleLabel(r.id)}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1.5 text-sm">
          <span className="text-graphite">{t("state")}</span>
          <select
            value={selectedState}
            onChange={(e) => {
              setSelectedState(e.target.value);
              setDistrict("");
            }}
            className="rounded-md border border-graphite/30 bg-transparent px-3 py-2"
          >
            <option value="" disabled>
              {t("statePlaceholder")}
            </option>
            {INDIA_DISTRICTS.map((entry) => (
              <option key={entry.state} value={entry.state}>
                {entry.state}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1.5 text-sm">
          <span className="text-graphite">{t("district")}</span>
          <select
            value={district}
            disabled={!selectedState}
            onChange={(e) => setDistrict(e.target.value)}
            className="rounded-md border border-graphite/30 bg-transparent px-3 py-2 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <option value="" disabled>
              {selectedState
                ? t("districtPlaceholder")
                : t("districtRequiresState")}
            </option>
            {districts.map((entry) => (
              <option key={entry} value={entry}>
                {entry}
              </option>
            ))}
          </select>
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
          disabled={!goal}
          className="mt-2 rounded-md bg-signal px-5 py-2.5 text-bone disabled:cursor-not-allowed disabled:opacity-50 sm:col-span-2 sm:w-fit"
        >
          {t("continue")}
        </button>
      </section>
    </main>
  );
}
