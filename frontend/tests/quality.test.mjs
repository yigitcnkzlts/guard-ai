import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..", "..");
const read = (path) => readFile(resolve(root, path), "utf8");

test("Vercel routes API traffic before the frontend catch-all", async () => {
  const config = JSON.parse(await read("vercel.json"));
  assert.equal(config.services.backend.entrypoint, "app.main:app");
  assert.equal(config.rewrites.at(-1).destination.service, "frontend");
  assert.match(config.rewrites[0].source, /^\/api/);
});

test("production API defaults to same-origin", async () => {
  const api = await read("frontend/lib/api.ts");
  assert.match(api, /NEXT_PUBLIC_GUARD_API_URL \?\? ""/);
  assert.doesNotMatch(api, /NEXT_PUBLIC_GUARD_API_URL \?\? "http:\/\/localhost/);
});

test("public metadata endpoints and bilingual controls are present", async () => {
  const [layout, locale, robots, sitemap] = await Promise.all([
    read("frontend/app/layout.tsx"), read("frontend/components/layout/LocaleProvider.tsx"),
    read("frontend/app/robots.ts"), read("frontend/app/sitemap.ts"),
  ]);
  assert.match(layout, /metadataBase/);
  assert.match(locale, /Türkçe/);
  assert.match(locale, /English/);
  assert.match(robots, /sitemap\.xml/);
  assert.match(sitemap, /\/product/);
});

test("listed product screens disclose their purpose and live or demo status", async () => {
  const shell = await read("frontend/components/layout/AppShell.tsx");
  for (const route of [
    "/agents", "/policies", "/security-events", "/shadow-mode",
    "/investigations", "/controls", "/onboarding", "/integrations",
    "/discovery", "/policy-copilot", "/ai-analyst", "/attack-lab",
    "/compliance",
  ]) {
    assert.ok(shell.includes(`"${route}"`), `missing guidance for ${route}`);
  }
  assert.match(shell, /Canlı API verisi/);
  assert.match(shell, /Etkileşimli demo/);
  assert.match(shell, /sertifikasyon değildir/);
});
