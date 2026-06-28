# uruguay-stats

## Run

```bash
uv sync                      # one-time setup
./<project>/plot.py            # outputs {project}.{svg,png} (or {project}-{variant}.{svg,png} for multi-chart)
./<project>/plot.py --no-open  # suppress opening PNG in system viewer (headless/CI)
./<project>/plot.py -c <variant>[,<variant>] # select specific chart variants (multi-chart only)
./<project>/plot.py --notebook # generate notebook + open in JupyterLab
./build_notebooks.py           # generates notebooks for all tagged projects
uv run install-hooks            # installs the pre-commit hook
uv run ruff format              # format all Python files
uv run ruff check               # lint all Python files
uv run pyright                  # type-check all Python files
```

`CI=1` env var suppresses `open_file()`.

## Tests

```bash
./test.py
```

Backup/restore flow handles tracked image files + notebooks.

## Dependencies

`uv sync`. Requires Python ≥3.14. Key deps: `matplotlib`, `jupyterlab`, `nbformat`, `nbconvert`, `ipykernel`.

## Structure

- Each project is independent: `<project>/plot.py`, `data/`, outputs `{project}.{svg|png}` (or `{project}-{variant}.{svg|png}` for multi-chart).
- No cross-imports, no `__init__.py` in project dirs.
- `shared/` is a proper Python package registered in `pyproject.toml` via `uv_build`. Exports: `save_chart`, `get_cli_args`, `open_file`, `generate_notebook`.
- `data/` dirs may contain processing scripts and `README.md` with source docs.

## Conventions & gotchas

- Shebang: `#! /usr/bin/env -S uv run python` on every plot script.
- `shared.utils` imports (`generate_notebook`, `get_cli_args`, `open_file`, `save_chart`) go inside `if __name__ == "__main__":` — they are CLI-only and should not leak into notebooks.
- Section markers: `# --- SECTION NAME: <tag> ---` tags. Valid tags: `imports`, `constants`, `data loading`, `data processing`, `plot`, `metadata`. Unknown tags raise `SystemExit`.
- Multi-chart projects declare `VARIANTS: list[str] = [...]` in `metadata`; single-chart projects omit `metadata` entirely.
- `__main__` patterns:
  - **Single-chart**: `args = get_cli_args()`, then `save_chart(fig, output_dir / output_dir.name)`.
  - **Multi-chart**: `args = get_cli_args(VARIANTS)`, then loop `for variant in selected:` creating one fig per variant, calling `globals()[f"plot_{variant.replace('-', '_')}"](ax)`, saving as `{project}-{variant}`.
  - Both check `args.notebook` first, call `generate_notebook(project_name)`, then `raise SystemExit(0)`.
- Matplotlib: `plt.style.use("ggplot")`, `subplot_mosaic`, `layout="constrained"`, `cm = 1 / 2.54`, 200 DPI. `plt.rcParams["svg.hashsalt"] = "salt-for-svg-generation"`.
- `save_chart` sets `SOURCE_DATE_EPOCH=0` locally for deterministic SVG timestamps.
- Annotations in **Spanish**.
- Output files (`.svg`, `.png`, `.ipynb`) are **tracked in git** — `.gitignore` covers only `__pycache__/`, `.ruff_cache/`, `.venv/`, `.ipynb_checkpoints/`.
- `electoral/plot.py` shifts first-round markers -1yr via `assign_x()` for clarity.
- `bus/data/download_lines.py` and `abitab/data/parse_adresses.py` are examples of auxiliary data-processing scripts.
- `build_notebooks.py` uses AST for function splitting and variant extraction. Notebook generator skips `__main__` block, replaces `Path(__file__).parent` with `Path.cwd()`.
- Pre-commit hook at `.githooks/pre-commit` regenerates notebooks, formats, lints, and type-checks before every commit. Run `uv run install-hooks` to enable it (`git config core.hooksPath .githooks`).
- Dev dependencies (`ruff`, `pyright`) in `[project.optional-dependencies] dev` — install with `uv sync --dev`.
