#!/usr/bin/env python3
"""Join 311 complaint counts with Census population data and compute complaints per 1,000 residents."""

import csv
from collections import Counter

import matplotlib.pyplot as plt

CSV_FILE = "nyc-311-2025-november.csv"

# 2020 Census populations for the five NYC boroughs
POPULATION = {
    "Bronx": 1_472_654,
    "Brooklyn": 2_736_074,
    "Manhattan": 1_694_251,
    "Queens": 2_405_464,
    "Staten Island": 495_747,
}

# Map CSV borough values to our population keys
BOROUGH_MAP = {
    "BRONX": "Bronx",
    "BROOKLYN": "Brooklyn",
    "MANHATTAN": "Manhattan",
    "QUEENS": "Queens",
    "STATEN ISLAND": "Staten Island",
}


def main():
    # ---------- Count complaints per borough ----------
    with open(CSV_FILE, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    complaint_counts = Counter()
    unspecified = 0

    for row in rows:
        borough_raw = row["Borough"]
        borough = BOROUGH_MAP.get(borough_raw)
        if borough is None:
            unspecified += 1
            continue
        complaint_counts[borough] += 1

    print(f"Dropped {unspecified} rows where Borough is 'Unspecified' (no population to normalize against).\n")

    # ---------- Join and compute per 1,000 ----------
    print(f"{'Borough':<18} {'Population':>12} {'Complaints':>12} {'Per 1,000':>10} {'Verify':>12}")
    print(f"{'─'*18} {'─'*12} {'─'*12} {'─'*10} {'─'*12}")

    data = []  # (borough, population, complaints, per_1000)
    for borough, pop in POPULATION.items():
        complaints = complaint_counts[borough]
        per_1000 = complaints / pop * 1000
        # Verification: manually compute 74,674 / 1,472,654 × 1000
        if borough == "Bronx":
            manual = 74674 / 1472654 * 1000
            verify_str = f"✓ {manual:.2f}"
        else:
            verify_str = ""
        data.append((borough, pop, complaints, per_1000))
        print(f"{borough:<18} {pop:>12,} {complaints:>12,} {per_1000:>9.2f} {verify_str:>12}")

    print(f"\n  Verification detail: Bronx per-1,000 = 74,674 ÷ 1,472,654 × 1000 = {74674/1472654*1000:.2f}")

    # ---------- Bar chart: complaints per 1,000 ----------
    boroughs = [d[0] for d in data][::-1]          # reverse for top-to-bottom display
    per_1000_vals = [d[3] for d in data][::-1]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(boroughs, per_1000_vals, color="cornflowerblue")

    for bar, val in zip(bars, per_1000_vals):
        ax.text(
            bar.get_width() + 0.3,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.2f}",
            va="center",
            fontsize=10,
        )

    ax.set_xlabel("Complaints per 1,000 Residents")
    ax.set_ylabel("Borough")
    ax.set_title("NYC 311 Complaints per 1,000 Residents by Borough (November 2025)")
    ax.margins(x=0.1)
    ax.set_xlim(0, max(per_1000_vals) * 1.18)

    plt.tight_layout()
    plt.savefig("fig-borough-per1000.png", dpi=150)
    print(f"\nChart saved as fig-borough-per1000.png")

    # ---------- Append to report.md ----------
    with open("report.md", "a") as rpt:
        rpt.write("\n\n## Complaints per 1,000 Residents by Borough\n\n")
        rpt.write(f"Dropped {unspecified} rows where Borough is 'Unspecified'.\n\n")
        rpt.write(f"| Borough | Population | Complaints | Per 1,000 Residents |\n")
        rpt.write(f"|---------|-----------|-----------|--------------------|\n")
        for borough, pop, complaints, per_1000 in data:
            rpt.write(f"| {borough} | {pop:,} | {complaints:,} | {per_1000:.2f} |\n")
        rpt.write(f"\n![Complaints per 1,000 Residents](fig-borough-per1000.png)\n")

    print("Report appended to report.md")


if __name__ == "__main__":
    main()