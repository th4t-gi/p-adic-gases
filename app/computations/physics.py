"""Physics formulas for the p-adic gas log-Coulomb partition function.

Mirrors the math in data-analysis/physics.py and data-analysis/utils.py.
The math is duplicated here so the GUI does not depend on the data-analysis
script layout.
"""

from __future__ import annotations

import math
from typing import List

import numpy as np

from app.computations.utils import falling_factorial


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
    n = max(0, math.ceil((bc + step) / step))
    return max(0, n - 1)


def beta_grid(charges: list[int], step: float) -> np.ndarray:
    """β values from -step up to (but excluding) β_c, with the leading -step dropped.

    Matches ``np.arange(-step, beta_critical(charges), step)[1:]`` from
    data-analysis/physics.py.
    """
    if step <= 0:
        raise ValueError("step must be positive")
    return np.arange(-step, beta_critical(charges), step)[1:]


def factor(branch: int, degree: int, p: int, e_J: float, beta: float) -> float:
    size_J = branch.bit_count()
    denom = p ** (size_J + (e_J * beta)) - p
    return falling_factorial(p, degree) / denom


def weight(branches: List[int], p: int, energies: np.ndarray, beta: float) -> float:
    total = 0.0
    for J in branches:
        size_J = J.bit_count()
        e_J = energies[J]
        total += e_J / (1 - p ** (1 - size_J - (e_J * beta)))
    return total


def double_weight(branches: List[int], p: int, energies: np.ndarray, beta: float) -> float:
    total = 0.0
    for J in branches:
        size_J = J.bit_count()
        e_J = energies[J]
        power = p ** (1 - size_J - (e_J * beta))
        total += power * ((e_J / (1 - power)) ** 2)
    return total


def term(branches: List[int], degrees: List[int], p: int, energies: np.ndarray, beta: float) -> float:
    out = 1.0
    for J, degree in zip(branches, degrees):
        out *= factor(J, degree, p, energies[J], beta)
    return out


def interaction_energy(charges: list[int]) -> np.ndarray:
    """Array of length 2^N indexed by branch bitmask J, returning e_J."""
    n = len(charges)
    out = np.empty(1 << n, dtype=float)
    for J in range(1 << n):
        sum1 = 0.0
        sum2 = 0.0
        for i, q in enumerate(charges):
            if J & (1 << i):
                sum1 += q
                sum2 += q * q
        out[J] = (sum1 * sum1 - sum2) / 2.0
    return out
