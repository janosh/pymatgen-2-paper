"""
Number of commits by module heatmap.
"""

import pandas as pd
import plotly.express as px

INPUT_CSV: str = "monthly_commits_per_module.csv"
BIN_MONTHS: int = 3  # set your desired bin size here

# Load and process data
df = pd.read_csv(INPUT_CSV, index_col="time")
df.index = pd.to_datetime(df.index, format="%Y-%m")

# Resample to bins
df_binned = df.resample(f"{BIN_MONTHS}ME").sum().rename_axis("time_binned")

# Transpose for heatmap (modules = rows, time = cols)
heatmap_data = df_binned.T

# Format columns as short labels like "2023-01"
heatmap_data.columns = heatmap_data.columns.to_series().dt.strftime("%Y-%m")

fig = px.imshow(
    heatmap_data,
    labels=dict(x="Time", y="Module", color="# Commits"),
    aspect="auto",
    color_continuous_scale="Viridis",
)

fig.update_layout(
    title=f"Commits per Module (every {BIN_MONTHS} months)",
    title_x=0.5,
    title_font=dict(size=20),
    xaxis=dict(
        title=dict(text="Year", font=dict(size=20)),
        tickfont=dict(size=16),
    ),
    yaxis=dict(
        title=dict(text="Module", font=dict(size=20)),
        tickfont=dict(size=16),
    ),
    coloraxis_colorbar=dict(
        title=dict(text="Number of Commits", font=dict(size=20), side="right"),
        tickfont=dict(size=16),
    ),
    height=600,
    width=1400,
)

fig.write_image("commits-per-module-heatmap.svg")
fig.show()
