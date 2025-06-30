import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from utils import interaction_energy, polyfit
from collections import defaultdict

k = 3
N = int(2*k)
q_i = [-1 if n % 2 else 1 for n in range(N)]
print(q_i)

energies = interaction_energy(q_i)
total_charge = sum(q_i)
print(energies)

branches = range(len(energies))
sizes = [bin(x).count("1") for x in branches]


# Group energies by size and calculate average for each size
inter_energies_dict: defaultdict[int, list] = defaultdict(list)
for size, energy in zip(sizes, energies):
    inter_energies_dict[size].append(energy)

size_avgs = {size: np.mean(vals) for size, vals in inter_energies_dict.items()}
size_sums = {size: np.sum(vals) for size, vals in inter_energies_dict.items()}

# for size, energies in size_to_energies.items():
#     sum_squared = 2*np.array(energies) + size
#     unique, counts = np.unique(sum_squared, return_counts=True)

sizes_sorted = sorted(size_sums.keys())
sums_sorted = [np.float32(size_sums[x]) for x in sizes_sorted]

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

for size, sn in sums_not_squared_dict.items():
    print(f"size: {size}, sum: {sum(sn)}, len: {len(sn)}, avg: {sum(sn)/len(sn)}\narr: {sn}")


print(sum_square_dict.keys())
for size, sums in sum_square_dict.items():
    if size != 0:
        print(f"sum_{{|J| = {size}}}(sum q_i^2) = {sum(sums)}")
        
        k = size - 1
        # --- final eq ---
        # total = (math.comb(N, k)*(N-k) - sum(sum_square_dict[k]))
        # print(f"{size} - {total}")

fig2, ax2 = plt.subplots()
ax2.bar(branches, sums_squared)

ax2.set_xlabel("Branch")
ax2.set_ylabel(r"${\left(\sum_{i\in J} q_i \right)}^2$",
               rotation=0, labelpad=20)
ax2.set_title(f"Branches and their squared sums (N={N})")


def T(n, k):
    if k == 0:
        return 0
    return (n+1)*math.comb(n-1, k-1)


sqfig, sqax = plt.subplots()
sqax.set_xlabel("Branch size and squared sums of J")
sqax.set_ylabel("Frequency")
sqax.set_title("Size of J and frequency of squared sum")

sizes_sorted = sorted(sum_square_dict.keys())
bar_positions = []
bar_heights = []
bar_colors = []
u_labels = []
group_centers = []

color_map = plt.cm.get_cmap('tab10', len(sizes_sorted))
pos = 0

for idx, size in enumerate(sizes_sorted):
    vals = sum_square_dict[size]
    unique, counts = np.unique(vals, return_counts=True)

    group_start = pos
    for u, c in zip(unique, counts):
        bar_positions.append(pos)
        bar_heights.append(c)
        u_labels.append(str(u))
        bar_colors.append(color_map(idx))
        pos += 1
    group_end = pos - 1
    group_centers.append((group_start + group_end) / 2)
    pos += 0.5  # Gap between size groups

# Draw the bars
sqax.bar(bar_positions, bar_heights, color=bar_colors)

# Add squared sum labels just above the xtick labels (below the chart)
# For each group, place the squared sum labels centered under each bar
ymin, ymax = sqax.get_ylim()
label_y = ymin - 0.01 * (ymax - ymin)  # slightly below the x-axis

# Add unique ID labels above bars
for x, h, u in zip(bar_positions, bar_heights, u_labels):
    sqax.text(x, h + 0.3, f"{h}", ha='center', va='bottom', fontsize=8)
    sqax.text(x, label_y, u, ha='center', va='top',
              fontsize=8, rotation=0, clip_on=False)


# One size label per group
sqax.set_xticks(group_centers)
sqax.tick_params(top=False, bottom=False)
sqax.set_xticklabels([f"{size}" for size in sizes_sorted])

# Shift tick labels down
for label in sqax.get_xticklabels():
    label.set_y(-0.02)

# Add legend for sizes
# legend_handles = [Patch(color=color_map(
#     idx), label=f"{size}") for idx, size in enumerate(sizes_sorted)]
# sqax.legend(handles=legend_handles, title="Branch size")

# for size, inters in inter_energies_dict.items():
#     print(f"---- {size} ----")
#     unique, counts = np.unique(
#         np.array(sum_square_dict[size]), return_counts=True)
#     # if (size != 0):
#     # print(size, "- t(n,size):", T(N-1, size-1), "sum:", sum(energies), "")
#     print("avg (sum q_i)^2:", (size*(N-size))/(N-1))
#     for val, count in zip(unique, counts):
#         print(f"{val} appeared {count} times")
# print("sum squareds")
# for size, s in sum_square_dict.items():
#     print("size: ", size)
#     print(size/N)
#     print("binom: ", math.comb(N-1, size-1))
#     print(sum(s))


# ------------ plot interactino energies ------------
fig, ax = plt.subplots()
ax.set_xlabel('Branch size')
ax.set_ylabel(r'$\overline{e_{J}}$')
ax.set_title(f'Average interaction energies for {N} particles')
bar_container = ax.bar(branches, energies)
# Add average energy line
avg_energy = np.mean(energies)
ax.axhline(avg_energy, color='red', linestyle='--',
           label=f'Average = {avg_energy:.2f}')


# Plot average energy for each size
avg_vals = [size_avgs[s] for s in sizes_sorted]
ax.scatter(
    # x positions (first occurrence of each size)
    [branches[sizes.index(s)] for s in sizes_sorted],
    avg_vals,
    color='green',
    label='Average by size'
)

# Fit to a quadratic line
sizes_numeric = np.array(sizes_sorted)
avg_vals_numeric = np.array(avg_vals)

results = polyfit(sizes_numeric, avg_vals_numeric, 2)
coeffs = results["polynomial"]
quad_fit = np.polyval(coeffs, sizes_numeric)

ax.plot(
    [branches[sizes.index(s)] for s in sizes_sorted],
    quad_fit,
    color='blue',
    linestyle='--',
    label=f'Quadratic fit\n(coeffs: {coeffs.round(6)}, R^2 = {results["determination"]})'
)

ax.legend()
plt.xticks(rotation=90)

plt.show()
