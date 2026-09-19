"use client";

import { useLocale, useTranslations } from "next-intl";
import { useEffect, useMemo, useState } from "react";
import { RoadmapDiff } from "@/components/RoadmapDiff";
import type { GraphEdge, GraphNode } from "@/components/SkillGraph";
import { SkillGraph } from "@/components/SkillGraph";
import { useRouter } from "@/i18n/navigation";
import { api, type DiffJson, type PathJson, type SkillNode } from "@/lib/api";
import { loadOnboard, type OnboardState, saveOnboard } from "@/lib/session";

interface DiffState {
  before: PathJson;
  after: PathJson;
  diff: DiffJson;
  extraNote?: string;
}

export default function PathPage() {
  const t = useTranslations("path");
  const locale = useLocale();
  const router = useRouter();

  const [onboard, setOnboard] = useState<OnboardState | null>(null);
  const [skills, setSkills] = useState<SkillNode[]>([]);
  const [path, setPath] = useState<PathJson | null>(null);
  const [held, setHeld] = useState<Record<string, number>>({});
  const [diffState, setDiffState] = useState<DiffState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const [simSkill, setSimSkill] = useState("");
  const [shockSkill, setShockSkill] = useState("");
  const [shockWeight, setShockWeight] = useState(5);

  useEffect(() => {
    const ob = loadOnboard();
    if (!ob) {
      router.replace("/onboard");
      return;
    }
    setOnboard(ob);
    setHeld(ob.held);
    Promise.all([
      api.taxonomy(),
      api.roadmap({ held: ob.held, goal: ob.goal, persona: ob.persona }),
    ])
      .then(([tx, rm]) => {
        setSkills(tx.skills);
        setPath(rm.path);
        setSimSkill(rm.path.steps[0]?.skill ?? "");
        setShockSkill(rm.path.steps[0]?.skill ?? "");
      })
      .catch(() => setError(t("loadError")));
  }, [router, t]);

  function label(id: string): string {
    const s = skills.find((s) => s.id === id);
    if (!s) return id;
    if (locale === "te") return s.label_te;
    if (locale === "hi") return s.label_hi;
    return s.label_en;
  }

  const { nodes, edges } = useMemo<{
    nodes: GraphNode[];
    edges: GraphEdge[];
  }>(() => {
    if (!path) return { nodes: [], edges: [] };
    const labelFor = (id: string) => {
      const s = skills.find((s) => s.id === id);
      if (!s) return id;
      if (locale === "te") return s.label_te;
      if (locale === "hi") return s.label_hi;
      return s.label_en;
    };
    const nextSkill = path.steps[0]?.skill;
    const nodeMap = new Map<string, GraphNode>();
    for (const id of Object.keys(held)) {
      if (held[id] > 0) {
        nodeMap.set(id, {
          id,
          label: labelFor(id),
          demand: 0.4,
          held: true,
          isNext: false,
        });
      }
    }
    for (const s of path.steps) {
      nodeMap.set(s.skill, {
        id: s.skill,
        label: labelFor(s.skill),
        demand: s.demand || 0.4,
        held: false,
        isNext: s.skill === nextSkill,
      });
    }
    const edgeList: GraphEdge[] = [];
    for (const s of path.steps) {
      for (const prereq of s.prereqs) {
        edgeList.push({ source: prereq, target: s.skill });
      }
    }
    return { nodes: [...nodeMap.values()], edges: edgeList };
  }, [path, held, skills, locale]);

  async function applyLearn(skill: string) {
    if (!onboard || !path || !skill) return;
    setBusy(true);
    setError(null);
    try {
      const res = await api.learn({
        held,
        goal: onboard.goal,
        persona: onboard.persona,
        skill,
      });
      setDiffState({ before: res.before, after: res.after, diff: res.diff });
      setHeld(res.held_after);
      setPath(res.after);
      saveOnboard({ ...onboard, held: res.held_after });
    } catch {
      setError(t("actionError"));
    } finally {
      setBusy(false);
    }
  }

  async function applyShock() {
    if (!onboard || !path || !shockSkill) return;
    setBusy(true);
    setError(null);
    try {
      const res = await api.shock({
        held,
        goal: onboard.goal,
        persona: onboard.persona,
        skill: shockSkill,
        weight: shockWeight,
      });
      setDiffState({
        before: res.before,
        after: res.after,
        diff: res.diff,
        extraNote: `requested_weight: ${res.requested_weight}x -> applied_weight: ${res.applied_weight}x`,
      });
      setPath(res.after);
    } catch {
      setError(t("actionError"));
    } finally {
      setBusy(false);
    }
  }

  if (!onboard || !path) {
    return (
      <main className="mx-auto w-full max-w-[1440px] flex-1 px-6 py-10 sm:px-16">
        {error ? (
          <p className="text-signal">{error}</p>
        ) : (
          <p className="text-graphite">{t("loading")}</p>
        )}
      </main>
    );
  }

  return (
    <main className="mx-auto w-full max-w-[1440px] flex-1 px-6 py-10 sm:px-16">
      <div className="flex flex-wrap items-baseline justify-between gap-3">
        <div>
          <h1 className="font-display text-4xl italic">{t("title")}</h1>
          <p className="mt-1 text-graphite text-sm">
            {t("goalLine", {
              goal: locale === "te" ? path.goal_label_te : path.goal_label_en,
            })}
          </p>
        </div>
        <div className="flex gap-6 font-mono text-sm tabular-nums">
          <span>
            <span className="text-graphite">{t("totalHours")} </span>
            {path.total_hours}h
          </span>
          <span>
            <span className="text-graphite">{t("weeksAt10")} </span>
            {path.weeks_at_10hpw}
          </span>
        </div>
      </div>

      {error && <p className="mt-4 text-signal text-sm">{error}</p>}

      <div className="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-[1.2fr_1fr]">
        <div className="rounded-md border border-graphite/20 p-3">
          <SkillGraph nodes={nodes} edges={edges} />
        </div>

        <div>
          <h2 className="mb-3 font-mono text-graphite text-xs uppercase tracking-wide">
            {t("steps")}
          </h2>
          {path.steps.length === 0 ? (
            <p className="text-graphite text-sm">{t("goalReached")}</p>
          ) : (
            <ol className="flex flex-col gap-3">
              {path.steps.map((s, i) => (
                <li
                  key={s.skill}
                  className="rounded-md border border-graphite/15 p-3"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <span className="font-mono text-graphite text-xs tabular-nums">
                        {String(i + 1).padStart(2, "0")}
                      </span>{" "}
                      <span className="text-sm">
                        {locale === "te"
                          ? s.label_te
                          : locale === "hi"
                            ? s.label_hi
                            : s.label_en}
                      </span>
                      <p className="mt-1 text-graphite text-xs italic">
                        {s.why.join(" · ")}
                      </p>
                    </div>
                    <span className="whitespace-nowrap font-mono text-xs tabular-nums">
                      {s.hours}h &middot; L{s.level}
                    </span>
                  </div>
                  <button
                    type="button"
                    disabled={busy}
                    onClick={() => applyLearn(s.skill)}
                    className="mt-2 rounded-full border border-signal px-3 py-1 font-mono text-signal text-xs disabled:opacity-50"
                  >
                    {t("learnedThis")}
                  </button>
                </li>
              ))}
            </ol>
          )}
        </div>
      </div>

      <section className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-2">
        <div className="rounded-md border border-graphite/20 p-4">
          <h2 className="mb-3 font-mono text-graphite text-xs uppercase tracking-wide">
            {t("simulateTitle")}
          </h2>
          <div className="flex flex-wrap items-center gap-3">
            <select
              value={simSkill}
              onChange={(e) => setSimSkill(e.target.value)}
              className="rounded-md border border-graphite/30 bg-transparent px-3 py-2 text-sm"
            >
              {skills.map((s) => (
                <option key={s.id} value={s.id}>
                  {label(s.id)}
                </option>
              ))}
            </select>
            <button
              type="button"
              disabled={busy}
              onClick={() => applyLearn(simSkill)}
              className="rounded-md bg-signal px-4 py-2 text-bone text-sm disabled:opacity-50"
            >
              {t("apply")}
            </button>
          </div>
        </div>

        <div className="rounded-md border border-graphite/20 p-4">
          <h2 className="mb-3 font-mono text-graphite text-xs uppercase tracking-wide">
            {t("shockTitle")}
          </h2>
          <div className="flex flex-wrap items-center gap-3">
            <select
              value={shockSkill}
              onChange={(e) => setShockSkill(e.target.value)}
              className="rounded-md border border-graphite/30 bg-transparent px-3 py-2 text-sm"
            >
              {skills.map((s) => (
                <option key={s.id} value={s.id}>
                  {label(s.id)}
                </option>
              ))}
            </select>
            <input
              type="number"
              min={0.1}
              step={0.5}
              value={shockWeight}
              onChange={(e) => setShockWeight(Number(e.target.value))}
              className="w-20 rounded-md border border-graphite/30 bg-transparent px-3 py-2 font-mono text-sm tabular-nums"
            />
            <button
              type="button"
              disabled={busy}
              onClick={applyShock}
              className="rounded-md bg-signal px-4 py-2 text-bone text-sm disabled:opacity-50"
            >
              {t("apply")}
            </button>
          </div>
        </div>
      </section>

      {diffState && (
        <section className="mt-10">
          <h2 className="mb-3 font-mono text-graphite text-xs uppercase tracking-wide">
            {t("diffTitle")}
          </h2>
          <RoadmapDiff
            before={diffState.before}
            after={diffState.after}
            diff={diffState.diff}
            extra={
              diffState.extraNote ? (
                <span className="font-mono text-xs tabular-nums">
                  {diffState.extraNote}
                </span>
              ) : undefined
            }
          />
        </section>
      )}
    </main>
  );
}
