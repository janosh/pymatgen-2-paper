# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "matplotlib",
#     "pandas",
# ]
# ///
import json
from collections import defaultdict
from datetime import datetime
import math

import matplotlib.pyplot as plt
import pandas as pd

# Load PR data
with open("_pr_contributors.json") as f:
    data = json.load(f)

# Bin PRs by year
binned = defaultdict(lambda: defaultdict(int))

for pr in data.values():
    year = datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00")).year
    ysf: float = pr["years_since_first"]

    if math.isclose(ysf, 0, abs_tol=7 / 365):
        group = "New"
    elif ysf < 1:
        group = "<1 year"
    elif ysf < 3:
        group = "1-3 years"
    elif ysf < 6:
        group = "3-6 years"
    else:
        group = ">6 years"

    binned[year][group] += 1

# Convert to DataFrame
df = pd.DataFrame(binned).T.fillna(0).astype(int)
df = df.sort_index()  # sort by year

# Ensure consistent column order
columns = ["New", "<1 year", "1-3 years", "3-6 years", ">6 years"]
for col in columns:
    if col not in df:
        df[col] = 0
df = df[columns]

# Plot
colors = [
    "#1f77b4",  # blue
    "#ff7f0e",  # orange
    "#2ca02c",  # green
    "#d62728",  # red
    "#9467bd",  # purple
]

df.plot(kind="bar", stacked=True, color=colors, width=0.8)

plt.title("Pull Requests by Year")
plt.xlabel("Year")
plt.ylabel("Total Number of Pull Requests")
plt.legend(title="Year Since First PR", reverse=True)
plt.tight_layout()
plt.grid(axis="y", linestyle="--", alpha=0.4)

plt.savefig("pr_since_1st.svg", dpi=300, format="svg")
