from utils import query
import ast
import networkx as nx
import pygraphviz as pgv
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import os
import sys

from random import randint
from typing import List, Dict, Set
from numpy.testing import assert_array_equal
from collections import Counter
from itertools import permutations


trees = query(N, '../trees.db')
trees["branches"] = trees["branches"].apply(ast.literal_eval)
trees["degrees"] = trees["degrees"].apply(ast.literal_eval)

# trees.index = range(1, trees.index.size+1)

# i_min = trees.index.min()
# i_max = trees.index.max()
# idxs = [randint(i_min, i_max) for _ in range(3)]
# trees = trees.loc[idxs]
# trees = trees.loc[[2338,1593, 1444]]


def branches_to_prufer_seq(N: int, branches: List[int]) -> List[int]:
    # initialize things
    node_len = len(branches) + N
    prufer_len = node_len - 2
    prufer_seq = [0]*prufer_len

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

        # changes prufer sequences to be permutations of certain multisets
        # occurences = Counter(prufer_seq)
        # internal_nodes = range(1, len(branches))
        # cycle = {internal_nodes[i]: internal_nodes[(i + 1) % len(internal_nodes)] for i in range(len(internal_nodes))}
        # cycle[0] = 0

        # internal_degrees = [occurences[i] for i in internal_nodes]
        # def is_decreasing(l: List[int]) -> bool:
        #     return l == sorted(l, reverse=True)

        # while (not is_decreasing(internal_degrees)):
        #     prufer_seq = [cycle[x] for x in prufer_seq]
        #     occurences = Counter(prufer_seq)
        #     internal_degrees = [occurences[i] for i in internal_nodes]

    # turns sequence of branch indecies into node labels (1 indexed instead of 0 indexed)
    prufer_seq = [node_len - i - 1 for i in prufer_seq] 
    # prufer_seq.append(max(prufer_seq))
    # prufer_seq = [i+ 1 for i in prufer_seq] 
    # prufer_seq.append(1)

    return prufer_seq

def prufer_seq_to_tree(N: int, seq: List[int]) -> Dict[int, int]:
    # add implied final edge
    seq = seq.copy()
    seq.append(max(seq))
    # initialize things
    prufer_set = sorted(set(seq))
    branches = [0] * len(prufer_set)
    degrees = [0] * len(prufer_set)

    #for each branch, sum up all the leaves that connect to it
    for i,node in enumerate(prufer_set):
        for j,n in enumerate(seq[:N]):
            if node == n:
                branches[i] += 2**j
    
        degrees[i] = seq.count(node)
        
    
    # for the branches in prufer seq, find index of parent and add its sum to parent
    for j,n in enumerate(seq[N:]):
        i = prufer_set.index(n)
        branches[i] += branches[j]

    return dict(zip(branches[::-1], degrees[::-1]))

def prufer_seq_to_tree_inc(N: int, seq: List[int]) -> Dict[int, int]:
    # add implied final edge
    seq = seq.copy()
    seq.append(1)
    # initialize things
    prufer_max = max(seq)
    # prufer_set = sorted(set(seq))
    branches = [0] * prufer_max
    degrees = [0] * prufer_max

    #for each branch, sum up all the leaves that connect to it
    # for i,node in enumerate(prufer_set):
    for j,n in enumerate(seq[:N]):
        branches[n-1] += 2**j
        degrees[n-1] = seq.count(n)
        
    
    # for the branches in prufer seq, find index of parent and add its sum to parent
    for j,n in enumerate(seq[N:]):
        branches[n-1] += branches[prufer_max-j-1]

    return dict(zip(branches, degrees))

def prufer_seq_to_branches_inc(N: int, seq: List[int]) -> Dict[int, int]:
    # add implied final edge
    seq = seq.copy()
    seq.append(1)
    # initialize things
    prufer_max = max(seq)
    # prufer_set = sorted(set(seq))
    branches = [0] * prufer_max

    #for each branch, sum up all the leaves that connect to it
    # for i,node in enumerate(prufer_set):
    for i,n in enumerate(seq):
        if (i < N):
            branches[n-1] += 2**i
        else:
            # for the branches in prufer seq, find index of parent and add its sum to parent
            branches[n-1] += branches[prufer_max+N-i-1]

    return branches

def prufer_seq_to_branches(N: int, seq: List[int]) -> List[int]:
    # add implied final edge
    seq = seq.copy()
    seq.append(max(seq))
    # initialize things
    prufer_set = sorted(set(seq))
    branches = [0] * len(prufer_set)

    #for each branch, sum up all the leaves that connect to it
    for i,node in enumerate(prufer_set):
        for j,n in enumerate(seq[:N]):
            if node == n:
                branches[i] += 2**j
    
    # for the branches in prufer seq, find index of parent and add its sum to parent
    for j,n in enumerate(seq[N:]):
        i = prufer_set.index(n)
        branches[i] += branches[j]

    return branches[::-1]

    # TESTING
    # try:
    #     assert_array_equal(np.array(prufer_seq_to_branches(N, prufer_seq)), np.array(branches))
    #     assert_array_equal(np.array(prufer_seq_to_degrees(N, prufer_seq)), np.array(degrees))
    #     print("Arrays are equal.")
    # except AssertionError as e:
    #     print(branches, prufer_seq)
    #     print(f"Arrays are not equal: {e}")

def prufer_seq_to_degrees(N: int, seq: List[int]) -> List[int]:
    # add implied final edge
    seq = seq.copy()
    seq.append(max(seq))
    # initialize things
    prufer_set = sorted(set(seq))
    degrees = [0] * len(prufer_set)

    for i, node in enumerate(prufer_set):
        degrees[i] = seq.count(node)

    return degrees[::-1]

def get_tree_pos(G: pgv.AGraph):
    N = 0
    for node in G.nodes():
        if G.degree(node) == 1:
            N += 1

    # get positions from graph
    pos = {}
    for n in G.nodes():
        p = n.attr['pos']
        if p:
            x, y = map(float, p.split(','))
            pos[int(n.get_name())] = (x, y)

    nodes = G.nodes()
    nodes.sort(key=int)

    node_y = [y for k, (x, y) in pos.items()]
    y_levels = np.linspace(min(node_y), max(node_y), N)
    for n in nodes:
        # children = [int(node.name) for node in G.neighbors(n) if int(node.name) < int(n.name)]
        # if len(children):
        #     children_x = [pos[c][0] for c in children]
        #     # weights =
        #     new_x = sum(children_x)/len(children_x)
        #     pos[int(n)] = (new_x, pos[int(n)][1])

        leaves = ast.literal_eval(n.attr["leaves"]) if len(
            n.attr["leaves"]) else []
        leaves = [l-1 for l in leaves]
        if len(leaves):
            leave_x = [pos[l][0] for l in leaves]
            new_x = (max(leave_x)+min(leave_x))/2
            new_y = int(y_levels[len(leaves)-1])

            pos[int(n)] = (new_x, new_y)

    return pos


def label_set(branch: int, N: int):
    labels = []
    for i, bit in enumerate(reversed(format(branch, f"0{N}b"))):
        if bit == "1":
            labels.append(i+1)
    return labels


def get_sorted_prufer(p: str):
    return "".join(str(x) for x in sorted(p))


tree_img_dir = f"../trees{N}/"

if not os.path.isdir(tree_img_dir):
    os.mkdir(tree_img_dir)

prufer_sums = []
prufers: List[List[int]] = []
# pretty_prufers: List[List[int]] = []

for i, tree in trees.iterrows():
    filename = f"tree_{tree.name}"
    # filename= "temp"
    imgpath = tree_img_dir + filename + ".png"
    # print(imgpath)

    branches = tree["branches"]
    degrees = tree["degrees"]
    prufer_seq = branches_to_prufer_seq(N, branches)
    prufer_seq = [max(prufer_seq) - i+1 for i in prufer_seq]
    # pretty_prufer_seq = [max(prufer_seq) - i+1 for i in prufer_seq]
    # pretty_prufer_seq.append(1)
    p_sum = sum(prufer_seq)
    
    prufer_sums.append(p_sum)
    prufers.append(prufer_seq)

    # print(tree.name, branches, ":", pretty_prufer_seq, prufer_seq)

    # print(prufer_seq_to_tree(N, prufer_seq))



#     T = nx.from_prufer_sequence(prufer_seq)
#     for i, J in enumerate(reversed(branches)):
#         T.nodes[N+i]["branch"] = str(J)

#         T.nodes[N+i]["set"] = "\\{" + ",".join(map(str, label_set(J, N))) + "\\}"
#         # T.nodes[N+i]["set"] = "\{" + ",".join([f"x_{i}" for i in label_set(J, N)]) + "\}"
#         T.nodes[N+i]["leaves"] = label_set(J, N)

#     root = max(list(T.nodes()))
#     depth = max(nx.shortest_path_length(T, source=root).values())
#     leave_ids = range(0, N)

#     A: pgv.AGraph = nx.nx_agraph.to_agraph(T)
#     A.add_subgraph(leave_ids, rank='same')
#     A.layout(prog='dot', args='-y')

#     pos = get_tree_pos(A)

#     # --- NetworkX drawing section ---
#     plt.rcParams.update({
#         "text.usetex": True,
#         "text.latex.preamble": r"""\boldmath
# \usepackage[dvipsnames]{xcolor}
# \renewcommand{\familydefault}{\sfdefault}"""
#     })

#     fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT))
#     # ax.set_aspect('equal')
#     ax.axis('off')

#     # Node styling
#     node_labels = {}
#     node_sizes = []
#     node_colors = []
#     node_fontsizes = []
#     for n in T.nodes():
#         # if n in leave_ids:
#         #     node_labels[n] = str(int(n)+1)
#         #     node_sizes.append(300)
#         #     node_colors.append('white')
#         #     # node_fontsizes.append(20)
#         #     node_fontsizes.append(36)
#         # else:
#         #     node_labels[n] = T.nodes[n]['set']
#         #     node_sizes.append(0)
#         #     node_colors.append('black')
#         #     node_fontsizes.append(16)
#         node_sizes.append(0)
#         node_colors.append('#ED1B23')
#         node_fontsizes.append(30)
#         node_labels[n] = len(T.nodes()) - n

#     # Draw edges
#     nx.draw_networkx_edges(T, pos, ax=ax, width=3)

#     # Draw nodes
#     nx.draw_networkx_nodes(
#         T, pos, ax=ax,
#         node_color=node_colors,
#         node_size=node_sizes,
#         # edgecolors='black',
#         linewidths=1,
#     )

#     # Draw labels
#     colors = ["#ED1B23", "#F58137", "#bf803f",
#               "#008080", "#00AEEF", "#EC008C"]
#     color_i = 0
#     for n in T.nodes():
#         # if n in leave_ids:
#         #     ax.text(
#         #         pos[n][0], pos[n][1],
#         #         f"${node_labels[n]}$",
#         #         fontsize=node_fontsizes[n],
#         #         ha='center',
#         #         va='top',
#         #         # color=colors[color_i]
#         #     )
#         # else:
#         #     pass
#         #     # t = ax.text(
#         #     #     pos[n][0],
#         #     #     pos[n][1],
#         #     #     f"${node_labels[n]}$",
#         #     #     va='center',
#         #     #     ha='center',
#         #     #     fontsize=node_fontsizes[n]
#         #     # )
#         #     # t.set_bbox(dict(facecolor='white'))

#         t = ax.text(
#             pos[n][0]+15,
#             pos[n][1],
#             f"${node_labels[n]}$",
#             va='center',
#             ha='center',
#             fontsize=node_fontsizes[n]
#             # color=node_colors[n]
#         )
#         color_i += 1

#     # Draw title
#     ax.set_title(f"\\textbf{{{tree.name}}} [{','.join(str(x) for x in pretty_prufer_seq)}]" , fontsize=30, loc='left')

#     plt.tight_layout(pad=.5)
#     plt.savefig(imgpath, pad_inches=.5, dpi=100)
#     plt.close()

# p_sums_dict = dict((s, prufer_sums.count(s)) for s in set(prufer_sums))

# print("sums:", len(set(prufer_sums)))
# print(set(prufer_sums))
count = 0

# sorted_prufers: Set[str] = set()
prufers_dict: Dict[str, List[str]] = {}

for p in prufers:
    s = get_sorted_prufer(p)
    if (s not in prufers_dict.keys()):
        prufers_dict[s] = []
    prufers_dict[s].append("".join(str(x) for x in p))


print(len(prufers_dict.keys()), prufers_dict.keys())


for s,lst in prufers_dict.items():
    perms = ["".join(x for x in p) for p in list(set(permutations(s)))]


    def bold(s):
        return '\033[1m' + str(s) + '\033[0m'
    def italic(s):
        return '\033[3m' + str(s) + '\033[0m'
    not_trees = []
    for perm in perms:
        if perm not in lst:
            not_trees.append(perm)
    print(italic(s[::-1]),"--", bold(len(lst)), "trees,", bold(len(not_trees)), "not trees,", bold(len(perms)), "permutations, ", "tree %:", len(lst)/len(perms))

    unlabeled = []

    for p in lst:
        # p = p+'1'
        unlabeled.append(p[N:])

    print("\t internal nodes:", set(unlabeled))
    # if (s == "1222233"):
    #     for p in lst:
    #         # seq = [N+5 - int(x) for x in p]
    #         inc_seq = [int(x) for x in p]
    #         # seq.append(1)
    #         # print(seq)
    #         tree = prufer_seq_to_tree_inc(N, inc_seq)
    #         b = prufer_seq_to_branches_inc(N, inc_seq)
    #         print("\t",inc_seq, tree, b)
    #     print("---- perms not in trees ----")
    #     for perm in not_trees:
    #         inc_seq = [int(x) for x in perm]
    #         # seq.append(1)
    #         # print(seq)
    #         tree = prufer_seq_to_tree_inc(N, inc_seq)
    #         b = prufer_seq_to_branches_inc(N, inc_seq)
    #         print("\t",inc_seq, tree, b)

# unique_prufers = []
# unique_set: Set[str] = set()
# for s in sorted_prufers:
#     s = [int(x) for x in s.split(',')]
#     pmap = Counter(x for x in s if x != 1)
#     umap = (s.count(1), sorted(list(pmap.values())))
#     # print(s, pmap)
#     print(umap)
#     unique_prufers.append(umap)
#     unique_set.add(str(umap[0]) + "-" + ",".join(str(x) for x in umap[1]))

# unique_prufers.sort()
# print()
# print(len(unique_set),unique_prufers)
# shape_data = []

# for psum in sorted(set(prufer_sums)):
#     count = 0
#     arr = []
#     pretty_arr = []
#     for i,pretty in zip(prufers, pretty_prufers):
#         s = sum(i)

#         if s == psum:
#             arr.append(i)
#             pretty_arr.append(",".join(str(k) for k in sorted(pretty)))
#             count+=1
#         # if s == 60:
#         #     print(pretty)

#     # print(f"sum: {psum} - {count}:")
#     print(set(pretty_arr))
#     # all_sets.extend(pretty_arr)
#     # for seq in sorted(arr):
#     #     print(",".join(str(k) for k in seq))
    
# for i in set(prufers):
#     s = sum(int(j) for j in i.split(','))
#     print(i, p_sums_dict[s])
#     # print(i, prufer_sums.count(list(set(prufer_sums))[i]))
