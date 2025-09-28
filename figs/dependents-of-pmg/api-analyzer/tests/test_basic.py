from pathlib import Path
from api_analyzer import analyze_py, analyze_notebook, analyze_paths


def test_analyze_py(tmp_path: Path):
    code = """
import mypkg.core as core
core.run()
"""
    f = tmp_path / "demo.py"
    f.write_text(code)

    aliases, usage = analyze_py(f, "mypkg")
    assert "core" in aliases
    assert "mypkg.core.run" in usage


def test_analyze_notebook(tmp_path: Path):
    nb = {
        "cells": [
            {
                "cell_type": "code",
                "source": ["import mypkg.utils as u\n", "u.foo()\n"],
            }
        ]
    }
    f = tmp_path / "demo.ipynb"
    f.write_text(str(nb).replace("'", '"'))

    aliases, usage = analyze_notebook(f, "mypkg")
    assert "u" in aliases
    assert "mypkg.utils.foo" in usage


def test_analyze_paths(tmp_path: Path):
    # Test dir with both py and ipynb
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "mod.py").write_text("import mypkg.core as c\nc.do()\n")
    (tmp_path / "demo.ipynb").write_text(
        str(
            {
                "cells": [
                    {
                        "cell_type": "code",
                        "source": ["import mypkg.x as x\n", "x.go()\n"],
                    }
                ]
            }
        ).replace("'", '"')
    )

    aliases, usage = analyze_paths(tmp_path, "mypkg", exclude=[".venv"])
    assert "c" in aliases or "x" in aliases
    assert any("mypkg" in k for k in usage)
