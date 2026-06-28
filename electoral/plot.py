#! /usr/bin/env -S uv run python

# --- SECTION NAME: imports ---
import csv
from pathlib import Path

import matplotlib.pyplot as plt

# --- SECTION NAME: data loading ---


def load_csv(filename):
    with open(filename) as f:
        return list(csv.DictReader(f))


def parse_date(date_str):
    parts = date_str.split("-")
    return int(parts[0]), int(parts[1])  # year, month


def load_wide_series(filename):
    row = load_csv(filename)[0]
    result = []
    for k, v in row.items():
        try:
            result.append((int(k), float(v)))
        except ValueError, TypeError:
            pass
    return sorted(result)


def load_rounds(filename, value_col):
    """Returns list of (year, month, value)."""
    return [(*parse_date(r["Date"]), float(r[value_col])) for r in load_csv(filename)]


def assign_x(rows):
    """
    When two entries share a year, the earlier one (by month) is the first round —
    shift it one year left for visualization.
    Returns list of (x, value, is_first_round).
    """
    # group by year, sort each group by month
    by_year = {}
    for year, month, val in rows:
        by_year.setdefault(year, []).append((month, val))
    for year in by_year:
        by_year[year].sort()

    result = []
    for year, entries in by_year.items():
        for i, (month, val) in enumerate(entries):
            is_first = i == 0 and len(entries) > 1
            x = year - 1 if is_first else year
            result.append((x, val, is_first))
    return sorted(result)


data_dir = Path(__file__).parent / "data"

reg_rows = load_rounds(data_dir / "registered-voters-turnout.csv", "Voter Turnout")
vap_rows = load_rounds(data_dir / "vap-turnout.csv", "VAP Turnout")
reg_count = assign_x(load_rounds(data_dir / "registered-voters.csv", "Registration"))
migration = load_wide_series(data_dir / "net-migration.csv")
vote_count = assign_x(load_rounds(data_dir / "total-vote.csv", "Total vote"))
vap_abs = assign_x(load_rounds(data_dir / "vap.csv", "Voting age population"))
reg = assign_x(reg_rows)
vap = assign_x(vap_rows)

# --- SECTION NAME: data processing ---

# interpolate year where registered voters first exceed VAP
_rc = {x: v for x, v, _ in reg_count}
_va = {x: v for x, v, _ in vap_abs}
cross_x = None
for _x0, _x1 in zip(sorted(set(_rc) & set(_va)), sorted(set(_rc) & set(_va))[1:]):
    _d0, _d1 = _rc[_x0] - _va[_x0], _rc[_x1] - _va[_x1]
    if _d0 < 0 < _d1:
        cross_x = _x0 + (_x1 - _x0) * (-_d0 / (_d1 - _d0))
        break

# only keep x values present in both
vap_dict = {x: (v, f) for x, v, f in vap}
combined = [(x, rv, vap_dict[x][0], is_first) for x, rv, is_first in reg if x in vap_dict]

xs = [r[0] for r in combined]
reg_pct = [r[1] for r in combined]
vap_pct = [r[2] for r in combined]
is_first = [r[3] for r in combined]
gap = [v - r for r, v in zip(reg_pct, vap_pct)]

year_range = range(min(xs), max(xs) + 1)


# --- SECTION NAME: plot ---


def add_cross_line(ax, cross_x):
    if cross_x:
        ax.axvline(cross_x, linestyle=":", linewidth=1, color="black", zorder=2)
        ax.text(
            cross_x + 0.5,
            0.97,
            f"Register exceeds VAP (~{cross_x:.0f})",
            fontsize=9,
            color="black",
            alpha=1,
            va="top",
            ha="left",
            transform=ax.get_xaxis_transform(),
        )


def add_historical_spans(ax, y_offset=None):
    ax.axvspan(1973, 1985, alpha=0.15, color="C7")
    ax.axvspan(2001, 2004, alpha=0.15, color="C7")
    if y_offset is not None:
        y = ax.get_ylim()[0] + y_offset
        ax.text(
            1979,
            y,
            "Civic-military dictatorship",
            rotation=90,
            fontsize=7,
            color="C7",
            alpha=0.8,
            va="bottom",
            ha="center",
        )
        ax.text(
            2002.5,
            y,
            "Banking crisis",
            rotation=90,
            fontsize=7,
            color="C7",
            alpha=0.8,
            va="bottom",
            ha="center",
        )


def setup_x_ticks(ax, xs, x_min=None):
    lo = x_min if x_min is not None else min(xs)
    ax.set_xticks(range(lo - lo % 10, max(xs) + 1, 10))
    ax.set_xticks(range(lo - lo % 5, max(xs) + 1, 5), minor=True)
    ax.grid(which="major", axis="x", linewidth=0.8, alpha=0.6)
    ax.grid(which="minor", axis="x", linewidth=0.4, alpha=0.3)


cm = 1 / 2.54
plt.style.use("ggplot")
plt.rcParams["svg.hashsalt"] = "salt-for-svg-generation"

fig, axs = plt.subplot_mosaic(
    [
        ["1", "1", "1", "2", "2"],
        ["1", "1", "1", "2", "2"],
        ["3", "3", "3", "4", "4"],
        ["3", "3", "3", "4", "4"],
    ],
    figsize=(35 * cm, 32 * cm),
    layout="constrained",
)
fig.suptitle(
    "Why the Electoral Registry Exceeds Uruguay's Voting-Age Population",
    fontsize=16,
    fontweight="bold",
)

# 1 — bracketing interval
ax = axs["1"]
ax.set_title("Voter Turnout (Uruguay)")

ax.plot(xs, reg_pct, linewidth=1, color="C0", zorder=1)
ax.plot(xs, vap_pct, linewidth=1, color="C1", zorder=1)

# separate markers for first vs second rounds
for x, r, v, first in zip(xs, reg_pct, vap_pct, is_first):
    size = 3 if first else 5
    ax.plot(x, r, marker="o", markersize=size, color="C0")
    ax.plot(x, v, marker="o", markersize=size, color="C1")


# dummy handles for legend
ax.plot([], [], color="C0", marker="o", label="% registered voters")
ax.plot(
    [],
    [],
    color="C0",
    marker="o",
    markersize=3,
    linestyle="",
    label="first round (shifted -1yr)",
)
ax.plot([], [], color="C1", marker="o", label="% Voting-Age Population (VAP)")

ax.fill_between(
    xs,
    reg_pct,
    vap_pct,
    alpha=0.1,
    zorder=0,
    color="purple",
    label="Interval between VAP % and registered %",
)

add_cross_line(ax, cross_x)
add_historical_spans(ax, 1)

# peak VAP% — 2014 first round (shifted to 2013)
ax.annotate(
    'Peak "Buquebus Effect"\n(VAP% ~99%)',
    xy=(2013, 99.27),
    xytext=(2008, 80),
    fontsize=9,
    color="C1",
    arrowprops=dict(arrowstyle="->", color="C1", alpha=0.5, lw=1.5),
    ha="center",
)

setup_x_ticks(ax, xs)
ax.set_xlabel("Year")
ax.set_ylabel("Turnout (%)")
ax.legend()

# 2 — interval width
ax = axs["2"]
ax.set_title("Interval Width (VAP% − Reg%)")
ax.plot(xs, gap, linewidth=1, color="purple")
for x, g, first in zip(xs, gap, is_first):
    size = 3 if first else 5
    ax.plot(x, g, marker="o", markersize=size, color="purple")
ax.axhline(0, linestyle="dashed", linewidth=0.8, color="gray")
add_cross_line(ax, cross_x)
add_historical_spans(ax, 0.1)
setup_x_ticks(ax, xs)
ax.set_xlabel("Year")
ax.set_ylabel("Gap (Percentage Points)")

# 3 — absolute counts
ax = axs["3"]
ax.set_title("Electorate Size (Uruguay)")

rc_xs = [r[0] for r in reg_count]
rc_vs = [r[1] / 1e6 for r in reg_count]
rc_fs = [r[2] for r in reg_count]

vc_xs = [r[0] for r in vote_count]
vc_vs = [r[1] / 1e6 for r in vote_count]
vc_fs = [r[2] for r in vote_count]

va_xs = [r[0] for r in vap_abs]
va_vs = [r[1] / 1e6 for r in vap_abs]

ax.plot(rc_xs, rc_vs, linewidth=1, color="C0", zorder=1)
ax.plot(vc_xs, vc_vs, linewidth=1, color="C3", zorder=1)
ax.plot(va_xs, va_vs, linewidth=1, color="C1", zorder=1)

for x, v, first in zip(rc_xs, rc_vs, rc_fs):
    ax.plot(x, v, marker="o", markersize=3 if first else 5, color="C0")
for x, v, first in zip(vc_xs, vc_vs, vc_fs):
    ax.plot(x, v, marker="o", markersize=3 if first else 5, color="C3")
for x, v in zip(va_xs, va_vs):
    ax.plot(x, v, marker="o", markersize=5, color="C1")

ax.plot([], [], color="C0", marker="o", label="Registered voters")
ax.plot([], [], color="C1", marker="o", label="Voting-Age Population (VAP)")
ax.plot([], [], color="C3", marker="o", label="Total votes cast")

add_cross_line(ax, cross_x)
add_historical_spans(ax, 0.02)
setup_x_ticks(ax, rc_xs)
ax.set_xlabel("Year")
ax.set_ylabel("People (millions)")
ax.legend()

# 4 — net migration
ax = axs["4"]
ax.set_title("Net Migration (Uruguay)")

mg_xs = [r[0] for r in migration]
mg_vs = [r[1] / 1e3 for r in migration]

ax.plot(mg_xs, mg_vs, linewidth=1, color="C4", zorder=1)
ax.plot(mg_xs, mg_vs, marker="o", markersize=3, linestyle="", color="C4", zorder=2)
ax.axhline(0, linestyle="dashed", linewidth=0.8, color="gray")
add_cross_line(ax, cross_x)
add_historical_spans(ax)
ax.set_xlim(left=min(xs))
setup_x_ticks(ax, mg_xs, x_min=min(xs))
ax.set_xlabel("Year")
ax.set_ylabel("Net migration (thousands)")

if __name__ == "__main__":
    from shared.utils import generate_notebook, get_cli_args, open_file, save_chart

    args = get_cli_args()
    if args.notebook:
        generate_notebook("electoral")
        raise SystemExit(0)
    output_dir = Path(__file__).parent
    png = save_chart(fig, output_dir / output_dir.name)
    if args.interactive:
        plt.show()
    elif not args.no_open:
        open_file(png)
