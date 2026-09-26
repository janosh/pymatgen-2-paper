"""Commit collectors must retain complete records without switching checkouts."""

import os
import runpy
import subprocess
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import pytest

from fig_scripts.pr_data import ROOT


@pytest.mark.parametrize(
    "separator", ["\n", "\n\n", "\n\n\n"], ids=["adjacent", "blank", "extra-blank"]
)
def test_commit_records_end_at_headers_or_eof(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, separator: str
) -> None:
    """Keep the last commit, empty merge commits and stats after blank lines."""
    log = separator.join(
        [
            "--COMMIT--|first|Contributor|contributor@example.com|2025-01-02\n\n2\t1\tfile.py\n-\t-\timage.png",
            "--COMMIT--|merge|Contributor|contributor@example.com|2025-02-03",
            "--COMMIT--|last|Contributor|contributor@example.com|2025-03-04\n5\t3\tfile.py",
        ]
    )
    commands: list[list[str]] = []

    def read_log(command: list[str], **kwargs: object) -> bytes:
        """Supply representative git output without accessing another checkout."""
        commands.append(command)
        return log.encode()

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PMG_REPO_PATH", str(tmp_path))
    monkeypatch.setattr(subprocess, "check_output", read_log)
    runpy.run_path(
        f"{ROOT}/fig_scripts/contribution_over_time_plot/_retrieve_commit_info_over_time.py",
        run_name="__main__",
    )

    assert len(commands) == 1
    assert commands[0][:5] == ["git", "-C", str(tmp_path), "log", "master"]
    months = ["2025-01", "2025-02", "2025-03"]
    for metric, expected in [("commits", [1, 1, 1]), ("lines_changed", [3, 0, 8])]:
        frame = pd.read_csv(tmp_path / f"contributor_{metric}_by_month.csv.gz")
        assert frame[months].sum().tolist() == expected, metric


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
    assert list(figure.layout.xaxis.ticktext) == [
        *map(str, range(2012, 2025, 2)),
        "2025",
    ]
