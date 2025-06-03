"""
Plot a X-monthly number of active contributors bar plot,
with the color of bars showing total number of commits.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

BINNED_PERIOD_MONTH: int = 6
CSV_PATH: str = "contributor_commits_by_month.csv"

# Load and group by contributor_id
df = pd.read_csv(CSV_PATH)
df_grouped = df.groupby("contributor_id").sum(numeric_only=True)

# Convert column headers to datetime
date_columns = df_grouped.columns
df_grouped.columns = pd.to_datetime(date_columns, format="%Y-%m")

# Count active contributors
active_contributors = (df_grouped > 0).sum(axis=0)

# Sum total commits per month
total_commits = df_grouped.sum(axis=0)

# Bin both into X-month periods
active_contributors_binned = active_contributors.resample(
    f"{BINNED_PERIOD_MONTH}ME"
).sum()
total_commits_binned = total_commits.resample(f"{BINNED_PERIOD_MONTH}ME").sum()

# Use string for x-axis
index_str = active_contributors_binned.index.strftime("%Y-%m")

# Normalize total commits for coloring
norm = mpl.colors.Normalize(
    vmin=total_commits_binned.min(), vmax=total_commits_binned.max()
)
cmap = plt.get_cmap("RdYlGn_r")  # TODO: better colormap
colors = cmap(norm(total_commits_binned.values))

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(index_str, active_contributors_binned.values, color=colors)

# Colorbar
sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
cbar = plt.colorbar(sm, ax=ax)
cbar.set_label("Total Commits")


ax.set_title(f"Active Contributors per {BINNED_PERIOD_MONTH}-Month Period")
ax.set_ylabel("Number of Contributors")
ax.set_xlabel("Date")
plt.xticks(rotation=45)
plt.tight_layout()
plt.grid(True, axis="y", linestyle="--", alpha=0.5)

plt.savefig("active_contributors_colored.png", dpi=300)
plt.show()
