"""max_β phys_term — maximum phys_term across trees vs β, one curve per prime."""

from __future__ import annotations

from app.plots.base import BasePlot


class MaxQuotientPlot(BasePlot):
    def render(self) -> None:
        ax = self.fig.add_subplot(111)
        beta_vals = self.computation.beta_vals
        charges = self.config.charges
        trees_df = self.computation._trees_df

        # including all trees:
        # max_per_beta = self.df["phys_term"].groupby(level=["prime", "beta"]).max()
        # for p in max_per_beta.index.get_level_values("prime").unique():
        #     ax.plot(beta_vals, max_per_beta.loc[p].values, label=f"p={p}")

        # including only p-trees:
        for p in self.df.index.get_level_values("prime").unique():
            valid_ids = trees_df.index[trees_df[f"is_{p}_tree"]]
            phys_term_p = self.df.loc[p, "phys_term"]
            phys_term_p = phys_term_p[phys_term_p.index.get_level_values("tree_id").isin(valid_ids)]
            max_per_beta = phys_term_p.groupby(level="beta").max()
            ax.plot(beta_vals, max_per_beta.reindex(beta_vals).values, label=f"p={p}")

        ax.set_yscale("log")
        ax.set_xlabel(r"$\beta$")
        ax.set_ylabel(r"$M_I(\beta)$")
        ax.set_title(
            r"Max of $Q_\pitchfork(\beta)$ over all p-trees in $R_I$ for $q=("
            + ", ".join(map(str, charges))
            + r")$"
        )
        ax.legend(title="Prime p")
