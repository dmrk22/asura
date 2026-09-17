// Next.js 16 renamed the `middleware.ts` file convention to `proxy.ts`
// (function and export name change only — see node_modules/next/dist/docs/
// 01-app/03-api-reference/03-file-conventions/proxy.md). next-intl's
// createMiddleware factory is unaffected: it just returns a request handler,
// which we export here under the new `proxy` name.
import createMiddleware from "next-intl/middleware";
import { routing } from "./i18n/routing";

export const proxy = createMiddleware(routing);

export const config = {
  matcher: ["/((?!api|_next|_vercel|.*\\..*).*)"],
};
