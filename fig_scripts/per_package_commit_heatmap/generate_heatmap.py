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

COLORSCALE: str = "viridis"
TICK_LABEL_FONTSIZE: int = 18
PLOT_TITLE_FONTSIZE: int = 24
XY_AXIS_CBAR_TITLE_FONTSIZE: int = 20

PACKAGES: dict[str, str] = {
    # NOTE: for a file the `.py` suffix is necessary (e.g. `core/structure.py`)
    "command_line": "command_line",
    "symmetry": "symmetry",
    "alchemy": "alchemy",
    "core/structure.py": "core.structure",
    "core/periodic_table.py": "core.periodic_table",
    "io/vasp": "io.vasp",
    "transformations": "transformations",
    "analysis": "analysis",
    "optimization": "optimization",
    "electronic_structure": "electronic_structure",
    "phonon": "phonon",
    "vis": "vis",
    "entries": "entries",
}

BIN_MONTHS: int = 6  # bin width in months

ROW_SORTING: Literal["total_num_of_commits", "chronology", "alphabetical"] = (
    "total_num_of_commits"
)

# Start/end identifiers (can be dates or commit hashes)
START_COMMIT: str = "fa7f41d8bd769a04cca1f78242ebf072664c871d"
END_COMMIT: str = "2025-06-01"

# When pymatgen changed from flat to src layout
# commit: 9100860d7d938560610bcfadd04923b53756548e
LAYOUT_SWITCH_DATE: str = "2024-06-01"

# Get pymatgen repo path
if not (PMG_REPO_PATH := os.environ.get("PMG_REPO_PATH")):
    raise RuntimeError("PMG_REPO_PATH environment variable is not set.")


# Generate commit per package data
def run_git_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", PMG_REPO_PATH] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )


def get_git_dates(path_prefix: str, since: str, until: str) -> list[str]:
    cmd = [
        "log",
        "--no-merges",
        "--since",
        since,
        "--until",
        until,
        "--format=%ad",
        "--date=short",
        "--",
        path_prefix,
    ]
    return run_git_command(cmd).stdout.strip().splitlines()


def get_monthly_commits_per_package() -> pd.DataFrame:
    run_git_command(["checkout", "master"])

    package_series = {}

    for package in PACKAGES:
        all_dates = []

        # Flat layout (before June 2024)
        flat_path = f"pymatgen/{package}"
        all_dates.extend(get_git_dates(flat_path, START_COMMIT, LAYOUT_SWITCH_DATE))

        # Src layout (from June 2024 onward)
        src_path = f"src/pymatgen/{package}"
        all_dates.extend(get_git_dates(src_path, LAYOUT_SWITCH_DATE, END_COMMIT))

        # Count commits per month
        dates = pd.to_datetime(all_dates, format="%Y-%m-%d")
        monthly = dates.to_series().dt.to_period("M").value_counts().sort_index()
        monthly.index = monthly.index.to_timestamp()
        package_series[package] = monthly

    return pd.concat(package_series, axis=1).fillna(0).astype(int)


df_git = get_monthly_commits_per_package()

# Format index as YYYY-MM string
df_git.index = df_git.index.to_period("M").astype(str)
df_git.index.name = "time"

filename: str = "_monthly_commits_per_package.csv"
df_git.to_csv(filename)
print(f"A copy of the data is saved to {filename}")

df_git.index = pd.to_datetime(df_git.index, format="%Y-%m")

# Resample into X-month bins
df_binned = df_git.copy().resample(f"{BIN_MONTHS}ME").sum().rename_axis("time_binned")

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
    # Find the earliest month with a non-zero commit for each package
    first_commit_time = {
        package: df_git[df_git[package] > 0].index.min() for package in df_git.columns
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

# Replace 0 with NaN (grey color) and apply log10
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
    y=[PACKAGES[label] for label in log_data.index],
    colorscale=COLORSCALE,
    colorbar=dict(
        title=dict(
            text="Commits per Period",
            font=dict(size=XY_AXIS_CBAR_TITLE_FONTSIZE),
            side="right",
        ),
        tickvals=tick_vals.tolist(),
        ticktext=tick_text,
        tickfont=dict(size=TICK_LABEL_FONTSIZE),
        thickness=20,
        # len=0.8,
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

# title = f"Commits per Package (log scale, every {BIN_MONTHS} months)"
# fig.layout.title.update(text=title, x=0.5, font=dict(size=PLOT_TITLE_FONTSIZE))
fig.layout.xaxis.update(
    title=dict(text="Year", font=dict(size=XY_AXIS_CBAR_TITLE_FONTSIZE)),
    tickfont=dict(size=TICK_LABEL_FONTSIZE),
    showgrid=False,
)
fig.layout.yaxis.update(
    title=dict(text="Package", font=dict(size=XY_AXIS_CBAR_TITLE_FONTSIZE)),
    tickfont=dict(size=TICK_LABEL_FONTSIZE),
    autorange="reversed",
    showgrid=False,
    ticksuffix=" ",  # hack to add more spacing between tick labels and plot
)
fig.layout.update(height=500, width=1400, plot_bgcolor="lightgrey")

fig.write_image("../../paper/figs/commits-per-package-heatmap.pdf")
fig.show()
