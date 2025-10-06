import os

from api_analyzer import analyze_paths, analyze_py

pmg_root = os.getenv("PMG_REPO_PATH")
if not pmg_root:
    raise ValueError("PMG_REPO_PATH environment variable must be set")
PMG_REPO_PATH: str = f"{pmg_root}/src/pymatgen"


def test_pmg_py_numpy():
    aliases, usage = analyze_py(f"{PMG_REPO_PATH}/core/structure.py", package="numpy")

    assert aliases

    assert usage["numpy.array"] == 24
    assert len(usage) == 37


def test_pmg_py_scipy():
    aliases, usage = analyze_py(f"{PMG_REPO_PATH}/core/surface.py", package="scipy")

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
    aliases, usage = analyze_paths(f"{PMG_REPO_PATH}/core", package="scipy")

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
