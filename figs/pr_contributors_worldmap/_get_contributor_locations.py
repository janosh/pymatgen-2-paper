# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests",
# ]
# ///
import requests
import time
import csv
import os

REPO: str = "materialsproject/pymatgen"
GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"token {GITHUB_TOKEN}",
}


def get_all_pr_authors_with_counts(repo):
    print("Fetching merged PR authors (excluding bots)...")
    author_counts: dict[str, int] = {}
    page = 1
    per_page = 100

    while True:
        url = f"https://api.github.com/repos/{repo}/pulls"
        params = {"state": "closed", "per_page": per_page, "page": page}
        response = requests.get(url, headers=HEADERS, params=params)

        if response.status_code != 200:
            print(f"Failed to fetch PRs: {response.status_code}, {response.text}")
            break

        prs = response.json()
        if not prs:
            break

        for pr in prs:
            if not pr.get("merged_at"):
                continue

            user = pr.get("user")
            login = user.get("login", "") if user else ""
            if login and "[bot]" not in login:
                author_counts[login] = author_counts.get(login, 0) + 1

        print(
            f"Fetched page {page}, total unique merged authors so far: {len(author_counts)}"
        )
        page += 1

    return author_counts


def get_user_location(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return data.get("location")
    else:
        print(f"Failed to fetch user {username}: {response.status_code}")
        return None


def main():
    author_counts = get_all_pr_authors_with_counts(REPO)

    print("\nFetching locations...")
    user_locations = []
    for i, (username, count) in enumerate(sorted(author_counts.items())):
        location = get_user_location(username)
        user_locations.append(
            {"login": username, "location": location, "pr_count": count}
        )
        print(f"{i + 1:3d}/{len(author_counts)} {username}: {location} ({count} PRs)")
        time.sleep(1)

    # Save to CSV
    with open("contributor_locations.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["login", "location", "pr_count"])
        writer.writeheader()
        writer.writerows(user_locations)

    print("Saved contributor_locations.csv")


if __name__ == "__main__":
    main()
