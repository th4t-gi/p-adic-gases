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
primes = [2,3,5,7,11,13]
# input("what prime do you want to see")
beta_step = 0.01
set_charges = [1, -1, 1, -1]
n = len(set_charges)
m = max(set_charges)
k = min(set_charges)

# calculates interaction energies and sigmas
energies = interaction_energy(set_charges)
sig_minus = 1/(m*(-k))
sig_plus = 0.1
# caluclates array of values with given beta_step between (-\sigma^+, \sigma^-)
beta_vals = np.arange(-sig_plus, sig_minus, beta_step)
# excludes endpoints
beta_vals = beta_vals[1:]

# for b in beta_vals:
#     print(b)
# print("e_Js = ", energies)
# print("----")
# enum_energies = [(J, e) for J, e in enumerate(energies) if e < 0]
# for tup in np.array(enum_energies).tolist():
#     print(tup)
# # print("----")
# sig_minus_list = [(bin(J).count("1") - 1)/abs(e) for J, e in enum_energies]
# print(min(sig_minus_list))
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


prob_figs: List[TreePlt] = []

trees = query(n, primes, "..")
trees["branches"] = trees["branches"].apply(ast.literal_eval)
trees["degrees"] = trees["degrees"].apply(ast.literal_eval)

df = compute(set_charges, primes, beta_vals, trees)
print(len(df))

Zfig = canonical_partition_plt(df)
Efig = expected_val_plt(df)
Vfig = variance_plt(df)

prob_plt = TreePlt(df, set_charges, beta_step, sig_plus, sig_minus, beta_vals, split=False)

for p in primes:
    print(f"------------{p}------------")

    # do some formatting as arrays
    prob_plt.plot(p)

prob_plt2 = TreePlt(df, set_charges, beta_step, sig_plus,
                   sig_minus, beta_vals, split=False)
prob_plt2.plot(2)
prob_plt2.plot(3)
# for prob in prob_figs:
#      # Save animation after showing interactive plot
#     # save = input("Do you want to save this as a .mp4? (y/n) ")
#     save = "n"
#     if (save.lower() == "y"):
#         prob.save_beta_animation(
#             filename=f'../animations/prob_p{p}_n{n}_q{set_charges}_b{beta_step}.mp4')


plt.show()
