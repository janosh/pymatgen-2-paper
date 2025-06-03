"""
Number of commits by module heatmap (logscale colorscale).

Rows (modules) sorted by total number of commits (descending).
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go

from typing import Literal

INPUT_CSV: str = "monthly_commits_per_module.csv"
BIN_MONTHS: int = 6  # bin width in months

SORTING: Literal["total_num_of_commits", "chronology"] = "chronology"

EXCLUDE_MODULES: list[str] = [
    "ext",
    "cli",
    "vis",
    "command_line",
    "apps",
    "alchemy",
    "optimization",
]

# Load data
df = pd.read_csv(INPUT_CSV, index_col="time")
df.index = pd.to_datetime(df.index, format="%Y-%m")

df = df.drop(columns=EXCLUDE_MODULES)

# Resample into X-month bins
df_binned = df.resample(f"{BIN_MONTHS}ME").sum().rename_axis("time_binned")

# Transpose to (module vs time)
heatmap_data = df_binned.T
heatmap_data.columns = heatmap_data.columns.to_series().dt.strftime("%Y-%m")

# Sort modules (rows) by total commit count (descending)
print(f"Sorting modules by {SORTING}.")
if SORTING == "total_num_of_commits":
    heatmap_data["__total__"] = heatmap_data.sum(axis=1)
    heatmap_data = heatmap_data.sort_values("__total__", ascending=False)
    heatmap_data = heatmap_data.drop(columns="__total__")

# Sort modules from oldest (top) to latest
elif SORTING == "chronology":
    # Reload the original (unbinned) data to extract true first commit time
    df_raw = pd.read_csv(INPUT_CSV, index_col="time")
    df_raw.index = pd.to_datetime(df_raw.index, format="%Y-%m")

    df_raw = df_raw.drop(columns=EXCLUDE_MODULES)

    # Find the earliest month with a non-zero commit for each module
    first_commit_time = {
        module: df_raw[df_raw[module] > 0].index.min() for module in df_raw.columns
    }

    # Use this order to reorder the heatmap_data rows
    module_order = [
        mod for mod, _ in sorted(first_commit_time.items(), key=lambda x: x[1])
    ]
    heatmap_data = heatmap_data.loc[module_order]

else:
    raise ValueError(f"{SORTING=} not supported")

# Replace 0 with NaN (invisible) and apply log10
log_data = heatmap_data.replace(0, np.nan)
log_data = np.log10(log_data)

# Colorbar ticks still show original value
zmin = np.nanmin(log_data.values)
zmax = np.nanmax(log_data.values)

tick_vals = np.arange(np.floor(zmin), np.ceil(zmax) + 1)
tick_text = [str(int(10**v)) for v in tick_vals]

# Create heatmap
fig = go.Figure(
    data=go.Heatmap(
        z=log_data.values,
        x=log_data.columns,
        y=log_data.index,
        colorscale="temps",
        colorbar=dict(
            title=dict(text="Number of Commits", font=dict(size=20), side="right"),
            tickvals=tick_vals.tolist(),
            ticktext=tick_text,
            tickfont=dict(size=18),
        ),
        zmin=np.nanmin(log_data.values),
        zmax=np.nanmax(log_data.values),
        hovertemplate="Module=%{y}<br>Time=%{x}<br>log₁₀(Commits)=%{z:.2f}<extra></extra>",
        hoverongaps=False,
        showscale=True,
        connectgaps=False,
    )
)

fig.update_layout(
    title=f"Commits per Module (log scale, every {BIN_MONTHS} months)",
    title_x=0.5,
    title_font=dict(size=24),
    xaxis=dict(
        title=dict(text="Year", font=dict(size=20)),
        tickfont=dict(size=18),
        showgrid=False,
    ),
    yaxis=dict(
        title=dict(text="Module", font=dict(size=20)),
        tickfont=dict(size=18),
        autorange="reversed",
        showgrid=False,
    ),
    height=600,
    width=1400,
    plot_bgcolor="lightgrey",
)

fig.write_image("commits-per-module-heatmap-log.svg")
fig.show()
