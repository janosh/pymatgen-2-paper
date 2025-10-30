# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "kaleido",
#     "pandas",
#     "plotly",
# ]
# ///
import json
import re
from pathlib import Path

import pandas as pd
import plotly.express as px

ROOT = Path(__file__).resolve().parents[2]


# 1) Load data
with open("_topics.json", encoding="utf-8") as f:
    topics_by_year = json.load(f)

# 2) Theme mapping rules
THEME_RULES: list[tuple[str, str]] = [
    (
        r"bug fix|bugfix|error|correction|refactor|cleanup|quality",
        "Bug Fixes & Refactoring",
    ),
    (r"performance|speed|optimization", "Performance"),
    (
        r"test|ci|continuous integration|type annotation|code modern|dependency|compatibility|deprecate|breaking",
        "Testing & Code Quality",
    ),
    (r"doc|readme|tutorial", "Documentation"),
    (
        r"json|serialize|parse|i/o|io|parser|vasp|fhi-aims|lobster|cp2k|q-?chem|qe|abinit|nwchem|gulp|zeopp|openbabel|jdf",
        "I/O & Parsing",
    ),
    (
        r"structure|symmetry|elastic|phonon|nmr|band|magnetic|defect|surface|interface|graph|molecule|analyzer|analysis|connectivity|voronoi|phase diagram|chemical system|periodic table|visualization",
        "Structural & Analysis",
    ),
    (
        r"new features|new modules",
        "Misc. New Features",
    ),
]


def map_theme(topic: str) -> str:
    for pat, theme in THEME_RULES:
        if re.search(pat.lower(), topic.lower()):
            return theme

    print(f"Cannot find a theme for {topic=}")
    return "Other"


# 3) Build dataframe of counts
rows: list[dict[str, str | int]] = []
for year, topics in topics_by_year.items():
    for topic in topics:
        if match := re.search(r"\((\d+)\)\s*$", topic):
            row = {"year": int(year), "theme": map_theme(topic), "count": int(match[1])}
            rows.append(row)
        else:
            raise ValueError(f"Cannot extract count from {topic=}")

df = pd.DataFrame(rows)
counts = df.groupby(["year", "theme"])["count"].sum().unstack(fill_value=0).sort_index()

# 4) Stacked bar plot with counts
colors = px.colors.qualitative.D3

fig = px.bar(
    counts,
    x=counts.index.astype(str),
    y=counts.columns,
    # title="PR Topics by Theme",
    labels={"value": "Number of PRs", "x": "Year", "variable": "Theme"},
    color_discrete_sequence=colors[: len(counts.columns)],
)

fig.update_layout(
    barmode="stack",
    title_x=0.5,  # center title
    title_font=dict(size=20),
    xaxis_title="Year",
    yaxis_title="Number of PRs",
    xaxis=dict(
        tickangle=45,
        tickfont=dict(size=12),
        type="category",  # ensures categorical x-axis
    ),
    yaxis=dict(
        tickfont=dict(size=12),
        gridcolor="lightgray",
        griddash="dash",  # dashed horizontal gridlines
    ),
    legend=dict(
        title="Theme",
        traceorder="reversed",
        x=1.02,
        y=1,  # move outside plot, upper left like mpl
        xanchor="left",
        yanchor="top",
        font=dict(size=14),
    ),
    plot_bgcolor="white",
    paper_bgcolor="white",
)

fig.write_image(f"{ROOT}/paper/figs/pr-topics-over-time-stacked-bar.pdf")
