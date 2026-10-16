# Collection form and indicator specification

Synthetic teaching instrument. No official NSDA rubric or real institution assessment.

## Collection fields

| Field | Type / source | Validation |
|---|---|---|
| report_id | Controlled expected-report selection | Must match the roster; one provider and round per report |
| provider_id | Derived from report ID | Must match expected provider |
| officer_id | Derived from fictional assignment | Must match expected officer |
| round_date | Derived from roster | Must match the expected round |
| submitted_on | ISO date | Must be on/after the round and no later than the cutoff |
| version | Positive integer | Increases for each revision; never overwrite an original |
| infrastructure | Required integer 0–4 | No fractional/out-of-range score; missing blocks approval |
| equipment | Required integer 0–4 | Same |
| trainers | Required integer 0–4 | Same |
| records | Required integer 0–4 | Same |
| assessment_readiness | Required integer 0–4 | Same |
| decision | Draft / approved / rejected | Imports always draft; explicit simulated review needed |

Illustrative labels: 0 not observed; 1 major gaps; 2 partly ready; 3 mostly ready; 4 fully ready. “Not assessed” stays missing rather than being converted to 0. The meanings are invented for this example, and the domains are not a validated measurement scale. Scores do not determine actual compliance or accreditation.

The browser form is implemented. A Google Forms version is a configuration specification only; no Google account integration or collection deployment was created in this session. To configure it later, use the controlled roster and five required rating choices, link responses to a separate Sheet, retain version and receipt metadata, and pass export rows through validation before any approval. Do not collect actual personal identities in the demo.

## Indicators

| Indicator | Definition | Unit / denominator | Limitation |
|---|---|---|---|
| Due reporting roster | Expectations with due_date ≤ cutoff | Expected provider–round reports | Future expectations excluded |
| Receipt completeness | Due reports with a submission row / due expectations | Reports, each counted once | A physically captured row may contain invalid receipt metadata |
| Approval completeness | Due reports with latest approved valid version / due expectations | Reports | Newer draft does not replace approved data |
| On-time receipt | First recorded receipt by due date / due expectations | Reports | Invalid date is not counted as on time; synthetic revisions share receipt date |
| Illustrative score | Sum of five ratings / 20 × 100 | One approved report, 0–100 | Requires all five valid ratings; equal weights are assumptions |
| Mean displayed score | Arithmetic mean of approved valid report scores in selection | Reports, not distinct providers across rounds | One provider can contribute multiple rounds |
| Matched change | Mean of fourth-minus-first score among providers approved in both rounds | Matched providers; percentage points | Descriptive synthetic variation, not causal or operational improvement |
| Accepted closure | Status closed AND nonblank evidence AND verified | Actions | Claimed closed without proof stays unresolved |
| Overdue unresolved | Not accepted closed AND due_date < cutoff | Actions | Due today is not overdue under this rule |

Round and zone filters affect the dashboard's expected-report denominator. Review-band filters affect displayed rows and score summaries, not completeness KPIs. Four-round context and paired-change sections apply zone only, as labelled. The action tracker and frozen DQ log are separate scopes.
