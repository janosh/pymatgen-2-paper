from pathlib import Path

import pytest
from api_analyzer import analyze_notebook, analyze_paths, analyze_py

TEST_DIR = Path(__file__).parent / "data"


def test_analyze_py() -> None:
    """Test analyzing a regular Python file."""
    demo_py = TEST_DIR / "demo.py"
    aliases, usage = analyze_py(demo_py, "mypkg")
    assert aliases == {"core": "mypkg.core"}
    assert usage == {"mypkg.core.run": 3}


def test_analyze_py_ignore_exception(capsys: pytest.CaptureFixture[str]) -> None:
    """Malformed Python is reported and contributes no aliases or usages."""
    aliases, usage = analyze_py(TEST_DIR / "syntax_err.py", "mypkg")
    stdout, _ = capsys.readouterr()

    assert "AST parse error" in stdout
    assert aliases == {}
    assert usage == {}


def test_analyze_notebook() -> None:
    """Test analyzing a Jupyter notebook with multiple cells."""
    demo_nb = TEST_DIR / "demo.ipynb"
    aliases, usage = analyze_notebook(demo_nb, "mypkg")

    assert aliases == {"core": "mypkg.core"}

    # Calls in all three code cells contribute, including the nested function.
    assert usage == {"mypkg.core.run": 4}


def test_analyze_paths() -> None:
    """Test directory-level analysis combining .py and .ipynb results."""
    aliases, usage = analyze_paths(TEST_DIR, "mypkg", exclude=["excluded"])

    # Expect combined aliases from both demo.py and demo.ipynb
    assert aliases == {"core": "mypkg.core"}

    # Three calls from demo.py and four from demo.ipynb; excluded files add nothing.
    assert usage == {"mypkg.core.run": 7}


def test_analyze_paths_not_dir() -> None:
    """Directory analysis rejects a path that is not a directory."""
    with pytest.raises(NotADirectoryError, match="is not a directory"):
        analyze_paths("/not_dir", "mypkg")
