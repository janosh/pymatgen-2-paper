"""
Plot a citation by country world map.

References:
    - https://plotly.com/python/map-configuration/
"""

import os
import json
import gzip
import math
from collections import Counter

import requests
import pandas as pd
import pycountry
import plotly.graph_objects as go
import numpy as np


WORK_ID: str = "W2015197254"  # https://openalex.org/works/w2015197254
BASE_URL: str = "https://api.openalex.org/works"

CACHE_FILE: str = "citation_country_counts.json.gz"

CUTOFF_DATE: str = (
    "2025-06-01"  # cutoff date for collecting citation data from OpenAlex
)

LABEL_THRESHOLD: int = 100  # Only show labels for countries above this


def get_citing_countries(work_id: str, cutoff_date: str | None = None) -> Counter:
    PER_PAGE = 200
    countries_counter = Counter()
    cursor = "*"

    # Build filter string
    filters = [f"cites:{work_id}"]
    if cutoff_date:
        filters.append(f"from_publication_date:<{cutoff_date}")
    filter_str = ",".join(filters)

    while cursor:
        url = f"{BASE_URL}?filter={filter_str}&per-page={PER_PAGE}&cursor={cursor}"
        response = requests.get(url, timeout=5)
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


def load_or_fetch_countries(
    work_id: str,
    cache_file: str = CACHE_FILE,
) -> Counter:
    if os.path.exists(cache_file):
        print("Loading cached data...")
        with gzip.open(cache_file, "rt", encoding="utf-8") as f:
            return Counter(json.load(f))

    print("Fetching citation data... (expect ~30 sec)")
    country_counts = get_citing_countries(work_id, CUTOFF_DATE)
    with gzip.open(cache_file, "wt", encoding="utf-8") as f:
        json.dump(dict(country_counts), f, separators=(",", ":"))  # no pretty-print
    return country_counts


# Collect data
country_counts = load_or_fetch_countries(WORK_ID)


# Convert to DataFrame
def convert_iso2_to_iso3(iso2_code: str) -> str:
    """
    Plotly choropleth requires ISO alpha-3 codes, e.g. USA instead of US.
    """
    return pycountry.countries.get(alpha_2=iso2_code).alpha_3


def iso3_to_country_name(code3: str) -> str:
    return pycountry.countries.get(alpha_3=code3).name


df = pd.DataFrame(country_counts.items(), columns=["country_code_2", "citations"])
df["log_citations"] = np.log10(df["citations"].replace(0, np.nan))
df["iso_alpha"] = df["country_code_2"].apply(convert_iso2_to_iso3)
df = df.dropna(subset=["iso_alpha"])
df["country_name"] = df["iso_alpha"].apply(iso3_to_country_name)

# Plot
fig = go.Figure()

# Choropleth base map with log color scaling
max_citation = df["citations"].max()
rounded_max = 10 ** math.ceil(math.log10(max_citation))  # e.g., 9500 → 10000

powers_of_10 = [10**i for i in range(0, int(math.log10(rounded_max)) + 1)]
tick_vals = np.log10(powers_of_10)
tick_text = [str(v) if v < 1000 else f"{v // 1000}k" for v in powers_of_10]

fig.add_trace(
    go.Choropleth(
        locations=df["iso_alpha"],
        z=df["log_citations"],
        text=df["country_name"],
        colorscale="temps",
        colorbar=dict(
            title=dict(
                text="Citations",
                font=dict(size=18),
            ),
            tickvals=tick_vals,
            ticktext=tick_text,
            tickfont=dict(size=18),
        ),
        hovertemplate="<b>%{text}</b><br>Citations: %{customdata}<extra></extra>",
        customdata=df["citations"],  # citation count in hover
        zmin=np.log10(1),
        zmax=np.log10(rounded_max),
    )
)

# Text labels on top
df_labels = df[df["citations"] >= LABEL_THRESHOLD].copy()

fig.add_trace(
    go.Scattergeo(
        locations=df_labels["iso_alpha"],
        text=df_labels["citations"],
        mode="text",
        textfont=dict(size=12, color="black"),
        showlegend=False,
    )
)

fig.update_layout(
    title=dict(
        text="Citations by Country for 1ˢᵗ pymatgen Paper",
        font=dict(size=28),
        x=0.5,
        xanchor="center",
    ),
    geo=dict(showframe=True, showcoastlines=False, projection_type="natural earth"),
)

fig.write_image("citations_by_country.svg", width=1200, height=600, scale=3)
fig.show()
