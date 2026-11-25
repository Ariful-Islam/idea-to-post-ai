import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Idea → Post",
  description: "Turn a rough idea into a ready-to-publish post.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}