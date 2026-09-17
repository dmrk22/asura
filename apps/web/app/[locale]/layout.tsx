import type { Metadata } from "next";
import {
  Geist,
  Geist_Mono,
  Instrument_Serif,
  Noto_Sans_Devanagari,
  Noto_Sans_Telugu,
  Noto_Serif_Telugu,
} from "next/font/google";
import { notFound } from "next/navigation";
import { hasLocale, NextIntlClientProvider } from "next-intl";
import { getMessages } from "next-intl/server";
import { LanguageToggle } from "@/components/LanguageToggle";
import { routing } from "@/i18n/routing";
import "../globals.css";

const geist = Geist({ variable: "--font-geist", subsets: ["latin"] });
const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});
const instrumentSerif = Instrument_Serif({
  variable: "--font-instrument-serif",
  weight: "400",
  subsets: ["latin"],
});
const notoSansTelugu = Noto_Sans_Telugu({
  variable: "--font-noto-sans-telugu",
  subsets: ["telugu"],
});
const notoSerifTelugu = Noto_Serif_Telugu({
  variable: "--font-noto-serif-telugu",
  subsets: ["telugu"],
});
const notoSansDevanagari = Noto_Sans_Devanagari({
  variable: "--font-noto-sans-devanagari",
  subsets: ["devanagari"],
});

export const metadata: Metadata = {
  title: "DAARI",
  description: "DAARI — one path engine, two worlds.",
};

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

export default async function LocaleLayout({
  children,
  params,
}: LayoutProps<"/[locale]">) {
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) {
    notFound();
  }

  const messages = await getMessages();

  return (
    <html
      lang={locale}
      className={`${geist.variable} ${geistMono.variable} ${instrumentSerif.variable} ${notoSansTelugu.variable} ${notoSerifTelugu.variable} ${notoSansDevanagari.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col bg-bone text-ink">
        <NextIntlClientProvider messages={messages}>
          <header className="flex items-center justify-end border-graphite/20 border-b px-6 py-5">
            <LanguageToggle />
          </header>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
