"""Scrap pymatgen dependents from:
https://github.com/materialsproject/pymatgen/network/dependents?dependent_type=REPOSITORY


TODO:For some reason the number of starts cannot be scrapped correctly,
have to scrap the repos first, then get stars later.
"""

import os
import time
from urllib.parse import urlsplit, parse_qs, urljoin

import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = "https://github.com/materialsproject/pymatgen/network/dependents"
PARAMS_BASE = {"dependent_type": "REPOSITORY"}

OUTFILE = "pymatgen_dependents.csv"
CURSOR_FILE = "_pymatgen_dependents_cursor.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (pymatgen-dependents-scraper)",
    "Accept": "text/html,application/xhtml+xml",
}


def extract_next_cursor(soup: BeautifulSoup) -> str | None:
    """Find the 'Next' pagination link and extract its dependents_after cursor."""
    for a in soup.find_all("a", href=True):
        if a.get_text(strip=True) == "Next" and "dependents_after=" in a["href"]:
            qs = parse_qs(urlsplit(a["href"]).query)
            vals = qs.get("dependents_after")
            if vals:
                return vals[0]
    return None


def extract_repo(row: BeautifulSoup) -> tuple[str | None, str | None]:
    """Extract 'owner/repo' and absolute repo URL."""
    link = row.select_one('a[data-hovercard-type="repository"]')
    if not link:
        return None, None
    full_name = (link.get_text() or "").strip()
    href = link.get("href") or ""
    repo_url = urljoin("https://github.com", href)
    return full_name, repo_url


def save_checkpoint(rows: list[dict]) -> None:
    df = pd.DataFrame(rows).drop_duplicates("full_name")
    df.to_csv(OUTFILE, index=False)


def load_existing() -> tuple[list[dict], set[str], str | None]:
    repos, seen, cursor = [], set(), None
    if os.path.exists(OUTFILE):
        df = pd.read_csv(OUTFILE)
        repos = df.to_dict("records")
        seen = set(df["full_name"].astype(str))
        print(f"Resuming: {len(df)} repos loaded from {OUTFILE}")
    if os.path.exists(CURSOR_FILE):
        cursor = (open(CURSOR_FILE, "r", encoding="utf-8").read().strip()) or None
        if cursor:
            print(f"Resuming from cursor: {cursor[:12]}…")
    return repos, seen, cursor


def main():
    all_repos, seen, cursor = load_existing()
    page_ix = 1

    while True:
        params = PARAMS_BASE.copy()
        if cursor:
            params["dependents_after"] = cursor

        print(f"\n[page {page_ix}] GET {BASE_URL} params={params}")
        try:
            r = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=30)
        except requests.RequestException as e:
            print(f"Request error: {e}. Sleeping 20s…")
            time.sleep(20)
            continue

        if r.status_code in (403, 429):
            wait = int(r.headers.get("Retry-After", "20"))
            print(f"Rate-limited ({r.status_code}). Sleeping {wait}s…")
            time.sleep(wait)
            continue
        if r.status_code != 200:
            print(f"Stopped: HTTP {r.status_code}")
            break

        soup = BeautifulSoup(r.text, "html.parser")
        rows = soup.select("div.Box-row")
        if not rows:
            print("No rows found on this page; done.")
            break

        page_new = []
        for row in rows:
            full_name, repo_url = extract_repo(row)
            if not full_name or full_name in seen:
                continue
            page_new.append({"full_name": full_name, "repo_url": repo_url})
            seen.add(full_name)

        if page_new:
            all_repos.extend(page_new)
            save_checkpoint(all_repos)
            # Show preview
            preview = page_new[:5]
            print(f"Saved {len(all_repos)} total repos → {OUTFILE}")
            print("Preview from this page:")
            for rec in preview:
                print(f"  - {rec['full_name']} {rec['repo_url']}")
        else:
            print("No NEW repos on this page.")

        next_cursor = extract_next_cursor(soup)
        if not next_cursor:
            print("No 'Next' cursor found — reached the end.")
            break

        cursor = next_cursor
        with open(CURSOR_FILE, "w", encoding="utf-8") as f:
            f.write(cursor)
        print(f"Next cursor: {cursor[:12]}… (saved to {CURSOR_FILE})")

        page_ix += 1
        time.sleep(1.1)  # polite delay

    print(f"\nDone. Final CSV: {OUTFILE}")


if __name__ == "__main__":
    main()
