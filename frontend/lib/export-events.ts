import { sanitizePayload } from "@/lib/format";
import type { SecurityEvent } from "@/lib/types";

export function downloadEvents(events: SecurityEvent[], filename: string) {
  const payload = {
    exported_at: new Date().toISOString(),
    count: events.length,
    events: events.map((event) => ({
      ...event,
      request_body: sanitizePayload(event.request_body),
    })),
  };
  const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
