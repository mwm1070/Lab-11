#!/usr/bin/env python3
"""Analyze NYC 311 data for Manhattan: top complaints and a bar chart."""

import csv
from collections import Counter

import matplotlib.pyplot as plt

CSV_FILE = "nyc-311-2025-november.csv"


def main():
    # Read the CSV
    with open(CSV_FILE, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Filter for Manhattan
    manhattan_rows = [r for r in rows if r["Borough"] == "MANHATTAN"]
    total_manhattan = len(manhattan_rows)

    # Count complaints
    complaint_counts = Counter(r["Problem (formerly Complaint Type)"] for r in manhattan_rows)

    # Top 5
    top5 = complaint_counts.most_common(5)
    # Top 10 for chart
    top10 = complaint_counts.most_common(10)

    # Verification: double-check by grepping via shell
    import subprocess
    grep_result = subprocess.run(
        ["grep", "-c", '"MANHATTAN"', CSV_FILE],
        capture_output=True, text=True
    )
    # This is approximate (matches any field with MANHATTAN), so we just show it
    grep_count = int(grep_result.stdout.strip())
    verify_note = f"(grep -c returns {grep_count}, which includes header; csv-parsed = {total_manhattan})"

    # ---------- Print results ----------
    print(f"Manhattan total complaints: {total_manhattan}")
    print(f"  Verified: {verify_note}")
    print()
    print(f"  {'#':>2}  {'Complaint':<45} {'Count':>8} {'Share':>8}")
    print(f"  {'--':>2}  {'-'*45} {'------':>8} {'-----':>8}")
    for i, (problem, count) in enumerate(top5, 1):
        share = count / total_manhattan * 100
        print(f"  {i:>2}  {problem:<45} {count:>8} {share:>7.2f}%")

    # ---------- Bar chart ----------
    problems_top10 = [p for p, _ in top10][::-1]
    counts_top10 = [c for _, c in top10][::-1]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(problems_top10, counts_top10, color="steelblue")

    # Add count labels on the bars
    for bar, count in zip(bars, counts_top10):
        ax.text(
            bar.get_width() + 2,
            bar.get_y() + bar.get_height() / 2,
            str(count),
            va="center",
            fontsize=9,
        )

    ax.set_xlabel("Number of Complaints")
    ax.set_ylabel("Complaint Type")
    ax.set_title("Top 10 Complaints in Manhattan — NYC 311 (November 2025)")
    ax.margins(x=0.08)
    ax.set_xlim(0, max(counts_top10) * 1.12)

    plt.tight_layout()
    plt.savefig("fig-borough-rbl.png", dpi=150)
    print("\nChart saved as fig-borough-rbl.png")

    # ---------- Append to report.md ----------
    with open("report.md", "a") as rpt:
        rpt.write("\n\n## Manhattan Analysis\n\n")
        rpt.write(f"Manhattan total complaints: {total_manhattan}\n\n")
        rpt.write("Top 5 complaints in Manhattan:\n\n")
        rpt.write(f"| # | Complaint | Count | Share |\n")
        rpt.write(f"|---|-----------|-------|-------|\n")
        for i, (problem, count) in enumerate(top5, 1):
            share = count / total_manhattan * 100
            rpt.write(f"| {i} | {problem} | {count} | {share:.2f}% |\n")
        rpt.write(f"\n![Top 10 Complaints in Manhattan](fig-borough-rbl.png)\n")

    print("Report appended to report.md")


if __name__ == "__main__":
    main()