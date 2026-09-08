"""Check the actual Typst color mapping against logarithmic count positions."""

import json
import math
import os
import runpy
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

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


def test_mindmap_producer_accepts_descriptive_branch_titles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Export the requested descriptive headings without requiring a Topic_N prefix."""
    output = "\n".join(
        f"Research {idx}:\n    Subtopic {idx} ({10 + idx})" for idx in range(5)
    )
    exported: list[dict] = []
    monkeypatch.chdir(tmp_path)
    monkeypatch.setitem(
        sys.modules,
        "requests",
        SimpleNamespace(
            get=lambda *args, **kwargs: SimpleNamespace(
                json=lambda: {
                    "group_by": [
                        {"key_display_name": f"Subtopic {idx}", "count": 10 + idx}
                        for idx in range(5)
                    ]
                }
            )
        ),
    )
    monkeypatch.setitem(
        sys.modules,
        "openai",
        SimpleNamespace(
            OpenAI=lambda: SimpleNamespace(
                responses=SimpleNamespace(
                    create=lambda **kwargs: SimpleNamespace(output_text=output)
                )
            )
        ),
    )
    monkeypatch.setitem(
        sys.modules,
        "yaml",
        SimpleNamespace(safe_dump=lambda data, *args, **kwargs: exported.append(data)),
    )
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: None)
    runpy.run_path(
        f"{ROOT}/fig_scripts/openalex-topics-mindmap/openalex-topics-mindmap.py",
        run_name="__main__",
    )
    assert len(exported) == 1
    assert [branch["title"] for branch in exported[0]["branches"]] == [
        f"Research {idx}" for idx in reversed(range(5))
    ]
    assert [branch["children"][0]["value"] for branch in exported[0]["branches"]] == [
        14,
        13,
        12,
        11,
        10,
    ]
