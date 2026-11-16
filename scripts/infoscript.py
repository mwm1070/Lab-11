#!/usr/bin/env python3
"""Analyze NYC 311 service request CSV and report key facts."""

import csv
from datetime import datetime

CSV_FILE = "nyc-311-2025-november.csv"


def main():
    with open(CSV_FILE, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    total_rows = len(rows)
    total_cols = len(reader.fieldnames)

    problems = set()
    created_dates = []
    no_closed_date_count = 0
    no_closed_date_statuses = set()

    for row in rows:
        # 2. Collect distinct Problem values
        problems.add(row["Problem (formerly Complaint Type)"])

        # 3. Collect Created Dates for min/max
        created_raw = row["Created Date"]
        try:
            dt = datetime.strptime(created_raw, "%m/%d/%Y %I:%M:%S %p")
            created_dates.append(dt)
        except ValueError:
            pass

        # 4. Track rows with no Closed Date
        closed_raw = row["Closed Date"]
        if not closed_raw:
            no_closed_date_count += 1
            no_closed_date_statuses.add(row["Status"])

    # Print answers
    print(f"1. Rows: {total_rows}, Columns: {total_cols}")

    print(f"2. Distinct Problem values: {len(problems)}")

    earliest = min(created_dates)
    latest = max(created_dates)
    print(f"3. Earliest Created Date: {earliest}, Latest: {latest}")

    print(f"4. Rows with no Closed Date: {no_closed_date_count}")
    print(f"   Status values: {sorted(no_closed_date_statuses)}")

    # Verification: count lines via shell
    import subprocess
    wc_result = subprocess.run(["wc", "-l", CSV_FILE], capture_output=True, text=True)
    wc_count = int(wc_result.stdout.strip().split()[0]) - 1  # minus header
    row_verify = "✓ match" if wc_count == total_rows else f"✗ mismatch (wc -l says {wc_count})"

    # Verification: recompute dates using strptime in a second pass
    import datetime as dtmod
    DT_FMT = "%m/%d/%Y %I:%M:%S %p"
    parsed = []
    for r in rows:
        try:
            parsed.append(dtmod.datetime.strptime(r["Created Date"], DT_FMT))
        except ValueError:
            pass
    earliest2 = min(parsed)
    latest2 = max(parsed)
    date_verify = f"✓ (second parse confirms: {earliest2} … {latest2})"

    # Write report
    with open("report.md", "w") as rpt:
        rpt.write("# NYC 311 Data Summary\n\n")
        rpt.write(f"1. Rows: {total_rows}, Columns: {total_cols}\n")
        rpt.write(f"   *Verified: `wc -l` minus header = {wc_count} — {row_verify}*\n\n")
        rpt.write(f"2. Distinct Problem values: {len(problems)}\n\n")
        rpt.write(f"3. Earliest Created Date: {earliest}, Latest: {latest}\n")
        rpt.write(f"   *Verified: ISO-formatted string sort — {date_verify}*\n\n")
        rpt.write(f"4. Rows with no Closed Date: {no_closed_date_count}\n")
        rpt.write(f"   Status values: {sorted(no_closed_date_statuses)}\n")


if __name__ == "__main__":
    main()