import type { Decision, RiskLevel } from "@/lib/types";

const decisionClass: Record<Decision, string> = {
  ALLOW: "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
  BLOCK: "border-rose-500/40 bg-rose-500/15 text-rose-300",
  REQUIRE_APPROVAL: "border-amber-500/30 bg-amber-500/10 text-amber-300",
};

const riskClass: Record<RiskLevel, string> = {
  LOW: "border-slate-500/30 bg-slate-500/10 text-slate-300",
  MEDIUM: "border-sky-500/30 bg-sky-500/10 text-sky-300",
  HIGH: "border-orange-500/30 bg-orange-500/10 text-orange-300",
  CRITICAL: "border-rose-500/50 bg-rose-500/20 text-rose-200",
};

export function DecisionBadge({ decision }: { decision: Decision }) {
  const label = decision === "REQUIRE_APPROVAL" ? "REQUIRE APPROVAL" : decision;
  return (
    <span
      className={`inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] font-semibold tracking-wide ${decisionClass[decision]}`}
    >
      {label}
    </span>
  );
}

export function RiskBadge({ risk }: { risk: RiskLevel }) {
  return (
    <span
      className={`inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] font-semibold tracking-wide ${riskClass[risk]}`}
    >
      {risk}
    </span>
  );
}

export function StatusBadge({ active }: { active: boolean }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-[11px] font-semibold tracking-wide ${
        active
          ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300"
          : "border-zinc-500/30 bg-zinc-500/10 text-zinc-400"
      }`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${active ? "bg-emerald-400" : "bg-zinc-500"}`} />
      {active ? "Active" : "Inactive"}
    </span>
  );
}
