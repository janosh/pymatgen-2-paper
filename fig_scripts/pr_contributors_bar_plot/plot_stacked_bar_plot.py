# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "plotly",
#     "pandas",
#     "kaleido",
# ]
# ///
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px

ROOT = Path(__file__).resolve().parents[2]
DAYS_PER_YEAR = 365.25


# Load PR data
with open("_pr_contributors.json") as f:
    data = json.load(f)

# Bin PRs by year
binned = defaultdict(lambda: defaultdict(int))

for pr in data.values():
    pr_date = datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00"))
    first_pr_date = datetime.fromisoformat(pr["first_contribution_date"])
    elapsed_days = (pr_date - first_pr_date).total_seconds() / 86_400
    elapsed_years = elapsed_days / DAYS_PER_YEAR

    if elapsed_days < 7:
        group = "<7 days"
    elif elapsed_years < 1:
        group = "<1 year"
    elif elapsed_years < 3:
        group = "1-3 years"
    elif elapsed_years < 6:
        group = "3-6 years"
    else:
        group = ">6 years"

    binned[pr_date.year][group] += 1

# Convert to DataFrame
df = pd.DataFrame(binned).T.fillna(0).astype(int)
df = df.sort_index()  # sort by year

# Ensure consistent column order
columns = ["<7 days", "<1 year", "1-3 years", "3-6 years", ">6 years"]
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
    # title="Pull Requests by Year",
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
    xaxis=dict(
        type="category",
        automargin=True,
        tickmode="array",
        tickvals=[str(y) for y in df.index if y % 2 == 1],  # 2013, 2015, ...
    ),
    yaxis=dict(
        gridcolor="lightgray",
        gridwidth=1,
        griddash="dash",
    ),
    plot_bgcolor="white",
    paper_bgcolor="white",
    bargap=0.2,
    title_x=0.5,
    font=dict(size=16),
)
fig.layout.margin.update(t=50, l=0, b=80, r=0)
fig.layout.legend.update(x=0, y=1)

fig.write_image(f"{ROOT}/paper/figs/pr-since-1st.pdf")
