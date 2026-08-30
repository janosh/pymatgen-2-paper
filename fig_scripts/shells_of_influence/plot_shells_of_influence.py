# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "matplotlib>=3.11.1",
# ]
# ///
from __future__ import annotations

from pathlib import Path
from typing import TypedDict

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

ROOT = Path(__file__).resolve().parents[2]


class SectionData(TypedDict):
    """User-editable text and metrics for one section."""

    eyebrow: str
    title: str
    cards: list[tuple[str, str]]


class SectionLayout(TypedDict):
    """Drawing positions and card widths for one section."""

    title_y: float
    eyebrow_offset: float
    cards_y: float
    card_widths: list[float]


# Edit displayed text and values here.
FIGURE_DATA: dict[str, SectionData] = {
    "stewardship": {
        "eyebrow": "STEWARDSHIP",
        "title": "Core\nmaintainers",
        "cards": [("2", "total")],
    },
    "community": {
        "eyebrow": "COMMUNITY DEVELOPMENT",
        "title": "Contributors",
        "cards": [
            ("284", "total\ncontributors"),
            ("~150", "pull requests\nper year"),
        ],
    },
    "ecosystem": {
        "eyebrow": "SOFTWARE ECOSYSTEM",
        "title": "Downstream integration",
        "cards": [
            ("2,713", "dependent\nrepositories"),
            ("626", "dependent\npackages"),
        ],
    },
    "downloads": {
        "eyebrow": "DIRECT REACH",
        "title": "Package downloads",
        "cards": [("~23.2M", "PyPI downloads\nAug 2018–Dec 2025")],
    },
    "platform": {
        "eyebrow": "INDIRECT REACH",
        "title": "Platform-enabled interactions",
        "cards": [
            ("~1.8M", "Materials Project\nuses per year"),
            (">650,000", "registered MP\nusers"),
        ],
    },
}

# Layout is separate so changing values above does not disturb the geometry.
SECTION_LAYOUT: dict[str, SectionLayout] = {
    "stewardship": {
        "title_y": 0.852,
        "eyebrow_offset": 0.038,
        "cards_y": 0.744,
        "card_widths": [0.060],
    },
    "community": {
        "title_y": 0.675,
        "eyebrow_offset": 0.039,
        "cards_y": 0.592,
        "card_widths": [0.090, 0.100],
    },
    "ecosystem": {
        "title_y": 0.489,
        "eyebrow_offset": 0.040,
        "cards_y": 0.402,
        "card_widths": [0.100, 0.085],
    },
    "downloads": {
        "title_y": 0.321,
        "eyebrow_offset": 0.040,
        "cards_y": 0.235,
        "card_widths": [0.145],
    },
    "platform": {
        "title_y": 0.132,
        "eyebrow_offset": 0.040,
        "cards_y": 0.043,
        "card_widths": [0.125, 0.125],
    },
}


def add_metric_cards(
    ax: plt.Axes,
    *,
    y: float,
    cards: list[tuple[str, str]],
    widths: list[float],
) -> None:
    """Draw one centered row of metric cards."""
    gap = 0.024
    height = 0.064 if len(cards) > 1 else 0.066
    total_width = sum(widths) + gap * (len(cards) - 1)
    x = 0.5 - total_width / 2

    for (value, label), width in zip(cards, widths, strict=True):
        ax.add_patch(
            Rectangle(
                (x + 0.004, y - 0.004),
                width,
                height,
                transform=ax.transAxes,
                facecolor="#00000040",
                edgecolor="none",
                zorder=5,
            )
        )
        ax.add_patch(
            Rectangle(
                (x, y),
                width,
                height,
                transform=ax.transAxes,
                facecolor="#050505",
                edgecolor="none",
                zorder=6,
            )
        )
        ax.text(
            x + width / 2,
            y + height * 0.67,
            value,
            transform=ax.transAxes,
            ha="center",
            va="center",
            color="white",
            fontsize=8.5,
            fontweight="bold",
            zorder=7,
        )
        ax.text(
            x + width / 2,
            y + height * 0.27,
            label,
            transform=ax.transAxes,
            ha="center",
            va="center",
            color="white",
            fontsize=5.2,
            fontweight="bold",
            linespacing=1.05,
            zorder=7,
        )
        x += width + gap


def add_section(
    ax: plt.Axes,
    section: SectionData,
    layout: SectionLayout,
    index: int,
) -> None:
    """Draw the heading and metrics for one influence layer."""
    title_y = layout["title_y"]
    title = section["title"]
    ax.text(
        0.5,
        title_y + layout["eyebrow_offset"],
        section["eyebrow"],
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=6.5,
        fontfamily="DejaVu Sans Mono",
        fontweight="bold",
        zorder=4,
    )
    ax.text(
        0.5,
        title_y,
        title,
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=10.2 if index else 10.0,
        fontweight="bold",
        linespacing=1.02,
        zorder=4,
    )
    add_metric_cards(
        ax,
        y=layout["cards_y"],
        cards=section["cards"],
        widths=layout["card_widths"],
    )


def make_figure() -> plt.Figure:
    """Build and return the figure."""
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
        }
    )
    figure, ax = plt.subplots(figsize=(8.0, 7.45), constrained_layout=False)
    figure.patch.set_facecolor("white")
    ax.set_xlim(0, 1.073)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.axis("off")

    # x, y and radius are expressed in units of the figure height. Moving the
    # smaller circles upward creates the five readable bands in the reference.
    circles = [
        (0.5365, 0.500, 0.495, "#fae6fb"),
        (0.5365, 0.589, 0.392, "#ea8fc4"),
        (0.5365, 0.669, 0.292, "#e74698"),
        (0.5365, 0.745, 0.196, "#f7b53b"),
        (0.5365, 0.826, 0.095, "#fff173"),
    ]
    for x, y, radius, color in circles:
        ax.add_patch(Circle((x, y), radius, facecolor=color, edgecolor="none"))

    for index, (key, section) in enumerate(FIGURE_DATA.items()):
        add_section(ax, section, SECTION_LAYOUT[key], index)

    return figure


def main() -> None:
    """Save the figure as a publication-ready PDF."""
    output_path = ROOT / "paper" / "figs" / "shells-of-influence.pdf"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure = make_figure()

    figure.savefig(
        output_path,
        bbox_inches="tight",
        pad_inches=0.02,
        facecolor="white",
    )
    plt.close(figure)


if __name__ == "__main__":
    main()
