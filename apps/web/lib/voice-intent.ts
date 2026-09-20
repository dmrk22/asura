import type { RoleNode, SkillNode } from "@/lib/api";

export interface VoiceIntent {
  goal: string | null;
  held: Record<string, number>;
  district: string | null;
}

const ROLE_ALIASES: Record<string, string[]> = {
  customer_support_executive: [
    "customer support",
    "call center",
    "call centre",
  ],
  data_analyst: ["data analyst", "data analytics", "data analysis"],
  data_entry_operator: ["data entry", "data operator"],
  data_operations_associate: ["data operations", "data ops"],
  delivery_executive: ["delivery executive", "delivery job", "delivery rider"],
  delivery_operations_coordinator: [
    "delivery operations",
    "delivery coordinator",
  ],
  digital_services_assistant: ["digital services", "digital service"],
  ecommerce_delivery_associate: ["e-commerce delivery", "ecommerce delivery"],
  field_sales_executive: ["field sales", "sales executive"],
  retail_sales_associate: ["retail sales", "retail job", "shop sales"],
  warehouse_packing_associate: ["warehouse", "packing job", "packer"],
};

const SKILL_ALIASES: Record<string, string[]> = {
  basic_numeracy: ["maths", "math", "arithmetic"],
  customer_service_basic: ["customer service", "customer support"],
  data_cleaning: ["data cleaning", "data wrangling"],
  data_visualization_powerbi: ["power bi"],
  data_visualization_tableau: ["tableau"],
  digital_literacy: ["computer basics", "smartphone"],
  excel_advanced: ["advanced excel", "pivot table", "pivot tables"],
  ms_excel_basic: ["excel"],
  python_programming: ["python"],
  sql_querying: ["sql"],
};

function normalise(value: string): string {
  return value
    .normalize("NFKC")
    .toLocaleLowerCase()
    .replace(/\s+/g, " ")
    .trim();
}

function matchedTerm(text: string, terms: string[]): string | null {
  const matches = terms
    .map(normalise)
    .filter((term) => term.length > 1 && text.includes(term))
    .sort((a, b) => b.length - a.length);
  return matches[0] ?? null;
}

function detectDistrict(transcript: string): string | null {
  const match = transcript.match(
    /\b(?:in|from|near|at)\s+([A-Za-z][A-Za-z -]{1,40}?)(?=\s+(?:and|with|who|i|for|want|looking)\b|[,.]|$)/i,
  );
  return match?.[1]?.trim() || null;
}

/** A local, transparent parser: transcripts never leave the browser. */
export function parseVoiceIntent(
  transcript: string,
  roles: RoleNode[],
  skills: SkillNode[],
): VoiceIntent {
  const text = normalise(transcript);
  const rankedRoles = roles
    .map((role) => ({
      id: role.id,
      term: matchedTerm(text, [
        role.id.replaceAll("_", " "),
        role.label_en,
        role.label_te,
        role.label_hi,
        ...(ROLE_ALIASES[role.id] ?? []),
      ]),
    }))
    .filter((role): role is { id: string; term: string } => role.term !== null)
    .sort((a, b) => b.term.length - a.term.length);

  const held: Record<string, number> = {};
  for (const skill of skills) {
    const term = matchedTerm(text, [
      skill.id.replaceAll("_", " "),
      skill.label_en,
      skill.label_te,
      skill.label_hi,
      ...skill.aliases,
      ...(SKILL_ALIASES[skill.id] ?? []),
    ]);
    if (term) held[skill.id] = term.includes("advanced") ? 2 : 1;
  }

  return {
    goal: rankedRoles[0]?.id ?? null,
    held,
    district: detectDistrict(transcript),
  };
}
