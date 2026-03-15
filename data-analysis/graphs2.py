import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from utils import interaction_energy, polyfit
from collections import defaultdict
from random import randint
from fractions import Fraction
from typing import List


# q_i = [1 if randint(0, 1) else -1 for n in range(enn)]
q_i = [1,1,1,1,-1,-1,-1]
M_plus = max(q_i)
M_minus = min(q_i)
enn = len(q_i)
print(q_i, sum(q_i))


for N in range(enn, enn+1):
    q_iN = q_i[:N]
    P = q_iN.count(1)
    E = q_iN.count(-1)

    # q_i = [-1 if n % 2 else 1 for n in range(N)]

    energies = interaction_energy(q_iN)
    total_charge = sum(q_iN)
    # print(energies)

    branches = range(len(energies))
    sizes = [x.bit_count() for x in branches]

    # odd = N % 2
    # binom = [odd * math.comb(N-1, k-1) for k in range(1, N+1)]
    # print(binom)


    # Group energies by size and calculate average for each size
    inter_energies_dict: defaultdict[int, list] = defaultdict(list)
    for size, energy in zip(sizes, energies):
        inter_energies_dict[size].append(energy)

    sums_squared = []
    sums_not_squared = []
    for J in branches:
        sum1 = 0
        for i, charge in enumerate(q_i):
            sum1 += ((bool(J & (1 << i))) * charge)
        sums_squared.append(sum1**2)
        sums_not_squared.append(sum1)

    sum_square_dict: defaultdict[int, list] = defaultdict(list)
    sums_not_squared_dict: defaultdict[int, list] = defaultdict(list)
    for size, s, sn in zip(sizes, sums_squared, sums_not_squared):
        sum_square_dict[size].append(s)
        sums_not_squared_dict[size].append(sn)

    sums_not_squared_per_size = [sum(sn) for sn in sums_not_squared_dict.values()]
    sums_squared_per_size = [sum(s) for s in sum_square_dict.values()]

    # for k in range(N):
    #     joe_and_ians_eq.append(sum([math.comb(n_plus, j)*math.comb(n_minus, k-j)*(2*j-k) for j in range(k)]))
    # print(f"{N} (add: {q_iN[-1]}, sum: {sum(q_iN)}) - {sums_not_squared_per_size}")
    fractions: List[Fraction] = []
    max_denom = 0
    for k,total in enumerate(sums_squared_per_size):
        num = (total/math.comb(N, k))
        frac = Fraction.from_float(num).limit_denominator()
        if (frac.denominator >= max_denom):
            max_denom = frac.denominator
        fractions.append(frac)

    # print("max: ", max_denom)
    guess_vals = []
    for k,frac in enumerate(fractions):
        ratio = max_denom/frac.denominator
        f = frac.as_integer_ratio()
        print(f"{N} (P: {P}, E: {E}, k: {k})")
        # print(f"{N} (P: {P}, E: {E}, k: {k}) {int(f[0]*ratio)}/{int(f[1]*ratio)}")

        guess = (((P-E)**2 - N)*(k**2) + 4*P*E*k)/(N*(N-1))
        print(f"actual: {float(frac)} ({frac})\n guess: {guess} ({Fraction(guess).limit_denominator()})")
        guess_vals.append(guess)

    print(f"actual: {fractions}")
    print("\n")
    # print(f"{N} (P: {P}, E: {E}) - {sums_squared_per_size}")

    # --- Line plot of frac (float) vs k ---
    ks = list(range(len(fractions)))
    frac_floats = [float(f) for f in fractions]
    plt.figure()
    plt.plot(ks, frac_floats, marker='o', label='actual')
    plt.plot(ks, guess_vals, marker='x', linestyle='--', label='guess')
    plt.xlabel("k")
    plt.ylabel("sum(sq)/binom(N,k)")
    plt.title(f"Fraction values for P={P}, E={E}")
    plt.grid(True)
    plt.legend()
    plt.show()



