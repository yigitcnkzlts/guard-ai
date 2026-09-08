"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { DECISION_COLORS } from "@/lib/constants";
import type { Decision, SecurityEvent } from "@/lib/types";

const ORDER: Decision[] = ["ALLOW", "BLOCK", "REQUIRE_APPROVAL"];

export function DecisionChart({ events }: { events: SecurityEvent[] }) {
  const data = ORDER.map((decision) => ({
    name: decision === "REQUIRE_APPROVAL" ? "APPROVAL" : decision,
    value: events.filter((event) => event.decision === decision).length,
    color: DECISION_COLORS[decision],
  })).filter((item) => item.value > 0);

  if (data.length === 0) {
    return <p className="text-sm text-muted">No security activity yet.</p>;
  }

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" innerRadius={58} outerRadius={84} paddingAngle={3} isAnimationActive={false}>
            {data.map((entry) => (
              <Cell key={entry.name} fill={entry.color} stroke="transparent" />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: "#192129",
              border: "1px solid #29343f",
              borderRadius: 8,
              color: "#dce5ec",
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
