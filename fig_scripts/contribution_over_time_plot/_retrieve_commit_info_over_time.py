"""Aggregate annual non-merge commit and contributor activity from pymatgen Git history.

PMG_REPO_PATH is required; CONTRIBUTION_OUTPUT_PATH optionally overrides the CSV path.
Author names and emails link identities transiently and are not written to disk.
"""

import csv
import os
import subprocess

START_YEAR = 2012
CUTOFF_YEAR = 2026
OUTPUT_PATH = os.environ.get(
    "CONTRIBUTION_OUTPUT_PATH",
    f"{os.path.dirname(__file__)}/contributor_activity_by_year.csv",
)
PMG_REPO_PATH = os.environ.get("PMG_REPO_PATH")
if PMG_REPO_PATH is None or not os.path.isdir(PMG_REPO_PATH):
    raise OSError(f"PMG_REPO_PATH is not a directory: {PMG_REPO_PATH!r}")

print("Extracting non-merge Git commit metadata...")
git_log_output = subprocess.check_output(
    [
        "git",
        "-C",
        PMG_REPO_PATH,
        "log",
        "main",
        "--no-merges",
        # Git's date filters use committer timestamps; bin and filter author years below.
        "--pretty=format:%an%x1f%ae%x1f%ad",
        "--date=format:%Y",
    ],
    text=True,
)

annual_contributors: dict[int, list[str]] = {
    year: [] for year in range(START_YEAR, CUTOFF_YEAR)
}
# Join all matching names/emails before counting annual contributors.
parents: dict[str, str] = {}


def find_root(identity: str) -> str:
    """Resolve an alias group, compressing paths for subsequent lookups."""
    parents.setdefault(identity, identity)
    while identity != parents[identity]:
        parents[identity] = parents[parents[identity]]
        identity = parents[identity]
    return identity


for line in git_log_output.splitlines():
    try:
        name, email, year_text = line.split("\x1f")
        year = int(year_text)
    except ValueError as exc:
        raise ValueError(f"Invalid Git log record: {line!r}") from exc
    name = name.strip()
    if name.lower().endswith("[bot]") or year not in annual_contributors:
        continue
    name_key = f"name:{name}"
    parents[find_root(name_key)] = find_root(f"email:{email.strip().lower()}")
    annual_contributors[year].append(name_key)

if not any(annual_contributors.values()):
    raise ValueError(
        f"No non-bot, non-merge commits in {PMG_REPO_PATH!r} "
        f"with author years in [{START_YEAR}, {CUTOFF_YEAR})"
    )

with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as output_file:
    writer = csv.writer(output_file, lineterminator="\n")
    writer.writerow(["year", "active_contributors", "commits"])
    for year, authors in annual_contributors.items():
        writer.writerow(
            [year, len({find_root(author) for author in authors}), len(authors)]
        )
print(f"Saved {OUTPUT_PATH}")
