"""Coverage aggregation must use statement counts from one report."""

import pytest

from fig_scripts.code_coverage_treemap.plot_coverage_treemap import (
    FileCoverage,
    coverage_nodes,
    make_figure,
)


def file_coverage(statements: int, covered: int) -> FileCoverage:
    """Make a minimal coverage.py file entry."""
    return {"summary": {"num_statements": statements, "covered_lines": covered}}


def test_statement_weighting_and_zero_coverage() -> None:
    """Retain uncovered files and weight parents by statements, not file averages."""
    nodes = coverage_nodes(
        {
            "src/pymatgen/core/large.py": file_coverage(10000, 9000),
            "src/pymatgen/core/small.py": file_coverage(10, 0),
            "src/pymatgen/core/tiny.py": file_coverage(5, 5),
            "src/pymatgen/core/__init__.py": file_coverage(0, 0),
            "src/pymatgen/io/vasp/outputs.py": file_coverage(600, 0),
            "src/pymatgen/io/vasp/inputs.py": file_coverage(600, 600),
            "tests/test_core.py": file_coverage(3000, 3000),
        }
    )
    assert nodes["pymatgen"] == (11215, 9605)
    assert nodes["pymatgen/core"] == (10015, 9005)
    assert nodes["pymatgen/core/other"] == (15, 5)
    assert nodes["pymatgen/io"] == (1200, 600)
    assert "pymatgen/io/other" not in nodes  # Small packages stay single cells.
    assert "pymatgen/core/__init__" not in nodes
    trace = make_figure(nodes).data[0]
    root_idx = list(trace.ids).index("pymatgen")
    assert trace.values[root_idx] == 11215
    assert trace.text[root_idx] == "86% cov"
    # One division and multiplication in f64; 1e-13 percentage points is conservative.
    assert trace.marker.colors[root_idx] == pytest.approx(
        100 * 9605 / 11215, rel=0, abs=1e-13
    )
    for node_id, (statements, covered) in nodes.items():
        children = [
            counts
            for child, counts in nodes.items()
            if child.rpartition("/")[0] == node_id
        ]
        if children:
            assert sum(counts[0] for counts in children) == statements
            assert sum(counts[1] for counts in children) == covered


@pytest.mark.parametrize(("statements", "covered"), [(2, 3), (2, -1), (-1, 0)])
def test_invalid_coverage_counts(statements: int, covered: int) -> None:
    """Reject inconsistent reports rather than painting misleading percentages."""
    with pytest.raises(
        ValueError, match="Invalid coverage counts for src/pymatgen/core.py"
    ):
        coverage_nodes({"src/pymatgen/core.py": file_coverage(statements, covered)})


def test_empty_source_report() -> None:
    """Fail clearly if a report uses a different source path convention."""
    with pytest.raises(ValueError, match="no executable"):
        coverage_nodes({"pymatgen/core.py": file_coverage(100, 90)})
