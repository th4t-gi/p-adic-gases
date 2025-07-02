from typing import List

import pandas as pd
import numpy as np
import ast
import math
from utils import interaction_energy, term, weight, query
import matplotlib.pyplot as plt
import matplotlib.widgets as mwidgets
from matplotlib.animation import FuncAnimation

# primes = [7] # primes to compute probabilities for
primes = [2,3,5,7,11,13]
# input("what prime do you want to see")
beta_resolution = 1000 # resolution (number of points, so 1 more than the number of gaps)
set_charges = [1,-1,1,-1]
n = len(set_charges)
m = max([abs(q) for q in set_charges])

# calculates interaction energies and sigmas 
energies = interaction_energy(set_charges)
sig_plus = 0.1
sig_minus = 2/(m+1)
#caluclates array of values with given beta_resolution between (-\sigma^+, \sigma^-)
beta_vals, beta_step = np.linspace(-sig_plus, sig_minus, beta_resolution + 1, retstep=True)
#excludes endpoints
beta_vals = beta_vals[1:-1]

# print(len(beta_vals))
# beta_vals = [val for ]


prob_figs = []
Zfig, Zax = plt.subplots()
Zax.set_xlabel(r'$\beta$')
Zax.set_ylabel(r'$Z_I(\beta)$')
Zax.set_title(f'Partition Function $Z_I(\\beta)$\n(N={n}, q={set_charges}, step={beta_step:.4f})')
Zfig.canvas.manager.set_window_title(f"Z_I(β)")

Efig, Eax = plt.subplots()
Eax.set_xlabel(r'$\beta$')
Eax.set_ylabel(r'${\langle E \rangle}_\beta$')
Eax.set_title(f'Expected value vs $\\beta$\n(N={n}, q={set_charges}, step={beta_step:.4f})')
Efig.canvas.manager.set_window_title("<E>_β")
Eax.set_yscale("symlog")


for p in primes:
    df = query(n, p, "..")

    # do some formatting as arrays
    df["branches"] = df["branches"].apply(ast.literal_eval)
    df["degrees"] = df["degrees"].apply(ast.literal_eval)
    
    # initializes things to graph
    Z_i = []
    expected = []
    df_arr: List[pd.DataFrame] = []
    
    # Computes Z_I(\beta), Expected value, and P_tree(p, \beta) for all betas
    for i, beta in enumerate(beta_vals):

        df_beta = pd.DataFrame({
            'tree_id': df['id'],
            'terms': 0.0,
            'phys_prob': 0
        })
        
        # Computes product value for each tree and stores in df_beta
        df_beta["terms"] = df.apply(lambda row : term(row["branches"], row["degrees"], p, energies, beta), axis=1)
        #calculates sum and Z_I(\beta)
        total = sum(df_beta["terms"])
        Z_i_beta = (p ** (energies[-1]*beta)) * total
        Z_i.append(Z_i_beta)

        #computes probability for all trees
        df_beta['phys_prob'] = df_beta['terms']/total
        
        #computes expected value
        weights = df.apply(lambda row : weight(row["branches"], p, energies, beta), axis=1)
        expected_beta = math.log(p) * (-energies[-1] + sum(df_beta["phys_prob"]*weights))
        expected.append(expected_beta)

        df_arr.append(df_beta)
        
        # print(f"beta: {beta}, Z_I = {Z_i_beta}\n", df_beta.head(), "\n--------\n")
    
    # Set up probability plot with slider
    fig, ax = plt.subplots(figsize=(7, 4.5))
    plt.subplots_adjust(bottom=0.4)
    ax.set_xlabel('Tree ID (row index)')
    ax.set_ylabel('Probability')
    ax.set_title(f'Physical Probability of Trees\n(N={n}, q={set_charges}, p={p}, step={beta_step:.4f})')
    fig.canvas.manager.set_window_title(f"P={p}")
    # ax.set_ybound(upper=1.0)
    ax.set_ylim(top=0.5)
    # ax.set_yscale("log")
    plt.xticks(rotation=90)
    
    start = 0
    # end = len(df_arr[0])
    end = 900
    
    # trees = [81, 83, 847, 849]

    # Create x-axis labels and probabilities array
    all_phys_probs = [frame["phys_prob"].values for frame in df_arr]
    xlabels = [f"{tid} ({idx})" for tid, idx in zip(df['id'][start:end], df.index[start:end])]
    bar_container = ax.bar(xlabels, all_phys_probs[0][start:end])

    # beta slider
    ax_slider = plt.axes([0.15, 0.02, 0.7, 0.02])# left,bottom,width,height
    beta_slider = mwidgets.Slider(
        ax=ax_slider,
        label=r'$\beta$',
        valmin=beta_vals[0],
        valmax=beta_vals[-1],
        valinit=0,
        valstep=beta_vals
    )

    def update(val):
        idx = np.where(beta_vals == beta_slider.val)[0][0]
        for rect, h in zip(bar_container, all_phys_probs[idx][start:end]):
            rect.set_height(h)
        fig.canvas.draw_idle()

    beta_slider.on_changed(update)
    update(0)

    def save_beta_animation(fig, ax, bar_container, all_phys_probs, beta_vals, filename="beta_animation.mp4"):
        """
        Save an animation of the bar plot as beta varies.
        """
        def animate(i):
            # reindex i to start at beta = 0
            i = (i + (len(beta_vals) // 2)) % len(beta_vals)
            for rect, h in zip(bar_container, all_phys_probs[i]):
                rect.set_height(h)
            # ax.set_title(f'Physical Probability of Trees (β={beta_vals[i]:.3f})')
            beta_slider.set_val(beta_vals[i])
            return bar_container

        anim = FuncAnimation(
            fig, animate, frames=len(beta_vals), interval=100, blit=False, repeat=False
        )
        print(f"Saving animation to {filename}...")
        anim.save(filename, writer='ffmpeg')
        print(f"Animation saved to {filename}")
        
    save = "n"
    if (save.lower() == "y"):
        save_beta_animation(fig, ax, bar_container, all_phys_probs, beta_vals, filename=f'animations/prob_p{p}_n{n}_b{beta_step}.mp4')

    plt.tight_layout(pad=3.0)
    prob_figs.append(fig)
    # Plot Z_i vs beta for this prime
    Zax.plot(beta_vals, Z_i, label=f"p={p}")
    Eax.plot(beta_vals, expected, label=f"p={p}")

Zax.legend(title="Prime p")
Eax.legend(title="Prime p")
Zax.set_yscale("log")


        
# for fig in figs:
#         # Save animation after showing interactive plot
#     # save = input("Do you want to save this as a .mp4? (y/n) ")
#     save = "n"
#     if (save.lower() == "y"):
#         save_beta_animation(fig, ax, bar_container, all_phys_probs, beta_vals, filename=f'animations/prob_p{p}_n{n}_b{beta_step}.mp4')

plt.show()

