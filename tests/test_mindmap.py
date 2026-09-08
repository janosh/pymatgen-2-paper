"""Check the actual Typst color mapping against logarithmic count positions."""

import json
import math
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from fig_scripts.pr_data import ROOT


@pytest.mark.skipif(
    shutil.which("typst") is None, reason="Typst is required for mindmap rendering"
)
def test_mindmap_count_scale(tmp_path: Path) -> None:
    """Use the parent maximum and one logarithmic scale for nodes and legend."""
    source = tmp_path / "check.typ"
    mindmap = f"{ROOT}/fig_scripts/openalex-topics-mindmap/mindmap.typ"
    source.write_text(
        f'#import "{mindmap}": count-max, count-position, count-color, count-gradient\n'
        "#metadata((maximum: count-max, positions: (1, 10, 100, 1000, 1253).map(count-position), "
        "colors: (11, 52, 1173, 1253).map(value => count-color(value).to-hex()))) <scale>",
        encoding="utf-8",
    )
    result = subprocess.check_output(
        [
            "typst",
            "query",
            "--root",
            os.path.abspath(os.sep),
            str(source),
            "<scale>",
            "--field",
            "value",
            "--one",
        ],
        text=True,
    )
    scale = json.loads(result)
    assert scale["maximum"] == 1253  # Largest displayed branch, greater than any leaf.
    expected = [
        math.log10(value) / math.log10(1253) for value in [1, 10, 100, 1000, 1253]
    ]
    assert scale["positions"] == pytest.approx(expected, rel=0, abs=1e-14)
    assert len(set(scale["colors"])) == 4  # No clipping the largest leaf to its parent.
