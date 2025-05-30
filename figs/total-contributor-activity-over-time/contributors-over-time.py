"""First part of this notebook uses the GitHub API to fetch contributions,
to the pymatgen repository into a pandas DataFrame, sort it and save it as a CSV file.

The second part uses the git CLI to do the same
"""

# %%
from __future__ import annotations

import os
import subprocess
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pymatgen
import requests
from pymatviz.io import save_fig
from tokens import GH_TOKEN
from tqdm import tqdm

__author__ = "Janosh Riebesell"
__date__ = "2023-11-01"


# %% --- 1st part: fetch contributors from GitHub API ---
headers = {"Authorization": f"token {GH_TOKEN}"}  # GH personal access token
base_url = "https://api.github.com/repos/materialsproject/pymatgen"

contributors_url = f"{base_url}/stats/contributors"
pull_requests_url = f"{base_url}/pulls?state=closed&sort=created&direction=asc"

contributors_response = requests.get(contributors_url, headers=headers).json()


# %% fetch non-bot user data from GitHub API
gh_user_data = {}

for contributor in tqdm(contributors_response):
    user_url = f"https://api.github.com/users/{contributor['author']['login']}"
    user_data = requests.get(user_url, headers=headers).json()

    if user_data.get("type") == "Bot":  # Exclude bots
        continue
    gh_user_data[contributor["author"]["login"]] = user_data


# %% fetch merged PRs for each contributor
merged_prs_per_contributor = {}
for login in tqdm(gh_user_data):
    merged_pr_response = requests.get(
        pull_requests_url + f"&creator={login}&state=merged", headers=headers
    )
    merged_prs_per_contributor[login] = merged_pr_response.json()


# %% Process contributor data and PRs
contributor_dict = {}
weeks_with_prs_col = "Weeks with merged PR"
n_contribs_col = "Total contributions"

for contributor in tqdm(contributors_response):
    login = contributor["author"]["login"]
    if login not in merged_prs_per_contributor:
        continue
    pr_list = merged_prs_per_contributor[login]

    weeks_with_merged_pr = sum(1 for week in contributor["weeks"] if week["c"] > 0)

    years_with_merged_pr = {
        datetime.fromtimestamp(week["w"]).year
        for week in contributor["weeks"]
        if week["c"] > 0
    }

    name = gh_user_data[login]["name"]
    contributor_dict[name] = {
        "GitHub username": login,
        weeks_with_prs_col: weeks_with_merged_pr,
        "Years with merged PR": ", ".join(map(str, years_with_merged_pr)),
        "Number years active": len(years_with_merged_pr),
        "Oldest PR": pr_list[0]["html_url"] if pr_list else None,
        n_contribs_col: contributor["total"],
    }

df_contributors = pd.DataFrame(contributor_dict.values()).sort_values(
    n_contribs_col, ascending=False
)

today = f"{datetime.now():%Y-%m-%d}"
df_contributors.to_csv(f"{today}-top-contributors.csv", index=False)


# %% cache the data
# %store df_contributors


# restore the data
# %store -r df_contributors


# %% --- 2nd part: Use git CLI to compile contributors ---
contrib_col = "contributors"
px.defaults.labels = {
    "commits": "Commits",
    "first_commit_date": "Time",
    contrib_col: "Contributors",
}
px.defaults.template = "plotly_white"


def get_git_data(repo_path: str, log_type: str, author: str | None = None) -> list[str]:
    """Parse git log data from a given repository and return as strings.

    Args:
        repo_path (str): Path to the repository
        log_type (str): Type of log to parse. Either 'log' or 'shortlog'
        author (str, optional): Filter by author. Defaults to None.

    Returns:
        list[str]: parsed git log data
    """
    author_str = f"--author='{author}'" if author else ""
    command = f"git -C {repo_path} log {author_str} --pretty=format:'%ad' --date=short"
    if log_type == "shortlog":
        command = f"git -C {repo_path} shortlog -sn --all"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)  # noqa: PLW1510
    return result.stdout.strip().split("\n")


try:  # only works if pymatgen is installed in editable mode
    pmg_repo_path = pymatgen.__path__[-1]
except:  # otherwise, use the path to the repo  # noqa: E722
    pmg_repo_path = f"{os.path.expanduser('~')}/dev/pmg"

# %% Fetch contributor data and populate DataFrame
shortlog_data = get_git_data(pmg_repo_path, "shortlog")

contributor_data = [
    {
        "commit_count": int(line.split("\t")[0].strip()),
        "contributor": line.split("\t")[1].strip(),
    }
    for line in shortlog_data
]
df_git_hist = pd.DataFrame(contributor_data)

# Fetch first commit date for each contributor
df_git_hist["first_commit_date"] = [
    get_git_data(pmg_repo_path, "log", x)[-1] for x in tqdm(df_git_hist["contributor"])
]
df_git_hist["first_commit_date"] = pd.to_datetime(df_git_hist["first_commit_date"])
df_sorted = df_git_hist.sort_values("first_commit_date")
df_sorted[contrib_col] = range(1, len(df_sorted) + 1)

# Fetch all commit dates for the repo
commit_dates = pd.to_datetime(get_git_data(pmg_repo_path, "log"), errors="coerce")
df_commits = pd.DataFrame({"commit_date": commit_dates}).sort_values("commit_date")
commit_col = "commits"
df_commits[commit_col] = df_commits["commit_date"].expanding().count()


# %% create the plotly plot
fig = go.Figure()

for label, df, x_col, y_col in [
    ("contributors", df_sorted, "first_commit_date", contrib_col),
    ("commits", df_commits, "commit_date", commit_col),
]:
    trace = go.Scatter(x=df[x_col], y=df[y_col], mode="lines", name=label)
    fig.add_trace(trace)

fig.layout.template = "plotly_white"
fig.layout.margin.update(l=10, r=10, b=10, t=50)
fig.update_layout(yaxis2=dict(overlaying="y", side="right", title=commit_col))
fig.update_layout(yaxis=dict(title=contrib_col))
fig.layout.title.update(text="Pymatgen Contributors & Commits Over Time", x=0.5)
fig.layout.legend.update(x=0.01, y=0.99, xanchor="left", yanchor="top")

fig.show()
save_fig(fig, "contributors-over-time.pdf")
