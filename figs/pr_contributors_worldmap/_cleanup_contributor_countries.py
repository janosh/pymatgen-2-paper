# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "geopy",
#     "tqdm",
# ]
# ///
"""Cleanup locations: map locations to countries."""

import csv
import time
import json
from tqdm import tqdm
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable, GeocoderServiceError


INPUT_FILE: str = "contributor_locations.csv"
OUTPUT_FILE: str = "contributor_locations_cleaned.csv"
UNRESOLVED_FILE: str = "unresolved_locations.json"


def geocode_country(location, geolocator, max_retries=10):
    for attempt in range(max_retries):
        try:
            geo = geolocator.geocode(location, addressdetails=True, language="en")
            if geo and "country" in geo.raw.get("address", {}):
                return geo.raw["address"]["country"]
            break  # response received but no country

        except (
            GeocoderTimedOut,
            GeocoderUnavailable,
            GeocoderServiceError,
            OSError,
        ) as e:
            print(f"Retry {attempt + 1}/{max_retries} for '{location}': {e}")
            time.sleep(2)
    return None


def clean_and_resolve_locations(input_path, output_path, unresolved_path):
    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = [row for row in reader if row["location"].strip()]

    geolocator = Nominatim(user_agent="location-cleaner")
    cache: dict[str, str | None] = {}
    unresolved: dict[str, list[str]] = {}

    print(f"Resolving countries for {len(rows)} contributors...")

    for row in tqdm(rows, desc="Geocoding locations", unit="user"):
        loc = row["location"]
        login = row["login"]
        if loc in cache:
            country = cache[loc]
        else:
            country = geocode_country(loc, geolocator)
            cache[loc] = country
            time.sleep(1)

        if country:
            row["country"] = country
        else:
            row["country"] = ""
            unresolved.setdefault(loc, []).append(login)

    resolved_rows = [r for r in rows if r["country"]]

    # Write cleaned CSV
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(
            outfile, fieldnames=["login", "location", "country", "pr_count"]
        )
        writer.writeheader()
        writer.writerows(resolved_rows)

    print(
        f"\n✅ Cleaned CSV saved: {output_path} "
        f"({len(resolved_rows)} resolved out of {len(rows)} total)"
    )

    # Save unresolved for manual/LLM fix
    if unresolved:
        with open(unresolved_path, "w", encoding="utf-8") as f:
            json.dump(unresolved, f, indent=2, ensure_ascii=False)
        print(
            f"❌ Unresolved locations saved: {unresolved_path} ({len(unresolved)} unique entries)"
        )


if __name__ == "__main__":
    clean_and_resolve_locations(INPUT_FILE, OUTPUT_FILE, UNRESOLVED_FILE)
