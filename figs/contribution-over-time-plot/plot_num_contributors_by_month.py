"""
Plot a X-monthly number of active contributors bar plot.

TODO:
    - maybe we could add colorbar to the bars to show number of commits.
"""

import pandas as pd
import matplotlib.pyplot as plt

BINNED_PERIOD_MONTH: int = 6
CSV_PATH: str = "contributor_commits_by_month.csv"

# Load CSV and group by contributor ID
df = pd.read_csv(CSV_PATH)
df_grouped = df.groupby("contributor_id").sum(numeric_only=True)

# Convert column names to datetime index
date_columns = df_grouped.columns
df_grouped.columns = pd.to_datetime(date_columns, format="%Y-%m")

# Count only active contributors
active_contributors = (df_grouped > 0).sum(axis=0)

# Bin into X-month
resampled = active_contributors.resample(f"{BINNED_PERIOD_MONTH}ME").sum()

# Better x-axis labels
resampled.index = resampled.index.strftime("%Y-%m")

fig, ax = plt.subplots(figsize=(12, 6))
resampled.plot(kind="bar", ax=ax, color="steelblue")

ax.set_title(f"Active Contributors per {BINNED_PERIOD_MONTH}-Month Period")
ax.set_ylabel("Number of Contributors")
ax.set_xlabel("Date")
plt.xticks(rotation=45)
plt.tight_layout()
plt.grid(True, axis="y", linestyle="--", alpha=0.5)

plt.savefig("active_contributors.png", dpi=300)
plt.show()
