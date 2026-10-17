"""Plot exact annual counts from the shared, per-PR topic assignments."""

from collections import Counter

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from fig_scripts.pr_data import ROOT, THEMES, PaperPR, annual_counts, load_prs


def make_figure(records: dict[str, PaperPR]) -> go.Figure:
    """Count each PR once, including Other, and check every annual total."""
    counts = Counter(
        (int(record["merged_at"][:4]), record["theme"]) for record in records.values()
    )
    totals = annual_counts(records)
    rows = [
        {"year": year, "theme": theme, "count": counts[year, theme]}
        for year in sorted(totals)
        for theme in THEMES
    ]
    frame = pd.DataFrame(rows)
    if frame.groupby("year")["count"].sum().to_dict() != totals:
        raise ValueError("Topic counts do not reconcile with the PR population")
    figure = px.bar(
        frame,
        x="year",
        y="count",
        color="theme",
        category_orders={"theme": THEMES},
        color_discrete_sequence=[*px.colors.qualitative.D3[:6], "#999999"],
        labels={
            "year": "Year merged",
            "count": "Number of merged PRs",
            "theme": "Theme",
        },
    )
    figure.update_layout(
        barmode="stack",
        font=dict(size=20),
        legend=dict(orientation="h", y=1.03, yanchor="bottom", x=0, title_text=""),
        xaxis=dict(tickmode="array", tickvals=list(range(2013, 2026, 2))),
        yaxis=dict(gridcolor="lightgray", griddash="dash"),
        margin=dict(l=0, r=0, t=130, b=0),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    return figure


if __name__ == "__main__":
    make_figure(load_prs()).write_image(
        f"{ROOT}/paper/figs/pr-topics-over-time-stacked-bar.pdf", width=800, height=650
    )
