"""
Plot commits as stacked area chart.
"""

import pandas as pd
import plotly.express as px


CSV_PATH = "contributor_commits_by_month.csv"
MIN_TOTAL_COMMITS = 10  # Minimum total commits to be plotted

df = pd.read_csv(CSV_PATH)

# Melt columns
id_vars = ["contributor_id", "name", "email"]
date_cols = [col for col in df.columns if col not in id_vars]
df_long = df.melt(
    id_vars=id_vars, value_vars=date_cols, var_name="month", value_name="commits"
)

# Convert month string to datetime
df_long["month"] = pd.to_datetime(df_long["month"])

# Group by contributor_id + month (merging multiple emails/names)
df_grouped = df_long.groupby(["contributor_id", "month"], as_index=False).agg(
    {"commits": "sum"}
)

# Filter out contributors with total commits below threshold
total = df_grouped.groupby("contributor_id")["commits"].sum()
valid_ids = total[total >= MIN_TOTAL_COMMITS].index
df_filtered = df_grouped[df_grouped["contributor_id"].isin(valid_ids)]

print(
    f"Number of contributors with at least {MIN_TOTAL_COMMITS} commits: {len(valid_ids)}"
)

fig = px.area(
    df_filtered,
    x="month",
    y="commits",
    color="contributor_id",
    title="Monthly Git Commits by Contributor (Stacked Area)",
)

fig.update_layout(
    xaxis_title="Month",
    yaxis_title="Commits",
    hovermode="x unified",
    template="plotly_white",
    # showlegend=False,  # User ID doesn't really give much info
)

# fig.show()
fig.write_image("commits_area_plot.svg")
