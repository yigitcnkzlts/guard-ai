"use client";

import { DecisionBadge, RiskBadge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { agentNameById, formatTimestamp } from "@/lib/format";
import type { Agent, SecurityEvent } from "@/lib/types";

interface EventTableProps {
  events: SecurityEvent[];
  agents: Agent[];
  onSelect?: (event: SecurityEvent) => void;
}

export function EventTable({ events, agents, onSelect }: EventTableProps) {
  if (events.length === 0) {
    return (
      <EmptyState
        title="No security events"
        description="Gateway decisions will appear here as agents make requests."
      />
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-left text-sm">
        <thead className="text-[11px] uppercase tracking-wider text-muted">
          <tr>
            <th className="pb-3 pr-4 font-medium">Time</th>
            <th className="pb-3 pr-4 font-medium">Agent</th>
            <th className="pb-3 pr-4 font-medium">Method</th>
            <th className="pb-3 pr-4 font-medium">Path</th>
            <th className="pb-3 pr-4 font-medium">Decision</th>
            <th className="pb-3 pr-4 font-medium">Risk</th>
            <th className="pb-3 font-medium">Reason</th>
          </tr>
        </thead>
        <tbody>
          {events.map((event) => {
            const critical = event.decision === "BLOCK" || event.risk_level === "CRITICAL";
            return (
              <tr
                key={event.id}
                onClick={() => onSelect?.(event)}
                className={`border-t border-border/80 transition-colors ${
                  onSelect ? "cursor-pointer hover:bg-white/[0.03]" : ""
                } ${critical ? "bg-rose-500/[0.04]" : ""}`}
              >
                <td className="whitespace-nowrap py-3 pr-4 text-zinc-300">
                  {formatTimestamp(event.created_at)}
                </td>
                <td className="py-3 pr-4 text-zinc-200">{agentNameById(agents, event.agent_id)}</td>
                <td className="py-3 pr-4 font-mono text-xs text-zinc-300">{event.method}</td>
                <td className="max-w-[280px] truncate py-3 pr-4 font-mono text-xs text-zinc-300">
                  {event.path}
                </td>
                <td className="py-3 pr-4">
                  <DecisionBadge decision={event.decision} />
                </td>
                <td className="py-3 pr-4">
                  <RiskBadge risk={event.risk_level} />
                </td>
                <td className="max-w-[320px] truncate py-3 text-zinc-400">{event.reason}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
