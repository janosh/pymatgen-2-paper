import json
import re

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

# 1. Load data
with open("_topics.json", encoding="utf-8") as f:
    topics_by_year = json.load(f)

# 2. Map topics to coarse themes
# TODO:
THEME_RULES = [
    (r"bug fix|error|refactor|cleanup", "Bug fixes / refactoring"),
    (r"performance|speed|optimi", "Performance"),
    (r"test|ci|continuous integration", "Testing / CI"),
    (r"doc|readme|tutorial", "Documentation"),
    (r"deprecat|breaking", "Deprecations / breaking"),
    (r"json|serialize|parse|i/o|io|parser", "I/O & parsing"),
    (r"vasp|fhi-aims|lobster|cp2k|q-?chem|qe|abinit|nwchem|jdf", "Code integrations"),
    (r"phase diagram|chemical system|periodic table", "Chem data / phase diagrams"),
    (
        r"structure|symmetry|elastic|phonon|nmr|band|magnetic|defect|surface|interface|graph",
        "Structure & analysis",
    ),
    (r"python 3|type annotation|code modern", "Python & code quality"),
]


def map_theme(topic: str) -> str:
    s = topic.lower()
    for pat, theme in THEME_RULES:
        if re.search(pat, s):
            return theme
    return "Other"


# 3. Count themes per year
rows = []
for y, topics in topics_by_year.items():
    for t in topics:
        rows.append({"year": int(y), "theme": map_theme(t)})

df = pd.DataFrame(rows)
counts = df.groupby(["year", "theme"]).size().unstack(fill_value=0)

# Normalize to share per year
share = counts.div(counts.sum(axis=1), axis=0)

# Plot stacked area
fig, ax = plt.subplots(figsize=(10, 6))
colors = mpl.colormaps.get_cmap("tab20").colors  # TODO: pick colormap
share.sort_index().plot.area(ax=ax, color=colors[: len(share.columns)])

ax.set_title("PR Topic Mix Over Time")
ax.set_ylabel("Share of topics")
ax.set_xlabel("Year")
ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig("stacked_area.svg", format="svg")
