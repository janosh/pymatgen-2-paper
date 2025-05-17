"""Plot a logscale monthly commit by contributor plot, with colorbar showing
years since first commit.

TODO:
- merge commits from potentially the same person (but different name/email)
"""

import pandas as pd
import matplotlib.pyplot as plt

df_commits = pd.read_csv("contributor_commits_by_month.csv")

# Reshape to long format
df_long = df_commits.melt(id_vars=["name", "email"], var_name="month", value_name="n_commits")

# Convert "month" column to datetime
df_long["month"] = pd.to_datetime(df_long["month"], format="%Y-%m")

# Filter: only contributors with at least 1 commit that month
df_long = df_long[df_long["n_commits"] > 0]

# Compute first commit date per contributor
first_commit = df_long.groupby(["name", "email"])["month"].min().reset_index()
first_commit.columns = ["name", "email", "first_commit"]
df_long = df_long.merge(first_commit, on=["name", "email"])

# Compute years since first contribution
df_long["years_since_first"] = (df_long["month"] - df_long["first_commit"]).dt.days / 365

# Plot with log scale
plt.figure(figsize=(14, 6))
sc = plt.scatter(
    df_long["month"],
    df_long["n_commits"],
    c=df_long["years_since_first"],
    cmap="plasma",
    alpha=0.7,
    s=35
)
plt.yscale("log")
plt.colorbar(sc, label="Years Since First Commit")
plt.xlabel("Month")
plt.ylabel("Commits (log scale)")
plt.title("Monthly Contributor Activity (Log Y, Dot = One Contributor per Month)")
plt.grid(True, which="both", linestyle='--', linewidth=0.5)
plt.tight_layout()
plt.savefig("monthly-commits.png")
