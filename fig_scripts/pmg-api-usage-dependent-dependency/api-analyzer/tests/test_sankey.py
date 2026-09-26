from typing import Any

import pytest
from api_analyzer.sankey import PMG_COLORS, plot_usage_sankey
from plotly.graph_objects import Figure

# Same subpackages on both sides, but with flow totals that would sort them differently:
# on the dependency side `io` dominates, on the dependent side `core` does.
DEP_FLOWS: dict[tuple[str, str], int] = {  # (dependency, pmg subpackage) -> count
    ("numpy", "io"): 300,
    ("numpy", "core"): 100,
    ("scipy", "symmetry"): 50,
    ("scipy", "core"): 20,
}
DEPENDENT_FLOWS: dict[tuple[str, str], int] = {  # (pmg subpackage, dependent) -> count
    ("core", "matgl"): 300,
    ("io", "matgl"): 40,
    ("symmetry", "quacc"): 90,
    ("core", "quacc"): 60,
}


def node_labels(fig: Figure, side: str) -> list[str]:
    """Top-to-bottom labels of one column, read back off the placed nodes."""
    node = fig.data[0].node
    xs = sorted({round(x, 3) for x in node.x})
    keep = xs[0] if side == "source" else xs[-1]
    placed = [
        (y, lbl)
        for x, y, lbl in zip(node.x, node.y, node.label, strict=True)
        if round(x, 3) == keep
    ]
    return [lbl for _y, lbl in sorted(placed)]


@pytest.mark.parametrize(
    ("pmg_order", "expected_dependency", "expected_dependent"),
    [
        pytest.param(
            list(PMG_COLORS),
            ["core", "io", "symmetry"],
            ["core", "io", "symmetry"],
            id="canonical-order-skips-absent-subpackages",
        ),
        pytest.param(
            None,
            ["io", "core", "symmetry"],
            ["core", "symmetry", "io"],
            id="unpinned-flow-and-barycenter-order",
        ),
    ],
)
def test_pmg_subpackage_order(
    pmg_order: list[str] | None,
    expected_dependency: list[str],
    expected_dependent: list[str],
) -> None:
    """Pinning aligns the pmg columns; free ordering follows each figure's flows."""
    dep_fig = plot_usage_sankey(
        DEP_FLOWS,
        source_colors="#8FB9A8",
        target_colors=PMG_COLORS,
        color_links_by="target",
        target_order=pmg_order,
    )
    dependent_fig = plot_usage_sankey(
        DEPENDENT_FLOWS,
        source_colors=PMG_COLORS,
        target_colors="#F7B267",
        color_links_by="source",
        source_order=pmg_order,
    )
    assert node_labels(dep_fig, "target") == expected_dependency
    assert node_labels(dependent_fig, "source") == expected_dependent


@pytest.mark.parametrize(
    ("source_order", "expected_source"),
    [
        pytest.param(None, ["scipy", "numpy"], id="free-source-uses-barycenter"),
        pytest.param(
            ["numpy", "scipy"],
            ["numpy", "scipy"],
            id="pinned-source-overrides-barycenter",
        ),
    ],
)
def test_source_order_with_pinned_target(
    source_order: list[str] | None, expected_source: list[str]
) -> None:
    """The free column follows the pinned column unless explicitly ordered itself."""
    fig = plot_usage_sankey(
        DEP_FLOWS,
        source_colors="#8FB9A8",
        target_colors=PMG_COLORS,
        color_links_by="target",
        source_order=source_order,
        target_order=["symmetry", "core", "io"],  # deliberately not the flow order
    )
    assert node_labels(fig, "target") == ["symmetry", "core", "io"]
    # scipy leans on symmetry (top), numpy on io (bottom); free ordering puts scipy first
    assert node_labels(fig, "source") == expected_source


def test_name_on_both_sides_keeps_its_links_apart() -> None:
    """A name used as both source and target must not merge into one node."""
    flows = {("core", "alpha"): 100, ("beta", "core"): 50, ("beta", "alpha"): 10}
    fig = plot_usage_sankey(
        flows, source_colors="#111111", target_colors="#222222", color_links_by="source"
    )
    node, link = fig.data[0].node, fig.data[0].link
    n_src = sum(x < 0.5 for x in node.x)
    # every link must start in the left column and end in the right one
    assert all(idx < n_src for idx in link.source), list(link.source)
    assert all(idx >= n_src for idx in link.target), list(link.target)
    # and the two "core" nodes stay distinct
    assert list(node.label).count("core") == 2


@pytest.mark.parametrize(
    ("flows", "kwargs", "match"),
    [
        (
            DEP_FLOWS,
            {"target_order": ["core", "symmetry"]},
            r"missing .* order: \['io'\]",
        ),
        (DEP_FLOWS, {"source_order": ["numpy"]}, r"missing .* order: \['scipy'\]"),
        ({}, {}, "no nodes to place"),
        # 40 sources at pad=0.03 need 1.17 of the 0-1 axis for gaps alone
        ({(f"s{idx}", "t"): 10 for idx in range(40)}, {}, r"need 1\.17 of the 0-1"),
    ],
)
def test_invalid_layout(
    flows: dict[tuple[str, str], int], kwargs: dict[str, Any], match: str
) -> None:
    """Orders omitting flow-carrying nodes, empty flows and excess padding raise."""
    with pytest.raises(ValueError, match=match):
        plot_usage_sankey(
            flows,
            source_colors="#111111",
            target_colors="#222222",
            color_links_by="source",
            **kwargs,
        )
