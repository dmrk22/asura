"use client";

import { useTranslations } from "next-intl";

/** Present on every screen per UI_BRIEF — inert this hour, wired in a later phase. */
export function MicButton() {
  const t = useTranslations("nav");
  return (
    <button
      type="button"
      aria-label={t("mic")}
      title={t("mic")}
      disabled
      className="flex h-9 w-9 items-center justify-center rounded-full border border-graphite/30 text-graphite disabled:cursor-not-allowed disabled:opacity-50"
    >
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.6"
        aria-hidden="true"
      >
        <rect x="9" y="2" width="6" height="12" rx="3" />
        <path d="M5 10a7 7 0 0 0 14 0" />
        <path d="M12 17v4M9 21h6" strokeLinecap="round" />
      </svg>
    </button>
  );
}
