from utils import interaction_energy
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

set_charges = [1, 1, -1, -1]
energies = interaction_energy(set_charges)


print("e_Js = ", energies)
print("----")

sizes = [J.bit_count() for J in range(len(energies))]

df_e = pd.DataFrame({
    # "index": range(len(energies)),
    "sizes": sizes,
    "energies": energies
})

df_e["quant"] = (df_e["sizes"]-1)/df_e["energies"].abs()

# print(energies[21])
# print(df_e["quant"][[21,42]])

# df_e.plot.scatter(
#     x=df_e.index,
#     # x='index',
#     y="energies",
#     s="sizes"
# )

fig,ax = plt.subplots()

df_filtered = df_e.loc[(df_e["energies"] < 0)]

scatter = ax.scatter(
    x=df_filtered.index,
    y=(df_filtered["sizes"]-1)/df_filtered["energies"].abs(),
    s=8*(df_filtered["sizes"]**2),
    c=df_filtered["sizes"],
    cmap="gist_rainbow_r"
)

ax.set_xlabel(r"$J\subseteq I$")
ax.set_ylabel(r"$\frac{|J|-1}{|e_J|}$", rotation=0, labelpad=20)
ax.set_title(f"Quantity to minimize for each J subset of I\n(q={set_charges})")

handles, labels = scatter.legend_elements(prop="colors")
max_size = df_filtered["sizes"].max()
min_size = df_filtered["sizes"].min()

legend2 = ax.legend(handles, range(min_size, max_size+1), title="Size of J")

ax.set_xticks(range(len(energies)))
ax.set_xticklabels(range(len(energies)))

plt.show()
enum_energies = [(J.bit_count(), e) for J, e in enumerate(energies) if e < 0]
for tup in np.array(enum_energies).tolist():
    print(tup)
# print("----")
sig_minus_list = [(size-1)/abs(e) for size, e in enum_energies]
print(sig_minus_list)
print([round(num, 3) for num in np.array(sig_minus_list).tolist()])

