"""Pure-math helpers shared between the launch form and run logic.

Mirrors the formulas in data-analysis/physics.py (lines ~150-170): given a list
of charges and a beta step, derive the critical inverse-temperature β_c and the
β-grid that the partition-function sweep will use.
"""

from __future__ import annotations

import math
from fractions import Fraction
from functools import lru_cache


def parse_int_list(text: str) -> list[int]:
    """Parse a user-typed list of integers.

    Accepts ``"1, 2, 3"``, ``"[1, 2, 3]"``, ``"1 2 3"``, or any mix.
    Returns an empty list for empty input. Raises ``ValueError`` on any token
    that isn't a valid integer.
    """
    text = text.strip().strip("[]()").strip()
    if not text:
        return []
    parts = text.replace(",", " ").split()
    return [int(p) for p in parts]


def beta_critical(charges: list[int]) -> float:
    """β_c = 1/|q_max · q_min| when charges have mixed signs, else 2."""
    if not charges:
        raise ValueError("charges is empty")
    q_max = max(charges)
    q_min = min(charges)
    if q_max * q_min >= 0:
        return 2.0
    return 1.0 / abs(q_max * q_min)


def beta_value_count(charges: list[int], step: float) -> int:
    """Number of β values that ``np.arange(-step, β_c, step)[1:]`` will produce."""
    if step <= 0:
        raise ValueError("step must be positive")
    bc = beta_critical(charges)
    # np.arange(-step, bc, step) -> count = ceil((bc - (-step)) / step)
    n = max(0, math.ceil((bc + step) / step))
    # the [1:] slice in physics.py drops the first element (-step)
    return max(0, n - 1)


@lru_cache(maxsize=None)
def phylogenetic_tree_count(n: int) -> int:
    """|R_N|: number of rooted phylogenetic trees on n labeled leaves (OEIS A000311).

    Ports the recurrence from ``src/utils.cpp::phylogenees_num`` but in exact
    rational arithmetic so the result is exact for any n.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n < 2:
        return n  # A000311(0) = 0, A000311(1) = 1

    # b[i] satisfies a(i) = i! * b[i]; a(i) is the OEIS value.
    b = [Fraction(0), Fraction(1), Fraction(1, 2)]
    for i in range(3, n + 1):
        s = sum((b[k] * b[i - k] * (i - k) for k in range(2, i - 1)), Fraction(0))
        b.append(Fraction(i + 1, i) * b[i - 1] + Fraction(2, i) * s)

    return int(math.factorial(n) * b[n])
