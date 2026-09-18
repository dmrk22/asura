"use client";

import {
  forceCenter,
  forceCollide,
  forceLink,
  forceManyBody,
  forceSimulation,
  forceX,
  forceY,
} from "d3-force";
import { useEffect, useRef, useState } from "react";

export interface GraphNode {
  id: string;
  label: string;
  demand: number;
  held: boolean;
  isNext: boolean;
}

export interface GraphEdge {
  source: string;
  target: string;
}

interface SimNode extends GraphNode {
  x: number;
  y: number;
}

const WIDTH = 760;
const HEIGHT = 520;

function radiusFor(demand: number): number {
  return Math.max(9, Math.min(22, 8 + demand * 6));
}

/** `d3-force` graph — node size = demand, held filled, missing outlined, the
 * current path's next step in --signal. Owns the frame budget on /path: it
 * runs to settle (d3's own alpha-decay timer, not a React animation loop)
 * then stops, and nothing else on the screen animates while it runs. */
export function SkillGraph({
  nodes,
  edges,
}: {
  nodes: GraphNode[];
  edges: GraphEdge[];
}) {
  const [positions, setPositions] = useState<SimNode[]>([]);
  const reducedMotion = useRef(false);

  useEffect(() => {
    reducedMotion.current = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    ).matches;
  }, []);

  useEffect(() => {
    if (nodes.length === 0) {
      setPositions([]);
      return;
    }
    const simNodes: SimNode[] = nodes.map((n, i) => ({
      ...n,
      x: WIDTH / 2 + Math.cos(i) * 40,
      y: HEIGHT / 2 + Math.sin(i) * 40,
    }));
    const validIds = new Set(nodes.map((n) => n.id));
    const simEdges = edges.filter(
      (e) => validIds.has(e.source) && validIds.has(e.target),
    );

    if (reducedMotion.current) {
      // Static: one instant layout, no animation loop at all.
      const sim = forceSimulation(simNodes)
        .force(
          "link",
          forceLink(simEdges)
            .id((d) => (d as SimNode).id)
            .distance(90),
        )
        .force("charge", forceManyBody().strength(-220))
        .force("center", forceCenter(WIDTH / 2, HEIGHT / 2))
        // Weak per-node pull toward the middle: `forceCenter` only re-centers
        // the whole simulation's centroid, so an isolated node (no edges,
        // e.g. a skill with no prereqs) can otherwise drift off-canvas under
        // pure repulsion. This keeps it in frame without fighting clustering.
        .force("x", forceX(WIDTH / 2).strength(0.05))
        .force("y", forceY(HEIGHT / 2).strength(0.05))
        .stop();
      for (let i = 0; i < 200; i++) sim.tick();
      setPositions([...simNodes]);
      return;
    }

    const sim = forceSimulation(simNodes)
      .force(
        "link",
        forceLink(simEdges)
          .id((d) => (d as SimNode).id)
          .distance(90),
      )
      .force("charge", forceManyBody().strength(-220))
      .force("center", forceCenter(WIDTH / 2, HEIGHT / 2))
      .force("x", forceX(WIDTH / 2).strength(0.05))
      .force("y", forceY(HEIGHT / 2).strength(0.05))
      .force(
        "collide",
        forceCollide((d) => radiusFor((d as SimNode).demand) + 6),
      );

    sim.on("tick", () => setPositions([...simNodes]));
    // d3's own alpha-decay timer settles and stops itself — that is the
    // "pause once settled" the frame budget requires.
    return () => {
      sim.stop();
    };
  }, [nodes, edges]);

  const byId = new Map(positions.map((p) => [p.id, p]));

  return (
    <svg
      viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      role="img"
      aria-label="Skill graph: node size shows this week's demand, filled nodes are held, outlined nodes are missing"
      className="h-auto w-full"
    >
      <title>Skill graph</title>
      {edges.map((e) => {
        const a = byId.get(e.source);
        const b = byId.get(e.target);
        if (!a || !b) return null;
        return (
          <line
            key={`${e.source}-${e.target}`}
            x1={a.x}
            y1={a.y}
            x2={b.x}
            y2={b.y}
            stroke="var(--graphite)"
            strokeOpacity={0.3}
            strokeWidth={1}
          />
        );
      })}
      {positions.map((n) => {
        const r = radiusFor(n.demand);
        const fill = n.held
          ? "var(--sage)"
          : n.isNext
            ? "var(--signal)"
            : "var(--bone)";
        const stroke = n.held ? "var(--sage)" : "var(--signal)";
        return (
          <g key={n.id}>
            <circle
              cx={n.x}
              cy={n.y}
              r={r}
              fill={fill}
              stroke={stroke}
              strokeWidth={n.held ? 0 : 2}
            />
            <text
              x={n.x}
              y={n.y + r + 13}
              textAnchor="middle"
              fontSize="9.5"
              fontFamily="var(--font-ui)"
              fill="var(--graphite)"
            >
              {n.label.length > 18 ? `${n.label.slice(0, 17)}…` : n.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
