from more_itertools import set_partitions
import pandas as pd
import numpy as np
from utils import falling_factorial, interaction_energy

# primes to compute for
primes = [2,3,5,7,11]
charges_arr = [[1, 1, -1, -1]]#, [5, 2, 1, -3], [-1, -2, -2, -3]]
# beta_step_arr = [0.02, 0.0003, 0.05]
# charges_str = input("charges (comma seperated): ")
# charges_arr = [[int(q) for q in charges_str.split(',')]]
charges = charges_arr[0]
q_max = max(charges)
q_min = min(charges)

# calculates interaction energies and sigmas
energies = interaction_energy(charges)
sig_minus = 1/abs(q_max*q_min)
if q_max*q_min >= 0:
    sig_minus = 2
sig_plus = -step
# caluclates array of values with given beta_step between (-\sigma^+, \sigma^-)
beta_vals = np.arange(sig_plus, sig_minus, step)
# excludes endpoints
beta_vals = beta_vals[1:]




def Z_I_partition_based(charges, p):
    df = pd.DataFrame()
    N = len(charges)

    I = np.arange(N)
    partitions = []
    # get every proper partition of I
    for i in range(2, N+1):
        partitions.extend(set_partitions(I, i))
    
    df["partition"] = partitions

    def prod(row):
        lambba = row["partition"]
        prod = falling_factorial(p, len(lambba)) * 

    df["summand"] = df["partition"].apply()

    return df


df = Z_I_partition_based(charges_arr[0], primes[2])

print(df)


df_arr = []

# Computes Z_I(\beta), Expected value, Variance, and P_tree(p, \beta) for all betas
for p in primes:
    for beta in beta_vals:
        # computes probability for all trees
        terms = trees.apply(lambda row: term(
            row["branches"], row["degrees"], p, energies, beta), axis=1)
        total = terms.sum()
        probs = terms/total

        # computes weights and double weights for expected value and variance
        weights = trees.apply(lambda row: weight(
            row["branches"], p, energies, beta), axis=1)
        double_weights = trees.apply(lambda row: double_weight(
            row["branches"], p, energies, beta), axis=1)

        df_beta = pd.DataFrame({
            'prime': p,
            'beta': beta,
            'tree_id': trees.index,
            'term': terms,
            'phys_prob': probs,
            'weight': weights,
            'double_weight': double_weights,
        })

        df_arr.append(df_beta)

# Concatenate all per-beta DataFrames, set index as (beta, tree_id)
return pd.concat(df_arr).set_index(['prime', 'beta', 'tree_id'])