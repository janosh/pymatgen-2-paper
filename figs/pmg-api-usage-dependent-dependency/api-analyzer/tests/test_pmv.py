import os
import subprocess

import pytest
from api_analyzer import analyze_notebook, analyze_paths, analyze_py

if os.getenv("GITHUB_ACTIONS") == "true":
    pytest.skip("skip PMV test in CI", allow_module_level=True)


PMV_REPO_PATH: str | None = os.getenv("PMV_REPO_PATH")
PMV_COMMIT = "11f61e431e0ea6dd2f45797edf9e58479f36255c"


if PMV_REPO_PATH is None or not os.path.isdir(PMV_REPO_PATH):
    raise RuntimeError("You have to set `PMV_REPO_PATH` to the pymatviz repo path")


@pytest.fixture(scope="module", autouse=True)
def checkout_pmv_commit():
    orig = subprocess.check_output(
        ["git", "-C", PMV_REPO_PATH, "rev-parse", "HEAD"], text=True
    ).strip()

    subprocess.run(["git", "-C", PMV_REPO_PATH, "fetch"], check=True)
    subprocess.run(
        ["git", "-C", PMV_REPO_PATH, "checkout", PMV_COMMIT],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    yield

    subprocess.run(
        ["git", "-C", PMV_REPO_PATH, "checkout", orig],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def test_pmv_py():
    """
    NOTE:
        1. `local_env` is lazily imported, ensure it's captured.
        2. `core.Structure` is type checking only, should not be captured.
    """
    aliases, usage = analyze_py(
        f"{PMV_REPO_PATH}/pymatviz/chem_env.py", package="pymatgen"
    )

    assert "pymatgen.core.Structure" not in aliases.values()
    assert aliases == {"local_env": "pymatgen.analysis.local_env"}
    assert usage["pymatgen.analysis.local_env.CrystalNN"] >= 1


def test_pmv_ipynb():
    aliases, usage = analyze_notebook(
        f"{PMV_REPO_PATH}/examples/widgets/jupyter_demo.ipynb", package="pymatgen"
    )
    assert set(aliases.values()) == {
        "pymatgen.core.Composition",
        "pymatgen.core.Lattice",
        "pymatgen.core.Structure",
    }
    assert usage["pymatgen.core.Lattice.cubic"] == 2


def test_pmv_src():
    aliases, usage = analyze_paths(f"{PMV_REPO_PATH}/pymatviz", package="pymatgen")
    assert {
        "pymatgen.core.Structure",
        "pymatgen.analysis.chemenv.coordination_environments.coordination_geometries",
    }.issubset(aliases.values())

    assert usage["pymatgen.core.Structure.from_sites"] >= 1


def test_pmv_examples():
    aliases, usage = analyze_paths(f"{PMV_REPO_PATH}/examples", package="pymatgen")
    assert {
        "pymatgen.core.Composition",
        "pymatgen.io.vasp.sets.MPStaticSet",
    }.issubset(aliases.values())

    assert usage["pymatgen.core.Element.from_Z"] >= 1


def test_pmv_exclude():
    aliases, usage = analyze_paths(
        f"{PMV_REPO_PATH}",
        package="pymatgen",
        exclude=["pymatviz", "examples", ".venv"],
    )
    assert not aliases
    assert not usage
