import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from utils import interaction_energy, polyfit
from collections import defaultdict
from random import randint

enn = 10
q_i = [1 if randint(0, 1) else -1 for n in range(enn)]
print(q_i)
for N in range(1, enn):
    q_iN = q_i[:N]
    # q_i = [-1 if n % 2 else 1 for n in range(N)]

    energies = interaction_energy(q_iN)
    total_charge = sum(q_iN)
    # print(energies)

    branches = range(len(energies))
    sizes = [bin(x).count("1") for x in branches]

    # odd = N % 2
    # binom = [odd * math.comb(N-1, k-1) for k in range(1, N+1)]
    # print(binom)


    # Group energies by size and calculate average for each size
    inter_energies_dict: defaultdict[int, list] = defaultdict(list)
    for size, energy in zip(sizes, energies):
        inter_energies_dict[size].append(energy)

    sums_not_squared = []
    for J in branches:
        sum1 = 0
        for i, charge in enumerate(q_iN):
            sum1 += ((bool(J & (1 << i))) * charge)
        sums_not_squared.append(sum1)

    sums_not_squared_dict: defaultdict[int, list] = defaultdict(list)
    for size, sn in zip(sizes, sums_not_squared):
        sums_not_squared_dict[size].append(sn)

    sums_not_squared_per_size = [sum(sn) for sn in sums_not_squared_dict.values()]
    joe_and_ians_eq = []
    n_plus = q_iN.count(1)
    n_minus = q_iN.count(-1)

    for k in range(N):
        joe_and_ians_eq.append(sum([math.comb(n_plus, j)*math.comb(n_minus, k-j)*(2*j-k) for j in range(k)]))
    print(f"{N} (add: {q_iN[-1]}, sum: {sum(q_iN)}) - {sums_not_squared_per_size}")

    print(f"The fun side: {joe_and_ians_eq}")


