from typing import List,Set

R_0 = []
R_1 = [[1]]
# R_2 = [[1,2]]
# R_3 = [[1,2,3], [3,[1,2]], [[1,3],2], [1,[2,3]]]

# t = [2, [1,3,4]]


def compute_next_forest(N: int, R_N: List[List]) -> List:
    R_next = []
    for tree in R_N:
        # print("tree: ", tree)
        paths = traverse_tree(tree, [])

        for path in paths:
            # print("\t", path)
            new_tree = generate_tree(N, tree, path)
            # print("\t", new_tree)
            R_next.append(canonical(new_tree))
        R_next.append(canonical([N, tree]))
        
    return R_next

def tree_list_to_tuple(tree):
    for i,b in enumerate(tree):
        if type(b) == list:
            tree[i] = tree_list_to_tuple(tree[i])
    return tuple(tree)

def canonical(tree):
    if type(tree) == int:
        return tree
    tree = [canonical(branch) for branch in tree]
    return sorted(tree, key=normalize)

def normalize(x):
    if isinstance(x, int):
        return (0, x)  # ints come before lists
    return (1, tuple(normalize(e) for e in x))

def generate_tree(N, tree, path):
    new_tree = tree[:]
    if len(path) == 1:
        i = path[0]
        if i == -1:
            return new_tree+[N]
        else:
            new_tree[i] = [N, new_tree[i]]
            return new_tree

    new_tree[path[0]] = generate_tree(N, tree[path[0]], path[1:])
    return new_tree


def traverse_tree(b, path):
    yield path+[-1]
    for i,b in enumerate(b):
        new_path = path+[i]
        if isinstance(b, list):
            yield new_path
            # yield new_tree2
            # If the item is a list, call the function recursively
            yield from traverse_tree(b, new_path)
        else:
            yield new_path

charges = [1,2,3,4,5,6,7,8,9]
N = len(charges)
R_2 = [[charges[0], charges[1]]]
R_current = R_2
for i in range(2,N):
    R_current = compute_next_forest(charges[i], R_current)

print(len(R_current))
for i,tree in enumerate(sorted(R_current, key=str)):
    print(i+1, tree)