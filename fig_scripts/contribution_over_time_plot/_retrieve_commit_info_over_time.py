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
    raise OSError("PMG_REPO_PATH is not set or is invalid.")

print("Extracting git commit metadata and line changes...")
git_log_output = subprocess.check_output(
    [
        "git",
        "-C",
        PMG_REPO_PATH,
        "log",
        "master",
        f"--until={CUTOFF_DATE}",
        "--numstat",
        "--pretty=format:--COMMIT--|%H|%an|%ae|%ad",
        "--date=short",
    ]
).decode("utf-8")

rows: list[CommitRow] = []
current_commit: CommitRow | None = None

# Rows are appended on their header line and their numstat lines are summed in place,
# so a commit ends at the next header or EOF, not at a formatting separator.
for line in git_log_output.strip().split("\n"):
    if line.startswith("--COMMIT--|"):
        current_commit = None
        parts = line.split("|")
        if len(parts) != 5:
            continue
        _, commit_hash, name, email, date_str = parts
        try:
            date = datetime.fromisoformat(date_str)  # --date=short is YYYY-MM-DD
        except ValueError:
            continue
        current_commit = {
            "commit": commit_hash,
            "name": name.strip(),
            "email": email.strip().lower(),
            "date": date,
            "lines_added": 0,
            "lines_removed": 0,
        }
        rows.append(current_commit)
    elif current_commit and line.strip():
        try:
            added, removed, _ = line.split("\t")
            if added != "-":
                current_commit["lines_added"] += int(added)
            if removed != "-":
                current_commit["lines_removed"] += int(removed)
        except ValueError:
            continue

# Convert to DataFrame
df = pd.DataFrame(rows)
df = df[~df["name"].str.lower().str.endswith("[bot]", na=False)]  # drop bots
df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
df["lines_changed"] = df["lines_added"] + df["lines_removed"]

# Generate contributor IDs by walking through (name, email)
contributor_id_map: dict[tuple[str, str], str] = {}
next_id = 1
ids: list[str] = []

for name, email in zip(df["name"], df["email"], strict=True):
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

# Commits and lines changed per user/month, one gzipped CSV each
grouped = df.groupby(["contributor_id", "name", "email", "month"])["lines_changed"]
print("✅ CSV files saved:")
for metric, counts in [("commits", grouped.size()), ("lines_changed", grouped.sum())]:
    table = counts.unstack(fill_value=0)
    table.columns = [month.strftime("%Y-%m") for month in table.columns]
    filename = f"contributor_{metric}_by_month.csv.gz"
    table.reset_index().to_csv(filename, index=False, compression="gzip")
    print(f"  - {filename}")
