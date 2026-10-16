# Verification — 16 October 2026

Live application commit: e5d479d4a819558e6c85fc60dfd214fa8c7d894b.
Render deployment dep-db93ct3bc2fs73cnac6g: live at 14:37:43 UTC.

All five tests passed on Render with real Neon connections and no skips:

1. Invalid, missing, out-of-range and noninteger monitoring scores rejected.
2. Closure requires both nonblank evidence and verified status.
3. A newer draft preserves the latest approved baseline; future due dates excluded.
4. Real Neon signup, session, JWT verification and persistent private draft.
5. Persistent workflow, cross-workspace denial, officer/reviewer permissions, one-use code replay rejection, repeated review conflict, stale action rejection and audit events.

A separate end-to-end test called the deployed HTTPS endpoints and passed health, unauthenticated denial, read-only showcase protection, real authentication, workspace creation, saved draft and reload, approval and 75% score recalculation, incomplete-closure rejection, verified closure and audit persistence. Independent Neon readback confirmed the review and corrective-action events after the client request completed. Synthetic QA data reside only in isolated workspaces.

The public dashboard was opened and visually checked: 192 due expectations, 172 received validated reports, 172 approved baselines, a 50.5% mean score, 19 open actions and seven overdue actions. These are synthetic records and current-date-dependent figures, not field results. The original reconstruction counts raw receipts differently; this portal seeds validated versions only.

`npm audit --omit=dev`: zero known vulnerabilities at verification. Credentials remain server-side. The production entry point never enables the verifier stub used by integration tests. The service uses limited application-schema privileges and has no DDL or managed-auth schema grants.

Live portal: https://stp-monitoring-portal.onrender.com/
