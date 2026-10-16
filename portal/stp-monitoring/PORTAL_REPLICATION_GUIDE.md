# Portal build standard

Use the existing working STP portal as the reference implementation for future portals. Build a functioning information system with normal professional product language. Place a persistent data and confidentiality notice above the header on every screen. Keep source provenance, AI assistance and build history on About and in the repository.

## Current presentation

Product: STP Monitoring & Corrective Action. Public notice: “Confidential professional records are excluded from this public portal. Synthetic sample data are used to reproduce the monitoring and follow-up workflow.”

The public dataset is entirely synthetic. It is not a redacted export of an operational NSDA system. This 2026 application reproduces workflows informed by the owner's professional experience; deployment history and institutional endorsement must not be invented. Preserve provenance in seeds, audit history and technical records. Do not rewrite identifiers or events to imply field activity.

## Reuse map

| Component | Reuse | Adapt for each portal |
| --- | --- | --- |
| `client/presentation.js` | Central public text and disclosure | Product name, accurate data notice and provenance |
| `client/main.js`, `client/style.css` | Layout, persistent disclosure, navigation, dialogs | Domain screens, labels and metrics |
| `server/app.js` | Authentication, workspace authorization, transactional writes, access codes | Resource routes, input rules and audit events |
| `server/domain.js` | Explicit validation and stable approved baseline pattern | Domain-specific state changes and calculations |
| `sql/001.sql` | Tenant boundaries, revisions and audit pattern | Separate schema, tables and constraints |
| `server/seed.js`, `server/seed.json` | Sample initialization pattern | Purpose-built synthetic records; no confidential data |
| `tests/` | Permission, isolation, revision and persistence coverage | Domain rules and failure cases |
| `render.yaml` | Render web service configuration | Unique name, source path and secret references |

This is a reference application, not a domain-independent engine. Copying its branding does not implement a different workflow.

## Implementation sequence

1. Read the existing evidence folder and user-confirmed duties. Define the concrete original contribution and the separate new build.
2. Create a distinct source folder. Write a short brief: audience, workflow, roles, source permissions, data types, output and acceptance checks.
3. Reuse the shell and authentication patterns. Create an isolated development database branch and a separate application schema/role; do not copy production data or secrets.
4. Implement the actual domain: schema, validation, decisions, metrics, action rules and audit. Retain stable approved versions and stale-edit protection where relevant.
5. Generate realistic synthetic records and deliberate edge cases. For real public-source data, record the exact source URL, retrieval date, licence/terms, field projection and transformation. Label synthetic and public-source records separately when mixed.
6. Set `client/presentation.js` accurately. Do not claim public-source data when none is loaded, or describe synthetic data as anonymized original records.
7. Verify server-side permissions, tenant isolation, saved changes after reload, revisions, invalid inputs and key calculations. Build and inspect desktop/mobile screens.
8. Deploy to a distinct Render service using separate Neon configuration; preserve the existing service and database. Do not enable paid resources without authorization.
9. Verify the deployed workflow, document test limits and record the live URL and source commit in the application evidence folder. Keep original experience, new software and measured impact separately attributable.

## Candidate next portals

These are proposals, not completed work or claims of historical deployments. Prioritize evidence already confirmed by the owner.

| Priority | Portal | Core workflow | Distinct evidence |
| --- | --- | --- | --- |
| 1 | Assessment Results & Certification | Expected batches → upload → validate/reconcile → review → discrepancy resolution | Import quality, SQL reconciliation, exception handling |
| 2 | Skills Competition Registration | Registration → eligibility checks → deduplication → review → event roster | Form design, validation, coordination and exports |
| 3 | Training Provider Coverage & Access | Verified public provider records → geography checks → district coverage → map and gaps | GIS, spatial SQL/Python and transparent source handling |

Do not relabel the STP scoring rubric as a certification or competition process. GIS requires a real map, documented coordinate sources and a working spatial analysis. A PostgreSQL-backed table alone is not GIS evidence.

## Data notice variants

- Synthetic only: use the current STP wording.
- Verified public data only: “Confidential professional records are excluded. This public version uses publicly available data; sources and transformations are documented under About.” Use only after loading and verifying those sources.
- Mixed: state that the portal uses both public-source and synthetic sample data, with per-dataset provenance.

Maintain one prominent disclosure rather than calling every working screen a dummy or demonstration. Never promise that this hosting configuration is ready for confidential operational records without a separate assessment.
