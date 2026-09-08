import type { Metadata } from "next";

import { AppShell } from "@/components/layout/AppShell";
import { LocaleProvider } from "@/components/layout/LocaleProvider";
import "./globals.css";

export const metadata: Metadata = {
  title: "GUARD AI — Runtime Security for AI Agents",
  description: "Policy enforcement, human approvals and complete auditability for enterprise AI agents.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased" suppressHydrationWarning>
      <body className="min-h-full bg-background font-sans text-foreground">
        <LocaleProvider><AppShell>{children}</AppShell></LocaleProvider>
      </body>
    </html>
  );
}
