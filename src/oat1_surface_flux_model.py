"""Steady 1D axisymmetric model of OAT1 as a basolateral surface flux.

The polymer membrane remains one diffusion domain. Active transport is not a
volumetric Michaelis-Menten sink in the cell. Instead:

  blood (fixed c = C_in at the blood-membrane face)
    -> membrane diffusion
    -> OAT1 flux at the membrane-cell interface (basolateral)
    -> cell diffusion
    -> apical efflux flux at the cell-dialysate interface
    -> dialysate (c = 0)

This isolates whether OAT1 flux is the bottleneck for clearance.

Run from the repository root:

    python src/oat1_surface_flux_model.py
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares

# ---------------------------------------------------------------------------
# Inside-out geometry and parameters from the project
# ---------------------------------------------------------------------------

R_BM = 0.15e-3  # m, blood-membrane interface
R_MC = 0.25e-3  # m, membrane-cell (basolateral / OAT1) interface
R_CD = 0.27e-3  # m, cell-dialysate (apical) interface
DELTA_CELL = R_CD - R_MC  # 20 um

D_IS = 5.58e-10  # m^2/s, IS diffusivity in blood/cell/dialysate
EPS_MEM = 0.45
D_MEM = EPS_MEM * D_IS
D_CELL = D_IS

C_IN = 0.1  # mol/m^3 = 100 uM
K_M = 0.02  # mol/m^3 = 20 uM
K_M_AP = 0.02

# Baseline volumetric Vmax used in the original COMSOL cell-domain reaction
VMAX_VOL_BASE_UMOL_L_MIN = 1.0e6
# 1e6 umol/(L min) = 1000 mol/(m^3 min) = 1000/60 mol/(m^3 s)
VMAX_VOL_BASE = (VMAX_VOL_BASE_UMOL_L_MIN * 1.0e-3) / 60.0  # mol/(m^3 s)
# Equivalent areal capacity if that volume reaction is collapsed onto 20 um
VMAX_A_EQUIV = VMAX_VOL_BASE * DELTA_CELL  # mol/(m^2 s)

MPS_TO_UL_MIN_CM2 = 6.0e6

REPO_ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = REPO_ROOT / "figures" / "oat1_bottleneck"
DATA_DIR = REPO_ROOT / "data" / "oat1_surface_flux"


def membrane_permeance() -> float:
    """Effective membrane permeance [m/s] referred to the OAT1 surface (r = R_MC)."""
    return D_MEM / (R_MC * np.log(R_MC / R_BM))


def damkohler(vmax_a: float, c_ref: float = C_IN) -> float:
    """Da = Vmax^A / (P_m * C_ref). Da << 1: OAT1-limited. Da >> 1: membrane-limited."""
    return vmax_a / (membrane_permeance() * c_ref)


def mm(c: float, vmax: float, km: float) -> float:
    c = max(c, 0.0)
    return vmax * c / (km + c)


def solve_surface_oat1(vmax_bl: float, vmax_ap: float, d_mem: float = D_MEM, x0=None):
    """Solve steady radial chain with reversible OAT1 and irreversible apical efflux.

    Unknowns: Phi' [mol/s/m], c_extra at r=R_MC, c_cell at r=R_MC, c_cell at r=R_CD.

    OAT1 net flux (mol/m^2/s), reversible Michaelis-Menten:
        J_bl = Vmax_bl * (c_e/(Km+c_e) - c_i/(Km+c_i))
    Apical efflux into toxin-free dialysate:
        J_ap = Vmax_ap * c_ap / (Km_ap + c_ap)
    """

    p_m = d_mem / (R_MC * np.log(R_MC / R_BM))
    phi_max = 2.0 * np.pi * R_MC * p_m * C_IN * 1.25

    def residual(x):
        phi, ce, ci_in, ci_ap = x
        j_bl = mm(ce, vmax_bl, K_M) - mm(ci_in, vmax_bl, K_M)
        j_ap = mm(ci_ap, vmax_ap, K_M_AP)
        ce_from_phi = C_IN - phi * np.log(R_MC / R_BM) / (2.0 * np.pi * d_mem)
        phi_from_oat1 = 2.0 * np.pi * R_MC * j_bl
        phi_from_cell = (
            2.0 * np.pi * D_CELL * (ci_in - ci_ap) / np.log(R_CD / R_MC)
        )
        phi_from_apical = 2.0 * np.pi * R_CD * j_ap
        scale_phi = max(phi_max, 1e-16)
        return np.array(
            [
                (ce - ce_from_phi) / C_IN,
                (phi - phi_from_oat1) / scale_phi,
                (phi - phi_from_cell) / scale_phi,
                (phi - phi_from_apical) / scale_phi,
            ]
        )

    j_guess = min(vmax_bl * C_IN / (K_M + C_IN), p_m * C_IN) * 0.5
    phi_guess = 2.0 * np.pi * R_MC * j_guess
    if x0 is None:
        x0 = np.array([phi_guess, 0.7 * C_IN, 0.05 * C_IN, 0.03 * C_IN])

    lb = np.array([0.0, 0.0, 0.0, 0.0])
    ub = np.array([phi_max, C_IN, C_IN, C_IN])
    x0 = np.clip(x0, lb + 1e-18, ub - 1e-18)

    sol = least_squares(residual, x0, bounds=(lb, ub), xtol=1e-12, ftol=1e-12, max_nfev=400)

    phi, ce, ci_in, ci_ap = sol.x
    j_oat1 = phi / (2.0 * np.pi * R_MC)
    j_bm = phi / (2.0 * np.pi * R_BM)
    j_cd = phi / (2.0 * np.pi * R_CD)
    cl_m_s = j_oat1 / C_IN
    return {
        "success": bool(sol.success) and float(np.linalg.norm(sol.fun)) < 1e-8,
        "phi_per_length": phi,
        "c_extra_mc": ce,
        "c_cell_mc": ci_in,
        "c_cell_cd": ci_ap,
        "j_bm": j_bm,
        "j_oat1": j_oat1,
        "j_cd": j_cd,
        "cl_m_s": cl_m_s,
        "cl_uL_min_cm2": abs(cl_m_s) * MPS_TO_UL_MIN_CM2,
        "Da": vmax_bl / (p_m * C_IN),
        "j_oat1_capacity": vmax_bl,
        "j_apical_capacity": vmax_ap,
        "j_membrane_capacity": p_m * C_IN,
        "_x": sol.x,
    }


def classify_bottleneck(result: dict, rel_tol: float = 0.15) -> str:
    """Identify the capacity that is closest to the actual flux."""
    j = result["j_oat1"]
    loads = {
        "OAT1": j / max(result["j_oat1_capacity"], 1e-30),
        "apical": (result["j_cd"]) / max(result["j_apical_capacity"], 1e-30),
        "membrane": j / max(result["j_membrane_capacity"], 1e-30),
    }
    name = max(loads, key=loads.get)
    if result["Da"] < 0.3 and name == "OAT1":
        return "OAT1"
    if result["Da"] > 3.0 or name == "membrane":
        if loads["membrane"] >= loads["OAT1"] - rel_tol:
            return "membrane"
    if name == "apical" and loads["apical"] > loads["OAT1"]:
        return "apical"
    return name


def sweep_vmax(vmax_values: np.ndarray, apical_ratio: float) -> list[dict]:
    rows = []
    x0 = None
    for vmax_bl in vmax_values:
        vmax_ap = apical_ratio * vmax_bl
        res = solve_surface_oat1(vmax_bl, vmax_ap, x0=x0)
        x0 = res.get("_x")
        res["vmax_bl"] = vmax_bl
        res["vmax_ap"] = vmax_ap
        res["apical_ratio"] = apical_ratio
        res["bottleneck"] = classify_bottleneck(res)
        rows.append(res)
    return rows


def sweep_membrane_map(
    vmax_values: np.ndarray, eps_values: np.ndarray, apical_ratio: float = 10.0
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    cl = np.zeros((len(eps_values), len(vmax_values)))
    for i, eps in enumerate(eps_values):
        d_mem = eps * D_IS
        x0 = None
        for j, vmax_bl in enumerate(vmax_values):
            res = solve_surface_oat1(
                vmax_bl, apical_ratio * vmax_bl, d_mem=d_mem, x0=x0
            )
            x0 = res.get("_x")
            cl[i, j] = res["cl_uL_min_cm2"] if res["success"] else np.nan
    return vmax_values, eps_values, cl


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = [
        "vmax_bl",
        "vmax_ap",
        "Da",
        "cl_uL_min_cm2",
        "j_bm",
        "j_oat1",
        "j_cd",
        "c_extra_mc",
        "c_cell_mc",
        "c_cell_cd",
        "j_oat1_capacity",
        "j_membrane_capacity",
        "bottleneck",
        "success",
    ]
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k) for k in keys})


def plot_clearance_and_fluxes(rows: list[dict], title_suffix: str, stem: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    vmax = np.array([r["vmax_bl"] for r in rows])
    cl = np.array([r["cl_uL_min_cm2"] for r in rows])
    da = np.array([r["Da"] for r in rows])
    j_bm = np.array([r["j_bm"] for r in rows])
    j_oat1 = np.array([r["j_oat1"] for r in rows])
    j_cd = np.array([r["j_cd"] for r in rows])
    j_oat1_cap = np.array([r["j_oat1_capacity"] for r in rows])
    j_mem_cap = np.array([r["j_membrane_capacity"] for r in rows])

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8), dpi=140)

    ax = axes[0]
    ax.semilogx(vmax, cl, color="tab:blue", lw=2.4)
    ax.axvline(VMAX_A_EQUIV, color="gray", ls="--", lw=1.4, label="volumetric $V_{max}$ equivalent")
    # Da = 1 marker
    if np.any(da >= 1.0) and np.any(da < 1.0):
        vmax_da1 = np.interp(1.0, da, vmax)
        ax.axvline(vmax_da1, color="tab:red", ls=":", lw=1.4, label=r"$Da=1$")
    ax.set_xlabel(r"$V_{\max}^{A}$ (mol m$^{-2}$ s$^{-1}$)")
    ax.set_ylabel(r"Clearance ($\mu$L min$^{-1}$ cm$^{-2}$)")
    ax.set_title("Clearance vs OAT1 capacity")
    ax.legend(fontsize=9)
    ax.grid(True, which="both", alpha=0.3)

    ax = axes[1]
    ax.loglog(vmax, j_bm, lw=2.0, label=r"$J$ blood-membrane")
    ax.loglog(vmax, j_oat1, lw=2.0, label=r"$J$ OAT1")
    ax.loglog(vmax, j_cd, lw=2.0, ls="--", label=r"$J$ cell-dialysate")
    ax.loglog(vmax, j_oat1_cap, color="tab:green", ls=":", lw=1.6, label=r"$V_{\max}^{A}$ (OAT1 cap.)")
    ax.loglog(vmax, j_mem_cap, color="tab:orange", ls=":", lw=1.6, label=r"$P_m C_{in}$ (membrane cap.)")
    ax.set_xlabel(r"$V_{\max}^{A}$ (mol m$^{-2}$ s$^{-1}$)")
    ax.set_ylabel(r"Flux (mol m$^{-2}$ s$^{-1}$)")
    ax.set_title("Interface fluxes")
    ax.legend(fontsize=8)
    ax.grid(True, which="both", alpha=0.3)

    fig.suptitle(title_suffix, fontsize=13)
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"{stem}.png")
    plt.close(fig)


def plot_da_regimes(rows: list[dict], stem: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    vmax = np.array([r["vmax_bl"] for r in rows])
    da = np.array([r["Da"] for r in rows])
    cl = np.array([r["cl_uL_min_cm2"] for r in rows])

    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=140)
    ax.semilogx(da, cl, color="tab:purple", lw=2.4)
    ax.axvspan(1e-3, 0.3, color="tab:green", alpha=0.12, label="OAT1-limited ($Da\\ll 1$)")
    ax.axvspan(3.0, 1e4, color="tab:orange", alpha=0.12, label="membrane-limited ($Da\\gg 1$)")
    ax.axvline(1.0, color="k", ls="--", lw=1.0)
    ax.set_xlabel(r"$Da = V_{\max}^{A}/(P_m C_{in})$")
    ax.set_ylabel(r"Clearance ($\mu$L min$^{-1}$ cm$^{-2}$)")
    ax.set_title("Bottleneck diagnostic")
    ax.legend(fontsize=9)
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"{stem}.png")
    plt.close(fig)
    _ = vmax


def plot_membrane_map(vmax_values, eps_values, cl, stem: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.4, 5.0), dpi=140)
    im = ax.pcolormesh(
        vmax_values,
        eps_values,
        cl,
        shading="auto",
        cmap="viridis",
    )
    cb = fig.colorbar(im, ax=ax)
    cb.set_label(r"Clearance ($\mu$L min$^{-1}$ cm$^{-2}$)")
    ax.set_xscale("log")
    ax.set_xlabel(r"$V_{\max}^{A}$ (mol m$^{-2}$ s$^{-1}$)")
    ax.set_ylabel(r"Membrane porosity $\varepsilon$")
    ax.axhline(EPS_MEM, color="white", ls="--", lw=1.2, label=r"thesis $\varepsilon=0.45$")
    ax.legend(loc="upper left", fontsize=9, labelcolor="white")
    ax.set_title("Clearance map: OAT1 capacity vs membrane permeance")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"{stem}.png")
    plt.close(fig)


def print_summary(rows: list[dict], label: str) -> None:
    print(f"\n=== {label} ===")
    print(f"{'Vmax_A':>12} {'Da':>10} {'CL':>10} {'J_OAT1/Vmax':>14} {'J/Jmem':>10} {'bottleneck':>12}")
    for r in rows:
        load_oat = r["j_oat1"] / max(r["j_oat1_capacity"], 1e-30)
        load_mem = r["j_oat1"] / max(r["j_membrane_capacity"], 1e-30)
        print(
            f"{r['vmax_bl']:12.3e} {r['Da']:10.3e} {r['cl_uL_min_cm2']:10.4f} "
            f"{load_oat:14.3f} {load_mem:10.3f} {r['bottleneck']:>12}"
        )


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    print("Inside-out surface-OAT1 radial chain")
    print(f"  P_m (at r=R_MC)     = {membrane_permeance():.4e} m/s")
    print(f"  P_m * C_in          = {membrane_permeance() * C_IN:.4e} mol/m^2/s")
    print(f"  Vmax^A equivalent   = {VMAX_A_EQUIV:.4e} mol/m^2/s  (from 1e6 umol/L/min over 20 um)")
    print(f"  Da at equivalent    = {damkohler(VMAX_A_EQUIV):.4e}")

    # Sweep from well below membrane capacity to well above it
    vmax_values = np.logspace(-9, -3, 41)

    sweeps = {}
    rows_fast_apical = sweep_vmax(vmax_values, apical_ratio=10.0)
    write_csv(DATA_DIR / "sweep_vmaxA_apical_fast.csv", rows_fast_apical)
    sweeps["apical_fast"] = rows_fast_apical
    plot_clearance_and_fluxes(
        rows_fast_apical,
        "Apical efflux not limiting ($V_{max}^{ap}=10\\,V_{max}^{A}$)",
        "clearance_fluxes_apical_fast",
    )
    plot_da_regimes(rows_fast_apical, "da_regimes_apical_fast")
    print_summary(rows_fast_apical[::4], "Apical 10x OAT1")

    rows_equal_apical = sweep_vmax(vmax_values, apical_ratio=1.0)
    write_csv(DATA_DIR / "sweep_vmaxA_apical_equal.csv", rows_equal_apical)
    sweeps["apical_equal"] = rows_equal_apical
    plot_clearance_and_fluxes(
        rows_equal_apical,
        "Matched apical capacity ($V_{max}^{ap}=V_{max}^{A}$)",
        "clearance_fluxes_apical_equal",
    )
    print_summary(rows_equal_apical[::4], "Apical = OAT1")

    rows_slow_apical = sweep_vmax(vmax_values, apical_ratio=0.1)
    write_csv(DATA_DIR / "sweep_vmaxA_apical_slow.csv", rows_slow_apical)
    sweeps["apical_slow"] = rows_slow_apical
    plot_clearance_and_fluxes(
        rows_slow_apical,
        "Apical bottleneck ($V_{max}^{ap}=0.1\\,V_{max}^{A}$)",
        "clearance_fluxes_apical_slow",
    )
    print_summary(rows_slow_apical[::4], "Apical 0.1x OAT1")

    eps_values = np.linspace(0.1, 0.9, 17)
    vmax_map = np.logspace(-9, -3, 25)
    _, _, cl_map = sweep_membrane_map(vmax_map, eps_values, apical_ratio=10.0)
    plot_membrane_map(vmax_map, eps_values, cl_map, "clearance_map_vmaxA_vs_porosity")

    np.savetxt(DATA_DIR / "map_vmaxA.txt", vmax_map)
    np.savetxt(DATA_DIR / "map_eps.txt", eps_values)
    np.savetxt(DATA_DIR / "map_clearance_uL_min_cm2.txt", cl_map)

    from oat1_data_io import convert_all_comsol_exports, save_all_model_data

    paper_dir = save_all_model_data(
        sweeps, vmax_map, eps_values, cl_map, map_apical_ratio=10.0
    )
    n_comsol = convert_all_comsol_exports(DATA_DIR)
    print(f"\nWrote figures to {FIG_DIR}")
    print(f"Wrote tables to {DATA_DIR}")
    print(f"Wrote paper-ready data to {paper_dir}")
    if n_comsol:
        print(f"Converted {len(n_comsol)} COMSOL flux tables")
    print("Paper figures: python src/paper_figures_oat1.py")


if __name__ == "__main__":
    main()
