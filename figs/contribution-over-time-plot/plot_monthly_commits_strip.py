import pandas as pd
import plotly.express as px


PERIOD_MONTHS: int = 6

df = pd.read_csv("contributor_commits_by_month.csv")

# Melt monthly columns into long format
df_long = df.melt(
    id_vars=["contributor_id", "name", "email"],
    var_name="month",
    value_name="n_commits",
)

df_long = df_long[df_long["n_commits"] > 0]

# Convert to datetime
df_long["month"] = pd.to_datetime(df_long["month"], format="%Y-%m")

# Group by contributor and month to get summed commits
df_grouped = df_long.groupby(["contributor_id", "month"], as_index=False)[
    "n_commits"
].sum()

# Bin into X-month intervals
df_grouped = df_grouped.set_index("month")
binned = (
    df_grouped.groupby("contributor_id", group_keys=False)
    .resample(f"{PERIOD_MONTHS}ME")
    .sum()
    .reset_index()
)

# Compute first commit date per contributor
first_commit = binned.groupby("contributor_id")["month"].min().rename("first_commit")
binned = binned.merge(first_commit, on="contributor_id")

# Compute years since first commit
binned["years_since_first"] = (binned["month"] - binned["first_commit"]).dt.days / 365

# Bin into labeled experience groups
binned["years_since_bin"] = pd.cut(
    binned["years_since_first"],
    bins=[0, 1, 2, 3, 5, 10, 20],
    labels=["<1y", "1–2y", "2–3y", "3–5y", "5–10y", "10y+"],
)

# Strip plot
fig = px.strip(
    binned,
    x="month",
    y="n_commits",
    color="years_since_bin",
    hover_data=["contributor_id"],
    title=f"Strip Chart of Commits (Binned every {PERIOD_MONTHS} months)",
    labels={"month": "Year", "n_commits": "Number of Commits"},
)

fig.update_yaxes(type="log")
fig.update_layout(showlegend=True)

fig.write_image("strip_chart.svg")
fig.show()
