#!/usr/bin/env python3
"""Task 5 — Response times: median hours from created to closed, by agency."""

import csv
import statistics
from datetime import datetime
from collections import defaultdict, Counter

CSV_FILE = "nyc-311-2025-november.csv"

DATE_FMT = "%m/%d/%Y %I:%M:%S %p"


def parse_dt(raw):
    try:
        return datetime.strptime(raw, DATE_FMT)
    except (ValueError, TypeError):
        return None


def main():
    # ---------- 1. Find top 6 agencies by complaint count ----------
    agency_counts = Counter()
    with open(CSV_FILE, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            agency_counts[row["Agency"]] += 1

    top6_agencies = [a for a, _ in agency_counts.most_common(6)]
    print(f"Top 6 agencies: {top6_agencies}")
    print()

    # ---------- 2. Parse dates, compute hours, filter open cases ----------
    # Structure: agency -> list of hours_to_close
    hours_by_agency = defaultdict(list)
    all_times = []  # (hours, agency, problem, created, closed) for the longest search

    open_count = 0
    total_rows = 0

    with open(CSV_FILE, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            agency = row["Agency"]
            if agency not in top6_agencies:
                continue

            total_rows += 1
            created_raw = row["Created Date"]
            closed_raw = row["Closed Date"]

            # Skip open cases (no Closed Date)
            if not closed_raw:
                open_count += 1
                continue

            created_dt = parse_dt(created_raw)
            closed_dt = parse_dt(closed_raw)
            if created_dt is None or closed_dt is None:
                continue

            delta = closed_dt - created_dt
            hours = delta.total_seconds() / 3600

            hours_by_agency[agency].append(hours)
            all_times.append((hours, agency, row["Problem (formerly Complaint Type)"], created_raw, closed_raw))

    print(f"Total rows for top 6 agencies: {total_rows}")
    print(f"Open cases dropped (no Closed Date): {open_count}")
    print()

    # ---------- 3. Compute median hours per agency ----------
    print(f"{'Agency':<8} {'Median Hours':>14} {'Mean Hours':>14} {'Count':>8}")
    print(f"{'─'*8} {'─'*14} {'─'*14} {'─'*8}")

    medians = {}
    means = {}
    for agency in top6_agencies:
        vals = hours_by_agency[agency]
        med = statistics.median(vals)
        avg = statistics.mean(vals)
        medians[agency] = med
        means[agency] = avg
        print(f"{agency:<8} {med:>14.2f} {avg:>14.2f} {len(vals):>8}")

    # ---------- 4. Longest-closing complaint ----------
    longest = max(all_times, key=lambda x: x[0])
    longest_hours, longest_agency, longest_problem, longest_created, longest_closed = longest
    longest_days = longest_hours / 24

    print(f"\n=== Longest-closing complaint ===")
    print(f"Agency: {longest_agency}")
    print(f"Problem: {longest_problem}")
    print(f"Created: {longest_created}")
    print(f"Closed: {longest_closed}")
    print(f"Hours to close: {longest_hours:.2f}")
    print(f"Days to close: {longest_days:.2f}")

    # ---------- 5. For that agency, compare mean vs median ----------
    ag = longest_agency
    print(f"\n=== {ag} — Mean vs Median ===")
    print(f"Mean: {means[ag]:.2f} hours")
    print(f"Median: {medians[ag]:.2f} hours")
    print(f"Gap: {means[ag] - medians[ag]:.2f} hours")
    print(f"Longest case: {longest_hours:.2f} hours ({longest_days:.2f} days)")
    print()
    print("Explanation: The mean ({:.2f}) is much larger than the median ({:.2f}) because the distribution is "
          "right-skewed — most complaints close quickly, but a small number of extreme outliers "
          "(like the {:.0f}-day case above) pull the mean upward. The median better represents "
          "the 'typical' response time.".format(means[ag], medians[ag], longest_days))

    # ---------- 6. Verification: recompute one median using statistics.median ----------
    print(f"\n=== Verification ===")
    verify_agency = top6_agencies[0]  # pick the top agency
    verify_vals = hours_by_agency[verify_agency]
    # Groupby method already used statistics.median above. Let's sort and take the middle value manually.
    sorted_vals = sorted(verify_vals)
    n = len(sorted_vals)
    if n % 2 == 1:
        manual_median = sorted_vals[n // 2]
    else:
        manual_median = (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2

    print(f"Verification for {verify_agency}:")
    print(f"  statistics.median: {medians[verify_agency]:.2f}")
    print(f"  Manual median (sorted middle): {manual_median:.2f}")
    print(f"  Match: {abs(medians[verify_agency] - manual_median) < 0.001}")


if __name__ == "__main__":
    main()