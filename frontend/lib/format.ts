const SENSITIVE_KEY = /password|secret|token|authorization|api[_-]?key|credential/i;

export function formatTimestamp(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    return iso;
  }

  const formatted = new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).format(date);

  return formatted.replace(",", ",");
}

export function sanitizePayload(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map(sanitizePayload);
  }
  if (value && typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>).map(([key, item]) => {
      if (SENSITIVE_KEY.test(key)) {
        return [key, "***REDACTED***"];
      }
      return [key, sanitizePayload(item)];
    });
    return Object.fromEntries(entries);
  }
  return value;
}

export function agentNameById(agents: { id: string; name: string }[], agentId: string): string {
  return agents.find((agent) => agent.id === agentId)?.name ?? agentId;
}
