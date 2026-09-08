"use client";

import { ArrowDown } from "lucide-react";

import { ErrorState } from "@/components/ui/ErrorState";
import { Panel } from "@/components/ui/Panel";
import { TableSkeleton } from "@/components/ui/Skeleton";
import { GUARD_API_URL, guardApi } from "@/lib/api";
import { DISPLAY_SETTINGS } from "@/lib/constants";
import { useGuardQuery } from "@/lib/use-guard-query";

const FLOW = ["AI Agent", "GUARD Gateway", "Policy Engine", "ALLOW / BLOCK / APPROVAL", "Company API"];

export default function GatewayPage() {
  const healthQuery = useGuardQuery("health", () => guardApi.health());
  const online = healthQuery.data?.status === "ok";

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">Gateway</h1>
        <p className="mt-1 text-sm text-muted">
          How GUARD inspects AI agent actions before they reach company APIs.
        </p>
      </header>

      {healthQuery.error ? <ErrorState message={healthQuery.error} /> : null}

      <Panel title="Request flow">
        <div className="flex flex-col items-center gap-2 py-4">
          {FLOW.map((step, index) => (
            <div key={step} className="flex w-full max-w-md flex-col items-center">
              <div className="w-full rounded-lg border border-border bg-[#0b0f14] px-4 py-3 text-center text-sm font-medium">
                {step}
              </div>
              {index < FLOW.length - 1 ? <ArrowDown className="my-2 h-4 w-4 text-muted" /> : null}
            </div>
          ))}
        </div>
      </Panel>

      <div className="grid gap-4 md:grid-cols-2">
        <Panel title="Gateway Status">
          {healthQuery.loading ? (
            <TableSkeleton rows={2} />
          ) : (
            <div className="flex items-center gap-3">
              <span className={`h-2.5 w-2.5 rounded-full ${online ? "bg-emerald-400" : "bg-rose-400"}`} />
              <span className="text-lg font-semibold">{online ? "Online" : "Offline"}</span>
            </div>
          )}
        </Panel>
        <Panel title="Control plane">
          <dl className="space-y-3 text-sm">
            <Row label="Backend URL" value={GUARD_API_URL} />
            <Row label="Environment" value={DISPLAY_SETTINGS.environment} />
            <Row label="Protected upstream" value={DISPLAY_SETTINGS.protectedUpstream} />
            <Row label="Default policy behavior" value="Fail Closed" />
          </dl>
          <p className="mt-4 text-[11px] text-muted">
            Environment and upstream labels are display-only. The GUARD API does not expose these settings yet.
          </p>
        </Panel>
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start justify-between gap-4">
      <dt className="text-muted">{label}</dt>
      <dd className="text-right text-zinc-200">{value}</dd>
    </div>
  );
}
