#! /usr/bin/env -S uv run python

# --- SECTION NAME: imports ---
import csv
import io
from collections import defaultdict
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.axes import Axes

# --- SECTION NAME: constants ---

EDUCACION = "Educación"
SALUD = "Salud"
SEG_SOCIAL = "Seguridad Social"
SEG_DEFENSA = "Seguridad y Defensa"
INFRAESTRUC = "Infraestructura"
DEUDA = "Deuda"
ADMINISTRACION = "Administración"
OTROS = "Otros"

SECTORS = [
    EDUCACION,
    SALUD,
    SEG_SOCIAL,
    SEG_DEFENSA,
    INFRAESTRUC,
    DEUDA,
    ADMINISTRACION,
    OTROS,
]

SECTOR_COLORS = {
    EDUCACION: "#1E88E5",
    SALUD: "#43A047",
    SEG_SOCIAL: "#FB8C00",
    SEG_DEFENSA: "#E53935",
    INFRAESTRUC: "#8E24AA",
    DEUDA: "#546E7A",
    ADMINISTRACION: "#795548",
    OTROS: "#BDBDBD",
}

# --- Sector mapping: 1961-2010 incisos

INCISO_SECTOR = {
    "01 - PODER LEGISLATIVO": ADMINISTRACION,
    "02 - PRESIDENCIA DE LA REPUBLICA": ADMINISTRACION,
    "03 - MINISTERIO DE DEFENSA NACIONAL": SEG_DEFENSA,
    "04 - MINISTERIO DEL INTERIOR": SEG_DEFENSA,
    "05 - MINISTERIO DE ECONOMIA Y FINANZAS": ADMINISTRACION,
    "06 - MINISTERIO DE RELACIONES EXTERIORES": ADMINISTRACION,
    "07 - MINISTERIO DE GANADERIA, AGRICULTURA Y PESCA": OTROS,
    "08 - MINISTERIO DE INDUSTRIA, ENERGIA Y MINERIA": OTROS,
    "09 - MINISTERIO DE TURISMO Y DEPORTE (*1)": OTROS,
    "10 - MINISTERIO DE TRANSPORTE Y OBRAS PUBLICAS": INFRAESTRUC,
    "11 - MINISTERIO DE EDUCACION Y CULTURA (*2)": EDUCACION,
    "12 - MINISTERIO DE SALUD PUBLICA": SALUD,
    "13 - MINISTERIO DE TRABAJO Y SEGURIDAD SOCIAL": SEG_SOCIAL,
    "14 - MINISTERIO DE VIVIENDA, ORDENAMIENTO TERRITORIAL Y MEDIO AMBIENTE (*3)": INFRAESTRUC,
    "15 - MINISTERIO DE DEPORTE Y JUVENTUD (2001-2004)": OTROS,
    "15 - MINISTERIO DE DESARROLLO SOCIAL (desde 2005)": SEG_SOCIAL,
    "16 - PODER JUDICIAL (*5)": ADMINISTRACION,
    "17 - TRIBUNAL DE CUENTAS": ADMINISTRACION,
    "18 - CORTE ELECTORAL": ADMINISTRACION,
    "19 - TRIBUNAL CONTENCIOSO ADMINISTRATIVO": ADMINISTRACION,
    "20 - DESEMBOLSOS FINANCIEROS DEL ESTADO (*4)": DEUDA,
    "21 - SUBSIDIOS Y SUBVENCIONES (*8)": OTROS,
    "22 - TRANSFERENCIAS FINANCIERAS SECTOR SEGURIDAD SOCIAL": SEG_SOCIAL,
    "23 - PARTIDAS A REAPLICAR": OTROS,
    "24 - DIVERSOS CREDITOS (*9)": OTROS,
    "25 - ADMINISTRACION NACIONAL EDUCACION PUBLICA": EDUCACION,
    "26 - UNIVERSIDAD DE LA REPUBLICA (*6)": EDUCACION,
    "27 - INSTITUTO DEL NI¥O Y ADOLESCENTE DEL URUGUAY (*7)": SEG_SOCIAL,
    "29 - ADMINISTRACIàN DE SERVICIOS DE SALUD DEL ESTADO": SALUD,
}


def inciso_to_sector(name: str) -> str:
    return INCISO_SECTOR.get(name.strip(), OTROS)


# --- Sector mapping: 2011-2025 AP_nombre

AP_SECTOR = {
    "EDUCACIÓN": EDUCACION,
    "SALUD": SALUD,
    "SEGURIDAD SOCIAL": SEG_SOCIAL,
    "PROTECCIÓN SOCIAL": SEG_SOCIAL,
    "PROTECCIÓN Y SEGURIDAD SOCIAL": SEG_SOCIAL,
    "TRABAJO Y EMPLEO": SEG_SOCIAL,
    "SEGURIDAD PÚBLICA": SEG_DEFENSA,
    "DEFENSA NACIONAL": SEG_DEFENSA,
    "INFRAESTRUCTURA, TRANSPORTE Y COMUNICACIONES": INFRAESTRUC,
    "VIVIENDA": INFRAESTRUC,
    "TRANSFERENCIAS A GOBIERNOS SUBNACIONALES": INFRAESTRUC,
    "ADMINISTRACIÓN FINANCIERA": DEUDA,
    "SERVICIOS PÚBLICOS GENERALES": ADMINISTRACION,
    "ASUNTOS LEGISLATIVOS": ADMINISTRACION,
    "ADMINISTRACIÓN DE JUSTICIA": ADMINISTRACION,
    "REGISTROS E INFORMACIÓN OFICIAL": ADMINISTRACION,
    "REGULACION, CONTROL Y TRANSPARENCIA": ADMINISTRACION,
    "DESARROLLO PRODUCTIVO": OTROS,
    "CULTURA Y DEPORTE": OTROS,
    "MEDIO AMBIENTE Y RECURSOS NATURALES": OTROS,
    "CIENCIA, TECNOLOGÍA E INNOVACIÓN": OTROS,
    "ENERGÍA": OTROS,
}


def ap_to_sector(ap: str, org: str) -> str:
    # Pre-2020, interest payments were buried inside SERVICIOS PÚBLICOS GENERALES
    if ap == "SERVICIOS PÚBLICOS GENERALES" and org == "Intereses y otros Gastos de la Deuda":
        return DEUDA
    return AP_SECTOR.get(ap, OTROS)


# -- Political Terms

PN = "PN"
PC = "PC"
FA = "FA"

TERMS = [
    ("Colegiado", PN, 1961),
    ("Pacheco", PC, 1967),
    ("B.", PC, 1972),
    ("Dictadura", None, 1973),
    ("Sanguinetti I", PC, 1985),
    ("Lacalle", PN, 1990),
    ("Sanguinetti II", PC, 1995),
    ("Batlle", PC, 2000),
    ("Vázquez I", FA, 2005),
    ("Mujica", FA, 2010),
    ("Vázquez II", FA, 2015),
    ("Lacalle Pou", PN, 2020),
    ("Orsi", FA, 2025),
]
TERMS_NO_LABEL = {"Dictadura"}
PLOT_END = 2030

PARTY_COLORS = {PN: "#5DADE2", PC: "#BA0200", FA: "#013197"}
MARCH_FRAC = 60 / 365

# --- SECTION NAME: data loading ---


def parse_opp_1961_number(s: str) -> float:
    s = s.strip()
    if not s:
        return 0.0
    # European format: period = thousands sep, comma = decimal sep
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


data_dir = Path(__file__).parent / "data"


def load_1961_2010() -> dict[int, dict[str, float]]:
    text = (data_dir / "opp_1961_2010.csv").read_bytes().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text), delimiter=";")

    totals: defaultdict[int, defaultdict[str, float]] = defaultdict(lambda: defaultdict(float))
    udelar_row: dict[str, str] | None = None
    for row in reader:
        if row["INCISO"].strip().startswith("26 -"):
            udelar_row = row
        sector = inciso_to_sector(row["INCISO"])
        for yr_str, val_str in list(row.items())[1:]:
            totals[int(yr_str)][sector] += (
                parse_opp_1961_number(val_str) * 1000
            )  # file is in thousands of pesos

    # UdelaR data is blank in the source file for 1968-1972; it was likely absorbed
    # into inciso 20 (Desembolsos Financieros, mapped to DEUDA), which balloons by
    # roughly the right magnitude in those exact years. Reclassify by interpolating
    # UdelaR between 1967 and 1973 and moving that amount from DEUDA to EDUCACION.
    if udelar_row is not None:
        v_1967 = parse_opp_1961_number(udelar_row["1967"]) * 1000
        v_1973 = parse_opp_1961_number(udelar_row["1973"]) * 1000
        for i, yr in enumerate(range(1968, 1973), start=1):
            interp = v_1967 + (v_1973 - v_1967) * i / 6
            totals[yr][EDUCACION] += interp
            totals[yr][DEUDA] -= interp

    # {year: {sector: total}}
    return {yr: dict(sectors) for yr, sectors in totals.items()}


def load_2011_2025() -> dict[int, dict[str, float]]:
    text = (data_dir / "opp_2011_2025.csv").read_bytes().decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))

    totals: defaultdict[int, defaultdict[str, float]] = defaultdict(lambda: defaultdict(float))
    for row in reader:
        yr = int(row["AÑO"])
        sector = ap_to_sector(row["AP_nombre"], row["Organismo_nombre"])
        val = float(row["Ejecutado"].replace(",", "."))
        totals[yr][sector] += val

    # {year: {sector: total}}
    return {yr: dict(sectors) for yr, sectors in totals.items()}


def load_wb_gdp_const() -> dict[int, float]:
    result = {}
    with open(data_dir / "wb_gdp_const_usd.csv") as f:
        for row in csv.DictReader(f):
            result[int(row["year"])] = float(row["gdp_const_usd"])
    # {year: usd}
    return result


def load_wb_gdp_nominal() -> dict[int, float]:
    result = {}
    with open(data_dir / "wb_gdp_nominal_pesos.csv") as f:
        for row in csv.DictReader(f):
            result[int(row["year"])] = float(row["gdp_nominal_pesos"])
    # {year: value}
    return result


opp_1961_2010 = load_1961_2010()
opp_2011_2025 = load_2011_2025()
gdp_real_usd = load_wb_gdp_const()
gdp_real_usd_billions = {yr: val / 1e9 for yr, val in gdp_real_usd.items()}
gdp_nominal_pesos = load_wb_gdp_nominal()

# --- SECTION NAME: data processing ---

# merge budget
budget = {}
for yr, sectors in opp_1961_2010.items():
    budget[yr] = dict(sectors)
for yr, sectors in opp_2011_2025.items():
    budget[yr] = dict(sectors)

# 2025 OPP data is partial (budget appropriation, not full execution)
del budget[2025]

years_sorted = sorted(budget)

# --- % of budget per sector per year

# {year: {sector: percentage}}
pct_budget = {}
for yr in years_sorted:
    row = budget[yr]
    total = sum(row.values())
    if total == 0:
        continue
    pct_budget[yr] = {s: row.get(s, 0) / total * 100 for s in SECTORS}

# --- Budget by sector in real USD (constant 2015)

# {year: {sector: real_usd_billions}}
budget_real_usd_billions = {}

# {year: percentage_of_gdp}
budget_pct_gdp = {}

for yr in years_sorted:
    budget_pesos = sum(budget[yr].values())
    budget_pct_gdp[yr] = budget_pesos / gdp_nominal_pesos[yr] * 100

    budget_real_usd_billions_total = budget_pct_gdp[yr] / 100 * gdp_real_usd_billions[yr]
    budget_real_usd_billions[yr] = {
        s: pct_budget[yr][s] / 100 * budget_real_usd_billions_total for s in SECTORS
    }

# Extend GDP with IMF 2026 forecast
IMF_2026_GROWTH = 0.022
gdp_real_usd_billions[2026] = gdp_real_usd_billions[2025] * (1 + IMF_2026_GROWTH)

# --- SECTION NAME: plot ---

cm = 1 / 2.54
plt.style.use("ggplot")
plt.rcParams["svg.hashsalt"] = "salt-for-svg-generation"

FOOTNOTE = (
    "Fuente: OPP - Ejecución Presupuestal 1961-2010, Crédito Presupuestal 2011-2024."
    " World Bank NY.GDP.MKTP.KD (PBI constante 2015), NY.GDP.MKTP.CN (PBI corriente)."
)


def draw_annotations(ax: Axes) -> None:
    for _, _, year in TERMS[1:]:
        ax.axvline(
            year + MARCH_FRAC,
            linestyle="--",
            linewidth=0.4,
            color="#4d4d4d",
            alpha=0.6,
            zorder=3,
        )


def _add_term_labels(ax: Axes) -> None:
    for i, (label, party, year) in enumerate(TERMS):
        if label in TERMS_NO_LABEL:
            continue
        next_year = TERMS[i + 1][2] if i + 1 < len(TERMS) else PLOT_END
        mid = (year + next_year) / 2 + MARCH_FRAC
        if mid < PLOT_START:
            continue
        ylim = ax.get_ylim()
        y = ylim[1] - (ylim[1] - ylim[0]) * 0.05
        ax.text(
            mid,
            y,
            label,
            ha="center",
            va="top",
            fontsize=7.5,
            color=PARTY_COLORS[party],
            fontweight="bold",
        )


PLOT_START = 1973


def _setup_x_axis(ax: Axes) -> None:
    ax.set_xlim(PLOT_START, PLOT_END)
    ax.set_xticks(range(1975, PLOT_END + 1, 5))
    ax.set_xticks(range(PLOT_START, PLOT_END + 1, 1), minor=True)
    ax.grid(which="major", axis="x", linewidth=0.5, alpha=0.4)
    ax.grid(which="minor", axis="x", linewidth=0.2, alpha=0.2)
    ax.set_xlabel("Año")


def stacked_area(
    ax: Axes,
    year_val_dict: dict[int, dict[str, float]],
    ylabel: str,
    ylim: float,
    tick_step: int = 10,
    minor_step: int = 5,
) -> None:
    yrs = sorted(year_val_dict)
    xs = list(yrs)
    bottom = [0.0] * len(xs)
    for sector in SECTORS:
        ys = [year_val_dict[y].get(sector, 0) for y in yrs]
        top = [b + y for b, y in zip(bottom, ys)]
        ax.fill_between(
            xs,
            bottom,
            top,
            color=SECTOR_COLORS[sector],
            alpha=0.85,
            label=sector,
            zorder=2,
        )
        bottom = top
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, ylim)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(tick_step))
    ax.yaxis.set_minor_locator(mticker.MultipleLocator(minor_step))
    ax.grid(which="major", axis="y", linewidth=0.5, alpha=0.4, zorder=0)


def plot_stacked_pct(ax: Axes) -> None:
    stacked_area(ax, pct_budget, "Composición del presupuesto (%)", 100)
    ax.set_title(
        "Uruguay - Composición del presupuesto nacional por área (1973–2024)",
        fontsize=12,
        fontweight="bold",
    )
    draw_annotations(ax)
    _add_term_labels(ax)
    _setup_x_axis(ax)
    handles = [mpatches.Patch(color=SECTOR_COLORS[s], label=s) for s in SECTORS]
    ax.legend(
        handles=handles,
        loc="center right",
        fontsize=8.5,
        frameon=True,
        framealpha=0.6,
        ncol=2,
    )
    ax.figure.text(0.5, -0.03, FOOTNOTE, ha="center", fontsize=7.5, alpha=0.7)


def plot_real_usd(ax: Axes) -> None:
    stacked_area(
        ax,
        budget_real_usd_billions,
        "Miles de millones USD (base 2015)",
        75,
        tick_step=10,
        minor_step=5,
    )
    ax.set_title(
        "Uruguay - Presupuesto nacional vs. PBI en USD ajustados por inflación (1973–2024)",
        fontsize=12,
        fontweight="bold",
    )
    gdp_yrs_actual = sorted(y for y in gdp_real_usd_billions if y < 2026)
    gdp_yrs_forecast = [2025, 2026]
    ax.plot(
        gdp_yrs_actual,
        [gdp_real_usd_billions[y] for y in gdp_yrs_actual],
        color="black",
        linewidth=2,
        zorder=5,
    )
    ax.plot(
        gdp_yrs_forecast,
        [gdp_real_usd_billions[y] for y in gdp_yrs_forecast],
        color="black",
        linewidth=2,
        linestyle="--",
        zorder=5,
    )
    ax.text(
        max(gdp_real_usd_billions) + 0.3,
        gdp_real_usd_billions[max(gdp_real_usd_billions)],
        "PBI",
        va="center",
        fontsize=8,
        color="black",
    )
    for yr in [*range(1975, 2025, 5), 2024]:
        if yr not in budget_real_usd_billions or yr not in budget_pct_gdp:
            continue
        budget_top = sum(budget_real_usd_billions[yr].values())
        ax.text(
            yr,
            budget_top + 0.5,
            f"{budget_pct_gdp[yr]:.0f}%",
            ha="center",
            va="bottom",
            fontsize=9,
            color="#333333",
        )
    draw_annotations(ax)
    _add_term_labels(ax)
    _setup_x_axis(ax)
    handles = [mpatches.Patch(color=SECTOR_COLORS[s], label=s) for s in SECTORS]
    ax.legend(
        handles=handles,
        loc="upper left",
        bbox_to_anchor=(0, 0.92),
        fontsize=8.5,
        frameon=True,
        framealpha=0.6,
        ncol=1,
    )
    ax.figure.text(0.5, -0.03, FOOTNOTE, ha="center", fontsize=7.5, alpha=0.7)


def plot_lines(ax: Axes) -> None:
    yrs = sorted(pct_budget)
    xs = list(yrs)
    for sector in SECTORS:
        ys = [pct_budget[y].get(sector, 0) for y in yrs]
        ax.plot(xs, ys, color=SECTOR_COLORS[sector], linewidth=1.8, label=sector, zorder=2)
    ax.set_ylabel("% del presupuesto")
    ax.set_ylim(0, 50)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(10))
    ax.yaxis.set_minor_locator(mticker.MultipleLocator(5))
    ax.grid(which="major", axis="y", linewidth=0.5, alpha=0.4, zorder=0)
    ax.set_title(
        "Uruguay - Composición del presupuesto nacional por área (1973–2024)",
        fontsize=12,
        fontweight="bold",
    )
    draw_annotations(ax)
    _add_term_labels(ax)
    _setup_x_axis(ax)
    handles = [mpatches.Patch(color=SECTOR_COLORS[s], label=s) for s in SECTORS]
    ax.legend(handles=handles, loc="upper left", fontsize=8.5, frameon=True, ncol=1)
    ax.figure.text(0.5, -0.03, FOOTNOTE, ha="center", fontsize=7.5, alpha=0.7)


# --- SECTION NAME: metadata ---
VARIANTS = ["stacked-pct", "real-usd", "lines"]

if __name__ == "__main__":
    from shared.utils import generate_notebook, get_cli_args, open_file, save_chart

    args = get_cli_args(VARIANTS)
    if args.notebook:
        generate_notebook("budget")
        raise SystemExit(0)
    selected = args.chart
    output_dir = Path(__file__).parent
    project_name = output_dir.name

    for variant in selected:
        fig, ax = plt.subplots(figsize=(36 * cm, 16 * cm), layout="constrained")
        globals()[f"plot_{variant.replace('-', '_')}"](ax)

        stem = output_dir / f"{project_name}-{variant}"
        png = save_chart(fig, stem)
        if args.interactive:
            plt.show()
        elif not args.no_open:
            open_file(png)
        plt.close(fig)
