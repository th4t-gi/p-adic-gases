from utils import query
import ast
# import matplotlib.pyplot as plt
import numpy as np


def get_powers_of_two(num: int):
    return [1 << j for j in range(num.bit_length()) if (num & 2**j)]


N = 6

trees = query(N, '../size6.db')
trees["branches"] = trees["branches"].apply(ast.literal_eval)
trees["degrees"] = trees["degrees"].apply(ast.literal_eval)

print(trees)

I_max = 21
I_min = 10

I_max_arr = get_powers_of_two(I_max)
I_min_arr = get_powers_of_two(I_min)
print(I_max_arr, I_min_arr)

3, 6, 9, 12, 18, 24
pairs = [[3, 12],
         [12, 18],
         [18, 9],
         [9, 6],
         [6, 24],
         [24,3]]


star_trees = trees[trees['branches'].apply(
    lambda branches:
        np.any([
            np.all([
                code in branches for code in tup
            ]) for tup in pairs
        ])
)]

print(len(star_trees))
# trees.index = range(1, trees.index.size+1)

# i_min = trees.index.min()
# i_max = trees.index.max()
# idxs = [randint(i_min, i_max) for _ in range(3)]
# trees = trees.loc[idxs]
