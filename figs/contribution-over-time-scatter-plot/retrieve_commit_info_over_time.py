"""
Extracts Git commit history from a local pymatgen repo and summarizes the number of commits
and number of lines changed per contributor for each calendar month.

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
if PMG_REPO_PATH is None or not os.path.isdir(PMG_REPO_PATH):
    raise EnvironmentError("PMG_REPO_PATH is not set or is invalid.")

print("Extracting git commit metadata and line changes...")

# Get commit metadata and lines added/removed
git_log_output = subprocess.check_output([
    "git", "-C", PMG_REPO_PATH,
    "log", "--numstat", "--pretty=format:--COMMIT--|%H|%an|%ae|%ad", "--date=short"
]).decode("utf-8")

rows = []
current_commit = None

for line in git_log_output.strip().split("\n"):
    if line.startswith("--COMMIT--|"):
        parts = line.split("|")
        if len(parts) == 5:
            _, commit_hash, name, email, date_str = parts
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
                current_commit = {
                    "commit": commit_hash,
                    "name": name,
                    "email": email,
                    "date": date,
                    "lines_added": 0,
                    "lines_removed": 0,
                }
            except ValueError:
                current_commit = None
    elif current_commit and line.strip():
        try:
            added, removed, _ = line.split("\t")
            if added != "-":
                current_commit["lines_added"] += int(added)
            if removed != "-":
                current_commit["lines_removed"] += int(removed)
        except ValueError:
            continue
    elif not line.strip() and current_commit:
        rows.append(current_commit)
        current_commit = None

# Convert to DataFrame
df = pd.DataFrame(rows)
df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
df["lines_changed"] = df["lines_added"] + df["lines_removed"]

# Group: commits per user/month
commit_counts = df.groupby(["name", "email", "month"]).size().unstack(fill_value=0)
commit_counts.columns = [d.strftime("%Y-%m") for d in commit_counts.columns]

# Group: lines changed per user/month
lines_changed = df.groupby(["name", "email", "month"])["lines_changed"].sum().unstack(fill_value=0)
lines_changed.columns = [d.strftime("%Y-%m") for d in lines_changed.columns]

# Save both
commit_counts.reset_index().to_csv("contributor_commits_by_month.csv", index=False)
lines_changed.reset_index().to_csv("contributor_lines_changed_by_month.csv", index=False)

print("✅ CSV files saved:")
print(" - contributor_commits_by_month.csv")
print(" - contributor_lines_changed_by_month.csv")
