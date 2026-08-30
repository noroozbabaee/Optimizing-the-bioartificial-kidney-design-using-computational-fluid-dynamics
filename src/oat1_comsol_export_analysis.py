"""Post-process COMSOL exports for the surface-OAT1 bottleneck test.

Expected files in data/oat1_surface_flux/ (COMSOL line-integration tables):

    flux_BM_VmaxA_<tag>.txt
    flux_OAT1_VmaxA_<tag>.txt
    flux_CD_VmaxA_<tag>.txt

Each file is a COMSOL table:

    % Time (min)    Normal total flux (mol/s)

The tag encodes areal Vmax, e.g. 1e-8. A parameter list file is optional:

    vmaxA_list.txt   # one value per line, mol/(m^2 s)

If COMSOL files are not present, this script reports what to export and exits 0
after checking the 1D model tables produced by oat1_surface_flux_model.py.

Run from the repository root:

    python src/oat1_comsol_export_analysis.py
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data" / "oat1_surface_flux"
FIG_DIR = REPO_ROOT / "figures" / "oat1_bottleneck"

C_IN = 0.1
A_IO_M2 = 31.42e-6  # inside-out outer membrane area
MPS_TO_UL_MIN_CM2 = 6.0e6


def load_flux_table(path: Path) -> tuple[np.ndarray, np.ndarray]:
    data = np.loadtxt(path, comments="%")
    if data.ndim == 1:
        data = data.reshape(1, -1)
    time_raw = data[:, 0]
    flux = data[:, 1]
    if time_raw[-1] > 1000:
        time_min = time_raw / 60.0
    else:
        time_min = time_raw
    return time_min, flux


def end_point_clearance(flux_mol_s: np.ndarray, time_min: np.ndarray, area_m2: float) -> float:
    time_sec = time_min * 60.0
    trap = getattr(np, "trapezoid", None) or getattr(np, "trapz")
    total_mol = trap(flux_mol_s, time_sec)
    cl_m_s = total_mol / (time_sec[-1] * area_m2 * C_IN)
    return abs(cl_m_s * MPS_TO_UL_MIN_CM2)


def end_point_flux(flux_mol_s: np.ndarray) -> float:
    return float(flux_mol_s[-1])


def find_comsol_sweeps(data_dir: Path) -> dict[str, dict[str, Path]]:
    """Group files by Vmax tag: {tag: {BM: path, OAT1: path, CD: path}}."""
    groups: dict[str, dict[str, Path]] = {}
    for path in sorted(data_dir.glob("flux_*_VmaxA_*.txt")):
        name = path.stem
        # flux_BM_VmaxA_1e-8 -> interface=BM, tag=1e-8
        try:
            _, iface, _, tag = name.split("_", 3)
        except ValueError:
            continue
        groups.setdefault(tag, {})[iface] = path
    return groups


def plot_comsol_sweep(tags, vmax, cl, j_bm, j_oat1, j_cd) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8), dpi=140)

    axes[0].semilogx(vmax, cl, "o-", lw=2.0)
    axes[0].set_xlabel(r"$V_{\max}^{A}$ (mol m$^{-2}$ s$^{-1}$)")
    axes[0].set_ylabel(r"Clearance ($\mu$L min$^{-1}$ cm$^{-2}$)")
    axes[0].set_title("COMSOL: clearance vs OAT1 $V_{max}^{A}$")
    axes[0].grid(True, which="both", alpha=0.3)

    axes[1].loglog(vmax, np.abs(j_bm), "o-", label="BM")
    axes[1].loglog(vmax, np.abs(j_oat1), "s-", label="OAT1")
    axes[1].loglog(vmax, np.abs(j_cd), "^-", label="CD")
    axes[1].set_xlabel(r"$V_{\max}^{A}$ (mol m$^{-2}$ s$^{-1}$)")
    axes[1].set_ylabel("End-point molar flow (mol/s)")
    axes[1].set_title("COMSOL: three interface fluxes")
    axes[1].legend()
    axes[1].grid(True, which="both", alpha=0.3)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "comsol_oat1_bottleneck_sweep.png")
    plt.close(fig)
    _ = tags


def analyze_comsol_exports() -> bool:
    groups = find_comsol_sweeps(DATA_DIR)
    complete = {k: v for k, v in groups.items() if {"BM", "OAT1", "CD"} <= set(v)}
    if not complete:
        print("No complete COMSOL OAT1 sweep found in", DATA_DIR)
        print("Export, for each Vmax^A, three line integrals:")
        print("  flux_BM_VmaxA_<value>.txt    blood-membrane")
        print("  flux_OAT1_VmaxA_<value>.txt  membrane-cell (OAT1 surface)")
        print("  flux_CD_VmaxA_<value>.txt    cell-dialysate (apical)")
        return False

    rows = []
    for tag, files in sorted(complete.items(), key=lambda kv: float(kv[0].replace("e", "e"))):
        try:
            vmax = float(tag.replace("p", "."))
        except ValueError:
            continue
        t_bm, f_bm = load_flux_table(files["BM"])
        _, f_oat1 = load_flux_table(files["OAT1"])
        _, f_cd = load_flux_table(files["CD"])
        rows.append(
            {
                "tag": tag,
                "vmax_bl": vmax,
                "cl": end_point_clearance(f_bm, t_bm, A_IO_M2),
                "phi_bm": end_point_flux(f_bm),
                "phi_oat1": end_point_flux(f_oat1),
                "phi_cd": end_point_flux(f_cd),
            }
        )

    if not rows:
        return False

    vmax = np.array([r["vmax_bl"] for r in rows])
    cl = np.array([r["cl"] for r in rows])
    j_bm = np.array([r["phi_bm"] for r in rows])
    j_oat1 = np.array([r["phi_oat1"] for r in rows])
    j_cd = np.array([r["phi_cd"] for r in rows])
    plot_comsol_sweep([r["tag"] for r in rows], vmax, cl, j_bm, j_oat1, j_cd)

    out = DATA_DIR / "comsol_oat1_sweep_summary.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("Wrote", out)
    print("Wrote", FIG_DIR / "comsol_oat1_bottleneck_sweep.png")

    # Bottleneck hint from dCL / d log Vmax
    if len(vmax) >= 3:
        dlogv = np.diff(np.log10(vmax))
        dcl = np.diff(cl)
        slope = dcl / np.where(dlogv == 0, np.nan, dlogv)
        print("d(CL)/d(log10 Vmax^A) midpoint slopes:")
        for vmid, s in zip(0.5 * (vmax[1:] + vmax[:-1]), slope):
            print(f"  Vmax^A ~ {vmid:.3e}  slope = {s:.4f}")
        print("Near-zero slope => OAT1 is not the clearance bottleneck.")
        print("Large positive slope => OAT1 is rate-limiting.")
    return True


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    found = analyze_comsol_exports()
    model_csv = DATA_DIR / "sweep_vmaxA_apical_fast.csv"
    if model_csv.exists():
        print("1D surface-OAT1 sweep available at", model_csv)
    elif not found:
        print("Run python src/oat1_surface_flux_model.py first to generate the 1D diagnostic.")


if __name__ == "__main__":
    main()
