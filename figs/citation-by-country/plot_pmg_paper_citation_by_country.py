"""
Plot a citation by country world map.

References:
    - https://plotly.com/python/map-configuration/

TODO:
    - logscale (colorscale incorrect)
    - use a cutoff date (otherwise data change frequently)?
    - maybe only show labels for citation over certain threshold?
"""

import os
import json
import gzip
from collections import Counter

import requests
import pandas as pd
import pycountry
import plotly.graph_objects as go
import numpy as np


WORK_ID: str = "W2015197254"  # https://openalex.org/works/w2015197254
BASE_URL: str = "https://api.openalex.org/works"

CACHE_FILE = "citation_country_counts.json.gz"


def get_citing_countries(work_id: str) -> Counter:
    PER_PAGE: int = 200

    countries_counter: Counter = Counter()
    cursor: str = "*"

    while cursor:
        url = f"{BASE_URL}?filter=cites:{work_id}&per-page={PER_PAGE}&cursor={cursor}"
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
    force_refresh: bool = False,
) -> Counter:
    if os.path.exists(cache_file) and not force_refresh:
        print("Loading cached data...")
        with gzip.open(cache_file, "rt", encoding="utf-8") as f:
            return Counter(json.load(f))

    print("Fetching citation data... (expect ~30 sec)")
    country_counts = get_citing_countries(work_id)
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
fig.add_trace(
    go.Choropleth(
        locations=df["iso_alpha"],
        z=df["log_citations"],
        text=df["country_name"],
        colorscale="temps",  # https://plotly.com/python/builtin-colorscales/
        colorbar=dict(title="log₁₀(Citations)"),
        hovertemplate="<b>%{text}</b><br>Citations: %{z:.0f}<extra></extra>",
        zmin=0.1,  # log10(1) = 0, so 0.1 is a safe low end
        zmax=df["log_citations"].max(),
    )
)

# Text labels on top

# Hide labels for selected countries as labels overlap (sorry EU)
HIDE_COUNTRIES: set[str] = {
    "AUT",
    "BEL",
    "BGR",
    "HRV",
    "CYP",
    "CZE",
    "DNK",
    "EST",
    "FIN",
    "FRA",
    "DEU",
    "GRC",
    "HUN",
    "IRL",
    "ITA",
    "LVA",
    "LTU",
    "LUX",
    "MLT",
    "NLD",
    "POL",
    "PRT",
    "ROU",
    "SVK",
    "SVN",
    "ESP",
    "SWE",
    "SRB",
    "CHE",
}
df_labels = df[~df["iso_alpha"].isin(HIDE_COUNTRIES)].copy()

fig.add_trace(
    go.Scattergeo(
        locations=df_labels["iso_alpha"],
        text=df_labels["citations"],
        mode="text",
        textfont=dict(size=8, color="black"),
        showlegend=False,
    )
)

fig.update_layout(
    title="Citations by Country for 1ˢᵗ pymatgen Paper",
    geo=dict(showframe=True, showcoastlines=False, projection_type="natural earth"),
)

fig.write_image("citations_by_country.svg", width=1200, height=600, scale=3)
fig.show()
