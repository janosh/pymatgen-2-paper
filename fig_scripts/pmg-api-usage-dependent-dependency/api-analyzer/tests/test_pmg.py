import os
import subprocess

import pytest

from api_analyzer import analyze_paths, analyze_py

if os.getenv("GITHUB_ACTIONS") == "true":
    pytest.skip("skip PMG test in CI", allow_module_level=True)


PMG_REPO_PATH: str | None = os.getenv("PMG_REPO_PATH")
PMG_COMMIT = "ab34799d8ab5dee80756489cf2ca28a97de78121"


if PMG_REPO_PATH is None or not os.path.isdir(PMG_REPO_PATH):
    raise RuntimeError("You have to set `PMG_REPO_PATH` to the pymatgen repo path")


@pytest.fixture(scope="module", autouse=True)
def checkout_pmg_commit():
    orig = subprocess.check_output(  # type: ignore[call-overload]
        ["git", "-C", PMG_REPO_PATH, "rev-parse", "HEAD"], text=True
    ).strip()

    subprocess.run(["git", "-C", PMG_REPO_PATH, "fetch"], check=True)  # type: ignore[call-overload]
    subprocess.run(  # type: ignore[call-overload]
        ["git", "-C", PMG_REPO_PATH, "checkout", PMG_COMMIT],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    yield

    subprocess.run(  # type: ignore[call-overload]
        ["git", "-C", PMG_REPO_PATH, "checkout", orig],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def test_pmg_py_numpy():
    aliases, usage = analyze_py(
        f"{PMG_REPO_PATH}/src/pymatgen/core/structure.py", package="numpy"
    )

    assert aliases

    assert usage["numpy.array"] == 24
    assert len(usage) == 37


def test_pmg_py_scipy():
    aliases, usage = analyze_py(
        f"{PMG_REPO_PATH}/src/pymatgen/core/surface.py", package="scipy"
    )

    assert aliases == {
        "fcluster": "scipy.cluster.hierarchy.fcluster",
        "linkage": "scipy.cluster.hierarchy.linkage",
        "squareform": "scipy.spatial.distance.squareform",
    }

    assert usage == {
        "scipy.cluster.hierarchy.linkage": 1,
        "scipy.spatial.distance.squareform": 1,
        "scipy.cluster.hierarchy.fcluster": 1,
    }


def test_pmg_core_dir_scipy():
    aliases, usage = analyze_paths(
        f"{PMG_REPO_PATH}/src/pymatgen/core", package="scipy"
    )

    assert len(aliases) >= 5
    assert usage == {
        "scipy.linalg.polar": 2,
        "scipy.spatial.distance.squareform": 4,
        "scipy.cluster.hierarchy.linkage": 4,
        "scipy.cluster.hierarchy.fcluster": 4,
        "scipy.ndimage.convolve1d": 2,
        "scipy.spatial.Voronoi": 1,
        "scipy.linalg.expm": 2,
    }
