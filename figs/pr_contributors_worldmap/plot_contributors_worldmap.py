# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "kaleido",
#     "numpy",
#     "pandas",
#     "plotly",
#     "pycountry",
# ]
# ///
import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pycountry


def country_to_iso3(name):
    try:
        return pycountry.countries.lookup(name).alpha_3
    except LookupError as e:
        print(str(e))
        return None


# Convert data to logscale
df = pd.read_csv("contributor_locations_cleaned.csv")
country_counts = df.groupby("country", as_index=False)["pr_count"].sum()
country_counts["iso3"] = country_counts["country"].apply(country_to_iso3)

country_counts["prs"] = country_counts["pr_count"]
country_counts["log_prs"] = country_counts["prs"].clip(lower=1).map(np.log10)

max_prs = country_counts["prs"].max()
rounded_max = 10 ** math.ceil(math.log10(max_prs))

powers_of_10 = [10**i for i in range(0, int(math.log10(rounded_max)) + 1)]
tick_vals = np.log10(powers_of_10)
tick_text = [str(v) if v < 1000 else f"{v // 1000}k" for v in powers_of_10]

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
    zmax=np.log10(rounded_max),
    colorbar=dict(
        title=dict(text="PRs", font=dict(size=18)),
        tickvals=tick_vals,
        ticktext=tick_text,
        tickfont=dict(size=18),
    ),
    hovertemplate="<b>%{text}</b><br>PRs: %{customdata}<extra></extra>",
)

fig.layout.title.update(
    text="Merged PRs per Country (log scale)",
    font=dict(size=28),
    x=0.5,
    xanchor="center",
)

fig.layout.geo.update(
    showframe=True,
    showcoastlines=False,
    projection_type="natural earth",
)

fig.write_image("pr_contributors_worldmap.svg", width=1200, height=600, scale=3)
fig.show()
