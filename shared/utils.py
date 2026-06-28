import argparse
import os
import signal
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def install_hooks() -> None:
    """Set git hooksPath to .githooks so the pre-commit hook runs."""
    current = subprocess.run(
        ["git", "config", "core.hooksPath"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if current != ".githooks":
        subprocess.run(
            ["git", "config", "core.hooksPath", ".githooks"],
            cwd=ROOT,
            capture_output=True,
        )


def open_file(path):
    """Open a file with the system default application (cross-platform)."""
    if os.environ.get("CI"):
        return
    path = Path(path)
    if not path.exists():
        print(f"Warning: {path} not found, nothing to open", file=sys.stderr)
        return

    if sys.platform == "win32":
        try:
            os.startfile(path)
        except OSError as e:
            print(f"Warning: could not open {path}: {e}", file=sys.stderr)
        return

    cmd = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.Popen([cmd, path], start_new_session=True)


def get_cli_args(variants: list[str] | None = None) -> argparse.Namespace:
    """Configure argparse for chart generation and return arguments."""

    bold = "\033[1m"
    yellow = "\033[33m"
    reset = "\033[0m"
    variants_text = ", ".join(f"{bold}{yellow}{v}{reset}" for v in variants) if variants else ""

    parser = argparse.ArgumentParser(
        suggest_on_error=True,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Available chart variants: {variants_text}" if variants else None,
    )
    if variants:
        parser.add_argument(
            "-c",
            "--chart",
            default="all",
            help="Chart variant(s), comma-separated, or 'all' (default: all)",
        )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not open generated files",
    )
    parser.add_argument(
        "--notebook",
        action="store_true",
        help="Generate and open Jupyter notebook instead of charts",
    )
    args = parser.parse_args()

    # validate the chart argument
    if variants:
        if args.chart == "all":
            args.chart = list(variants)
        else:
            seen: set[str] = set()
            resolved: list[str] = []
            for v in args.chart.split(","):
                v = v.strip()
                if v not in variants:
                    raise SystemExit(
                        f"invalid chart variant: '{v}' (choose from {{{variants_text}}})"
                    )
                if v not in seen:
                    seen.add(v)
                    resolved.append(v)
            args.chart = resolved

    return args


def save_chart(fig, stem_path: Path) -> Path:
    """Save a matplotlib figure as SVG + PNG with standard settings.
    Returns the PNG path.
    """
    # Pin the SVG timestamp so identical runs produce identical SVGs.
    # Source: https://github.com/matplotlib/matplotlib/issues/23693
    old_date = os.environ.get("SOURCE_DATE_EPOCH")
    os.environ["SOURCE_DATE_EPOCH"] = "0"

    try:
        stem_path = Path(stem_path)
        for fmt in ("svg", "png"):
            fig.savefig(
                stem_path.with_suffix(f".{fmt}"),
                dpi=200,
                bbox_inches="tight",
                pad_inches=0.5,
            )
    finally:
        if old_date is None:
            del os.environ["SOURCE_DATE_EPOCH"]
        else:
            os.environ["SOURCE_DATE_EPOCH"] = old_date

    return stem_path.with_suffix(".png")


def generate_notebook(project_name: str) -> None:
    """Generate notebook for a project and open it."""
    from build_notebooks import build_project

    build_project(project_name)
    nb = ROOT / project_name / f"{project_name}.ipynb"

    # Launch via jupyter lab
    proc = subprocess.Popen(["uv", "run", "jupyter", "lab", str(nb)])
    orig = signal.signal(signal.SIGINT, signal.SIG_IGN)
    proc.wait()
    signal.signal(signal.SIGINT, orig)
