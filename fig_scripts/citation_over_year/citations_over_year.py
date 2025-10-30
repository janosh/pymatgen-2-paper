# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "kaleido",
#     "pandas",
#     "plotly",
# ]
# ///

"""
Plot citations of 1st pymatgen paper over year bar plot.

https://scholar.google.com/scholar?hl=en&as_sdt=2005&sciodt=0,5&cites=6511812476881528112&scipsc=&q=#d=gs_md_hist&t=1756930044910
"""

from pathlib import Path

import pandas as pd
import plotly.express as px

ROOT = Path(__file__).resolve().parents[2]


df = pd.read_csv("citations.csv")

fig = px.bar(
    df,
    x="Year",
    y="Citations",
    labels={"Year": "Year", "Citations": "Number of Citations"},
    text="Citations",
)

fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",  # remove background (inside plot)
    paper_bgcolor="rgba(0,0,0,0)",  # remove outer background
    # title=dict(
    #     text="1<sup>st</sup> pymatgen Paper Citations Per Year",
    #     x=0.5,
    #     font=dict(size=24),
    # ),
    xaxis=dict(
        title=dict(text="Year", font=dict(size=18)),
        tickfont=dict(size=14),
        showgrid=False,
    ),
    yaxis=dict(
        title=dict(text="Number of Citations", font=dict(size=18)),
        tickfont=dict(size=14),
        showgrid=True,
        gridcolor="lightgray",
        gridwidth=2,
        griddash="dot",
    ),
)
fig.update_traces(textposition="outside", textfont=dict(size=14, color="black"))

# fig.show()
fig.write_image(f"{ROOT}/paper/figs/citations.pdf")
