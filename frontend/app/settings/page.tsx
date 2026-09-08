"use client";

import { Panel } from "@/components/ui/Panel";
import { GUARD_API_URL } from "@/lib/api";
import { DISPLAY_SETTINGS } from "@/lib/constants";

export default function SettingsPage() {
  const rows = [
    { label: "GUARD API URL", value: GUARD_API_URL },
    { label: "Environment", value: DISPLAY_SETTINGS.environment },
    { label: "Theme", value: DISPLAY_SETTINGS.theme },
    { label: "Gateway Mode", value: DISPLAY_SETTINGS.gatewayMode },
    { label: "Default Decision", value: DISPLAY_SETTINGS.defaultDecision },
  ];

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="mt-1 text-sm text-muted">Read-only control-plane information for this deployment.</p>
      </header>
      <Panel title="Platform" description="Settings CRUD is not enabled in this version.">
        <dl className="divide-y divide-border">
          {rows.map((row) => (
            <div key={row.label} className="flex items-start justify-between gap-4 py-3 text-sm">
              <dt className="text-muted">{row.label}</dt>
              <dd className="text-right text-zinc-200">{row.value}</dd>
            </div>
          ))}
        </dl>
        <p className="mt-4 text-[11px] text-muted">
          Theme, gateway mode, and default decision are display-only constants. GUARD API URL is read from
          NEXT_PUBLIC_GUARD_API_URL.
        </p>
      </Panel>
    </div>
  );
}
