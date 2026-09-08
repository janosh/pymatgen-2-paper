<h1 align="center">
  <img alt="Pymatgen 2 Logo" src="paper/figs/pymatgen-2-logo.svg" height="90" />
  <br>
  Pymatgen 2nd Paper
</h1>

This repository contains the manuscript, figures, and analysis scripts for the
second pymatgen paper: "pymatgen: 15 years of community growth, new functionality, and future prospects"

The README is intended as a high-level guide to the repository. Detailed
implementation notes, data processing choices, prompts, and intermediate
analysis steps are kept in the relevant scripts and notebooks so they stay close
to the code that uses them.

## Repository Structure

- `paper/`: source for a draft version of the manuscript, references, journal template, and generated
  figures used in the paper.
- `paper/figs/`: final figure assets included by the manuscript.
- `fig_scripts/`: reproducible scripts, notebooks, and cached data used to
  create the paper figures. Each subdirectory corresponds to one figure or
  closely related analysis.

## Figure Scripts

- `openalex-topics-mindmap/`: builds the OpenAlex topic mindmap for papers
  citing the first pymatgen paper.
- `pmg-api-usage-dependent-dependency/`: analyzes upstream pymatgen dependency
  usage and downstream use of pymatgen modules by dependent packages.
- `pr_topics_over_time/`: summarizes pull request topics over time and plots
  annual PR themes.
- `per_package_commit_heatmap/`: generates the package-level commit activity heatmap.
- `citation_by_country/`: maps citation counts by country.
- `citation_over_year/`: plots citation counts over time.
- `contribution_over_time_plot/`: aggregates contributor and commit activity over time.
- `pr_contributors_bar_plot/`: groups pull requests by contributor tenure since
  each contributor's first PR.
- `pr_contributors_worldmap/`: maps pull request contributors by inferred country.

## Figures

- `mindmap.pdf`: research topics among works citing the original pymatgen paper,
  with OpenAlex topics grouped into broader thematic branches.
- `pmg-dependency-usage.pdf`: upstream usage of third-party Python packages by
  pymatgen subpackages.
- `dependent-usage-of-pmg.pdf`: downstream usage of pymatgen subpackages by
  dependent packages.
- `pr-topics-over-time-stacked-bar.pdf`: annual pull requests in the pymatgen
  repository, categorized by theme.
- `commits-per-package-heatmap.png`: pymatgen package-level commit activity over
  time, aggregated into 6-month periods.
- `py-pkg-treemap-pymatgen-coverage.pdf`: pymatgen Python code structure and test coverage, with module size representing executable statements and color representing line coverage percentage from the same coverage.py report.
- `pr-since-1st.pdf`: annual pymatgen pull requests grouped by contributor
  tenure since first pull request.
- `active-contributors-colored.pdf`: number of contributors and commits per year
  to pymatgen over time.
- `pr-contributors-worldmap.pdf`: geographic distribution of pymatgen pull
  request contributors, inferred from GitHub profile locations and curated
  sources.
- `citations.pdf` and `citations-by-country.pdf`: citation trends and geographic
  citation distribution for the original pymatgen paper.

## Reproducing the corrected figures

Run the following commands from the repository root with the plotting dependencies in `pyproject.toml` available. PDF export requires Kaleido and Chrome; the mindmap requires Typst.

```sh
uv run --no-project python -m fig_scripts.pr_topics_over_time.plot_stacked_bar
uv run --no-project python -m fig_scripts.pr_contributors_bar_plot.plot_stacked_bar_plot
uv run --no-project python -m fig_scripts.code_coverage_treemap.plot_coverage_treemap
typst compile fig_scripts/openalex-topics-mindmap/mindmap.typ paper/figs/mindmap.pdf
uv run --no-project python -m pytest tests
```

**PR population and themes.** Both annual PR charts read `fig_scripts/pr_topics_over_time/_prs.json`, refreshed from the GitHub REST API on September 8, 2026. Each PR number is retained once, including repeated titles. The population is all non-bot PRs merged before January 1, 2026; years refer to merger dates. This gives 2,494 PRs in 2013-2025, including 167 in the complete 2025 calendar year, and a mean of 204.5 per year in 2014-2025. GitHub accounts typed as `Bot` or ending in `[bot]` are excluded. To refresh the cache, run `uv run --no-project python -m fig_scripts.pr_contributors_bar_plot._get_pr_contributor_data` with an authenticated GitHub CLI. It fetches PRs in all states so tenure can be measured at merger relative to each author's first PR submission, including unmerged PRs.

The ordered, case-insensitive title rules in `fig_scripts/pr_data.py` assign the first matching theme: Documentation, Testing & Code Quality, Performance, Bug Fixes & Refactoring, I/O & Parsing, Structural & Analysis, then Other / unclassified. Word boundaries prevent `io` and `ci` from matching inside unrelated words. The cache preserves each PR's title, dates, author and assigned theme for inspection. These are approximate title-based classifications, not manually validated descriptions of PR contents. Unlike the previous LLM-summary pipeline, no counts are inferred from generated text and no unmatched PRs disappear.

**Mindmap colors.** The existing topic labels, counts, and LLM-assisted grouping are preserved. The source query selects up to 50 OpenAlex primary topics with at least 10 citing works, then displays up to four topics in each of five branches. The mindmap is a selected thematic summary, not an exhaustive partition of all citations. Typst computes branch counts from displayed children and maps every count and legend tick through the same logarithmic Viridis scale, from 1 to the largest branch count (currently 1,253). Recompiling the YAML cache needs no API calls; the Python producer is only needed to refresh the topic data.

**Coverage snapshot.** The treemap uses the [July 31, 2025 coverage.py JSON report](https://github.com/user-attachments/files/21545087/2025-07-31-pymatgen-coverage.json) for both areas and colors, without inspecting an installed pymatgen version. Areas count executable statements in reported `src/pymatgen/*.py` files, including files with 0% coverage; package percentages are summed covered statements divided by summed executable statements. The report totals are 60,242 / 76,389 = 78.9%. Cells are grouped to three path components, and groups below 1,500 statements are combined into `other` within their subpackage. Subpackages below 5,000 statements are shown as single cells for readability. A local copy of the report can be supplied with `--coverage-file`. This is a dated test-suite snapshot, not a claim about coverage of a later source release.
