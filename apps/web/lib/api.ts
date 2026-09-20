/**
 * Typed client for `daari.routes`. Shapes mirror apps/api/daari/routes.py
 * exactly — if they drift, the API schema wins (web.md).
 *
 * `/leads/live`, `/schemes`, `/geocode` and `POST /match`'s `live` flag are
 * landing on the API lane; they are typed optimistically below and every
 * caller treats a 404 as "not yet available" rather than throwing.
 */

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// The browser always calls the same-origin proxy (see next.config.ts
// `rewrites`) so no CORS headers are needed from the API.
const BASE = "/api-proxy";

export type Persona = "student" | "rural";

export interface SkillNode {
  id: string;
  label_en: string;
  label_te: string;
  label_hi: string;
  aliases: string[];
  level: number;
  hours: number;
  prereqs: string[];
  source: string;
}

export interface RoleNode {
  id: string;
  label_en: string;
  label_te: string;
  label_hi: string;
  required_skills: Record<string, number>;
  source: string;
}

export interface Taxonomy {
  skills: SkillNode[];
  roles: RoleNode[];
  counts: { skills: number; roles: number };
}

export interface PersonaProfile {
  id: string;
  name: string;
  persona: Persona;
  goal: string;
  held: Record<string, number>;
  districts: string[];
  district: string | null;
  languages: string[];
  note: string;
  synthetic: true;
}

export interface PathStep {
  skill: string;
  label_en: string;
  label_te: string;
  label_hi: string;
  hours: number;
  level: number;
  prereqs: string[];
  why: string[];
  source: string;
  demand: number;
}

export interface PathJson {
  goal: string;
  goal_label_en: string;
  goal_label_te: string;
  total_hours: number;
  weeks_at_10hpw: number;
  steps: PathStep[];
}

export interface DiffJson {
  removed: string[];
  added: string[];
  reordered: string[];
  hours_delta: number;
  cause: "learner" | "market";
  empty: boolean;
}

export interface RoadmapResponse {
  path: PathJson;
  persona: Persona;
}

export interface LearnResponse {
  before: PathJson;
  after: PathJson;
  diff: DiffJson;
  held_after: Record<string, number>;
  persona: Persona;
}

export interface ShockResponse {
  before: PathJson;
  after: PathJson;
  diff: DiffJson;
  shocked_skill: string;
  applied_weight: number;
  requested_weight: number;
  persona: Persona;
}

export interface MatchComponents {
  coverage: number;
  gap_cost: number;
  constraint_fit: number;
  demand_bonus: number;
  vector_sim?: number;
}

export interface ScamReason {
  rule: string;
  weight: number;
  quote: string;
}

export interface ScamInfo {
  score: number;
  band: "clear" | "check" | "red";
  reasons: ScamReason[];
}

export interface Candidate {
  id: string;
  title: string;
  org: string;
  location: string;
  pay: string | null;
  required_skills: Record<string, number>;
  source: string;
  source_url: string;
  fetched_at: string;
  is_live: boolean;
  match_score: number;
  components: MatchComponents;
  missing_skills: string[];
  reasons: string[];
  scam?: ScamInfo;
}

export interface MatchResponse {
  matches: Candidate[];
  count: number;
  live: boolean;
  live_count: number;
  seed_count: number;
  live_errors: Record<string, string>;
  provenance_note: string;
  persona: Persona;
}

export interface EvidenceResponse {
  shared_engine: {
    package: string;
    calls_by_persona: Record<string, Record<string, number>>;
    note: string;
  };
  taxonomy: { skills: number; roles: number };
  leads: { count: number; live: boolean };
}

export interface AssessState {
  theta: number;
  se: number;
  answered: [string, boolean][];
}

export interface AssessItem {
  id: string;
  skill_id: string;
  text: string;
  source: string;
}

export interface Scheme {
  id: string;
  name: string;
  description: string;
  ministry: string;
  source: string;
  source_url: string;
  fetched_at: string;
  is_live: boolean;
}

export interface EligibilityResponse {
  value: "true" | "false" | "unknown";
  reasons: string[];
  matched: string[];
  missing_fields: string[];
  needs_rule_extraction: boolean;
  source_url: string;
  fetched_at: string;
}

export interface InterviewReview {
  feedback: { area: string; quote: string; guidance: string }[];
  follow_up: string;
  word_count: number;
  star: Record<string, boolean>;
  question_source_url: string;
}

export interface PrepResponse {
  interview_date: string;
  notice_source_url: string;
  days: { day: number; focus: string; hours: number }[];
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${path} -> ${res.status}`);
  return res.json();
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`${path} -> ${res.status}`);
  return res.json();
}

export const api = {
  taxonomy: () => get<Taxonomy>("/taxonomy"),
  personas: () => get<{ personas: PersonaProfile[] }>("/personas"),
  roadmap: (req: {
    held: Record<string, number>;
    goal: string;
    demand?: Record<string, number>;
    persona?: Persona;
  }) => post<RoadmapResponse>("/roadmap", req),
  learn: (req: {
    held: Record<string, number>;
    goal: string;
    demand?: Record<string, number>;
    persona?: Persona;
    skill: string;
    level?: number;
  }) => post<LearnResponse>("/roadmap/learn", req),
  shock: (req: {
    held: Record<string, number>;
    goal: string;
    demand?: Record<string, number>;
    persona?: Persona;
    skill: string;
    weight?: number;
  }) => post<ShockResponse>("/roadmap/shock", req),
  match: (req: {
    held: Record<string, number>;
    districts?: string[];
    demand?: Record<string, number>;
    persona?: Persona;
    live?: boolean;
  }) => post<MatchResponse>("/match", req),
  evidence: () => get<EvidenceResponse>("/evidence"),
  assessNext: (req: {
    state?: AssessState;
    skill_id?: string;
    persona?: Persona;
  }) =>
    post<{ done: boolean; state: AssessState; item: AssessItem | null }>(
      "/assess/next",
      req,
    ),
  assessAnswer: (req: {
    state: AssessState;
    item_id: string;
    given_answer: string;
    persona?: Persona;
  }) =>
    post<{ correct: boolean; state: AssessState; done: boolean }>(
      "/assess/answer",
      req,
    ),
  schemes: (query: string) =>
    get<{ schemes: Scheme[]; count: number; error: string | null }>(
      `/schemes?q=${encodeURIComponent(query)}&limit=10`,
    ),
  eligibility: (req: {
    source_url: string;
    fetched_at: string;
    facts?: Record<string, unknown>;
    persona?: Persona;
  }) => post<EligibilityResponse>("/schemes/eligibility", req),
  interviewReview: (req: {
    question: string;
    transcript: string;
    question_source_url: string;
    persona?: Persona;
  }) => post<InterviewReview>("/interview/review", req),
  prep: (req: {
    interview_date: string;
    focus: string[];
    notice_source_url: string;
    persona?: Persona;
  }) => post<PrepResponse>("/prep", req),
};
