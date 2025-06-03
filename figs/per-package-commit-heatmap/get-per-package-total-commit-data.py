"""
Extract per-package number of commits data.
"""

import os
import sys
import subprocess
import pandas as pd

PACKAGES: list[str] = [
    "command_line",
    "ext",
    "symmetry",
    "alchemy",
    "core",
    "io",
    "transformations",
    "analysis",
    "optimization",
    "apps",
    "electronic_structure",
    "phonon",
    "vis",
    "cli",
    "entries",
]

# Start/end identifiers (can be dates or commit hashes)
START_COMMIT: str = "fa7f41d8bd769a04cca1f78242ebf072664c871d"
END_COMMIT: str = "2025-06-01"

# Switch point when pymatgen changed from flat to src layout
LAYOUT_SWITCH_DATE: str = "2024-06-01"

# Get repo path from environment
if not (PMG_REPO_PATH := os.environ.get("PMG_REPO_PATH")):
    print("Error: PMG_REPO_PATH environment variable is not set.")
    sys.exit(1)


def run_git_command(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", PMG_REPO_PATH] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )


def get_git_dates(path_prefix: str, since: str, until: str) -> list[str]:
    cmd = [
        "log",
        "--no-merges",
        "--since",
        since,
        "--until",
        until,
        "--format=%ad",
        "--date=short",
        "--",
        path_prefix,
    ]
    return run_git_command(cmd).stdout.strip().splitlines()


def get_monthly_commits_per_package() -> pd.DataFrame:
    run_git_command(["checkout", "master"])

    package_series = {}

    for package in PACKAGES:
        all_dates = []

        # Flat layout (before June 2024)
        flat_path = f"pymatgen/{package}/"
        all_dates.extend(get_git_dates(flat_path, START_COMMIT, LAYOUT_SWITCH_DATE))

        # Src layout (from June 2024 onward)
        src_path = f"src/pymatgen/{package}/"
        all_dates.extend(get_git_dates(src_path, LAYOUT_SWITCH_DATE, END_COMMIT))

        # Count commits per month
        dates = pd.to_datetime(all_dates, format="%Y-%m-%d")
        monthly = dates.to_series().dt.to_period("M").value_counts().sort_index()
        monthly.index = monthly.index.to_timestamp()
        package_series[package] = monthly

    return pd.concat(package_series, axis=1).fillna(0).astype(int)


if __name__ == "__main__":
    df = get_monthly_commits_per_package()

    # Format index as YYYY-MM string
    df.index = df.index.to_period("M").astype(str)
    df.index.name = "time"

    df.to_csv("monthly_commits_per_package.csv")
