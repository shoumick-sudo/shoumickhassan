# STP monitoring portal — deployment and CV evidence

Built 16 October 2026 for Shoumick Hassan’s information management portfolio. This extends the existing STP monitoring reconstruction into a persistent web application.

Portal: https://stp-monitoring-portal.onrender.com/
Source: https://github.com/shoumick-sudo/shoumickhassan/tree/main/portal/stp-monitoring
Original methods and workbook: https://shoumick-humanitarian-im-evidence.snappyraven4.chatgpt.site/stp-monitoring/

## Start using it

1. Open the portal. Visitors can inspect the public monitoring workspace without signing in.
2. Choose **Create account**, using your own email and a password of at least 12 characters. Credentials are managed by Neon Auth; do not share them in chat.
3. Open **Workspace → Create private workspace**. Give it a name. It starts with fictional providers and sample monitoring records.
4. Open **Reports**, choose a provider/round and save a new draft. Reopen the record to see its version history. As workspace owner, choose **Review this version**, record a note and approve or reject it.
5. Open **Actions**, enter evidence and select **verified** before closing an action. Reopening the portal reads the saved record from Neon.
6. In **Audit**, inspect the server-recorded events. Owners can generate a one-use officer or reviewer access code under **Workspace**.

## Architecture

Render Node/Express service in Singapore; Neon PostgreSQL 18 in Singapore; managed Neon Better Auth; EdDSA JWT verification against provider JWKS. A limited database role accesses the application schema. Database credentials remain in Render’s environment and are never included in the browser bundle.

The public showcase is read-only. Private workspace access uses authenticated account IDs and membership roles. Workspace creation, reporting versions, reviews, action updates and audit events are transactional. Review decisions are final for each version; corrections use another version. Action revisions reject stale writes. Audit records are not editable through the application.

## Data and claims

All demonstration data are synthetic: 48 fictional providers, 240 expected reports across five rounds, 190 validated versions, 172 approved report baselines and 24 actions. Raw defective/duplicate records remain in the original reconstruction source. This portal seeds validated versions only. Unverified historical closed statuses are reopened; five seeded closures meet the evidence+verification rule.

The portal uses today’s UTC date when deciding which reports and actions are due. Figures therefore change with time. Monitoring scores and review bands are illustrative, not official NSDA standards.

The underlying professional duties remain applicant-confirmed historical experience. This web portal is a **new, AI-assisted portfolio reconstruction**, not an original NSDA system, UNICEF deployment or proof of measured field impact.

Suggested CV project entry:

**STP Monitoring & Corrective-Action Portal (2026)**
Built and deployed a monitoring portal using Neon PostgreSQL and Render, with versioned reporting, role-based review, evidence-verified corrective actions and persistent audit history. Public version reproduces professional workflows using synthetic sample data; developed with substantial AI assistance.

## Hosting and limits

Both resources use free plans. Render may take time to wake after inactivity. Account signup currently does not require email verification; email addresses never grant privileged access. This demonstration is for synthetic records only, with text evidence references and no file uploads. It has not been assessed for confidential operational use. There is no account-recovery or team-removal interface in this version; workspace owners can administer membership through Neon. Issued JWTs can remain valid until expiry after sign-out.

Neon project: mute-mountain-94718407
Production branch: br-fragrant-sky-a1g9315e
Development branch: br-flat-meadow-a17swzc7
Render service: srv-db939qbl550s73fnd9qg
Render dashboard: https://dashboard.render.com/web/srv-db939qbl550s73fnd9qg

Rebuild: from repository root, `cd portal/stp-monitoring && npm ci --include=dev && npm test && npm run build`; start with `npm start`. Do not reset the database on deployment. `sql/001.sql` is additive; `scripts/init.js` initializes a fresh schema/showcase with an owner connection. The service uses the separate `portal_app` role. Never copy environment secrets into Drive, GitHub or the frontend.

## Verification record

Render build checks passed all five tests with zero skips: score validation; evidence-gated closure; approved baseline stability; real Neon signup/session/JWT and a saved private draft; persistent workflows including cross-workspace denial, officer/reviewer restrictions, one-use code replay prevention, duplicate review conflict, stale action updates and audit writes.

The first live build checks found and fixed ambiguous date ordering and a UUID/text seed audit parameter mismatch. The runtime production environment omitted Vite; the deployment now explicitly includes build dependencies. Local dependency audit reports zero known production vulnerabilities. Final live page verification is recorded after rollout.

Render deployment `dep-db93ct3bc2fs73cnac6g` reached **live** on 16 October 2026 at 14:37:43 UTC. Deployed application commit: `e5d479d4a819558e6c85fc60dfd214fa8c7d894b`. The service has `NPM_CONFIG_INCLUDE=dev` so the production build includes Vite. Five tests passed against the real database with no skips; generated synthetic QA accounts and workspaces are isolated from the recruiter showcase.

Final deployed-URL smoke check: **PASS**. It exercised /health, unauthenticated denial, public write rejection, real managed signup and JWT, private workspace creation, draft persistence after reload, approval and score recalculation, rejection of an incomplete closure, evidence-verified saved closure and audit persistence. Independent Neon readback confirmed the review and action events. The public page was visually verified at https://stp-monitoring-portal.onrender.com/ . No real NSDA or applicant private data were used.

## Public presentation update — 16 October 2026

The portal uses normal product language with a persistent notice above the header: “Confidential professional records are excluded from this public portal. Synthetic sample data are used to reproduce the monitoring and follow-up workflow.”

About retains data provenance, illustrative scoring and substantial AI assistance. No original institutional deployment is claimed. The dataset is unchanged; it does not contain verified public-source records. `PORTAL_REPLICATION_GUIDE.md` documents the architecture and next portal candidates. Presentation is centralized in `client/presentation.js`.

Local verification: production frontend build and three domain tests passed; two database/authentication tests skipped locally because no connection was supplied. Deployment verification for this update is recorded separately below.
