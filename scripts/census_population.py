#!/usr/bin/env python3
"""Fetch 2020 Census populations for NYC borough counties and present them."""

import json
import os
import subprocess
import sys

API_KEY = os.environ.get("CENSUS_API_KEY")
if not API_KEY:
    print("ERROR: Set CENSUS_API_KEY environment variable.")
    sys.exit(1)
URL = (
    "https://api.census.gov/data/2020/dec/pl"
    f"?get=NAME,P1_001N&for=county:*&in=state:36&key={API_KEY}"
)

# The 5 NYC counties and their borough names
# FIPS: (borough, county_name)
NYC_COUNTIES = {
    "005": ("Bronx", "Bronx County"),
    "047": ("Brooklyn", "Kings County"),
    "061": ("Manhattan", "New York County"),
    "081": ("Queens", "Queens County"),
    "085": ("Staten Island", "Richmond County"),
}


def main():
    # Fetch data via curl (subprocess to keep it as requested)
    result = subprocess.run(
        ["curl", "-s", URL],
        capture_output=True,
        text=True,
        timeout=30,
    )

    if result.returncode != 0:
        print("ERROR: curl failed")
        sys.exit(1)

    data = json.loads(result.stdout)

    # data[0] is the header row: ["NAME", "P1_001N", "state", "county"]
    # data[1:] are data rows: ["<County Name, New York", "<population>", "36", "<fips>"]
    header = data[0]
    rows = data[1:]

    # Build a lookup: fips -> (county_name, population)
    county_data = {}
    for row in rows:
        county_name = row[0]
        population = int(row[1])
        fips = row[3]
        county_data[fips] = (county_name, population)

    # Print the table for our 5 counties
    print(f"{'Borough':<18} {'County':<25} {'FIPS':<8} {'Population':>12}")
    print(f"{'─'*18} {'─'*25} {'─'*8} {'─'*12}")

    total_pop = 0
    for fips in ["005", "047", "061", "081", "085"]:
        borough, county_name = NYC_COUNTIES[fips]
        census_name, pop = county_data[fips]
        print(f"{borough:<18} {county_name:<25} {fips:<8} {pop:>12,}")
        total_pop += pop

    print(f"{'─'*18} {'─'*25} {'─'*8} {'─'*12}")
    print(f"{'NYC Total':<18} {'':<25} {'':<8} {total_pop:>12,}")

    # Append to report.md
    with open("report.md", "a") as rpt:
        rpt.write("\n\n## NYC Borough Populations (2020 Census)\n\n")
        rpt.write(f"| Borough | County | FIPS | Population |\n")
        rpt.write(f"|---------|--------|------|-----------|\n")
        for fips in ["005", "047", "061", "081", "085"]:
            borough, county_name = NYC_COUNTIES[fips]
            _, pop = county_data[fips]
            rpt.write(f"| {borough} | {county_name} | {fips} | {pop:,} |\n")
        rpt.write(f"| **NYC Total** | | | **{total_pop:,}** |\n")

    print("\nReport appended to report.md")


if __name__ == "__main__":
    main()