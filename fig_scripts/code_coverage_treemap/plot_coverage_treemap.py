"""Plot executable statements and line coverage from the same coverage.py report."""

import argparse
import json
import os
from typing import TypedDict
from urllib.request import urlopen

import plotly.graph_objects as go

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COVERAGE_JSON = "https://github.com/user-attachments/files/21545087/2025-07-31-pymatgen-coverage.json"


class Summary(TypedDict):
    """Integer counts used to aggregate line coverage without averaging percentages."""

    num_statements: int
    covered_lines: int


class FileCoverage(TypedDict):
    """Relevant portion of a file entry in a coverage.py JSON report."""

    summary: Summary


def coverage_nodes(files: dict[str, FileCoverage]) -> dict[str, tuple[int, int]]:
    """Aggregate (statements, covered) by package, grouping small cells as Other."""
    leaves: dict[str, tuple[int, int]] = {}
    for path, entry in files.items():
        if not path.startswith("src/pymatgen/") or not path.endswith(".py"):
            continue
        statements, covered = (
            entry["summary"]["num_statements"],
            entry["summary"]["covered_lines"],
        )
        if not 0 <= covered <= statements:
            raise ValueError(
                f"Invalid coverage counts for {path}: {statements=}, {covered=}"
            )
        if statements == 0:
            continue
        cell = "/".join(path.removeprefix("src/").removesuffix(".py").split("/")[:3])
        previous = leaves.get(cell, (0, 0))
        leaves[cell] = previous[0] + statements, previous[1] + covered
    if not leaves:
        raise ValueError(
            "Coverage report contains no executable src/pymatgen/*.py statements"
        )

    nodes: dict[str, tuple[int, int]] = {}
    for cell, (statements, covered) in leaves.items():
        parts = cell.split("/")
        if len(parts) == 3 and statements < 1500:
            parts[-1] = "other"
        for depth in range(1, len(parts) + 1):
            node_id = "/".join(parts[:depth])
            previous = nodes.get(node_id, (0, 0))
            nodes[node_id] = previous[0] + statements, previous[1] + covered
    # Keep small subpackages as single labeled cells at publication size.
    collapsed = {
        node_id
        for node_id, counts in nodes.items()
        if node_id.count("/") == 1 and counts[0] < 5000
    }
    return {
        node_id: counts
        for node_id, counts in nodes.items()
        if node_id.rpartition("/")[0] not in collapsed
    }


def make_figure(nodes: dict[str, tuple[int, int]]) -> go.Figure:
    """Use summed executable statements for areas and summed coverage for colors."""
    node_ids = sorted(nodes)
    counts = [nodes[node_id] for node_id in node_ids]
    percentages = [100 * covered / statements for statements, covered in counts]
    fig = go.Figure()
    fig.add_treemap(
        ids=node_ids,
        labels=[node_id.split("/")[-1] for node_id in node_ids],
        parents=[node_id.rpartition("/")[0] for node_id in node_ids],
        values=[statements for statements, _ in counts],
        branchvalues="total",
        marker={"colors": percentages, "coloraxis": "coloraxis"},
        customdata=[covered for _, covered in counts],
        text=[f"{percentage:.0f}% cov" for percentage in percentages],
        texttemplate="%{label}<br>%{value:,}<br>%{text}",
        hovertemplate="%{id}<br>%{customdata:,} / %{value:,} covered statements<br>%{text}<extra></extra>",
        textfont_size=16,
    )
    fig.update_layout(
        font_size=16,
        margin={"l": 0, "r": 0, "b": 0, "t": 0},
        coloraxis={
            "cmin": 0,
            "cmax": 100,
            "colorscale": "RdYlGn",
            "colorbar": {"len": 0.94, "title": "Coverage (%)"},
        },
    )
    return fig


def main() -> None:
    """Read the dated report, print auditable package counts and export the figure."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--coverage-file", help="Local copy of the linked coverage.py JSON report"
    )
    args = parser.parse_args()
    if args.coverage_file:
        with open(args.coverage_file, encoding="utf-8") as stream:
            report = json.load(stream)
    else:
        with urlopen(COVERAGE_JSON, timeout=60) as response:
            report = json.load(response)
    print(f"Coverage snapshot: {report['meta']['timestamp']}")
    nodes = coverage_nodes(report["files"])
    for node_id, (statements, covered) in sorted(nodes.items()):
        if node_id.count("/") <= 1:
            print(
                f"{node_id:<30} {covered:>6,} / {statements:>6,} statements  {100 * covered / statements:5.1f}%"
            )
    make_figure(nodes).write_image(
        f"{ROOT}/paper/figs/py-pkg-treemap-pymatgen-coverage.pdf",
        width=1000,
        height=600,
    )


if __name__ == "__main__":
    main()
