# /// script
# dependencies = ["numpy", "pandas", "plotly", "pycountry", "requests", "kaleido"]
# ///


"""
Plot a citation by country world map.

References:
    - https://plotly.com/python/map-configuration/
"""

import gzip
import json
import math
import os
from collections import Counter

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pycountry
import requests

WORK_ID: str = "W2015197254"  # https://openalex.org/works/w2015197254
BASE_URL: str = "https://api.openalex.org/works"

CACHE_FILE: str = "_citation_country_counts.json.gz"

# cutoff date for collecting citation data from OpenAlex
CUTOFF_DATE: str = "2026-01-01"


def get_citing_countries() -> Counter[str]:
    """Count institution countries over all authorships of works citing WORK_ID."""
    countries_counter: Counter[str] = Counter()
    filter_str = f"cites:{WORK_ID},from_publication_date:<{CUTOFF_DATE}"
    cursor = "*"
    while cursor:
        url = f"{BASE_URL}?filter={filter_str}&per-page=200&cursor={cursor}"
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


def load_or_fetch_countries() -> Counter[str]:
    """Read cached country counts, fetching and caching them from OpenAlex if absent."""
    if os.path.isfile(CACHE_FILE):
        print("Loading cached data...")
        with gzip.open(CACHE_FILE, "rt", encoding="utf-8") as file:
            return Counter(json.load(file))

    print("Fetching citation data... (expect ~30 sec)")
    country_counts = get_citing_countries()
    with gzip.open(CACHE_FILE, "wt", encoding="utf-8") as file:
        json.dump(dict(country_counts), file, separators=(",", ":"))  # no pretty-print
    return country_counts


def lookup_country(iso2_code: str) -> pycountry.db.Country:
    """Plotly choropleth requires ISO alpha-3 codes, e.g. USA instead of US."""
    country = pycountry.countries.get(alpha_2=iso2_code)
    if country is None:
        raise ValueError(f"unknown ISO alpha-2 code: {iso2_code!r}")
    return country


country_counts = load_or_fetch_countries()
df = pd.DataFrame(country_counts.items(), columns=["country_code_2", "citations"])
df["log_citations"] = np.log10(df["citations"].replace(0, np.nan))
countries = df["country_code_2"].map(lookup_country)
df["iso_alpha"] = [country.alpha_3 for country in countries]
df["country_name"] = [country.name for country in countries]

# Choropleth base map with log color scaling
max_exponent = math.ceil(math.log10(df["citations"].max()))  # e.g., 9500 → 10^4
powers_of_10 = [10**exponent for exponent in range(max_exponent + 1)]
tick_text = [str(v) if v < 1000 else f"{v // 1000}k" for v in powers_of_10]

fig = go.Figure()
fig.add_choropleth(
    locations=df["iso_alpha"],
    z=df["log_citations"],
    text=df["country_name"],
    colorscale="temps",
    colorbar=dict(
        title=dict(
            text="Citations",
            font=dict(size=18),
        ),
        tickvals=np.log10(powers_of_10),
        ticktext=tick_text,
        tickfont=dict(size=18),
    ),
    hovertemplate="<b>%{text}</b><br>Citations: %{customdata}<extra></extra>",
    customdata=df["citations"],  # citation count in hover
    zmin=np.log10(1),
    zmax=np.log10(10**max_exponent),
)

fig.layout.geo.update(
    showframe=True, showcoastlines=False, projection_type="natural earth"
)
fig.update_geos(fitbounds="locations", visible=True)

fig.write_image(
    "../../paper/figs/citations-by-country.pdf", width=1200, height=600, scale=3
)
fig.show()
