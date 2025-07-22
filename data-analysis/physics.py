from typing import List

import pandas as pd
import numpy as np
import ast
import math
from utils import interaction_energy, term, weight, query, double_weight
from tree_prob import TreePlt
import matplotlib.pyplot as plt
import matplotlib.widgets as mwidgets
from matplotlib.animation import FuncAnimation

def compute(charges: List[int], primes: List[int], beta_vals, trees: pd.DataFrame):
    energies = interaction_energy(charges)
    df_arr = []

    # Computes Z_I(\beta), Expected value, Variance, and P_tree(p, \beta) for all betas
    for p in primes:
        trees_p = trees.loc[p]
        for beta in beta_vals:
            # computes probability for all trees
            terms = trees_p.apply(lambda row: term(
                row["branches"], row["degrees"], p, energies, beta), axis=1)
            total = terms.sum()
            probs = terms/total

            # computes weights and double weights for expected value and variance
            weights = trees_p.apply(lambda row: weight(
                row["branches"], p, energies, beta), axis=1)
            double_weights = trees_p.apply(lambda row: double_weight(
                row["branches"], p, energies, beta), axis=1)

            df_beta = pd.DataFrame({
                'prime': p,
                'beta': beta,
                'tree_id': trees_p.index,
                'term': terms,
                'phys_prob': probs,
                'weight': weights,
                'double_weight': double_weights,
            })

            df_arr.append(df_beta)

    # Concatenate all per-beta DataFrames, set index as (beta, tree_id)
    return pd.concat(df_arr).set_index(['prime', 'beta', 'tree_id'])

def canonical_partition_plt(df: pd.DataFrame, fig = None, ax = None):
    if (fig and not ax) or (ax and not fig):
        raise ValueError("Must have both figure and axes or neither.")
    
    Zfig, Zax = plt.subplots(figsize=(8, 3)) if not fig and not ax else (fig, ax)

    for p in df.index.get_level_values("prime").unique():
        Z_i = []
        for beta in beta_vals:
            total = df["term"][(p, beta)].sum()

            # calculates Z_I(\beta)
            Z_i_beta = (p ** (energies[-1]*beta)) * total
            Z_i.append(Z_i_beta)

        Zax.plot(beta_vals, Z_i, label=p)

    # Zax.set_xlabel(r'\boldmath$\beta$', fontsize=10)
    # Zax.set_ylabel(r'\boldmath$Z_I(\beta)$', fontsize=14,
                #    rotation=0, horizontalalignment="right")
    # Zax.set_title(f'$\\mathcal{{Z}}_I(\\beta)$ for $q_I=({','.join(map(str, set_charges))})$', fontsize=14)
    # Zax.set_yscale("log")
    # Zax.legend(title="Prime p")

    return Zfig

def expected_val_plt(df: pd.DataFrame, set_charges, beta_step):
    Efig, Eax = plt.subplots()

    for p in df.index.get_level_values("prime").unique():
        expected = []
        for beta in beta_vals:
            probs = df["phys_prob"][(p, beta)]
            weights = df["weight"][(p, beta)]

            # calculates <E>
            expected_beta = math.log(p) * (-energies[-1] + sum(probs*weights))
            expected.append(expected_beta)

        Eax.plot(beta_vals, expected, label=f"p={p}")

    Eax.set_xlabel(r'$\beta$')
    Eax.set_ylabel(r'${\langle E \rangle}_\beta$')
    Eax.set_title(
        f'Expected value vs $\\beta$\n(N={n}, q={set_charges}, step={beta_step:.4f})')
    Efig.canvas.manager.set_window_title("<E>_β")
    Eax.set_yscale("symlog")
    Eax.legend(title="Prime p")

    return Efig

def variance_plt(df: pd.DataFrame, set_charges, beta_step):
    Vfig, Vax = plt.subplots()

    for p in df.index.get_level_values("prime").unique():
        variance = []
        for beta in beta_vals:
            probs = df["phys_prob"][(p,beta)]
            weights = df["weight"][(p, beta)]
            double_weights = df["double_weight"][(p, beta)]

            # calculates <<E>^2>
            variance_beta = (math.log(p)**2) * (sum(double_weights * probs) +
                                                sum((weights**2)*probs) -
                                                (sum(weights*probs)**2))
            variance.append(variance_beta)

        Vax.plot(beta_vals, variance, label=f"p={p}")

    Vax.set_xlabel(r'$\beta$')
    Vax.set_ylabel(r'${\langle{\langle E \rangle}^2\rangle}_\beta$')
    Vax.set_title(
        f'Variance of expected value vs $\\beta$\n(N={n}, q={set_charges}, step={beta_step:.4f})')
    Vfig.canvas.manager.set_window_title("<<E>^2>")
    # Vax.set_yscale("log")
    Vax.legend(title="Prime p")

    return Vfig

###############################################################

plt.rcParams.update({
    "text.usetex": True,
    "text.latex.preamble": r"""\usepackage{lmodern}\usepackage{amsfonts}\renewcommand{\familydefault}{\sfdefault}"""
})

# primes to compute for
primes = [2, 3, 5, 7, 11]
# charges_arr = [[1, 1, -1, -1], [5, 2, 1, -3], [-1, -2, -2, -3]]
# beta_step_arr = [0.02, 0.0003, 0.05]
charges_arr = [[5, 2, 1, -3]]
beta_step_arr = [0.0003]
num_plots = len(charges_arr)
# num_plots = 1

prob_figs: List[TreePlt] = []
# Zfig, Zaxs = plt.subplots(figsize=(5,8), nrows=num_plots)
Zfig, Zaxs = plt.subplots(figsize=(6, 2.5), nrows=num_plots)
# Zfig = canonical_partition_plt(df)
# Efig = expected_val_plt(df)
# Vfig = variance_plt(df)
if num_plots == 1:
    Zaxs = [Zaxs]

print(enumerate(zip(beta_step_arr, charges_arr)))
for i, (step, charges) in enumerate(zip(beta_step_arr, charges_arr)):
    n = len(charges)
    q_max = max(charges)
    q_min = min(charges)

    # calculates interaction energies and sigmas
    energies = interaction_energy(charges)
    sig_minus = 1/abs(q_max*q_min)
    if q_max*q_min >= 0:
        sig_minus = 2
    sig_plus = 0 + step
    # caluclates array of values with given beta_step between (-\sigma^+, \sigma^-)
    beta_vals = np.arange(-sig_plus, sig_minus, step)
    # excludes endpoints
    beta_vals = beta_vals[1:]

    trees = query(n, primes, "..")
    trees["branches"] = trees["branches"].apply(ast.literal_eval)
    trees["degrees"] = trees["degrees"].apply(ast.literal_eval)

    df = compute(charges, primes, beta_vals, trees)

    tree_ids = df.index.get_level_values('tree_id').unique()
    df.index = df.index.set_levels([range(1,len(tree_ids)+1) if name == 'tree_id' else df.index.levels[i]
                            for i, name in enumerate(df.index.names)])

    print(len(df))
    print(df.head(3))

    prob_plt = TreePlt(df, primes, charges, step, subplots=True)
    prob_figs.append(prob_plt)
    prob_plt.plot()

    print(f"charges {charges} have sig_minus {sig_minus}")

    # ------------ Plotting ------------
    ax = Zaxs[i]
    canonical_partition_plt(df, Zfig, ax)

    ax.set_title(
        r"$\mathcal{Z}_4(\beta)$ for $(\mathfrak{q}_1, \mathfrak{q}_2, \mathfrak{q}_3, \mathfrak{q}_4)=(" +
        ', '.join(map(str, charges)) +
        r")$",
        fontsize=14,
        pad=10
    )
    # if i == 0: 
    #     ax.legend(title="Prime p")
    #     patches, labels = ax.get_legend_handles_labels()
    #     # Get rid of the legend on the first plot, so it is only drawn on the separate figure
    #     ax.get_legend().remove()
    #     figlegend.legend(patches, labels, title="Prime p")
    #     figlegend.savefig('legend.png', dpi=300)

    if q_min < 0 and q_max > 0:
        ax.set_yscale("log")

        ax.axvline(
            x=sig_minus,
            linestyle="--",
            color="black",
            label=r"$\beta_c$"
        )

        # ax.set_xticklabels(current_labels)
        ax.annotate(
            r"\boldmath$\beta_c$",
            xy=(sig_minus, 0.3),
            xycoords=('data', 'axes fraction'),
            # xytext=(0),
            # textcoords='offset points',
            ha='center',
            va='top',
            fontsize=12,
            bbox=dict(
                # boxstyle="pad=0.3",
                facecolor="white",
                edgecolor="white"
            )
            # arrowprops=dict(arrowstyle='-', color='black')  # optional arrow
        )
    else:
        pass

    Zfig.canvas.manager.set_window_title(f"Z_I_beta_q{charges}")
    Zfig.supxlabel(r'\boldmath$\beta$', fontsize=10)
    width, height = Zfig.get_size_inches()
    print(0.96, height)
    Zfig.subplots_adjust(left=0.08, bottom=0.15, right=0.97, top=0.87, hspace=0.4)



path = f"../../poster/{Zfig.canvas.manager.get_window_title()}.png"
Zfig.savefig(path, dpi=300)
# prob_plt.fig.savefig("prob1.png", bbox_inches='tight', dpi=300)

plt.show()

for prob in prob_figs:
     # Save animation after showing interactive plot
    # save = input(f"Do you want to save \"{prob}\"? (y/n) ")
    save = "n"
    if (save.lower() == "y"):
        prob.save_beta_animation()

