# uruguay-stats

## Setup & run

```bash
uv sync                         # one-time setup (Python ≥3.14)
./<project>/plot.py             # single-chart: outputs {project}.{svg,png}
./<project>/plot.py --no-open   # suppress system viewer (CI/headless)
./<project>/plot.py --notebook  # generate notebook + open in JupyterLab
./build_notebooks.py            # generate all tagged notebooks
uv run ruff format              # format all Python files
uv run ruff check               # lint
uv run pyright                  # type-check
```

Multi-chart projects (bus, budget) additionally support:
```bash
./<project>/plot.py -c <variant>[,<variant>]  # select specific chart variants
```
`CI=1` suppresses `open_file()`.

## Tests

```bash
./test.py
```
Backs up tracked `.svg`/`.png`/`.ipynb` before running, restores after.

## Structure

- Each project: `<project>/plot.py` + `data/` + outputs (`{project}.{svg|png}` or `{project}-{variant}.{svg|png}`).
- No `__init__.py` in project dirs; no cross-imports between projects.
- `shared/` is a proper package (`uv_build` in `pyproject.toml`). Exports: `save_chart`, `get_cli_args`, `open_file`, `generate_notebook`.
- `data/` may contain processing scripts (e.g. `bus/data/download_lines.py`) and `README.md` with source docs.
- Dev deps (`ruff`, `pyright`) in `[project.optional-dependencies] dev`.

## Conventions & gotchas

- **Shebang**: `#! /usr/bin/env -S uv run python` on every `plot.py`.
- **`shared.utils` imports** (`generate_notebook`, `get_cli_args`, `open_file`, `save_chart`) go inside `if __name__ == "__main__":` — CLI-only, must not leak into notebooks.
- **Section markers**: `# --- SECTION NAME: <tag> ---`. Valid tags: `imports`, `constants`, `data loading`, `data processing`, `plot`, `metadata`. Unknown tags raise `SystemExit`.
- **Multi-chart**: declare `VARIANTS: list[str] = [...]` in the `metadata` section. Single-chart projects omit `metadata` entirely.
- **`__main__` patterns**:
  - Single-chart: `args = get_cli_args()`, then `save_chart(fig, output_dir / output_dir.name)`.
  - Multi-chart: `args = get_cli_args(VARIANTS)`, loop `for variant in selected:`, create fig + ax(s), call `globals()[f"plot_{variant.replace('-', '_')}"](ax)`, save as `{project}-{variant}`.
  - Both check `args.notebook` first, call `generate_notebook(project_name)`, then `raise SystemExit(0)`.
- **Matplotlib**: `plt.style.use("ggplot")`, `subplot_mosaic` (or `plt.subplots` for simple multi-chart layouts), `layout="constrained"`, `cm = 1 / 2.54`, 200 DPI output, `plt.rcParams["svg.hashsalt"] = "salt-for-svg-generation"`.
- **`save_chart`** sets `SOURCE_DATE_EPOCH=0` locally for deterministic SVG timestamps.
- **Spanish** for plot annotations and labels (except `electoral` which uses English).
- **Output files** (`.svg`, `.png`, `.ipynb`) **tracked in git** — `.gitignore` covers only `__pycache__/`, `.ruff_cache/`, `.venv/`, `.ipynb_checkpoints/`.
- **Notebook generation** (`build_notebooks.py`): uses AST for function splitting and variant extraction. Skips `__main__` block; replaces `Path(__file__).parent` with `Path.cwd()`.
- **Pre-commit** (`.githooks/pre-commit`): regenerates notebooks → `ruff format` → `ruff check --fix` → `pyright`. Enable via `uv run install-hooks`.
- **`electoral/plot.py`** shifts first-round markers -1yr via `assign_x()` for clarity.
