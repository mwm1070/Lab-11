#!/usr/bin/env python3
"""Task 7 — Data Detective: investigate the 196 Unspecified-borough rows."""

import csv
from collections import Counter, defaultdict

CSV_FILE = "nyc-311-2025-november.csv"


def main():
    # ---------- Gather all Unspecified rows ----------
    unspecified_rows = []
    unspecified_keys = set()
    total_rows = 0

    with open(CSV_FILE, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_rows += 1
            if row["Borough"] == "Unspecified":
                unspecified_rows.append(row)
                unspecified_keys.add(row["Unique Key"])

    print(f"Total rows in CSV: {total_rows}")
    print(f"Unspecified borough rows: {len(unspecified_rows)}")
    print(f"Unique keys among them: {len(unspecified_keys)}")
    print(f"Duplicates? {'Yes' if len(unspecified_rows) != len(unspecified_keys) else 'No'}")
    print()

    # ---------- Query 1: Agency breakdown ----------
    agencies = Counter(r["Agency"] for r in unspecified_rows)
    print("=== Query 1: What agencies? ===")
    for a, c in agencies.most_common():
        print(f"  {a}: {c}")

    # ---------- Query 2: Problem type breakdown ----------
    problems = Counter(r["Problem (formerly Complaint Type)"] for r in unspecified_rows)
    print("\n=== Query 2: What problem types? ===")
    for p, c in problems.most_common():
        print(f"  {p}: {c}")

    # ---------- Query 3: What do these rows have in common? ----------
    # Check City, Location Type, coordinates
    cities = Counter(r["City"] for r in unspecified_rows)
    print("\n=== Query 3: City field ===")
    for city, c in cities.most_common():
        print(f"  {repr(city)}: {c}")

    loc_types = Counter(r["Location Type"] for r in unspecified_rows)
    print("\n=== Query 3b: Location Type ===")
    for lt, c in loc_types.most_common():
        print(f"  {repr(lt)}: {c}")

    # Check coordinates — are they empty or NYC-like?
    has_coords = sum(1 for r in unspecified_rows if r["Latitude"] and r["Longitude"])
    print(f"\n  Rows with coordinates: {has_coords} / {len(unspecified_rows)}")

    # Show a few sample rows
    print("\n=== Sample rows ===")
    for r in unspecified_rows[:5]:
        print(f"  Key={r['Unique Key']}, Agency={r['Agency']}, Problem={r['Problem (formerly Complaint Type)']}, "
              f"Status={r['Status']}, City={r['City']!r}, Lat={r['Latitude']}, Lon={r['Longitude']}")
    print("  ...")
    for r in unspecified_rows[-3:]:
        print(f"  Key={r['Unique Key']}, Agency={r['Agency']}, Problem={r['Problem (formerly Complaint Type)']}, "
              f"Status={r['Status']}, City={r['City']!r}, Lat={r['Latitude']}, Lon={r['Longitude']}")

    # ---------- Query 4: Are these all transit-related? ----------
    transit_agencies = {"TLC", "DOT"}
    transit_rows = [r for r in unspecified_rows if r["Agency"] in transit_agencies]
    non_transit = [r for r in unspecified_rows if r["Agency"] not in transit_agencies]
    print(f"\n=== Transit vs Non-Transit ===")
    print(f"  Transit (TLC/DOT): {len(transit_rows)}")
    print(f"  Non-transit: {len(non_transit)}")

    # Non-transit breakdown
    non_transit_agencies = Counter(r["Agency"] for r in non_transit)
    print(f"  Non-transit agencies: {dict(non_transit_agencies.most_common())}")
    non_transit_problems = Counter(r["Problem (formerly Complaint Type)"] for r in non_transit)
    print(f"  Non-transit problems: {dict(non_transit_problems.most_common())}")

    # Check DSNY (30 rows) — derelict vehicles?
    dsny_rows = [r for r in unspecified_rows if r["Agency"] == "DSNY"]
    dsny_problems = Counter(r["Problem (formerly Complaint Type)"] for r in dsny_rows)
    print(f"\n  DSNY problems: {dict(dsny_problems)}")


if __name__ == "__main__":
    main()