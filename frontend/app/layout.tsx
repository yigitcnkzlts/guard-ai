import type { Metadata } from "next";

import { AppShell } from "@/components/layout/AppShell";
import { LocaleProvider } from "@/components/layout/LocaleProvider";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? "https://guard-ai.vercel.app"),
  title: { default: "GUARD AI — AI Ajanları İçin Çalışma Zamanı Güvenliği", template: "%s · GUARD AI" },
  description: "Kurumsal AI ajanları için politika uygulama, insan onayı ve eksiksiz denetim izi.",
  applicationName: "GUARD AI",
  keywords: ["AI security", "AI agent governance", "yapay zeka güvenliği", "runtime policy"],
  openGraph: { title: "GUARD AI", description: "AI ajanlarının her işlemini görün, yönetin ve kanıtlayın.", type: "website", locale: "tr_TR", alternateLocale: "en_US" },
  twitter: { card: "summary", title: "GUARD AI", description: "Enterprise runtime security for AI agents." },
  robots: { index: true, follow: true },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="tr" className="h-full antialiased" suppressHydrationWarning>
      <body className="min-h-full bg-background font-sans text-foreground">
        <LocaleProvider><AppShell>{children}</AppShell></LocaleProvider>
      </body>
    </html>
  );
}
