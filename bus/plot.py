#! /usr/bin/env -S uv run python

# --- SECTION NAME: imports ---
import csv
import re
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

# --- SECTION NAME: constants ---

CURRENT_YEAR: int = 2026
YEAR_RANGE: range = range(1920, CURRENT_YEAR + 1)

# bottom to top in plot
COMPANIES: list[str] = [
    "Pre-CUTCSA",
    "CUTCSA",
    "COME",
    "UCOT",
    "COETC",
    "Raincoop",
    "COTSUR",
    "AMDET",
]


# legend order (independent of stack order)
LEGEND_ORDER: list[str] = [
    "Pre-CUTCSA",
    "CUTCSA",
    "AMDET",
    "COME",
    "UCOT",
    "COETC",
    "COTSUR",
    "Raincoop",
]

COLORS: dict[str, str] = {
    "Pre-CUTCSA": "#C4A882",
    "CUTCSA": "#3A3E7E",
    "UCOT": "#FFF200",
    "COETC": "#C80000",
    "COME": "#298A08",
    "Raincoop": "#9B5DE5",
    "COTSUR": "#F4A86A",
    "AMDET": "#8D8D8D",
}

KEY_EVENTS: dict[int, str] = {
    1937: "CUTCSA\nfundada",
    1963: "UCOT/COETC/COME\nfundadas",
    1975: "AMDET\ndisuelta",
    1992: "COTSUR/COOPTROL\ndisueltas",
    2007: "STM\nlanzado",
    2016: "Raincoop\ndisuelta",
}

# --- SECTION NAME: data loading ---


data_dir = Path(__file__).parent / "data"
with open(data_dir / "lines.csv") as f:
    raw_rows = list(csv.DictReader(f))


# --- SECTION NAME: data processing ---


def normalize_company(name: str) -> str | None:
    name = name.strip()
    if "PRE-CUTCSA" in name.upper():
        return "Pre-CUTCSA"
    if "CUTCSA" in name.upper():
        return "CUTCSA"
    if "UCOT" in name.upper():
        return "UCOT"
    if "COETC" in name.upper():
        return "COETC"
    if re.search(r"\bCOME\b|COMESA", name, re.I):
        return "COME"
    if "RAINCOOP" in name.upper():
        return "Raincoop"
    if "COTSUR" in name.upper():
        return "COTSUR"
    if "AMDET" in name.upper():
        return "AMDET"
    return None


def parse_year_field(s: str | None) -> int | None:
    if not s:
        return None
    s = s.strip().lstrip("~")
    if "~" in s:
        s = s.split("~")[0]
    try:
        return int(s)
    except ValueError:
        return None


def parse_history_row(hist_str: str) -> list[tuple[str, int | None, int | None]]:
    # Date spec inside parens: YEAR | ~YEAR | YEAR~YEAR | present | actualidad | unknown
    _date = r"~?\d{4}(?:~\d{4})?"
    period_re = re.compile(
        rf"([^(;]+)\(\s*({_date}|unknown)\s*-\s*({_date}|present|actualidad|unknown)\s*\)"
    )

    def _year_from_spec(s):
        """Lower bound of a date spec like ~1928 or 1948~1975."""
        s = s.lstrip("~")
        return int(s.split("~")[0])

    periods = []
    for m in period_re.finditer(hist_str):
        company = normalize_company(m.group(1))
        if not company:
            continue
        raw_start = m.group(2)
        yr_start = None if raw_start == "unknown" else _year_from_spec(raw_start)
        raw_end = m.group(3)
        if raw_end in ("present", "actualidad"):
            yr_end = CURRENT_YEAR
        elif raw_end == "unknown":
            yr_end = None
        else:
            yr_end = _year_from_spec(raw_end)
        periods.append((company, yr_start, yr_end))

    # handoff years are stored as the same year in both periods; make them
    # non-overlapping by giving the outgoing period the year before
    for i in range(len(periods) - 1):
        co, yr_s, yr_e = periods[i]
        _, next_yr_s, _ = periods[i + 1]
        if yr_e is not None and next_yr_s is not None and yr_e == next_yr_s:
            periods[i] = (co, yr_s, yr_e - 1)

    return periods


def _resolve_end(yr_s: int | None, yr_e: int | None) -> int:
    """Replace unknown (None) end with yr_s + UNKNOWN_END_YEARS."""
    unknown_end_years = 10  # assumed lifespan for lines with unknown suppression date

    if yr_e is not None:
        return yr_e
    return (yr_s + unknown_end_years) if yr_s is not None else CURRENT_YEAR


def build_periods(rows: list[dict[str, str]]) -> list[tuple[str, int | None, int]]:
    all_periods: list[tuple[str, int | None, int]] = []
    for r in rows:
        # get periods from history row
        if r["company_history"]:
            periods = parse_history_row(r["company_history"])
            if not periods:
                continue

            # year_start is a hard floor: it drops pre-bus eras (tram,
            # trolleybus), it clamps surviving period to the bus debut year
            yr_floor = parse_year_field(r["year_start"])
            if yr_floor is not None:
                periods = [
                    (company, max(yr_start or yr_floor, yr_floor), yr_end)
                    for company, yr_start, yr_end in periods
                    if yr_end is None or yr_end >= yr_floor
                ]

            # persist
            all_periods.extend(
                (company, yr_start, _resolve_end(yr_start, yr_end))
                for company, yr_start, yr_end in periods
            )
            continue

        # fallback: no history — use company_current + year_start
        yr_start = parse_year_field(r["year_start"])
        if yr_start is None:
            continue
        if r["status"] == "inactive":
            end = _resolve_end(yr_start, parse_year_field(r["year_end"]))
        else:
            end = CURRENT_YEAR
        for co_name in r["company_current"].split("+"):
            co = normalize_company(co_name)
            if co:
                all_periods.append((co, yr_start, end))

    return all_periods


def count_per_year(periods: list[tuple[str, int | None, int]]) -> dict[str, dict[int, int]]:
    counts: defaultdict[str, defaultdict[int, int]] = defaultdict(lambda: defaultdict(int))
    for co, yr_s, yr_e in periods:
        if yr_s is None:
            continue
        for y in range(max(yr_s, YEAR_RANGE.start), min(yr_e + 1, YEAR_RANGE.stop)):
            counts[co][y] += 1
    return counts  # type: ignore[return-value]


periods: list[tuple[str, int | None, int]] = build_periods(raw_rows)
counts: dict[str, dict[int, int]] = count_per_year(periods)

# --- SECTION NAME: plot ---

xs: list[int] = list(YEAR_RANGE)
ys_by_company: dict[str, list[int]] = {co: [counts[co][y] for y in xs] for co in COMPANIES}


def _draw_titles(ax: Axes, title: str | None = None, subtitle: str | None = None) -> None:
    if title is None:
        title = "Líneas de ómnibus de Montevideo por empresa operadora (1920–2026)"
    if subtitle is None:
        subtitle = (
            "Solo ómnibus (tranvías y trolebuses excluidos) · "
            '"Líneas" = rutas, no cantidad de vehículos'
        )
    ax.text(
        0.5,
        1.06,
        title,
        transform=ax.transAxes,
        ha="center",
        fontsize=14,
        fontweight="bold",
    )
    ax.text(
        0.5,
        1.02,
        subtitle,
        transform=ax.transAxes,
        ha="center",
        fontsize=10,
        style="italic",
    )


def _draw_key_events(ax: Axes) -> None:
    top = ax.get_ylim()[1]
    for yr, label in KEY_EVENTS.items():
        ax.axvline(yr, linestyle=":", linewidth=1, color="black", alpha=0.9, zorder=5)
        ax.text(
            yr + 0.4,
            top,
            label,
            fontsize=8,
            color="black",
            alpha=0.9,
            va="top",
            ha="left",
        )


def plot_stacked(ax: Axes) -> None:
    ax.stackplot(
        xs,
        [ys_by_company[co] for co in COMPANIES],
        colors=[COLORS[co] for co in COMPANIES],
        alpha=0.85,
        step="pre",
    )
    _draw_key_events(ax)
    _draw_titles(ax)
    ax.set_xlabel("Año")
    ax.set_ylabel("Líneas activas")
    ax.set_xlim(YEAR_RANGE.start, YEAR_RANGE.stop - 1)
    ax.set_xticks(range(YEAR_RANGE.start, YEAR_RANGE.stop, 10))
    ax.set_ylim(0, 175)
    handles = {co: Rectangle((0, 0), 1, 1, color=COLORS[co]) for co in COMPANIES}
    ax.legend(
        [handles[co] for co in LEGEND_ORDER],
        LEGEND_ORDER,
        loc="upper left",
        fontsize=9,
    )


def plot_per_company(ax: Axes) -> None:
    # nudges for the plot
    label_offsets = {
        "UCOT": 4,
    }
    line_offsets = {
        "UCOT": 1,
    }

    active = [co for co in COMPANIES if counts[co][CURRENT_YEAR] > 0]
    for co in active:
        offset = line_offsets.get(co, 0)
        ys: list[int | None] = [v + offset if v else None for v in ys_by_company[co]]
        ax.plot(xs, ys, color=COLORS[co], linewidth=2.5)  # type: ignore[arg-type]
        # annotate the last active year rather than always at 2026
        last_yr = max((y for y in xs if counts[co][y] > 0), default=None)
        if last_yr is not None:
            total = sum(counts[c][last_yr] for c in COMPANIES)
            pct = counts[co][last_yr] / total * 100 if total else 0
            ax.text(
                last_yr + 0.5,
                counts[co][last_yr] + label_offsets.get(co, 0),
                f"{counts[co][last_yr]} ({pct:.0f}%)",
                color=COLORS[co],
                fontsize=12,
                va="center",
            )
    # _draw_key_events(ax)
    _draw_titles(ax)
    ax.set_xlabel("Año")
    ax.set_ylabel("Líneas")
    ax.set_xlim(YEAR_RANGE.start, YEAR_RANGE.stop + 9)  # room for right-side labels
    ax.set_xticks(range(YEAR_RANGE.start, YEAR_RANGE.stop, 10))
    ax.set_ylim(0, 110)
    by_count = sorted(active, key=lambda co: counts[co][CURRENT_YEAR], reverse=True)
    handles = {co: Rectangle((0, 0), 1, 1, color=COLORS[co]) for co in active}
    ax.legend(
        [handles[co] for co in by_count],
        by_count,
        loc="upper left",
        fontsize=9,
    )


def build_active_numbered_lines(rows: list[dict[str, str]]) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    for r in rows:
        try:
            num = int(r["line"].strip())
        except ValueError:
            continue
        company = None
        if r["company_history"]:
            periods = parse_history_row(r["company_history"])
            yr_floor = parse_year_field(r["year_start"])
            if yr_floor is not None:
                periods = [
                    (co, max(yr_s or yr_floor, yr_floor), yr_e)
                    for co, yr_s, yr_e in periods
                    if yr_e is None or yr_e >= yr_floor
                ]
            for co, yr_s, yr_e in periods:
                if _resolve_end(yr_s, yr_e) >= CURRENT_YEAR:
                    company = co
        else:
            if r["status"] == "active":
                for co_name in r["company_current"].split("+"):
                    co = normalize_company(co_name)
                    if co:
                        company = co
                        break
        if company:
            result.append((num, company))
    return result


def plot_distribution(ax: Axes) -> None:
    bin_size = 10

    active = build_active_numbered_lines(raw_rows)
    max_num = max(num for num, _ in active)
    n_bins = (max_num + bin_size - 1) // bin_size

    bin_counts = defaultdict(lambda: defaultdict(int))
    for num, co in active:
        bin_counts[(num - 1) // bin_size][co] += 1

    bin_xs = list(range(n_bins))
    bin_labels = [str(i * bin_size + 1) for i in bin_xs]

    present_cos = [co for co in COMPANIES if any(bin_counts[b][co] for b in bin_xs)]
    bottoms = [0] * n_bins
    for co in present_cos:
        heights = [bin_counts[b][co] for b in bin_xs]
        ax.bar(bin_xs, heights, bottom=bottoms, color=COLORS[co], label=co, width=0.8)
        bottoms = [b + h for b, h in zip(bottoms, heights)]

    ax.set_xticks(bin_xs)
    ax.set_xticklabels(bin_labels, rotation=45, ha="right", fontsize=8)
    ax.set_xlabel("Número de línea (inicio de grupo de 10)")
    ax.set_ylabel("Líneas activas en el grupo")
    ax.set_ylim(0, bin_size)
    _draw_titles(
        ax,
        title="Distribución de líneas de ómnibus activas de Montevideo por número (2026)",
        subtitle="Solo líneas con número (se excluyen letras) · agrupadas en rangos de 10",
    )
    handles = {co: Rectangle((0, 0), 1, 1, color=COLORS[co]) for co in present_cos}
    ax.legend(
        [handles[co] for co in present_cos],
        present_cos,
        loc="upper right",
        fontsize=9,
    )


# --- SECTION NAME: metadata ---

VARIANTS: list[str] = ["stacked", "per-company", "distribution"]

if __name__ == "__main__":
    from shared.utils import generate_notebook, get_cli_args, open_file, save_chart

    args = get_cli_args(VARIANTS)
    if args.notebook:
        generate_notebook("bus")
        raise SystemExit(0)
    selected = args.chart

    cm = 1 / 2.54
    plt.style.use("ggplot")
    plt.rcParams["svg.hashsalt"] = "salt-for-svg-generation"
    output_dir = Path(__file__).parent
    project_name = output_dir.name

    for variant in selected:
        fig, axs = plt.subplot_mosaic(
            [["main"]],
            figsize=(32 * cm, 18 * cm),
            layout="constrained",
        )
        ax = axs["main"]

        # Call plotting function for the variant, which should be on this file
        # with name 'plot_variant_name'
        globals()[f"plot_{variant.replace('-', '_')}"](ax)

        stem = output_dir / f"{project_name}-{variant}"
        png = save_chart(fig, stem)
        if not args.no_open:
            open_file(png)
        plt.close(fig)
