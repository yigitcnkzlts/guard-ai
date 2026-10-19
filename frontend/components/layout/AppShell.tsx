"use client";

import { useState } from "react";
import { Menu } from "lucide-react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { Bell } from "lucide-react";

import { Sidebar } from "@/components/layout/Sidebar";
import { DEMO_MODE_ENABLED } from "@/lib/api";
import { LanguageSwitch } from "@/components/layout/LocaleProvider";
import { ProductTools } from "@/components/layout/ProductTools";

const SCREEN_GUIDANCE: Record<string, { purpose: string; status: string }> = {
  "/agents": { purpose: "Gateway tarafından korunan ajanları ve durumlarını gösterir.", status: "Canlı API verisi" },
  "/policies": { purpose: "Policy Engine tarafından uygulanan kuralları gösterir.", status: "Canlı, salt okunur API verisi" },
  "/security-events": { purpose: "Gateway kararlarını arar, filtreler, inceler ve dışa aktarır.", status: "Canlı API verisi" },
  "/shadow-mode": { purpose: "Trafiği engellemeden önerilen kontrollerin etkisini gösterir.", status: "Etkileşimli demo" },
  "/investigations": { purpose: "Bir kararın kullanıcı niyetinden policy sonucuna kadar izini açıklar.", status: "Örnek olay simülasyonu" },
  "/controls": { purpose: "Ajan duraklatma ve acil kilitleme davranışını gösterir.", status: "Güvenli demo; canlı sistem değişmez" },
  "/onboarding": { purpose: "İlk ajan entegrasyonu için örnek kurulum adımlarını gösterir.", status: "Yönlendirmeli demo" },
  "/integrations": { purpose: "Ajan, onay, SIEM ve gözlemleme bağlantılarını listeler.", status: "Demo katalog; bağlantılar kalıcı değildir" },
  "/discovery": { purpose: "Ajanların araçlar ve korunan sistemlerle ilişkisini görselleştirir.", status: "Örnek erişim haritası" },
  "/policy-copilot": { purpose: "Doğal dildeki kuralı açıklanabilir policy taslağına dönüştürür.", status: "Deterministik demo; taslak yayınlanmaz" },
  "/ai-analyst": { purpose: "Güvenlik olaylarını kanıt kayıtlarıyla özetler.", status: "API olayları üzerinde çalışan kural tabanlı analiz" },
  "/attack-lab": { purpose: "Yaygın ajan saldırılarının nasıl engelleneceğini simüle eder.", status: "İzole simülasyon" },
  "/compliance": { purpose: "Kanıt türlerini güvenlik ve mevzuat kontrolleriyle eşler.", status: "Örnek skorlar; sertifikasyon değildir" },
};

export function AppShell({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const screenGuidance = SCREEN_GUIDANCE[pathname];
  if (pathname === "/login" || pathname === "/product") return <>{children}</>;

  return (
    <div className="flex min-h-screen bg-background">
      <a href="#main-content" className="skip-link">Skip to content</a>
      <Sidebar open={open} onClose={() => setOpen(false)} />
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 flex items-center gap-3 border-b border-border bg-surface/90 px-4 py-3 backdrop-blur lg:hidden">
          <button type="button" aria-label="Open navigation" onClick={() => setOpen(true)} className="rounded-md p-1 text-zinc-300">
            <Menu className="h-5 w-5" />
          </button>
          <span className="text-sm font-semibold">GUARD AI</span>
          <Link href="/audit-logs" aria-label="Notifications" className="ml-auto rounded-md p-1 text-muted"><Bell className="h-4 w-4"/></Link>
          <LanguageSwitch />
        </header>
        <div className="hidden h-14 items-center justify-end gap-3 border-b border-border px-10 lg:flex">
          <ProductTools />
          <Link href="/audit-logs" aria-label="Notifications" className="relative rounded-lg border border-border p-2 text-muted hover:text-foreground"><Bell className="h-4 w-4"/><span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-accent"/></Link>
          <LanguageSwitch />
          {DEMO_MODE_ENABLED ? <DemoBadge /> : null}
        </div>
        {DEMO_MODE_ENABLED ? <div className="border-b border-sky-400/15 bg-sky-400/[.05] px-4 py-2 text-center text-xs text-sky-200 lg:hidden" role="status">Demo workspace · No live systems are changed</div> : null}
        {screenGuidance ? (
          <div className="border-b border-border bg-white/[.02] px-4 py-2 text-xs text-muted sm:px-7 lg:px-10" role="note">
            <span className="font-medium text-zinc-200">{screenGuidance.status}</span>
            <span aria-hidden="true"> · </span>
            {screenGuidance.purpose}
          </div>
        ) : null}
        <main id="main-content" tabIndex={-1} className="flex-1 px-4 py-6 sm:px-7 lg:px-10 lg:py-8">{children}</main>
      </div>
    </div>
  );
}

function DemoBadge() {
  return (
    <span className="ml-auto inline-flex items-center gap-2 rounded-full border border-sky-400/20 bg-sky-400/10 px-3 py-1 text-xs font-medium text-sky-200">
      <span className="h-1.5 w-1.5 rounded-full bg-sky-300" />
      Demo workspace · Safe data
    </span>
  );
}
