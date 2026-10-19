import type { SecurityEventQuery } from "@/lib/types";
import type { Agent, HealthStatus, Policy, PolicyWrite, SecurityEvent } from "@/lib/types";
import { DEMO_AGENTS, DEMO_HEALTH, DEMO_POLICIES, queryDemoEvents } from "@/lib/demo-data";

export const GUARD_API_URL =
  process.env.NEXT_PUBLIC_GUARD_API_URL ?? "";
export const DEMO_MODE_ENABLED = process.env.NEXT_PUBLIC_DEMO_MODE !== "false";

export class GuardApiError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "GuardApiError";
    this.status = status;
  }
}

function buildQuery(params: SecurityEventQuery): string {
  const search = new URLSearchParams();
  if (params.decision) search.set("decision", params.decision);
  if (params.risk_level) search.set("risk_level", params.risk_level);
  if (params.agent_id) search.set("agent_id", params.agent_id);
  if (params.limit) search.set("limit", String(params.limit));
  if (params.offset) search.set("offset", String(params.offset));
  if (params.search) search.set("search", params.search);
  const encoded = search.toString();
  return encoded ? `?${encoded}` : "";
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${GUARD_API_URL}${path}`, {
      ...init,
      headers: { Accept: "application/json", ...init.headers },
      cache: "no-store",
    });
  } catch {
    throw new GuardApiError("GUARD backend is currently unavailable.");
  }

  if (!response.ok) {
    throw new GuardApiError(
      `GUARD backend returned HTTP ${response.status}.`,
      response.status,
    );
  }

  return (await response.json()) as T;
}

export const guardApi = {
  health: () => withDemoFallback(() => request<HealthStatus>("/health"), DEMO_HEALTH),
  agents: () => withDemoFallback(() => request<Agent[]>("/api/agents"), DEMO_AGENTS),
  agent: (id: string) => withDemoFallback(
    () => request<Agent>(`/api/agents/${id}`),
    DEMO_AGENTS.find((agent) => agent.id === id) ?? DEMO_AGENTS[0],
  ),
  policies: () => withDemoFallback(() => request<Policy[]>("/api/policies"), DEMO_POLICIES),
  policy: (id: string) => withDemoFallback(
    () => request<Policy>(`/api/policies/${id}`),
    DEMO_POLICIES.find((policy) => policy.id === id) ?? DEMO_POLICIES[0],
  ),
  createPolicy: (payload: PolicyWrite) => request<Policy>("/api/policies", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }),
  updatePolicy: (id: string, payload: Partial<PolicyWrite>) => request<Policy>(`/api/policies/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }),
  events: (params: SecurityEventQuery = {}) =>
    withDemoFallback(
      () => request<SecurityEvent[]>(`/api/security-events${buildQuery(params)}`),
      queryDemoEvents(params),
    ),
};

async function withDemoFallback<T>(loader: () => Promise<T>, fallback: T): Promise<T> {
  try {
    return await loader();
  } catch (error) {
    if (!DEMO_MODE_ENABLED) throw error;
    return fallback;
  }
}
