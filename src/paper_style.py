"""Journal figure style: vector PDF + 600 dpi PNG, Okabe–Ito colors."""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

# Okabe–Ito (colorblind-safe)
BLUE = "#0072B2"
ORANGE = "#E69F00"
GREEN = "#009E73"
VERMILION = "#D55E00"
SKY = "#56B4E9"
PURPLE = "#CC79A7"
BLACK = "#000000"
GRAY = "#666666"

SINGLE_COL = 3.54  # 90 mm
DOUBLE_COL = 7.08  # 180 mm


def apply_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans"],
            "font.size": 8,
            "axes.labelsize": 8,
            "axes.titlesize": 8,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "legend.fontsize": 7,
            "legend.frameon": False,
            "axes.linewidth": 0.8,
            "xtick.major.width": 0.8,
            "ytick.major.width": 0.8,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.top": True,
            "ytick.right": True,
            "axes.spines.top": True,
            "axes.spines.right": True,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "mathtext.default": "regular",
            "axes.formatter.use_mathtext": True,
            "figure.dpi": 150,
            "savefig.dpi": 600,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.03,
            "lines.linewidth": 1.4,
            "lines.markersize": 4.5,
        }
    )


def panel_label(ax, letter: str, x: float = -0.18, y: float = 1.08) -> None:
    ax.text(
        x,
        y,
        letter,
        transform=ax.transAxes,
        fontsize=10,
        fontweight="bold",
        va="bottom",
        ha="left",
    )


def save_figure(fig: mpl.figure.Figure, directory: Path, stem: str) -> list[Path]:
    directory.mkdir(parents=True, exist_ok=True)
    paths = []
    for ext in ("pdf", "png"):
        path = directory / f"{stem}.{ext}"
        fig.savefig(path, format=ext)
        paths.append(path)
    plt.close(fig)
    return paths
