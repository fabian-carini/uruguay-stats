#! /usr/bin/env python

import math
import statistics
from collections import Counter
from statistics import mean, stdev

### This file has implementations of basic statistic features, using built-in
### solutions when available.


def freq_table(vals: list[int] | list[float]):
    freqs = Counter(vals)

    # fill in-between values, but only for integers
    # - note: in any case, a frequency table only works well for
    #   integers, or for floats which mostly represent integers.
    if isinstance(vals[0], int):
        lo, hi = int(min(vals)), int(max(vals))
        return {v: freqs.get(v, 0) for v in range(lo, hi + 1)}

    return dict(freqs)


def binned_freq_table(vals: list[int] | list[float], bin_width: int | float = 14):
    # replace every value with the start of its bin
    binned_vals = [(v // bin_width) * bin_width for v in vals]

    # count values
    freqs = Counter(binned_vals)

    # Populate result. Fill in empty bins with 0
    lo, hi = min(binned_vals), max(binned_vals)
    return {v: freqs.get(v, 0) for v in range(int(lo), int(hi) + int(bin_width), int(bin_width))}


def pmf(vals: list[int] | list[float], bin_width: int | float | None = None):
    if bin_width:
        ft = binned_freq_table(vals, bin_width)
    else:
        ft = freq_table(vals)
    n = sum(ft.values())
    return {v: f / n for v, f in ft.items()}


def cdf_from_pmf(pm: dict[int, float]):
    acc = 0
    res = {}
    for v, p in pm.items():
        acc += p
        res[v] = acc
    return res


def cdf(vals: list[int] | list[float]):
    """Work for both discrete and continuous data."""
    sorted_vals = sorted(vals)
    n = len(sorted_vals)

    # Automatically overwrites duplicate keys with the highest index, which
    # solves ties.
    return {v: (i + 1) / n for i, v in enumerate(sorted_vals)}


def inverse_cdf(vals: list[int]):
    cd = cdf(vals)
    inv = {}
    for v, p in cd.items():
        # Only keep first 'v' we see for a 'p'
        if p not in inv:
            inv[p] = v
    return inv


def percentile_from_cdf(p_rank, vals):
    inverse_cd = inverse_cdf(vals)
    p = p_rank / 100
    keys = [k for k in inverse_cd if k >= p]
    return inverse_cd[min(keys)]


# See `statistics.quantiles` for an alternative
def percentile(p_rank: float, vals: list[int] | list[float]):
    """Work for both discrete and continuous data."""
    sorted_vals = sorted(vals)
    n = len(sorted_vals)

    if p_rank <= 0:
        return sorted_vals[0]
    if p_rank >= 100:
        return sorted_vals[-1]

    index = (p_rank / 100) * n

    # interpolate between the two bounding values
    lower = int(index)
    upper = lower + 1
    weight = index - lower

    # Value = lower_val + (percentage_distance * difference)
    return sorted_vals[lower] + weight * (sorted_vals[upper] - sorted_vals[lower])


def binomial_pmf(k: int, n: int, p: float):
    return math.comb(n, k) * (p**k) * ((1 - p) ** (n - k))


def poisson_pmf(k: int, lam: float):
    return (lam**k) * math.exp(-lam) / math.factorial(k)


def exponential_cdf(x: float, lam: float):
    return 1 - math.exp(-lam * x)


def exponential_pdf(x: float, lam: float):
    return lam * math.exp(-lam * x)


def _get_normaldist_instance(_mean: float, _stdev: float):
    return statistics.NormalDist(_mean, _stdev)


def normal_cdf(x: float, _mean: float, _stdev: float):
    normal = _get_normaldist_instance(_mean, _stdev)
    return normal.cdf(x)


def normal_pdf(x: float, _mean: float, _stdev: float):
    normal = _get_normaldist_instance(_mean, _stdev)
    return normal.pdf(x)


def _get_normal_kde_function(vals: list[int] | list[float]):
    # calculate bandwidth with "scott's rule"
    # - This is what `scipy.gaussian_kde` does by default.
    bandwidth = 1.059 * stdev(vals) * (len(vals) ** (-1 / 5))
    return statistics.kde(vals, h=bandwidth)


def normal_kde(x: float, vals: list[int] | list[float]):
    kde = _get_normal_kde_function(vals)
    return kde(x)


def generate_normal(_mean: float, _stdev: float):
    return statistics.NormalDist(_mean, _stdev).samples(1)[0]


def generate_correlated(
    vals: list[int] | list[float], rho: float, gen_mean: float, gen_stdev: float
):
    """
    Generate a correlated variable to the variable in 'vals', with the passed
    'correlation coefficient'
    """
    n = len(vals)
    m, s = mean(vals), stdev(vals)
    y_std = [(v - m) / s for v in vals]
    normal_noise = [generate_normal(0, 1) for _ in range(n)]
    z_std = [rho * y_std[i] + math.sqrt(1 - rho**2) * normal_noise[i] for i in range(n)]
    return [gen_mean + gen_stdev * v for v in z_std]


def bin_paired(x_vals, y_vals, q=10):
    """
    Sorts pairs by x_vals, then splits them into q equal-sized bins.
    Returns a list of (x_bin, y_bin) tuples.
    """
    paired = list(zip(x_vals, y_vals))

    # Sort based on `x_vals`
    paired.sort(key=lambda pair: pair[0])

    n = len(paired)
    chunks = [paired[i * n // q : (i + 1) * n // q] for i in range(q)]

    result = []
    for chunk in chunks:
        x_bin = [p[0] for p in chunk]
        y_bin = [p[1] for p in chunk]
        result.append((x_bin, y_bin))

    return result


def jitter(vals: list[int] | list[float], stdev: float = 1):
    # Note: uniform nosi would also work fine
    return [v + generate_normal(0, stdev) for v in vals]


def standardize(vals: list[int] | list[float]):
    m, s = mean(vals), stdev(vals)
    return [(v - m) / s for v in vals]


def linspace(start: int | float, stop: int | float, num=50):
    """Return numbers spaced evenly over an interval (inclusive)"""
    step = (stop - start) / (num - 1)
    return [start + i * step for i in range(num)]


def logspace(start: int | float, stop: int | float, num=50, base=10.0):
    """Return numbers spaced evenly over a log scale (inclusive)"""
    return [base**x for x in linspace(start, stop, num)]


def get_normal_domain(_mean: float, _stdev: float, num=50):
    """Get domain range for a normal distribution, based on mean and stdev"""
    return linspace(_mean - 4 * _stdev, _mean + 4 * _stdev, num=num)


def mse(estimates, actual):
    """Mean Squared Error of a sequence of estimates."""
    errors = [estimate - actual for estimate in estimates]
    return mean([error**2 for error in errors])


def mae(estimates, actual):
    """Mean Absolute Error of a sequence of estimates."""
    errors = [estimate - actual for estimate in estimates]
    return mean([abs(error) for error in errors])
