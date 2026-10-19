"use client";
import Link from "next/link";
import { Plus } from "lucide-react";

import { DecisionBadge, RiskBadge, StatusBadge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { TableSkeleton } from "@/components/ui/Skeleton";
import { guardApi } from "@/lib/api";
import { agentNameById } from "@/lib/format";
import { useGuardQuery } from "@/lib/use-guard-query";

export default function PoliciesPage() {
  const agentsQuery = useGuardQuery("agents", () => guardApi.agents());
  const policiesQuery = useGuardQuery("policies", () => guardApi.policies());
  const loading = agentsQuery.loading || policiesQuery.loading;
  const error = agentsQuery.error ?? policiesQuery.error;
  const agents = agentsQuery.data ?? [];
  const policies = policiesQuery.data ?? [];

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
        <h1 className="text-2xl font-semibold tracking-tight">Policies</h1>
        <p className="mt-1 text-sm text-muted">Create and manage rules enforced by the current policy engine.</p>
        </div><Link href="/policies/new" className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-[#071412]"><Plus className="h-4 w-4"/>Create policy</Link>
      </header>
      {error ? <ErrorState message={error} /> : null}
      {loading ? (
        <TableSkeleton />
      ) : policies.length === 0 ? (
        <EmptyState title="No policies" description="No security policies are registered yet." />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-border bg-surface p-5">
          <table className="min-w-full text-left text-sm">
            <thead className="text-[11px] uppercase tracking-wider text-muted">
              <tr>
                <th className="pb-3 pr-4 font-medium">Policy</th>
                <th className="pb-3 pr-4 font-medium">Agent</th>
                <th className="pb-3 pr-4 font-medium">Method</th>
                <th className="pb-3 pr-4 font-medium">Path Pattern</th>
                <th className="pb-3 pr-4 font-medium">Decision</th>
                <th className="pb-3 pr-4 font-medium">Risk</th>
                <th className="pb-3 font-medium">Status</th>
                <th className="pb-3 font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {policies.map((policy) => (
                <tr key={policy.id} className="border-t border-border/80">
                  <td className="py-3 pr-4 text-zinc-200">{policy.name}</td>
                  <td className="py-3 pr-4 text-zinc-300">{agentNameById(agents, policy.agent_id)}</td>
                  <td className="py-3 pr-4 font-mono text-xs">{policy.method}</td>
                  <td className="py-3 pr-4 font-mono text-xs text-zinc-300">{policy.path_pattern}</td>
                  <td className="py-3 pr-4">
                    <DecisionBadge decision={policy.decision} />
                  </td>
                  <td className="py-3 pr-4">
                    <RiskBadge risk={policy.risk_level} />
                  </td>
                  <td className="py-3">
                    <StatusBadge active={policy.active} />
                  </td>
                  <td className="py-3 text-right"><Link href={`/policies/${policy.id}/edit`} className="text-xs font-medium text-accent">Edit</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
