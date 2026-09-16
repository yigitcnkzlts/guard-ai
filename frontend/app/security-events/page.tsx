"use client";

import { useEffect, useState } from "react";

import { EventDrawer } from "@/components/events/EventDrawer";
import { EventTable } from "@/components/events/EventTable";
import { ErrorState } from "@/components/ui/ErrorState";
import { TableSkeleton } from "@/components/ui/Skeleton";
import { guardApi } from "@/lib/api";
import { downloadEvents } from "@/lib/export-events";
import type { Decision, RiskLevel } from "@/lib/types";
import { useGuardQuery } from "@/lib/use-guard-query";

const PAGE_SIZE = 50;

const DECISIONS: Array<Decision | ""> = ["", "ALLOW", "BLOCK", "REQUIRE_APPROVAL"];
const RISKS: Array<RiskLevel | ""> = ["", "LOW", "MEDIUM", "HIGH", "CRITICAL"];

export default function SecurityEventsPage() {
  const [decision, setDecision] = useState<Decision | "">("");
  const [risk, setRisk] = useState<RiskLevel | "">("");
  const [agentId, setAgentId] = useState("");
  const [search, setSearch] = useState("");
  const [appliedSearch, setAppliedSearch] = useState("");
  const [page, setPage] = useState(0);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    const initialSearch = new URLSearchParams(window.location.search).get("search")?.slice(0, 200).trim();
    if (initialSearch) queueMicrotask(() => { setSearch(initialSearch); setAppliedSearch(initialSearch); });
  }, []);

  const agentsQuery = useGuardQuery("agents", () => guardApi.agents());
  const policiesQuery = useGuardQuery("policies", () => guardApi.policies());
  const eventsQuery = useGuardQuery(JSON.stringify(["events", decision, risk, agentId, appliedSearch, page]), () =>
    guardApi.events({
      limit: PAGE_SIZE + 1,
      offset: page * PAGE_SIZE,
      search: appliedSearch || undefined,
      decision: decision || undefined,
      risk_level: risk || undefined,
      agent_id: agentId || undefined,
    }),
  );

  const loading = agentsQuery.loading || policiesQuery.loading || eventsQuery.loading;
  const error = agentsQuery.error ?? policiesQuery.error ?? eventsQuery.error;
  const agents = agentsQuery.data ?? [];
  const policies = policiesQuery.data ?? [];
  const events = eventsQuery.data ?? [];
  const visibleEvents = events.slice(0, PAGE_SIZE);
  const hasNextPage = events.length > PAGE_SIZE;
  const selected = visibleEvents.find((event) => event.id === selectedId) ?? null;
  const buttonClass = "rounded-lg border border-border px-3 py-2 text-sm text-zinc-200 hover:bg-white/5 disabled:cursor-not-allowed disabled:opacity-40";

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">Security Events</h1>
        <p className="mt-1 text-sm text-muted">Inspect every gateway decision recorded by GUARD AI.</p>
      </header>

      {error ? <ErrorState message={error} /> : null}

      <form onSubmit={(event) => { event.preventDefault(); setAppliedSearch(search.trim()); setPage(0); }} className="grid gap-3 rounded-xl border border-border bg-surface p-4 md:grid-cols-4">
        <label className="text-xs text-muted">
          Decision
          <select
            value={decision}
            onChange={(event) => { setDecision(event.target.value as Decision | ""); setPage(0); }}
            className="mt-1 w-full rounded-lg border border-border bg-[#0b0f14] px-3 py-2 text-sm text-zinc-200"
          >
            <option value="">All</option>
            {DECISIONS.filter(Boolean).map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>
        <label className="text-xs text-muted">
          Risk Level
          <select
            value={risk}
            onChange={(event) => { setRisk(event.target.value as RiskLevel | ""); setPage(0); }}
            className="mt-1 w-full rounded-lg border border-border bg-[#0b0f14] px-3 py-2 text-sm text-zinc-200"
          >
            <option value="">All</option>
            {RISKS.filter(Boolean).map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>
        <label className="text-xs text-muted">
          Agent
          <select
            value={agentId}
            onChange={(event) => { setAgentId(event.target.value); setPage(0); }}
            className="mt-1 w-full rounded-lg border border-border bg-[#0b0f14] px-3 py-2 text-sm text-zinc-200"
          >
            <option value="">All</option>
            {agents.map((agent) => (
              <option key={agent.id} value={agent.id}>
                {agent.name}
              </option>
            ))}
          </select>
        </label>
        <label className="text-xs text-muted">
          Search path or reason
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            maxLength={200}
            placeholder="/api/orders/cancel-all"
            className="mt-1 w-full rounded-lg border border-border bg-[#0b0f14] px-3 py-2 text-sm text-zinc-200"
          />
        </label>
        <div className="flex flex-wrap gap-2 md:col-span-4">
          <button type="submit" className={buttonClass}>Search all events</button>
          <button type="button" className={buttonClass} onClick={() => {
            setDecision(""); setRisk(""); setAgentId(""); setSearch(""); setAppliedSearch(""); setPage(0); setSelectedId(null);
          }}>Clear filters</button>
          <button type="button" className={buttonClass} disabled={loading} onClick={() => { void eventsQuery.reload(); }}>Refresh</button>
          <button type="button" className={buttonClass} disabled={loading || !!error || visibleEvents.length === 0} onClick={() => downloadEvents(visibleEvents, `guard-events-page-${page + 1}.json`)}>Export this page (JSON)</button>
        </div>
      </form>

      <div className="rounded-xl border border-border bg-surface p-5">
        {loading ? (
          <TableSkeleton rows={8} />
        ) : (
          <EventTable events={visibleEvents} agents={agents} onSelect={(event) => setSelectedId(event.id)} />
        )}
      </div>

      <nav aria-label="Event pagination" className="flex items-center justify-between gap-3">
        <p className="text-sm text-muted" aria-live="polite">
          Page {page + 1}{!loading && !error ? ` · ${visibleEvents.length} events` : ""}
        </p>
        <div className="flex gap-2">
          <button className={buttonClass} disabled={page === 0 || loading} onClick={() => { setSelectedId(null); setPage(page - 1); }}>Previous</button>
          <button className={buttonClass} disabled={!hasNextPage || loading || !!error} onClick={() => { setSelectedId(null); setPage(page + 1); }}>Next</button>
        </div>
      </nav>

      <EventDrawer
        event={selected}
        agents={agents}
        policies={policies}
        onClose={() => setSelectedId(null)}
      />
    </div>
  );
}
