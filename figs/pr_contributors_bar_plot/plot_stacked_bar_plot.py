# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "plotly",
#     "pandas",
#     "kaleido",
# ]
# ///
import json
import math
import os
from collections import defaultdict
from datetime import datetime

import pandas as pd
import plotly.express as px

ROOT = os.path.dirname(os.path.dirname(__file__))


# Load PR data
with open("_pr_contributors.json") as f:
    data = json.load(f)

# Bin PRs by year
binned = defaultdict(lambda: defaultdict(int))

for pr in data.values():
    year = datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00")).year
    ysf: float = pr["years_since_first"]

    if math.isclose(ysf, 0, abs_tol=7 / 365):
        group = "New"
    elif ysf < 1:
        group = "<1 year"
    elif ysf < 3:
        group = "1-3 years"
    elif ysf < 6:
        group = "3-6 years"
    else:
        group = ">6 years"

    binned[year][group] += 1

# Convert to DataFrame
df = pd.DataFrame(binned).T.fillna(0).astype(int)
df = df.sort_index()  # sort by year

# Ensure consistent column order
columns = ["New", "<1 year", "1-3 years", "3-6 years", ">6 years"]
for col in columns:
    if col not in df:
        df[col] = 0
df = df[columns]

# Plot
colors = [
    "#1f77b4",  # blue
    "#ff7f0e",  # orange
    "#2ca02c",  # green
    "#d62728",  # red
    "#9467bd",  # purple
]

fig = px.bar(
    df,
    x=df.index.astype(str),
    y=columns,
    title="Pull Requests by Year",
    labels={
        "x": "Year",
        "value": "Total Number of Pull Requests",
        "variable": "Year Since First PR",
    },
    color_discrete_sequence=colors,
)

fig.update_layout(
    barmode="stack",
    legend_title_text="Year Since First PR",
    legend=dict(traceorder="reversed"),
    xaxis_title="Year",
    yaxis_title="Total Number of Pull Requests",
    xaxis=dict(type="category"),  # ensure discrete years
    yaxis=dict(
        gridcolor="lightgray",
        gridwidth=1,
        griddash="dash",
    ),
    plot_bgcolor="white",
    paper_bgcolor="white",
    bargap=0.2,
    title_x=0.5,
)
fig.layout.margin.update(t=50, l=0, b=0, r=0)
fig.layout.legend.update(x=0, y=1)

fig.write_image(f"{ROOT}/paper/figs/pr_since_1st.svg")
