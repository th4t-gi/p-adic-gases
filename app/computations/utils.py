"""Non-physics helpers: input parsing, DB I/O, and combinatorial counts."""

from __future__ import annotations

import ast
import math
import sqlite3
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import pandas as pd


def parse_int_list(text: str) -> list[int]:
    """Parse a user-typed list of integers.

    Accepts ``"1, 2, 3"``, ``"[1, 2, 3]"``, ``"1 2 3"``, or any mix.
    Returns an empty list for empty input. Raises ``ValueError`` on any token
    that isn't a valid integer.
    """
    text = text.strip().strip("[]()").strip()
    if not text:
        return []
    parts = text.replace(",", " ").split()
    return [int(p) for p in parts]


def falling_factorial(x: float, n: int) -> float:
    prod = 1.0
    for i in range(0, n):
        prod *= x - i
    return prod


def default_db_path() -> Path:
    """`<repo-root>/data/trees.db` derived from this file's location."""
    return Path(__file__).resolve().parents[2] / "data" / "trees.db"


def tree_image_path(n: int, tree_id: int) -> Path:
    """`<repo-root>/out/treesN/tree_<id>.png` — produced by data-analysis/tree_viz.py."""
    return Path(__file__).resolve().parents[2] / "out" / f"trees{n}" / f"tree_{tree_id}.png"


def load_trees(n: int, db_path: Path | None = None) -> pd.DataFrame:
    """Load `treesN` from the SQLite DB, with branches/degrees parsed from JSON."""
    path = db_path or default_db_path()
    con = sqlite3.connect(str(path))
    try:
        df = pd.read_sql_query(f"SELECT rowid, * FROM trees{n}", con).set_index(["rowid"]).rename_axis(["tree_id"])
    finally:
        con.close()
    df["branches"] = df["branches"].apply(ast.literal_eval)
    df["degrees"] = df["degrees"].apply(ast.literal_eval)
    return df


@lru_cache(maxsize=None)
def phylogenetic_tree_count(n: int) -> int:
    """|R_N|: number of rooted phylogenetic trees on n labeled leaves (OEIS A000311).

    Ports the recurrence from ``src/utils.cpp::phylogenees_num`` but in exact
    rational arithmetic so the result is exact for any n.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n < 2:
        return n  # A000311(0) = 0, A000311(1) = 1

    # b[i] satisfies a(i) = i! * b[i]; a(i) is the OEIS value.
    b = [Fraction(0), Fraction(1), Fraction(1, 2)]
    for i in range(3, n + 1):
        s = sum((b[k] * b[i - k] * (i - k) for k in range(2, i - 1)), Fraction(0))
        b.append(Fraction(i + 1, i) * b[i - 1] + Fraction(2, i) * s)

    return int(math.factorial(n) * b[n])
