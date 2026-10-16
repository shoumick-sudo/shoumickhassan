"""Standalone fictional information-management and assessment QA demonstration.

Run: python portfolio/unicef-im-projects/qa_examples.py
All rows are invented teaching examples (16 October 2026), not NSDA/UNICEF records.
Prepared with AI assistance. Applicant independent execution/explanation must be checked.
"""
from collections import Counter, defaultdict

PROVIDERS = [
    ("P01", "Group-A", "Active"), ("P02", "Group-A", "Active"),
    ("P03", "Group-B", "Active"), ("P04", "Group-A", "Inactive"),
    ("P05", "Group-B", "Active"), ("P06", "Group-B", "Active"),
    ("P07", "Group-A", "Active"), ("P08", "Group-B", "Active"),
]

# course_id, provider_id, accredited? Duplicated CR12 and missing provider P99 are intentional.
COURSES = [
    ("CR01", "P01", True), ("CR02", "P01", True),
    ("CR03", "P01", False), ("CR04", "P02", True),
    ("CR05", "P02", True), ("CR06", "P03", False),
    ("CR07", "P03", True), ("CR08", "P04", True),
    ("CR09", "P05", True), ("CR10", "P06", True),
    ("CR11", "P06", False), ("CR12", "P07", True),
    ("CR12", "P07", True), ("CR14", "P99", True),
]

# candidate_id, skill, correct, wrong, blank: all IDs/answers are fictional.
RESPONSES = [
    ("C001", "S1", 17, 2, 1), ("C002", "S1", 14, 4, 2),
    ("C003", "S1", 18, 2, 0), ("C004", "S1", 10, 5, 5),
    ("C005", "S1", 16, 2, 2), ("C005", "S1", 15, 2, 3),
    ("C007", "S2", 13, 5, 2), ("C008", "S2", 19, 1, 0),
    ("C009", "S2", 11, 6, 3), ("C010", "S2", 20, 0, 0),
    ("C011", "S2", 12, 3, 5), ("C012", "S2", 12, 4, 5),
]


def registry_report():
    providers = {pid: (group, status) for pid, group, status in PROVIDERS}
    course_ids = Counter(course_id for course_id, _, _ in COURSES)
    provider_count = defaultdict(int)
    active_count = defaultdict(int)
    raw_accredited = defaultdict(int)
    reviewed_accredited = defaultdict(set)
    flags = []

    for pid, group, status in PROVIDERS:
        provider_count[group] += 1
        active_count[group] += status == "Active"

    for course_id, provider_id, accredited in COURSES:
        if course_ids[course_id] > 1:
            flags.append((course_id, "DUPLICATE_ID"))
        elif provider_id not in providers:
            flags.append((course_id, "ORPHAN_PROVIDER"))
        if provider_id not in providers:
            continue
        group = providers[provider_id][0]
        raw_accredited[group] += bool(accredited)
        if accredited and course_ids[course_id] == 1:
            reviewed_accredited[group].add(course_id)

    summary = {
        group: (provider_count[group], active_count[group],
                raw_accredited[group], len(reviewed_accredited[group]))
        for group in sorted(provider_count)
    }
    assert summary == {
        "Group-A": (4, 3, 7, 5),
        "Group-B": (4, 4, 3, 3),
    }, summary
    assert Counter(reason for _, reason in flags) == {
        "DUPLICATE_ID": 2, "ORPHAN_PROVIDER": 1
    }
    return summary, flags


def scoring_report():
    ids = Counter(row[0] for row in RESPONSES)
    scores = defaultdict(list)
    flags = defaultdict(list)
    for candidate, skill, correct, wrong, blank in RESPONSES:
        if correct + wrong + blank != 20:
            flags[skill].append((candidate, "COUNT_MISMATCH"))
        elif ids[candidate] > 1:
            flags[skill].append((candidate, "DUPLICATE_ID"))
        elif min(correct, wrong, blank) < 0:
            flags[skill].append((candidate, "NEGATIVE_INPUT"))
        else:
            scores[skill].append((candidate, correct - 0.25 * wrong))

    report = {}
    for skill in sorted(set(row[1] for row in RESPONSES)):
        valid = scores[skill]
        report[skill] = (len(valid), len(flags[skill]),
                         max(score for _, score in valid),
                         sum(score for _, score in valid) / len(valid))
    assert report == {
        "S1": (4, 2, 17.5, 13.9375),
        "S2": (5, 1, 20.0, 14.25),
    }, report
    return report, flags


if __name__ == "__main__":
    registry, bad_courses = registry_report()
    scores, bad_scores = scoring_report()
    print("FICTIONAL PROVIDER REPORT (providers, active, raw accredited rows, QA-reviewed courses)")
    for group, measures in registry.items():
        print(group, measures)
    print("Flagged course records:", bad_courses)
    print("FICTIONAL ASSESSMENT REPORT (valid, flagged, top valid, mean valid)")
    for skill, measures in scores.items():
        print(skill, measures)
    print("Flagged assessment records:", dict(bad_scores))
    print("PASS — all reference checks matched. No actual programme data used.")
