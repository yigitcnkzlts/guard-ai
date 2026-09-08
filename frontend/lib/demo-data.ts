import type { Agent, HealthStatus, Policy, SecurityEvent, SecurityEventQuery } from "@/lib/types";

export const DEMO_AGENTS: Agent[] = [
  { id: "agt-support", name: "Customer Support Agent", slug: "support-agent-prod", description: "Resolves customer requests and performs approved account actions.", environment: "production", active: true, created_at: "2026-08-12T08:30:00Z", updated_at: "2026-09-08T07:12:00Z" },
  { id: "agt-finance", name: "Finance Operations Agent", slug: "finance-ops-prod", description: "Automates invoice review and payment preparation.", environment: "production", active: true, created_at: "2026-08-16T10:20:00Z", updated_at: "2026-09-08T06:45:00Z" },
  { id: "agt-devops", name: "DevOps Copilot", slug: "devops-copilot-stage", description: "Assists engineers with infrastructure diagnostics.", environment: "staging", active: true, created_at: "2026-08-24T13:10:00Z", updated_at: "2026-09-07T21:18:00Z" },
  { id: "agt-legacy", name: "Legacy Data Assistant", slug: "legacy-data-dev", description: "Migration sandbox for legacy data workflows.", environment: "development", active: false, created_at: "2026-07-29T09:00:00Z", updated_at: "2026-09-02T11:35:00Z" },
];

export const DEMO_POLICIES: Policy[] = [
  { id: "pol-1", name: "Allow customer lookup", agent_id: "agt-support", method: "GET", path_pattern: "/api/customers/*", decision: "ALLOW", risk_level: "LOW", description: "Read-only customer lookup for support cases.", active: true, created_at: "2026-08-12T09:00:00Z", updated_at: "2026-09-01T10:00:00Z" },
  { id: "pol-2", name: "Approve order cancellation", agent_id: "agt-support", method: "POST", path_pattern: "/api/orders/*/cancel", decision: "REQUIRE_APPROVAL", risk_level: "HIGH", description: "Human approval required before cancelling an order.", active: true, created_at: "2026-08-12T09:05:00Z", updated_at: "2026-09-03T12:00:00Z" },
  { id: "pol-3", name: "Block bulk deletion", agent_id: "agt-support", method: "DELETE", path_pattern: "/api/*", decision: "BLOCK", risk_level: "CRITICAL", description: "Prevents destructive deletion requests.", active: true, created_at: "2026-08-12T09:10:00Z", updated_at: "2026-09-03T12:00:00Z" },
  { id: "pol-4", name: "Allow invoice review", agent_id: "agt-finance", method: "GET", path_pattern: "/api/invoices/*", decision: "ALLOW", risk_level: "LOW", description: "Read-only access to invoice records.", active: true, created_at: "2026-08-16T11:00:00Z", updated_at: "2026-09-04T08:00:00Z" },
  { id: "pol-5", name: "Approve payment release", agent_id: "agt-finance", method: "POST", path_pattern: "/api/payments/release", decision: "REQUIRE_APPROVAL", risk_level: "CRITICAL", description: "Requires finance owner approval.", active: true, created_at: "2026-08-16T11:10:00Z", updated_at: "2026-09-04T08:10:00Z" },
  { id: "pol-6", name: "Block production mutation", agent_id: "agt-devops", method: "POST", path_pattern: "/api/infra/production/*", decision: "BLOCK", risk_level: "CRITICAL", description: "Staging agents cannot mutate production infrastructure.", active: true, created_at: "2026-08-24T14:00:00Z", updated_at: "2026-09-05T15:20:00Z" },
];

const EVENT_SEED: Array<[string, string, string, SecurityEvent["decision"], SecurityEvent["risk_level"], string, string | null]> = [
  ["agt-support", "GET", "/api/customers/C-10482", "ALLOW", "LOW", "Matched read-only customer lookup policy.", "pol-1"],
  ["agt-finance", "POST", "/api/payments/release", "REQUIRE_APPROVAL", "CRITICAL", "Payment release requires a finance owner.", "pol-5"],
  ["agt-support", "DELETE", "/api/orders/84721", "BLOCK", "CRITICAL", "Destructive operation denied by fail-closed policy.", "pol-3"],
  ["agt-devops", "GET", "/api/infra/health", "ALLOW", "LOW", "Read-only infrastructure check allowed.", null],
  ["agt-support", "POST", "/api/orders/84710/cancel", "REQUIRE_APPROVAL", "HIGH", "Order cancellation routed to human review.", "pol-2"],
  ["agt-finance", "GET", "/api/invoices/INV-2031", "ALLOW", "LOW", "Matched read-only invoice policy.", "pol-4"],
  ["agt-devops", "POST", "/api/infra/production/restart", "BLOCK", "CRITICAL", "Production mutation blocked for staging agent.", "pol-6"],
  ["agt-support", "GET", "/api/customers/C-10477", "ALLOW", "LOW", "Matched read-only customer lookup policy.", "pol-1"],
  ["agt-finance", "GET", "/api/invoices/INV-2028", "ALLOW", "LOW", "Matched read-only invoice policy.", "pol-4"],
  ["agt-support", "POST", "/api/orders/84692/cancel", "REQUIRE_APPROVAL", "HIGH", "Order cancellation routed to human review.", "pol-2"],
  ["agt-devops", "GET", "/api/infra/deployments", "ALLOW", "MEDIUM", "Deployment metadata access allowed.", null],
  ["agt-support", "PATCH", "/api/customers/C-10461/profile", "BLOCK", "HIGH", "No matching write policy; fail-closed decision applied.", null],
];

export const DEMO_EVENTS: SecurityEvent[] = EVENT_SEED.map((item, index) => ({
  id: `evt-${12048 - index}`,
  agent_id: item[0],
  method: item[1],
  path: item[2],
  decision: item[3],
  risk_level: item[4],
  reason: item[5],
  matched_policy_id: item[6],
  request_body: null,
  created_at: new Date(Date.UTC(2026, 8, 8, 9, 42 - index * 3)).toISOString(),
}));

export const DEMO_HEALTH: HealthStatus = { status: "ok", service: "guard-demo" };

export function queryDemoEvents(params: SecurityEventQuery = {}): SecurityEvent[] {
  const search = params.search?.toLowerCase();
  const filtered = DEMO_EVENTS.filter((event) =>
    (!params.decision || event.decision === params.decision) &&
    (!params.risk_level || event.risk_level === params.risk_level) &&
    (!params.agent_id || event.agent_id === params.agent_id) &&
    (!search || event.path.toLowerCase().includes(search) || event.reason.toLowerCase().includes(search)),
  );
  const offset = params.offset ?? 0;
  return filtered.slice(offset, offset + (params.limit ?? filtered.length));
}
