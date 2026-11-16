#!/usr/bin/env python3
"""Build a day × hour heatmap for Noise - Residential complaints and identify anomalies."""

import csv
from datetime import datetime, date
from collections import Counter, defaultdict

import numpy as np
import matplotlib.pyplot as plt


CSV_FILE = "nyc-311-2025-november.csv"


def main():
    # ---------- Load data: day × hour table for Noise - Residential ----------
    # Also collect Unique Keys for dedup checks
    table = defaultdict(lambda: defaultdict(int))
    all_keys = set()
    duplicate_keys = set()
    seen_keys = set()

    parsed_rows_total = 0
    bad_parse = 0

    with open(CSV_FILE, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            problem = row["Problem (formerly Complaint Type)"]
            if problem != "Noise - Residential":
                continue

            created_raw = row["Created Date"]
            try:
                dt = datetime.strptime(created_raw, "%m/%d/%Y %I:%M:%S %p")
            except ValueError:
                bad_parse += 1
                continue

            day = dt.date()
            hour = dt.hour
            table[day][hour] += 1
            parsed_rows_total += 1

            # Track unique keys for dedup
            uid = row.get("Unique Key", "")
            if uid in seen_keys:
                duplicate_keys.add(uid)
            seen_keys.add(uid)

    all_days = sorted(table.keys())
    hours = list(range(24))

    # Build matrix: rows = days, cols = hours
    mat = np.zeros((len(all_days), 24), dtype=int)
    for i, d in enumerate(all_days):
        for h in hours:
            mat[i, h] = table[d][h]

    print(f"Noise - Residential rows parsed: {parsed_rows_total}")
    print(f"Date range: {all_days[0]} to {all_days[-1]} ({len(all_days)} days)")
    print(f"Bad date parses: {bad_parse}")
    print(f"Duplicate Unique Keys: {len(duplicate_keys)}")
    if duplicate_keys:
        print(f"  Duplicate keys: {sorted(duplicate_keys)[:10]}{'...' if len(duplicate_keys) > 10 else ''}")

    # ---------- Identify anomalous night ----------
    # Focus on "night" hours: 20:00-23:00 + 0:00-3:00
    night_hours = list(range(20, 24)) + list(range(0, 4))
    night_totals = {d: sum(table[d][h] for h in night_hours) for d in all_days}

    # Find the night with the most noise complaints
    sorted_nights = sorted(night_totals.items(), key=lambda x: x[1], reverse=True)
    print(f"\n=== Top 5 nights (20:00-03:59) by Noise - Residential count ===")
    for d, cnt in sorted_nights[:5]:
        print(f"  {d}: {cnt} complaints")

    # Also look at evening peak hours specifically (20:00-23:00)
    evening_totals = {d: sum(table[d][h] for h in range(20, 24)) for d in all_days}
    sorted_evenings = sorted(evening_totals.items(), key=lambda x: x[1], reverse=True)
    print(f"\n=== Top 5 evenings (20:00-23:59) by Noise - Residential count ===")
    for d, cnt in sorted_evenings[:5]:
        print(f"  {d}: {cnt} complaints")

    # Hour-by-hour breakout for the anomalous day
    anomaly_day = sorted_nights[0][0]
    print(f"\n=== Hour-by-hour for anomalous day ({anomaly_day}) ===")
    for h in hours:
        print(f"  {h:02d}:00 -> {table[anomaly_day][h]}")

    # ---------- Checks ----------
    print(f"\n=== Checks ===")

    # Check 1: Count total rows in CSV vs parsed (bad rows?)
    with open(CSV_FILE, newline="", encoding="utf-8", errors="replace") as f:
        total_lines = sum(1 for _ in f) - 1  # minus header

    expected_noise = sum(sum(row.values()) for row in table.values())
    print(f"Check 1 — Total data rows in CSV: {total_lines}")
    print(f"  Noise - Residential rows in our table: {expected_noise}")

    # Check 2: Duplicate Unique Keys on the anomalous day
    dup_on_anomaly_day = set()
    all_keys_for_day = set()
    with open(CSV_FILE, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            problem = row["Problem (formerly Complaint Type)"]
            if problem != "Noise - Residential":
                continue
            created_raw = row["Created Date"]
            try:
                dt = datetime.strptime(created_raw, "%m/%d/%Y %I:%M:%S %p")
            except ValueError:
                continue
            if dt.date() != anomaly_day:
                continue
            uid = row.get("Unique Key", "")
            if uid in all_keys_for_day:
                dup_on_anomaly_day.add(uid)
            all_keys_for_day.add(uid)

    print(f"Check 2 — Duplicate Unique Keys on {anomaly_day}: {len(dup_on_anomaly_day)}")
    if dup_on_anomaly_day:
        print(f"  Duplicate keys: {sorted(dup_on_anomaly_day)[:10]}{'...' if len(dup_on_anomaly_day) > 10 else ''}")

    # Check 3: Look at the raw hourly pattern on that day — does it look "real"?
    # Real complaints would follow a natural diurnal curve; a spike at a strange
    # hour or a perfectly flat distribution would suggest bad data.
    print(f"\nCheck 3 — Hourly profile on {anomaly_day}:")
    for h in night_hours:
        print(f"  {h:02d}:00 -> {table[anomaly_day][h]}")

    # Also check the previous and next day for comparison
    idx = all_days.index(anomaly_day)
    if idx > 0:
        prev_day = all_days[idx - 1]
        print(f"\n  Previous day ({prev_day}) night hours for comparison:")
        for h in night_hours:
            print(f"    {h:02d}:00 -> {table[prev_day][h]}")
    if idx + 1 < len(all_days):
        next_day = all_days[idx + 1]
        print(f"\n  Next day ({next_day}) night hours for comparison:")
        for h in night_hours:
            print(f"    {h:02d}:00 -> {table[next_day][h]}")

    # ---------- Heatmap ----------
    fig, ax = plt.subplots(figsize=(14, 8))
    im = ax.imshow(mat, aspect="auto", cmap="YlOrRd", interpolation="nearest")

    # Labels
    ax.set_xticks(range(24))
    ax.set_xticklabels([f"{h:02d}:00" for h in hours], rotation=45, fontsize=8)
    ax.set_yticks(range(len(all_days)))
    ax.set_yticklabels([d.strftime("%b %d") for d in all_days], fontsize=9)
    ax.set_xlabel("Hour of Day", fontsize=11)
    ax.set_ylabel("Date", fontsize=11)
    ax.set_title("Noise - Residential Complaints: Day × Hour Heatmap (November 2025)", fontsize=13)

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, shrink=0.75)
    cbar.set_label("Complaint Count", fontsize=10)

    # Annotate the anomaly
    if anomaly_day in all_days:
        ani = all_days.index(anomaly_day)
        ax.add_patch(plt.Rectangle((-0.5, ani - 0.5), 24, 1, fill=False,
                                    edgecolor="blue", linewidth=3, linestyle="--",
                                    label=f"Anomaly: {anomaly_day}"))
        ax.legend(loc="upper right", fontsize=9)

    plt.tight_layout()
    plt.savefig("fig-nights.png", dpi=150)
    print(f"\nHeatmap saved as fig-nights.png")

    # ---------- Print summary for the user's write-up ----------
    print(f"\n=== Summary for your write-up ===")
    print(f"Anomalous night: {anomaly_day}")
    print(f"Peak night hour on that day: {max(night_hours, key=lambda h: table[anomaly_day][h])}:00")
    print(f"Night total: {night_totals[anomaly_day]}")
    print(f"Duplicates on that day: {len(dup_on_anomaly_day)}")
    print(f"Bad date parses overall: {bad_parse}")
    print(f"To verify: check if {anomaly_day} was a holiday or notable event in NYC (e.g., Thanksgiving was Nov 27, 2025)")


if __name__ == "__main__":
    main()