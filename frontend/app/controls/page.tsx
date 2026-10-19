"use client";

import { useState } from "react";
import { AlertTriangle, Lock, Power, ShieldAlert } from "lucide-react";

import { ErrorState } from "@/components/ui/ErrorState";
import { TableSkeleton } from "@/components/ui/Skeleton";
import { guardApi } from "@/lib/api";
import { useGuardQuery } from "@/lib/use-guard-query";

export default function Page() {
  const agentsQuery = useGuardQuery("agents", () => guardApi.agents());
  const [confirm, setConfirm] = useState(false);
  const [busy, setBusy] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const agents = agentsQuery.data ?? [];
  const locked = agents.length > 0 && agents.every(agent => !agent.active);
  const pausedCount = agents.filter(agent => !agent.active).length;

  const setAgentStatus = async (id: string, active: boolean) => {
    setBusy(id); setActionError(null);
    try { await guardApi.updateAgentStatus(id, active); await agentsQuery.reload(); }
    catch (error) { setActionError(error instanceof Error ? error.message : "Agent status could not be updated."); }
    finally { setBusy(null); }
  };

  const setAllStatus = async (active: boolean) => {
    setBusy("all"); setActionError(null);
    try { await guardApi.setAllAgentStatus(active); await agentsQuery.reload(); setConfirm(false); }
    catch (error) { setActionError(error instanceof Error ? error.message : "Emergency control could not be applied."); }
    finally { setBusy(null); }
  };

  return <div className="mx-auto max-w-[1050px] space-y-7">
    <header><p className="mb-2 flex items-center gap-2 text-sm font-medium text-rose-300"><ShieldAlert className="h-4 w-4" />Privileged operations</p><h1 className="text-3xl font-semibold tracking-tight">Emergency Controls</h1><p className="mt-2 max-w-2xl text-muted">Pause agents or block the entire registered fleet. Changes are persisted and enforced by the gateway.</p></header>
    {actionError ? <ErrorState message={actionError} /> : null}
    {locked ? <div className="flex gap-3 rounded-xl border border-rose-400/30 bg-rose-400/10 p-4 text-rose-100"><Lock className="h-5 w-5" /><div><strong>Emergency lockdown active</strong><p className="mt-1 text-sm text-rose-100/70">All registered agents are inactive and their gateway requests are blocked.</p></div></div> : null}
    {agentsQuery.error ? <ErrorState message={agentsQuery.error} /> : agentsQuery.loading ? <TableSkeleton rows={4} /> : <section className="rounded-xl border border-border bg-surface"><header className="flex items-center justify-between border-b border-border p-5"><div><h2 className="font-semibold">Agent isolation</h2><p className="mt-1 text-sm text-muted">Pause one agent without affecting the rest of the fleet.</p></div><span className="text-xs text-muted">{pausedCount} paused</span></header>{agents.map(agent => <div key={agent.id} className="flex items-center justify-between border-b border-border/70 p-5 last:border-0"><div><strong className="text-sm">{agent.name}</strong><p className="mt-1 text-xs text-muted">{agent.environment} · {agent.active ? "Gateway access active" : "Gateway access blocked"}</p></div><button disabled={busy !== null} onClick={() => void setAgentStatus(agent.id, !agent.active)} className={`rounded-lg border px-3 py-2 text-sm disabled:opacity-50 ${agent.active ? "border-border text-zinc-300" : "border-emerald-400/20 text-emerald-300"}`}>{busy === agent.id ? "Saving…" : agent.active ? "Pause agent" : "Resume"}</button></div>)}</section>}
    <section className="rounded-xl border border-rose-500/25 bg-rose-500/[.04] p-6"><div className="flex flex-wrap items-center justify-between gap-5"><div className="flex gap-4"><span className="grid h-11 w-11 place-items-center rounded-xl bg-rose-500/10 text-rose-300"><Power className="h-5 w-5" /></span><div><h2 className="font-semibold text-rose-100">Emergency lockdown</h2><p className="mt-1 max-w-xl text-sm text-muted">Persistently disable every registered agent and block new gateway actions.</p></div></div>{locked ? <button disabled={busy !== null} onClick={() => void setAllStatus(true)} className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50">{busy === "all" ? "Saving…" : "Resume all agents"}</button> : <button disabled={busy !== null || agents.length === 0} onClick={() => setConfirm(true)} className="rounded-lg bg-rose-500 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50">Activate lockdown</button>}</div></section>
    {confirm && !locked ? <div className="fixed inset-0 z-50 grid place-items-center bg-black/70 p-4"><div role="dialog" aria-modal="true" aria-labelledby="lockdown-title" className="w-full max-w-md rounded-2xl border border-rose-400/30 bg-surface p-6 shadow-2xl"><AlertTriangle className="h-7 w-7 text-rose-300" /><h2 id="lockdown-title" className="mt-4 text-xl font-semibold">Activate emergency lockdown?</h2><p className="mt-2 text-sm text-muted">Every registered agent will be disabled. Gateway requests will be blocked and the decision will be written to the audit log.</p><div className="mt-6 flex justify-end gap-3"><button onClick={() => setConfirm(false)} className="rounded-lg border border-border px-4 py-2 text-sm">Cancel</button><button disabled={busy !== null} onClick={() => void setAllStatus(false)} className="rounded-lg bg-rose-500 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50">Confirm lockdown</button></div></div></div> : null}
  </div>;
}
