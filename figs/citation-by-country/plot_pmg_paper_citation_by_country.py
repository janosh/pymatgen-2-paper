"""
TODO:
- fill docstring.
- use a cutoff date (otherwise data change frequently)?
"""

import os
import json
from collections import Counter

import requests
import pandas as pd
import pycountry
import plotly.express as px


# Target OpenAlex Work ID
WORK_ID = "W2015197254"  # https://openalex.org/works/w2015197254
BASE_URL = "https://api.openalex.org/works"
PER_PAGE = 200

def get_citing_countries(work_id):
    countries_counter = Counter()
    cursor = "*"

    while cursor:
        url = f"{BASE_URL}?filter=cites:{work_id}&per-page={PER_PAGE}&cursor={cursor}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        for work in data["results"]:
            for authorship in work.get("authorships", []):
                for inst in authorship.get("institutions", []):
                    country = inst.get("country_code")
                    if country:
                        countries_counter[country.upper()] += 1

        cursor = data["meta"].get("next_cursor")

    return countries_counter

CACHE_FILE = "citation_country_counts.json"

def load_or_fetch_countries(work_id, cache_file=CACHE_FILE, force_refresh=False):
    if os.path.exists(cache_file) and not force_refresh:
        print("Loading cached data...")
        with open(cache_file, "r", encoding="utf-8") as f:
            return Counter(json.load(f))

    print("Fetching citation data... (expect ~30 sec)")
    country_counts = get_citing_countries(work_id)
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(dict(country_counts), f, indent=2)
    return country_counts

def convert_iso2_to_iso3(iso2_code):
    try:
        return pycountry.countries.get(alpha_2=iso2_code).alpha_3
    except:
        return None

def iso3_to_country_name(code3):
    try:
        return pycountry.countries.get(alpha_3=code3).name
    except:
        return "Unknown"

# Step 1: Collect data
country_counts = load_or_fetch_countries(WORK_ID)

# Step 2: Convert to DataFrame
df = pd.DataFrame(country_counts.items(), columns=["country_code_2", "citations"])
df["iso_alpha"] = df["country_code_2"].apply(convert_iso2_to_iso3)
df = df.dropna(subset=["iso_alpha"])
df["country_name"] = df["iso_alpha"].apply(iso3_to_country_name)

# Step 3: Plot
fig = px.choropleth(
    df,
    locations="iso_alpha",
    color="citations",
    color_continuous_scale="Plasma",
    title="Citations by Country for 1ˢᵗ pymatgen Paper",
    hover_name="country_name",
    hover_data={
        "citations": True,
        "iso_alpha": False,
        "country_code_2": False,
    },
)

fig.write_image(
    "citations_by_country.svg",
    width=1200,
    height=600,
    scale=3  # ≈ 288 DPI
)
fig.show()
