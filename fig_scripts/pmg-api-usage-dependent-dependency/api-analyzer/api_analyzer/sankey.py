"""Shared Sankey plotting for the dependency/dependent API usage notebooks."""

from collections import defaultdict
from collections.abc import Sequence
from typing import Literal

import plotly.graph_objects as go

# Color per pymatgen subpackage, shared by both Sankey diagrams in the paper. Dict order
# is also the canonical top-to-bottom node order (roughly by subpackage size) so the
# subpackages stack the same way in both figures, whichever side they appear on.
# Deliberately omits `cli` and `vis`: the dependent-usage notebook filters them out.
PMG_COLORS: dict[str, str] = {
    "core": "#3B9C9C",
    "analysis": "#6C5B7B",
    "io": "#355C7D",
    "entries": "#99B898",
    "symmetry": "#FFD3B6",
    "ext": "#E84A5F",
    "electronic_structure": "#F67280",
    "transformations": "#C06C84",
    "phonon": "#A8E6CF",
    "optimization": "#FFAAA5",
    "util": "#FF8B94",
    "command_line": "#0384fc",
    "alchemy": "#6203fc",
    "apps": "#343deb",
}


def hex_to_rgba(hex_color: str, alpha: float = 0.5) -> str:
    """Convert hex color like '#F67280' to 'rgba(246,114,128,0.5)'."""
    hex_color = hex_color.lstrip("#")
    red, green, blue = (int(hex_color[idx : idx + 2], 16) for idx in (0, 2, 4))
    return f"rgba({red},{green},{blue},{alpha})"


def node_positions(totals: dict[str, int], pad: float) -> dict[str, float]:
    """Vertical node centers (0=top, 1=bottom) proportional to each node's total flow.

    Nodes are stacked in dict order with a fixed gap `pad` between them.
    """
    if not totals:
        raise ValueError("no nodes to place, `flows` is empty")
    if (gaps := pad * (len(totals) - 1)) >= 1:
        # otherwise the leftover height is <=0 and nodes stack inverted and off-canvas
        raise ValueError(
            f"{len(totals)} nodes at {pad=} need {gaps:.2f} of the 0-1 axis for gaps "
            f"alone; use pad < {1 / (len(totals) - 1):.4f} or plot fewer nodes"
        )
    scale = (1 - gaps) / sum(totals.values())
    centers, cursor = {}, 0.0
    for name, total in totals.items():
        height = total * scale
        centers[name] = cursor + height / 2
        cursor += height + pad
    return centers


def in_given_order(totals: dict[str, int], order: Sequence[str]) -> dict[str, int]:
    """Reorder node totals to follow `order`, skipping nodes that carry no flow."""
    if unknown := set(totals) - set(order):
        raise ValueError(f"nodes missing from explicit node order: {sorted(unknown)}")
    return {name: totals[name] for name in order if name in totals}


def sorted_by_barycenter(
    totals: dict[str, int],
    links: dict[str, dict[str, int]],
    other_y: dict[str, float],
) -> dict[str, int]:
    """Order nodes by the flow-weighted mean position of their counterparts.

    This barycenter heuristic pulls each node level with whatever it connects to on the
    already-placed column, which keeps the bands between the two columns from crossing.
    """

    def barycenter(name: str) -> float:
        counterparts = links[name].items()
        return sum(val * other_y[other] for other, val in counterparts) / totals[name]

    return {name: totals[name] for name in sorted(totals, key=barycenter)}


def plot_usage_sankey(
    flows: dict[tuple[str, str], int],
    *,
    source_colors: dict[str, str] | str,
    target_colors: dict[str, str] | str,
    color_links_by: Literal["source", "target"],
    pad: float = 0.03,
    source_order: Sequence[str] | None = None,
    target_order: Sequence[str] | None = None,
) -> go.Figure:
    """Sankey diagram of API usage counts with a deterministic node layout.

    Plotly's automatic arrangement is not deterministic, which made the figure hard to
    reproduce, so both columns are placed explicitly. The caller can pin either or both
    columns (`source_order`/`target_order`, used to keep the pymatgen subpackages stacked
    identically across both paper figures). With neither pinned, the sources are sorted
    by total flow so the widest bands are on top. A column left unpinned is sorted by the
    flow-weighted mean position of its counterparts (barycenter heuristic) to reduce
    band crossings.

    Args:
        flows: (source, target) -> usage count.
        source_colors: color per source node, or a single color for all sources.
        target_colors: color per target node, or a single color for all targets.
        color_links_by: which end of a link determines its (semi-transparent) color.
        pad: vertical gap between neighboring nodes in paper coordinates.
        source_order: explicit top-to-bottom order for the left column. Names carrying
            no flow are skipped, so one canonical order can serve several figures.
        target_order: same for the right column.
    """
    # each node's counterparts on the other side, so barycenters are a local lookup
    src_links: dict[str, dict[str, int]] = defaultdict(dict)
    tgt_links: dict[str, dict[str, int]] = defaultdict(dict)
    for (src, tgt), value in flows.items():
        src_links[src][tgt] = value
        tgt_links[tgt][src] = value
    src_totals = {src: sum(links.values()) for src, links in src_links.items()}
    tgt_totals = {tgt: sum(links.values()) for tgt, links in tgt_links.items()}

    if target_order is not None:
        tgt_totals = in_given_order(tgt_totals, target_order)
    if source_order is not None:
        src_totals = in_given_order(src_totals, source_order)
    elif target_order is not None:  # only the right column pinned, arrange left around it
        tgt_y = node_positions(tgt_totals, pad)
        src_totals = sorted_by_barycenter(src_totals, src_links, tgt_y)
    else:  # nothing pinned: widest sources on top anchor the layout
        src_totals = dict(sorted(src_totals.items(), key=lambda item: -item[1]))
    src_y = node_positions(src_totals, pad)
    if target_order is None:  # arrange the right column around the now-fixed left one
        tgt_totals = sorted_by_barycenter(tgt_totals, tgt_links, src_y)
    tgt_y = node_positions(tgt_totals, pad)

    # index per column, not by label: a name can legitimately appear on both sides and a
    # single label -> index map would silently route its links to the wrong node
    src_idx = {name: idx for idx, name in enumerate(src_totals)}
    tgt_idx = {name: len(src_idx) + idx for idx, name in enumerate(tgt_totals)}

    def color_of(colors: dict[str, str] | str, name: str) -> str:
        return colors if isinstance(colors, str) else colors[name]

    link_colors = [
        color_of(source_colors, src)
        if color_links_by == "source"
        else color_of(target_colors, tgt)
        for src, tgt in flows
    ]

    return go.Figure(
        go.Sankey(
            arrangement="fixed",
            node={
                "label": [*src_totals, *tgt_totals],
                "color": [color_of(source_colors, src) for src in src_totals]
                + [color_of(target_colors, tgt) for tgt in tgt_totals],
                # plotly ignores node positions of exactly 0 or 1
                "x": [0.01] * len(src_totals) + [0.99] * len(tgt_totals),
                "y": [*src_y.values(), *tgt_y.values()],
                "line": {"color": "rgba(0,0,0,0.1)", "width": 0.5},
            },
            link={
                "source": [src_idx[src] for src, _ in flows],
                "target": [tgt_idx[tgt] for _, tgt in flows],
                "value": list(flows.values()),
                "color": [hex_to_rgba(color) for color in link_colors],
            },
        )
    )
