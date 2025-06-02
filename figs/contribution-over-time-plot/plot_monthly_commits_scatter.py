"""
Plot a logscale monthly commit-by-contributor scatter plot, with colorbar showing
years since first commit. Contributors are identified by `contributor_id`.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

PERIOD_MONTHS: int = 6

df_commits: pd.DataFrame = pd.read_csv("contributor_commits_by_month.csv")

# Melt everything from the 4th column onward (assumed to be months)
df_long = df_commits.melt(
    id_vars=["contributor_id"],
    value_vars=df_commits.columns[3:],  # months start from 4th column
    var_name="month",
    value_name="n_commits",
)
df_long["month"] = pd.to_datetime(df_long["month"], format="%Y-%m")

# Filter out rows with 0 commits
df_long = df_long[df_long["n_commits"] > 0]


# Round each date to the nearest PERIOD_MONTHS interval
def floor_to_n_months(date, n=PERIOD_MONTHS):
    return pd.Timestamp(year=date.year, month=((date.month - 1) // n) * n + 1, day=1)


df_long["period"] = df_long["month"].apply(
    lambda x: floor_to_n_months(x, n=PERIOD_MONTHS)
)

# Aggregate total commits per contributor per period
df_binned = (
    df_long.groupby(["contributor_id", "period"])["n_commits"].sum().reset_index()
)

# Calculate first commit period for each contributor
first_commit = df_binned.groupby("contributor_id")["period"].min().reset_index()
first_commit.columns = ["contributor_id", "first_commit"]
df_binned = df_binned.merge(first_commit, on="contributor_id")
df_binned["years_since_first"] = (
    df_binned["period"] - df_binned["first_commit"]
).dt.days / 365

# Add small jitter to reduce scatters overlap
jitter_strength = 0.1
df_binned["n_commits_jittered"] = df_binned["n_commits"] + np.random.uniform(
    -jitter_strength, jitter_strength, size=len(df_binned)
)

plt.figure(figsize=(14, 6))
scatter = plt.scatter(
    df_binned["period"],
    df_binned["n_commits_jittered"],
    c=df_binned["years_since_first"],
    cmap="plasma",
    alpha=0.8,
    s=35,
)
plt.yscale("log")

# X/Y ticks and label
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.xlabel(f"Year (Binned Every {PERIOD_MONTHS} Months)", fontsize=18)
plt.ylabel("Number of Commits", fontsize=18)

ax = plt.gca()
ax.tick_params(axis="both", width=1.5, length=5)

plt.title(f"Contributor Activity Binned by {PERIOD_MONTHS}-Month Periods", fontsize=18)

ax.set_axisbelow(True)
ax.grid(True, which="both", linestyle="--", linewidth=0.75, zorder=0)

# Thicken plot borders
for spine in plt.gca().spines.values():
    spine.set_linewidth(2)

# Colorbar
cbar = plt.colorbar(scatter)
cbar.set_label("Years Since First Commit", fontsize=18)
cbar.ax.tick_params(labelsize=16, width=1.5, length=5)

plt.tight_layout()

plt.savefig(f"commits_per_contributor_{PERIOD_MONTHS}m_bins.png", dpi=300)
plt.show()
