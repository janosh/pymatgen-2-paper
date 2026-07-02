<h1 align="center">
  <img alt="Pymatgen 2 Logo" src="paper/figs/pymatgen-2-logo.svg" height="90" />
  <br>
  Pymatgen 2nd Paper
</h1>

This repository contains the manuscript, figures, and analysis scripts for the
second pymatgen paper: "pymatgen: 15 years of community growth, new functionality, and future prospects"

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
- `contribution_over_time_plot/`: aggregates contributor and commit activityover time.
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
- `py-pkg-treemap-pymatgen-coverage.pdf`: pymatgen code structure and test
  coverage, with module size representing lines of code and color representing
  coverage percentage.
- `pr-since-1st.pdf`: annual pymatgen pull requests grouped by contributor
  tenure since first pull request.
- `active-contributors-colored.pdf`: number of contributors and commits per year
  to pymatgen over time.
- `pr-contributors-worldmap.pdf`: geographic distribution of pymatgen pull
  request contributors, inferred from GitHub profile locations and curated
  sources.
- `citations.pdf` and `citations-by-country.pdf`: citation trends and geographic
  citation distribution for the original pymatgen paper.
