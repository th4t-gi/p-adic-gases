"""Run-time computation: turns a RunConfig into the per-tree DataFrame.

Mirrors data-analysis/physics.py::compute() but driven by RunConfig from the
launch form. Synchronous for now — runs on the GUI thread when RunWindow opens.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from app.computations.physics import (
    beta_grid,
    double_weight,
    interaction_energy,
    term,
    weight,
)
from app.computations.utils import load_trees
from app.plots import RunConfig


class RunComputation:
    def __init__(self, config: RunConfig, db_path: Path | None = None) -> None:
        self.config = config
        self.db_path = db_path
        self.energies: np.ndarray = interaction_energy(config.charges)
        self.beta_vals: np.ndarray = beta_grid(config.charges, config.beta_step)
        self._df: pd.DataFrame | None = None

    @property
    def n(self) -> int:
        return len(self.config.charges)

    def run(self) -> pd.DataFrame:
        """Build the (prime, beta, tree_id)-indexed DataFrame and cache it."""
        if self._df is not None:
            return self._df

        trees = load_trees(self.n, self.db_path)
        energies = self.energies
        df_arr: list[pd.DataFrame] = []

        for p in self.config.primes:
            for beta in self.beta_vals:
                terms = trees.apply(
                    lambda row, p=p, beta=beta: term(row["branches"], row["degrees"], p, energies, beta),
                    axis=1,
                )
                total = terms.sum()
                probs = terms / total

                weights = trees.apply(
                    lambda row, p=p, beta=beta: weight(row["branches"], p, energies, beta),
                    axis=1,
                )
                doubles = trees.apply(
                    lambda row, p=p, beta=beta: double_weight(row["branches"], p, energies, beta),
                    axis=1,
                )

                df_arr.append(
                    pd.DataFrame(
                        {
                            "prime": p,
                            "beta": beta,
                            "tree_id": trees.index,
                            "term": terms,
                            "phys_prob": probs,
                            "weight": weights,
                            "double_weight": doubles,
                        }
                    )
                )

        df = pd.concat(df_arr).set_index(["prime", "beta", "tree_id"])
        self._df = df
        return df
