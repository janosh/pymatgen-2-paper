# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "kaleido",
#     "pymatgen==2025.10.7",
#     "pymatviz @ git+https://github.com/janosh/pymatviz",  # needs py_pkg_treemap depth pruning (pymatviz#346)
# ]
# ///
"""Treemap of the installed pymatgen package: cell size = lines of code, color = test coverage.

Coverage comes from a Codecov export of the pymatgen test suite. Mirrors
pymatviz/assets/scripts/treemap/py_pkg_treemap.py.
"""

from pathlib import Path

import pymatgen
import pymatviz as pmv

ROOT = Path(__file__).resolve().parents[2]
COVERAGE_JSON = "https://github.com/user-attachments/files/21545087/2025-07-31-pymatgen-coverage.json"
FONT_SCALE = 1.3

# Namespace packages have their own repos and coverage reports, so they would show
# as 0% coverage here which is misleading. Exclude them.
NAMESPACE_PKGS = {"analysis.defects", "analysis.diffusion"}


def cell_size(cell: pmv.treemap.py_pkg.ModuleStats) -> int:
    """Lines of code per cell, dropping namespace packages and near-empty files."""
    dotted = f".{cell.full_module}."
    if any(f".{ns_pkg}." in dotted for ns_pkg in NAMESPACE_PKGS):
        return 0
    return cell.line_count if cell.line_count >= 20 else 0


fig = pmv.py_pkg_treemap(
    pymatgen,
    color_by="coverage",
    coverage_data_file=COVERAGE_JSON,
    color_range=(0, 100),
    cell_size_fn=cell_size,
    show_counts="value",
    color_continuous_scale="RdYlGn",
    max_module_depth=3,
    min_lines_for_split=500,  # only expand if every child has >=500 lines
    max_children_for_split=5,  # only expand if parent has <=5 children
)
trace = fig.data[0]

# pymatviz omits the per-cell "% cov" text under depth pruning (aggregated nodes lack
# customdata) but marker.colors still holds every cell's coverage, so rebuild the text
trace.text = [f"{cov:.0f}% cov" for cov in trace.marker.colors]
trace.texttemplate = "%{label}<br>%{value:,}<br>%{text}"
trace.textfont.size = 12 * FONT_SCALE  # plotly shrinks to fit, this is the max
fig.layout.font.size = 12 * FONT_SCALE  # colorbar
fig.layout.margin = {"l": 0, "r": 0, "b": 0, "t": 0}
# the colorbar defaults to the full figure height, so with zero top/bottom margin its
# outermost tick labels (0 and 100) stick out past the canvas and get clipped. Shrink it
# by half a label at each end, keeping the treemap itself full-bleed.
fig.layout.coloraxis.colorbar.update(len=0.94, y=0.5, yanchor="middle")

# Print top-level subpackage coverage so the numbers in the paper text can be checked
for cell_id, value, cov in zip(
    trace.ids, trace.values, trace.marker.colors, strict=True
):
    if cell_id.count("/") <= 1:  # root and its direct children
        print(f"{cell_id.split('/')[-1]:<22} {int(value):>8,} lines  {cov:5.1f}%")

fig.write_image(
    f"{ROOT}/paper/figs/py-pkg-treemap-pymatgen-coverage.pdf", width=900, height=495
)
