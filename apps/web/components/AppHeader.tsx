import { useTranslations } from "next-intl";
import { LanguageToggle } from "@/components/LanguageToggle";
import { MicButton } from "@/components/MicButton";
import { Link } from "@/i18n/navigation";

/** One header, every screen. Nav + language toggle + mic — Telugu is the
 * product's feature, not the rural screen's (web.md v6). */
export function AppHeader() {
  const t = useTranslations("nav");
  return (
    <header className="flex flex-wrap items-center justify-between gap-4 border-graphite/20 border-b px-6 py-5">
      <div className="flex items-center gap-6">
        <Link
          href="/"
          className="font-ui text-sm font-semibold uppercase tracking-[0.28em] text-brand transition-colors hover:text-ink"
        >
          {t("brand")}
        </Link>
        <nav
          aria-label={t("primaryNav")}
          className="flex items-center gap-5 text-sm"
        >
          <Link href="/onboard" className="text-graphite hover:text-ink">
            {t("onboard")}
          </Link>
          <Link href="/path" className="text-graphite hover:text-ink">
            {t("path")}
          </Link>
          <Link href="/assess" className="text-graphite hover:text-ink">
            {t("assess")}
          </Link>
          <Link href="/leads" className="text-graphite hover:text-ink">
            {t("leads")}
          </Link>
          <Link href="/schemes" className="text-graphite hover:text-ink">
            {t("schemes")}
          </Link>
          <Link href="/interview" className="text-graphite hover:text-ink">
            {t("interview")}
          </Link>
          <Link href="/evidence" className="text-graphite hover:text-ink">
            {t("evidence")}
          </Link>
        </nav>
      </div>
      <div className="flex items-center gap-4">
        <MicButton />
        <LanguageToggle />
      </div>
    </header>
  );
}
