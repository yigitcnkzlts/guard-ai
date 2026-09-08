"use client";

import {
  Activity,
  Ban,
  Bot,
  ClipboardCheck,
  ShieldAlert,
  ShieldCheck,
  Siren,
} from "lucide-react";
import dynamic from "next/dynamic";

import { EventTable } from "@/components/events/EventTable";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { MetricCard } from "@/components/ui/MetricCard";
import { MetricSkeleton, TableSkeleton } from "@/components/ui/Skeleton";
import { Panel } from "@/components/ui/Panel";
import { guardApi } from "@/lib/api";
import { useGuardQuery } from "@/lib/use-guard-query";

const DecisionChart = dynamic(() => import("@/components/charts/DecisionChart").then((module) => module.DecisionChart), { loading: () => <TableSkeleton rows={4}/> });
const RiskChart = dynamic(() => import("@/components/charts/RiskChart").then((module) => module.RiskChart), { loading: () => <TableSkeleton rows={4}/> });

export default function OverviewPage() {
  const agentsQuery = useGuardQuery("agents", () => guardApi.agents());
  const eventsQuery = useGuardQuery("events:overview", () => guardApi.events({ limit: 200 }));

  const loading = agentsQuery.loading || eventsQuery.loading;
  const error = agentsQuery.error ?? eventsQuery.error;
  const agents = agentsQuery.data ?? [];
  const events = eventsQuery.data ?? [];

  const allowed = events.filter((event) => event.decision === "ALLOW").length;
  const blocked = events.filter((event) => event.decision === "BLOCK").length;
  const approval = events.filter((event) => event.decision === "REQUIRE_APPROVAL").length;
  const critical = events.filter((event) => event.risk_level === "CRITICAL").length;

  return (
    <div className="mx-auto max-w-[1180px] space-y-7">
      <header>
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="mb-2 text-sm font-medium text-accent">Runtime protection</p>
            <h1 className="text-3xl font-semibold tracking-tight">Security Overview</h1>
          </div>
          <div className="flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 text-sm text-emerald-200">
            <Activity className="h-4 w-4" />
            All controls operational
          </div>
        </div>
        <p className="mt-2 max-w-2xl text-base text-muted">
          Real-time policy enforcement for every AI agent action across your organization.
        </p>
      </header>

      {error ? <ErrorState message={error} onRetry={() => { void agentsQuery.reload(); void eventsQuery.reload(); }} /> : null}

      <section aria-label="Security metrics" className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {loading ? (
          Array.from({ length: 6 }).map((_, index) => <MetricSkeleton key={index} />)
        ) : (
          <>
            <MetricCard label="Protected Agents" value={agents.length} icon={Bot} />
            <MetricCard label="Total Security Events" value={events.length} icon={ShieldCheck} />
            <MetricCard label="Allowed" value={allowed} icon={ClipboardCheck} tone="success" />
            <MetricCard label="Blocked" value={blocked} icon={Ban} tone="danger" />
            <MetricCard label="Approval Required" value={approval} icon={ShieldAlert} tone="warning" />
            <MetricCard label="Critical Risks" value={critical} icon={Siren} tone="danger" />
          </>
        )}
      </section>

      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="Security Activity" description="Decision distribution across observed events.">
          {loading ? <TableSkeleton rows={4} /> : <DecisionChart events={events} />}
        </Panel>
        <Panel title="Risk Distribution" description="Risk levels assigned by the policy engine.">
          {loading ? <TableSkeleton rows={4} /> : <RiskChart events={events} />}
        </Panel>
      </div>

      <Panel title="Recent Security Events" description="Latest gateway decisions.">
        {loading ? (
          <TableSkeleton />
        ) : events.length === 0 ? (
          <EmptyState
            title="No recent events"
            description="Execute a request through GUARD to populate this feed."
          />
        ) : (
          <EventTable events={events.slice(0, 10)} agents={agents} />
        )}
      </Panel>
    </div>
  );
}
