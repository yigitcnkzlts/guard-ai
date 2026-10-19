"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { AlertCircle } from "lucide-react";

import type { Agent, Decision, PolicyWrite, RiskLevel } from "@/lib/types";

type Props = { agents: Agent[]; initial: PolicyWrite; submitLabel: string; onSubmit: (values: PolicyWrite) => Promise<void> };

export function PolicyForm({ agents, initial, submitLabel, onSubmit }: Props) {
  const [values, setValues] = useState(initial);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);
  const change = <K extends keyof PolicyWrite>(key: K, value: PolicyWrite[K]) => { setValues(current => ({ ...current, [key]: value })); setErrors(current => ({ ...current, [key]: "" })); };
  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const next: Record<string, string> = {};
    if (values.name.trim().length < 3) next.name = "Policy name must be at least 3 characters.";
    if (!values.path_pattern.startsWith("/")) next.path_pattern = "Path must start with /.";
    if (!values.description.trim()) next.description = "Description is required.";
    if (!values.agent_id) next.agent_id = "Select an agent.";
    setErrors(next);
    if (Object.keys(next).length > 0) return;
    setSubmitting(true); setServerError(null);
    try { await onSubmit(values); } catch (error) { setServerError(error instanceof Error ? error.message : "Policy could not be saved."); } finally { setSubmitting(false); }
  };
  return <form noValidate onSubmit={submit} className="space-y-6 rounded-xl border border-border bg-surface p-5 sm:p-6">
    {serverError ? <div role="alert" className="flex items-center gap-2 rounded-xl border border-rose-400/20 bg-rose-400/10 p-4 text-sm text-rose-100"><AlertCircle className="h-4 w-4" />{serverError}</div> : null}
    <div className="grid gap-5 sm:grid-cols-2">
      <Field id="policy-name" label="Policy name" value={values.name} error={errors.name} onChange={value => change("name", value)} />
      <Select id="agent" label="Agent" value={values.agent_id} error={errors.agent_id} onChange={value => change("agent_id", value)} options={agents.map(agent => ({ value: agent.id, label: agent.name }))} />
      <Select id="method" label="HTTP method" value={values.method} onChange={value => change("method", value)} options={["GET", "POST", "PATCH", "DELETE"].map(value => ({ value, label: value }))} />
      <Field id="path" label="Path pattern" value={values.path_pattern} error={errors.path_pattern} onChange={value => change("path_pattern", value)} />
      <Select id="decision" label="Decision" value={values.decision} onChange={value => change("decision", value as Decision)} options={["REQUIRE_APPROVAL", "ALLOW", "BLOCK"].map(value => ({ value, label: value }))} />
      <Select id="risk" label="Risk level" value={values.risk_level} onChange={value => change("risk_level", value as RiskLevel)} options={["HIGH", "CRITICAL", "MEDIUM", "LOW"].map(value => ({ value, label: value }))} />
    </div>
    <label htmlFor="description" className="block text-sm text-muted">Description<textarea id="description" value={values.description} onChange={event => change("description", event.target.value)} aria-invalid={Boolean(errors.description)} className={`mt-2 min-h-28 w-full rounded-lg border bg-background p-3 text-foreground ${errors.description ? "border-rose-400" : "border-border"}`} />{errors.description ? <span className="mt-1 block text-xs text-rose-300">{errors.description}</span> : null}</label>
    <label className="flex items-center gap-3 text-sm"><input type="checkbox" checked={values.active} onChange={event => change("active", event.target.checked)} />Policy active</label>
    <div className="flex justify-end gap-3"><Link href="/policies" className="rounded-lg border border-border px-4 py-2 text-sm">Cancel</Link><button disabled={submitting} className="rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-[#071412] disabled:opacity-50">{submitting ? "Saving…" : submitLabel}</button></div>
  </form>;
}

function Field({ id, label, value, error, onChange }: { id: string; label: string; value: string; error?: string; onChange: (value: string) => void }) { return <label htmlFor={id} className="text-sm text-muted">{label}<input id={id} value={value} onChange={event => onChange(event.target.value)} aria-invalid={Boolean(error)} className={`mt-2 w-full rounded-lg border bg-background px-3 py-2.5 text-foreground ${error ? "border-rose-400" : "border-border"}`} />{error ? <span className="mt-1 block text-xs text-rose-300">{error}</span> : null}</label>; }

function Select({ id, label, value, error, options, onChange }: { id: string; label: string; value: string; error?: string; options: Array<{ value: string; label: string }>; onChange: (value: string) => void }) { return <label htmlFor={id} className="text-sm text-muted">{label}<select id={id} value={value} onChange={event => onChange(event.target.value)} aria-invalid={Boolean(error)} className={`mt-2 w-full rounded-lg border bg-background px-3 py-2.5 text-foreground ${error ? "border-rose-400" : "border-border"}`}>{options.map(option => <option key={option.value} value={option.value}>{option.label}</option>)}</select>{error ? <span className="mt-1 block text-xs text-rose-300">{error}</span> : null}</label>; }
