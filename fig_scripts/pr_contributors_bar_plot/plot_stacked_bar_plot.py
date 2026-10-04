"""Plot merged PRs by contributor tenure using the topic chart's PR population."""

from collections import Counter

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from fig_scripts.pr_data import (
    ROOT,
    TENURE_GROUPS,
    PaperPR,
    annual_counts,
    load_prs,
    tenure_group,
)


def make_figure(records: dict[str, PaperPR]) -> go.Figure:
    """Group all included PRs by merger year and tenure at merger."""
    grouped = Counter(
        (int(record["merged_at"][:4]), tenure_group(record))
        for record in records.values()
    )
    counts = pd.DataFrame(
        [
            {"year": year, "tenure": group, "count": count}
            for (year, group), count in sorted(grouped.items())
        ]
    )
    if counts.groupby("year")["count"].sum().to_dict() != dict(annual_counts(records)):
        raise ValueError("Tenure counts do not reconcile with the PR population")
    figure = px.bar(
        counts,
        x="year",
        y="count",
        color="tenure",
        category_orders={"tenure": TENURE_GROUPS},
        color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
        labels={
            "year": "Year merged",
            "count": "Number of merged PRs",
            "tenure": "Time since first PR",
        },
    )
    figure.update_layout(
        barmode="stack",
        font=dict(size=18),
        xaxis=dict(
            tickmode="array", tickvals=list(range(2013, 2026, 2)), automargin=True
        ),
        yaxis=dict(gridcolor="lightgray", griddash="dash", automargin=True),
        legend=dict(x=0.01, y=1, traceorder="reversed"),
        # Explicit margins prevent axis titles from being clipped by static export or
        # by downstream PDF renderers. automargin handles font/rendering differences.
        margin=dict(l=110, r=20, t=20, b=75),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    return figure


if __name__ == "__main__":
    make_figure(load_prs()).write_image(f"{ROOT}/paper/figs/pr-since-1st.pdf")
