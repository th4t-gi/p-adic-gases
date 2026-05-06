from typing import List
import numpy as np
import sqlite3
import pandas as pd

def falling_factorial(x,n):
    prod = 1.0
    for i in range (0, n):
        prod *= x-i
    return prod

def factor(branch: int, degree: int, p: int, e_J: int, beta: float):
    size_J = branch.bit_count()
    denom = p**(size_J + (e_J * beta)) - p
    return falling_factorial(p, degree)/denom


def weight(branches: List[int], p: int, energies: List[float], beta: float):
    total = 0.0
    for J in branches:
        size_J = J.bit_count()
        e_J = energies[J]
        
        factor = e_J/(1-p**(1-size_J - (e_J*beta)))
        total += factor
    return total

def double_weight(branches: List[int], p: int, energies: List[float], beta: float):
    total = 0.0
    for J in branches:
        size_J = J.bit_count()
        e_J = energies[J]
        power = p**(1-size_J - (e_J*beta))

        factor = power*((e_J/(1-power))**2)
        total += factor
    return total


def alteration(N: int, branches: List[int], degrees: List[int], p: int, energies: List[float], beta: float):
    # add leaves to branches array
    verticies = branches
    for i in range(N):
        verticies.append(1 << i)
        degrees.append(0)
    # print(verticies, degrees)

    def ramify(vertex):
        N_plus_1 = 1 << (N)
        new_vertex = vertex + N_plus_1
        size_new_vertex = new_vertex.bit_count()
        return (p*(p-1))/contrib(p, size_new_vertex, energies[new_vertex], beta)
        

    def branchify(vertex, children):
        size_vertex = vertex.bit_count()            # |v|
        N_plus_1 = 1 << (N)                         # \{N\}
        new_vertex = vertex + N_plus_1              # v \cup \{N\}
        size_new_vertex = new_vertex.bit_count()    # |v \cup \{N\}|
        if (p < children):
            return 0
        
        return ((p - children)*contrib(p, size_vertex, energies[vertex], beta))/contrib(p, size_new_vertex, energies[new_vertex], beta)

    def alter(vertex):
        size_vertex = vertex.bit_count()
        numerator = 1.0
        denominator = 1.0
        for J in branches:
            # if v \subsetneq J
            if (vertex & J) == vertex:
                numerator *= contrib(p, size_vertex, energies[vertex], beta)
                denominator *= contrib(p, size_vertex + 1, energies[vertex], beta)
        
        return numerator/denominator

    total = 0

    for (v, c) in zip(verticies, degrees):
        total += (ramify(v) + branchify(v, c))*alter(v)

    return total

def contrib(p: int, size: int, energy: float, beta: float):
    return ((p ** (size + energy*beta)) - p)

def term(branches: List[int], degrees: List[int], p: int, energies: List[float],  beta: float):
    out = 1.0
    for J,degree in zip(branches, degrees):
        out *= factor(J, degree, p, energies[J], beta)
    return out


def interaction_energy(charges: List[int]): 
    size_of_charges = len(charges)
    out = np.empty(pow(2, size_of_charges), dtype= float)
    for J in range (0, pow(2, size_of_charges)):
        sum1 = 0.0
        sum2 = 0.0
        for i,charge in enumerate(charges):
            sum1 += ((bool(J & (1 << i))) * charge)
            sum2 += ((bool(J & (1 << i))) * charge* charge)
        out[J] = (((sum1 * sum1) - sum2) / 2.0)
    return out


def query(n: int, dbname = "./trees.db") -> pd.DataFrame:
    # create connection
    con = sqlite3.connect(dbname)

    print(dbname)
    
    # Read query results into a pandas DataFrame
    query = f"SELECT rowid, * FROM trees{n}"
    df = pd.read_sql_query(query, con).set_index(["rowid"])
    con.close()
    
    return df

# from https://stackoverflow.com/questions/893657/how-do-i-calculate-r-squared-using-python-and-numpy
# Polynomial Regression
def polyfit(x, y, degree):
    results = {}

    coeffs = np.polyfit(x, y, degree)

     # Polynomial Coefficients
    results['polynomial'] = coeffs
    # r-squared
    p = np.poly1d(coeffs)
    # fit values, and mean
    yhat = p(x)                         # or [p(z) for z in x]
    ybar = np.sum(y)/len(y)          # or sum(y)/len(y)
    ssreg = np.sum((yhat-ybar)**2)   # or sum([ (yihat - ybar)**2 for yihat in yhat])
    sstot = np.sum((y - ybar)**2)    # or sum([ (yi - ybar)**2 for yi in y])
    results['determination'] = ssreg / sstot

    return results