"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  Bell,
  Bot,
  CheckCircle2,
  ClipboardList,
  FlaskConical,
  SearchCheck,
  Power,
  Plug,
  Radar,
  Rocket,
  WandSparkles,
  Bug,
  BadgeCheck,
  ChartNoAxesCombined,
  CodeXml,
  UsersRound,
  Waves,
  LifeBuoy,
  CreditCard,
  Palette,
  Presentation,
  ShieldEllipsis,
  LayoutDashboard,
  Settings,
  Shield,
  Waypoints,
  X,
} from "lucide-react";
import { BrandMark } from "@/components/brand/BrandMark";
import { useLocale } from "@/components/layout/LocaleProvider";

const NAV = [
  { href: "/", label: "Overview", tr: "Genel Bakış", icon: LayoutDashboard },
  { href: "/agents", label: "AI Agents", tr: "AI Ajanları", icon: Bot },
  { href: "/policies", label: "Policies", tr: "Politikalar", icon: Shield },
  { href: "/security-events", label: "Security Events", tr: "Güvenlik Olayları", icon: Activity },
  { href: "/shadow-mode", label: "Shadow Mode", tr: "Gölge Modu", icon: FlaskConical },
  { href: "/investigations", label: "Investigations", tr: "İncelemeler", icon: SearchCheck },
  { href: "/controls", label: "Emergency Controls", tr: "Acil Kontroller", icon: Power },
  { href: "/onboarding", label: "Quick Setup", tr: "Hızlı Kurulum", icon: Rocket },
  { href: "/integrations", label: "Integrations", tr: "Entegrasyonlar", icon: Plug },
  { href: "/discovery", label: "Agent Discovery", tr: "Ajan Keşfi", icon: Radar },
  { href: "/policy-copilot", label: "Policy Copilot", tr: "Politika Asistanı", icon: WandSparkles },
  { href: "/attack-lab", label: "Attack Lab", tr: "Saldırı Laboratuvarı", icon: Bug },
  { href: "/compliance", label: "Compliance", tr: "Uyumluluk", icon: BadgeCheck },
  { href: "/value", label: "Business Value", tr: "İş Değeri", icon: ChartNoAxesCombined },
  { href: "/developers", label: "Developers", tr: "Geliştiriciler", icon: CodeXml },
  { href: "/organization", label: "Organization", tr: "Organizasyon", icon: UsersRound },
  { href: "/anomalies", label: "Anomalies", tr: "Anomaliler", icon: Waves },
  { href: "/support", label: "Support", tr: "Destek", icon: LifeBuoy },
  { href: "/billing", label: "Plan & License", tr: "Plan ve Lisans", icon: CreditCard },
  { href: "/branding", label: "Branding", tr: "Markalama", icon: Palette },
  { href: "/trust-center", label: "Trust Center", tr: "Güven Merkezi", icon: ShieldEllipsis },
  { href: "/sales-demo", label: "Sales Demo", tr: "Satış Demosu", icon: Presentation },
  { href: "/approvals", label: "Approvals", tr: "Onaylar", icon: CheckCircle2 },
  { href: "/executive-report", label: "Executive Report", tr: "Yönetici Raporu", icon: ClipboardList },
  { href: "/audit-logs", label: "Audit Logs", tr: "Denetim Kayıtları", icon: Bell },
  { href: "/gateway", label: "Gateway", tr: "Ağ Geçidi", icon: Waypoints },
  { href: "/settings", label: "Settings", tr: "Ayarlar", icon: Settings },
];

export function Sidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  const pathname = usePathname();
  const { locale } = useLocale();

  return (
    <>
      {open ? (
        <button
          type="button"
          aria-label="Close navigation"
          className="fixed inset-0 z-30 bg-black/50 lg:hidden"
          onClick={onClose}
        />
      ) : null}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-60 flex-col border-r border-border bg-[#10161c] transition-transform duration-200 lg:static lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between border-b border-border px-5 py-6">
          <div><BrandMark /><p className="mt-2 text-xs text-muted">Agent security console</p></div>
          <button type="button" aria-label="Close navigation" className="rounded-md p-1 text-muted lg:hidden" onClick={onClose}>
            <X className="h-4 w-4" />
          </button>
        </div>
        <nav aria-label="Primary navigation" className="flex-1 space-y-1.5 overflow-y-auto px-3 py-5">
          {NAV.map((item) => {
            const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onClose}
                className={`flex min-h-10 items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                  active
                    ? "bg-accent/12 font-medium text-accent"
                    : "text-zinc-400 hover:bg-white/5 hover:text-zinc-100"
                }`}
              >
                <Icon className="h-4 w-4" />
                {locale === "tr" ? item.tr : item.label}
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-border px-5 py-4 text-xs text-muted">Runtime Gateway v0.1</div>
      </aside>
    </>
  );
}
