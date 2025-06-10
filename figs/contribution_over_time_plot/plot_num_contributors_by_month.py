# /// script
# dependencies = ["pandas", "plotly", "kaleido"]
# ///

"""
Plot a X-monthly number of active contributors bar plot,
with the color of bars showing total number of commits.
"""

import os
import sys
import subprocess

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from style import (
    COLORSCALE,
    PLOT_TITLE_FONTSIZE,
    XY_AXIS_CBAR_TITLE_FONTSIZE,
    TICK_LABEL_FONTSIZE,
)

BINNED_PERIOD_MONTH = 6
CSV_PATH = "contributor_commits_by_month.csv.gz"

if not os.path.isfile(CSV_PATH):
    print("Data CSV not found. Running script to generate it...")
    result = subprocess.run(
        ["uv", "run", "_retrieve_commit_info_over_time.py"],
        capture_output=True,
        text=True,
    )

df = pd.read_csv("contributor_commits_by_month.csv.gz", compression="gzip")
df_grouped = df.groupby("contributor_id").sum(numeric_only=True)

# Convert columns to datetime
df_grouped.columns = pd.to_datetime(df_grouped.columns, format="%Y-%m")

# Count active contributors
active_contributors = (df_grouped > 0).sum(axis=0)

# Total number of commits per month
total_commits = df_grouped.sum(axis=0)

# Resample into X-month bins
active_binned = active_contributors.resample(f"{BINNED_PERIOD_MONTH}ME").sum()
commits_binned = total_commits.resample(f"{BINNED_PERIOD_MONTH}ME").sum()

# Normalize for colormap
normed = (commits_binned - commits_binned.min()) / (
    commits_binned.max() - commits_binned.min()
)
colors = [px.colors.sample_colorscale(COLORSCALE, val)[0] for val in normed]

# Build bar plot
fig = go.Figure()
fig.add_bar(
    x=active_binned.index.strftime("%Y-%m"),
    y=active_binned.values,
    marker=dict(color=colors),
    customdata=commits_binned.values.reshape(-1, 1),
    hovertemplate="Period: %{x}<br>Contributors: %{y}<br>Total Commits: %{customdata[0]}",
    showlegend=False,
)

# Colorbar using a dummy scatter trace
fig.add_scatter(
    x=[None],
    y=[None],
    mode="markers",
    marker=dict(
        colorscale=COLORSCALE,
        cmin=commits_binned.min(),
        cmax=commits_binned.max(),
        color=[commits_binned.max()],
        showscale=True,
        colorbar=dict(
            title=dict(
                text="Total Commits", font=dict(size=XY_AXIS_CBAR_TITLE_FONTSIZE)
            ),
            tickfont=dict(size=13),
            title_side="right",
        ),
    ),
    hoverinfo="skip",
    showlegend=False,
)

title = f"Active Contributors per {BINNED_PERIOD_MONTH}-Month Period"
fig.layout.title.update(text=title, x=0.5, font=dict(size=PLOT_TITLE_FONTSIZE))
fig.layout.update(width=1100, height=600, template="plotly_white")
fig.layout.xaxis.update(
    title=dict(text="Year", font=dict(size=XY_AXIS_CBAR_TITLE_FONTSIZE)),
    tickfont=dict(size=TICK_LABEL_FONTSIZE),
)
fig.layout.yaxis.update(
    title=dict(
        text="Number of Contributors", font=dict(size=XY_AXIS_CBAR_TITLE_FONTSIZE)
    ),
    tickfont=dict(size=TICK_LABEL_FONTSIZE),
    gridcolor="rgba(0,0,0,0.2)",
    gridwidth=1.2,
)
fig.layout.font.update(size=14)

fig.write_image("active_contributors_colored.svg")
fig.show()
