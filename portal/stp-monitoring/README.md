# STP Monitoring & Corrective Action

A working portal for versioned monitoring reports, reviewer approvals, corrective actions and audit history. Confidential professional records are excluded from the public portal; the current dataset is synthetic sample data.

The workflow is informed by Shoumick Hassan’s confirmed professional experience. This is a separate 2026 implementation built with substantial AI assistance, with no claim of prior institutional deployment or endorsement. Presentation settings live in `client/presentation.js`; see [PORTAL_REPLICATION_GUIDE.md](PORTAL_REPLICATION_GUIDE.md) for the build standard and reuse map.

## Workflows

- Read-only public recruiter showcase, isolated from authenticated private workspaces.
- Neon managed Better Auth email/password accounts. Account ID determines workspace membership; email never grants privileges.
- Owner, reviewer and officer roles; one-use, hashed, 24-hour access codes.
- Versioned drafts, validated integer 0–4 scores, explicit approval/rejection with a note. New drafts preserve the last approved baseline.
- Corrective actions require evidence and reviewer verification before closure. Optimistic revision checks reject stale updates.
- Audit events stored in the same transaction as the mutation.
- Parameterized SQL, tenant checks on every workspace route, EdDSA JWKS verification, rate limits and security headers.

## Run

Node 24. `npm ci`, `npm test`, `npm run build`, then `npm start` with `DATABASE_URL` and `NEON_AUTH_BASE_URL` configured. Render binds `0.0.0.0:$PORT`. Use a pooled, TLS-verified connection for `portal_app`. Never expose the database URL in a browser build.

Apply `sql/001.sql` with a direct owner connection on a development branch first. `scripts/init.js` reads one JSON line from standard input (`url`, optional `role`) and creates an idempotent showcase using `server/seed.json`. Do not place secrets in shell arguments. Use the same migration for production after validation. Runtime needs schema usage; SELECT/INSERT/UPDATE on workflow tables; SELECT/INSERT only on audit; sequence usage. No DDL or auth schema privileges.

`render.yaml` documents a reproducible deployment. The actual service uses the equivalent commands from the repository root. Integration tests run when DATABASE_URL is present, using an in-process verifier stub that is never enabled by the production entry point. They retain clearly labelled synthetic test workspaces to avoid destructive cleanup. No password, JWT or connection URL belongs in logs.

## Data

Seed copied from the validated SQLite output in `portfolio/stp-monitoring-reconstruction`. 240 expected reports, 190 validated versions, 172 approved report baselines and 24 corrective actions. Twelve defective source versions are excluded; original raw records and rules remain in that reconstruction. Five closures meet evidence+verification requirements; the remaining historical closed statuses are reopened. Portal “received” counts validated versions only and therefore differs from the original raw-receipt metric. Due reporting uses the current UTC date, so the 23 October round will eventually become due.

## Limits and handover

Demonstration deployment on free Render/Neon plans; Render may sleep when idle. No operational NSDA data, file uploads, reminders or official scoring methodology. The current account configuration allows email/password signup without email verification. No privileged role is assigned by email. Workspaces use application authorization; database credentials must remain server-side. A JWT already issued can remain valid until its expiry after sign-out. Team membership revocation and account recovery UI are not included in v2; database owners can administer membership through Neon. Do not use this demonstration for confidential operational records.

CV wording: “Developed an AI-assisted monitoring portal reconstruction using Neon Postgres and Render, demonstrating versioned reporting, role-based review, corrective-action verification and audit trails with synthetic data.” Claim a professional skills evidence project, not an official system deployment or measured field impact.
