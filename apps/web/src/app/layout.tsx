import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/lib/providers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Pulse — Aortic Surgery Intelligence",
  description: "Aortic & endovascular surgery intelligence — from referral to recovery. Educational demo on synthetic data.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <Providers>{children}</Providers>
        <footer className="fixed bottom-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-sm border-t border-border/50 px-4 py-1 text-center">
          <p className="text-xs text-muted-foreground">
            Educational demo on synthetic data — not for clinical use; not medical advice.
          </p>
        </footer>
      </body>
    </html>
  );
}
