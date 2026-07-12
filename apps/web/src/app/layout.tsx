import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "@/lib/providers";

const geistSans = Geist({ subsets: ["latin"], variable: "--font-sans", display: "swap" });
const geistMono = Geist_Mono({ subsets: ["latin"], variable: "--font-mono", display: "swap" });

export const metadata: Metadata = {
  title: "Pulse — Aortic Surgery Intelligence",
  description:
    "Aortic & endovascular surgery intelligence — from referral to recovery. Educational demo on synthetic data.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning className={`${geistSans.variable} ${geistMono.variable}`}>
      <body className="font-sans">
        <Providers>{children}</Providers>
        <footer className="fixed bottom-0 left-0 right-0 z-50 border-t border-border/60 bg-background/80 px-4 py-1 text-center backdrop-blur-sm">
          <p className="text-xs text-muted-foreground">
            Educational demo on synthetic data — not for clinical use; not medical advice.
          </p>
        </footer>
      </body>
    </html>
  );
}
