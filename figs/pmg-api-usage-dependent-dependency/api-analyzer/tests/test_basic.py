from pathlib import Path
from api_analyzer import analyze_py, analyze_notebook, analyze_paths

import pytest

TEST_DIR = Path(__file__).parent / "data"


def test_analyze_py():
    """Test analyzing a regular Python file."""
    demo_py = TEST_DIR / "demo.py"
    aliases, usage = analyze_py(demo_py, "mypkg")
    assert "core" in aliases
    assert "mypkg.core.run" in usage
    assert usage["mypkg.core.run"] == 1


def test_analyze_notebook():
    """Test analyzing a Jupyter notebook with multiple cells."""
    demo_nb = TEST_DIR / "demo.ipynb"
    aliases, usage = analyze_notebook(demo_nb, "mypkg")

    assert aliases == {"core": "mypkg.core"}

    # should count both runs (one in each cell)
    assert usage == {"mypkg.core.run": 2}


def test_analyze_paths():
    """Test directory-level analysis combining .py and .ipynb results."""
    aliases, usage = analyze_paths(TEST_DIR, "mypkg", exclude=[".venv"])

    # Expect combined aliases from both demo.py and demo.ipynb
    expected_aliases = {"core": "mypkg.core"}
    assert aliases == expected_aliases

    # Expect one call from demo.py and two from demo.ipynb
    expected_usage = {"mypkg.core.run": 3}
    assert usage == expected_usage


def test_analyze_paths_not_dir():
    with pytest.raises(NotADirectoryError, match="is not a directory"):
        analyze_paths("/not_dir", "mypkg")
