from functools import lru_cache, cmp_to_key
from itertools import product

def partitions(n, max_part=None):
    if max_part is None:
        max_part = n
    if n == 0:
        yield []
        return
    for i in range(min(max_part, n), 1-1, -1):
        for rest in partitions(n-i, i):
            yield [i] + rest

def canonical(children):
    return tuple(sorted(children, key=str))

@lru_cache(None)
def trees(n):
    if n == 1:
        return {("1",)}
    
    result = set()
    
    for p in partitions(n):
        if len(p) < 2:
            continue
        
        child_sets = [trees(k) for k in p]
        for combo in product(*child_sets):
            # print("\t", combo)
            result.add(canonical(combo))
    
    return result

def format_tree(t):
    if t == ("1",):
        return "1"
    return "(" + ",".join(format_tree(c) for c in t) + ")"


four = trees(4)
five = trees(5)
six = trees(6)
seven = trees(7)
eight = trees(8)
nine = trees(9)
# example
for t in tuple(sorted(four.union(five, six, seven, eight), key=str)):
    string = format_tree(t)
    leaves = string.count("1")
    print("\t"*(leaves - 4), string)