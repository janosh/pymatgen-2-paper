# /// script
# dependencies = ["pandas", "plotly", "kaleido"]
# ///

"""Plot annual numbers of active contributors and commits."""

import os
import subprocess
from pathlib import Path

import pandas as pd
import plotly
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parents[2]


PLOT_TITLE_FONTSIZE: float = 22
XY_AXIS_CBAR_TITLE_FONTSIZE: float = 22
TICK_LABEL_FONTSIZE: float = 20

CSV_PATH: str = "contributor_commits_by_month.csv.gz"

# TODO: `kaleido` doesn't seem to respect width/height
# https://github.com/plotly/Kaleido/issues/378
plotly.io.defaults.default_width = None  # ty: ignore[invalid-assignment]
plotly.io.defaults.default_height = None  # ty: ignore[invalid-assignment]

if not os.path.isfile(CSV_PATH):
    print("Data CSV not found. Running script to generate it...")
    subprocess.run(
        ["uv", "run", "_retrieve_commit_info_over_time.py"],
        capture_output=True,
        text=True,
        check=True,
    )

df = pd.read_csv("contributor_commits_by_month.csv.gz", compression="gzip")
df_grouped = df.groupby("contributor_id").sum(numeric_only=True)

# Convert columns to datetime
df_grouped.columns = pd.to_datetime(df_grouped.columns, format="%Y-%m")

# Sum each contributor's commits by calendar year, then count contributors with
# at least one commit in each year. This counts each contributor once per year.
annual_by_contributor = df_grouped.T.groupby(df_grouped.columns.year).sum().T
active_annual = (annual_by_contributor > 0).sum(axis=0)
commits_annual = annual_by_contributor.sum(axis=0)
years = pd.to_datetime(active_annual.index.astype(str), format="%Y")

fig = go.Figure()

# Line 1: Active contributors (left axis)
fig.add_trace(
    go.Scatter(
        x=years,
        y=active_annual.values,
        mode="lines+markers",
        name="Active Contributors",
        yaxis="y",
        line=dict(width=3),
    )
)

# Line 2: Annual commits (right axis)
fig.add_trace(
    go.Scatter(
        x=years,
        y=commits_annual.values,
        mode="lines+markers",
        name="Annual Commits",
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
            font=dict(size=XY_AXIS_CBAR_TITLE_FONTSIZE, color="royalblue"),
        ),
        tickfont=dict(size=TICK_LABEL_FONTSIZE, color="royalblue"),
        gridcolor="rgba(0,0,0,0.2)",
        rangemode="tozero",
    ),
    yaxis2=dict(
        title=dict(
            text="Annual Commits",
            font=dict(size=XY_AXIS_CBAR_TITLE_FONTSIZE, color="orangered"),
        ),
        tickfont=dict(size=TICK_LABEL_FONTSIZE, color="orangered"),
        overlaying="y",
        side="right",
        showgrid=False,
        rangemode="tozero",
    ),
    legend=dict(
        x=0.7,
        y=1.0,
        yanchor="bottom",
        bgcolor="rgba(255,255,255,0.6)",
    ),
)
fig.layout.font.update(size=20)

fig.write_image(f"{ROOT}/paper/figs/active-contributors-colored.pdf")
fig.show()
