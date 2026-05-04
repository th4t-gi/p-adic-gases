"""Base class for all CANO.PY plots."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from app.computations.computation import RunComputation


class BasePlot(ABC):
    supports_video: bool = False

    def __init__(self, df: pd.DataFrame, computation: "RunComputation") -> None:
        self.df = df
        self.computation = computation
        self.config = computation.config
        self.fig: Figure = Figure(figsize=(8, 5), tight_layout=True)

    @abstractmethod
    def render(self) -> None:
        """Draw the plot onto self.fig. Called once after construction."""

    def widget(self) -> QWidget:
        return FigureCanvasQTAgg(self.fig)

    def export_video(self, path: Path, fps: float = 10.0) -> None:
        raise NotImplementedError(f"{type(self).__name__} does not support video export")

    def _stub(self, message: str = "Not yet implemented") -> None:
        ax = self.fig.add_subplot(111)
        ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=18, color="#888")
        ax.set_axis_off()
