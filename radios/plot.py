#! /usr/bin/env -S uv run python

# --- SECTION NAME: imports ---
import csv
from collections import defaultdict
from enum import StrEnum
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

# --- SECTION NAME: constants ---


class Station(StrEnum):
    MONTE_CARLO = "Monte Carlo"
    SARANDI = "Sarandí"
    SPORT_890 = "Sport 890"
    CARVE = "Carve"
    CARVE_DEPORTIVA = "Carve Deportiva"
    EL_ESPECTADOR = "El Espectador"
    EL_ESPECTADOR_FM = "El Espectador (repetidora FM)"
    ORIENTAL = "Radio Oriental"
    ORIENTAL_AGROPECUARIA = "Radio Oriental Agropecuaria"
    CLARIN = "Clarín"
    UNIVERSAL = "Universal"
    CONTINENTE = "Continente"
    CENTENARIO = "Centenario"
    RADIO_URUGUAY = "Radio Uruguay"
    RADIO_URUGUAY_FM = "Radio Uruguay (repetidora FM)"
    RADIOMUNDO = "Radiomundo"
    RURAL = "Rural"
    NACIONAL = "Nacional"
    AIRE = "Aire"
    INOLVIDABLE = "Inolvidable"
    DEL_SOL = "Del Sol"
    AZUL = "Azul"
    DISNEY = "Disney"
    FM_LIKE = "FM Like"
    METROPOLIS = "Metrópolis"
    OCEANO = "Océano"
    DEL_PLATA = "Del Plata"
    FM_HIT = "FM Hit"
    RADIO_FUTURA = "Radio Futura"
    GALAXIA = "Galaxia"
    RADIO_CERO = "Radio Cero"
    COSQUIN_ROCK_RADIO = "Cosquín Rock Radio"
    LA_LEY = "La Ley"
    UNI_RADIO = "Uni Radio"
    LATINA = "Latina"
    TOTAL = "Sarandí (repetidora FM)"
    BABEL = "Babel"
    M24 = "M24"
    LA_DIARIA = "La Diaria Radio"
    VOZ_DE_LA_ESPERANZA = "Voz de la Esperanza"
    URBANA = "Urbana"
    EMISORA_DEL_SUR_FM = "Emisora Del Sur (repetidora FM)"
    ALFA = "Alfa"
    DIAMANTE = "Diamante"
    LA_COSTA = "La Costa"
    AM_LIBRE = "AM Libre"
    CLASICA = "Clásica"
    AMERICA = "América"
    CULTURA = 'Cultura (Prev. "Emisora del Sur")'
    FENIX = "Fénix"
    CIUDAD_DE_MDEO = "Ciudad de Mdeo"
    INDEPENDENCIA = "Independencia"
    IMPARCIAL = "Imparcial"
    CRISTAL = "Cristal"
    BOLICHE_RADIO = "Boliche Radio"


INACTIVE_STATIONS: set[Station] = {
    Station.LATINA,
    Station.URBANA,
    Station.EMISORA_DEL_SUR_FM,
    Station.AM_LIBRE,
    Station.CIUDAD_DE_MDEO,
    Station.INDEPENDENCIA,
    Station.IMPARCIAL,
    Station.M24,
    Station.VOZ_DE_LA_ESPERANZA,
    Station.RADIO_CERO,
    Station.ORIENTAL,
}

STATION_FREQ: dict[Station, int | float] = {
    Station.LA_COSTA: 88.3,
    Station.BOLICHE_RADIO: 89.7,
    Station.FM_HIT: 90.3,
    Station.RADIO_FUTURA: 91.1,
    Station.FM_LIKE: 91.9,
    Station.EL_ESPECTADOR_FM: 92.5,
    Station.INOLVIDABLE: 93.1,
    Station.OCEANO: 93.9,
    Station.RADIO_URUGUAY_FM: 94.7,
    Station.DEL_PLATA: 95.5,
    Station.ALFA: 96.3,
    Station.BABEL: 97.1,
    Station.LA_DIARIA: 97.9,
    Station.DIAMANTE: 98.7,
    Station.DEL_SOL: 99.5,
    Station.AIRE: 100.3,
    Station.AZUL: 101.9,
    Station.TOTAL: 102.9,
    Station.DISNEY: 103.7,
    Station.COSQUIN_ROCK_RADIO: 104.3,
    Station.METROPOLIS: 104.9,
    Station.GALAXIA: 105.9,
    Station.LA_LEY: 106.7,
    Station.UNI_RADIO: 107.7,
    Station.CLARIN: 580,
    Station.RURAL: 610,
    Station.CLASICA: 650,
    Station.SARANDI: 690,
    Station.CONTINENTE: 730,
    Station.ORIENTAL_AGROPECUARIA: 770,
    Station.EL_ESPECTADOR: 810,
    Station.CARVE: 850,
    Station.SPORT_890: 890,
    Station.MONTE_CARLO: 930,
    Station.UNIVERSAL: 970,
    Station.CARVE_DEPORTIVA: 1010,
    Station.RADIO_URUGUAY: 1050,
    Station.NACIONAL: 1130,
    Station.RADIOMUNDO: 1170,
    Station.CENTENARIO: 1250,
    Station.CULTURA: 1290,
    Station.FENIX: 1330,
    Station.AMERICA: 1450,
}

STATION_ALIASES: dict[str, Station] = {
    "CX20 MONTECARLO": Station.MONTE_CARLO,
    "930 - CX20 MONTECARLO": Station.MONTE_CARLO,
    "CX8 SARANDI": Station.SARANDI,
    "690 - CX8 SARANDI": Station.SARANDI,
    "CX18 SPORT 890": Station.SPORT_890,
    "890 - CX18 SPORT 890": Station.SPORT_890,
    "CX16 CARVE": Station.CARVE,
    "850 - CX16 CARVE": Station.CARVE,
    "CX14 EL ESPECTADOR": Station.EL_ESPECTADOR,
    "810 - CX14 EL ESPECTADOR": Station.EL_ESPECTADOR,
    "CX12 ORIENTAL": Station.ORIENTAL,
    "770 - CX12 ORIENTAL": Station.ORIENTAL,
    "CX58 CLARIN": Station.CLARIN,
    "580 - CX58 CLARIN": Station.CLARIN,
    "CX22 UNIVERSAL": Station.UNIVERSAL,
    "970 - CX22 UNIVERSAL": Station.UNIVERSAL,
    "CX24 RADIO 1010 AM": Station.CARVE_DEPORTIVA,
    "1010 - CX24 LA 1010 AM": Station.CARVE_DEPORTIVA,
    "CX10 CONTINENTE": Station.CONTINENTE,
    "730 - CX10 CONTINENTE": Station.CONTINENTE,
    "CX36 CENTENARIO": Station.CENTENARIO,
    "1250 - CX36 CENTENARIO": Station.CENTENARIO,
    "CX26 RADIO URUGUAY": Station.RADIO_URUGUAY,
    "1050 - CX26 RADIO URUGUAY": Station.RADIO_URUGUAY,
    "CX32 RADIOMUNDO": Station.RADIOMUNDO,
    "1170 - CX32 RADIOMUNDO": Station.RADIOMUNDO,
    "CX32 MUNDO": Station.RADIOMUNDO,
    "CX4 RURAL": Station.RURAL,
    "610 - CX4 RURAL": Station.RURAL,
    "1130 - CX30 NACIONAL": Station.NACIONAL,
    "CX30 NACIONAL": Station.NACIONAL,
    "100.3 AIRE": Station.AIRE,
    "100.3 - AIRE": Station.AIRE,
    "93.1 INOLVIDABLE": Station.INOLVIDABLE,
    "93.1 - INOLVIDABLE": Station.INOLVIDABLE,
    "99.5 DEL SOL": Station.DEL_SOL,
    "99.5 - DEL SOL": Station.DEL_SOL,
    "101.9 AZUL": Station.AZUL,
    "101.9 - AZUL": Station.AZUL,
    "91.9 DISNEY": Station.DISNEY,
    "91.9 - FM LIKE": Station.FM_LIKE,
    "103.7 LATINA": Station.LATINA,
    "103.7 - RADIO DISNEY": Station.DISNEY,
    "91.9 FM LIKE": Station.FM_LIKE,
    "104.9 METROPOLIS": Station.METROPOLIS,
    "104.9 - METROPOLIS": Station.METROPOLIS,
    "93.9 OCEANO": Station.OCEANO,
    "93.9 - OCEANO": Station.OCEANO,
    "95.5 DEL PLATA": Station.DEL_PLATA,
    "95.5 - DEL PLATA": Station.DEL_PLATA,
    "90.3 OLDIES": Station.FM_HIT,
    "90.3 - FM HIT (OLDIES)": Station.FM_HIT,
    "90.3 - FM HIT": Station.FM_HIT,
    "91.1 RADIOFUTURA": Station.RADIO_FUTURA,
    "91.1 - RADIO FUTURA": Station.RADIO_FUTURA,
    "105.9 GALAXIA": Station.GALAXIA,
    "105.9 - GALAXIA": Station.GALAXIA,
    "104.3 RADIOCERO": Station.RADIO_CERO,
    "104.3 - RADIO CERO": Station.RADIO_CERO,
    "106.7 LA LEY": Station.LA_LEY,
    "106.7 - LA LEY": Station.LA_LEY,
    "102.9 TOTAL": Station.TOTAL,
    "102.9 - TOTAL": Station.TOTAL,
    "97.1 BABEL": Station.BABEL,
    "97.1 - BABEL": Station.BABEL,
    "97.9 M24": Station.M24,
    "97.9 - M24": Station.M24,
    "101.3 VOZ DE LA ESPERANZA": Station.VOZ_DE_LA_ESPERANZA,
    "101.3 - VOZ DE LA ESPERANZA": Station.VOZ_DE_LA_ESPERANZA,
    "92.5 CONCIERTO URBANA": Station.URBANA,
    "92.5 - URBANA FM": Station.URBANA,
    "92.5 - LATINA": Station.LATINA,
    "94.7 E. DEL SUR": Station.EMISORA_DEL_SUR_FM,
    "94.7 - DEL SUR": Station.EMISORA_DEL_SUR_FM,
    "96.3 ALFA": Station.ALFA,
    "96.3 - ALFA": Station.ALFA,
    "98.7 DIAMANTE": Station.DIAMANTE,
    "98.7 - DIAMANTE": Station.DIAMANTE,
    "88.3 LACOSTA": Station.LA_COSTA,
    "88.3 - LACOSTA": Station.LA_COSTA,
    "1410 - CX44 LA 1410": Station.AM_LIBRE,
    "1410 - CX44 LA R / LIBRE": Station.AM_LIBRE,
    "CX44 AM LIBRE": Station.AM_LIBRE,
    "650 - CX6 CLASICA": Station.CLASICA,
    "650 - CX6 CLÁSICA": Station.CLASICA,
    "CX6 CLÁSICA": Station.CLASICA,
    "1450 - CX46 AMERICA": Station.AMERICA,
    "CX46 AMERICA": Station.AMERICA,
    "1290 - CX38 EMISORA DEL SUR": Station.CULTURA,
    "1290 - CX38 CULTURA / DEL SUR": Station.CULTURA,
    "CX38 EMISORA DEL SUR": Station.CULTURA,
    "1330 - CX40 FENIX": Station.FENIX,
    "CX40 FENIX": Station.FENIX,
    "1370 - CX42 CIUDAD DE MDEO.": Station.CIUDAD_DE_MDEO,
    "CX42 C. DE MDEO.": Station.CIUDAD_DE_MDEO,
    "1530 - CX50 INDEPENDENCIA": Station.INDEPENDENCIA,
    "1090 - CX28 IMPARCIAL": Station.IMPARCIAL,
    "CX28 IMPARCIAL": Station.IMPARCIAL,
    "CX48 CRISTAL": Station.CRISTAL,
}

# Semi-official Factum data for 2024-2025
FACTUM_DATA = {
    "AM": {
        Station.MONTE_CARLO: {2024: 1.16, 2025: 1.09},
        Station.SARANDI: {2024: 0.86, 2025: 0.84},
        Station.EL_ESPECTADOR: {2024: 0.50},
        Station.SPORT_890: {2024: 0.46, 2025: 0.36},
        Station.ORIENTAL: {2024: 0.10},
        Station.UNIVERSAL: {2024: 0.20},
        Station.RADIO_URUGUAY: {2024: 0.17},
        Station.CARVE_DEPORTIVA: {2024: 0.16},
    },
    "FM": {
        Station.INOLVIDABLE: {2024: 2.2, 2025: 2.60},
        Station.AIRE: {2024: 1.92, 2025: 2.03},
        Station.DEL_SOL: {2024: 1.53},
        Station.DISNEY: {2024: 1.29, 2025: 1.51},
        Station.BABEL: {2024: 0.26},
    },
}


# --- SECTION NAME: data loading ---


def normalize_name(name):
    name = name.strip()
    if name in STATION_ALIASES:
        return STATION_ALIASES[name]
    # Try partial match
    for k, v in STATION_ALIASES.items():
        if name.startswith(k) or k.startswith(name):
            return v
    return name


def load_ratings():
    data = defaultdict(lambda: defaultdict(dict))
    with open(Path(__file__).parent / "data" / "station_ratings.csv") as f:
        for row in csv.DictReader(f):
            name = normalize_name(row["station"])
            band = row["band"]
            year = int(row["year"])
            rating = float(row["avg_rating"])
            data[band][year][name] = rating
    return data


data = load_ratings()

# CX50 Radio Independencia (AM 1530) has been defunct since ~2007. The 2022
# datapoint (0.0351) in the Buró spreadsheet is almost certainly erroneous.
for band in list(data):
    for year in list(data[band]):
        data[band][year].pop(Station.INDEPENDENCIA, None)

# --- SECTION NAME: data processing ---


def select_stations(data, band, min_years=3):
    """Select stations present in at least min_years."""
    counts = defaultdict(int)
    for year, stations in data[band].items():
        for name in stations:
            counts[name] += 1
    return sorted(
        [s for s, c in counts.items() if c >= min_years],
        key=lambda s: -max(data[band][y].get(s, 0) for y in data[band]),
    )


def build_series(data, band, stations, all_years):
    series = {}
    for st in stations:
        years = []
        vals = []
        for y in all_years:
            if y in data[band] and st in data[band][y]:
                years.append(y)
                vals.append(data[band][y][st])
        series[st] = (years, vals)
    return series


all_years = sorted(set(data["AM"]) | set(data["FM"]) | {2024, 2025})

am_stations = select_stations(data, "AM", min_years=1)[:]
fm_stations = select_stations(data, "FM", min_years=1)[:]

am_series = build_series(data, "AM", am_stations, all_years)
fm_series = build_series(data, "FM", fm_stations, all_years)

# --- SECTION NAME: plot ---


def plot_band(ax: Axes, series, factum_data, title, all_years):
    # Era background shading
    ax.axvspan(2016.5, 2022.5, alpha=0.2, color="gray", zorder=0)
    ax.axvspan(2023.5, 2026.5, alpha=0.1, color="lightcoral", zorder=0)

    colors = [plt.cm.tab20(i) for i in range(20)] + [plt.cm.tab20b(i) for i in range(20)]
    st_color = {}

    for i, (st, (years, vals)) in enumerate(series.items()):
        color = colors[i % len(colors)]
        st_color[st] = color
        freq = STATION_FREQ.get(st)
        if freq and st not in INACTIVE_STATIONS:
            label = f"{st} ({freq})"
        else:
            label = f"{st} (N/A)" if st in INACTIVE_STATIONS else st
        ax.plot(years, vals, marker="o", label=label, color=color, linewidth=1.5, markersize=4)

    # Interpolate from last Buró data point to Factum data points
    for st, vals in factum_data.items():
        if st not in series:
            continue
        sy, sv = series[st]
        fy = sorted(vals)
        fv = [vals[y] for y in fy]
        # Dashed connector from last Buró to first Factum
        ax.plot(
            [sy[-1], fy[0]],
            [sv[-1], fv[0]],
            linestyle="--",
            color=st_color[st],
            linewidth=1.5,
        )
        # Solid line among Factum data points
        if len(fy) > 1:
            ax.plot(fy, fv, linestyle="-", color=st_color[st], linewidth=1.5)
        ax.scatter(fy, fv, marker="s", color=st_color[st], s=16)

    # Legend
    proxy = Line2D([], [], marker="s", linestyle="--", color="gray", linewidth=1.5)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        handles + [proxy],
        labels + ["Factum 2024–2025"],
        fontsize=7.5,
        ncol=2,
        loc="upper left",
    )

    # Expand y-axis by 20% for header headroom
    ymin, ymax = ax.get_ylim()
    ax.set_ylim(ymin, ymax * 1.2)

    # Era headers
    ax.text(
        2019.5,
        0.92,
        "Buró de Radios",
        ha="center",
        va="bottom",
        fontsize=9,
        color="gray",
        fontweight="bold",
        transform=ax.get_xaxis_transform(),
    )
    ax.text(
        2025,
        0.92,
        "Factum\n(Cambio de metodologia, datos privados)",
        ha="center",
        va="bottom",
        fontsize=9,
        color="lightcoral",
        fontweight="bold",
        transform=ax.get_xaxis_transform(),
    )

    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_ylabel("Rating promedio (L–D, 00–24)", fontsize=8)
    ax.set_xlabel("Año", fontsize=8)
    ax.set_xlim(2016.5, 2026.5)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
    ax.tick_params(axis="x", labelsize=7)
    ax.tick_params(axis="y", labelsize=7)


def plot_am(ax: Axes) -> None:
    plot_band(ax, am_series, FACTUM_DATA["AM"], "AM", all_years)


def plot_fm(ax: Axes) -> None:
    plot_band(ax, fm_series, FACTUM_DATA["FM"], "FM", all_years)


def plot_fm_freq(ax: Axes) -> None:
    fm_stations = sorted(
        (freq, station)
        for station, freq in STATION_FREQ.items()
        if isinstance(freq, float) and station not in INACTIVE_STATIONS
    )

    # Merge Factum data into ratings for average computation
    for st, years in FACTUM_DATA["FM"].items():
        for year, rating in years.items():
            data["FM"][year][st] = rating

    # Compute average rating per station
    station_ratings: dict[Station, list[float]] = {}
    all_ratings: list[float] = []
    for year_data in data["FM"].values():
        for st, rating in year_data.items():
            all_ratings.append(rating)
            station_ratings.setdefault(st, []).append(rating)

    station_avg = {st: sum(v) / len(v) for st, v in station_ratings.items()}
    global_mean = sum(all_ratings) / len(all_ratings)

    # Manual label offsets to resolve collisions
    label_dy: dict[Station, float] = {
        Station.EL_ESPECTADOR_FM: 0.1,
        Station.METROPOLIS: 0.1,
    }

    for freq, station in fm_stations:
        has = station in station_avg
        if has:
            y = station_avg[station]
            lw = 1 + y * 3
            sz = 10 + y * 60
            color = "#2196F3"
            ax.plot(
                [freq, freq], [0, y], color=color, linewidth=lw, alpha=0.7, solid_capstyle="round"
            )
            ax.scatter(freq, y, color=color, s=sz, zorder=5)
        else:
            y = global_mean
            lw = 1 + y * 3
            sz = 10 + y * 60
            color = "#999999"
            ax.plot(
                [freq, freq],
                [0, y],
                color=color,
                linewidth=lw,
                linestyle="dotted",
                solid_capstyle="round",
            )
            ax.scatter(freq, y, color=color, s=sz, zorder=5)

        fs = 5.5 + y * 1.8
        ax.text(
            freq,
            y + 0.06 + label_dy.get(station, 0),
            str(station).replace(" ", "\n"),
            ha="center",
            va="bottom",
            fontsize=fs,
            color="black",
            rotation=0,
        )

    ax.set_xlim(86, 109)
    y_max = max(station_avg.values())
    ax.set_ylim(0, y_max * 1.15)
    ax.set_xlabel("Frecuencia (MHz)", fontsize=8)
    ax.set_ylabel("Rating promedio (L–D, 00–24)", fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="x", which="major", labelsize=6, length=6)
    ax.tick_params(axis="x", which="minor", length=3)
    ax.tick_params(axis="y", labelsize=7)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(0.2))
    ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
    ax.xaxis.set_minor_locator(mticker.MultipleLocator(0.1))

    proxy_rated = Line2D([], [], color="#2196F3", linewidth=2, marker="o", markersize=6, alpha=0.7)
    proxy_unrated = Line2D(
        [],
        [],
        color="#999999",
        linewidth=2,
        linestyle="dotted",
        marker="o",
        markersize=6,
        alpha=0.7,
    )
    ax.legend(
        [proxy_rated, proxy_unrated],
        ["Promedio 2017–2025", "Sin datos de rating (altura = promedio global 2017–2025)"],
        fontsize=7,
        loc="upper left",
    )

    ax.figure.suptitle("Rating de Radios FM en Montevideo", fontsize=13, fontweight="bold")

    ax.figure.text(
        0.5,
        -0.02,
        "Fuentes: Buró de Radios (2017–2022) · Factum (2024–2025, datos semioficiales, "
        "solo publican top 3–4)",
        ha="center",
        va="top",
        fontsize=6,
        color="gray",
        transform=ax.figure.transFigure,
    )


def plot_am_freq(ax: Axes) -> None:
    am_stations = sorted(
        (freq, station)
        for station, freq in STATION_FREQ.items()
        if isinstance(freq, int) and station not in INACTIVE_STATIONS
    )

    # Merge Factum AM data
    for st, years in FACTUM_DATA["AM"].items():
        for year, rating in years.items():
            data["AM"][year][st] = rating

    station_ratings: dict[Station, list[float]] = {}
    all_ratings: list[float] = []
    for year_data in data["AM"].values():
        for st, rating in year_data.items():
            all_ratings.append(rating)
            station_ratings.setdefault(st, []).append(rating)

    station_avg = {st: sum(v) / len(v) for st, v in station_ratings.items()}
    global_mean = sum(all_ratings) / len(all_ratings)

    label_dy: dict[Station, float] = {}

    for freq, station in am_stations:
        has = station in station_avg
        if has:
            y = station_avg[station]
            lw = 1 + y * 3
            sz = 10 + y * 60
            color = "#FF6F00"
            ax.plot(
                [freq, freq], [0, y], color=color, linewidth=lw, alpha=0.7, solid_capstyle="round"
            )
            ax.scatter(freq, y, color=color, s=sz, zorder=5)
        else:
            y = global_mean
            lw = 1 + y * 3
            sz = 10 + y * 60
            color = "#999999"
            ax.plot(
                [freq, freq],
                [0, y],
                color=color,
                linewidth=lw,
                linestyle="dotted",
                solid_capstyle="round",
            )
            ax.scatter(freq, y, color=color, s=sz, zorder=5)

        fs = 5.5 + y * 2.5
        ax.text(
            freq,
            y + 0.06 + label_dy.get(station, 0),
            str(station).replace(" ", "\n"),
            ha="center",
            va="bottom",
            fontsize=fs,
            color="black",
            rotation=0,
        )

    ax.set_xlim(500, 1600)
    y_max = max(station_avg.values())
    ax.set_ylim(0, y_max * 1.15)
    ax.set_xlabel("Frecuencia (kHz)", fontsize=8)
    ax.set_ylabel("Rating promedio (L–D, 00–24)", fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="x", which="major", labelsize=6, length=6)
    ax.tick_params(axis="x", which="minor", length=3)
    ax.tick_params(axis="y", labelsize=7)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(0.2))
    ax.xaxis.set_major_locator(mticker.MultipleLocator(100))
    ax.xaxis.set_minor_locator(mticker.MultipleLocator(10))

    proxy_rated = Line2D([], [], color="#FF6F00", linewidth=2, marker="o", markersize=6, alpha=0.7)
    proxy_unrated = Line2D(
        [],
        [],
        color="#999999",
        linewidth=2,
        linestyle="dotted",
        marker="o",
        markersize=6,
        alpha=0.7,
    )
    ax.legend(
        [proxy_rated, proxy_unrated],
        ["Promedio 2017–2025", "Sin datos de rating (altura = promedio global 2017–2025)"],
        fontsize=7,
        loc="upper left",
    )

    ax.figure.suptitle("Rating de Radios AM en Montevideo", fontsize=13, fontweight="bold")

    ax.figure.text(
        0.5,
        -0.02,
        "Fuentes: Buró de Radios (2017–2022) · Factum (2024–2025, datos semioficiales, "
        "solo publican top 3–4)",
        ha="center",
        va="top",
        fontsize=6,
        color="gray",
        transform=ax.figure.transFigure,
    )


# --- SECTION NAME: metadata ---

VARIANTS: list[str] = ["am", "fm", "fm-freq", "am-freq"]


if __name__ == "__main__":
    from shared.utils import generate_notebook, get_cli_args, open_file, save_chart

    args = get_cli_args(VARIANTS)
    if args.notebook:
        generate_notebook("radios")
        raise SystemExit(0)
    selected = args.chart

    cm = 1 / 2.54
    plt.style.use("ggplot")
    plt.rcParams["svg.hashsalt"] = "salt-for-svg-generation"
    output_dir = Path(__file__).parent
    project_name = output_dir.name

    for variant in selected:
        if variant in ("fm-freq", "am-freq"):
            figsize = (32 * cm, 16 * cm)
        else:
            figsize = (30 * cm, 16 * cm)
        fig, axs = plt.subplot_mosaic(
            [["main"]],
            figsize=figsize,
            layout="constrained",
        )
        ax = axs["main"]

        fig.suptitle(
            "Rating de radios en Montevideo",
            fontsize=13,
            fontweight="bold",
        )

        globals()[f"plot_{variant.replace('-', '_')}"](ax)

        stem = output_dir / f"{project_name}-{variant}"
        png = save_chart(fig, stem)
        if args.interactive:
            plt.show()
        elif not args.no_open:
            open_file(png)
        plt.close(fig)
