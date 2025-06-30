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
    size_J = bin(branch).count("1")
    denom = p**(size_J + (e_J * beta)) - p
    return falling_factorial(p, degree)/denom


def weight(branches: List[int], p: int, energies: List[float], beta: float):
    total = 0.0
    for J in branches:
        size_J = bin(J).count("1")
        e_J = energies[J]
        
        factor = e_J/(1-p**(1-size_J - e_J*beta))
        total += factor
    return total

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


def query(n: int, p: int) -> pd.DataFrame:
    # create connection
    dbname = f"./size{n}.db"
    # print(dbname)
    con = sqlite3.connect(dbname)
    
    # Read query results into a pandas DataFrame
    query = f"""
        SELECT
            trees.id, trees.branches, trees.degrees, probabilities.prime, probabilities.probability
        FROM
            probabilities
        JOIN
            trees ON probabilities.tree_id = trees.id
        WHERE
            probabilities.prime = {p}
        ORDER BY
            probabilities.probability DESC
    """
    df = pd.read_sql_query(query, con)
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