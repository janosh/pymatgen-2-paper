"""Ensure pymatviz/pymatgen is at a fixed commit for reproducible tests."""

import os
import subprocess

import pytest


PMG_REPO_PATH: str | None = os.getenv("PMG_REPO_PATH")
PMG_COMMIT = "ab34799d8ab5dee80756489cf2ca28a97de78121"

PMV_REPO_PATH: str | None = os.getenv("PMV_REPO_PATH")
PMV_COMMIT = "11f61e431e0ea6dd2f45797edf9e58479f36255c"

if PMG_REPO_PATH is None or not os.path.isdir(PMG_REPO_PATH):
    raise RuntimeError("You have to set `PMG_REPO_PATH` to the pymatgen repo path")

if PMV_REPO_PATH is None or not os.path.isdir(PMV_REPO_PATH):
    raise RuntimeError("You have to set `PMV_REPO_PATH` to the pymatviz repo path")


@pytest.fixture(scope="session", autouse=True)
def checkout_pmg_commit():
    orig = subprocess.check_output(
        ["git", "-C", PMG_REPO_PATH, "rev-parse", "HEAD"], text=True
    ).strip()

    subprocess.run(["git", "-C", PMG_REPO_PATH, "fetch"], check=True)
    subprocess.run(
        ["git", "-C", PMG_REPO_PATH, "checkout", PMG_COMMIT],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    yield

    subprocess.run(
        ["git", "-C", PMG_REPO_PATH, "checkout", orig],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


@pytest.fixture(scope="session", autouse=True)
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
