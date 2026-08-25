"""Shared Sankey plotting for the dependency/dependent API usage notebooks."""

from collections import defaultdict
from typing import Literal

import plotly.graph_objects as go

# Color per pymatgen subpackage, shared by both Sankey diagrams in the paper
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
    scale = (1 - pad * (len(totals) - 1)) / sum(totals.values())
    centers, cursor = {}, 0.0
    for name, total in totals.items():
        height = total * scale
        centers[name] = cursor + height / 2
        cursor += height + pad
    return centers


def plot_usage_sankey(
    flows: dict[tuple[str, str], int],
    *,
    source_colors: dict[str, str] | str,
    target_colors: dict[str, str] | str,
    color_links_by: Literal["source", "target"],
    pad: float = 0.03,
) -> go.Figure:
    """Sankey diagram of API usage counts with a deterministic node layout.

    Sources (left column) are sorted by total flow so the widest bands are on top.
    Targets (right column) are sorted by the flow-weighted mean position of their
    sources (barycenter heuristic) to reduce band crossings. Plotly's automatic
    arrangement is not deterministic, which made the figure hard to reproduce.

    Args:
        flows: (source, target) -> usage count.
        source_colors: color per source node, or a single color for all sources.
        target_colors: color per target node, or a single color for all targets.
        color_links_by: which end of a link determines its (semi-transparent) color.
        pad: vertical gap between neighboring nodes in paper coordinates.
    """
    src_totals: dict[str, int] = defaultdict(int)
    tgt_totals: dict[str, int] = defaultdict(int)
    for (src, tgt), value in flows.items():
        src_totals[src] += value
        tgt_totals[tgt] += value

    src_totals = dict(sorted(src_totals.items(), key=lambda item: -item[1]))
    src_y = node_positions(src_totals, pad)
    barycenter = {
        tgt: sum(val * src_y[src] for (src, tg), val in flows.items() if tg == tgt)
        / total
        for tgt, total in tgt_totals.items()
    }
    tgt_totals = dict(sorted(tgt_totals.items(), key=lambda item: barycenter[item[0]]))
    tgt_y = node_positions(tgt_totals, pad)

    labels = [*src_totals, *tgt_totals]
    label_to_idx = {label: idx for idx, label in enumerate(labels)}

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
                "label": labels,
                "color": [color_of(source_colors, src) for src in src_totals]
                + [color_of(target_colors, tgt) for tgt in tgt_totals],
                # plotly ignores node positions of exactly 0 or 1
                "x": [0.01] * len(src_totals) + [0.99] * len(tgt_totals),
                "y": [*src_y.values(), *tgt_y.values()],
                "line": {"color": "rgba(0,0,0,0.1)", "width": 0.5},
            },
            link={
                "source": [label_to_idx[src] for src, _ in flows],
                "target": [label_to_idx[tgt] for _, tgt in flows],
                "value": list(flows.values()),
                "color": [hex_to_rgba(color) for color in link_colors],
            },
        )
    )
