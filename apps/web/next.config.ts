import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./i18n/request.ts");

const nextConfig: NextConfig = {
  // The Next.js development-tools bubble is useful while building but is
  // visual noise in a product demo. Runtime errors still surface normally.
  devIndicators: false,
  // Same-origin proxy to the daari API: the browser calls `/api-proxy/*`
  // (no CORS involved, since it never leaves this origin) and the Next
  // server forwards it. `daari.main` doesn't ship a CORS middleware and
  // apps/api is another builder's lane — proxying is the apps/web-only fix.
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    return [{ source: "/api-proxy/:path*", destination: `${apiUrl}/:path*` }];
  },
};

export default withNextIntl(nextConfig);
