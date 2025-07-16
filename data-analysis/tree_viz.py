from binarytree import tree
from utils import query
import ast
import networkx as nx
import pygraphviz as pgv
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from random import randint
from typing import List

N = 4

trees = query(N, [2], '..').loc[2]
trees["branches"] = trees["branches"].apply(ast.literal_eval)
trees["degrees"] = trees["degrees"].apply(ast.literal_eval)

trees.index = range(1, trees.index.size+1)

# i_min = trees.index.min()
# i_max = trees.index.max()
# idxs = [randint(i_min, i_max) for _ in range(3)]
# trees = trees.loc[idxs]
# trees = trees.loc[[9, 12,16]]


def branches_to_prufer_seq(N: int, branches: List[int]) -> List[int]:
    node_len = len(branches) + N
    prufer_len = node_len - 2
    prufer_seq = [N]*prufer_len

    if len(branches) >= 2:
        # sets the branch index of all the leaves
        for i, J in enumerate(branches):
            for j, bit in enumerate(reversed(format(J, f'0{N}b'))):
                if bit == "1":
                    prufer_seq[j] = i

        # sets parent index of every branch except first 2
        for i, J in enumerate(reversed(branches[2:])):
            for j, branch in enumerate(branches):
                # print(J, branch, prufer_seq)
                if J & branch and J < branch:
                    prufer_seq[i + N] = j

        #turns sequence of branch indecies into node labels (since leaves are nodes 0 to N-1)
        prufer_seq = [node_len - i - 1 for i in prufer_seq]

    return prufer_seq


def get_tree_pos(G: pgv.AGraph):
    # Extract node positions from AGraph
    pos = {}
    for n in G.nodes():
        p = n.attr['pos']
        if p:
            x, y = map(float, p.split(','))
            pos[int(n.get_name())] = (x, y)

    for n in G.nodes():
        leaves = ast.literal_eval(n.attr["leaves"]) if len(n.attr["leaves"]) else []
        leaves = [l-1 for l in leaves]
        if len(leaves):
            leave_x = [pos[l][0] for l in leaves]
            new_x = (max(leave_x)+min(leave_x))/2
            pos[int(n)] = (new_x, pos[int(n)][1])

    return pos

    


def label_set(branch: int, N: int):
    labels = []
    for i, bit in enumerate(reversed(format(branch, f"0{N}b"))):
        if bit == "1":
            labels.append(i+1)
    return labels

tree_img_dir = "./trees2/"

for i, tree in trees.iterrows():
    # filename = f"tree_{tree.name}"
    filename= "temp"
    imgpath = tree_img_dir + filename + ".png"
    print(imgpath)

    branches = tree["branches"]
    prufer_seq = branches_to_prufer_seq(N, branches)
    
    print(branches, ":", prufer_seq)

    T = nx.from_prufer_sequence(prufer_seq)
    for i, J in enumerate(reversed(branches)):
        T.nodes[N+i]["branch"] = str(J)
        
        T.nodes[N+i]["set"] = "\{" + ",".join([f"x_{i}" for i in label_set(J, N)]) + "\}"
        T.nodes[N+i]["leaves"] = label_set(J, N)

    root = max(list(T.nodes()))
    depth = max(nx.shortest_path_length(T, source=root).values())
    leave_ids = range(0, N)

    A: pgv.AGraph = nx.nx_agraph.to_agraph(T)
    A.add_subgraph(leave_ids, rank='same')
    A.layout(prog='dot', args='-Grank=BT')
    
    pos = get_tree_pos(A)

    # --- NetworkX drawing section ---
    fig, ax = plt.subplots(figsize=(4, 4))
    # plt.rc('text', usetex=True)

    # ax.set_aspect('equal')
    ax.axis('off')

    # Node styling
    node_labels = {}
    node_sizes = []
    node_colors = []
    node_fontsizes = []
    for n in T.nodes():
        if n in leave_ids:
            node_labels[n] = str(int(n)+1)
            node_sizes.append(300)
            node_colors.append('white')
            node_fontsizes.append(20)
        else:
            node_labels[n] = T.nodes[n]['set']
            node_sizes.append(0)
            node_colors.append('black')
            node_fontsizes.append(16)

    # Draw edges
    nx.draw_networkx_edges(T, pos, ax=ax, width=3)

    # Draw nodes
    nx.draw_networkx_nodes(
        T, pos, ax=ax,
        node_color=node_colors,
        node_size=node_sizes,
        # edgecolors='black',
        linewidths=1,
    )

    # Draw labels
    # colors = ["red", "orange", "brown",
    #           "teal", "blue", "magenta"]
    # color_i = 0
    for n in T.nodes():
        if n in leave_ids:
            ax.text(
                pos[n][0], pos[n][1],
                node_labels[n],
                # f"$x_{node_labels[n]}$",
                fontsize=node_fontsizes[n],
                ha='center',
                va='top',
                # color=colors[color_i]
            )
        # else:
        #     t = ax.text(
        #         apos[n][0],
        #         apos[n][1],
        #         f"${node_labels[n]}$",
        #         va='center',
        #         ha='center',
        #         fontsize=node_fontsizes[n]
        #     )
        #     t.set_bbox(dict(facecolor='white'))
        
        # color_i += 1

    # Draw title
    plt.title(f"{tree.name}", fontsize=30, fontweight="bold", loc='left')

    plt.tight_layout(pad=1)
    plt.savefig(imgpath, pad_inches=0, dpi=300)
    plt.show()
