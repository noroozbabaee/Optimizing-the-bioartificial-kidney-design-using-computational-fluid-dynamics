"""Write COMSOL 6.3/6.4 Model Java files for IO, original OI, and fair OI.

Run from the repository root (does not need COMSOL):

    python3 src/write_comsol_java_models.py

On the university PC (COMSOL 6.4): compile to .class, then File > Open the .class.
See comsol/compile_models.bat and comsol/OPEN_ON_COMSOL64.txt.

WHY THREE MODELS
----------------
Same physics (surface OAT1 + apical efflux, no volumetric MM). Different
geometry only. See src/bak_geometries.py for the equations.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bak_geometries import (
    C_IN,
    D_IS,
    EPS_MEM,
    K_M,
    L_M,
    MU_B,
    MU_D,
    RHO_B,
    RHO_D,
    VMAX_A_EQUIV,
    FiberGeometry,
    all_geometries,
    mean_velocities,
    volumetric_flows_from_io_mean_velocity,
)

REPO = Path(__file__).resolve().parents[1]
COMSOL = REPO / "comsol"


def _mm(x: float) -> str:
    return f"{x * 1e3:.6f}"


def _box(r0: float, r1: float, z0: float, z1: float, pad_r=0.001, pad_z=0.02):
    """Box selection limits in mm with a small pad."""
    return (
        min(r0, r1) * 1e3 - pad_r,
        max(r0, r1) * 1e3 + pad_r,
        z0 * 1e3 - pad_z,
        z1 * 1e3 + pad_z,
    )


def java_for(geom: FiberGeometry) -> str:
    q_b, q_d = volumetric_flows_from_io_mean_velocity()
    u_b, u_d = mean_velocities(geom, q_b, q_d)
    Lmm = L_M * 1e3
    # Short class names: easier on Windows path limits and COMSOL Open dialogs.
    class_name = {
        "IO": "BAK_IO",
        "OI_original": "BAK_OI",
        "OI_fair": "BAK_OI_fair",
    }[geom.name]

    if geom.lumen_fluid == "blood":
        # IO: r increases blood | mem | cell | dialysate
        r0, r_bm, r_oat, r_ap, r_h = (
            0.0,
            geom.r_blood_membrane,
            geom.r_oat1,
            geom.r_apical,
            geom.r_housing,
        )
        rects = [
            ("r_blood", "Blood", 0.0, r_bm),
            ("r_mem", "Membrane", r_bm, r_oat),
            ("r_cell", "Cell layer", r_oat, r_ap),
            ("r_dial", "Dialysate", r_ap, r_h),
        ]
        id_blood, id_mem, id_cell, id_dial = 1, 2, 3, 4
        blood_in = _box(0.0, r_bm, 0.0, 0.0)
        blood_out = _box(0.0, r_bm, L_M, L_M)
        dial_in = _box(r_ap, r_h, L_M, L_M)  # countercurrent: dialysate inlet at z=L
        dial_out = _box(r_ap, r_h, 0.0, 0.0)
        u_blood_expr = "2*U_avg_b*(1-(r/R_BM)^2)"
    else:
        # OI: r increases dialysate | cell | mem | blood
        r_ap, r_oat, r_bm, r_h = (
            geom.r_apical,
            geom.r_oat1,
            geom.r_blood_membrane,
            geom.r_housing,
        )
        rects = [
            ("r_dial", "Dialysate", 0.0, r_ap),
            ("r_cell", "Cell layer", r_ap, r_oat),
            ("r_mem", "Membrane", r_oat, r_bm),
            ("r_blood", "Blood", r_bm, r_h),
        ]
        id_dial, id_cell, id_mem, id_blood = 1, 2, 3, 4
        blood_in = _box(r_bm, r_h, 0.0, 0.0)
        blood_out = _box(r_bm, r_h, L_M, L_M)
        dial_in = _box(0.0, r_ap, L_M, L_M)
        dial_out = _box(0.0, r_ap, 0.0, 0.0)
        u_blood_expr = "U_avg_b"

    bnd_bm = _box(r_bm, r_bm, 0.0, L_M, pad_r=0.0015, pad_z=0.0)
    bnd_oat = _box(r_oat, r_oat, 0.0, L_M, pad_r=0.0015, pad_z=0.0)
    bnd_ap = _box(r_ap, r_ap, 0.0, L_M, pad_r=0.0015, pad_z=0.0)
    bnd_axis = _box(0.0, 0.0, 0.0, L_M, pad_r=0.01, pad_z=0.0)
    bnd_outer = _box(r_h, r_h, 0.0, L_M, pad_r=0.002, pad_z=0.0)
    mem_lo, mem_hi = sorted((r_bm, r_oat))
    cell_lo, cell_hi = sorted((r_oat, r_ap))
    mem_z0 = _box(mem_lo, mem_hi, 0.0, 0.0)
    mem_zL = _box(mem_lo, mem_hi, L_M, L_M)
    cell_z0 = _box(cell_lo, cell_hi, 0.0, 0.0)
    cell_zL = _box(cell_lo, cell_hi, L_M, L_M)

    rect_java = []
    for tag, label, ra, rb in rects:
        rect_java.append(
            f"""
    model.component("comp1").geom("geom1").create("{tag}", "Rectangle");
    model.component("comp1").geom("geom1").feature("{tag}").label("{label}");
    model.component("comp1").geom("geom1").feature("{tag}")
        .set("pos", new String[]{{"{_mm(ra)}[mm]", "0"}});
    model.component("comp1").geom("geom1").feature("{tag}")
        .set("size", new String[]{{"{_mm(rb - ra)}[mm]", "L"}});"""
        )

    def box_java(tag, label, lim):
        xmin, xmax, ymin, ymax = lim
        return f"""
    boxEdge(model, "{tag}", "{label}", {xmin:.5f}, {xmax:.5f}, {ymin:.5f}, {ymax:.5f});"""

    title = {
        "IO": "BAK inside-out - surface OAT1",
        "OI_original": "BAK outside-in (thesis) - surface OAT1",
        "OI_fair": "BAK outside-in FAIR - surface OAT1",
    }[geom.name]

    stack = (
        "blood | membrane | cell | dialysate"
        if geom.lumen_fluid == "blood"
        else "dialysate | cell | membrane | blood"
    )

    return f'''/*
 * {class_name}.java
 *
 * COMSOL Multiphysics 6.3 Model Java - OPEN WITH: File -> Open
 *
 * PLAN (read this before pressing Compute)
 * ---------------------------------------
 * 1. This file is ONE of three twins that share the SAME physics and
 *    DIFFERENT geometry. Physics is never volumetric Michaelis-Menten.
 * 2. Run IO first (this family). Confirm cell concentration isc rises
 *    and molar flow at OAT1 is into the cell. If isc falls, flip the
 *    sign of N0 on oat1_mem / oat1_cell (see CHECK SIGNS below).
 * 3. Export tables Flux BM, Flux OAT1, Flux CD vs time into
 *    data/comsol_surface_oat1/{geom.name}/
 * 4. Repeat for the other two Java files, same Vmax_A, Q_b, Q_d, C_in.
 * 5. python3 src/comsol_io_oi_comparison.py
 *
 * Geometry: {geom.name}  ({geom.role})
 * Material order from the axis: {stack}
 *   R_apical (cell-dialysate) = {_mm(geom.r_apical)} mm
 *   R_OAT1   (membrane-cell)  = {_mm(geom.r_oat1)} mm
 *   R_BM     (blood-membrane) = {_mm(geom.r_blood_membrane)} mm
 *   R_housing                 = {_mm(geom.r_housing)} mm
 *   A_OAT1 = 2*pi*R_OAT1*L    = {geom.a_oat1 * 1e6:.4f} mm^2
 *   V_blood                   = {geom.v_blood * 1e9:.4f} mm^3
 *
 * WHY THREE TRANSPORT INTERFACES
 * ------------------------------
 * One continuous concentration cannot represent OAT1: the transporter
 * sees a different concentration on the membrane side (extracellular)
 * and the cell side (intracellular). We therefore use three TDS fields:
 *   tds  (is)  blood + polymer membrane   - passive continuity at BM
 *   tds2 (isc) cell layer only
 *   tds3 (isd) dialysate only
 * Coupled by equal-and-opposite FLUXES (mass is transferred, not created):
 *   J_OAT1   = Vmax_A * ( is/(Km+is) - isc/(Km+isc) )     reversible OAT1
 *   J_apical = Vmax_ap * isc / (Km_ap + isc)              irreversible exit
 *
 * CHECK SIGNS (after the first 5 min of a test run)
 * -------------------------------------------------
 * isc in the cell must increase from 0. Molar flow 2*pi*r*J_OAT1 > 0
 * means blood -> dialysate. If isc decreases, set N0 to the opposite sign
 * on both members of the pair (keep them equal-and-opposite).
 *
 * Compile / batch (optional):
 *   comsol compile {class_name}.java
 *   comsol batch -inputfile {class_name}.class -outputfile {class_name}.mph
 */

import com.comsol.model.Model;
import com.comsol.model.util.ModelUtil;

public class {class_name} {{

  public static Model run() {{
    Model model = ModelUtil.create("Model");
    model.label("{title}");
    model.comments("{geom.name}: surface OAT1 + apical efflux. {geom.role}.");
    parameters(model);
    component(model);
    geometry(model);
    selections(model);
    variables(model);
    materials(model);
    laminarBlood(model);
    laminarDialysate(model);
    transportBloodMembrane(model);
    transportCell(model);
    transportDialysate(model);
    oat1AndApicalCoupling(model);
    mesh(model);
    studies(model);
    results(model);
    return model;
  }}

  public static void main(String[] args) {{
    // File > Open of the .class calls run(). No save here (IOException on COMSOL 6.4).
    run();
  }}

  private static void parameters(Model model) {{
    model.param().set("L", "{Lmm:g}[mm]", "Fiber length");
    model.param().set("R_AP", "{_mm(geom.r_apical)}[mm]", "Apical / cell-dialysate radius");
    model.param().set("R_OAT1", "{_mm(geom.r_oat1)}[mm]", "OAT1 / membrane-cell radius");
    model.param().set("R_BM", "{_mm(geom.r_blood_membrane)}[mm]", "Blood-membrane radius");
    model.param().set("R_house", "{_mm(geom.r_housing)}[mm]", "Housing radius");

    model.param().set("C_in", "{C_IN}[mol/m^3]", "Inlet free IS = 100 uM (thesis)");
    model.param().set("D_is", "{D_IS}[m^2/s]", "IS diffusivity in aqueous domains");
    model.param().set("eps_mem", "{EPS_MEM}", "Membrane porosity (thesis)");
    model.param().set("D_mem", "eps_mem*D_is", "Effective membrane diffusivity");

    model.param().set("rho_b", "{RHO_B}[kg/m^3]", "Blood density");
    model.param().set("mu_b", "{MU_B}[Pa*s]", "Blood viscosity");
    model.param().set("rho_d", "{RHO_D}[kg/m^3]", "Dialysate density");
    model.param().set("mu_d", "{MU_D}[Pa*s]", "Dialysate viscosity");

    // Volumetric flows are the FAIR quantities (same for IO and both OI models).
    model.param().set("Q_b", "{q_b:.6e}[m^3/s]", "Blood volumetric flow (~0.10 mL/min)");
    model.param().set("Q_d", "{q_d:.6e}[m^3/s]", "Dialysate volumetric flow (~0.20 mL/min)");
    model.param().set("U_avg_b", "{u_b:.6e}[m/s]", "Mean blood speed = Q_b / A_blood for THIS geometry");
    model.param().set("U_avg_d", "{u_d:.6e}[m/s]", "Mean dialysate speed = Q_d / A_dial for THIS geometry");

    model.param().set("Km_bl", "{K_M}[mol/m^3]", "OAT1 Km = 20 uM");
    model.param().set("Km_ap", "{K_M}[mol/m^3]", "Apical Km = 20 uM (same as thesis split-cell default)");
    // First-run default is in the OAT1-sensitive window. Thesis-equivalent areal
    // Vmax is Param.Vmax_A_equiv (Da >> 1, membrane-limited). Sweep both.
    model.param().set("Vmax_A", "1e-7[mol/(m^2*s)]", "OAT1 areal capacity (change this)");
    model.param().set("Vmax_ap", "10*Vmax_A", "Apical capacity; 10x so apical is not the bottleneck");
    model.param().set("Vmax_A_equiv", "{VMAX_A_EQUIV}[mol/(m^2*s)]",
        "Thesis volumetric Vmax collapsed onto 20 um cell");
    model.param().set("T_end", "60[min]", "Transport duration (raise to 240 min to match thesis)");
  }}

  private static void component(Model model) {{
    model.component().create("comp1", true);
    model.component("comp1").geom().create("geom1", 2);
    model.component("comp1").mesh().create("mesh1");
    model.component("comp1").geom("geom1").label("{geom.name} fiber (axisymmetric)");
    model.component("comp1").geom("geom1").lengthUnit("mm");
    model.component("comp1").geom("geom1").axisymmetric(true);
  }}

  private static void geometry(Model model) {{
{"".join(rect_java)}
    model.component("comp1").geom("geom1").run();
  }}

  private static void selections(Model model) {{
    explicitDomain(model, "dom_blood", "Blood domain", {id_blood});
    explicitDomain(model, "dom_mem", "Membrane domain", {id_mem});
    explicitDomain(model, "dom_cell", "Cell domain", {id_cell});
    explicitDomain(model, "dom_dial", "Dialysate domain", {id_dial});

    model.component("comp1").selection().create("dom_blood_mem", "Explicit");
    model.component("comp1").selection("dom_blood_mem").label("Blood + membrane (field is)");
    model.component("comp1").selection("dom_blood_mem").geom("geom1", 2);
    model.component("comp1").selection("dom_blood_mem").set({id_blood}, {id_mem});
{box_java("bnd_blood_in", "Blood inlet z=0", blood_in)}
{box_java("bnd_blood_out", "Blood outlet z=L", blood_out)}
{box_java("bnd_dial_in", "Dialysate inlet z=L (countercurrent)", dial_in)}
{box_java("bnd_dial_out", "Dialysate outlet z=0", dial_out)}
{box_java("bnd_bm", "Blood-membrane interface", bnd_bm)}
{box_java("bnd_mc", "Membrane-cell interface (OAT1)", bnd_oat)}
{box_java("bnd_cd", "Cell-dialysate interface (apical)", bnd_ap)}
{box_java("bnd_axis", "Axis r=0", bnd_axis)}
{box_java("bnd_outer", "Housing wall", bnd_outer)}
{box_java("bnd_mem_ends", "Membrane axial end z=0", mem_z0)}
{box_java("bnd_mem_ends_L", "Membrane axial end z=L", mem_zL)}
{box_java("bnd_cell_ends", "Cell axial end z=0", cell_z0)}
{box_java("bnd_cell_ends_L", "Cell axial end z=L", cell_zL)}
  }}

  private static void explicitDomain(Model model, String tag, String label, int id) {{
    model.component("comp1").selection().create(tag, "Explicit");
    model.component("comp1").selection(tag).label(label);
    model.component("comp1").selection(tag).geom("geom1", 2);
    model.component("comp1").selection(tag).set(id);
  }}

  private static void boxEdge(
      Model model, String tag, String label,
      double xmin, double xmax, double ymin, double ymax) {{
    model.component("comp1").selection().create(tag, "Box");
    model.component("comp1").selection(tag).label(label);
    model.component("comp1").selection(tag).geom("geom1", 1);
    model.component("comp1").selection(tag).set("xmin", xmin);
    model.component("comp1").selection(tag).set("xmax", xmax);
    model.component("comp1").selection(tag).set("ymin", ymin);
    model.component("comp1").selection(tag).set("ymax", ymax);
    model.component("comp1").selection(tag).set("condition", "inside");
  }}

  private static void variables(Model model) {{
    model.component("comp1").variable().create("var1");
    model.component("comp1").variable("var1").label("Transporter fluxes and inlet profile");
    model.component("comp1").variable("var1")
        .set("u_blood", "{u_blood_expr}", "Blood inlet axial speed");
    // Reversible OAT1: net flux positive when extracellular is > intracellular isc.
    model.component("comp1").variable("var1")
        .set("J_OAT1", "Vmax_A*(is/(Km_bl+is)-isc/(Km_bl+isc))",
            "OAT1 net flux mol/(m^2 s), membrane -> cell when >0");
    model.component("comp1").variable("var1")
        .set("J_apical", "Vmax_ap*isc/(Km_ap+isc)",
            "Apical efflux mol/(m^2 s), cell -> dialysate");
    model.component("comp1").variable("var1")
        .set("n_dot_OAT1", "2*pi*r*J_OAT1", "OAT1 molar flow per length * r-weight");
  }}

  private static void materials(Model model) {{
    model.component("comp1").material().create("mat_blood", "Common");
    model.component("comp1").material("mat_blood").label("Blood");
    model.component("comp1").material("mat_blood").selection().named("dom_blood");
    model.component("comp1").material("mat_blood").propertyGroup("def").set("density", "rho_b");
    model.component("comp1").material("mat_blood").propertyGroup("def").set("dynamicviscosity", "mu_b");

    model.component("comp1").material().create("mat_dial", "Common");
    model.component("comp1").material("mat_dial").label("Dialysate");
    model.component("comp1").material("mat_dial").selection().named("dom_dial");
    model.component("comp1").material("mat_dial").propertyGroup("def").set("density", "rho_d");
    model.component("comp1").material("mat_dial").propertyGroup("def").set("dynamicviscosity", "mu_d");
  }}

  private static void laminarBlood(Model model) {{
    model.component("comp1").physics().create("spf", "LaminarFlow", "geom1");
    model.component("comp1").physics("spf").label("Laminar Flow - blood");
    model.component("comp1").physics("spf").selection().named("dom_blood");
    model.component("comp1").physics("spf").prop("ShapeProperty").set("order_fluid", 1);

    model.component("comp1").physics("spf").create("inl_b", "Inlet", 1);
    model.component("comp1").physics("spf").feature("inl_b").label("Blood inlet");
    model.component("comp1").physics("spf").feature("inl_b").selection().named("bnd_blood_in");
    // Velocity inlet (portable across COMSOL 6.3/6.4; avoid LaminarInflow API drift)
    model.component("comp1").physics("spf").feature("inl_b").set("U0in", "U_avg_b");

    model.component("comp1").physics("spf").create("out_b", "Outlet", 1);
    model.component("comp1").physics("spf").feature("out_b").label("Blood outlet p=0");
    model.component("comp1").physics("spf").feature("out_b").selection().named("bnd_blood_out");
    model.component("comp1").physics("spf").feature("out_b").set("p0", "0");
  }}

  private static void laminarDialysate(Model model) {{
    model.component("comp1").physics().create("spf2", "LaminarFlow", "geom1");
    model.component("comp1").physics("spf2").label("Laminar Flow - dialysate, countercurrent");
    model.component("comp1").physics("spf2").selection().named("dom_dial");
    model.component("comp1").physics("spf2").prop("ShapeProperty").set("order_fluid", 1);

    model.component("comp1").physics("spf2").create("inl_d", "Inlet", 1);
    model.component("comp1").physics("spf2").feature("inl_d").label("Dialysate inlet z=L");
    model.component("comp1").physics("spf2").feature("inl_d").selection().named("bnd_dial_in");
    model.component("comp1").physics("spf2").feature("inl_d").set("U0in", "U_avg_d");

    model.component("comp1").physics("spf2").create("out_d", "Outlet", 1);
    model.component("comp1").physics("spf2").feature("out_d").label("Dialysate outlet p=0");
    model.component("comp1").physics("spf2").feature("out_d").selection().named("bnd_dial_out");
    model.component("comp1").physics("spf2").feature("out_d").set("p0", "0");
  }}

  private static void transportBloodMembrane(Model model) {{
    model.component("comp1").physics().create("tds", "DilutedSpecies", "geom1");
    model.component("comp1").physics("tds").label("TDS - IS in blood + membrane");
    model.component("comp1").physics("tds").selection().named("dom_blood_mem");
    model.component("comp1").physics("tds").prop("ShapeProperty").set("order_concentration", 2);
    model.component("comp1").physics("tds").field("concentration").field("is");
    model.component("comp1").physics("tds").field("concentration").component(1, "is");

    model.component("comp1").physics("tds").feature("cdm1").set("minput_velocity_src", "root.comp1.u");
    model.component("comp1").physics("tds").feature("cdm1").setIndex("D_c", "D_is", 0);

    model.component("comp1").physics("tds").create("cdm_mem", "ConvectionDiffusion", 2);
    model.component("comp1").physics("tds").feature("cdm_mem").label("Membrane diffusion only");
    model.component("comp1").physics("tds").feature("cdm_mem").selection().named("dom_mem");
    model.component("comp1").physics("tds").feature("cdm_mem").set("Convection", false);
    model.component("comp1").physics("tds").feature("cdm_mem").setIndex("D_c", "D_mem", 0);

    model.component("comp1").physics("tds").feature("init1").set("is", "C_in");

    model.component("comp1").physics("tds").create("conc_b", "Concentration", 1);
    model.component("comp1").physics("tds").feature("conc_b").label("Blood inlet c=C_in");
    model.component("comp1").physics("tds").feature("conc_b").selection().named("bnd_blood_in");
    model.component("comp1").physics("tds").feature("conc_b").set("is", "C_in");

    model.component("comp1").physics("tds").create("outfl_b", "Outflow", 1);
    model.component("comp1").physics("tds").feature("outfl_b").label("Blood outflow");
    model.component("comp1").physics("tds").feature("outfl_b").selection().named("bnd_blood_out");

    model.component("comp1").physics("tds").create("nflx_mem0", "NoFlux", 1);
    model.component("comp1").physics("tds").feature("nflx_mem0").selection().named("bnd_mem_ends");
    model.component("comp1").physics("tds").create("nflx_memL", "NoFlux", 1);
    model.component("comp1").physics("tds").feature("nflx_memL").selection().named("bnd_mem_ends_L");
  }}

  private static void transportCell(Model model) {{
    model.component("comp1").physics().create("tds2", "DilutedSpecies", "geom1");
    model.component("comp1").physics("tds2").label("TDS - IS in cell (no volume MM)");
    model.component("comp1").physics("tds2").selection().named("dom_cell");
    model.component("comp1").physics("tds2").prop("ShapeProperty").set("order_concentration", 2);
    model.component("comp1").physics("tds2").field("concentration").field("isc");
    model.component("comp1").physics("tds2").field("concentration").component(1, "isc");
    model.component("comp1").physics("tds2").feature("cdm1").set("Convection", false);
    model.component("comp1").physics("tds2").feature("cdm1").setIndex("D_c", "D_is", 0);
    model.component("comp1").physics("tds2").feature("init1").set("isc", "0");

    model.component("comp1").physics("tds2").create("nflx_c0", "NoFlux", 1);
    model.component("comp1").physics("tds2").feature("nflx_c0").selection().named("bnd_cell_ends");
    model.component("comp1").physics("tds2").create("nflx_cL", "NoFlux", 1);
    model.component("comp1").physics("tds2").feature("nflx_cL").selection().named("bnd_cell_ends_L");
  }}

  private static void transportDialysate(Model model) {{
    model.component("comp1").physics().create("tds3", "DilutedSpecies", "geom1");
    model.component("comp1").physics("tds3").label("TDS - IS in dialysate");
    model.component("comp1").physics("tds3").selection().named("dom_dial");
    model.component("comp1").physics("tds3").prop("ShapeProperty").set("order_concentration", 2);
    model.component("comp1").physics("tds3").field("concentration").field("isd");
    model.component("comp1").physics("tds3").field("concentration").component(1, "isd");
    model.component("comp1").physics("tds3").feature("cdm1").set("minput_velocity_src", "root.comp1.u2");
    model.component("comp1").physics("tds3").feature("cdm1").setIndex("D_c", "D_is", 0);
    model.component("comp1").physics("tds3").feature("init1").set("isd", "0");

    model.component("comp1").physics("tds3").create("conc_d", "Concentration", 1);
    model.component("comp1").physics("tds3").feature("conc_d").label("Dialysate inlet c=0");
    model.component("comp1").physics("tds3").feature("conc_d").selection().named("bnd_dial_in");
    model.component("comp1").physics("tds3").feature("conc_d").set("isd", "0");

    model.component("comp1").physics("tds3").create("outfl_d", "Outflow", 1);
    model.component("comp1").physics("tds3").feature("outfl_d").selection().named("bnd_dial_out");

    model.component("comp1").physics("tds3").create("nflx_out", "NoFlux", 1);
    model.component("comp1").physics("tds3").feature("nflx_out").selection().named("bnd_outer");
  }}

  private static void oat1AndApicalCoupling(Model model) {{
    // Equal-and-opposite fluxes: solute that leaves one field enters the other.
    // N0 is INWARD flux into the physics selection (COMSOL convention).
    // Pair 1 - OAT1 at membrane-cell. Positive J_OAT1: membrane -> cell.
    model.component("comp1").physics("tds").create("oat1_mem", "Fluxes", 1);
    model.component("comp1").physics("tds").feature("oat1_mem")
        .label("OAT1: outward from membrane");
    model.component("comp1").physics("tds").feature("oat1_mem").selection().named("bnd_mc");
    model.component("comp1").physics("tds").feature("oat1_mem").setIndex("N0", "-J_OAT1", 0);

    model.component("comp1").physics("tds2").create("oat1_cell", "Fluxes", 1);
    model.component("comp1").physics("tds2").feature("oat1_cell")
        .label("OAT1: inward to cell");
    model.component("comp1").physics("tds2").feature("oat1_cell").selection().named("bnd_mc");
    model.component("comp1").physics("tds2").feature("oat1_cell").setIndex("N0", "J_OAT1", 0);

    // Pair 2 - apical at cell-dialysate. Positive J_apical: cell -> dialysate.
    model.component("comp1").physics("tds2").create("ap_cell", "Fluxes", 1);
    model.component("comp1").physics("tds2").feature("ap_cell")
        .label("Apical: outward from cell");
    model.component("comp1").physics("tds2").feature("ap_cell").selection().named("bnd_cd");
    model.component("comp1").physics("tds2").feature("ap_cell").setIndex("N0", "-J_apical", 0);

    model.component("comp1").physics("tds3").create("ap_dial", "Fluxes", 1);
    model.component("comp1").physics("tds3").feature("ap_dial")
        .label("Apical: inward to dialysate");
    model.component("comp1").physics("tds3").feature("ap_dial").selection().named("bnd_cd");
    model.component("comp1").physics("tds3").feature("ap_dial").setIndex("N0", "J_apical", 0);
  }}

  private static void mesh(Model model) {{
    model.component("comp1").mesh("mesh1").label("Mapped quads");
    model.component("comp1").mesh("mesh1").create("map1", "Map");
    model.component("comp1").mesh("mesh1").feature("map1").selection().all();
    model.component("comp1").mesh("mesh1").feature("map1").create("dis_z", "Distribution");
    model.component("comp1").mesh("mesh1").feature("map1").feature("dis_z").set("numelem", 80);
    model.component("comp1").mesh("mesh1").create("size1", "Size");
    model.component("comp1").mesh("mesh1").feature("size1").selection().named("dom_cell");
    model.component("comp1").mesh("mesh1").feature("size1").set("custom", "on");
    model.component("comp1").mesh("mesh1").feature("size1").set("hmax", "0.005[mm]");
    // Mesh is built in the GUI (right-click Mesh -> Build All) after open.
  }}

  private static void studies(Model model) {{
    String[] flowOn = new String[] {{
        "spf", "on", "spf2", "on", "tds", "off", "tds2", "off", "tds3", "off"}};
    String[] tdsOn = new String[] {{
        "spf", "off", "spf2", "off", "tds", "on", "tds2", "on", "tds3", "on"}};

    model.study().create("std1");
    model.study("std1").label("1. Flow then IS (use this first)");
    model.study("std1").create("stat", "Stationary");
    model.study("std1").feature("stat").label("Stationary laminar flow");
    model.study("std1").feature("stat").set("activate", flowOn);
    model.study("std1").create("time", "Transient");
    model.study("std1").feature("time").label("Time-dependent IS");
    model.study("std1").feature("time").set("tunit", "min");
    model.study("std1").feature("time").set("tlist", "range(0,5,T_end)");
    model.study("std1").feature("time").set("activate", tdsOn);

    model.study().create("std2");
    model.study("std2").label("2. Vmax_A sweep (after signs are correct)");
    model.study("std2").create("param", "Parametric");
    model.study("std2").feature("param").set("pname", new String[]{{"Vmax_A"}});
    model.study("std2").feature("param").set("plistarr", new String[]{{
        "1e-9 1e-8 1e-7 1e-6 1e-5 1e-4 3.333e-4"}});
    model.study("std2").feature("param").set("punit", new String[]{{"mol/(m^2*s)"}});
    model.study("std2").create("stat2", "Stationary");
    model.study("std2").feature("stat2").set("activate", flowOn);
    model.study("std2").create("time2", "Transient");
    model.study("std2").feature("time2").set("tunit", "min");
    model.study("std2").feature("time2").set("tlist", "range(0,5,T_end)");
    model.study("std2").feature("time2").set("activate", tdsOn);
  }}

  private static void results(Model model) {{
    // Line integrals of 2*pi*r*J give molar flow [mol/s] on an axisymmetric cut.
    intLine(model, "int_bm", "Molar flow blood-membrane", "bnd_bm", "2*pi*r*tds.ndflux_is");
    intLine(model, "int_oat1", "Molar flow OAT1 (use J_OAT1, sign-independent of ndflux)",
        "bnd_mc", "2*pi*r*J_OAT1");
    intLine(model, "int_cd", "Molar flow apical", "bnd_cd", "2*pi*r*J_apical");

    model.result().table().create("tbl_bm", "Table");
    model.result().table("tbl_bm").label("Flux BM vs time");
    model.result().numerical("int_bm").set("table", "tbl_bm");
    model.result().table().create("tbl_oat1", "Table");
    model.result().table("tbl_oat1").label("Flux OAT1 vs time");
    model.result().numerical("int_oat1").set("table", "tbl_oat1");
    model.result().table().create("tbl_cd", "Table");
    model.result().table("tbl_cd").label("Flux CD vs time");
    model.result().numerical("int_cd").set("table", "tbl_cd");

    model.result().create("pg_is", "PlotGroup2D");
    model.result("pg_is").label("IS blood+membrane (is)");
    model.result("pg_is").create("surf1", "Surface");
    model.result("pg_is").feature("surf1").set("expr", "is");

    model.result().create("pg_isc", "PlotGroup2D");
    model.result("pg_isc").label("IS cell (isc) - must be >0 after a few minutes");
    model.result("pg_isc").create("surf2", "Surface");
    model.result("pg_isc").feature("surf2").set("expr", "isc");
  }}

  private static void intLine(Model model, String tag, String label, String sel, String expr) {{
    model.result().numerical().create(tag, "IntLine");
    model.result().numerical(tag).label(label);
    model.result().numerical(tag).selection().named(sel);
    model.result().numerical(tag).set("expr", expr);
    model.result().numerical(tag).set("unit", "mol/s");
  }}
}}
'''


def main() -> None:
    COMSOL.mkdir(parents=True, exist_ok=True)
    mapping = {
        "IO": "BAK_IO.java",
        "OI_original": "BAK_OI.java",
        "OI_fair": "BAK_OI_fair.java",
    }
    for key, filename in mapping.items():
        text = java_for(all_geometries()[key])
        path = COMSOL / filename
        path.write_text(text)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
