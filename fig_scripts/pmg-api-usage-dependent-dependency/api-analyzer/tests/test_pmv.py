import os
import subprocess
from collections.abc import Iterator

import pytest
from api_analyzer import analyze_notebook, analyze_paths, analyze_py

if os.getenv("GITHUB_ACTIONS") == "true":
    pytest.skip("skip PMV test in CI", allow_module_level=True)


PMV_REPO_PATH = os.environ.get("PMV_REPO_PATH", "")
PMV_COMMIT = "11f61e431e0ea6dd2f45797edf9e58479f36255c"


if not os.path.isdir(PMV_REPO_PATH):
    raise RuntimeError("You have to set `PMV_REPO_PATH` to the pymatviz repo path")


@pytest.fixture(scope="module", autouse=True)
def checkout_pmv_commit() -> Iterator[None]:
    """Check out the pinned pymatviz commit for the module, then restore HEAD."""
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


def test_pmv_py() -> None:
    """Lazy imports are captured, `if TYPE_CHECKING:` imports are not."""
    # `local_env` is lazily imported, `core.Structure` is type checking only
    aliases, usage = analyze_py(
        f"{PMV_REPO_PATH}/pymatviz/chem_env.py", package="pymatgen"
    )

    assert "pymatgen.core.Structure" not in aliases.values()
    assert aliases == {"local_env": "pymatgen.analysis.local_env"}
    assert usage["pymatgen.analysis.local_env.CrystalNN"] >= 1


def test_pmv_ipynb() -> None:
    """Aliases and calls are collected from a real notebook."""
    aliases, usage = analyze_notebook(
        f"{PMV_REPO_PATH}/examples/widgets/jupyter_demo.ipynb", package="pymatgen"
    )
    assert set(aliases.values()) == {
        "pymatgen.core.Composition",
        "pymatgen.core.Lattice",
        "pymatgen.core.Structure",
    }
    assert usage["pymatgen.core.Lattice.cubic"] == 2


@pytest.mark.parametrize(
    ("subdir", "expected_aliases", "expected_call"),
    [
        (
            "pymatviz",
            {
                "pymatgen.core.Structure",
                "pymatgen.analysis.chemenv.coordination_environments.coordination_geometries",
            },
            "pymatgen.core.Structure.from_sites",
        ),
        (
            "examples",
            {"pymatgen.core.Composition", "pymatgen.io.vasp.sets.MPStaticSet"},
            "pymatgen.core.Element.from_Z",
        ),
    ],
)
def test_pmv_dir(subdir: str, expected_aliases: set[str], expected_call: str) -> None:
    """Directory analysis finds known aliases and calls in pymatviz source/examples."""
    aliases, usage = analyze_paths(f"{PMV_REPO_PATH}/{subdir}", package="pymatgen")
    assert expected_aliases.issubset(aliases.values())
    assert usage[expected_call] >= 1


def test_pmv_exclude() -> None:
    """Excluding every dir with pymatgen usage leaves nothing."""
    aliases, usage = analyze_paths(
        f"{PMV_REPO_PATH}",
        package="pymatgen",
        exclude=["pymatviz", "examples", ".venv"],
    )
    assert not aliases
    assert not usage
