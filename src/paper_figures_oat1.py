"""Publication figures for surface-OAT1 clearance bottleneck analysis.

Reads saved tables from data/oat1_surface_flux/paper/ (run the model first).
Writes journal PDF + 600 dpi PNG files to figures/paper_oat1/.

    python src/oat1_surface_flux_model.py
    python src/paper_figures_oat1.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch
from mpl_toolkits.axes_grid1 import make_axes_locatable

sys.path.insert(0, str(Path(__file__).resolve().parent))

from oat1_data_io import PAPER_DIR, load_map_tidy, load_sweep_csv
from oat1_surface_flux_model import EPS_MEM, VMAX_A_EQUIV
from paper_style import (
    BLACK,
    BLUE,
    DOUBLE_COL,
    GRAY,
    GREEN,
    ORANGE,
    PURPLE,
    SINGLE_COL,
    VERMILION,
    apply_style,
    panel_label,
    save_figure,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = REPO_ROOT / "figures" / "paper_oat1"


def require_data() -> None:
    needed = [
        PAPER_DIR / "sweep_apical_fast.csv",
        PAPER_DIR / "sweep_apical_equal.csv",
        PAPER_DIR / "sweep_apical_slow.csv",
        PAPER_DIR / "map_clearance_tidy.csv",
    ]
    missing = [p for p in needed if not p.exists()]
    if missing:
        raise SystemExit(
            "Missing saved data. Run first:\n"
            "  python src/oat1_surface_flux_model.py\n"
            "Missing:\n  " + "\n  ".join(str(p) for p in missing)
        )


def fig1_schematic() -> None:
    fig, ax = plt.subplots(figsize=(DOUBLE_COL, 2.15))
    ax.set_xlim(0, 10.2)
    ax.set_ylim(0, 2.4)
    ax.axis("off")

    bands = [
        (0.15, 2.35, "#d6f5d6", "Blood\nlumen"),
        (2.50, 1.70, "#f4c2c2", "Membrane\n(diffusion)"),
        (4.20, 1.10, "#ffd9b3", "Cell"),
        (5.30, 4.50, "#cfe8ff", "Dialysate"),
    ]
    for x, w, color, text in bands:
        ax.add_patch(
            FancyBboxPatch(
                (x, 0.45),
                w,
                1.35,
                boxstyle="round,pad=0.02,rounding_size=0.04",
                facecolor=color,
                edgecolor=BLACK,
                linewidth=0.8,
            )
        )
        ax.text(x + w / 2, 1.12, text, ha="center", va="center", fontsize=8)

    ax.annotate(
        "",
        xy=(2.50, 1.95),
        xytext=(4.20, 1.95),
        arrowprops=dict(arrowstyle="<->", color=VERMILION, lw=1.4),
    )
    ax.text(3.35, 2.12, "OAT1 flux", ha="center", va="bottom", color=VERMILION, fontsize=8)

    ax.annotate(
        "",
        xy=(5.30, 0.62),
        xytext=(4.20, 0.62),
        arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.4),
    )
    ax.text(4.75, 0.28, "apical efflux", ha="center", va="center", color=BLUE, fontsize=8)

    ax.text(0.15, 0.18, r"$r=0$", fontsize=7, color=GRAY)
    ax.text(2.42, 0.18, r"$R_1$", fontsize=7, color=GRAY)
    ax.text(4.12, 0.18, r"$R_2$", fontsize=7, color=GRAY)
    ax.text(5.22, 0.18, r"$R_3$", fontsize=7, color=GRAY)
    save_figure(fig, FIG_DIR, "Fig1_transport_schematic")


def fig2_clearance() -> None:
    fast = load_sweep_csv(PAPER_DIR / "sweep_apical_fast.csv")
    equal = load_sweep_csv(PAPER_DIR / "sweep_apical_equal.csv")
    slow = load_sweep_csv(PAPER_DIR / "sweep_apical_slow.csv")

    fig, ax = plt.subplots(figsize=(SINGLE_COL, 2.55))
    ax.semilogx(fast["Vmax_A_mol_m2_s"], fast["clearance_uL_min_cm2"], color=BLUE, label=r"$V_{\mathrm{max}}^{\mathrm{ap}}=10\,V_{\max}^{A}$")
    ax.semilogx(equal["Vmax_A_mol_m2_s"], equal["clearance_uL_min_cm2"], color=ORANGE, label=r"$V_{\mathrm{max}}^{\mathrm{ap}}=V_{\max}^{A}$")
    ax.semilogx(slow["Vmax_A_mol_m2_s"], slow["clearance_uL_min_cm2"], color=GREEN, label=r"$V_{\mathrm{max}}^{\mathrm{ap}}=0.1\,V_{\max}^{A}$")
    ax.axvline(VMAX_A_EQUIV, color=GRAY, ls="--", lw=0.9)
    ax.text(
        VMAX_A_EQUIV * 1.15,
        0.55,
        "thesis volumetric\n$V_{\\max}$ equivalent",
        fontsize=6.5,
        color=GRAY,
        rotation=90,
        va="bottom",
    )
    da = fast["Da"]
    vmax = fast["Vmax_A_mol_m2_s"]
    if np.min(da) < 1 < np.max(da):
        ax.axvline(np.interp(1.0, da, vmax), color=VERMILION, ls=":", lw=0.9)
    ax.set_xlabel(r"$V_{\max}^{A}$ (mol m$^{-2}$ s$^{-1}$)")
    ax.set_ylabel(r"Clearance ($\mu$L min$^{-1}$ cm$^{-2}$)")
    ax.legend(loc="lower right")
    save_figure(fig, FIG_DIR, "Fig2_clearance_vs_VmaxA")


def fig3_fluxes() -> None:
    d = load_sweep_csv(PAPER_DIR / "sweep_apical_fast.csv")
    fig, ax = plt.subplots(figsize=(SINGLE_COL, 2.55))
    x = d["Vmax_A_mol_m2_s"]
    ax.loglog(x, d["J_BM_mol_m2_s"], color=BLUE, label=r"$J$ blood–membrane")
    ax.loglog(x, d["J_OAT1_mol_m2_s"], color=VERMILION, label=r"$J$ OAT1")
    ax.loglog(x, d["J_CD_mol_m2_s"], color=GREEN, ls="--", label=r"$J$ apical")
    ax.loglog(x, d["J_OAT1_capacity_mol_m2_s"], color=ORANGE, ls=":", label=r"$V_{\max}^{A}$")
    ax.loglog(
        x,
        d["J_membrane_capacity_mol_m2_s"],
        color=PURPLE,
        ls=":",
        label=r"$P_m C_{\mathrm{in}}$",
    )
    ax.set_xlabel(r"$V_{\max}^{A}$ (mol m$^{-2}$ s$^{-1}$)")
    ax.set_ylabel(r"Flux (mol m$^{-2}$ s$^{-1}$)")
    ax.legend(loc="lower right", ncol=1)
    save_figure(fig, FIG_DIR, "Fig3_interface_fluxes")


def fig4_damkohler() -> None:
    d = load_sweep_csv(PAPER_DIR / "sweep_apical_fast.csv")
    fig, ax = plt.subplots(figsize=(SINGLE_COL, 2.55))
    ax.semilogx(d["Da"], d["clearance_uL_min_cm2"], color=BLUE)
    ax.axvspan(1e-3, 0.3, color=GREEN, alpha=0.15, lw=0)
    ax.axvspan(3.0, 2e3, color=ORANGE, alpha=0.15, lw=0)
    ax.axvline(1.0, color=BLACK, ls="--", lw=0.8)
    ax.text(0.02, 10.2, "OAT1-limited", color=GREEN, fontsize=7)
    ax.text(8.0, 10.2, "membrane-limited", color=ORANGE, fontsize=7)
    ax.set_xlim(3e-3, 8e3)
    ax.set_xlabel(r"$Da = V_{\max}^{A}/(P_m C_{\mathrm{in}})$")
    ax.set_ylabel(r"Clearance ($\mu$L min$^{-1}$ cm$^{-2}$)")
    save_figure(fig, FIG_DIR, "Fig4_Damkohler_regimes")


def fig5_heatmap() -> None:
    m = load_map_tidy(PAPER_DIR / "map_clearance_tidy.csv")
    vmax = np.unique(m["Vmax_A_mol_m2_s"])
    eps = np.unique(m["eps_membrane"])
    cl = np.zeros((len(eps), len(vmax)))
    da = np.zeros_like(cl)
    for i, e in enumerate(eps):
        for j, v in enumerate(vmax):
            mask = (np.isclose(m["eps_membrane"], e)) & (np.isclose(m["Vmax_A_mol_m2_s"], v))
            cl[i, j] = m["clearance_uL_min_cm2"][mask][0]
            da[i, j] = m["Da"][mask][0]

    fig, ax = plt.subplots(figsize=(SINGLE_COL, 2.7))
    im = ax.pcolormesh(vmax, eps, cl, shading="auto", cmap="cividis")
    ax.contour(vmax, eps, da, levels=[1.0], colors="white", linewidths=1.0)
    ax.axhline(EPS_MEM, color="white", ls="--", lw=0.8)
    ax.set_xscale("log")
    ax.set_xlabel(r"$V_{\max}^{A}$ (mol m$^{-2}$ s$^{-1}$)")
    ax.set_ylabel(r"Membrane porosity $\varepsilon$")
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.08)
    cb = fig.colorbar(im, cax=cax)
    cb.set_label(r"Clearance ($\mu$L min$^{-1}$ cm$^{-2}$)")
    ax.text(1.2e-8, EPS_MEM + 0.03, r"$\varepsilon=0.45$", color="white", fontsize=6.5)
    ax.text(3e-8, 0.78, r"$Da=1$", color="white", fontsize=6.5)
    save_figure(fig, FIG_DIR, "Fig5_clearance_map")


def fig6_capacity_load() -> None:
    d = load_sweep_csv(PAPER_DIR / "sweep_apical_fast.csv")
    fig, ax = plt.subplots(figsize=(SINGLE_COL, 2.55))
    x = d["Vmax_A_mol_m2_s"]
    ax.semilogx(x, d["J_OAT1_mol_m2_s"] / d["J_OAT1_capacity_mol_m2_s"], color=VERMILION, label="OAT1")
    ax.semilogx(
        x,
        d["J_OAT1_mol_m2_s"] / d["J_membrane_capacity_mol_m2_s"],
        color=ORANGE,
        label="membrane",
    )
    ax.semilogx(
        x,
        d["J_CD_mol_m2_s"] / d["J_apical_capacity_mol_m2_s"],
        color=BLUE,
        label="apical",
    )
    ax.axhline(1.0, color=GRAY, ls=":", lw=0.8)
    ax.set_ylim(0, 1.15)
    ax.set_xlabel(r"$V_{\max}^{A}$ (mol m$^{-2}$ s$^{-1}$)")
    ax.set_ylabel("Flux / capacity")
    ax.legend(loc="center right")
    save_figure(fig, FIG_DIR, "Fig6_flux_capacity_ratio")


def fig_combined() -> None:
    fast = load_sweep_csv(PAPER_DIR / "sweep_apical_fast.csv")
    equal = load_sweep_csv(PAPER_DIR / "sweep_apical_equal.csv")
    slow = load_sweep_csv(PAPER_DIR / "sweep_apical_slow.csv")
    m = load_map_tidy(PAPER_DIR / "map_clearance_tidy.csv")

    fig, axes = plt.subplots(2, 2, figsize=(DOUBLE_COL, 5.1))

    ax = axes[0, 0]
    ax.semilogx(fast["Vmax_A_mol_m2_s"], fast["clearance_uL_min_cm2"], color=BLUE, label=r"$10\times$ apical")
    ax.semilogx(equal["Vmax_A_mol_m2_s"], equal["clearance_uL_min_cm2"], color=ORANGE, label="matched apical")
    ax.semilogx(slow["Vmax_A_mol_m2_s"], slow["clearance_uL_min_cm2"], color=GREEN, label=r"$0.1\times$ apical")
    ax.axvline(VMAX_A_EQUIV, color=GRAY, ls="--", lw=0.8)
    ax.set_xlabel(r"$V_{\max}^{A}$ (mol m$^{-2}$ s$^{-1}$)")
    ax.set_ylabel(r"Clearance ($\mu$L min$^{-1}$ cm$^{-2}$)")
    ax.legend(loc="lower right")
    panel_label(ax, "a")

    ax = axes[0, 1]
    x = fast["Vmax_A_mol_m2_s"]
    ax.loglog(x, fast["J_OAT1_mol_m2_s"], color=VERMILION, label="OAT1")
    ax.loglog(x, fast["J_membrane_capacity_mol_m2_s"], color=PURPLE, ls=":", label=r"$P_m C_{\mathrm{in}}$")
    ax.loglog(x, fast["J_OAT1_capacity_mol_m2_s"], color=ORANGE, ls=":", label=r"$V_{\max}^{A}$")
    ax.set_xlabel(r"$V_{\max}^{A}$ (mol m$^{-2}$ s$^{-1}$)")
    ax.set_ylabel(r"Flux (mol m$^{-2}$ s$^{-1}$)")
    ax.legend(loc="lower right")
    panel_label(ax, "b")

    ax = axes[1, 0]
    ax.semilogx(fast["Da"], fast["clearance_uL_min_cm2"], color=BLUE)
    ax.axvspan(1e-3, 0.3, color=GREEN, alpha=0.15, lw=0)
    ax.axvspan(3.0, 2e3, color=ORANGE, alpha=0.15, lw=0)
    ax.axvline(1.0, color=BLACK, ls="--", lw=0.8)
    ax.set_xlim(3e-3, 8e3)
    ax.set_xlabel(r"$Da$")
    ax.set_ylabel(r"Clearance ($\mu$L min$^{-1}$ cm$^{-2}$)")
    panel_label(ax, "c")

    ax = axes[1, 1]
    vmax = np.unique(m["Vmax_A_mol_m2_s"])
    eps = np.unique(m["eps_membrane"])
    cl = np.zeros((len(eps), len(vmax)))
    da = np.zeros_like(cl)
    for i, e in enumerate(eps):
        for j, v in enumerate(vmax):
            mask = (np.isclose(m["eps_membrane"], e)) & (np.isclose(m["Vmax_A_mol_m2_s"], v))
            cl[i, j] = m["clearance_uL_min_cm2"][mask][0]
            da[i, j] = m["Da"][mask][0]
    im = ax.pcolormesh(vmax, eps, cl, shading="auto", cmap="cividis")
    ax.contour(vmax, eps, da, levels=[1.0], colors="white", linewidths=0.9)
    ax.axhline(EPS_MEM, color="white", ls="--", lw=0.7)
    ax.set_xscale("log")
    ax.set_xlabel(r"$V_{\max}^{A}$ (mol m$^{-2}$ s$^{-1}$)")
    ax.set_ylabel(r"$\varepsilon$")
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.06)
    cb = fig.colorbar(im, cax=cax)
    cb.set_label(r"CL ($\mu$L min$^{-1}$ cm$^{-2}$)")
    panel_label(ax, "d")

    fig.tight_layout()
    save_figure(fig, FIG_DIR, "Fig_main_bottleneck")


CAPTIONS = """\
Fig. 1. Inside-out hollow-fiber geometry used for the surface-OAT1 formulation. The polymer membrane is a single diffusion domain. Organic anion transporter 1 (OAT1) is imposed as an areal Michaelis–Menten flux at the membrane–cell (basolateral) interface. Apical efflux is imposed at the cell–dialysate interface. There is no volumetric reaction in the cell layer.

Fig. 2. Area-normalized clearance as a function of OAT1 areal capacity Vmax^A for three apical-to-basolateral capacity ratios. The vertical dashed line marks the areal equivalent of the original volumetric Vmax = 10^6 umol L^{-1} min^{-1} distributed over a 20 um cell layer. Clearance rises with Vmax^A only at low transporter capacity and saturates once membrane diffusion limits transport.

Fig. 3. Steady interfacial fluxes versus Vmax^A when apical efflux is not limiting (Vmax^ap = 10 Vmax^A). Blood–membrane, OAT1, and apical fluxes coincide at steady state. Dotted lines show the OAT1 capacity Vmax^A and the membrane capacity Pm Cin. The operating flux follows the lower of the two capacities.

Fig. 4. Clearance versus Damkohler number Da = Vmax^A / (Pm Cin). Green: OAT1-limited regime (Da << 1). Orange: membrane-limited regime (Da >> 1). The original volumetric parameterization lies deep in the membrane-limited regime.

Fig. 5. Clearance map versus OAT1 capacity and membrane porosity. The white contour is Da = 1. The dashed line is the thesis porosity epsilon = 0.45. Increasing Vmax^A at fixed epsilon does not increase clearance once Da > 1.

Fig. 6. Ratio of the realized flux to each step's capacity. Values approaching 1 identify the rate-limiting step. At low Vmax^A the OAT1 ratio is high (transporter-limited); at high Vmax^A the membrane ratio approaches 1 (diffusion-limited).

Fig. main. Combined paper figure: (a) clearance versus Vmax^A, (b) OAT1 flux compared with membrane and transporter capacities, (c) Damkohler diagnostic, (d) clearance map with Da = 1.
"""


def write_captions() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    (FIG_DIR / "figure_captions.txt").write_text(CAPTIONS)


def main() -> None:
    require_data()
    apply_style()
    fig1_schematic()
    fig2_clearance()
    fig3_fluxes()
    fig4_damkohler()
    fig5_heatmap()
    fig6_capacity_load()
    fig_combined()
    write_captions()
    print(f"Wrote paper figures to {FIG_DIR}")
    for path in sorted(FIG_DIR.iterdir()):
        print(" ", path.name)


if __name__ == "__main__":
    main()
