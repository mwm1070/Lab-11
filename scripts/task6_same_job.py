#!/usr/bin/env python3
"""Task 6 — Hold the job fixed: HEAT/HOT WATER response times by borough."""

import csv
import statistics
from datetime import datetime
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

CSV_FILE = "nyc-311-2025-november.csv"
DATE_FMT = "%m/%d/%Y %I:%M:%S %p"

# Population for per-borough context
POPULATION = {
    "BRONX": 1_472_654,
    "BROOKLYN": 2_736_074,
    "MANHATTAN": 1_694_251,
    "QUEENS": 2_405_464,
    "STATEN ISLAND": 495_747,
}

BOROUGH_LABELS = {
    "BRONX": "Bronx",
    "BROOKLYN": "Brooklyn",
    "MANHATTAN": "Manhattan",
    "QUEENS": "Queens",
    "STATEN ISLAND": "Staten Island",
}


def parse_dt(raw):
    try:
        return datetime.strptime(raw, DATE_FMT)
    except (ValueError, TypeError):
        return None


def main():
    # ---------- Filter HEAT/HOT WATER, compute hours, track opens ----------
    hours_by_borough = defaultdict(list)
    open_count = 0
    total_heat = 0

    with open(CSV_FILE, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Problem (formerly Complaint Type)"] != "HEAT/HOT WATER":
                continue
            total_heat += 1
            closed_raw = row["Closed Date"]

            if not closed_raw:
                open_count += 1
                continue

            created_dt = parse_dt(row["Created Date"])
            closed_dt = parse_dt(closed_raw)
            if created_dt is None or closed_dt is None:
                continue

            delta = closed_dt - created_dt
            hours = delta.total_seconds() / 3600
            hours_by_borough[row["Borough"]].append(hours)

    print(f"Total HEAT/HOT WATER complaints: {total_heat}")
    print(f"Open cases dropped (no Closed Date): {open_count}")
    print()

    # ---------- Compute median by borough ----------
    boroughs = ["BRONX", "BROOKLYN", "MANHATTAN", "QUEENS", "STATEN ISLAND"]
    results = []

    print(f"{'Borough':<18} {'Count':>8} {'Median Hours':>14}")
    print(f"{'─'*18} {'─'*8} {'─'*14}")
    for b in boroughs:
        vals = hours_by_borough[b]
        med = statistics.median(vals)
        results.append((BOROUGH_LABELS[b], len(vals), med))
        print(f"{BOROUGH_LABELS[b]:<18} {len(vals):>8} {med:>14.2f}")

    # ---------- Sort fastest to slowest ----------
    results.sort(key=lambda x: x[2])

    print(f"\nSorted by median (fastest → slowest):")
    for label, cnt, med in results:
        print(f"  {label:<18} {med:>8.2f} hours ({cnt} cases)")

    # ---------- Plot ----------
    labels = [r[0] for r in results]
    medians = [r[2] for r in results]
    counts = [r[1] for r in results]

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#2ecc71", "#27ae60", "#f39c12", "#e67e22", "#e74c3c"]
    bars = ax.barh(labels, medians, color=colors)

    # Add median labels on bars
    for bar, med, cnt in zip(bars, medians, counts):
        ax.text(
            bar.get_width() + 0.5,
            bar.get_y() + bar.get_height() / 2,
            f"{med:.1f}h (n={cnt})",
            va="center",
            fontsize=9,
        )

    ax.set_xlabel("Median Hours to Close")
    ax.set_ylabel("Borough")
    ax.set_title("HEAT/HOT WATER: Median Hours to Close by Borough (November 2025)")
    ax.margins(x=0.1)
    ax.set_xlim(0, max(medians) * 1.35)
    ax.grid(True, axis="x", alpha=0.3)

    plt.tight_layout()
    plt.savefig("fig-same-job.png", dpi=150)
    print(f"\nChart saved as fig-same-job.png")

    # ---------- Gap analysis ----------
    fastest = results[0]
    slowest = results[-1]
    gap = slowest[2] - fastest[2]
    ratio = slowest[2] / fastest[2]
    print(f"\n=== Gap analysis ===")
    print(f"Fastest: {fastest[0]} ({fastest[2]:.2f} hours)")
    print(f"Slowest: {slowest[0]} ({slowest[2]:.2f} hours)")
    print(f"Gap: {gap:.2f} hours ({ratio:.1f}x difference)")

    # ---------- Verification ----------
    print(f"\n=== Verification ===")
    verify_borough = "QUEENS"  # pick one
    verify_vals = hours_by_borough[verify_borough]
    sorted_vals = sorted(verify_vals)
    n = len(sorted_vals)
    if n % 2 == 1:
        manual_med = sorted_vals[n // 2]
    else:
        manual_med = (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2

    print(f"Verification for {BOROUGH_LABELS[verify_borough]}:")
    print(f"  statistics.median: {statistics.median(verify_vals):.2f}")
    print(f"  Manual median: {manual_med:.2f}")
    print(f"  Match: {abs(statistics.median(verify_vals) - manual_med) < 0.001}")


if __name__ == "__main__":
    main()