"""Compare COMSOL exports of IO vs original OI vs fair OI (surface OAT1).

HOW TO USE
----------
1. Run the three Java models on university COMSOL (see
   comsol/RUN_ON_UNIVERSITY_COMSOL.md).
2. Put the exported tables under data/comsol_surface_oat1/<geometry>/.
3. From the repository root:

       python3 src/comsol_io_oi_comparison.py

If the COMSOL files are not there yet, this script still writes the geometry
table and prints the exact paths it needs. It will not invent clearance numbers.

EQUATIONS (what we plot and why)
--------------------------------
Axisymmetric molar flow through a cylindrical interface of radius r:

    n_dot(t) = ∫ J_n  2 π r  dℓ     [mol/s]                 (1)

COMSOL already exports (1) as the second column of flux_*.txt.

Clearance from that molar flow and the inlet concentration C_in:

    CL(t) = n_dot(t) / C_in         [m³/s]                  (2)

WHY we divide by C_in: clearance is the virtual blood flow that would be
wiped of toxin at concentration C_in. It is not a permeability.

Area-normalized clearance, ALWAYS using the OAT1 area of that geometry:

    A_OAT1 = 2 π R_OAT1 L                                   (3)
    CL'    = CL / A_OAT1            [m/s]                   (4)
    CL'_uL_min_cm2 = CL' * 6e6                              (5)

WHY OAT1 area and not blood–membrane area: OAT1 is the biological working
surface. Using membrane area would reward or punish a design just because
the polymer cylinder is larger, which is how the thesis "adjusted OI" looked
good on total solute but not on a fair per-cell basis.

Time-averaged clearance (thesis definition), trapezoid in time:

    CL_bar = (1 / (t_end A C_in)) ∫_0^{t_end} n_dot(τ) dτ   (6)

At steady state, (2) and (6) agree. For short T_end they can differ; we
report both.

Fair comparison rule
--------------------
IO vs OI_fair  : same A_OAT1, same V_blood, same Q_b, Q_d, C_in, wall
                 thicknesses. Unmatched: blood gap and mean dialysate speed.
IO vs OI_original : NOT fair. Shown only so you can see the thesis geometry
                 on the new physics.

Expected files
--------------
    data/comsol_surface_oat1/IO/flux_BM.txt
    data/comsol_surface_oat1/IO/flux_OAT1.txt
    data/comsol_surface_oat1/IO/flux_CD.txt
and the same three names under OI_original/ and OI_fair/.

Sweep files (optional): flux_OAT1_VmaxA_1e-7.txt
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bak_geometries import (
    C_IN,
    MPS_TO_UL_MIN_CM2,
    all_geometries,
    volumetric_flows_from_io_mean_velocity,
)
from paper_style import apply_style

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data" / "comsol_surface_oat1"
FIG = REPO / "figures" / "comsol_io_oi"
GEOMS = ("IO", "OI_original", "OI_fair")
INTERFACES = ("BM", "OAT1", "CD")


def _trap(y, x):
    fn = getattr(np, "trapezoid", None) or getattr(np, "trapz")
    return fn(y, x)


def load_flux_table(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Read COMSOL table: col0 = time (min or s), col1 = molar flow (mol/s)."""
    data = np.loadtxt(path, comments="%")
    if data.ndim == 1:
        data = data.reshape(1, -1)
    t_raw = data[:, 0]
    n_dot = data[:, 1]
    # COMSOL sometimes writes seconds. A BAK run of tens of minutes never
    # has a last time of thousands of minutes.
    t_min = t_raw / 60.0 if t_raw[-1] > 1000 else t_raw
    return t_min, n_dot


def find_exports(folder: Path) -> dict[str, Path]:
    found = {}
    for iface in INTERFACES:
        exact = folder / f"flux_{iface}.txt"
        if exact.is_file():
            found[iface] = exact
            continue
        matches = sorted(folder.glob(f"flux_{iface}*.txt"))
        if matches:
            found[iface] = matches[0]
    return found


def metrics_from_oat1(t_min: np.ndarray, n_dot: np.ndarray, a_oat1: float) -> dict:
    t_s = t_min * 60.0
    n_end = float(n_dot[-1])
    cl_end = abs(n_end) / C_IN
    cl_bar = abs(_trap(n_dot, t_s)) / (t_s[-1] * C_IN)
    return {
        "n_dot_end_mol_s": n_end,
        "CL_end_uL_min_cm2": (cl_end / a_oat1) * MPS_TO_UL_MIN_CM2,
        "CL_bar_uL_min_cm2": (cl_bar / a_oat1) * MPS_TO_UL_MIN_CM2,
        "CL_end_uL_min": cl_end * 6.0e7,  # m^3/s → µL/min
        "t_end_min": float(t_min[-1]),
    }


def write_geometry_table(path: Path) -> None:
    q_b, q_d = volumetric_flows_from_io_mean_velocity()
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, g in all_geometries().items():
        s = g.summary()
        s["Q_b_m3_s"] = q_b
        s["Q_d_m3_s"] = q_d
        rows.append(s)
    keys = sorted({k for row in rows for k in row})
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    (path.with_suffix(".json")).write_text(json.dumps(rows, indent=2, default=str))


def plot_molar_flow(series: dict, out: Path) -> None:
    apply_style()
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    for name, (t, n) in series.items():
        ax.plot(t, np.abs(n) * 1e12, label=name)
    ax.set_xlabel("Time (min)")
    ax.set_ylabel(r"$|\dot n|$ at OAT1 (pmol/s)")
    ax.set_title("COMSOL molar flow through OAT1")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def plot_clearance_bars(metrics: dict, out: Path) -> None:
    apply_style()
    names = [k for k in GEOMS if k in metrics]
    vals = [metrics[k]["CL_end_uL_min_cm2"] for k in names]
    fig, ax = plt.subplots(figsize=(5.4, 3.6))
    ax.bar(names, vals, color=["#0072B2", "#E69F00", "#009E73"][: len(names)])
    ax.set_ylabel(r"Endpoint CL ($\mu$L min$^{-1}$ cm$^{-2}$)")
    ax.set_title("Area-normalized clearance (OAT1 area)")
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def main() -> int:
    FIG.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    write_geometry_table(DATA / "geometry_table.csv")
    print("Wrote", DATA / "geometry_table.csv")
    print("Fair pair is IO vs OI_fair (same A_OAT1 and V_blood).")
    print("OI_original is the thesis control (unmatched area and volume).\n")

    missing = []
    series = {}
    metrics = {}
    geoms = all_geometries()
    for name in GEOMS:
        folder = DATA / name
        folder.mkdir(parents=True, exist_ok=True)
        found = find_exports(folder)
        if "OAT1" not in found:
            missing.append(str(folder / "flux_OAT1.txt"))
            continue
        t, n = load_flux_table(found["OAT1"])
        series[name] = (t, n)
        metrics[name] = metrics_from_oat1(t, n, geoms[name].a_oat1)
        print(f"{name:14s}  CL_end = {metrics[name]['CL_end_uL_min_cm2']:.4f} "
              f"uL/min/cm2   (t={metrics[name]['t_end_min']:.1f} min)")

    if missing:
        print("\nNo (or incomplete) COMSOL exports yet. Put tables at:")
        for p in missing:
            print("  ", p)
        print("\nAlso export flux_BM.txt and flux_CD.txt in the same folders.")
        print("Until then there is nothing physical to plot from COMSOL.")
        return 0

    plot_molar_flow(series, FIG / "oat1_molar_flow_vs_time.png")
    plot_clearance_bars(metrics, FIG / "clearance_endpoint_bars.png")
    out_csv = DATA / "comparison_metrics.csv"
    with out_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["geometry", *next(iter(metrics.values()))])
        w.writeheader()
        for k, row in metrics.items():
            w.writerow({"geometry": k, **row})
    print("Wrote figures in", FIG)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
