"""Regression checks for PR inclusion, title classification and chart totals."""

from collections import Counter
from datetime import UTC, datetime, timedelta

import pytest

from fig_scripts.pr_contributors_bar_plot.plot_stacked_bar_plot import (
    make_figure as tenure_figure,
)
from fig_scripts.pr_data import (
    OTHER,
    PaperPR,
    RawPR,
    annual_counts,
    classify_pr,
    load_prs,
    prepare_prs,
    tenure_group,
)
from fig_scripts.pr_topics_over_time.plot_stacked_bar import make_figure as topic_figure


def raw_pr(number: int, **changes: object) -> RawPR:
    """Make a GitHub record with explicit dates and a reusable title."""
    record: RawPR = {
        "number": number,
        "title": "New functionality",
        "author": "contributor",
        "author_type": "User",
        "created_at": "2024-12-01T00:00:00Z",
        "merged_at": "2025-12-31T23:59:59Z",
    }
    return {**record, **changes}


def test_full_year_population_and_first_submission() -> None:
    """Keep identical titles and year-end merges, excluding bots and 2026 merges."""
    records = prepare_prs(
        [
            raw_pr(1, created_at="2020-01-01T00:00:00Z", merged_at=None),
            raw_pr(2),
            raw_pr(3),
            raw_pr(4, merged_at="2026-01-01T00:00:00Z"),
            raw_pr(5, author="robot", author_type="Bot"),
            raw_pr(6, author="robot[bot]"),
        ]
    )
    assert set(records) == {"2", "3"}
    assert annual_counts(records) == {2025: 2}
    assert records["2"]["first_pr_at"] == "2020-01-01T00:00:00Z"
    assert records["2"]["theme"] == OTHER
    with pytest.raises(ValueError, match="Duplicate PR #2"):
        prepare_prs([raw_pr(2), raw_pr(2)])


@pytest.mark.parametrize(
    ("title", "theme"),
    [
        ("New functionality", OTHER),
        ("Special handling", OTHER),
        ("Add CI workflow", "Testing & Code Quality"),
        ("Improve io support", "I/O & Parsing"),
        ("Add diffusion analysis", "Structural & Analysis"),
        ("Fix VASP documentation", "Documentation"),
        ("Fix VASP parser", "Bug Fixes & Refactoring"),
        ("Optimize structure matching", "Performance"),
        ("Add tests for VASP", "Testing & Code Quality"),
    ],
)
def test_title_rules(title: str, theme: str) -> None:
    """Match whole words and explicit precedence, preserving unmatched titles."""
    assert classify_pr(title) == theme


@pytest.mark.parametrize(
    ("days", "group"),
    [
        (0, "<7 days"),
        (7 - 1 / 86400, "<7 days"),
        (7, "7 days–<1 year"),
        (365.25, "1–<3 years"),
        (3 * 365.25, "3–<6 years"),
        (6 * 365.25, "≥6 years"),
    ],
)
def test_disjoint_tenure_boundaries(days: float, group: str) -> None:
    """Put every boundary in the next tenure bin, using merger time."""
    first = datetime(2019, 1, 1, tzinfo=UTC)
    record: PaperPR = {
        "title": "Example",
        "author": "contributor",
        "theme": OTHER,
        "first_pr_at": first.isoformat(),
        "created_at": first.isoformat(),
        "merged_at": (first + timedelta(days=days)).isoformat(),
    }
    assert tenure_group(record) == group


def test_both_charts_reconcile_with_github_snapshot() -> None:
    """Check plotted stacks against independently reported merge-year totals."""
    expected = dict(
        zip(
            range(2013, 2026),
            [40, 83, 52, 142, 292, 264, 167, 140, 143, 247, 399, 358, 167],
            strict=True,
        )
    )
    records = load_prs()
    assert annual_counts(records) == expected
    assert sum(expected.values()) == len(records) == 2494
    for pr_id, record in records.items():
        assert record["theme"] == classify_pr(record["title"]), pr_id
    for make_figure in [topic_figure, tenure_figure]:
        figure = make_figure(records)
        plotted: Counter[int] = Counter()
        for trace in figure.data:
            for year, count in zip(trace.x, trace.y, strict=True):
                plotted[int(year)] += int(count)
        assert plotted == expected
    other_trace = next(
        trace for trace in topic_figure(records).data if trace.name == OTHER
    )
    assert (
        sum(other_trace.y)
        == sum(record["theme"] == OTHER for record in records.values())
        > 0
    )
