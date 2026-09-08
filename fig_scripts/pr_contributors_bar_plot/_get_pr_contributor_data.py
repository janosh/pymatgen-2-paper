"""Refresh the shared PR snapshot with authenticated, paginated GitHub CLI reads."""

import argparse
import json
import subprocess

from fig_scripts.pr_data import PR_FILE, RawPR, annual_counts, prepare_prs


def main() -> None:
    """Fetch all PR states so first-submission dates include unmerged PRs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="Read a previously fetched JSONL response")
    args = parser.parse_args()
    if args.input:
        with open(args.input, encoding="utf-8") as stream:
            response = stream.read()
    else:
        response = subprocess.check_output(
            [
                "gh",
                "api",
                "repos/materialsproject/pymatgen/pulls?state=all&per_page=100",
                "--paginate",
                "--jq",
                ".[] | {number,title,created_at,merged_at,author:.user.login,author_type:.user.type}",
            ],
            text=True,
        )
    raw_records: list[RawPR] = [json.loads(line) for line in response.splitlines()]
    records = prepare_prs(raw_records)
    with open(PR_FILE, "w", encoding="utf-8") as stream:
        json.dump(records, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(f"Saved {len(records)} merged non-bot PRs through 2025 to {PR_FILE}")
    print(dict(sorted(annual_counts(records).items())))


if __name__ == "__main__":
    main()
