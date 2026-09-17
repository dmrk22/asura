import type { Metadata } from "next";
import "../styles/tokens.css";

export const metadata: Metadata = {
  title: "NADI",
  description: "One agent for your whole day. Five engines, every answer traceable.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
