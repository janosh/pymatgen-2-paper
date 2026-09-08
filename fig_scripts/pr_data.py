"""Shared PR population and title classification for the paper's annual charts."""

import json
import os
import re
from bisect import bisect_right
from collections import Counter
from datetime import datetime
from typing import TypedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PR_FILE = f"{ROOT}/fig_scripts/pr_topics_over_time/_prs.json"
CUTOFF = "2026-01-01T00:00:00Z"
OTHER = "Other / unclassified"
TENURE_GROUPS = ["<7 days", "7 days–<1 year", "1–<3 years", "3–<6 years", "≥6 years"]

# First match wins: explicit maintenance tasks take priority over scientific domains.
THEME_RULES = {
    "Documentation": r"\b(?:docs?|documentation|docstrings?|readme|tutorials?|citation|typos?)\b",
    "Testing & Code Quality": r"\b(?:tests?|testing|pytest|unittest|ci|lint|ruff|mypy|typing|type hints?|type annotations?|dependencies|dependency|packaging|compatibility|deprecate[ds]?|deprecation\w*|deprecating|python \d)\b",
    "Performance": r"\b(?:performance|speed\w*|optimi[sz]\w*|vectori[sz]\w*|cache[ds]?|caching|parallel\w*)\b",
    "Bug Fixes & Refactoring": r"\b(?:fix\w*|bug\w*|errors?|correct\w*|refactor\w*|cleanup|clean up)\b",
    "I/O & Parsing": r"\b(?:i/o|io|pars\w*|seriali[sz]\w*|json|vasp|incar|poscar|potcar|outcar|fhi[ -]aims|lobster|cp2k|q[ -]?chem|qe|abinit|nwchem|gulp|zeopp|openbabel|jdftx|lammps|api|cif|file formats?)\b",
    "Structural & Analysis": r"\b(?:structure\w*|structural\w*|symmetr\w*|elastic\w*|piezoelectric\w*|phonon\w*|nmr|bands?|magnet\w*|defect\w*|surface\w*|interface\w*|graphs?|molecul\w*|analy[sz]\w*|connectivity|voronoi|phase diagrams?|pourbaix|chemical systems?|periodic table|visuali[sz]\w*|composition\w*|lattice\w*|transformations?|thermodynamic\w*|diffusion)\b",
}
THEMES = [*THEME_RULES, OTHER]


class RawPR(TypedDict):
    """GitHub fields needed for filtering, grouping and contributor tenure."""

    number: int
    title: str
    author: str | None
    author_type: str | None
    created_at: str
    merged_at: str | None


class PaperPR(TypedDict):
    """One auditable, non-bot PR merged before the end of calendar year 2025."""

    title: str
    author: str
    created_at: str
    merged_at: str
    first_pr_at: str
    theme: str


def classify_pr(title: str) -> str:
    """Assign one theme by whole-word title rules, retaining unmatched PRs."""
    for theme, pattern in THEME_RULES.items():
        if re.search(pattern, title, re.IGNORECASE):
            return theme
    return OTHER


def prepare_prs(records: list[RawPR]) -> dict[str, PaperPR]:
    """Select full-year merged PRs, using all PRs to establish first submission."""
    first_dates: dict[str, str] = {}
    for record in records:
        author = record["author"]
        if author:
            first_dates[author] = min(
                first_dates.get(author, record["created_at"]), record["created_at"]
            )
    selected: dict[str, PaperPR] = {}
    for record in sorted(records, key=lambda entry: entry["number"]):
        author, merged_at = record["author"], record["merged_at"]
        if merged_at is None or merged_at >= CUTOFF:
            continue
        if author is None:
            raise ValueError(f"Missing author for merged PR #{record['number']}")
        if record["author_type"] == "Bot" or author.lower().endswith("[bot]"):
            continue
        pr_id = str(record["number"])
        if pr_id in selected:
            raise ValueError(f"Duplicate PR #{pr_id} in GitHub response")
        selected[pr_id] = {
            "title": record["title"],
            "author": author,
            "created_at": record["created_at"],
            "merged_at": merged_at,
            "first_pr_at": first_dates[author],
            "theme": classify_pr(record["title"]),
        }
    return selected


def load_prs(path: str = PR_FILE) -> dict[str, PaperPR]:
    """Read validated assignments shared by the topic and tenure charts."""
    with open(path, encoding="utf-8") as stream:
        records: dict[str, PaperPR] = json.load(stream)
    for pr_id, record in records.items():
        if record["theme"] not in THEMES:
            raise ValueError(f"Unknown theme for PR #{pr_id}: {record['theme']!r}")
        if (
            not record["first_pr_at"]
            <= record["created_at"]
            <= record["merged_at"]
            < CUTOFF
        ):
            raise ValueError(f"Invalid dates for PR #{pr_id}: {record}")
    return records


def annual_counts(records: dict[str, PaperPR]) -> Counter[int]:
    """Count distinct PR records by merger year, retaining repeated titles."""
    return Counter(int(record["merged_at"][:4]) for record in records.values())


def tenure_group(record: PaperPR) -> str:
    """Measure tenure at merger relative to the author's first PR submission."""
    elapsed_days = (
        datetime.fromisoformat(record["merged_at"])
        - datetime.fromisoformat(record["first_pr_at"])
    ).total_seconds() / 86_400
    group_idx = bisect_right((7, 365.25, 3 * 365.25, 6 * 365.25), elapsed_days)
    return TENURE_GROUPS[group_idx]
