"""Extract number of stars/forks for each repo."""

import os
import time
import requests
import pandas as pd

INPUT_FILE = "pymatgen_dependents.csv"
OUTPUT_FILE = "pymatgen_dependents_with_stars.csv"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def fetch_repo_info(full_name: str) -> dict:
    """Fetch stargazers_count and forks_count from GitHub API for owner/repo slug."""
    url = f"https://api.github.com/repos/{full_name}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "pymatgen-dependents-scraper",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    r = requests.get(url, headers=headers)

    # Handle rate limits
    if r.status_code == 403 and r.headers.get("X-RateLimit-Remaining") == "0":
        reset_ts = int(r.headers.get("X-RateLimit-Reset", time.time() + 60))
        wait = max(0, reset_ts - int(time.time())) + 5
        print(f"Rate limit reached, sleeping {wait}s…")
        time.sleep(wait)
        return fetch_repo_info(full_name)

    if r.status_code != 200:
        print(f"Failed {full_name}: {r.status_code}")
        return {"stars": None, "forks": None}

    data = r.json()
    return {
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
    }


def main():
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} repos from {INPUT_FILE}")

    # Always ensure owner/repo slug is available
    df["owner_repo"] = df["repo_url"].str.replace(
        "https://github.com/", "", regex=False
    )

    # Resume if output exists
    if os.path.exists(OUTPUT_FILE):
        df_out = pd.read_csv(OUTPUT_FILE)
        if "owner_repo" not in df_out.columns:  # fix older runs
            df_out["owner_repo"] = df_out["repo_url"].str.replace(
                "https://github.com/", "", regex=False
            )
        done = set(df_out["owner_repo"])
        print(f"Resuming: already enriched {len(done)} repos")
    else:
        df_out = df.copy()
        df_out["stars"] = None
        df_out["forks"] = None
        done = set()

    for i, row in df.iterrows():
        full_name = row["owner_repo"]
        if full_name in done:
            continue

        info = fetch_repo_info(full_name)
        df_out.loc[df_out["owner_repo"] == full_name, "stars"] = info["stars"]
        df_out.loc[df_out["owner_repo"] == full_name, "forks"] = info["forks"]

        # Save after each repo
        df_out.to_csv(OUTPUT_FILE, index=False)

        print(
            f"[{i + 1}/{len(df)}] {full_name}: ⭐ {info['stars']} | 🍴 {info['forks']}"
        )

        time.sleep(1)  # polite delay

    print(f"\nDone! Saved enriched data to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
