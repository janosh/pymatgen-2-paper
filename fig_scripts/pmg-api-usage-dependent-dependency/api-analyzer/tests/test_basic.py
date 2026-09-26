import json
import warnings
from collections.abc import Callable
from pathlib import Path

import pytest
from api_analyzer import analyze_notebook, analyze_paths, analyze_py

TEST_DIR = Path(__file__).parent / "data"


@pytest.mark.parametrize(
    ("analyze", "file_name", "n_calls"),
    [
        (analyze_py, "demo.py", 3),
        # calls in all three code cells contribute, including the nested function
        (analyze_notebook, "demo.ipynb", 4),
    ],
)
def test_analyze_file(
    analyze: Callable[[Path, str], tuple[dict[str, str], dict[str, int]]],
    file_name: str,
    n_calls: int,
) -> None:
    """Imports and calls are tracked in .py files and across notebook cells."""
    aliases, usage = analyze(TEST_DIR / file_name, "mypkg")
    assert aliases == {"core": "mypkg.core"}
    assert usage == {"mypkg.core.run": n_calls}


@pytest.mark.parametrize(
    ("analyze", "file_name", "content"),
    [
        (analyze_py, "bad.py", "x = (\n"),
        (
            analyze_notebook,
            "bad.ipynb",
            json.dumps({"cells": [{"cell_type": "code", "source": ["x = (\n"]}]}),
        ),
    ],
)
def test_analyze_ignores_syntax_error(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    analyze: Callable[[Path, str], tuple[dict[str, str], dict[str, int]]],
    file_name: str,
    content: str,
) -> None:
    """Malformed code is reported by its file name and contributes nothing."""
    path = tmp_path / file_name
    path.write_text(content)
    aliases, usage = analyze(path, "mypkg")
    stdout, _ = capsys.readouterr()

    assert f"Skipping {path} (AST parse error" in stdout
    assert aliases == {}
    assert usage == {}


def test_analyze_py_no_invalid_escape_warning(tmp_path: Path) -> None:
    """Invalid escape sequences in analyzed code emit no SyntaxWarning."""
    py_file = tmp_path / "escapes.py"
    py_file.write_text('import mypkg.core as core\ncore.run("\\d+")\n')
    with warnings.catch_warnings():
        warnings.simplefilter("error", SyntaxWarning)
        _aliases, usage = analyze_py(py_file, "mypkg")
    assert usage == {"mypkg.core.run": 1}


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
