# Production hardening baseline

This iteration establishes the backend foundations required to turn the GUARD demo into a multi-tenant security product.

## Implemented

- Optional API-key enforcement for the runtime gateway.
- Per-agent/IP rate limiting, request-size limits, replay-safe idempotency keys, request IDs and security headers.
- Organization ownership fields for agents and security events.
- Versioned, priority-aware policies.
- Durable approval requests created for `REQUIRE_APPROVAL` decisions.
- Tamper-evident audit records linked through SHA-256 hashes.
- Explainable volume-anomaly detection primitive.
- Migration `0002` for governance tables and fields.
- Automated backend and frontend quality workflow.

## Required before a real customer deployment

- Replace in-memory rate-limit and idempotency stores with Redis or an equivalent shared store.
- Enforce organization context on every list, detail and mutation endpoint.
- Integrate an identity provider using OIDC/SAML and verify roles server-side.
- Execute approved requests through a short-lived, signed continuation token.
- Store secrets in a managed secret store; never in database fields or repository files.
- Export metrics to an observability platform and alert on gateway error rate and latency.
- Exercise backup restore, migration rollback and incident-response procedures in staging.
