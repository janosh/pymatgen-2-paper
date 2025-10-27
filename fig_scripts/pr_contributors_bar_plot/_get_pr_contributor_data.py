# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests",
# ]
# ///
"""Get all merged PRs and calculate time since first contribution for each."""

import json
import os
import re
import time
from datetime import datetime

import requests

GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
REPO: str = "materialsproject/pymatgen"
DATAFILE: str = "_pr_contributors.json"

if not GITHUB_TOKEN:
    raise RuntimeError("Set GITHUB_TOKEN environment variable.")


# List of usernames to skip
SKIP_USER_PATTERNS = [
    r".*\[bot\]$",
]
compiled_skip_patterns = [re.compile(p) for p in SKIP_USER_PATTERNS]

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


def get_merged_prs(repo: str) -> list[dict]:
    """Fetch all merged PRs from the given GitHub repo, paginated until empty."""
    prs = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{repo}/pulls"
        params = {
            "state": "closed",
            "per_page": 100,
            "page": page,
        }
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        page_prs = response.json()

        merged = [pr for pr in page_prs if pr.get("merged_at")]
        if not merged:
            print(f"🛑 No more merged PRs after page {page}")
            break

        prs.extend(merged)
        print(f"📦 Loaded page {page}: {len(merged)} merged PRs")
        page += 1
        time.sleep(0.3)  # polite delay

    return prs


def get_first_pr_date(repo: str, username: str) -> str | None:
    """Return ISO datetime string of user's first PR in the repo."""
    url = "https://api.github.com/search/issues"
    params = {
        "q": f"repo:{repo} is:pr author:{username}",
        "sort": "created",
        "order": "asc",
        "per_page": 1,
    }
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 403:
        print(f"⚠️ Rate limited while querying {username}. Sleeping for 60 seconds...")
        time.sleep(60)
        return get_first_pr_date(repo, username)

    if response.status_code == 422:
        print(f"⚠️ Skipping {username} — user might have changed username")
        return None

    response.raise_for_status()
    items = response.json().get("items", [])
    if items:
        return items[0]["created_at"]
    return None


def main() -> None:
    prs = get_merged_prs(REPO)
    print(f"✅ Total merged PRs fetched: {len(prs)}")

    if os.path.exists(DATAFILE):
        with open(DATAFILE) as f:
            existing_data = {int(k): v for k, v in json.load(f).items()}
    else:
        existing_data = {}

    first_pr_dates: dict[str, datetime] = {
        v["author"]: datetime.fromisoformat(v["first_contribution_date"])
        for v in existing_data.values()
    }

    for pr in prs:
        pr_number = pr["number"]
        if pr_number in existing_data:
            continue  # skip already processed PR

        user = pr["user"]["login"]
        created_at = pr["created_at"]
        pr_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

        # Skip users matching patterns
        if any(pat.match(user) for pat in compiled_skip_patterns):
            print(f"⏭️ Skipping user: {user}")
            continue

        if user not in first_pr_dates:
            first_pr_iso = get_first_pr_date(REPO, user)
            if not first_pr_iso:
                continue
            first_date = datetime.fromisoformat(first_pr_iso.replace("Z", "+00:00"))
            first_pr_dates[user] = first_date
            time.sleep(2)  # avoid triggering 403 again
        else:
            first_date = first_pr_dates[user]

        years_since = (pr_date - first_date).days / 365.25
        print(
            f"PR #{pr_number:5} by {user:20} | {pr_date.date()} | {years_since:.2f} years since first PR"
        )

        existing_data[pr_number] = {
            "author": user,
            "title": pr["title"],
            "created_at": created_at,
            "first_contribution_date": first_date.isoformat(),
            "years_since_first": round(years_since, 2),
        }

        with open(DATAFILE, "w") as f:
            json.dump(existing_data, f, indent=2, sort_keys=True)

    print("✅ Finished.")


if __name__ == "__main__":
    main()
