from typing import List
import numpy as np

def falling_factorial(x,n):
    prod = 1.0
    for i in range (0, n):
        prod *= x-i
    return prod

def factor(branch: int, degree: int, p: int, e_J: int, beta: float):
    size_J = bin(branch).count("1")
    denom = p**(size_J + (e_J * beta)) - p
    return falling_factorial(p, degree)/denom


def weight(branches: List[int], degrees: List[int], p: int, interaction_enrgy: List[float], beta: float):
    total = 0.0
    for J,degree in zip(branches, degrees):
        total += factor(J, degree, p, interaction_enrgy[J], beta)
    return total

def term(branches: List[int], degrees: List[int], p: int, interaction_enrgy: List[float], beta: float):
    out = 1.0
    for J,degree in zip(branches, degrees):
        out *= factor(J, degree, p, interaction_enrgy[J], beta)
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