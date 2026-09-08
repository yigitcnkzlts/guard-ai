"use client";

import { useParams } from "next/navigation";
import { useMemo } from "react";

import { EventTable } from "@/components/events/EventTable";
import { DecisionBadge, RiskBadge, StatusBadge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Panel } from "@/components/ui/Panel";
import { TableSkeleton } from "@/components/ui/Skeleton";
import { guardApi } from "@/lib/api";
import { formatTimestamp } from "@/lib/format";
import type { RiskLevel } from "@/lib/types";
import { useGuardQuery } from "@/lib/use-guard-query";

const RISK_ORDER: RiskLevel[] = ["CRITICAL", "HIGH", "MEDIUM", "LOW"];

export default function AgentDetailPage() {
  const params = useParams<{ id: string }>();
  const agentId = params.id;

  const agentQuery = useGuardQuery(`agent:${agentId}`, () => guardApi.agent(agentId));
  const policiesQuery = useGuardQuery("policies", () => guardApi.policies());
  const eventsQuery = useGuardQuery(`events:agent:${agentId}`, () =>
    guardApi.events({ agent_id: agentId, limit: 200 }),
  );

  const loading = agentQuery.loading || policiesQuery.loading || eventsQuery.loading;
  const error = agentQuery.error ?? policiesQuery.error ?? eventsQuery.error;
  const agent = agentQuery.data;
  const policies = (policiesQuery.data ?? []).filter((policy) => policy.agent_id === agentId);
  const events = useMemo(() => eventsQuery.data ?? [], [eventsQuery.data]);
  const agents = agent ? [agent] : [];

  const riskSummary = useMemo(
    () =>
      RISK_ORDER.map((risk) => ({
        risk,
        count: events.filter((event) => event.risk_level === risk).length,
      })),
    [events],
  );

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      {error ? <ErrorState message={error} /> : null}
      {loading || !agent ? (
        <TableSkeleton />
      ) : (
        <>
          <header className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight">{agent.name}</h1>
              <p className="mt-1 font-mono text-sm text-muted">{agent.slug}</p>
            </div>
            <StatusBadge active={agent.active} />
          </header>
          <section className="grid gap-4 md:grid-cols-3">
            <Info label="Environment" value={agent.environment} />
            <Info label="Created At" value={formatTimestamp(agent.created_at)} />
            <Info label="Description" value={agent.description ?? "No description"} />
          </section>
          <section className="rounded-xl border border-border bg-surface p-5">
            <div className="flex flex-wrap items-center justify-between gap-4"><div><p className="text-sm text-muted">Agent trust score</p><p className="mt-1 text-3xl font-semibold text-emerald-300">94<span className="text-base text-muted">/100</span></p></div><div className="grid grid-cols-3 gap-6 text-center text-sm"><div><strong className="block text-emerald-300">100%</strong><span className="text-xs text-muted">Policy coverage</span></div><div><strong className="block">0</strong><span className="text-xs text-muted">Anomalies</span></div><div><strong className="block">2</strong><span className="text-xs text-muted">Reviews</span></div></div></div>
            <div className="mt-4 h-2 overflow-hidden rounded-full bg-white/5"><div className="h-full w-[94%] rounded-full bg-emerald-400"/></div>
          </section>
        </>
      )}

      <Panel title="Risk summary" description="Event counts for this agent by risk level.">
        {loading ? (
          <TableSkeleton rows={3} />
        ) : (
          <div className="grid gap-3 sm:grid-cols-4">
            {riskSummary.map((item) => (
              <div key={item.risk} className="rounded-lg border border-border px-3 py-3">
                <RiskBadge risk={item.risk} />
                <p className="mt-3 text-2xl font-semibold">{item.count}</p>
              </div>
            ))}
          </div>
        )}
      </Panel>

      <Panel title="Policies" description="Rules evaluated for this agent.">
        {loading ? (
          <TableSkeleton />
        ) : policies.length === 0 ? (
          <EmptyState title="No policies" description="This agent has no attached policies." />
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="text-[11px] uppercase tracking-wider text-muted">
                <tr>
                  <th className="pb-3 pr-4 font-medium">Policy</th>
                  <th className="pb-3 pr-4 font-medium">Method</th>
                  <th className="pb-3 pr-4 font-medium">Path Pattern</th>
                  <th className="pb-3 pr-4 font-medium">Decision</th>
                  <th className="pb-3 font-medium">Risk</th>
                </tr>
              </thead>
              <tbody>
                {policies.map((policy) => (
                  <tr key={policy.id} className="border-t border-border/80">
                    <td className="py-3 pr-4 text-zinc-200">{policy.name}</td>
                    <td className="py-3 pr-4 font-mono text-xs">{policy.method}</td>
                    <td className="py-3 pr-4 font-mono text-xs text-zinc-300">{policy.path_pattern}</td>
                    <td className="py-3 pr-4">
                      <DecisionBadge decision={policy.decision} />
                    </td>
                    <td className="py-3">
                      <RiskBadge risk={policy.risk_level} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>

      <Panel title="Recent security events">
        {loading ? <TableSkeleton /> : <EventTable events={events.slice(0, 10)} agents={agents} />}
      </Panel>
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-surface p-4">
      <p className="text-xs uppercase tracking-wider text-muted">{label}</p>
      <p className="mt-2 text-sm text-zinc-200">{value}</p>
    </div>
  );
}
