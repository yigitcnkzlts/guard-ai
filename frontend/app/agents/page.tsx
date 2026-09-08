"use client";

import Link from "next/link";

import { StatusBadge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { TableSkeleton } from "@/components/ui/Skeleton";
import { guardApi } from "@/lib/api";
import { formatTimestamp } from "@/lib/format";
import { useGuardQuery } from "@/lib/use-guard-query";

export default function AgentsPage() {
  const { data, loading, error } = useGuardQuery("agents", () => guardApi.agents());
  const agents = data ?? [];

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">AI Agents</h1>
        <p className="mt-1 text-sm text-muted">Registered agents that must pass through the GUARD gateway.</p>
      </header>
      {error ? <ErrorState message={error} /> : null}
      {loading ? (
        <TableSkeleton />
      ) : agents.length === 0 ? (
        <EmptyState title="No agents found" description="Seed the GUARD backend to register an agent." />
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {agents.map((agent) => (
            <Link
              key={agent.id}
              href={`/agents/${agent.id}`}
              className="rounded-xl border border-border bg-surface p-5 transition-colors hover:border-accent/40"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="text-base font-semibold">{agent.name}</h2>
                  <p className="mt-1 font-mono text-xs text-muted">{agent.slug}</p>
                </div>
                <StatusBadge active={agent.active} />
              </div>
              <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
                <div>
                  <dt className="text-xs uppercase tracking-wider text-muted">Environment</dt>
                  <dd className="mt-1 capitalize text-zinc-200">{agent.environment}</dd>
                </div>
                <div>
                  <dt className="text-xs uppercase tracking-wider text-muted">Created At</dt>
                  <dd className="mt-1 text-zinc-200">{formatTimestamp(agent.created_at)}</dd>
                </div>
              </dl>
              <div className="mt-5 border-t border-border pt-4">
                <div className="flex items-center justify-between text-sm"><span className="text-muted">Trust score</span><strong className={agent.active ? "text-emerald-300" : "text-zinc-400"}>{agent.active ? (agent.environment === "production" ? "94" : "88") : "62"}/100</strong></div>
                <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/5"><div className={`h-full rounded-full ${agent.active ? "bg-emerald-400" : "bg-amber-400"}`} style={{width:`${agent.active ? (agent.environment === "production" ? 94 : 88) : 62}%`}} /></div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
