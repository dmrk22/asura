"use client";

import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";

/** A first-class entry point to the browser voice surface on every screen. */
export function MicButton() {
  const t = useTranslations("nav");
  return (
    <Link
      href="/voice"
      aria-label={t("mic")}
      title={t("mic")}
      className="flex h-9 w-9 items-center justify-center rounded-full border border-graphite/30 text-graphite hover:border-signal hover:text-signal"
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
    </Link>
  );
}
