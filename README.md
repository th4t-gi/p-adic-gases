# CANO.PY

**Computational ANalysis and Observation in Python For Log-Coulomb Gases.**

CANO.PY is a desktop GUI for investigating the canonical partition function of *p-adic log-Coulomb gases*. It wraps the  computations and plots developed during the Summer 2025 MAP mentored by Joe Webster — a collection of scripts in [`data-analysis/`](data-analysis/) — into a single interactive interface.

Computations run against either:

1. a pre-generated SQLite database of phylogenetic trees (`data/trees.db`, built by the C++ tools in [`src/`](src/)), or
2. an in-memory tree generator based on [`data-analysis/unlabeled_trees.py`](data-analysis/unlabeled_trees.py), for cases where the database isn't available or N is small enough not to need it.

The app is under active development.

## Background

A *log-Coulomb gas* in $\Z_p$ is a system of $N$ charged particles with randomly varying locations $x_1,\dots, x_N \in \Z_p$. Its state space is $X = \Z_p^N$ and the canonical partition function takes the form

<!-- the energy of each state $\vec{x} = (x_1, \dots, x_N) \in X$ is defined by
$$
    E(\vec{x})\vcentcolon= \sum\limits_{\mathclap{1 \leq i < j \leq N}}\mathfrak{q}_i \mathfrak{q}_j\log\frac{1}{|x_i - x_j|_p},
$$
where $\mathfrak{q}_i$ is the charge of the particle at $x_i$. For this system,  -->

$$
    \mathcal{Z}_N(\beta)\vcentcolon=\int\limits_{\Z_p^N}\!\prod_{1\leq i < j \leq N}\!\!\!|x_i-x_j|_p^{\mathfrak{q}_i\mathfrak{q}_j\beta}\,d\mu^N\!(\vec{x}),
$$

where $\mu^N$ is the additive Haar measure on $\Z_p^N$ satisfying $\mu^N(\Z_p^N)=1$.

In Webster 2023, it was shown that, for all $\beta$ such that $\mathcal{Z}_N(\beta)$ converges, we have

$$
    \mathcal{Z}_N(\beta) =  p^{e_{[N]}\beta}\!\sum\limits_{\pitchfork \in \mathcal{R}_N}\prod_{J \in \mathcal{B}(\pitchfork)}\!\!\left(\frac{(p)_{\deg_{\pitchfork}(J)}}{p^{|J| + e_J\beta}- p}\right),
$$

where $\mathcal{R}_N$ is the set of all rooted phylogenetic trees with leaves labeled $1, \dots, N$. CANO.PY evaluates this discrete sum for user-supplied charges and primes.

### Summer 2025 Abstract (Low Temperature Limits for $Z_N(\beta)$)

This project extends results on log-Coulomb gases done in recent years and creates new tools to aid the investigation of the model. In past results, it was found that the canonical partition function for an $N$ particle log-Coulomb gas in $p$-adic space can be expressed as a sum over all `phylogenetic trees' with $N$ labeled leaves. Using a computational approach to calculate and analyze the behavior of the canonical partition over this discrete sum for small $N$ values, we formed, then later proved our main result: an explicit expression for the low temperature limit of the system of $N$ charged particles dependent only on the maximum and minimum charges of the system as well as the number of those charges, and importantly not dependent on $N$ at all.

### Future Directions

In spring 2026, we intend to continue investigating this model and specifically try to determine what the thermodynamic limit of the system is. That is, what is the behavior of $\mathcal{Z}_N(\beta)$ as $N \to \infty$. This is quite challenging since $|\mathcal{R}_N| > N!$ for all $N\geq 4$ so pursuit of this question will require further experimentation and optimization of our software. CANO.PY is the platform we plan to do that experimentation in.

### Database Design

Because of the refinement feature of phylogenetic trees, the minimal information required to store a given tree in $\mathcal{R}_N$

for each tree in $\mathcal{R}_N$ and still efficently compute $\mathcal{Z}_N(\beta)$ for varying charges and $\beta$,

## Installation

CANO.PY lives in [`app/`](app/) and is built on [PySide6](https://doc.qt.io/qtforpython-6/). To install, run from the repo root:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
```

This creates a virtual environment, activates the venv, and installs required packages.

## Usage

Launch the app:

```sh
make app
# or, equivalently:
python3 -m app
```

The launcher window takes a list of charges, a list of primes, and a β resolution. Clicking **Run** opens a separate window for each computation so you can compare behavior between runs.

<!-- While iterating on the source, run with auto-restart on save:

```sh
make dev
```

`make dev` uses `watchmedo` (from `watchdog`) to relaunch the process whenever a Python file under `app/` changes. Ctrl-C to stop watching. -->

## Resources

- see websters papers
- oeis A000311
-

## Acknowledgements

We would like to acknowledge Professor Webster for his guidance throughout our research, and we would like to express our gratitude to Grinnell College for funding this project.
