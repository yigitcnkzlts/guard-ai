"use client";

import { X } from "lucide-react";

import { DecisionBadge, RiskBadge } from "@/components/ui/Badge";
import { downloadEvents } from "@/lib/export-events";
import { agentNameById, formatTimestamp, sanitizePayload } from "@/lib/format";
import type { Agent, Policy, SecurityEvent } from "@/lib/types";

interface EventDrawerProps {
  event: SecurityEvent | null;
  agents: Agent[];
  policies: Policy[];
  onClose: () => void;
}

export function EventDrawer({ event, agents, policies, onClose }: EventDrawerProps) {
  if (!event) {
    return null;
  }

  const policy = policies.find((item) => item.id === event.matched_policy_id);
  const body = sanitizePayload(event.request_body);

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <button type="button" className="absolute inset-0 bg-black/50" onClick={onClose} aria-label="Close details" />
      <aside className="relative h-full w-full max-w-md overflow-y-auto border-l border-border bg-[#10161d] p-6 shadow-2xl">
        <div className="mb-6 flex items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-wider text-muted">Security Event</p>
            <h2 className="mt-1 text-lg font-semibold">Request details</h2>
          </div>
          <button type="button" onClick={onClose} className="text-muted hover:text-zinc-100">
            <X className="h-4 w-4" />
          </button>
        </div>
        <dl className="space-y-4 text-sm">
          <Row label="Event ID" value={event.id} mono />
          <Row label="Agent" value={agentNameById(agents, event.agent_id)} />
          <Row label="Method" value={event.method} mono />
          <Row label="Path" value={event.path} mono />
          <div>
            <dt className="text-xs uppercase tracking-wider text-muted">Decision</dt>
            <dd className="mt-1">
              <DecisionBadge decision={event.decision} />
            </dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wider text-muted">Risk</dt>
            <dd className="mt-1">
              <RiskBadge risk={event.risk_level} />
            </dd>
          </div>
          <Row label="Reason" value={event.reason} />
          <Row label="Matched Policy" value={policy?.name ?? "No matching policy"} />
          <Row label="Timestamp" value={formatTimestamp(event.created_at)} />
          <div>
            <dt className="text-xs uppercase tracking-wider text-muted">Request Body</dt>
            <dd className="mt-2 overflow-x-auto rounded-lg border border-border bg-black/30 p-3 font-mono text-xs text-zinc-300">
              {body == null ? "null" : JSON.stringify(body, null, 2)}
            </dd>
          </div>
        </dl>
        <button type="button" onClick={() => downloadEvents([event], `guard-event-${event.id}.json`)} className="mt-6 rounded-lg border border-border px-3 py-2 text-sm hover:bg-white/5">
          Export event (JSON)
        </button>
      </aside>
    </div>
  );
}

function Row({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-wider text-muted">{label}</dt>
      <dd className={`mt-1 text-zinc-200 ${mono ? "font-mono text-xs" : ""}`}>{value}</dd>
    </div>
  );
}
