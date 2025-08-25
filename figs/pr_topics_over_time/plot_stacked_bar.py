import json
import re

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

# 1) Load data
with open("_topics.json", encoding="utf-8") as f:
    topics_by_year = json.load(f)

# 2) Theme mapping rules
THEME_RULES = [
    (r"bug fix|error|correction|refactor|cleanup|quality", "Bug fixes / refactoring"),
    (r"performance|speed|optimi", "Performance"),
    (r"test|ci|continuous integration", "Testing / CI"),
    (r"doc|readme|tutorial", "Documentation"),
    (r"deprecat|breaking", "Deprecations / breaking"),
    (r"json|serialize|parse|i/o|io|parser", "I/O & parsing"),
    (
        r"vasp|fhi-aims|lobster|cp2k|q-?chem|qe|abinit|nwchem|gulp|zeopp|openbabel|jdf",
        "Code integrations",
    ),
    (
        r"phase diagram|chemical system|periodic table|visualization",
        "Chem data / phase diagrams",
    ),
    (
        r"structure|symmetry|elastic|phonon|nmr|band|magnetic|defect|surface|interface|graph|molecule",
        "Structure & analysis",
    ),
    (r"python 3|type annotation|code modern|dependency", "Python & code quality"),
]


def map_theme(topic: str) -> str:
    s = topic.lower()
    for pat, theme in THEME_RULES:
        if re.search(pat, s):
            return theme
    return "Other"


# helper to extract count in "(N)" at end
def extract_count(s: str) -> int:
    m = re.search(r"\((\d+)\)\s*$", s)
    return int(m.group(1)) if m else 1


# 3) Build dataframe of counts
rows = []
for y, topics in topics_by_year.items():
    for t in topics:
        cnt = extract_count(t)
        rows.append({"year": int(y), "theme": map_theme(t), "count": cnt})

df = pd.DataFrame(rows)

counts = df.groupby(["year", "theme"])["count"].sum().unstack(fill_value=0).sort_index()

# 4) Stacked bar plot with absolute counts
fig, ax = plt.subplots(figsize=(10, 6))
colors = mpl.colormaps.get_cmap("tab20").colors
counts.plot(kind="bar", stacked=True, ax=ax, color=colors[: len(counts.columns)])

ax.set_title("PR Topics by Theme", fontsize=16)
ax.set_ylabel("Number of PRs", fontsize=16)
ax.set_xlabel("Year", fontsize=16)
ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=14)
ax.tick_params(axis="both", labelsize=12)
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("stacked_bar.svg", format="svg")
