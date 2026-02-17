# /// script
# dependencies = ["pandas"]
# ///

"""
Extract Git commit history from a local pymatgen repo and summarizes the number of commits
and number of lines changed per contributor for each calendar month.

Environment Variables:
    PMG_REPO_PATH (optional): Path to the pymatgen repo.

Output:
    A CSV file named 'contributor_commits_by_month.csv' is saved in the current directory.

Notes:
- The same person may appear multiple times due to variations in name or email. For example:
    First Last, personal@email.com
    First M. Last, personal@email.com
    First M. Last, work@email.com

    A contributor ID is assigned heuristically: if either name or email matches a known contributor,
    they share the same ID.
"""

import os
import subprocess
from datetime import datetime
from typing import TypedDict

import pandas as pd


class CommitRow(TypedDict):
    """Typed schema for parsed git commit metadata."""

    commit: str
    name: str
    email: str
    date: datetime
    lines_added: int
    lines_removed: int


CUTOFF_DATE = "2026-01-01"
PMG_REPO_PATH = os.environ.get("PMG_REPO_PATH")
if PMG_REPO_PATH is None or not os.path.isdir(PMG_REPO_PATH):
    raise EnvironmentError("PMG_REPO_PATH is not set or is invalid.")

subprocess.run(["git", "-C", PMG_REPO_PATH, "checkout", "master"], check=True)
print("Extracting git commit metadata and line changes...")
git_log_output = subprocess.check_output(
    [
        "git",
        "-C",
        PMG_REPO_PATH,
        "log",
        f"--until={CUTOFF_DATE}",
        "--numstat",
        "--pretty=format:--COMMIT--|%H|%an|%ae|%ad",
        "--date=short",
    ]
).decode("utf-8")

rows: list[CommitRow] = []
current_commit: CommitRow | None = None

for line in git_log_output.strip().split("\n"):
    if line.startswith("--COMMIT--|"):
        parts = line.split("|")
        if len(parts) == 5:
            _, commit_hash, name, email, date_str = parts
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
                current_commit = {
                    "commit": commit_hash,
                    "name": name.strip(),
                    "email": email.strip().lower(),
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
df = df[~df["name"].str.contains(r"\[bot\]", case=False, na=False)]  # drop bots
df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
df["lines_changed"] = df["lines_added"] + df["lines_removed"]

# Generate contributor IDs by walking through (name, email)
contributor_id_map: dict[tuple[str, str], str] = {}
next_id = 1
ids: list[str] = []

for name, email in zip(df["name"], df["email"]):
    key: tuple[str, str] | None = None
    for existing_key in contributor_id_map:
        if name == existing_key[0] or email == existing_key[1]:
            key = existing_key
            break
    if key is None:
        key = (name, email)
        contributor_id_map[key] = f"user_{next_id:04d}"
        next_id += 1
    ids.append(contributor_id_map[key])

df["contributor_id"] = ids

# Group for commits per user/month
commit_counts = (
    df.groupby(["contributor_id", "name", "email", "month"])
    .size()
    .unstack(fill_value=0)
)
commit_counts.columns = [d.strftime("%Y-%m") for d in commit_counts.columns]
commit_counts = commit_counts.reset_index()

# Group for lines changed per user/month
lines_changed = (
    df.groupby(["contributor_id", "name", "email", "month"])["lines_changed"]
    .sum()
    .unstack(fill_value=0)
)
lines_changed.columns = [d.strftime("%Y-%m") for d in lines_changed.columns]
lines_changed = lines_changed.reset_index()

# Save both CSVs
commit_counts.to_csv(
    "contributor_commits_by_month.csv.gz", index=False, compression="gzip"
)
lines_changed.to_csv(
    "contributor_lines_changed_by_month.csv.gz", index=False, compression="gzip"
)

print("✅ CSV files saved:")
print("  - contributor_commits_by_month.csv.gz")
print("  - contributor_lines_changed_by_month.csv.gz")
