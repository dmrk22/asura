import { expect, test } from "@playwright/test";
import type { RoleNode, SkillNode } from "@/lib/api";
import { parseVoiceIntent } from "@/lib/voice-intent";

const roles: RoleNode[] = [
  {
    id: "data_operations_associate",
    label_en: "Data Operations Associate",
    label_te: "డేటా ఆపరేషన్స్ అసోసియేట్",
    label_hi: "डेटा ऑपरेशंस एसोसिएट",
    required_skills: {},
    source: "test",
  },
  {
    id: "delivery_executive",
    label_en: "Delivery Executive",
    label_te: "డెలివరీ ఎగ్జిక్యూటివ్",
    label_hi: "डिलीवरी एग्जीक्यूटिव",
    required_skills: {},
    source: "test",
  },
];
const skills: SkillNode[] = [
  {
    id: "ms_excel_basic",
    label_en: "Basic MS Excel",
    label_te: "ప్రాథమిక MS ఎక్సెల్",
    label_hi: "बुनियादी एमएस एक्सेल",
    aliases: ["Excel basics", "spreadsheets"],
    level: 2,
    hours: 20,
    prereqs: [],
    source: "test",
  },
  {
    id: "sql_querying",
    label_en: "SQL querying",
    label_te: "SQL క్వెరీయింగ్",
    label_hi: "एसक्यूएल क्वेरी",
    aliases: ["SQL"],
    level: 3,
    hours: 40,
    prereqs: [],
    source: "test",
  },
];

test("voice intent turns a spoken goal and skills into a roadmap-ready profile", () => {
  expect(
    parseVoiceIntent(
      "I know Excel and SQL. I want a data operations job in Guntur.",
      roles,
      skills,
    ),
  ).toEqual({
    goal: "data_operations_associate",
    held: { ms_excel_basic: 1, sql_querying: 1 },
    district: "Guntur",
  });
});

test("voice intent recognises a practical role alias", () => {
  expect(
    parseVoiceIntent("I am looking for a delivery rider role.", roles, skills)
      .goal,
  ).toBe("delivery_executive");
});
