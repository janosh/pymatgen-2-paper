"""
Extracts Git commit history from a local pymatgen repo and summarizes the number of commits
per contributor (identified by name and email) for each calendar month.

Environment Variables:
    PMG_REPO_PATH (optional): Path to the pymatgen repo.

Output:
    A CSV file named 'contributor_commits_by_month.csv' is saved in the current directory.

Notes:
- Contributors may appear multiple times due to variations in name or email. For example:
    First Last, personal@email.com
    First M. Last, personal@email.com
    First M. Last, work@email.com

    While I don't think there's fully robust automated solution, grouping by either
    name OR email (in the plotter script) may be a good starting point.
"""



import os
import subprocess
from datetime import datetime

import pandas as pd

PMG_REPO_PATH = os.environ.get("PMG_REPO_PATH")
if not os.path.isdir(PMG_REPO_PATH):
    raise EnvironmentError("PMG_REPO_PATH is not set or is invalid.")

# Extract commit info (hash, author name/email, date)
print("Extracting git commit history...")
git_log_output = subprocess.check_output([
    "git", "-C", PMG_REPO_PATH,
    "log", "--pretty=format:%H|%an|%ae|%ad", "--date=short"
]).decode("utf-8")

# Parse lines
data = []
for line in git_log_output.strip().split("\n"):
    try:
        commit_hash, name, email, date_str = line.split("|")
        commit_date = datetime.strptime(date_str, "%Y-%m-%d")
        data.append({"commit": commit_hash, "name": name, "email": email, "date": commit_date})
    except ValueError:
        continue

df = pd.DataFrame(data)

# Bin by calendar month
df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()

# Count commits per user per month
commit_counts = df.groupby(["name", "email", "month"]).size().unstack(fill_value=0)

# Format columns like "2020-01"
commit_counts.columns = [d.strftime("%Y-%m") for d in commit_counts.columns]

# Output to CSV
output_file = "contributor_commits_by_month.csv"
commit_counts.reset_index().to_csv(output_file, index=False)
print(f"✅ CSV saved to: {output_file}")
