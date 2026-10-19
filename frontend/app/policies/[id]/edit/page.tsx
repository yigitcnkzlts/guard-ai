"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { ChevronLeft } from "lucide-react";

import { PolicyForm } from "@/components/policies/PolicyForm";
import { ErrorState } from "@/components/ui/ErrorState";
import { TableSkeleton } from "@/components/ui/Skeleton";
import { guardApi } from "@/lib/api";
import type { PolicyWrite } from "@/lib/types";
import { useGuardQuery } from "@/lib/use-guard-query";

export default function Page() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const agentsQuery = useGuardQuery("agents", () => guardApi.agents());
  const policyQuery = useGuardQuery(`policy:${id}`, () => guardApi.policy(id));
  const error = agentsQuery.error ?? policyQuery.error;
  const loading = agentsQuery.loading || policyQuery.loading;
  const policy = policyQuery.data;
  const agents = agentsQuery.data ?? [];
  const initial: PolicyWrite | null = policy ? { name: policy.name, agent_id: policy.agent_id, method: policy.method, path_pattern: policy.path_pattern, decision: policy.decision, risk_level: policy.risk_level, description: policy.description, active: policy.active, priority: 100 } : null;

  return <div className="mx-auto max-w-3xl space-y-7"><header><Link href="/policies" className="mb-5 flex items-center gap-1 text-sm text-muted"><ChevronLeft className="h-4 w-4" />Back to policies</Link><h1 className="text-3xl font-semibold tracking-tight">Edit policy</h1><p className="mt-2 text-muted">Update live Policy Engine behavior.</p></header>{error ? <ErrorState message={error} /> : loading || !initial ? <TableSkeleton rows={4} /> : <PolicyForm key={policy?.id} agents={agents} initial={initial} submitLabel="Save changes" onSubmit={async values => { await guardApi.updatePolicy(id, values); router.push("/policies"); router.refresh(); }} />}</div>;
}
