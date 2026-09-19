"use client";

import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import type { DiffJson, PathJson } from "@/lib/api";

const SPRING = { type: "spring" as const, stiffness: 260, damping: 28 };

function StepRow({
  label,
  hours,
  state,
}: {
  label: string;
  hours: number;
  state: "removed" | "added" | "reordered" | "same";
}) {
  const cls =
    state === "removed"
      ? "text-graphite line-through opacity-60"
      : state === "reordered"
        ? "text-signal"
        : "text-ink";
  return (
    <div
      className={`flex items-center justify-between gap-3 border-graphite/10 border-b py-1.5 text-sm ${cls}`}
    >
      <span>{label}</span>
      <span className="font-mono text-xs tabular-nums">{hours}h</span>
    </div>
  );
}

function Pane({
  title,
  path,
  removed,
  reordered,
}: {
  title: string;
  path: PathJson;
  removed: Set<string>;
  reordered: Set<string>;
}) {
  return (
    <div>
      <h3 className="mb-2 font-mono text-graphite text-xs uppercase tracking-wide">
        {title}
      </h3>
      {path.steps.length === 0 ? (
        <p className="text-graphite text-sm">Goal reached.</p>
      ) : (
        path.steps.map((s) => (
          <StepRow
            key={s.skill}
            label={s.label_en}
            hours={s.hours}
            state={
              removed.has(s.skill)
                ? "removed"
                : reordered.has(s.skill)
                  ? "reordered"
                  : "same"
            }
          />
        ))
      )}
    </div>
  );
}

/** Before | After diff, with `cause` and the animated once-then-settle beat
 * from UI_BRIEF (§Motion). Reduced motion collapses to an instant state
 * change with a static +/- list. */
export function RoadmapDiff({
  before,
  after,
  diff,
  extra,
}: {
  before: PathJson;
  after: PathJson;
  diff: DiffJson;
  /** e.g. applied vs requested weight for market shock */
  extra?: React.ReactNode;
}) {
  const prefersReduced = useReducedMotion();
  const removed = new Set(diff.removed);
  const reordered = new Set(diff.reordered);
  const Wrap = prefersReduced ? "div" : motion.div;
  const wrapProps = prefersReduced
    ? {}
    : {
        initial: { opacity: 0, y: 8 },
        animate: { opacity: 1, y: 0 },
        transition: SPRING,
      };

  return (
    <AnimatePresence mode="wait">
      <Wrap
        key={diff.cause + diff.hours_delta}
        {...wrapProps}
        className="rounded-md border border-graphite/20 p-4"
      >
        <div className="mb-3 flex flex-wrap items-center gap-3">
          <span className="rounded-full border border-graphite/30 px-2 py-0.5 font-mono text-xs uppercase tracking-wide">
            cause: {diff.cause}
          </span>
          <span className="font-mono text-xs tabular-nums">
            hours_delta: {diff.hours_delta}h
          </span>
          {extra}
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Pane
            title="Before"
            path={before}
            removed={removed}
            reordered={reordered}
          />
          <Pane
            title="After"
            path={after}
            removed={new Set()}
            reordered={reordered}
          />
        </div>
      </Wrap>
    </AnimatePresence>
  );
}
