import { getLocale, getTranslations } from "next-intl/server";

export default async function Home() {
  const locale = await getLocale();
  const t = await getTranslations("brand");

  const isTelugu = locale === "te";
  const isDevanagari = locale === "hi";

  const wordmarkFont = isTelugu ? "font-telugu-serif" : "font-display";
  const statusFont = isTelugu
    ? "font-telugu-sans"
    : isDevanagari
      ? "font-devanagari-sans"
      : "font-mono";

  return (
    <main className="flex flex-1 flex-col items-start justify-center gap-6 px-6 py-16 sm:px-16">
      <h1
        className={`${wordmarkFont} text-[clamp(3.5rem,12vw,8rem)] leading-none text-ink`}
      >
        {t("wordmark")}
      </h1>
      <div aria-hidden="true" className="h-px w-16 bg-graphite" />
      <p
        className={`${statusFont} flex items-center gap-2 text-graphite text-lg`}
      >
        <span
          aria-hidden="true"
          className="inline-block h-2 w-2 rounded-full bg-sage"
        />
        {t("status")}
      </p>
    </main>
  );
}
