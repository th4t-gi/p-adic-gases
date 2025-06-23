from typing import List
import numpy as np

def falling_factorial(x,n):
    prod = 1.0
    for i in range (0, n):
        prod *= x-i
    return prod


def term(branches: List[int], degrees: List[int], p: int, beta: float, intrc_enrgy_array: List[float]):
    # branch_arr = branches.apply(lambda b: list(map(int, b[1:-1].split(","))))
    # branch_arr = list(map(int, branches[1:-1].split(",")))
    # print(branch_arr[0])
    #deg_arr = degrees.apply(lambda d: list(map(int, d[1:-1].split(","))))
    # deg_arr = list(map(int, degrees[1:-1].split(",")))
    out = 1.0
    for J,degree in zip(branches, degrees):
        size_J = bin(J).count("1")

        denom = p**(size_J + (beta * intrc_enrgy_array[J])) - p
        if (denom == 0):
          print(f"p {p}, size_J {size_J}, beta {beta} ej {intrc_enrgy_array[J]}")
        out *= falling_factorial(p, degree)/(p**(size_J + (beta * intrc_enrgy_array[J])) - p)
    return out


def interaction_energy(charges, size_of_charge): 
    out = np.empty(pow(2, size_of_charge), dtype= float)
    for J in range (0,  pow(2, size_of_charge)):
        sum1 = 0.0
        sum2 = 0.0
        for i,charge in enumerate(charges):
            sum1 += ((bool(J & (1 << i))) * charge)
            sum2 += ((bool(J & (1 << i))) * charge* charge)
        out[J] = (((sum1 * sum1) - sum2) / 2.0)
    return out