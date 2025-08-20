# /// script
# dependencies = ["pandas", "plotly", "kaleido", "numpy"]
# ///

"""
Plot a X-monthly number of active contributors bar plot,
with the color of bars showing total number of commits.
"""

import os
import sys
import subprocess

import plotly
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from style import (
    PLOT_TITLE_FONTSIZE,
    XY_AXIS_CBAR_TITLE_FONTSIZE,
    TICK_LABEL_FONTSIZE,
)

COLORSCALE = "magma"

BINNED_PERIOD_MONTH: int = 6
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

# Normalize for colormap
log_commits = np.log10(commits_binned.clip(lower=1))  # avoid log(0)

COLORBAR_MIN: float = np.log10(100)
COLORBAR_MAX: float = np.log10(1000)

normed = (log_commits - COLORBAR_MIN) / (COLORBAR_MAX - COLORBAR_MIN)
normed = normed.clip(0, 1)  # keep values within [0,1]

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
    # Add values to the bar
    text=commits_binned.values,
    textposition="outside",
    textfont=dict(size=12),
)

# Colorbar using a dummy scatter trace
tick_values_original = [300, 500, 1000, 1500]
tickvals = np.log10(tick_values_original)

fig.add_scatter(
    x=[None],
    y=[None],
    mode="markers",
    marker=dict(
        colorscale=COLORSCALE,
        cmin=COLORBAR_MIN,
        cmax=COLORBAR_MAX,
        color=[COLORBAR_MAX],
        showscale=True,
        colorbar=dict(
            title=dict(
                text="Total Commits (log scale)",
                font=dict(size=XY_AXIS_CBAR_TITLE_FONTSIZE),
            ),
            tickvals=np.log10([100, 1000, 10000]),
            ticktext=["100", "1k", "10k"],
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
