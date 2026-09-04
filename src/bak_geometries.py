"""Hollow-fiber geometries for the surface-OAT1 BAK models.

WHY THIS FILE EXISTS
--------------------
The thesis compared inside-out (IO) and outside-in (OI) fibers, then an
"adjusted OI" that matched blood VOLUME by thinning the blood shell while the
membrane grew out to the 1.8 mm housing. That makes OAT1 area ~6x larger than
IO, so a higher total clearance is not a fair win for the OI arrangement.

This module is the single source of truth for THREE geometries that must be
used in COMSOL (Java files in comsol/) and in Python post-processing:

  1. IO            thesis inside-out (reference)
  2. OI_original   thesis outside-in (control: inverted layers, UNFAIR area)
  3. OI_fair       same OAT1 area AND same blood volume as IO

All lengths below are SI (metres) unless a name ends with _mm.

PHYSICS OF THE STACK (why the order is not arbitrary)
-----------------------------------------------------
OAT1 sits on the BASOLATERAL membrane of the proximal-tubule cell: it faces
the polymer membrane / blood side. The APICAL membrane faces the dialysate
(filtrate) side.

So the radial order of MATERIALS must always be:

    blood  |  polymer membrane  |  cell  |  dialysate

with OAT1 on the membrane–cell face and apical efflux on the cell–dialysate
face. What changes between IO and OI is which compartment occupies the LUMEN:

    IO:  lumen = blood,      shell = dialysate
    OI:  lumen = dialysate,  shell = blood

EQUATIONS
---------
Axisymmetric surface area of a cylinder of radius R and length L:

    A = 2 π R L                                             (1)

Blood volume:

    IO lumen:     V_b = π R_lumen² L                        (2)
    OI annulus:   V_b = π (R_housing² − R_BM²) L            (3)

Fair OI housing (match V_b to IO at the same L, with blood starting at R_BM):

    π (R_housing² − R_BM²) L  =  π R_blood_IO² L
    R_housing = sqrt(R_BM² + R_blood_IO²)                   (4)

Membrane permeance referred to the OAT1 surface (cylindrical wall):

    P_m = D_mem / (R_OAT1 * ln(R_outer_mem / R_inner_mem))  (5)

Damkohler number (OAT1 capacity vs membrane diffusion of inlet concentration):

    Da = Vmax_A / (P_m * C_in)                              (6)

    Da << 1  →  raising Vmax_A still raises flux (OAT1-limited)
    Da >> 1  →  flux saturates at ~ P_m C_in (membrane-limited)

Clearance from a COMSOL line integral of molar flow n_dot [mol/s]:

    CL          = n_dot / C_in                 [m³/s]       (7)
    CL_area     = CL / A_OAT1                  [m/s]        (8)
    CL_uL_min_cm2 = CL_area * 6e6              (unit convert) (9)

Fair comparison ALWAYS reports CL_area using A_OAT1 from (1) at the OAT1
radius of THAT geometry, and also reports unmatched quantities (blood-side
gap, shear, k_b). Matching A and V_b does NOT match hydrodynamics.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass

PI = math.pi

# --- Thesis constants (IO fiber) ---
L_M = 20.0e-3
DELTA_MEM_M = 0.10e-3  # 100 um polymer wall
DELTA_CELL_M = 0.02e-3  # 20 um epithelium
R_BLOOD_IO_M = 0.15e-3  # IO blood lumen radius = blood–membrane interface
R_OAT1_IO_M = 0.25e-3  # IO membrane–cell = OAT1
R_APICAL_IO_M = 0.27e-3  # IO cell–dialysate
R_HOUSING_THESIS_M = 1.80e-3

# Transport (thesis IS)
D_IS = 5.58e-10  # m^2/s
EPS_MEM = 0.45
C_IN = 0.1  # mol/m^3 = 100 uM
K_M = 0.02  # mol/m^3 = 20 uM

# Thesis mean velocities on the IO geometry (used only to define volumetric flow)
U_AVG_BLOOD_IO = 0.02358  # m/s
U_AVG_DIAL_IO = 3.4e-4  # m/s

RHO_B = 1050.0  # kg/m^3
MU_B = 0.0035  # Pa s
RHO_D = 1000.0
MU_D = 0.7e-3

VMAX_VOL_UMOL_L_MIN = 1.0e6
# 1e6 umol/(L min) = 1000 mol/(m^3 min) = 1000/60 mol/(m^3 s)
VMAX_VOL = (VMAX_VOL_UMOL_L_MIN * 1.0e-3) / 60.0
# Collapse that volume reaction onto the 20 um cell as an areal capacity
VMAX_A_EQUIV = VMAX_VOL * DELTA_CELL_M  # mol/(m^2 s)

MPS_TO_UL_MIN_CM2 = 6.0e6


def _area_cyl(r: float, length: float = L_M) -> float:
    """Equation (1): A = 2 π R L."""
    return 2.0 * PI * r * length


def _vol_lumen(r: float, length: float = L_M) -> float:
    """Equation (2): V = π R² L."""
    return PI * r * r * length


def _vol_annulus(r_in: float, r_out: float, length: float = L_M) -> float:
    """Equation (3): V = π (R_out² − R_in²) L."""
    return PI * (r_out * r_out - r_in * r_in) * length


@dataclass(frozen=True)
class FiberGeometry:
    """One 2D-axisymmetric hollow fiber. Radii increase from the axis."""

    name: str
    role: str
    # Inner → outer interfaces (metres)
    r_lumen_outer: float
    r_oat1: float
    r_apical: float
    r_blood_membrane: float
    r_housing: float
    lumen_fluid: str  # "blood" or "dialysate"
    length: float = L_M

    @property
    def a_oat1(self) -> float:
        return _area_cyl(self.r_oat1, self.length)

    @property
    def a_apical(self) -> float:
        return _area_cyl(self.r_apical, self.length)

    @property
    def a_blood_membrane(self) -> float:
        return _area_cyl(self.r_blood_membrane, self.length)

    @property
    def v_blood(self) -> float:
        if self.lumen_fluid == "blood":
            return _vol_lumen(self.r_blood_membrane, self.length)
        return _vol_annulus(self.r_blood_membrane, self.r_housing, self.length)

    @property
    def v_dialysate(self) -> float:
        if self.lumen_fluid == "dialysate":
            return _vol_lumen(self.r_apical, self.length)
        return _vol_annulus(self.r_apical, self.r_housing, self.length)

    @property
    def a_blood_cs(self) -> float:
        """Blood flow cross-section (m²), for converting Q_b → mean velocity."""
        if self.lumen_fluid == "blood":
            return PI * self.r_blood_membrane**2
        return PI * (self.r_housing**2 - self.r_blood_membrane**2)

    @property
    def a_dial_cs(self) -> float:
        if self.lumen_fluid == "dialysate":
            return PI * self.r_apical**2
        return PI * (self.r_housing**2 - self.r_apical**2)

    def membrane_permeance(self) -> float:
        """Equation (5). D_mem = eps * D_IS. Referred to the OAT1 radius."""
        d_mem = EPS_MEM * D_IS
        r_in, r_out = sorted((self.r_blood_membrane, self.r_oat1))
        return d_mem / (self.r_oat1 * math.log(r_out / r_in))

    def damkohler(self, vmax_a: float, c_ref: float = C_IN) -> float:
        """Equation (6)."""
        return vmax_a / (self.membrane_permeance() * c_ref)

    def radii_mm(self) -> dict[str, float]:
        scale = 1.0e3
        return {
            "r_lumen_outer_mm": self.r_lumen_outer * scale,
            "r_oat1_mm": self.r_oat1 * scale,
            "r_apical_mm": self.r_apical * scale,
            "r_blood_membrane_mm": self.r_blood_membrane * scale,
            "r_housing_mm": self.r_housing * scale,
        }

    def summary(self) -> dict:
        d = asdict(self)
        d.update(self.radii_mm())
        d["A_OAT1_mm2"] = self.a_oat1 * 1.0e6
        d["A_BM_mm2"] = self.a_blood_membrane * 1.0e6
        d["V_blood_mm3"] = self.v_blood * 1.0e9
        d["V_dialysate_mm3"] = self.v_dialysate * 1.0e9
        d["P_m_m_s"] = self.membrane_permeance()
        d["Da_at_Vmax_equiv"] = self.damkohler(VMAX_A_EQUIV)
        return d


def inside_out() -> FiberGeometry:
    """Thesis IO: blood lumen | membrane | cell | dialysate shell."""
    return FiberGeometry(
        name="IO",
        role="reference (thesis inside-out)",
        r_lumen_outer=R_BLOOD_IO_M,
        r_blood_membrane=R_BLOOD_IO_M,
        r_oat1=R_OAT1_IO_M,
        r_apical=R_APICAL_IO_M,
        r_housing=R_HOUSING_THESIS_M,
        lumen_fluid="blood",
    )


def outside_in_original() -> FiberGeometry:
    """Thesis OI: dialysate lumen | cell | membrane | blood shell to 1.8 mm.

    This is a CONTROL, not the fair pair. OAT1 sits at r = 0.17 mm, so A_OAT1
    is smaller than IO (0.25 mm). Blood volume is much larger (thick shell).
    """
    r_apical = 0.15e-3
    r_oat1 = 0.17e-3
    r_bm = 0.27e-3
    return FiberGeometry(
        name="OI_original",
        role="control (thesis outside-in, unmatched area and blood volume)",
        r_lumen_outer=r_apical,
        r_apical=r_apical,
        r_oat1=r_oat1,
        r_blood_membrane=r_bm,
        r_housing=R_HOUSING_THESIS_M,
        lumen_fluid="dialysate",
    )


def outside_in_fair() -> FiberGeometry:
    """Fair OI: same wall thicknesses, same OAT1 radius (hence area), same V_b.

    Stack from the axis:
        dialysate lumen  0 → (R_OAT1 − δ_cell)
        cell             (R_OAT1 − δ_cell) → R_OAT1          [OAT1 at outer cell]
        membrane         R_OAT1 → (R_OAT1 + δ_mem)
        blood            (R_OAT1 + δ_mem) → R_housing        [Eq. 4]
    """
    r_oat1 = R_OAT1_IO_M
    r_apical = r_oat1 - DELTA_CELL_M
    r_bm = r_oat1 + DELTA_MEM_M
    r_housing = math.sqrt(r_bm**2 + R_BLOOD_IO_M**2)
    return FiberGeometry(
        name="OI_fair",
        role="fair pair to IO (matched A_OAT1 and V_blood; hydrodynamics unmatched)",
        r_lumen_outer=r_apical,
        r_apical=r_apical,
        r_oat1=r_oat1,
        r_blood_membrane=r_bm,
        r_housing=r_housing,
        lumen_fluid="dialysate",
    )


def volumetric_flows_from_io_mean_velocity() -> tuple[float, float]:
    """Define Q_b and Q_d from the thesis IO mean velocities, then KEEP them
    for every geometry (fair comparison of throughput, not of mean speed).

        Q_b = U_avg_b_IO * π R_blood_IO²
        Q_d = U_avg_d_IO * π (R_housing² − R_apical_IO²)
    """
    io = inside_out()
    q_b = U_AVG_BLOOD_IO * io.a_blood_cs
    q_d = U_AVG_DIAL_IO * io.a_dial_cs
    return q_b, q_d


def mean_velocities(geom: FiberGeometry, q_b: float | None = None, q_d: float | None = None):
    if q_b is None or q_d is None:
        q_b, q_d = volumetric_flows_from_io_mean_velocity()
    return q_b / geom.a_blood_cs, q_d / geom.a_dial_cs


def all_geometries() -> dict[str, FiberGeometry]:
    return {
        "IO": inside_out(),
        "OI_original": outside_in_original(),
        "OI_fair": outside_in_fair(),
    }


def print_table() -> None:
    q_b, q_d = volumetric_flows_from_io_mean_velocity()
    print(f"Q_b = {q_b*6e7:.4f} mL/min   Q_d = {q_d*6e7:.4f} mL/min")
    print(
        f"{'name':<14} {'A_OAT1 mm2':>12} {'V_b mm3':>10} {'R_house mm':>12} "
        f"{'U_b m/s':>10} {'U_d m/s':>10} {'Da_eq':>8}"
    )
    for g in all_geometries().values():
        ub, ud = mean_velocities(g, q_b, q_d)
        print(
            f"{g.name:<14} {g.a_oat1*1e6:12.4f} {g.v_blood*1e9:10.4f} "
            f"{g.r_housing*1e3:12.4f} {ub:10.4f} {ud:10.5f} "
            f"{g.damkohler(VMAX_A_EQUIV):8.1f}"
        )


if __name__ == "__main__":
    print_table()
