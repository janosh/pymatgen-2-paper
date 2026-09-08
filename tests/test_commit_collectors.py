"""Commit collectors must retain complete records without switching checkouts."""

import os
import runpy
import subprocess
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import pytest

from fig_scripts.pr_data import ROOT


@pytest.mark.parametrize("separator", ["\n", "\n\n", "\n\n\n"])
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
    saved: dict[str, pd.DataFrame] = {}

    def read_log(command: list[str], **kwargs: object) -> bytes:
        """Supply representative git output without accessing another checkout."""
        commands.append(command)
        return log.encode()

    def save_frame(frame: pd.DataFrame, filename: str, **kwargs: object) -> None:
        """Inspect the collector's CSV contents without changing tracked caches."""
        saved[filename] = frame.copy()

    monkeypatch.setenv("PMG_REPO_PATH", str(tmp_path))
    monkeypatch.setattr(subprocess, "check_output", read_log)
    monkeypatch.setattr(pd.DataFrame, "to_csv", save_frame)
    runpy.run_path(
        f"{ROOT}/fig_scripts/contribution_over_time_plot/_retrieve_commit_info_over_time.py",
        run_name="__main__",
    )

    assert len(commands) == 1
    assert commands[0][:5] == ["git", "-C", str(tmp_path), "log", "master"]
    months = ["2025-01", "2025-02", "2025-03"]
    assert saved["contributor_commits_by_month.csv.gz"][months].sum().tolist() == [
        1,
        1,
        1,
    ]
    assert saved["contributor_lines_changed_by_month.csv.gz"][
        months
    ].sum().tolist() == [3, 0, 8]
    assert not list(tmp_path.iterdir())


def test_heatmap_reads_master_without_checkout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Read the intended revision explicitly for both historical source layouts."""
    commands: list[list[str]] = []
    images: list[str] = []

    def read_dates(
        command: list[str], **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        """Reject commands that could alter the supplied working tree."""
        commands.append(command)
        assert command[:5] == ["git", "-C", str(tmp_path), "log", "master"]
        return subprocess.CompletedProcess(
            command, 0, stdout="2025-01-02\n2025-06-03\n"
        )

    def save_image(figure: go.Figure, filename: str, **kwargs: object) -> None:
        """Record image export without rendering or changing the paper asset."""
        images.append(os.path.basename(filename))

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PMG_REPO_PATH", str(tmp_path))
    monkeypatch.setattr(subprocess, "run", read_dates)
    monkeypatch.setattr(go.Figure, "write_image", save_image)
    monkeypatch.setattr(go.Figure, "show", lambda *args, **kwargs: None)
    namespace = runpy.run_path(
        f"{ROOT}/fig_scripts/per_package_commit_heatmap/generate_heatmap.py",
        run_name="__main__",
    )
    assert len(commands) == 2 * len(namespace["PACKAGES"])
    assert images == ["commits-per-package-heatmap.png"]
