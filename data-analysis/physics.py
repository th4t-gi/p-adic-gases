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

# primes = [7] # primes to compute probabilities for
primes = [2,3,5]
# input("what prime do you want to see")
beta_step = 0.01
set_charges = [1,1,-1,-1]
# set_charges.sort()
n = len(set_charges)
m_plus = max(set_charges)
m_minus = min(set_charges)    

# calculates interaction energies and sigmas
energies = interaction_energy(set_charges)
sig_minus = 1/abs(m_plus*m_minus)
if m_plus*m_minus >= 0:
    sig_minus = 5
sig_plus = 0 + beta_step
# caluclates array of values with given beta_step between (-\sigma^+, \sigma^-)
beta_vals = np.arange(-sig_plus, sig_minus, beta_step)
# excludes endpoints
beta_vals = beta_vals[1:]

print("e_Js = ", energies)
print("----")

sizes = [bin(J).count("1") for J in range(len(energies))]

# df_e = pd.DataFrame({
#     # "index": range(len(energies)),
#     "sizes": sizes,
#     "energies": energies
# })

# df_e["quant"] = (df_e["sizes"]-1)/df_e["energies"].abs()

# # print(energies[21])
# # print(df_e["quant"][[21,42]])

# # df_e.plot.scatter(
# #     x=df_e.index,
# #     # x='index',
# #     y="energies",
# #     s="sizes"
# # )

# fig,ax = plt.subplots()

# df_filtered = df_e.loc[(df_e["energies"] < 0)]

# scatter = ax.scatter(
#     x=df_filtered.index,
#     y=(df_filtered["sizes"]-1)/df_filtered["energies"].abs(),
#     s=8*(df_filtered["sizes"]**2),
#     c=df_filtered["sizes"],
#     cmap="gist_rainbow_r"
# )

# ax.set_xlabel(r"$J\subseteq I$")
# ax.set_ylabel(r"$\frac{|J|-1}{|e_J|}$", rotation=0, labelpad=20)
# ax.set_title(f"Quantity to minimize for each J subset of I\n(q={set_charges})")

# handles, labels = scatter.legend_elements(prop="colors")
# max_size = df_filtered["sizes"].max()
# min_size = df_filtered["sizes"].min()

# legend2 = ax.legend(handles, range(min_size, max_size+1), title="Size of J")

# ax.set_xticks(range(len(energies)))``
# ax.set_xticklabels(range(len(energies)))

# plt.show()
# enum_energies = [(bin(J).count("1"), e) for J, e in enumerate(energies) if e < 0]
# for tup in np.array(enum_energies).tolist():
#     print(tup)
# # print("----")
# sig_minus_list = [(size-1)/abs(e) for size, e in enum_energies]
# print(sig_minus_list)
# print([round(num, 3) for num in np.array(sig_minus_list).tolist()])






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

def canonical_partition_plt(df: pd.DataFrame):
    Zfig, Zax = plt.subplots()

    for p in df.index.get_level_values("prime").unique():
        Z_i = []
        for beta in beta_vals:
            total = df["term"][(p, beta)].sum()

            # calculates Z_I(\beta)
            Z_i_beta = (p ** (energies[-1]*beta)) * total
            Z_i.append(Z_i_beta)

        Zax.plot(beta_vals, Z_i, label=f"p={p}")

    Zax.set_xlabel(r'$\beta$')
    Zax.set_ylabel(r'$Z_I(\beta)$')
    Zax.set_title(
        f'Partition Function $Z_I(\\beta)$\n(N={n}, q={set_charges}, step={beta_step:.4f})')
    Zfig.canvas.manager.set_window_title(f"Z_I(β)")
    Zax.set_yscale("log")
    Zax.legend(title="Prime p")

    return Zfig

def expected_val_plt(df: pd.DataFrame):
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

def variance_plt(df: pd.DataFrame):
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


trees = query(n, primes, "..")
trees["branches"] = trees["branches"].apply(ast.literal_eval)
trees["degrees"] = trees["degrees"].apply(ast.literal_eval)

df = compute(set_charges, primes, beta_vals, trees)

tree_ids = df.index.get_level_values('tree_id').unique()
df.index = df.index.set_levels([range(1,len(tree_ids)+1) if name == 'tree_id' else df.index.levels[i]
                          for i, name in enumerate(df.index.names)])

print(len(df))
print(df.head())
# Zfig = canonical_partition_plt(df)
# Efig = expected_val_plt(df)
# Vfig = variance_plt(df)

prob_figs: List[TreePlt] = []
prob_plt = TreePlt(df, primes, set_charges, beta_step, subplots=True)
prob_figs.append(prob_plt)
prob_plt.plot()

# for p in primes:
#     print(f"------------{p}------------")

#     prob_plt.plot(p)

plt.show()

prob_plt.fig.savefig("prob1.png", bbox_inches='tight', dpi=300)

for prob in prob_figs:
     # Save animation after showing interactive plot
    # save = input(f"Do you want to save \"{prob}\"? (y/n) ")
    save = "n"
    if (save.lower() == "y"):
        prob.save_beta_animation()

