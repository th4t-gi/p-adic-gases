import numpy as np
from typing import List

from utils import interaction_energy, term, weight, double_weight

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.animation import FuncAnimation
from matplotlib.ticker import MaxNLocator

import pandas as pd


class TreePlt:

    def __init__(self, df: pd.DataFrame, primes: List[int], set_charges: List[int], beta_step: float,
                 sort_by: int | str =None, init_sort_only=False, subplots=False, n_trees=0, auto_scale=False):
        if (init_sort_only and not sort_by):
            raise ValueError("Sort_by not provided for initial sort")
        self.df = df
        self.primes = primes
        self.set_charges = set_charges
        self.beta_step = beta_step
        self.sort = sort_by
        if (type(sort_by) == int):
            self.sort_by = sort_by
        self.init_sort_only = init_sort_only
        self.subplots = subplots
        self.auto_scale = auto_scale

        self.N = len(self.set_charges)
        self.energies = interaction_energy(self.set_charges)
        self.beta_vals = self.df.index.get_level_values("beta").unique()
        self.tree_ids = self.df.index.get_level_values('tree_id').unique()
        self.tree_labels = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26]
        self.n_trees = n_trees if n_trees > 0 and n_trees < len(
            self.tree_ids) else len(self.tree_ids)
        
        self.fig_size = (10, 3)

        # Set up probability plot with slider
        if self.subplots:
            self.fig, axs = plt.subplots(
                1,
                len(self.primes),
                figsize=self.fig_size,
                sharey=True,
                sharex=sort_by != "all"
            )
            self.ax = np.atleast_1d(axs)
            # for ax in self.ax[1:]:
            #     ax.set_yticks([])  # Remove y-ticks
            #     # ax.set_ylabel("")
        else:
            self.fig, ax = plt.subplots(figsize=self.fig_size)
            self.ax = np.array([ax])
                
        self.fig.supylabel("Probability", x=0.01)
        self.fig.supxlabel("Tree ID", y=0.01)

        self.ax_slider = self.fig.add_axes([0.15, 0.04, 0.7, 0.02])
        self.fig._slider = Slider(
            # left,bottom,width,height
            ax=self.ax_slider,
            label=r'$\beta$',
            valmin=min(self.beta_vals),
            valmax=max(self.beta_vals),
            valinit=0,
            valstep=self.beta_vals
        )
        self.fig._slider.on_changed(self.update)

        # self.ax_slider.set_axis_off()
        # self.fig._slider.ax.set_visible(False)

    def __str__(self):
        return f"Tree Plot (q={self.set_charges}, p={self.primes}, step={self.beta_step})"

    def plot(self):
        # if p not in self.df.index.get_level_values("prime").unique():
        #     print(f"Unable to plot prime {p}")
        #     return

        # beta = self.beta_vals[90]
        beta = self.fig._slider.val

        # sorting
        sorted_idx = self.get_sort_index(beta, init=True)
        sorted_tree_ids = np.array(self.tree_ids)[sorted_idx]
        print(sorted_tree_ids)

        # Filter for the desired beta
        df_beta = self.df.xs(beta, level="beta")
        # Pivot so that tree_id is index, prime values are columns
        df_p = df_beta["phys_prob"].unstack(level="prime")[self.primes]
        # Filter rows for sorted_tree_ids
        df_p = df_p.loc[sorted_tree_ids]

        ax = self.ax.tolist()
        title = [f"p={p}" for p in self.primes]
        if not self.subplots:
            ax = self.ax.tolist()[0]
            title = None

        df_p.plot(
            kind="bar", 
            width=0.8, 
            ax=ax, 
            subplots=self.subplots, 
            legend=False, 
            title=title,
            xlabel="",
            rot=0,
        )

        # Automatically set a reasonable number of x-ticks
        for i, ax in enumerate(self.ax if self.subplots else [self.ax[0]]):
            xticks = [list(df_p.index).index(t)
                      for t in self.tree_labels if t in df_p.index]
            ax.set_xticks(xticks)
            ax.set_xticklabels([str(t) for t in self.tree_labels if t in df_p.index])
            if i > 0:
                ax.tick_params(left=False)
            # ax.yaxis.set_major_locator(plt.NullLocator())


        # Update Titles
        self.filename = f"prob_n{self.N}_q{self.set_charges}_p{self.primes}_b{self.beta_step:.3f}.mp4"
        self.title = f'Physical Probability of Trees\n(N={self.N}, q={self.set_charges}, p={self.primes}, step={self.beta_step:.3f})'
        self.fig.suptitle(self.title)
        self.fig.canvas.manager.set_window_title(f"Prob for {self.primes}")

        if self.subplots and self.sort == "all":
            self.update(0)

        if not self.subplots:
            self.ax[0].legend(title="Prime p")

        plt.tight_layout(w_pad=0.25)
        plt.subplots_adjust(bottom=0.15)

    def update(self, val):
        beta = self.fig._slider.val
        

        for i, ax in enumerate(self.ax):
            primes = [self.primes[i]] if self.subplots else self.primes
            for j, p in enumerate(primes):
                container = ax.containers[0] if self.subplots else ax.containers[j]

                sort_by = self.sort_by if hasattr(self, "sort_by") else p
                sorted_idx = self.get_sort_index(beta, sort_by)
                sorted_tree_ids = np.array(self.tree_ids)[sorted_idx]
                # ax.set_xticklabels(sorted_tree_ids)


                probs = self.df["phys_prob"][(p, beta)]
                probs_sorted = np.array(probs)[sorted_idx]

                for rect, h in zip(container, probs_sorted):
                    rect.set_height(h)

                if (self.auto_scale):
                    ax.relim()
                    ax.autoscale_view()

        self.fig.canvas.draw_idle()

    def get_sort_index(self, beta, p=None, init=False):
        sort_idx = None
        beta = 0 if self.init_sort_only else beta

        if self.init_sort_only and hasattr(self, "sort_idx"):
            return self.sort_idx
        if not self.sort:
            sort_idx = np.arange(len(self.tree_ids))
        elif init:
            if hasattr(self, "sort_by"):
                sort_probs = self.df["phys_prob"][(self.sort_by, beta)]
                sort_idx = np.argsort(-np.array(sort_probs), stable=True)
            else:
                sort_idx = np.arange(len(self.tree_ids))
        elif p:
            sort_probs = self.df["phys_prob"][(p, beta)]
            sort_idx = np.argsort(-np.array(sort_probs), stable=True)

        self.sort_idx = sort_idx[:self.n_trees]
        return self.sort_idx

    def save_beta_animation(self, total_time=20):
        """
        Save an animation of the bar plot as beta varies.
        """
        def animate(i):
            beta = self.beta_vals[i]
            self.fig._slider.set_val(beta)

            return [rect for ax in self.ax for rect in ax.containers[0]]

        interval = total_time*1000/len(self.beta_vals)
        anim = FuncAnimation(
            self.fig, animate, frames=len(self.beta_vals), interval=interval, blit=False, repeat=False
        )

        print(f"Saving animation to ./animations/{self.filename}...")
        anim.save("../animations/"+self.filename, writer='ffmpeg')
        print(f"Animation saved to ./animations/{self.filename}")
