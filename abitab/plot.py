#! /usr/bin/env -S uv run python

# --- SECTION NAME: imports ---
import csv
import re
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt

# --- SECTION NAME: constants ---

AB_COLOR = "#005bb5"  # Abitab Blue
RP_COLOR = "#009c3b"  # Redpagos Green
GAP_COLOR = "purple"


# --- SECTION NAME: data loading ---


def load_csv(filename):
    with open(filename, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def parse_date_from_filename(filename):
    match = re.search(r"^(\d{4}-\d{2}-\d{2})", filename)
    if match:
        return datetime.strptime(match.group(1), "%Y-%m-%d").date()
    return None


def load_store_counts(data_dir):
    directory = Path(data_dir)
    data = []

    if not directory.exists():
        print(f"Warning: Directory '{data_dir}' not found. Ensure it exists.")
        return data

    for file_path in directory.glob("*.csv"):
        dt = parse_date_from_filename(file_path.name)

        if not dt:
            continue

        # modify date to be Jan 01
        dt = dt.replace(month=1, day=1)

        rows = load_csv(file_path)
        companies = [row.get("Company", "").strip().upper() for row in rows]
        counts = Counter(companies)

        data.append((dt, counts.get("ABITAB", 0), counts.get("REDPAGOS", 0)))

    return sorted(data)


data_dir = Path(__file__).parent / "data"
series = load_store_counts(data_dir)

# --- SECTION NAME: data processing ---


def estimate_convergence_year(xs, abitab_vals, redpagos_vals):
    origin = xs[0]
    x = [(d - origin).days for d in xs]
    gaps = [a - r for a, r in zip(abitab_vals, redpagos_vals)]

    # Linear regression (least squares): y = m*x + b
    n = len(x)
    mean_x = sum(x) / n
    mean_y = sum(gaps) / n
    m = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, gaps)) / sum(
        (xi - mean_x) ** 2 for xi in x
    )
    b = mean_y - m * mean_x

    if m >= 0:
        return None  # Gap not shrinking

    days_to_zero = -b / m
    return origin + timedelta(days=int(days_to_zero))


xs = [r[0] for r in series]
abitab_vals = [r[1] for r in series]
redpagos_vals = [r[2] for r in series]

totals = [a + r for a, r in zip(abitab_vals, redpagos_vals)]
abitab_shares = [(a / t * 100) if t > 0 else 0 for a, t in zip(abitab_vals, totals)]
redpagos_shares = [(r / t * 100) if t > 0 else 0 for r, t in zip(redpagos_vals, totals)]
gaps = [a - r for a, r in zip(abitab_vals, redpagos_vals)]

# Calculate net differences from the first point to the last point
ab_net_diff = abitab_vals[-1] - abitab_vals[0]
rp_net_diff = redpagos_vals[-1] - redpagos_vals[0]

# Calculate dynamic x-axis limits with padding to avoid label clipping
if len(xs) > 1:
    days_span = (xs[-1] - xs[0]).days
    x_pad_left = timedelta(days=int(days_span * 0.05))
    x_pad_right = timedelta(days=int(days_span * 0.15))
else:
    x_pad_left = timedelta(days=30)
    x_pad_right = timedelta(days=180)

x_min = xs[0] - x_pad_left
x_max = xs[-1] + x_pad_right

convergence = estimate_convergence_year(xs, abitab_vals, redpagos_vals)

# --- SECTION NAME: plot ---


def annotate_last(ax, x, y, text, color):
    """Appends the actual value text to the final point in a series."""
    ax.annotate(
        text,
        xy=(x, y),
        xytext=(8, 0),  # offset 8 points to the right
        textcoords="offset points",
        color=color,
        fontweight="bold",
        fontsize=10,
        va="center",
        ha="left",
        clip_on=False,
    )


def add_max_gap_annotation(ax, dates, gaps):
    if not gaps:
        return
    max_gap = max(gaps)
    max_idx = gaps.index(max_gap)
    max_date = dates[max_idx]

    ax.annotate(
        f"Max Gap\n({max_gap} locs)",
        xy=(max_date, max_gap),
        xytext=(max_date, max_gap * 0.7),
        fontsize=9,
        color=GAP_COLOR,
        arrowprops=dict(arrowstyle="->", color=GAP_COLOR, alpha=0.5, lw=1.5),
        ha="center",
        clip_on=False,
    )


cm = 1 / 2.54
plt.style.use("ggplot")
plt.rcParams["svg.hashsalt"] = "salt-for-svg-generation"
fig, axs = plt.subplot_mosaic(
    [
        ["1", "2"],
        ["3", "4"],
    ],
    figsize=(32 * cm, 22 * cm),
    layout="constrained",
)
fig.suptitle(
    "Abitab vs Redpagos (In Montevideo)",
    fontsize=16,
    fontweight="bold",
)

# 1 — Absolute Counts
ax = axs["1"]
ax.set_title("Store Counts")

ax.plot(
    xs,
    abitab_vals,
    linewidth=1.5,
    color=AB_COLOR,
    marker="o",
    markersize=5,
    zorder=2,
    label="ABITAB",
)
ax.plot(
    xs,
    redpagos_vals,
    linewidth=1.5,
    color=RP_COLOR,
    marker="o",
    markersize=5,
    zorder=2,
    label="REDPAGOS",
)

annotate_last(ax, xs[-1], abitab_vals[-1], f"{abitab_vals[-1]}", AB_COLOR)
annotate_last(ax, xs[-1], redpagos_vals[-1], f"{redpagos_vals[-1]}", RP_COLOR)

ax.set_ylim(bottom=-12, top=270)
ax.set_ylabel("Number of Stores")
ax.legend()

# 2 — Market Share
ax = axs["2"]
ax.set_title("Market Share (By Number of Stores)")

ax.plot(
    xs,
    abitab_shares,
    linewidth=1.5,
    color=AB_COLOR,
    marker="o",
    markersize=4,
    label="ABITAB %",
)
ax.plot(
    xs,
    redpagos_shares,
    linewidth=1.5,
    color=RP_COLOR,
    marker="o",
    markersize=4,
    label="REDPAGOS %",
)

ax.axhline(50, linestyle="dashed", linewidth=0.8, color="gray", alpha=0.7)

annotate_last(ax, xs[-1], abitab_shares[-1], f"{abitab_shares[-1]:.1f}%", AB_COLOR)
annotate_last(ax, xs[-1], redpagos_shares[-1], f"{redpagos_shares[-1]:.1f}%", RP_COLOR)

ax.set_ylabel("Share of Total (%)")
ax.set_ylim(-5, 105)
ax.legend()

# 3 — Absolute Gap
ax = axs["3"]
ax.set_title("Gap (Abitab − Redpagos)")

ax.plot(xs, gaps, linewidth=1.5, color=GAP_COLOR, marker="o", markersize=4)
ax.axhline(0, linestyle="dashed", linewidth=0.8, color="gray", alpha=0.7)

add_max_gap_annotation(ax, xs, gaps)

ax.set_xlabel("Year")
ax.set_ylim(-5, 105)
ax.set_ylabel("Gap (Locations)")

if convergence is not None:
    axs["3"].text(
        0.93,
        0.63,
        f"At current trend, parity by {convergence.year}",
        transform=axs["3"].transAxes,
        fontsize=9,
        color=GAP_COLOR,
        ha="right",
        va="top",
    )

# 4 — Net Change Bar Chart
ax = axs["4"]
ax.set_title(f"Net Change ({xs[0].year} to {xs[-1].year})")

categories = ["ABITAB", "REDPAGOS"]
values = [ab_net_diff, rp_net_diff]
colors = [AB_COLOR, RP_COLOR]

bars = ax.bar(categories, values, color=colors, width=0.5, alpha=0.85)
ax.axhline(0, color="gray", linewidth=1.2)

for bar in bars:
    yval = bar.get_height()
    label_text = f"+{yval}" if yval > 0 else str(yval)
    offset = 4 if yval >= 0 else -14
    va = "bottom" if yval >= 0 else "top"
    ax.annotate(
        label_text,
        xy=(bar.get_x() + bar.get_width() / 2, yval),
        xytext=(0, offset),
        textcoords="offset points",
        ha="center",
        va=va,
        fontweight="bold",
        fontsize=11,
        color=bar.get_facecolor(),
    )

ax.set_ylim(top=30)
ax.set_ylabel("Net Difference (Locations)")

for key in ["1", "2", "3"]:
    axs[key].set_xlim(left=x_min, right=x_max)

if __name__ == "__main__":
    from shared.utils import generate_notebook, get_cli_args, open_file, save_chart

    args = get_cli_args()
    if args.notebook:
        generate_notebook("abitab")
        raise SystemExit(0)
    output_dir = Path(__file__).parent
    png = save_chart(fig, output_dir / output_dir.name)
    if args.interactive:
        plt.show()
    elif not args.no_open:
        open_file(png)
