export const DECISION_COLORS = {
  ALLOW: "#34d399",
  BLOCK: "#f87171",
  REQUIRE_APPROVAL: "#fbbf24",
} as const;

export const RISK_COLORS = {
  LOW: "#64748b",
  MEDIUM: "#38bdf8",
  HIGH: "#fb923c",
  CRITICAL: "#f43f5e",
} as const;

export const DISPLAY_SETTINGS = {
  // Display-only values. The GUARD API does not expose runtime settings yet.
  theme: "Dark",
  gatewayMode: "Runtime Policy Gateway",
  defaultDecision: "Fail Closed (BLOCK)",
  protectedUpstream: "DemoShop API (http://localhost:8000)",
  environment: "development",
} as const;
