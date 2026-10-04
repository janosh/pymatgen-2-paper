# /// script
# dependencies = ["pandas", "numpy", "plotly", "kaleido"]
# ///

"""
Number of commits by package heatmap (log-scaled color scale).

Rows (packages) sorted by total number of commits (descending).
"""

import os
import subprocess

import numpy as np
import pandas as pd
import plotly.graph_objects as go

COLORSCALE: str = "viridis"
TICK_LABEL_FONTSIZE: int = 22
XY_AXIS_CBAR_TITLE_FONTSIZE: int = 24

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

PLOT_START_DATE: str = "2012-01-01"
PLOT_END_DATE: str = "2026-01-01"  # exclusive

CSV_CACHE: str = "_monthly_commits_per_package.csv"

# Set PMG_REPO_PATH to a local pymatgen clone to regenerate the commit counts,
# otherwise the committed CSV cache is plotted as-is.
PMG_REPO_PATH: str = os.environ.get("PMG_REPO_PATH", "")


def get_git_dates(path_prefixes: list[str]) -> list[str]:
    """Dates (YYYY-MM-DD) of non-merge commits touching any of path_prefixes in the plot window.

    Each commit is counted once even if it touches several of the given paths.
    """
    cmd = [
        *["git", "-C", PMG_REPO_PATH, "log", "main", "--no-merges"],
        *["--format=%ad", "--date=short"],
        *["--since", f"{PLOT_START_DATE}T00:00:00Z"],
        *["--until", f"{PLOT_END_DATE}T00:00:00Z"],
        *["--", *path_prefixes],
    ]
    process = subprocess.run(cmd, capture_output=True, encoding="utf-8", check=True)
    return process.stdout.strip().splitlines()


def get_monthly_commits_per_package() -> pd.DataFrame:
    """Monthly commit counts per package (columns) indexed by YYYY-MM strings."""
    package_series = {}

    for package in PACKAGES:
        # pymatgen moved from flat to src layout on 2024-06-26 (commit 9100860d7), so
        # count both path spellings over the full window instead of a cutoff date
        paths = [f"pymatgen/{package}", f"src/pymatgen/{package}"]
        all_dates = get_git_dates(paths)

        # Count commits per month
        dates = pd.to_datetime(all_dates, format="%Y-%m-%d")
        monthly = dates.to_series().dt.to_period("M").value_counts().sort_index()
        monthly.index = monthly.index.strftime("%Y-%m")
        package_series[package] = monthly

    df_git = pd.concat(package_series, axis=1).fillna(0).astype(int).sort_index()
    return df_git.rename_axis("time")


if PMG_REPO_PATH:
    df_git = get_monthly_commits_per_package()
    df_git.to_csv(CSV_CACHE)
    print(f"A copy of the data is saved to {CSV_CACHE}")
else:
    print(f"PMG_REPO_PATH not set, plotting cached {CSV_CACHE}")
    df_git = pd.read_csv(CSV_CACHE, index_col="time")

df_git.index = pd.to_datetime(df_git.index, format="%Y-%m")

# A complete monthly grid enforces the plotting window and retains empty periods.
# Anchor half-years in January, then label them by their June/December end dates.
calendar_months = pd.date_range(
    PLOT_START_DATE, PLOT_END_DATE, freq="MS", inclusive="left"
)
df_git = df_git.reindex(calendar_months, fill_value=0)
df_binned = df_git.resample("6MS").sum().rename_axis("time_binned")
df_binned.index += pd.offsets.MonthEnd(6)

# Transpose to (package vs time)
heatmap_data = df_binned.T
heatmap_data.columns = heatmap_data.columns.to_series().dt.strftime("%Y-%m")

# Sort packages (rows) by total commit count (descending)
heatmap_data = heatmap_data.loc[
    heatmap_data.sum(axis=1).sort_values(ascending=False).index
]

# Replace 0 with NaN (grey color) and apply log10
log_data = np.log10(heatmap_data.replace(0, np.nan))

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
        x=1.02,
        tickmode="array",
    ),
    zmin=zmin,
    zmax=zmax,
    customdata=heatmap_data.values,  # Original data for hover
    hovertemplate="<b>%{y}</b><br>Time: %{x}<br>Commits: %{customdata}<extra></extra>",
    hoverongaps=False,
    showscale=True,
    connectgaps=False,
)

year_tick_vals = heatmap_data.columns[::4].tolist()
if heatmap_data.columns[-1] not in year_tick_vals:
    year_tick_vals.append(heatmap_data.columns[-1])
fig.layout.xaxis.update(
    title=dict(text="Year", font=dict(size=XY_AXIS_CBAR_TITLE_FONTSIZE)),
    type="category",
    tickmode="array",
    tickvals=year_tick_vals,
    ticktext=[date[:4] for date in year_tick_vals],
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
fig.layout.update(
    height=600, width=1400, plot_bgcolor="lightgrey", margin=dict(l=0, r=0, t=10, b=0)
)

fig.write_image("../../figs/commits-per-package-heatmap.png", scale=4)
fig.show()
