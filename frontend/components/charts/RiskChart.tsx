"use client";

import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { RISK_COLORS } from "@/lib/constants";
import type { RiskLevel, SecurityEvent } from "@/lib/types";

const ORDER: RiskLevel[] = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];

export function RiskChart({ events }: { events: SecurityEvent[] }) {
  const data = ORDER.map((risk) => ({
    name: risk,
    value: events.filter((event) => event.risk_level === risk).length,
    fill: RISK_COLORS[risk],
  }));

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} barSize={28}>
          <CartesianGrid stroke="#29343f" strokeOpacity={0.65} vertical={false} />
          <XAxis dataKey="name" tick={{ fill: "#97a6b4", fontSize: 12 }} axisLine={false} tickLine={false} />
          <YAxis allowDecimals={false} tick={{ fill: "#97a6b4", fontSize: 12 }} axisLine={false} tickLine={false} />
          <Tooltip
            cursor={{ fill: "rgba(255,255,255,0.03)" }}
            contentStyle={{
              background: "#192129",
              border: "1px solid #29343f",
              borderRadius: 8,
              color: "#dce5ec",
            }}
          />
          <Bar dataKey="value" radius={[4, 4, 0, 0]} isAnimationActive={false}>
            {data.map((entry) => (
              <Cell key={entry.name} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
