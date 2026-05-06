# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

Computational research code for the *p-adic Gas Canonical Partition Calculator* (Webster lab). The canonical partition function $\mathcal{Z}_N(\beta)$ for an N-particle log-Coulomb gas in $\Z_p$ reduces to a sum over rooted phylogenetic trees with N labeled leaves (OEIS A000311 grows faster than N!). This repo:

1. **C++ generator** (`src/`) enumerates all phylogenetic trees up to a given N and persists them to SQLite (`data/trees.db`).
2. **Python analysis** (`data-analysis/`) loads trees from the DB and computes/plots physical quantities (partition function, expected energy, variance, per-tree probabilities) for given charge configurations.
3. **(In progress) `app/` GUI** to run the computations in `data-analysis/` interactively, including an in-memory mode driven by `unlabeled_trees.py` (no DB required).

## Build & run

C++ side (CMake ≥ 3.20). `fmt`, `spdlog`, and `nlohmann_json` are fetched automatically if not found. `sqlite3`, `SQLiteCpp`, and `boost` must be installed manually:

```sh
# macOS (Homebrew — prefix detected automatically)
brew install sqlite3 sqlitecpp boost

# Linux (apt)
sudo apt install libsqlite3-dev libsqlitecpp-dev libboost-program-options-dev

# Windows — install vcpkg, then:
# vcpkg install sqlite3 sqlitecpp boost-program-options
# pass -DCMAKE_TOOLCHAIN_FILE=<vcpkg>/scripts/buildsystems/vcpkg.cmake
```

```sh
cmake -B build                          # configure (Release)
cmake -B build -DCMAKE_BUILD_TYPE=Debug # configure (Debug, also builds test)
cmake --build build                     # compile into build/
rm -rf build                            # clean
```

Run the tree generator (note `main.cpp` is the primary executable, but the legacy script `profile.sh` calls `build/phylogenees`):

```sh
build/main <N> -d data/trees.db [-r <reset_to>] [--ignore-changes] [-v]
```

`main` prompts interactively for a "changes" log message and a y/n confirmation before running unless `--ignore-changes` is set; pipe input or use the flag in non-interactive contexts.

Python side: each subdirectory has its own venv (`.venv` and `data-analysis/.venv`). Most scripts are run directly from `data-analysis/`:

```sh
cd data-analysis
python physics.py        # main partition-function/probability/expected-value plots
python tree_viz.py       # graphviz tree rendering (requires pygraphviz)
python unlabeled_trees.py
```

Scripts assume cwd is `data-analysis/` and reference the DB via relative paths (e.g. `query(n, "..")` resolves to `../trees.db`). `data/trees.db` lives at the repo root in `data/`, so when adding new entry points pass an explicit DB path rather than relying on the legacy default.

## Architecture

### Tree representation (shared C++/Python)

A phylogenetic tree on N labeled leaves is stored as **two parallel arrays**:

- `branches: List[int]` — each branch (internal node) is a bitmask over `{1,...,N}` indicating which leaves are below it. Bit `i` set means leaf `i+1` is in the subset. Convention: branches are listed root-first (index 0 is `2^N - 1`, the full set), and each branch is a superset of the branches it contains.
- `degrees: List[int]` — number of children of each branch (same index).

The set $\mathcal{B}(\pitchfork)$ in the math is exactly `branches`; $\deg_\pitchfork(J)$ is the matching `degrees` entry; $|J|$ is `J.bit_count()`. The SQLite tables store both as JSON-encoded arrays.

### Database layout (`data/trees.db`, ~16 GB)

- One table per leaf size: `trees1`, `trees2`, ..., `treesN` (and `trees{N}_r` for filtered/restricted variants), schema `(branches JSON, degrees JSON)` — `rowid` is the implicit ID.
- Metadata table `trees_sequence(name, label_size, is_filtered)` lists which tables exist and at what `label_size`.
- `APIWrapper` (`src/api.{h,cpp}`) is the only writer; `data-analysis/utils.py::query(n, ...)` is the canonical reader (`SELECT rowid, * FROM trees{n}`, parses JSON via `ast.literal_eval` at the call site).

### C++ tree generation pipeline

`src/main.cpp` is a thin Boost.ProgramOptions front-end that:

1. Initializes the spdlog logger and the SQLite connection.
2. Reads `MAX(label_size)` already in the DB.
3. For each `i` from `max+1` to `N`, calls `make_trees(i, db, IMAX, IMIN)` from `phylogenees.cpp`.

`make_trees` builds `treesN` from `treesK` and `treesN-K` in the DB by iterating over subsets `J ⊂ {1,...,N-1}` and combining left/right sub-trees via `Tree::translate` (bit-shuffles a tree's branch masks to a target subset; see `translate_block_*` in `utils.h`). Two derived trees (with and without merging the top fork) are emitted per pair, batched into vectors of size `BATCH_COMPUTE_SIZE` and written via `APIWrapper::insert_trees` (which sets `synchronous=OFF`/`journal_mode=MEMORY` during the batch). `check_tree(...)` is the hook for filtering by `IMAX`/`IMIN` charge masks (currently no-op — the "PUSH TREE TO R*_I" branch is not implemented).

Tree generation is the dominant cost; `BATCH_COMPUTE_SIZE`, `BATCH_WRITE_SIZE`, `BATCH_READ_SIZE` in `api.h` are the tuning knobs.

`partitions.cpp`, `translate.cpp`, `blocks.cpp`, `probabilities.cpp` are standalone executables/experiments — `blocks.cpp` and `probabilities.cpp` reference an old `sqlpp11` API and do not currently compile against the rest.

### Python analysis layer

- `data-analysis/utils.py` — DB loader (`query`), interaction-energy precomputation (`interaction_energy(charges)` returns array of length `2^N` indexed by branch bitmask), per-tree summands `term`/`weight`/`double_weight`/`factor` matching the formulas in the README. These are the building blocks every analysis script uses.
- `data-analysis/physics.py` — main script that, for arrays of `charges` and `primes`, loads the right `treesN` table, computes a long-form `DataFrame` indexed by `(prime, beta, tree_id)` containing `term`, `phys_prob`, `weight`, `double_weight`, then plots $\mathcal{Z}_I(\beta)$, $\langle E\rangle_\beta$, variance, and per-tree probability bars.
- `data-analysis/tree_prob.py` — `TreePlt` class wraps the per-tree probability bar plot with a $\beta$ slider and an `FuncAnimation`-based MP4 export.
- `data-analysis/tree_viz.py` — converts `(branches, degrees)` to a Prüfer sequence, builds an `nx`/`pgv.AGraph`, lays out with Graphviz (`dot`), and renders one image per tree to `../trees{N}/`.
- `data-analysis/unlabeled_trees.py` — pure-Python recursive enumerator of *unlabeled* rooted trees (canonical-form set, memoized). This is the in-memory algorithm the upcoming `app/` will use as the no-DB code path.
- `graphs2.py`, `interaction_energies.py`, `star_counting.py`, `sums_and_squares.py` — exploratory one-off scripts; treat as research notebooks rather than library code.

### `app/` GUI (planned, not yet on disk)

Goal: a GUI that exposes the analyses in `data-analysis/` (partition function, expected value, variance, per-tree probability, tree visualization) with two backends — (a) read trees for a chosen N from `data/trees.db` via `utils.query`, and (b) generate trees in memory via `unlabeled_trees.trees(n)`. Build incrementally, committing per feature. The existing `data-analysis/*.py` should be the source of truth for the math; refactor shared logic out of the script-style files into importable functions rather than duplicating formulas.

## Conventions

- **C++**: C++20, clang-format Google-based with 2-space indent, 120-col, BlockIndent brackets (see `.clang-format`). Use `SPDLOG_INFO`/`SPDLOG_DEBUG` etc. — `logger::init` wires up file + stdout sinks and `logger::preamble` records the invocation in the log header.
- **Tree array ordering**: root is index 0 in `branches`. When constructing a new tree by composition, prepend new degree counts at `degrees.begin()` (see `make_trees`), not append.
- **N is small**: `code_t = uint16_t` caps the bitmask at 16 leaves. Don't widen without auditing `translate_block_*` and `bit_length`.
- **DB writes are append-only by construction**: `make_trees` checks `MAX(label_size)` and refuses to recompute. Use `--reset <K>` to truncate everything strictly above leaf size K.
- **Gitignored data**: `data/`, `out/`, `build/`, `__pycache__/`, `**/.DS_Store`, and stray `test.cpp` are all ignored. Do not check in DB files or generated CSVs.
