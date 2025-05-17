"""Plot a logscale monthly commit by contributor plot, with colorbar showing
years since first commit.
"""

import pandas as pd
import matplotlib.pyplot as plt

# GLOBAL: binning interval in months
PERIOD_MONTHS = 3

# Load the commit data
df_commits = pd.read_csv("contributor_commits_by_month.csv")

# Melt to long format (name, email, month, n_commits)
df_long = df_commits.melt(id_vars=["name", "email"], var_name="month", value_name="n_commits")
df_long["month"] = pd.to_datetime(df_long["month"], format="%Y-%m")

# Filter out rows with 0 commits
df_long = df_long[df_long["n_commits"] > 0]

# Round the month to a binned period
def floor_to_n_months(date, n=PERIOD_MONTHS):
    return pd.Timestamp(year=date.year, month=((date.month - 1) // n) * n + 1, day=1)

df_long["period"] = df_long["month"].apply(lambda x: floor_to_n_months(x, n=PERIOD_MONTHS))

# Aggregate total commits per contributor per binned period
df_binned = df_long.groupby(["name", "email", "period"])["n_commits"].sum().reset_index()

# Determine first contribution period for each contributor
first_commit = df_binned.groupby(["name", "email"])["period"].min().reset_index()
first_commit.columns = ["name", "email", "first_commit"]
df_binned = df_binned.merge(first_commit, on=["name", "email"])
df_binned["years_since_first"] = (df_binned["period"] - df_binned["first_commit"]).dt.days / 365

# Plotting
plt.figure(figsize=(14, 6))
sc = plt.scatter(
    df_binned["period"],
    df_binned["n_commits"],
    c=df_binned["years_since_first"],
    cmap="plasma",
    alpha=0.7,
    s=35
)
plt.yscale("log")
plt.colorbar(sc, label="Years Since First Commit")
plt.xlabel(f"Time (Binned Every {PERIOD_MONTHS} Months)")
plt.ylabel("Commits (log scale)")
plt.title(f"Contributor Activity Binned by {PERIOD_MONTHS}-Month Periods")
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.tight_layout()
fig_name = f"commits_per_contributor_{PERIOD_MONTHS}m_bins.png"
plt.savefig(fig_name, dpi=300)
print(f"Plot saved as: {fig_name}")
