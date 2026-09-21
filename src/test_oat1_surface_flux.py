"""Sanity checks for the surface-OAT1 radial chain."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from oat1_surface_flux_model import (
    C_IN,
    D_MEM,
    R_BM,
    R_MC,
    damkohler,
    membrane_permeance,
    solve_surface_oat1,
    sweep_vmax,
)


def test_low_vmax_is_oat1_limited():
    vmax = 1e-9
    res = solve_surface_oat1(vmax, 10 * vmax)
    assert res["success"]
    assert res["Da"] < 0.3
    # Flux cannot exceed OAT1 capacity
    assert res["j_oat1"] <= vmax * 1.05
    # Clearance should scale with Vmax when Da << 1
    res2 = solve_surface_oat1(2 * vmax, 20 * vmax)
    assert res2["cl_uL_min_cm2"] > 1.5 * res["cl_uL_min_cm2"]


def test_high_vmax_is_membrane_limited():
    vmax = 1e-4
    res = solve_surface_oat1(vmax, 10 * vmax)
    assert res["success"]
    assert res["Da"] > 3.0
    p_m = membrane_permeance()
    j_mem_cap = p_m * C_IN
    assert res["j_oat1"] < j_mem_cap * 1.05
    # Further increasing Vmax should barely change clearance
    res2 = solve_surface_oat1(3 * vmax, 30 * vmax)
    rel = abs(res2["cl_uL_min_cm2"] - res["cl_uL_min_cm2"]) / res["cl_uL_min_cm2"]
    assert rel < 0.15


def test_steady_fluxes_match_along_chain():
    res = solve_surface_oat1(1e-7, 1e-6)
    phi = res["phi_per_length"]
    assert np.isclose(phi, 2 * np.pi * R_BM * res["j_bm"], rtol=1e-4)
    assert np.isclose(phi, 2 * np.pi * R_MC * res["j_oat1"], rtol=1e-4)
    assert np.isclose(phi, 2 * np.pi * 0.27e-3 * res["j_cd"], rtol=1e-4)


def test_damkohler_definition():
    p_m = D_MEM / (R_MC * np.log(R_MC / R_BM))
    assert np.isclose(membrane_permeance(), p_m)
    vmax = p_m * C_IN
    assert np.isclose(damkohler(vmax), 1.0)


def test_sweep_monotonic_then_plateau():
    vmax = np.logspace(-9, -4, 12)
    rows = sweep_vmax(vmax, apical_ratio=10.0)
    cl = np.array([r["cl_uL_min_cm2"] for r in rows])
    assert np.all(np.diff(cl) >= -1e-6)
    # Last increments much smaller than early rise (membrane plateau)
    early = cl[3] - cl[0]
    late = cl[-1] - cl[-3]
    assert late < 0.25 * early
