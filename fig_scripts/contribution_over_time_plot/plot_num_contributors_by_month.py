# /// script
# dependencies = ["pandas", "plotly", "kaleido"]
# ///

"""Plot annual numbers of active contributors and commits."""

import os

import pandas as pd
import plotly
import plotly.graph_objects as go

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


XY_AXIS_CBAR_TITLE_FONTSIZE: float = 22
TICK_LABEL_FONTSIZE: float = 20

CSV_PATH = f"{os.path.dirname(__file__)}/contributor_activity_by_year.csv"

# TODO: `kaleido` doesn't seem to respect width/height
# https://github.com/plotly/Kaleido/issues/378
plotly.io.defaults.default_width = None  # ty: ignore[invalid-assignment]
plotly.io.defaults.default_height = None  # ty: ignore[invalid-assignment]

df = pd.read_csv(CSV_PATH)
years = pd.to_datetime(df["year"].astype(str), format="%Y")
year_ticks = [*range(2012, 2025, 2), 2025]

fig = go.Figure()

# Line 1: Active contributors (left axis)
fig.add_scatter(
    x=years,
    y=df["active_contributors"],
    mode="lines+markers",
    name="Active Contributors",
    yaxis="y",
    line=dict(width=3, color="royalblue"),
)

# Line 2: Annual commits (right axis)
fig.add_scatter(
    x=years,
    y=df["commits"],
    mode="lines+markers",
    name="Non-merge Commits",
    yaxis="y2",
    line=dict(width=3, dash="dot", color="orangered"),
)

fig.update_layout(
    width=1100,
    height=600,
    template="plotly_white",
    margin=dict(t=110),
    xaxis=dict(
        title=dict(text="Year", font=dict(size=XY_AXIS_CBAR_TITLE_FONTSIZE)),
        tickfont=dict(size=TICK_LABEL_FONTSIZE),
        tickmode="array",
        tickvals=[f"{year}-01-01" for year in year_ticks],
        ticktext=[str(year) for year in year_ticks],
        showgrid=False,
    ),
    yaxis=dict(
        title=dict(
            text="Number of Contributors",
            font=dict(size=XY_AXIS_CBAR_TITLE_FONTSIZE, color="royalblue"),
        ),
        tickfont=dict(size=TICK_LABEL_FONTSIZE, color="royalblue"),
        showgrid=False,
        # The proportional ranges align these seven ticks with the commit ticks.
        range=[0, 97.5],
        tick0=0,
        dtick=15,
    ),
    yaxis2=dict(
        title=dict(
            text="Non-merge Commits",
            font=dict(size=XY_AXIS_CBAR_TITLE_FONTSIZE, color="orangered"),
        ),
        tickfont=dict(size=TICK_LABEL_FONTSIZE, color="orangered"),
        overlaying="y",
        side="right",
        showgrid=True,
        gridcolor="rgba(0,0,0,0.2)",
        range=[0, 3250],
        tick0=0,
        dtick=500,
        tickformat=",d",
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
