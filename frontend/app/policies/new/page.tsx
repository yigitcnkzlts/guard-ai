"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { ChevronLeft } from "lucide-react";

import { PolicyForm } from "@/components/policies/PolicyForm";
import { ErrorState } from "@/components/ui/ErrorState";
import { TableSkeleton } from "@/components/ui/Skeleton";
import { guardApi } from "@/lib/api";
import type { PolicyWrite } from "@/lib/types";
import { useGuardQuery } from "@/lib/use-guard-query";

export default function Page() {
  const router = useRouter();
  const agentsQuery = useGuardQuery("agents", () => guardApi.agents());
  const agents = agentsQuery.data ?? [];
  const initial: PolicyWrite = { name: "", agent_id: agents[0]?.id ?? "", method: "POST", path_pattern: "", decision: "REQUIRE_APPROVAL", risk_level: "HIGH", description: "", active: true, priority: 100 };

  return <div className="mx-auto max-w-3xl space-y-7"><header><Link href="/policies" className="mb-5 flex items-center gap-1 text-sm text-muted"><ChevronLeft className="h-4 w-4" />Back to policies</Link><h1 className="text-3xl font-semibold tracking-tight">Create policy</h1><p className="mt-2 text-muted">Create a rule used by the live Policy Engine.</p></header>{agentsQuery.error ? <ErrorState message={agentsQuery.error} /> : agentsQuery.loading ? <TableSkeleton rows={4} /> : <PolicyForm agents={agents} initial={initial} submitLabel="Create policy" onSubmit={async values => { await guardApi.createPolicy(values); router.push("/policies"); router.refresh(); }} />}</div>;
}
