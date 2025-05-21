"""
TODO:
- fill docstring.
- use a cutoff date (otherwise data change frequently)?
- Cache data (for dev)?
"""

from collections import Counter

import requests
import pandas as pd
import pycountry
import plotly.express as px


# Target OpenAlex Work ID
WORK_ID = "W2015197254"
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

def convert_iso2_to_iso3(iso2_code):
    try:
        return pycountry.countries.get(alpha_2=iso2_code).alpha_3
    except:
        return None

# Step 1: Collect data
print("Fetching citation data... (quite slow, expect ~ 30 sec)")
country_counts = get_citing_countries(WORK_ID)

# Step 2: Convert to DataFrame
df = pd.DataFrame(country_counts.items(), columns=["country_code_2", "citations"])
df["iso_alpha"] = df["country_code_2"].apply(convert_iso2_to_iso3)
df = df.dropna(subset=["iso_alpha"])

# Step 3: Plot
fig = px.choropleth(
    df,
    locations="iso_alpha",
    color="citations",
    color_continuous_scale="Plasma",
    title="Citations by Country for W2015197254",
)
fig.write_image(
    "citations_by_country.png",
    width=1200,          # in pixels
    height=600,          # in pixels
    scale=3              # ≈ 288 DPI
)  # need kaleido
fig.show()
