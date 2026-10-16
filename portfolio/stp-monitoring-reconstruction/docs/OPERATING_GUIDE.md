# Monitoring and follow-up operating guide

## One cycle

1. Maintain stable provider, officer and round codes. Define the expected reporting roster before submissions arrive.
2. Collect five required fictional ratings and receipt metadata. Use a controlled report ID. Keep raw submissions unchanged.
3. Run validation. Whole-version defects include missing or out-of-range scores, duplicate submission IDs, wrong provider/officer, inconsistent round and impossible receipt dates. Keep an issue record and request a corrected version.
4. Review valid versions. Pick the newest approved version per report; preserve earlier versions and all drafts. A higher version number alone never authorizes publication.
5. Reconcile expected/received/approved counts and score calculations between SQL, CSV, dashboard and workbook. Separate future-due, missing and held records. Do not report a missing score as zero.
6. Prepare the management brief using the declared cutoff and selection. Explain partial coverage and the illustrative nature of ratings before interpreting a mean.
7. Assign a corrective action, fictional owner and due date. A status change is not enough: retain correction evidence and verification before accepting closure. Report overdue unresolved actions separately.
8. Archive the released snapshot, input hashes, rules, selected versions and run log. Export any browser exercise before reload.

## Roles and handover

Monitoring focal point owns the roster and form; analyst owns validation/reconciliation; reviewer owns interpretation and approval; action owner supplies correction evidence; verifier checks closure; release owner authorizes the final audience. These are workflow roles. No production authentication or role enforcement is implemented by a local SQLite file or browser button.

For handover retain the owner/backup, source locations, cutoff, expected reporting cycle, rubric, open issues/actions, selected versions, commands, output paths and restore instructions. The automated tests include a SQLite backup/restore check. Filesystem and account permissions must be configured separately for a real deployment.

## Refresh and import

Run `python src/build.py` for a full seeded rebuild. Run with `--source candidate.csv --output imported_candidate` for safe draft-only ingestion. These are manual refresh routes. No scheduled task has been installed. A future authorized scheduler could call the same command after receiving verified source inputs. A Google Sheets or Metabase connection would require its own implementation and evidence.

The Excel file is a release snapshot. It recalculates illustrative scores, review bands and closure checks, but is not a live database. Refresh source rows deliberately after a pipeline change and reconcile. Editing a workbook does not update the website automatically.

## Bangla quick guide

প্রথমে নির্ধারিত রিপোর্ট আইডি ও মনিটরিং রাউন্ড নির্বাচন করুন। পাঁচটি কাল্পনিক সূচকে ০–৪ মান দিন। মূল্যায়ন করা হয়নি—এমন ক্ষেত্রে শূন্য বসাবেন না। এই স্কোর ও মানদণ্ড শুধু অনুশীলনের জন্য; এগুলো এনএসডিএর অনুমোদিত মনিটরিং মানদণ্ড নয়।

ভুল বা অসম্পূর্ণ রিপোর্ট মুছে না দিয়ে সংশোধিত সংস্করণ দিন। নতুন খসড়া পুরোনো অনুমোদিত ফলাফল পরিবর্তন করবে না। কোনো সমস্যা সমাধান হয়েছে বললেই কাজটি বন্ধ হবে না; সংশোধনের প্রমাণ ও যাচাই দরকার। বাস্তব প্রশিক্ষণার্থী, কর্মকর্তা বা প্রতিষ্ঠানের গোপন তথ্য এই নমুনায় দেবেন না।
