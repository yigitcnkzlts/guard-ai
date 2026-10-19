export type Decision = "ALLOW" | "BLOCK" | "REQUIRE_APPROVAL";
export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type AgentEnvironment = "development" | "staging" | "production";

export interface Agent {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  environment: AgentEnvironment;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Policy {
  id: string;
  name: string;
  agent_id: string;
  method: string;
  path_pattern: string;
  decision: Decision;
  risk_level: RiskLevel;
  description: string;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface PolicyWrite {
  name: string;
  agent_id: string;
  method: string;
  path_pattern: string;
  decision: Decision;
  risk_level: RiskLevel;
  description: string;
  active: boolean;
  priority: number;
}

export interface SecurityEvent {
  id: string;
  agent_id: string;
  method: string;
  path: string;
  decision: Decision;
  risk_level: RiskLevel;
  matched_policy_id: string | null;
  reason: string;
  request_body: unknown;
  created_at: string;
}

export interface HealthStatus {
  status: string;
  service: string;
}

export interface SecurityEventQuery {
  decision?: Decision;
  risk_level?: RiskLevel;
  agent_id?: string;
  limit?: number;
  offset?: number;
  search?: string;
}

export type ApprovalStatus = "PENDING" | "APPROVED" | "REJECTED" | "EXPIRED";

export interface Approval {
  id: string;
  organization_id: string | null;
  security_event_id: string;
  status: ApprovalStatus;
  required_approvals: number;
  approvals_received: number;
  decided_by: string | null;
  decision_reason: string | null;
  expires_at: string | null;
  created_at: string;
}
