#! /usr/bin/env -S uv run python

import atexit
import subprocess
import sys
import unittest
from pathlib import Path

import nbformat as nbf

from build_notebooks import extract_variants, parse_sections

ROOT = Path(__file__).parent

# Per-project output stems (without extension)
PROJECT_STEMS = {
    "electoral": ["electoral"],
    "approval": ["approval"],
    "abitab": ["abitab"],
    "bus": ["bus-stacked", "bus-per-company", "bus-distribution"],
    "budget": ["budget-stacked-pct", "budget-real-usd", "budget-lines"],
}

# Projects that also generate Jupyter notebooks
PROJECTS = [
    "electoral",
    "approval",
    "abitab",
    "bus",
    "budget",
]


# --- back up version-controlled image + notebook files, and restore them
#     after tests


def _backup():
    for proj, stems in PROJECT_STEMS.items():
        for stem in stems:
            for ext in ("svg", "png"):
                src = ROOT / proj / f"{stem}.{ext}"
                dst = ROOT / proj / f"{stem}.{ext}.bkp"
                if src.exists():
                    src.rename(dst)
    for proj in PROJECTS:
        src = ROOT / proj / f"{proj}.ipynb"
        dst = ROOT / proj / f"{proj}.ipynb.bkp"
        if src.exists():
            src.rename(dst)


def _restore():
    for proj, stems in PROJECT_STEMS.items():
        for stem in stems:
            for ext in ("svg", "png"):
                src = ROOT / proj / f"{stem}.{ext}.bkp"
                dst = ROOT / proj / f"{stem}.{ext}"
                if src.exists():
                    src.rename(dst)
    for proj in PROJECTS:
        src = ROOT / proj / f"{proj}.ipynb.bkp"
        dst = ROOT / proj / f"{proj}.ipynb"
        if src.exists():
            src.rename(dst)


_backup()

# Ensure cleanup happens also on SIGINT
atexit.register(_restore)


def _execute_notebook(nb_path: Path, out_path: Path) -> None:
    """Run jupyter nbconvert --execute on nb_path, writing to out_path."""
    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            str(nb_path),
            "--output",
            str(out_path),
        ],
        capture_output=True,
        timeout=120,
    )
    assert res.returncode == 0, (
        f"nbconvert exited {res.returncode}:\n{res.stdout.decode()}\n{res.stderr.decode()}"
    )


# --- tests


class TestPlotScripts(unittest.TestCase):
    def _run_cli(self, proj, *args):
        """Run plot.py with given args; assert exit code 0."""
        res = subprocess.run(
            [sys.executable, str(ROOT / proj / "plot.py"), *args],
            capture_output=True,
            timeout=30,
            env={"CI": "1"},
        )
        assert res.returncode == 0, (
            f"{proj} exited {res.returncode}:\n{res.stdout.decode()}\n{res.stderr.decode()}"
        )

    def _assert_stems(self, proj):
        """Assert every stem in PROJECT_STEMS for `proj` exists as SVG+PNG."""
        for stem in PROJECT_STEMS[proj]:
            for ext in ("svg", "png"):
                assert (ROOT / proj / f"{stem}.{ext}").exists(), f"{stem}.{ext} missing for {proj}"

    def test_electoral(self):
        self._run_cli("electoral")
        self._assert_stems("electoral")

    def test_approval(self):
        self._run_cli("approval")
        self._assert_stems("approval")

    def test_bus(self):
        self._run_cli("bus")
        self._assert_stems("bus")

    def test_abitab(self):
        self._run_cli("abitab")
        self._assert_stems("abitab")

    def test_budget(self):
        self._run_cli("budget")
        self._assert_stems("budget")

    # --- subset selection tests

    def test_single_variant(self):
        self._run_cli("bus", "-c", "stacked")
        for ext in ("svg", "png"):
            assert (ROOT / "bus" / f"bus-stacked.{ext}").exists()

    def test_two_variants(self):
        self._run_cli("bus", "-c", "stacked,distribution")
        for stem in ("bus-stacked", "bus-distribution"):
            for ext in ("svg", "png"):
                assert (ROOT / "bus" / f"{stem}.{ext}").exists()


# --- notebook generation tests


class TestNotebooks(unittest.TestCase):
    def _generate(self, proj: str) -> None:
        res = subprocess.run(
            [sys.executable, str(ROOT / "build_notebooks.py")],
            capture_output=True,
            timeout=30,
        )
        assert res.returncode == 0, (
            f"notebook gen exited {res.returncode}:\n{res.stdout.decode()}\n{res.stderr.decode()}"
        )
        nb_path = ROOT / proj / f"{proj}.ipynb"
        assert nb_path.exists(), f"{nb_path} not created"

    def _assert_notebook(self, proj: str) -> None:
        self._generate(proj)
        nb_path = ROOT / proj / f"{proj}.ipynb"
        tmp = ROOT / f"{proj}-executed-check.ipynb"
        try:
            _execute_notebook(nb_path, tmp)
            nb = nbf.read(tmp, as_version=4)

            meta_code = parse_sections(ROOT / proj / "plot.py").get("metadata", "")
            n_variants = len(extract_variants(meta_code))

            if n_variants:
                chart_cells = [
                    c
                    for c in nb.cells
                    if c.cell_type == "code"
                    and c.source.split("\n")[0].startswith('# --- SECTION NAME: plot "')
                ]
            else:
                chart_cells = [
                    c
                    for c in nb.cells
                    if c.cell_type == "code"
                    and c.source.split("\n")[0] == "# --- SECTION NAME: plot ---"
                ]

            n_expected = n_variants or 1
            assert len(chart_cells) == n_expected, (
                f"Expected {n_expected} chart cells, got {len(chart_cells)}"
            )

            for cell in chart_cells:
                assert len(cell.get("outputs", [])) >= 1, (
                    f"Chart cell has no outputs:\n{cell.source[:200]}"
                )
                errors = [o for o in cell.outputs if o.get("output_type") == "error"]
                assert not errors, (
                    f"Chart cell had errors: {errors[0]['ename']}: {errors[0]['evalue']}"
                )
        finally:
            if tmp.exists():
                tmp.unlink()

    def test_bus_notebook(self):
        self._assert_notebook("bus")

    def test_abitab_notebook(self):
        self._assert_notebook("abitab")

    def test_electoral_notebook(self):
        self._assert_notebook("electoral")

    def test_approval_notebook(self):
        self._assert_notebook("approval")

    def test_budget_notebook(self):
        self._assert_notebook("budget")


if __name__ == "__main__":
    unittest.main()
