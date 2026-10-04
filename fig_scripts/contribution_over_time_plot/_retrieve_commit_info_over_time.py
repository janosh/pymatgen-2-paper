# /// script
# dependencies = ["pandas"]
# ///

"""Aggregate annual non-merge commit and contributor activity from pymatgen Git history.

The output contains only the two annual series needed by the figure. Author names and
email addresses are used transiently to reconcile aliases but are not written to disk.

Environment Variables:
    PMG_REPO_PATH: Path to a local pymatgen repository.
"""

import os
import subprocess
from pathlib import Path

import pandas as pd

START_DATE = "2012-01-01"
CUTOFF_DATE = "2026-01-01"
OUTPUT_PATH = Path(
    os.environ.get(
        "CONTRIBUTION_OUTPUT_PATH",
        Path(__file__).with_name("contributor_activity_by_year.csv"),
    )
)
PMG_REPO_PATH = os.environ.get("PMG_REPO_PATH")
if PMG_REPO_PATH is None or not os.path.isdir(PMG_REPO_PATH):
    raise OSError("PMG_REPO_PATH is not set or is invalid.")

print("Extracting non-merge Git commit metadata...")
git_log_output = subprocess.check_output(
    [
        "git",
        "-C",
        PMG_REPO_PATH,
        "log",
        "main",
        "--no-merges",
        f"--since={START_DATE}",
        f"--until={CUTOFF_DATE}",
        "--pretty=format:%an%x1f%ae%x1f%ad",
        "--date=short",
    ],
    text=True,
)

records: list[dict[str, str]] = []
for line in git_log_output.splitlines():
    parts = line.split("\x1f")
    if len(parts) != 3:
        continue
    name, email, date = parts
    name = name.strip()
    if name.lower().endswith("[bot]"):
        continue
    records.append({"name": name, "email": email.strip().lower(), "year": date[:4]})

if not records:
    raise ValueError("Git history contains no non-bot commits before the cutoff")

df = pd.DataFrame(records)

# Reconcile aliases using the same heuristic as the original figure: an exact author
# name or lower-cased email match assigns a record to an existing contributor.
contributor_id_map: dict[tuple[str, str], str] = {}
contributor_ids: list[str] = []
for name, email in zip(df["name"], df["email"], strict=True):
    matching_key = next(
        (key for key in contributor_id_map if name == key[0] or email == key[1]),
        None,
    )
    if matching_key is None:
        matching_key = (name, email)
        contributor_id_map[matching_key] = f"user_{len(contributor_id_map) + 1:04d}"
    contributor_ids.append(contributor_id_map[matching_key])

df["contributor_id"] = contributor_ids
annual = (
    df.groupby("year")
    .agg(
        active_contributors=("contributor_id", "nunique"),
        commits=("contributor_id", "size"),
    )
    .reset_index()
)
annual.to_csv(OUTPUT_PATH, index=False)
print(f"Saved {OUTPUT_PATH}")
