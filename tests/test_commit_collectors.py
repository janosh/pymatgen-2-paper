"""Commit collectors must retain complete records without switching checkouts."""

import os
import runpy
import subprocess
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import pytest

from fig_scripts.pr_data import ROOT


@pytest.mark.parametrize("reverse", [False, True])
def test_annual_commit_aliases(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, reverse: bool
) -> None:
    """Merge alias chains and bridged groups independently of commit order."""
    log = (
        "Contributor\x1fcontributor@example.com\x1f2024\n"
        "Other\x1fother@example.com\x1f2024\n"
        " Contributor \x1f CONTRIBUTOR@EXAMPLE.COM \x1f2025\n"
        "Other\x1fcontributor@example.com\x1f2025\n"
        "Alias\x1fcontributor@example.com\x1f2025\n"
        "Alias\x1fnew@example.com\x1f2025\n"
        "dependabot[BOT] \x1fbot@example.com\x1f2025"
    )
    log = "\n".join(reversed(log.splitlines())) if reverse else log
    monkeypatch.setenv("PMG_REPO_PATH", str(tmp_path))
    monkeypatch.setenv("CONTRIBUTION_OUTPUT_PATH", str(tmp_path / "annual.csv"))
    monkeypatch.setattr(subprocess, "check_output", lambda *args, **kwargs: log)
    runpy.run_path(
        f"{ROOT}/fig_scripts/contribution_over_time_plot/_retrieve_commit_info_over_time.py",
        run_name="__main__",
    )

    frame = pd.read_csv(tmp_path / "annual.csv", index_col="year")
    assert frame.loc[[2024, 2025]].to_dict("records") == [
        {"active_contributors": 1, "commits": 2},
        {"active_contributors": 1, "commits": 4},
    ]


def test_annual_commit_author_year_boundaries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Use real Git history to retain boundary authors, exclude merges and fill empty years."""
    subprocess.run(
        ["git", "init", "-b", "main", str(tmp_path)], check=True, capture_output=True
    )
    tree = subprocess.check_output(
        ["git", "-C", str(tmp_path), "mktree"], input="", text=True
    ).strip()

    def make_commit(
        author_date: str,
        commit_date: str,
        parents: list[str],
        name: str = "Contributor",
    ) -> str:
        """Create a fixture commit with independently controlled author and committer dates."""
        return subprocess.check_output(
            [
                "git",
                "-C",
                str(tmp_path),
                "commit-tree",
                tree,
                "-m",
                "fixture",
                *[argument for parent in parents for argument in ("-p", parent)],
            ],
            env={
                **os.environ,
                "GIT_AUTHOR_NAME": name,
                "GIT_AUTHOR_EMAIL": "author@example.com",
                "GIT_COMMITTER_NAME": "Committer",
                "GIT_COMMITTER_EMAIL": "committer@example.com",
                "GIT_AUTHOR_DATE": author_date,
                "GIT_COMMITTER_DATE": commit_date,
            },
            text=True,
        ).strip()

    commits: list[str] = []
    for author_date, commit_date, name in [
        ("2011-12-31T23:59:59Z", "2025-06-01T00:00:00Z", "Contributor"),
        ("2012-01-01T00:00:00Z", "2011-12-31T23:59:59Z", "Contributor"),
        ("2014-06-01T00:00:00Z", "2014-06-01T00:00:00Z", "Contributor"),
        ("2025-12-31T23:59:59Z", "2026-01-01T00:00:00Z", "Contributor"),
        ("2026-01-01T00:00:00Z", "2025-12-31T23:59:59Z", "Contributor"),
        ("2025-06-01T00:00:00Z", "2025-06-01T00:00:00Z", "robot[bot]"),
    ]:
        commits.append(make_commit(author_date, commit_date, commits[-1:], name))
    merge = make_commit(
        "2016-06-01T00:00:00Z", "2016-06-01T00:00:00Z", [commits[-1], commits[0]]
    )
    subprocess.run(
        ["git", "-C", str(tmp_path), "update-ref", "refs/heads/main", merge], check=True
    )
    monkeypatch.setenv("PMG_REPO_PATH", str(tmp_path))
    monkeypatch.setenv("CONTRIBUTION_OUTPUT_PATH", str(tmp_path / "annual.csv"))
    runpy.run_path(
        f"{ROOT}/fig_scripts/contribution_over_time_plot/_retrieve_commit_info_over_time.py",
        run_name="__main__",
    )
    frame = pd.read_csv(tmp_path / "annual.csv", index_col="year")
    expected = {2012: [1, 1], 2014: [1, 1], 2025: [1, 1]}
    assert frame.index.tolist() == list(range(2012, 2026))
    assert frame.values.tolist() == [expected.get(year, [0, 0]) for year in frame.index]


@pytest.mark.parametrize(
    ("log", "message"),
    [
        ("", "No non-bot, non-merge commits"),
        ("robot[bot]\x1fbot@example.com\x1f2025", "No non-bot, non-merge commits"),
        ("Contributor\x1femail@example.com\x1f2026", "No non-bot, non-merge commits"),
        ("malformed", "Invalid Git log record"),
        ("Contributor\x1femail@example.com\x1fnot-a-year", "Invalid Git log record"),
    ],
)
def test_annual_commit_invalid_history(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, log: str, message: str
) -> None:
    """Fail explicitly on invalid or empty input without replacing an existing cache."""
    output_path = tmp_path / "annual.csv"
    output_path.write_text("existing cache")
    monkeypatch.setenv("PMG_REPO_PATH", str(tmp_path))
    monkeypatch.setenv("CONTRIBUTION_OUTPUT_PATH", str(output_path))
    monkeypatch.setattr(subprocess, "check_output", lambda *args, **kwargs: log)
    with pytest.raises(ValueError, match=message):
        runpy.run_path(
            f"{ROOT}/fig_scripts/contribution_over_time_plot/_retrieve_commit_info_over_time.py",
            run_name="__main__",
        )
    assert output_path.read_text() == "existing cache"


def test_annual_activity_plot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Plot the cached counts from any directory with matching axis colors and gridlines."""
    images: list[str] = []

    def save_image(figure: go.Figure, filename: str, **kwargs: object) -> None:
        """Record the figure destination without rendering the paper asset."""
        images.append(filename)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(go.Figure, "write_image", save_image)
    monkeypatch.setattr(go.Figure, "show", lambda *args, **kwargs: None)
    namespace = runpy.run_path(
        f"{ROOT}/fig_scripts/contribution_over_time_plot/plot_num_contributors_by_month.py",
        run_name="__main__",
    )
    figure = namespace["fig"]
    frame = namespace["df"]
    assert images == [f"{ROOT}/paper/figs/active-contributors-colored.pdf"]
    for trace, column, axis_name in zip(
        figure.data,
        ["active_contributors", "commits"],
        ["yaxis", "yaxis2"],
        strict=True,
    ):
        axis = figure.layout[axis_name]
        assert list(trace.y) == frame[column].tolist()
        assert (
            list(trace.x)
            == pd.to_datetime(frame["year"].astype(str), format="%Y").tolist()
        )
        assert trace.line.color == axis.title.font.color == axis.tickfont.color
        assert axis.range[0] == axis.tick0 == 0
        assert max(trace.y) < axis.range[1]
    left, right = figure.layout.yaxis, figure.layout.yaxis2
    assert left.dtick * right.range[1] == right.dtick * left.range[1]
    assert right.showgrid and not left.showgrid and not figure.layout.xaxis.showgrid
    assert list(figure.layout.xaxis.ticktext) == list(map(str, range(2012, 2026, 2)))
    assert not figure.layout.annotations


@pytest.mark.parametrize("source", ["git", "cache"])
def test_heatmap_calendar_bins_without_checkout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, source: str
) -> None:
    """Keep empty calendar half-years and exclude dates outside 2012–2025."""
    commands: list[list[str]] = []
    images: list[str] = []
    dates = [
        "2011-12-31",
        "2012-03-01",
        "2012-06-30",
        "2012-07-01",
        "2012-12-31",
        "2013-07-01",
        "2025-12-31",
        "2026-01-01",
    ]

    def read_dates(
        command: list[str], **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        """Reject commands that could alter the supplied working tree."""
        commands.append(command)
        assert command[:5] == ["git", "-C", str(tmp_path), "log", "main"]
        # Both layouts are queried together over the full window so commits made
        # before the 2024-06-26 src-layout move are not dropped
        flat_path, src_path = command[-2:]
        assert command[-3] == "--"
        assert src_path == f"src/{flat_path}"
        assert flat_path.startswith("pymatgen/")
        assert command[command.index("--since") + 1] == "2012-01-01T00:00:00Z"
        assert command[command.index("--until") + 1] == "2026-01-01T00:00:00Z"
        return subprocess.CompletedProcess(command, 0, stdout="\n".join(dates))

    def save_image(figure: go.Figure, filename: str, **kwargs: object) -> None:
        """Record image export without rendering or changing the paper asset."""
        images.append(os.path.basename(filename))

    monkeypatch.chdir(tmp_path)
    if source == "git":
        monkeypatch.setenv("PMG_REPO_PATH", str(tmp_path))
    else:
        monkeypatch.delenv("PMG_REPO_PATH", raising=False)
        pd.DataFrame(
            {"analysis": 1}, index=pd.Index([date[:7] for date in dates], name="time")
        ).to_csv(tmp_path / "_monthly_commits_per_package.csv")
    monkeypatch.setattr(subprocess, "run", read_dates)
    monkeypatch.setattr(go.Figure, "write_image", save_image)
    monkeypatch.setattr(go.Figure, "show", lambda *args, **kwargs: None)
    namespace = runpy.run_path(
        f"{ROOT}/fig_scripts/per_package_commit_heatmap/generate_heatmap.py",
        run_name="__main__",
    )
    assert len(commands) == (len(namespace["PACKAGES"]) if source == "git" else 0)
    assert images == ["commits-per-package-heatmap.png"]
    binned = namespace["df_binned"]
    expected = [2, 2, 0, 1, *([0] * 23), 1]
    for package in binned:
        assert binned[package].tolist() == expected, package
    assert binned.index.strftime("%Y-%m-%d").tolist() == [
        f"{year}-{month_day}"
        for year in range(2012, 2026)
        for month_day in ["06-30", "12-31"]
    ]
    figure = namespace["fig"]
    assert list(figure.data[0].x) == binned.index.strftime("%Y-%m").tolist()
    assert figure.layout.xaxis.type == "category"
    assert list(figure.layout.xaxis.ticktext) == list(map(str, range(2012, 2026, 2)))
