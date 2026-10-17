# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "kaleido",
#     "numpy",
#     "pandas",
#     "plotly",
#     "pycountry",
#     "pyyaml",
# ]
# ///

"""Plot merged PRs per contributor country as a log-scaled world map."""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pycountry
import yaml

ROOT = Path(__file__).resolve().parents[2]


def country_to_iso3(name: str) -> str:
    """Map a country name to its ISO alpha-3 code, correcting names pycountry lacks."""
    manual_country_names = {"Russia": "Russian Federation"}
    return pycountry.countries.lookup(manual_country_names.get(name, name)).alpha_3


# Load PR info
pr_info = pd.read_csv("pr_info.csv")

# Load username to country mapping
with open("user_to_country.yaml", encoding="utf-8") as file:
    country_data = yaml.safe_load(file)

username_to_country: dict[str, str] = {}
for source in ("manual", "from_pmg_doc", "from_github"):
    username_to_country.update(country_data[source])

# Map usernames to countries
pr_info["country"] = pr_info["username"].map(username_to_country)

# Report unresolved users
unresolved = pr_info[pr_info["country"].isna()]
unresolved = unresolved.sort_values("pr_count", ascending=False)
if not unresolved.empty:
    print(f"⚠️ Could not resolve country for the following {len(unresolved)} users:")
    for _, row in unresolved.iterrows():
        print(f"  - {row['username']} (PRs: {row['pr_count']})")

# Filter valid entries and group by country
df = pr_info.dropna(subset=["country"])
country_counts = df.groupby("country", as_index=False)["pr_count"].sum()
country_counts["iso3"] = country_counts["country"].apply(country_to_iso3)

# Compute log-scaled values
country_counts["log_prs"] = country_counts["pr_count"].clip(lower=1).map(np.log10)

ticks = [1, 10, 100, 1000]

# Plot
fig = go.Figure()

fig.add_choropleth(
    locations=country_counts["iso3"],
    locationmode="ISO-3",
    z=country_counts["log_prs"],
    text=country_counts["country"],
    customdata=country_counts["pr_count"],
    colorscale="temps",
    zmin=np.log10(1),
    zmax=np.log10(country_counts["pr_count"].max()),
    colorbar=dict(
        title="PRs",
        tickvals=np.log10(ticks),
        ticktext=[str(v) for v in ticks],
        len=0.7,  # make colorbar shorter
    ),
    hovertemplate="<b>%{text}</b><br>PRs: %{customdata}<extra></extra>",
)

fig.layout.geo.update(
    showframe=True,
    showcoastlines=False,
    projection_type="natural earth",
)
fig.update_geos(fitbounds="locations", visible=True)
fig.update_layout(font=dict(size=22), margin=dict(l=10, r=0, t=0, b=0))

fig.write_image(
    f"{ROOT}/paper/figs/pr-contributors-worldmap.pdf", width=1200, height=600, scale=3
)
fig.show()
