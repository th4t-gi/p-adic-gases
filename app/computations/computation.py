"""Run-time computation: turns a RunConfig into the per-tree DataFrame.

Mirrors data-analysis/physics.py::compute() but driven by RunConfig from the
launch form. Synchronous for now — runs on the GUI thread when RunWindow opens.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from PySide6.QtCore import QEventLoop, QProcess, Qt, QTimer
from PySide6.QtWidgets import QApplication, QMessageBox, QProgressDialog

from app.computations.physics import (
    beta_grid,
    double_weight,
    interaction_energy,
    term,
    q_term,
    c_term,
    weight,
)
from app.computations.utils import load_trees, default_db_path, tree_image_path
from app.plots import RunConfig


class RunComputation:
    def __init__(self, config: RunConfig, db_path: Path | None = None) -> None:
        self.config = config
        self.db_path = db_path
        self.energies: np.ndarray = interaction_energy(config.charges)
        self.beta_vals: np.ndarray = beta_grid(config.charges, config.beta_step)
        self._physics_df: pd.DataFrame | None = None
        self._trees_df: pd.DataFrame | None = None

    @property
    def n(self) -> int:
        return len(self.config.charges)

    def run(self) -> pd.DataFrame:
        """Build the (prime, beta, tree_id)-indexed DataFrame and cache it."""
        if self._physics_df is not None:
            return self._physics_df

        trees = load_trees(self.n, self.db_path)
        if trees.empty:
            trees = self._prompt_generate_trees()
            print(trees, "hello!!!")
            if trees.empty:
                raise Exception("No trees found to run computation.")

        img_dir = tree_image_path(self.n, 0).parent
        if not img_dir.exists():
            self._prompt_generate_tree_images(len(trees))

        charges_str = ", ".join(map(str, self.config.charges))
        _comp_progress = QProgressDialog(f"Running computation for q=({charges_str})…", None, 0, 0)
        _comp_progress.setWindowTitle("Computing")
        _comp_progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        _comp_progress.setMinimumDuration(0)
        _comp_progress.setAutoClose(False)
        _comp_progress.setAutoReset(False)
        _comp_progress.show()
        QApplication.processEvents()

        for p in self.config.primes:
            # Creates Series of whether tree is a q-tree or not
            trees[f"is_{p}_tree"] = trees["degrees"].apply(lambda degs, p=p: all(d <= p for d in degs))
            # Computes $\prod_{J\in B(\tree)} (p)_{c_\tree(J)}$ for all trees
            trees[f"{p}_comb_prod"] = trees["degrees"].apply(lambda degs, p=p: c_term(degs, p))


        self._trees_df = trees
        print(trees)
        
        energies = self.energies
        df_arr: list[pd.DataFrame] = []

        for p in self.config.primes:
            for beta in self.beta_vals:
                QApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

                terms = trees.apply(
                    lambda row, p=p, beta=beta: term(row["branches"], row["degrees"], p, energies, beta),
                    axis=1,
                )
                total = terms.sum()
                probs = terms / total

                phys_terms = trees.apply(
                    lambda row, p=p, beta=beta: q_term(row["branches"], p, energies, beta),
                    axis=1,
                )
                comb_terms = trees.apply(
                    lambda row, p=p: c_term(row["degrees"], p),
                    axis=1,
                )
                terms2 = phys_terms * comb_terms

                weights = trees.apply(
                    lambda row, p=p, beta=beta: weight(row["branches"], p, energies, beta),
                    axis=1,
                )
                doubles = trees.apply(
                    lambda row, p=p, beta=beta: double_weight(row["branches"], p, energies, beta),
                    axis=1,
                )

                df_arr.append(
                    pd.DataFrame(
                        {
                            "prime": p,
                            "beta": beta,
                            "tree_id": trees.index,
                            "term": terms,
                            "term2": terms2,
                            "phys_term": phys_terms,
                            "comb_term": comb_terms,
                            "phys_prob": probs,
                            "weight": weights,
                            "double_weight": doubles,
                            "alteration": np.zeros(len(trees)),
                        }
                    )
                )

        df = pd.concat(df_arr).set_index(["prime", "beta", "tree_id"])
        self._physics_df = df
        _comp_progress.close()

        # import tempfile
        # import webbrowser
        # from itables import to_html_datatable

        # html = f"<!DOCTYPE html><html><body>{to_html_datatable(df, column_filters='header')}</body></html>"
        # with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
        #     f.write(html)
        #     webbrowser.open(f"file://{f.name}")
        return df

    def _prompt_generate_trees(self) -> pd.DataFrame:
        db_path = self.db_path or default_db_path()
        repo_root = db_path.resolve().parents[1]
        cmd = f"build/main {self.n} -d {db_path} --ignore-changes --confirm"

        reply = QMessageBox.question(
            None,
            "No trees found",
            f"No trees for N={self.n} found in the database.\n\nRun:\n{cmd}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return pd.DataFrame()
        
        print("PROCESS!")

        executable = str(repo_root / "build" / "main")

        process = QProcess()
        process.setWorkingDirectory(str(repo_root))

        progress = QProgressDialog(f"Generating trees for N={self.n}…", "Cancel", 0, 0)
        progress.setWindowTitle("Generating Trees")
        progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress.setMinimumDuration(0)
        progress.setAutoClose(False)
        progress.setAutoReset(False)

        loop = QEventLoop()
        canceled = [False]

        def on_cancel():
            canceled[0] = True
            process.terminate()
            loop.quit()

        start: list[float] = []

        def on_finished():
            elapsed_ms = (time.monotonic() - start[0]) * 1000
            delay = max(0, 500 - elapsed_ms)
            QTimer.singleShot(int(delay), loop.quit)

        process.finished.connect(on_finished)
        progress.canceled.connect(on_cancel)

        process.start(
            executable,
            [str(self.n), "-d", str(db_path), "--ignore-changes", "--confirm"],
        )
        start.append(time.monotonic())
        progress.show()
        loop.exec()
        progress.canceled.disconnect(on_cancel)
        progress.close()

        if canceled[0]:
            return pd.DataFrame()

        if process.exitCode() != 0:
            msg = QMessageBox(None)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Generation failed")
            msg.setText(f"build/main exited with code {process.exitCode()}.")
            msg.setDetailedText(process.readAllStandardError().toStdString())
            msg.exec()
            return pd.DataFrame()

        return load_trees(self.n, self.db_path)

    def _prompt_generate_tree_images(self, n_trees: int) -> None:
        db_path = self.db_path or default_db_path()
        repo_root = db_path.resolve().parents[1]
        img_dir = tree_image_path(self.n, 0).parent

        reply = QMessageBox.question(
            None,
            "Generate tree images",
            f"Tree images for N={self.n} not found.\n\nGenerate images for trees ({n_trees} total)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        process = QProcess()
        process.setWorkingDirectory(str(repo_root))

        progress = QProgressDialog(f"Generating tree images for N={self.n}…", "Cancel", 0, n_trees)
        progress.setWindowTitle("Generating Tree Images")
        progress.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress.setMinimumDuration(0)
        progress.setAutoClose(False)
        progress.setAutoReset(False)

        loop = QEventLoop()
        canceled = [False]

        def on_cancel():
            canceled[0] = True
            process.terminate()
            loop.quit()

        def poll_progress():
            if img_dir.exists():
                count = sum(1 for f in img_dir.iterdir() if f.suffix == ".png")
                progress.setValue(min(count, n_trees))

        timer = QTimer()
        timer.setInterval(500)
        timer.timeout.connect(poll_progress)

        process.finished.connect(loop.quit)
        progress.canceled.connect(on_cancel)

        process.start(sys.executable, [str(repo_root / "data-analysis" / "tree_viz.py"), str(self.n)])
        timer.start()
        progress.show()
        loop.exec()
        timer.stop()
        progress.canceled.disconnect(on_cancel)
        progress.close()

        if canceled[0]:
            return

        if process.exitCode() != 0:
            msg = QMessageBox(None)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Image generation failed")
            msg.setText(f"tree_viz.py exited with code {process.exitCode()}.")
            msg.setDetailedText(process.readAllStandardError().toStdString())
            msg.exec()