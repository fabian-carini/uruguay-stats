#! /usr/bin/env -S uv run python

import ast
import re
from pathlib import Path

import nbformat

ROOT = Path(__file__).parent
SECTION_RE = re.compile(r"# --- SECTION NAME: (.+?) ---")
GITHUB_REPO = "fabian-carini/uruguay-stats"

VALID_SCRIPT_SECTIONS: frozenset[str] = frozenset(
    {
        "imports",
        "constants",
        "data loading",
        "data processing",
        "plot",
        "metadata",
    }
)


def parse_sections(plot_path: Path) -> dict[str, str]:
    """Split plot.py into {tag: code} sections, stopping before __main__."""
    sections: dict[str, str] = {}
    current_tag: str | None = None
    current_lines: list[str] = []

    for line in plot_path.read_text().splitlines():
        if line.lstrip().startswith('if __name__ == "__main__":'):
            break

        m = SECTION_RE.match(line)
        if m:
            if current_tag is not None:
                sections[current_tag] = "\n".join(current_lines)

            current_tag = m.group(1)
            if current_tag not in VALID_SCRIPT_SECTIONS:
                raise SystemExit(
                    f"{plot_path}: unknown section {current_tag!r} "
                    f"(valid: {', '.join(sorted(VALID_SCRIPT_SECTIONS))})"
                )

            current_lines = []
        elif current_tag is not None:
            current_lines.append(line)

    if current_tag is not None:
        sections[current_tag] = "\n".join(current_lines)

    return sections


def split_plot_section(code: str, chart_funcs: list[str]) -> tuple[str, dict[str, str]]:
    """Split plot section into shared preamble + per-function blocks using AST.

    Returns (shared_code, {chart_name: function_code}).
    Non-chart functions stay in shared_code.
    """
    tree = ast.parse(code)

    segments: list[str] = []
    chart_blocks: dict[str, str] = {}

    for node in tree.body:
        source = ast.get_source_segment(code, node)
        if source is None:
            continue
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in chart_funcs:
                chart_blocks[node.name] = source
            else:
                segments.append(source)
        else:
            segments.append(source)

    return "\n".join(segments).strip(), chart_blocks


def build_chart_cell(variant: str, func_name: str, func_code: str) -> nbformat.NotebookNode:
    code = f'''\
# --- SECTION NAME: plot "{variant}" ---

{func_code}


cm = 1 / 2.54
plt.style.use("ggplot")
fig, axs = plt.subplot_mosaic(
    [["main"]],
    figsize=(32 * cm, 18 * cm),
    layout="constrained",
)
ax = axs["main"]
{func_name}(ax)
plt.show()
'''
    return nbformat.v4.new_code_cell(code)


def extract_variants(code: str) -> list[str]:
    """Extract VARIANTS list from metadata section code using AST."""
    tree = ast.parse(code)
    for node in ast.walk(tree):
        targets = (
            node.targets
            if isinstance(node, ast.Assign)
            else [node.target]
            if isinstance(node, ast.AnnAssign)
            else []
        )
        value = node.value if isinstance(node, (ast.Assign, ast.AnnAssign)) else None
        if (
            value is not None
            and isinstance(value, ast.List)
            and any(isinstance(t, ast.Name) and t.id == "VARIANTS" for t in targets)
        ):
            return [
                el.value
                for el in value.elts
                if isinstance(el, ast.Constant) and isinstance(el.value, str)
            ]
    return []


def build_project(project_name: str) -> None:
    proj_dir = ROOT / project_name
    plot_path = proj_dir / "plot.py"

    sections = parse_sections(plot_path)

    # Collect variant names and their functions names
    variants: list[str] = extract_variants(sections.get("metadata", ""))
    chart_funcs: list[str] = [f"plot_{v.replace('-', '_')}" for v in variants]

    # Process plot section
    plot_shared = ""
    plot_funcs: dict[str, str] = {}
    if "plot" in sections:
        plot_shared, plot_funcs = split_plot_section(sections["plot"], chart_funcs)

    nb = nbformat.v4.new_notebook()
    cells: list = []

    # Cell 0: title + Colab badge + source link
    cells.append(
        nbformat.v4.new_markdown_cell(
            f"# {project_name.title()}\n\n"
            f"[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)]"
            f"(https://colab.research.google.com/github/{GITHUB_REPO}"
            f"/blob/main/{project_name}/{project_name}.ipynb)\n\n"
            f"Source: [{GITHUB_REPO}/tree/main/{project_name}]"
            f"(https://github.com/{GITHUB_REPO}/tree/main/{project_name})"
        )
    )

    # Cell 1: notebook configuration
    cells.append(
        nbformat.v4.new_code_cell(
            f"""\
# --- SECTION NAME: notebook configuration ---

import sys
if "google.colab" in sys.modules:
    from pathlib import Path
    !git clone https://github.com/{GITHUB_REPO}.git
    %cd uruguay-stats/{project_name}
import sys; sys.path.insert(0, '..')
import matplotlib.pyplot as plt
%matplotlib inline
plt.rcParams["svg.hashsalt"] = "salt-for-svg-generation"
"""
        )
    )

    # Remaining non-plot, non-metadata sections
    for tag, code in sections.items():
        if tag in ("plot", "metadata"):
            continue
        code = code.strip()
        if not code:
            continue
        code = f"# --- SECTION NAME: {tag} ---\n\n{code}"
        code = code.replace("Path(__file__).parent", "Path.cwd()")
        cells.append(nbformat.v4.new_code_cell(code))

    # Shared plot cell (preamble + non-chart helpers)
    if plot_shared:
        cell_code = f"# --- SECTION NAME: plot ---\n\n{plot_shared}"
        if not variants:
            cell_code += "\n\nplt.show()"
        cells.append(nbformat.v4.new_code_cell(cell_code))

    # Chart cells — each inlines its own function + figure boilerplate
    for variant in variants:
        func_name = f"plot_{variant.replace('-', '_')}"
        cells.append(build_chart_cell(variant, func_name, plot_funcs[func_name]))

    nb.cells = cells
    # Deterministic cell IDs to avoid git noise
    for i, cell in enumerate(nb.cells):
        cell.id = f"cell-{i}"
    out_path = proj_dir / f"{project_name}.ipynb"
    nbformat.write(nb, str(out_path))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    projects = sorted(p.name for p in ROOT.iterdir() if p.is_dir() and (p / "plot.py").exists())
    for p in projects:
        build_project(p)
