"""Save and load OAT1 bottleneck data for paper figures and COMSOL exports."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data" / "oat1_surface_flux"
PAPER_DIR = DATA_DIR / "paper"

SWEEP_COLUMNS = [
    "Vmax_A_mol_m2_s",
    "Vmax_ap_mol_m2_s",
    "apical_ratio",
    "Da",
    "clearance_uL_min_cm2",
    "J_BM_mol_m2_s",
    "J_OAT1_mol_m2_s",
    "J_CD_mol_m2_s",
    "c_extra_MC_mol_m3",
    "c_cell_MC_mol_m3",
    "c_cell_CD_mol_m3",
    "J_OAT1_capacity_mol_m2_s",
    "J_membrane_capacity_mol_m2_s",
    "J_apical_capacity_mol_m2_s",
    "bottleneck",
    "success",
]


def _row_from_solver(row: dict) -> dict:
    return {
        "Vmax_A_mol_m2_s": row["vmax_bl"],
        "Vmax_ap_mol_m2_s": row["vmax_ap"],
        "apical_ratio": row["apical_ratio"],
        "Da": row["Da"],
        "clearance_uL_min_cm2": row["cl_uL_min_cm2"],
        "J_BM_mol_m2_s": row["j_bm"],
        "J_OAT1_mol_m2_s": row["j_oat1"],
        "J_CD_mol_m2_s": row["j_cd"],
        "c_extra_MC_mol_m3": row["c_extra_mc"],
        "c_cell_MC_mol_m3": row["c_cell_mc"],
        "c_cell_CD_mol_m3": row["c_cell_cd"],
        "J_OAT1_capacity_mol_m2_s": row["j_oat1_capacity"],
        "J_membrane_capacity_mol_m2_s": row["j_membrane_capacity"],
        "J_apical_capacity_mol_m2_s": row["j_apical_capacity"],
        "bottleneck": row["bottleneck"],
        "success": row["success"],
    }


def save_parameters(path: Path, extra: dict | None = None) -> None:
    from oat1_surface_flux_model import (
        C_IN,
        D_CELL,
        D_IS,
        D_MEM,
        DELTA_CELL,
        EPS_MEM,
        K_M,
        K_M_AP,
        R_BM,
        R_CD,
        R_MC,
        VMAX_A_EQUIV,
        membrane_permeance,
    )

    payload = {
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "geometry": {
            "configuration": "inside-out",
            "R_blood_membrane_m": R_BM,
            "R_membrane_cell_m": R_MC,
            "R_cell_dialysate_m": R_CD,
            "cell_thickness_m": DELTA_CELL,
        },
        "transport": {
            "D_IS_m2_s": D_IS,
            "D_cell_m2_s": D_CELL,
            "eps_membrane": EPS_MEM,
            "D_membrane_m2_s": D_MEM,
            "P_membrane_m_s": membrane_permeance(),
            "C_in_mol_m3": C_IN,
            "Km_OAT1_mol_m3": K_M,
            "Km_apical_mol_m3": K_M_AP,
            "Vmax_A_volumetric_equivalent_mol_m2_s": VMAX_A_EQUIV,
        },
        "notes": (
            "OAT1 is an areal flux at the membrane-cell interface. "
            "Apical efflux is an areal flux at the cell-dialysate interface. "
            "The polymer membrane is a single diffusion domain."
        ),
    }
    if extra:
        payload.update(extra)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def save_sweep_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SWEEP_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(_row_from_solver(row))


def save_map_tidy(
    path: Path,
    vmax_values: np.ndarray,
    eps_values: np.ndarray,
    cl: np.ndarray,
    apical_ratio: float,
) -> None:
    """Save clearance map as one row per (Vmax_A, epsilon) for plotting/stats."""
    from oat1_surface_flux_model import C_IN, D_IS, R_BM, R_MC

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Vmax_A_mol_m2_s",
                "eps_membrane",
                "apical_ratio",
                "Da",
                "clearance_uL_min_cm2",
            ]
        )
        ln = np.log(R_MC / R_BM)
        for i, eps in enumerate(eps_values):
            p_m = (eps * D_IS) / (R_MC * ln)
            for j, vmax in enumerate(vmax_values):
                da = vmax / (p_m * C_IN)
                writer.writerow([vmax, eps, apical_ratio, da, cl[i, j]])


def load_sweep_csv(path: Path) -> dict[str, np.ndarray]:
    with path.open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    out: dict[str, list] = {k: [] for k in SWEEP_COLUMNS}
    for row in rows:
        for key in SWEEP_COLUMNS:
            val = row[key]
            if key in {"bottleneck", "success"}:
                out[key].append(val)
            else:
                out[key].append(float(val))
    arrays: dict[str, np.ndarray] = {}
    for key, values in out.items():
        if key in {"bottleneck", "success"}:
            arrays[key] = np.array(values)
        else:
            arrays[key] = np.array(values, dtype=float)
    return arrays


def load_map_tidy(path: Path) -> dict[str, np.ndarray]:
    with path.open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    keys = list(rows[0].keys()) if rows else []
    out = {k: np.array([float(r[k]) for r in rows], dtype=float) for k in keys}
    return out


def convert_comsol_flux_txt(src: Path, dest: Path) -> None:
    """Rewrite a COMSOL % table as a clean two-column CSV (time_min, flux_mol_s)."""
    raw = np.loadtxt(src, comments="%")
    if raw.ndim == 1:
        raw = raw.reshape(1, -1)
    time_raw = raw[:, 0]
    flux = raw[:, 1]
    time_min = time_raw / 60.0 if time_raw[-1] > 1000 else time_raw
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["time_min", "flux_mol_s", "source_file"])
        for t, j in zip(time_min, flux):
            writer.writerow([f"{t:.8g}", f"{j:.8e}", src.name])


def convert_all_comsol_exports(data_dir: Path | None = None) -> list[Path]:
    data_dir = data_dir or DATA_DIR
    out_dir = PAPER_DIR / "comsol"
    written = []
    for path in sorted(data_dir.glob("flux_*_VmaxA_*.txt")):
        dest = out_dir / f"{path.stem}.csv"
        convert_comsol_flux_txt(path, dest)
        written.append(dest)
    return written


def save_all_model_data(
    sweeps: dict[str, list[dict]],
    vmax_map: np.ndarray,
    eps_map: np.ndarray,
    cl_map: np.ndarray,
    map_apical_ratio: float = 10.0,
) -> Path:
    PAPER_DIR.mkdir(parents=True, exist_ok=True)
    save_parameters(PAPER_DIR / "parameters.json")
    for name, rows in sweeps.items():
        save_sweep_csv(PAPER_DIR / f"sweep_{name}.csv", rows)
    save_map_tidy(
        PAPER_DIR / "map_clearance_tidy.csv",
        vmax_map,
        eps_map,
        cl_map,
        map_apical_ratio,
    )
    np.savetxt(PAPER_DIR / "map_Vmax_A.txt", vmax_map, header="Vmax_A_mol_m2_s")
    np.savetxt(PAPER_DIR / "map_eps_membrane.txt", eps_map, header="eps_membrane")
    np.savetxt(PAPER_DIR / "map_clearance_uL_min_cm2.txt", cl_map)
    (PAPER_DIR / "DATA_DICTIONARY.txt").write_text(
        "sweep_*.csv columns\n"
        "  Vmax_A_mol_m2_s              OAT1 areal capacity\n"
        "  Vmax_ap_mol_m2_s             apical areal capacity\n"
        "  apical_ratio                 Vmax_ap / Vmax_A\n"
        "  Da                           Vmax_A / (P_m * C_in)\n"
        "  clearance_uL_min_cm2         area-normalized clearance at OAT1 surface\n"
        "  J_BM_mol_m2_s                flux at blood-membrane interface\n"
        "  J_OAT1_mol_m2_s              flux at membrane-cell (OAT1) interface\n"
        "  J_CD_mol_m2_s                flux at cell-dialysate (apical) interface\n"
        "  c_*_mol_m3                   interface concentrations\n"
        "  J_*_capacity_mol_m2_s        capacity of that step\n"
        "  bottleneck                   classified limiting step\n"
        "\n"
        "map_clearance_tidy.csv         one row per (Vmax_A, epsilon)\n"
        "parameters.json                geometry and transport constants\n"
        "comsol/*.csv                   cleaned COMSOL time-flux tables\n"
    )
    return PAPER_DIR


if __name__ == "__main__":
    written = convert_all_comsol_exports()
    print(f"Converted {len(written)} COMSOL tables into {PAPER_DIR / 'comsol'}")
