"""Unit tests: fair OI must match IO OAT1 area and blood volume."""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bak_geometries import (
    DELTA_CELL_M,
    DELTA_MEM_M,
    inside_out,
    outside_in_fair,
    outside_in_original,
    volumetric_flows_from_io_mean_velocity,
)


def test_fair_matches_io_area_and_blood_volume():
    io = inside_out()
    fair = outside_in_fair()
    assert math.isclose(fair.a_oat1, io.a_oat1, rel_tol=1e-12)
    assert math.isclose(fair.v_blood, io.v_blood, rel_tol=1e-12)
    assert math.isclose(fair.r_oat1 - fair.r_apical, DELTA_CELL_M, rel_tol=1e-12)
    assert math.isclose(fair.r_blood_membrane - fair.r_oat1, DELTA_MEM_M, rel_tol=1e-12)


def test_original_oi_is_not_fair():
    io = inside_out()
    orig = outside_in_original()
    assert orig.a_oat1 < io.a_oat1
    assert orig.v_blood > 10 * io.v_blood


def test_io_stack_order():
    io = inside_out()
    assert io.lumen_fluid == "blood"
    assert io.r_blood_membrane < io.r_oat1 < io.r_apical < io.r_housing


def test_oi_stack_order():
    for g in (outside_in_original(), outside_in_fair()):
        assert g.lumen_fluid == "dialysate"
        assert g.r_apical < g.r_oat1 < g.r_blood_membrane < g.r_housing


def test_flows_positive():
    q_b, q_d = volumetric_flows_from_io_mean_velocity()
    assert q_b > 0 and q_d > 0
