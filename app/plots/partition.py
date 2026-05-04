"""Z_N(β) — canonical partition function vs β, one curve per prime."""

from __future__ import annotations

from app.computations.physics import beta_critical
from app.plots.base import BasePlot


class PartitionPlot(BasePlot):
    def render(self) -> None:
        ax = self.fig.add_subplot(111)
        beta_vals = self.computation.beta_vals
        energies = self.computation.energies
        charges = self.config.charges

        for p in self.df.index.get_level_values("prime").unique():
            z_vals = []
            for beta in beta_vals:
                total = self.df["term"][(p, beta)].sum()
                z_vals.append((p ** (energies[-1] * beta)) * total)
            ax.plot(beta_vals, z_vals, label=f"p={p}")

        q_min, q_max = min(charges), max(charges)
        if q_min < 0 < q_max:
            ax.set_yscale("log")
            bc = beta_critical(charges)
            ax.axvline(x=bc, linestyle="--", color="black")
            ax.annotate(
                r"$\beta_c$",
                xy=(bc, 0.3),
                xycoords=("data", "axes fraction"),
                ha="center",
                va="top",
                fontsize=12,
                bbox=dict(facecolor="white", edgecolor="white"),
            )

        ax.set_xlabel(r"$\beta$")
        ax.set_ylabel(r"$\mathcal{Z}_N(\beta)$")
        ax.set_title(
            r"$\mathcal{Z}_N(\beta)$ for $q=("
            + ", ".join(map(str, charges))
            + r")$"
        )
        ax.legend(title="Prime p")
