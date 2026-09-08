import type { LucideIcon } from "lucide-react";

interface MetricCardProps {
  label: string;
  value: string | number;
  hint?: string;
  icon: LucideIcon;
  tone?: "default" | "success" | "danger" | "warning";
}

const toneClass = {
  default: "text-zinc-200",
  success: "text-emerald-300",
  danger: "text-rose-300",
  warning: "text-amber-300",
};

export function MetricCard({ label, value, hint, icon: Icon, tone = "default" }: MetricCardProps) {
  return (
    <article className="rounded-xl border border-border bg-surface p-5 shadow-[0_1px_0_rgba(255,255,255,0.02)]">
      <div className="flex items-start justify-between gap-3">
        <p className="text-sm font-medium text-muted">{label}</p>
        <span className="rounded-lg bg-white/[0.035] p-2"><Icon className="h-4 w-4 text-muted" /></span>
      </div>
      <p className={`mt-4 text-3xl font-semibold tabular-nums tracking-tight ${toneClass[tone]}`}>{value}</p>
      {hint ? <p className="mt-2 text-xs text-muted">{hint}</p> : null}
    </article>
  );
}
