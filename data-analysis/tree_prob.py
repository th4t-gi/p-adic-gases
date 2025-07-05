import numpy as np
from typing import List

from utils import interaction_energy, term, weight, double_weight

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.animation import FuncAnimation

import pandas as pd


class TreePlt:

    def __init__(self, df: pd.DataFrame, set_charges: List[int], beta_step: float, sig_plus: float, sig_minus: float, beta_vals, split=False):
        self.df = df
        self.primes = []
        self.set_charges = set_charges
        self.N = len(self.set_charges)
        self.energies = interaction_energy(self.set_charges)

        self.beta_step = beta_step
        self.sig_plus = sig_plus
        self.sig_minus = sig_minus
        self.beta_vals = self.df.index.get_level_values("beta").unique()

        # Set up probability plot with slider
        self.fig, self.ax = plt.subplots(figsize=(7, 4.5))
        plt.subplots_adjust(bottom=0.2)
        self.ax.set_xlabel('Tree ID (row index)')
        self.ax.set_ylabel('Probability')

        # ax.set_ylim(top=0.5, auto=False)
        # ax.set_yscale("log")
        plt.xticks(rotation=90)

        self.fig._slider = Slider(
            # left,bottom,width,height
            ax=self.fig.add_axes([0.15, 0.04, 0.7, 0.02]),
            label=r'$\beta$',
            valmin=-sig_plus,
            valmax=sig_minus,
            valinit=0,
            valstep=self.beta_vals
        )
        self.fig._slider.on_changed(self.update)

    def plot(self, p: int):
        if p in self.primes:
            return

        self.primes.append(p)
        # Gets x-axis tree IDs
        tree_ids = self.df.loc[p].index.get_level_values('tree_id').unique()
        # xlabels = [f"{tid} ({i})" for i, tid in enumerate(tree_ids)]
        n_trees = len(tree_ids)
        n_p = len(self.primes)
        width = 0.8 / n_p  # width of each bar

        # Remove previous bars if any
        if hasattr(self, "bar_containers"):
            for bars in self.bar_containers:
                for rect in bars:
                    rect.remove()

        self.bar_containers = []
        colors = plt.cm.get_cmap('tab10')
        beta = self.fig._slider.val

        for i, p in enumerate(self.primes):
            probs = self.df["phys_prob"][(p, beta)]
            # Calculate bar positions for grouped bars
            x = np.arange(n_trees) + (i - n_p/2) * width + width/2
            bars = self.ax.bar(x, probs, width=width,
                               label=f"p={p}", color=colors(i))
            self.bar_containers.append(bars)

        self.title = f'Physical Probability of Trees\n(N={self.N}, q={self.set_charges}, p={self.primes}, step={self.beta_step:.4f})'
        self.ax.set_title(self.title)
        self.fig.canvas.manager.set_window_title(f"P={self.primes}")

        self.ax.set_xticks(np.arange(n_trees))
        self.ax.set_xticklabels(tree_ids)
        # Remove duplicate legend entries
        handles, labels = self.ax.get_legend_handles_labels()
        unique = dict(zip(labels, handles))
        self.ax.legend(unique.values(), unique.keys(), title="Prime p")
        # plt.tight_layout(pad=3.0)

    def update(self, val):
        beta = self.fig._slider.val

        for i, p in enumerate(self.primes):
            probs = self.df["phys_prob"][(p, beta)]
            bars = self.bar_containers[i]
            for rect, h in zip(bars, probs):
                rect.set_height(h)
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw_idle()

    def save_beta_animation(self, filename="beta_animation.mp4"):
        """
        Save an animation of the bar plot as beta varies.
        """
        def animate(i):
            # reindex i to start at beta = 0
            start = np.where(self.beta_vals == 0)
            i = (i + start) % len(self.beta_vals)
            for rect, h in zip(self.bar_container, self.df["phys_prob"][i]):
                rect.set_height(h)
            # ax.set_title(f'Physical Probability of Trees (β={beta_vals[i]:.3f})')
            self.fig._slider.set_val(self.beta_vals[i])
            return self.bar_container

        anim = FuncAnimation(
            self.fig, animate, frames=len(self.beta_vals), interval=100, blit=False, repeat=False
        )
        print(f"Saving animation to {filename}...")
        anim.save(filename, writer='ffmpeg')
        print(f"Animation saved to {filename}")
