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

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pycountry
import yaml

ROOT = Path(__file__).resolve().parents[2]


def country_to_iso3(name: str) -> str:
    try:
        return pycountry.countries.lookup(name).alpha_3
    except LookupError:
        # Manually correct some country names
        MANUAL_COUNTRY_NAME: dict[str, str] = {"Russia": "Russian Federation"}
        name = MANUAL_COUNTRY_NAME[name]
        return pycountry.countries.lookup(name).alpha_3


# Load PR info
pr_info = pd.read_csv("pr_info.csv")

# Load username to country mapping
with open("user_to_country.yaml", encoding="utf-8") as f:
    country_data = yaml.safe_load(f)

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
country_counts["prs"] = country_counts["pr_count"]
country_counts["log_prs"] = country_counts["prs"].clip(lower=1).map(np.log10)

max_prs: int = country_counts["prs"].max()

ticks = [1, 10, 100, 1000]

# Plot
fig = go.Figure()

fig.add_choropleth(
    locations=country_counts["iso3"],
    locationmode="ISO-3",
    z=country_counts["log_prs"],
    text=country_counts["country"],
    customdata=country_counts["prs"],
    colorscale="temps",
    zmin=np.log10(1),
    zmax=np.log10(max_prs),
    colorbar=dict(
        title=dict(text="PRs", font=dict(size=18)),
        tickvals=np.log10(ticks),
        ticktext=[str(v) for v in ticks],
        tickfont=dict(size=18),
    ),
    hovertemplate="<b>%{text}</b><br>PRs: %{customdata}<extra></extra>",
)

fig.layout.geo.update(
    showframe=True,
    showcoastlines=False,
    projection_type="natural earth",
)
fig.update_geos(fitbounds="locations", visible=True)

fig.write_image(
    f"{ROOT}/paper/figs/pr_contributors_worldmap.svg", width=1200, height=600, scale=3
)
fig.show()
