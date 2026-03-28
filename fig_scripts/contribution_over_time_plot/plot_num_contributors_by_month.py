# /// script
# dependencies = ["pandas", "plotly", "kaleido"]
# ///

"""
Plot a X-monthly number of active contributors bar plot,
with the color of bars showing total number of commits.
"""

import os
import subprocess
from pathlib import Path

import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parents[2]


COLORSCALE = "magma"
PLOT_TITLE_FONTSIZE: float = 22
XY_AXIS_CBAR_TITLE_FONTSIZE: float = 22
TICK_LABEL_FONTSIZE: float = 20

BINNED_PERIOD_MONTH: int = 12
CSV_PATH: str = "contributor_commits_by_month.csv.gz"

# TODO: `kaleido` doesn't seem to respect width/height
# https://github.com/plotly/Kaleido/issues/378
plotly.io.defaults.default_width = None
plotly.io.defaults.default_height = None

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

# Drop first and last bin
active_binned = active_binned.iloc[1:-1]
commits_binned = commits_binned.iloc[1:-1]

# Normalize for colormap (linear scale, no log)
COLORBAR_MIN: float = 400
COLORBAR_MAX: float = 3000  # manual cap

normed = (commits_binned - COLORBAR_MIN) / (COLORBAR_MAX - COLORBAR_MIN)
normed = normed.clip(0, 1)  # keep values within [0,1]

colors = [px.colors.sample_colorscale(COLORSCALE, val)[0] for val in normed]

fig = go.Figure()

# Line 1: Active contributors (left axis)
fig.add_trace(
    go.Scatter(
        x=active_binned.index,
        y=active_binned.values,
        mode="lines+markers",
        name="Active Contributors",
        yaxis="y",
        line=dict(width=3),
    )
)

# Line 2: Total commits (right axis)
fig.add_trace(
    go.Scatter(
        x=commits_binned.index,
        y=commits_binned.values,
        mode="lines+markers",
        name="Total Commits",
        yaxis="y2",
        line=dict(width=3, dash="dot"),
    )
)

fig.update_layout(
    width=1100,
    height=600,
    template="plotly_white",
    margin=dict(t=110),
    xaxis=dict(
        title=dict(text="Year", font=dict(size=XY_AXIS_CBAR_TITLE_FONTSIZE)),
        tickfont=dict(size=TICK_LABEL_FONTSIZE),
    ),
    yaxis=dict(
        title=dict(
            text="Number of Contributors",
            font=dict(size=XY_AXIS_CBAR_TITLE_FONTSIZE),
        ),
        tickfont=dict(size=TICK_LABEL_FONTSIZE),
        gridcolor="rgba(0,0,0,0.2)",
    ),
    yaxis2=dict(
        title=dict(
            text="Total Commits",
            font=dict(size=XY_AXIS_CBAR_TITLE_FONTSIZE),
        ),
        tickfont=dict(size=TICK_LABEL_FONTSIZE),
        overlaying="y",  # share same x-axis
        side="right",  # put on right side
        showgrid=False,  # avoid double grid clutter
    ),
    legend=dict(
        x=0.01,
        y=0.99,
        bgcolor="rgba(255,255,255,0.6)",
    ),
)
fig.layout.font.update(size=20)

fig.write_image(f"{ROOT}/paper/figs/active-contributors-colored.pdf")
fig.show()
