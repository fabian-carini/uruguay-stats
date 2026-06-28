#! /usr/bin/env -S uv run python

# --- SECTION NAME: imports ---
import csv
import math
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

import matplotlib.pyplot as plt

# --- SECTION NAME: constants ---

# (label, party, inauguration year, opuy `presidente` slug)
TERMS = [
    ("Lacalle", "PN", 1990, "Lacalle"),
    ("Sanguinetti II", "PC", 1995, "Sanguinetti 2"),
    ("Batlle", "PC", 2000, "Batlle"),
    ("Vázquez I", "FA", 2005, "Vazquez 1"),
    ("Mujica", "FA", 2010, "Mujica"),
    ("Vázquez II", "FA", 2015, "Vazquez 2"),
    ("Lacalle Pou", "PN", 2020, "Lacalle Pou"),
    ("Orsi", "FA", 2025, "Orsi"),
]
TERM_END_YEAR = 2030

PARTY_COLORS = {
    "PN": "#5DADE2",
    "PC": "#BA0200",
    "FA": "#013197",
}

MARCH_FRAC = 60 / 365  # March 1 ≈ day 60

# --- SECTION NAME: data loading ---


def parse_date(s):
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def to_decimal_year(d):
    start = date(d.year, 1, 1)
    end = date(d.year + 1, 1, 1)
    return d.year + (d - start).days / (end - start).days


def load_approval(path):
    with open(path) as f:
        for r in csv.DictReader(f):
            if r["medicion"] != "Evaluacion de gestion presidente":
                continue
            if r["categoria_unificada"] != "3":
                continue
            d = parse_date(r["fecha"])
            if d is None:
                continue
            yield {
                "x": to_decimal_year(d),
                "value": float(r["valor"]),
                "president": r["presidente"].strip(),
            }


data_dir = Path(__file__).parent / "data"
rows = list(load_approval(data_dir / "opuy.csv")) + list(load_approval(data_dir / "new.csv"))

# --- SECTION NAME: data processing ---

by_president = defaultdict(list)
for r in rows:
    by_president[r["president"]].append(r)


# Tricube-weighted local linear regression — mirrors ggplot2's
# geom_smooth(method = "loess", span = 0.75) for our purposes.
def lowess(xs, ys, frac=0.75):
    n = len(xs)
    if n < 2:
        return list(xs), list(ys)
    r = max(math.ceil(frac * n), 2)
    out = []
    for i in range(n):
        d = [abs(xs[j] - xs[i]) for j in range(n)]
        h = sorted(d)[min(r - 1, n - 1)]
        if h > 0:
            w = [(1 - min(di / h, 1.0) ** 3) ** 3 for di in d]
        else:
            w = [1.0 if di == 0 else 0.0 for di in d]
        sw = sum(w)
        if sw == 0:
            out.append(ys[i])
            continue
        x_bar = sum(w[j] * xs[j] for j in range(n)) / sw
        y_bar = sum(w[j] * ys[j] for j in range(n)) / sw
        denom = sum(w[j] * (xs[j] - x_bar) ** 2 for j in range(n))
        if denom > 0:
            b = sum(w[j] * (xs[j] - x_bar) * (ys[j] - y_bar) for j in range(n)) / denom
            out.append((y_bar - b * x_bar) + b * xs[i])
        else:
            out.append(y_bar)
    return list(xs), out


# --- SECTION NAME: plot ---

cm = 1 / 2.54
plt.style.use("ggplot")
plt.rcParams["svg.hashsalt"] = "salt-for-svg-generation"

fig, ax = plt.subplots(figsize=(34 * cm, 18 * cm), layout="constrained")

# term-boundary vlines at each inauguration (Mar 1)
for _, _, year, _ in TERMS[1:]:
    ax.axvline(
        year + MARCH_FRAC,
        linestyle="--",
        linewidth=0.4,
        color="#4d4d4d",
        alpha=0.6,
        zorder=1,
    )

# 50% reference line
ax.axhline(50, linestyle=":", linewidth=0.8, color="gray", alpha=0.5, zorder=1)

# per-president: scatter + LOESS curve in the party color
for label, party, year, slug in TERMS:
    pts = sorted(by_president.get(slug, []), key=lambda r: r["x"])
    if not pts:
        continue
    xs = [p["x"] for p in pts]
    ys = [p["value"] for p in pts]
    color = PARTY_COLORS[party]
    ax.scatter(xs, ys, color=color, s=12, alpha=0.3, edgecolors="none", zorder=2)
    if len(xs) >= 4:
        xs_s, ys_s = lowess(xs, ys, frac=0.5)
        ax.plot(xs_s, ys_s, color=color, linewidth=2, zorder=3)
    # president label at top of the term band
    next_year = next((y for _, _, y, _ in TERMS if y > year), TERM_END_YEAR)
    mid = (year + next_year) / 2 + MARCH_FRAC
    ax.text(
        mid,
        92,
        label,
        ha="center",
        va="bottom",
        fontsize=9.5,
        color="black",
        alpha=0.85,
    )

# legend entries for the three parties
for party, name in [
    ("FA", "Frente Amplio"),
    ("PN", "Partido Nacional"),
    ("PC", "Partido Colorado"),
]:
    ax.plot([], [], color=PARTY_COLORS[party], linewidth=2, label=name)

ax.set_xlabel("Año")
ax.set_ylabel("% de aprobación")
ax.set_title(
    "Serie histórica de aprobación del presidente (Uruguay, 1990 – 2026/06)",
    fontsize=14,
    fontweight="bold",
)
ax.set_xlim(1990, TERM_END_YEAR + MARCH_FRAC)
ax.set_ylim(0, 100)
ax.set_xticks(range(1990, TERM_END_YEAR + 1, 2))
ax.set_xticks(range(1990, TERM_END_YEAR + 1, 1), minor=True)
ax.grid(which="major", axis="x", linewidth=0.5, alpha=0.4)
ax.grid(which="minor", axis="x", linewidth=0.3, alpha=0.2)
ax.legend(loc="lower left", fontsize=9, frameon=True)

# caption
fig.text(
    0.5,
    -0.05,
    "Fuente: opuy (UMAD-FCS, 1990–2023) + Encuestadoras\n"
    "Encuestadoras: Equipos, Cifra, Factum, Opción, Interconsult, Radar, Nómade, Ágora",
    ha="center",
    fontsize=8,
    alpha=0.7,
)

if __name__ == "__main__":
    from shared.utils import generate_notebook, get_cli_args, open_file, save_chart

    args = get_cli_args()
    if args.notebook:
        generate_notebook("approval")
        raise SystemExit(0)
    output_dir = Path(__file__).parent
    png = save_chart(fig, output_dir / output_dir.name)
    if args.interactive:
        plt.show()
    elif not args.no_open:
        open_file(png)
