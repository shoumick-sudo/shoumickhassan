# Operating guide and partner orientation

Independent portfolio demonstration using synthetic programme data. Not UNICEF or official response data.

## Reporting cycle

1. IM focal point maintains partner, location, indicator and expected-report master codes. For this simulation, each partner reports at each of twelve locations every month.
2. Partner enters six event-count cells per expected report. Required values are whole numbers from zero to one million. Use zero only for an actual reported zero. A missing report remains absent, not a fabricated zero.
3. Preserve the original submission and receipt metadata. Assign a stable report ID and increasing version number. Record who actually submitted and reviewed it in a real deployment; synthetic reviewer labels do not represent real people.
4. Run validation. Critical row errors block the whole report version from approved outputs. Send an issue list to the responsible partner through an authorized channel; this demonstration sends no messages.
5. Request a corrected version. Keep original rows and issue history. Record actual correction evidence and review decision. Do not mark an issue closed merely because a replacement file exists.
6. Analyst selects the latest approved version, reconciles SQL and spreadsheet totals, and drafts the narrative with missingness and unit caveats.
7. Programme lead reviews interpretation; authorized release owner approves the product and audience. Archive source hashes, cutoff, selected versions and released products. These are proposed roles for a real deployment, not implemented access controls.

The proposed routine service target is two working days for complete routine requests; emergency triage begins immediately and negotiates a delivery time based on source readiness. Never invent missing data to meet a deadline.

## Responsibility matrix

| Action | Responsible | Accountable | Consulted |
|---|---|---|---|
| Master codes and indicator definitions | IM analyst | IM coordinator | Sector focal points |
| Source report and correction | Partner focal point | Partner reporting lead | IM analyst |
| Validation and reconciliation | IM analyst | IM coordinator | Partner focal point |
| Interpretation | Sector focal point | Programme lead | IM analyst |
| External product release | Authorized release officer | Programme lead | IM coordinator |
| Account removal and handover | System administrator | System owner | IM coordinator |

## Indicator reference sheets

| Code | Meaning and unit | Numerator / denominator | Grain and interpretation |
|---|---|---|---|
| ED_ATT | Learning attendances | Sum of approved event cells / none | Partner–location–month–sex–age. Repeat attendance allowed. |
| WA_CON | WASH service contacts | Sum of approved event cells / none | Same grain. Repeat contacts allowed. |
| HE_CON | Health consultation events | Sum of approved event cells / none | Same grain. Consultations are not unique patients. |
| FAC_FUN | Functional observed facilities | Latest observed functional / latest observed known eligible facilities | Facility snapshot. Show unknown and stale separately; no current rate asserted. |
| REP_REC | Receipt completeness | Expected reports with a receipt / all due expectations | Report grain. Revisions count once. |
| REP_APP | Approval completeness | Expected reports with approved version / all due expectations | Report grain. New drafts do not displace approved versions. |
| REP_TIME | On-time receipt | Reports received by due date / all due expectations | First receipt concept; simulation receipt dates shared across versions. |
| DQ_CRIT | Critical issue flags | Count of unresolved issue records / none | Issue grain. Flags are not distinct defective rows or reports. |

Programme baseline is unavailable: this simulation has no pre-programme measurement. Targets are scenario inputs and not performance commitments. Six months must not be summed into unique people. Unknown sex is retained; no disability, refugee or child-level identities are collected. No dataset is an official indicator catalogue.

## Data protection and handover

Public release contains synthetic data only. A real deployment would separately classify public aggregates, internal operational records, restricted personal data and highly sensitive case data. Use minimum necessary fields, explicit access approval, role-specific exports, encryption and an agreed retention schedule. Do not put child-protection case records in this demonstrator. Access roles, retention periods and legal bases require the actual organization's policy; this file does not certify compliance with UNICEF requirements.

For handover, record the owner and backup, source location, indicator dictionary, expected-report roster, current cutoff and released version, open issues, scheduled updates, dependencies, restore instructions, access inventory and departing-account revocation. Rebuild the database, run the tests, compare approved report counts and document any discrepancy. The released file's checksum is in MANIFEST.sha256.

## Twenty-minute orientation design

- Minutes 0–3: explain report ID, service event versus person and missing versus zero.
- Minutes 3–8: complete the mock form for R0001. Enter six values and a version number; no real person data.
- Minutes 8–13: show a negative value, duplicate cell and missing report. Explain why the report version is held.
- Minutes 13–18: inspect the dashboard; trace one headline to SQL and the source report.
- Minutes 18–20: ask the learner to identify one limitation and one correction action.

This is a session plan, not delivered training. Record actual date, participant consent, exercise results and feedback only after a real volunteer session.

## Bangla partner quick guide

প্রতিটি মাসে নির্ধারিত রিপোর্ট আইডি ব্যবহার করুন। একই রিপোর্ট সংশোধন করলে সংস্করণ নম্বর বাড়ান। নারী, পুরুষ ও লিঙ্গ অজ্ঞাত—প্রতিটি শ্রেণিতে শিশু ও প্রাপ্তবয়স্কের সেবা-ঘটনার সংখ্যা আলাদাভাবে দিন। শিশু বলতে ১৮ বছরের কম এবং প্রাপ্তবয়স্ক বলতে ১৮ বছর বা বেশি বোঝানো হয়েছে। একজন ব্যক্তি একাধিকবার সেবা নিলে সেবা-ঘটনার সংখ্যা অনন্য ব্যক্তির সংখ্যা হবে না।

কোনো কার্যক্রম না হলে যাচাইকৃত শূন্য দিন। রিপোর্ট না পেলে শূন্য বসাবেন না। নেতিবাচক সংখ্যা, ভগ্নাংশ, ভুল লোকেশন কোড বা একই ঘরের পুনরাবৃত্তি থাকলে সংশোধিত রিপোর্ট প্রয়োজন। মূল রিপোর্ট মুছবেন না। এই অনুশীলনে সব তথ্য কৃত্রিম; বাস্তব শিক্ষার্থী, রোগী বা শরণার্থীর ব্যক্তিগত তথ্য দেবেন না।
