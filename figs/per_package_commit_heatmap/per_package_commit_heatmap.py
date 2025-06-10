# /// script
# dependencies = ["pandas", "numpy", "plotly", "kaleido"]
# ///

"""
Number of commits by package heatmap (log-scaled color scale).

Rows (packages) sorted by total number of commits (descending).
"""

import os
import subprocess
from typing import Literal

import numpy as np
import pandas as pd
import plotly.graph_objects as go

INPUT_CSV: str = "monthly_commits_per_package.csv"
BIN_MONTHS: int = 6  # bin width in months

RowSorting = Literal["total_num_of_commits", "chronology", "alphabetical"]
ROW_SORTING: RowSorting = "total_num_of_commits"

EXCLUDE_PACKAGES: tuple[str, ...] = (
    "ext",
    "cli",
    "vis",
    "command_line",
    "apps",
    "alchemy",
    "optimization",
)

# Load data
if not os.path.isfile(INPUT_CSV):
    print(f"{INPUT_CSV} not found. Running script to generate it...")
    result = subprocess.run(
        ["uv", "run", "_get_per_package_total_commit_data.py"],
        capture_output=True,
        text=True,
        check=True,
    )

df_git = pd.read_csv(INPUT_CSV, index_col="time")
df_git.index = pd.to_datetime(df_git.index, format="%Y-%m")

df_git = df_git.drop(columns=[*EXCLUDE_PACKAGES])

# Resample into X-month bins
df_binned = df_git.resample(f"{BIN_MONTHS}ME").sum().rename_axis("time_binned")

# Transpose to (package vs time)
heatmap_data = df_binned.T
heatmap_data.columns = heatmap_data.columns.to_series().dt.strftime("%Y-%m")

# Sort packages (rows) by total commit count (descending)
print(f"Sorting packages by {ROW_SORTING}.")
if ROW_SORTING == "total_num_of_commits":
    heatmap_data["__total__"] = heatmap_data.sum(axis=1)
    heatmap_data = heatmap_data.sort_values("__total__", ascending=False)
    heatmap_data = heatmap_data.drop(columns="__total__")

# Sort packages from oldest (top) to latest
elif ROW_SORTING == "chronology":
    # Reload the original (unbinned) data to extract true first commit time
    df_raw = pd.read_csv(INPUT_CSV, index_col="time")
    df_raw.index = pd.to_datetime(df_raw.index, format="%Y-%m")

    df_raw = df_raw.drop(columns=EXCLUDE_PACKAGES)

    # Find the earliest month with a non-zero commit for each package
    first_commit_time = {
        package: df_raw[df_raw[package] > 0].index.min() for package in df_raw.columns
    }

    # Use this order to reorder the heatmap_data rows
    package_order = [
        mod for mod, _ in sorted(first_commit_time.items(), key=lambda x: x[1])
    ]
    heatmap_data = heatmap_data.loc[package_order]

elif ROW_SORTING == "alphabetical":
    heatmap_data = heatmap_data.sort_index()

else:
    raise ValueError(f"{ROW_SORTING=} not supported")

# Replace 0 with NaN (invisible) and apply log10
log_data = heatmap_data.replace(0, np.nan)
log_data = np.log10(log_data)

# Colorbar ticks still show original value
zmin = np.nanmin(log_data.values)
zmax = np.nanmax(log_data.values)

tick_vals = np.arange(np.floor(zmin), np.ceil(zmax) + 1)
tick_text = [str(int(10**v)) for v in tick_vals]

fig = go.Figure()
fig.add_heatmap(
    z=log_data.values,
    x=log_data.columns,
    y=log_data.index,
    colorscale="viridis",
    colorbar=dict(
        title=dict(text="Commits per Period", font=dict(size=18), side="right"),
        tickvals=tick_vals.tolist(),
        ticktext=tick_text,
        tickfont=dict(size=16),
        thickness=20,
        len=0.8,
        x=1.02,
        tickmode="array",
    ),
    zmin=np.nanmin(log_data.values),
    zmax=np.nanmax(log_data.values),
    customdata=heatmap_data.values,  # Original data for hover
    hovertemplate="<b>%{y}</b><br>Time: %{x}<br>Commits: %{customdata}<extra></extra>",
    hoverongaps=False,
    showscale=True,
    connectgaps=False,
)

title = f"Commits per Package (log scale, every {BIN_MONTHS} months)"
fig.layout.title.update(text=title, x=0.5, font=dict(size=24))
fig.layout.xaxis.update(
    title=dict(text="Year", font=dict(size=20)), tickfont=dict(size=18), showgrid=False
)
fig.layout.yaxis.update(
    title=dict(text="Package", font=dict(size=20)),
    tickfont=dict(size=18),
    autorange="reversed",
    showgrid=False,
    ticks="outside",
    tickcolor="white",
    ticksuffix=" ",
)
fig.layout.update(height=500, width=1400, plot_bgcolor="lightgrey")

fig.write_image("commits_per_package_heatmap_log.svg")
fig.show()
