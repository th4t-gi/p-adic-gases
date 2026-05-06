"""max_β phys_term — maximum phys_term across trees vs β, one curve per prime."""

from __future__ import annotations

import matplotlib.image as mpimg
import mplcursors
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

from app.computations.utils import tree_image_path
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
        line_to_info: dict = {}
        for p in self.df.index.get_level_values("prime").unique():
            valid_ids = trees_df.index[trees_df[f"is_{p}_tree"]]
            phys_term_p = self.df.loc[p, "phys_term"]
            phys_term_p = phys_term_p[phys_term_p.index.get_level_values("tree_id").isin(valid_ids)]
            max_per_beta = phys_term_p.groupby(level="beta").max()
            argmax_per_beta = phys_term_p.groupby(level="beta").idxmax()

            # argmax values are (beta, tree_id) tuples; extract tree_id per beta
            argmax_reindexed = argmax_per_beta.reindex(beta_vals)
            tree_ids_for_line = [
                v[1] if isinstance(v, tuple) else None for v in argmax_reindexed
            ]
            max_vals_for_line = max_per_beta.reindex(beta_vals).tolist()

            (line,) = ax.plot(beta_vals, max_per_beta.reindex(beta_vals).values, label=f"p={p}")
            line_to_info[line] = (tree_ids_for_line, max_vals_for_line)

        ax.set_yscale("log")
        ax.set_xlabel(r"$\beta$")
        ax.set_ylabel(r"$M_I(\beta)$")
        ax.set_title(
            r"Max of $Q_\pitchfork(\beta)$ over all p-trees in $R_I$ for $q=("
            + ", ".join(map(str, charges))
            + r")$"
        )
        ax.legend(title="Prime p")

        self._attach_hover_tooltip(ax, line_to_info, beta_vals)

    def _attach_hover_tooltip(self, ax, line_to_info: dict, beta_vals) -> None:
        if not line_to_info:
            return

        self._hover_cursor = mplcursors.cursor(list(line_to_info), hover=True)
        n = self.computation.n

        @self._hover_cursor.connect("add")
        def _on_add(sel) -> None:
            tree_ids, max_vals = line_to_info.get(sel.artist, ([], []))
            idx = int(sel.index)
            print(sel.index)
            if not (0 <= idx < len(tree_ids)):
                return
            tid = tree_ids[idx]
            if tid is None:
                return
            val = max_vals[idx] if idx < len(max_vals) else None
            beta = beta_vals[idx] if idx < len(beta_vals) else None
            val_str = f"{val:.4e}" if val is not None else "?"
            beta_str = f"{beta:.4f}" if beta is not None else "?"
            label = f"Tree {tid}\nβ={beta_str}\n{val_str}"

            path = tree_image_path(n, tid)
            if not path.exists():
                sel.annotation.set_text(label)
                sel.annotation.arrow_patch.set_visible(True)
                return

            img = mpimg.imread(str(path))
            sel.annotation.set_text(label)
            sel.annotation.arrow_patch.set_visible(False)
            ab = AnnotationBbox(
                OffsetImage(img, zoom=0.2),
                sel.target,
                xybox=(60, 60),
                xycoords="data",
                boxcoords="offset points",
                frameon=True,
                pad=0.1,
            )
            ax.add_artist(ab)
            sel.extras.append(ab)
