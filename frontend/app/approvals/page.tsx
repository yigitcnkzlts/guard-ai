"use client";

import { useState } from "react";
import { Check, Clock3, X } from "lucide-react";

import { ErrorState } from "@/components/ui/ErrorState";
import { TableSkeleton } from "@/components/ui/Skeleton";
import { guardApi } from "@/lib/api";
import { formatTimestamp } from "@/lib/format";
import { useGuardQuery } from "@/lib/use-guard-query";

export default function Page() {
  const approvalsQuery = useGuardQuery("approvals:pending", () => guardApi.approvals("PENDING"));
  const eventsQuery = useGuardQuery("events:approvals", () => guardApi.events({ decision: "REQUIRE_APPROVAL", limit: 200 }));
  const [busy, setBusy] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const approvals = approvalsQuery.data ?? [];
  const events = eventsQuery.data ?? [];
  const eventById = new Map(events.map(event => [event.id, event]));
  const loading = approvalsQuery.loading || eventsQuery.loading;
  const error = approvalsQuery.error ?? eventsQuery.error ?? actionError;

  const decide = async (id: string, approve: boolean) => {
    setBusy(id); setActionError(null); setMessage(null);
    try { await guardApi.decideApproval(id, approve, approve ? "Approved in GUARD console" : "Rejected in GUARD console"); await approvalsQuery.reload(); setMessage(`${id} ${approve ? "approved" : "rejected"}`); }
    catch (caught) { setActionError(caught instanceof Error ? caught.message : "Approval decision could not be recorded."); }
    finally { setBusy(null); }
  };

  return <div className="mx-auto max-w-[1000px] space-y-7">
    <header><p className="mb-2 text-sm font-medium text-amber-300">Human-in-the-loop</p><h1 className="text-3xl font-semibold tracking-tight">Approval Center</h1><p className="mt-2 text-muted">Review persisted high-risk gateway actions and record an audited decision.</p></header>
    {message ? <div role="status" className="rounded-xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-200">Decision recorded: {message}</div> : null}
    {error ? <ErrorState message={error} /> : null}
    <div className="flex items-center justify-between rounded-xl border border-border bg-surface px-5 py-4"><span className="flex items-center gap-2 text-sm"><Clock3 className="h-4 w-4 text-amber-300" />{approvals.length} requests waiting</span><button disabled={loading} onClick={() => void approvalsQuery.reload()} className="rounded-lg border border-border px-3 py-1.5 text-xs disabled:opacity-50">Refresh</button></div>
    {loading ? <TableSkeleton rows={4} /> : <div className="space-y-3">{approvals.map(approval => { const event = eventById.get(approval.security_event_id); return <article key={approval.id} className="rounded-xl border border-border bg-surface p-5"><div className="flex flex-wrap items-start justify-between gap-4"><div><div className="flex items-center gap-2"><span className="rounded-md border border-amber-400/20 bg-amber-400/10 px-2 py-1 text-xs text-amber-200">{event?.risk_level ?? "REVIEW"}</span><span className="text-xs text-muted">{approval.id.slice(0, 8)} · {formatTimestamp(approval.created_at)}</span></div><h2 className="mt-4 text-lg font-semibold">{event ? `${event.method} ${event.path}` : "Gateway action"}</h2><p className="mt-1 text-sm text-muted">{event?.reason ?? `Security event ${approval.security_event_id}`}</p><p className="mt-2 text-xs text-muted">Approvals {approval.approvals_received}/{approval.required_approvals}{approval.expires_at ? ` · Expires ${formatTimestamp(approval.expires_at)}` : ""}</p></div><div className="flex gap-2"><button disabled={busy !== null} onClick={() => void decide(approval.id, false)} className="flex items-center gap-2 rounded-lg border border-rose-400/20 px-3 py-2 text-sm text-rose-200 disabled:opacity-50"><X className="h-4 w-4" />Deny</button><button disabled={busy !== null} onClick={() => void decide(approval.id, true)} className="flex items-center gap-2 rounded-lg bg-accent px-3 py-2 text-sm font-semibold text-[#071412] disabled:opacity-50"><Check className="h-4 w-4" />{busy === approval.id ? "Saving…" : "Approve"}</button></div></div></article>; })}{approvals.length === 0 ? <div className="rounded-xl border border-border bg-surface p-12 text-center"><Check className="mx-auto h-8 w-8 text-emerald-300" /><h2 className="mt-4 font-semibold">Queue cleared</h2><p className="mt-1 text-sm text-muted">No pending approval requests.</p></div> : null}</div>}
  </div>;
}
