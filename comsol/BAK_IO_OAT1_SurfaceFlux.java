/*
 * BAK_IO_OAT1_SurfaceFlux.java
 *
 * COMSOL Multiphysics 6.3 — complete inside-out hollow-fiber BAK model
 * with OAT1 as a BASOLATERAL SURFACE FLUX (not a volumetric cell reaction).
 *
 * Geometry (2D axisymmetric, mm):
 *   blood      r = 0    .. 0.15   z = 0 .. 20
 *   membrane   r = 0.15 .. 0.25   (ONE diffusion domain)
 *   cell       r = 0.25 .. 0.27
 *   dialysate  r = 0.27 .. 1.80
 *
 * Physics:
 *   Laminar Flow in blood (spf) and dialysate (spf2), countercurrent
 *   Transport of Diluted Species (is) in all four domains
 *   NO volumetric Michaelis-Menten in the cell
 *   OAT1 flux on membrane-cell interface
 *   Apical efflux on cell-dialysate interface
 *
 * Open this file in COMSOL 6.3 (File > Open) or compile:
 *   comsol compile BAK_IO_OAT1_SurfaceFlux.java
 *   comsol batch -inputfile BAK_IO_OAT1_SurfaceFlux.class
 *
 * After the first open in the GUI: check Box selections on the geometry,
 * then Study 1 > Compute. Export line integrals of normal total flux on
 * BM / MC / CD as flux_BM_VmaxA_*.txt etc. into data/oat1_surface_flux/.
 */

import com.comsol.model.Model;
import com.comsol.model.util.ModelUtil;

public class BAK_IO_OAT1_SurfaceFlux {

  public static Model run() {
    Model model = ModelUtil.create("Model");
    model.label("BAK inside-out — surface OAT1");
    model.comments(
        "Inside-out BAK fiber. Polymer membrane is one diffusion domain. "
            + "OAT1 is a surface flux at the membrane-cell (basolateral) face. "
            + "Apical efflux is a surface flux at the cell-dialysate face. "
            + "No volumetric Michaelis-Menten reaction in the cell domain."
    );

    parameters(model);
    component(model);
    geometry(model);
    selections(model);
    variables(model);
    materials(model);
    laminarBlood(model);
    laminarDialysate(model);
    transport(model);
    mesh(model);
    studies(model);
    results(model);

    return model;
  }

  public static void main(String[] args) {
    Model model = run();
    if (args != null && args.length > 0) {
      model.save(args[0]);
    }
  }

  // -------------------------------------------------------------------------
  private static void parameters(Model model) {
    model.param().set("L", "20[mm]", "Fiber length");
    model.param().set("R_blood", "0.15[mm]", "Blood lumen outer radius");
    model.param().set("R_mem", "0.25[mm]", "Membrane outer radius / OAT1 surface");
    model.param().set("R_cell", "0.27[mm]", "Cell outer radius / apical surface");
    model.param().set("R_shell", "1.80[mm]", "Dialysate housing radius");

    model.param().set("C_in", "0.1[mol/m^3]", "Inlet free IS (100 uM)");
    model.param().set("D_is", "5.58e-10[m^2/s]", "IS diffusivity in blood/cell/dialysate");
    model.param().set("eps_mem", "0.45", "Membrane porosity");
    model.param().set("D_mem", "eps_mem*D_is", "Effective membrane diffusivity");

    model.param().set("rho_b", "1050[kg/m^3]", "Blood density");
    model.param().set("mu_b", "0.0035[Pa*s]", "Blood viscosity");
    model.param().set("U_avg_b", "0.02358[m/s]", "Mean blood velocity");
    model.param().set("rho_d", "1000[kg/m^3]", "Dialysate density");
    model.param().set("mu_d", "0.7e-3[Pa*s]", "Dialysate viscosity");
    model.param().set("U_avg_d", "3.4e-4[m/s]", "Mean dialysate velocity");

    model.param().set("Km_bl", "0.02[mol/m^3]", "OAT1 Km (20 uM)");
    model.param().set("Km_ap", "0.02[mol/m^3]", "Apical Km");
    model.param().set("Vmax_A", "1e-7[mol/(m^2*s)]", "OAT1 areal Vmax");
    model.param().set("Vmax_ap", "1e-6[mol/(m^2*s)]", "Apical areal Vmax (10x OAT1 default)");
    model.param().set("T_end", "240[min]", "Simulation time");
  }

  private static void component(Model model) {
    model.component().create("comp1", true);
    model.component("comp1").geom().create("geom1", 2);
    model.component("comp1").mesh().create("mesh1");
    model.component("comp1").geom("geom1").label("Inside-out fiber (axisymmetric)");
    model.component("comp1").geom("geom1").lengthUnit("mm");
    model.component("comp1").geom("geom1").axisymmetric(true);
  }

  private static void geometry(Model model) {
    // Blood lumen
    model.component("comp1").geom("geom1").create("r_blood", "Rectangle");
    model.component("comp1").geom("geom1").feature("r_blood").label("Blood");
    model.component("comp1").geom("geom1").feature("r_blood")
        .set("pos", new String[]{"0", "0"});
    model.component("comp1").geom("geom1").feature("r_blood")
        .set("size", new String[]{"R_blood", "L"});

    // Polymer membrane — single domain
    model.component("comp1").geom("geom1").create("r_mem", "Rectangle");
    model.component("comp1").geom("geom1").feature("r_mem").label("Membrane");
    model.component("comp1").geom("geom1").feature("r_mem")
        .set("pos", new String[]{"R_blood", "0"});
    model.component("comp1").geom("geom1").feature("r_mem")
        .set("size", new String[]{"R_mem-R_blood", "L"});

    // Epithelial cell layer
    model.component("comp1").geom("geom1").create("r_cell", "Rectangle");
    model.component("comp1").geom("geom1").feature("r_cell").label("Cell layer");
    model.component("comp1").geom("geom1").feature("r_cell")
        .set("pos", new String[]{"R_mem", "0"});
    model.component("comp1").geom("geom1").feature("r_cell")
        .set("size", new String[]{"R_cell-R_mem", "L"});

    // Dialysate shell
    model.component("comp1").geom("geom1").create("r_dial", "Rectangle");
    model.component("comp1").geom("geom1").feature("r_dial").label("Dialysate");
    model.component("comp1").geom("geom1").feature("r_dial")
        .set("pos", new String[]{"R_cell", "0"});
    model.component("comp1").geom("geom1").feature("r_dial")
        .set("size", new String[]{"R_shell-R_cell", "L"});

    model.component("comp1").geom("geom1").run();
  }

  /**
   * Box selections in the geometry length unit (mm). Domain ids after
   * Finalize are 1=blood, 2=membrane, 3=cell, 4=dialysate if built in that order.
   */
  private static void selections(Model model) {
    explicitDomain(model, "dom_blood", "Blood domain", 1);
    explicitDomain(model, "dom_mem", "Membrane domain", 2);
    explicitDomain(model, "dom_cell", "Cell domain", 3);
    explicitDomain(model, "dom_dial", "Dialysate domain", 4);

    model.component("comp1").selection().create("dom_fluid", "Explicit");
    model.component("comp1").selection("dom_fluid").label("Fluid domains (blood+dialysate)");
    model.component("comp1").selection("dom_fluid").geom("geom1", 2);
    model.component("comp1").selection("dom_fluid").set(1, 4);

    model.component("comp1").selection().create("dom_solid", "Explicit");
    model.component("comp1").selection("dom_solid").label("No-flow domains (membrane+cell)");
    model.component("comp1").selection("dom_solid").geom("geom1", 2);
    model.component("comp1").selection("dom_solid").set(2, 3);

    // z = 0 inlets / z = L outlets / radial interfaces
    boxEdge(model, "bnd_blood_in", "Blood inlet z=0", 0.0, 0.15, -0.02, 0.02);
    boxEdge(model, "bnd_blood_out", "Blood outlet z=L", 0.0, 0.15, 19.98, 20.02);
    boxEdge(model, "bnd_dial_in", "Dialysate inlet z=L (countercurrent)", 0.27, 1.80, 19.98, 20.02);
    boxEdge(model, "bnd_dial_out", "Dialysate outlet z=0", 0.27, 1.80, -0.02, 0.02);

    boxEdge(model, "bnd_bm", "Blood-membrane interface", 0.149, 0.151, 0.0, 20.0);
    boxEdge(model, "bnd_mc", "Membrane-cell interface (OAT1)", 0.249, 0.251, 0.0, 20.0);
    boxEdge(model, "bnd_cd", "Cell-dialysate interface (apical)", 0.269, 0.271, 0.0, 20.0);
    boxEdge(model, "bnd_axis", "Axis r=0", -0.01, 0.01, 0.0, 20.0);
    boxEdge(model, "bnd_outer", "Housing r=R_shell", 1.79, 1.81, 0.0, 20.0);

    boxEdge(model, "bnd_mem_ends", "Membrane axial ends", 0.15, 0.25, -0.02, 0.02);
    // second axial end of membrane/cell: union via extra boxes
    boxEdge(model, "bnd_mem_ends_L", "Membrane axial end z=L", 0.15, 0.25, 19.98, 20.02);
    boxEdge(model, "bnd_cell_ends", "Cell axial end z=0", 0.25, 0.27, -0.02, 0.02);
    boxEdge(model, "bnd_cell_ends_L", "Cell axial end z=L", 0.25, 0.27, 19.98, 20.02);
  }

  private static void explicitDomain(Model model, String tag, String label, int id) {
    model.component("comp1").selection().create(tag, "Explicit");
    model.component("comp1").selection(tag).label(label);
    model.component("comp1").selection(tag).geom("geom1", 2);
    model.component("comp1").selection(tag).set(id);
  }

  private static void boxEdge(
      Model model, String tag, String label,
      double xmin, double xmax, double ymin, double ymax
  ) {
    model.component("comp1").selection().create(tag, "Box");
    model.component("comp1").selection(tag).label(label);
    model.component("comp1").selection(tag).geom("geom1", 1);
    model.component("comp1").selection(tag).set("xmin", xmin);
    model.component("comp1").selection(tag).set("xmax", xmax);
    model.component("comp1").selection(tag).set("ymin", ymin);
    model.component("comp1").selection(tag).set("ymax", ymax);
    model.component("comp1").selection(tag).set("condition", "inside");
  }

  private static void variables(Model model) {
    model.component("comp1").variable().create("var1");
    model.component("comp1").variable("var1").label("Inlet profiles");
    model.component("comp1").variable("var1")
        .set("u_blood", "2*U_avg_b*(1-(r/R_blood)^2)", "Poiseuille blood inlet (axial)");
    model.component("comp1").variable("var1")
        .set("J_OAT1", "Vmax_A*is/(Km_bl+is)", "OAT1 Michaelis-Menten flux");
    model.component("comp1").variable("var1")
        .set("J_apical", "Vmax_ap*is/(Km_ap+is)", "Apical Michaelis-Menten flux");
    model.component("comp1").variable("var1")
        .set("Da_OAT1", "Vmax_A/((D_mem/(R_mem*log(R_mem/R_blood)))*C_in)",
            "Damkohler: OAT1 vs membrane");
  }

  private static void materials(Model model) {
    model.component("comp1").material().create("mat_blood", "Common");
    model.component("comp1").material("mat_blood").label("Blood");
    model.component("comp1").material("mat_blood").selection().named("dom_blood");
    model.component("comp1").material("mat_blood").propertyGroup("def")
        .set("density", "rho_b");
    model.component("comp1").material("mat_blood").propertyGroup("def")
        .set("dynamicviscosity", "mu_b");

    model.component("comp1").material().create("mat_dial", "Common");
    model.component("comp1").material("mat_dial").label("Dialysate (water)");
    model.component("comp1").material("mat_dial").selection().named("dom_dial");
    model.component("comp1").material("mat_dial").propertyGroup("def")
        .set("density", "rho_d");
    model.component("comp1").material("mat_dial").propertyGroup("def")
        .set("dynamicviscosity", "mu_d");
  }

  private static void laminarBlood(Model model) {
    model.component("comp1").physics().create("spf", "LaminarFlow", "geom1");
    model.component("comp1").physics("spf").label("Laminar Flow — blood");
    model.component("comp1").physics("spf").selection().named("dom_blood");
    model.component("comp1").physics("spf").prop("ShapeProperty")
        .set("order_fluid", 1);

    model.component("comp1").physics("spf").create("inl_b", "Inlet", 1);
    model.component("comp1").physics("spf").feature("inl_b").label("Blood inlet");
    model.component("comp1").physics("spf").feature("inl_b").selection().named("bnd_blood_in");
    model.component("comp1").physics("spf").feature("inl_b").set("U0in", "u_blood");

    model.component("comp1").physics("spf").create("out_b", "Outlet", 1);
    model.component("comp1").physics("spf").feature("out_b").label("Blood outlet p=0");
    model.component("comp1").physics("spf").feature("out_b").selection().named("bnd_blood_out");
    model.component("comp1").physics("spf").feature("out_b").set("p0", "0");
    // Walls: default no-slip, including blood-membrane interface
  }

  private static void laminarDialysate(Model model) {
    model.component("comp1").physics().create("spf2", "LaminarFlow", "geom1");
    model.component("comp1").physics("spf2").label("Laminar Flow — dialysate (countercurrent)");
    model.component("comp1").physics("spf2").selection().named("dom_dial");
    model.component("comp1").physics("spf2").prop("ShapeProperty")
        .set("order_fluid", 1);

    // Inlet at z = L, flow toward z = 0 (opposite to blood)
    model.component("comp1").physics("spf2").create("inl_d", "Inlet", 1);
    model.component("comp1").physics("spf2").feature("inl_d").label("Dialysate inlet");
    model.component("comp1").physics("spf2").feature("inl_d").selection().named("bnd_dial_in");
    model.component("comp1").physics("spf2").feature("inl_d").set("U0in", "U_avg_d");

    model.component("comp1").physics("spf2").create("out_d", "Outlet", 1);
    model.component("comp1").physics("spf2").feature("out_d").label("Dialysate outlet p=0");
    model.component("comp1").physics("spf2").feature("out_d").selection().named("bnd_dial_out");
    model.component("comp1").physics("spf2").feature("out_d").set("p0", "0");
  }

  private static void transport(Model model) {
    model.component("comp1").physics().create("tds", "DilutedSpecies", "geom1");
    model.component("comp1").physics("tds").label("Transport of Diluted Species — IS");
    model.component("comp1").physics("tds").prop("ShapeProperty")
        .set("order_concentration", 2);
    model.component("comp1").physics("tds").field("concentration")
        .field("is");
    model.component("comp1").physics("tds").field("concentration")
        .component(1, "is");

    // Default convection-diffusion on all domains; velocity from blood NS in lumen
    model.component("comp1").physics("tds").feature("cdm1")
        .set("minput_velocity_src", "root.comp1.u");
    model.component("comp1").physics("tds").feature("cdm1")
        .setIndex("D_c", "D_is", 0);

    // Membrane: diffusion only, reduced D, no convection
    model.component("comp1").physics("tds").create("cdm_mem", "ConvectionDiffusion", 2);
    model.component("comp1").physics("tds").feature("cdm_mem").label("Membrane diffusion");
    model.component("comp1").physics("tds").feature("cdm_mem").selection().named("dom_mem");
    model.component("comp1").physics("tds").feature("cdm_mem").set("Convection", false);
    model.component("comp1").physics("tds").feature("cdm_mem").setIndex("D_c", "D_mem", 0);

    // Cell: diffusion only, NO volumetric reaction
    model.component("comp1").physics("tds").create("cdm_cell", "ConvectionDiffusion", 2);
    model.component("comp1").physics("tds").feature("cdm_cell").label("Cell diffusion (no volume MM)");
    model.component("comp1").physics("tds").feature("cdm_cell").selection().named("dom_cell");
    model.component("comp1").physics("tds").feature("cdm_cell").set("Convection", false);
    model.component("comp1").physics("tds").feature("cdm_cell").setIndex("D_c", "D_is", 0);

    // Dialysate: convection from spf2
    model.component("comp1").physics("tds").create("cdm_dial", "ConvectionDiffusion", 2);
    model.component("comp1").physics("tds").feature("cdm_dial").label("Dialysate convection-diffusion");
    model.component("comp1").physics("tds").feature("cdm_dial").selection().named("dom_dial");
    model.component("comp1").physics("tds").feature("cdm_dial")
        .set("minput_velocity_src", "root.comp1.u");
    model.component("comp1").physics("tds").feature("cdm_dial").setIndex("D_c", "D_is", 0);

    // Initial conditions: blood + membrane at C_in; cell + dialysate at 0
    model.component("comp1").physics("tds").feature("init1").set("is", "C_in");
    model.component("comp1").physics("tds").create("init_empty", "Init", 2);
    model.component("comp1").physics("tds").feature("init_empty")
        .label("Cell and dialysate initially toxin-free");
    model.component("comp1").physics("tds").feature("init_empty").selection()
        .named("dom_cell");
    model.component("comp1").physics("tds").feature("init_empty").set("is", "0");
    model.component("comp1").physics("tds").create("init_dial", "Init", 2);
    model.component("comp1").physics("tds").feature("init_dial")
        .label("Dialysate initially toxin-free");
    model.component("comp1").physics("tds").feature("init_dial").selection()
        .named("dom_dial");
    model.component("comp1").physics("tds").feature("init_dial").set("is", "0");

    // Blood inlet concentration
    model.component("comp1").physics("tds").create("conc_b", "Concentration", 1);
    model.component("comp1").physics("tds").feature("conc_b").label("Blood inlet c=C_in");
    model.component("comp1").physics("tds").feature("conc_b").selection().named("bnd_blood_in");
    model.component("comp1").physics("tds").feature("conc_b").set("is", "C_in");

    // Blood outlet: outflow (homogeneous Neumann / convective exit)
    model.component("comp1").physics("tds").create("outfl_b", "Outflow", 1);
    model.component("comp1").physics("tds").feature("outfl_b").label("Blood outflow");
    model.component("comp1").physics("tds").feature("outfl_b").selection().named("bnd_blood_out");

    // Dialysate inlet toxin-free
    model.component("comp1").physics("tds").create("conc_d", "Concentration", 1);
    model.component("comp1").physics("tds").feature("conc_d").label("Dialysate inlet c=0");
    model.component("comp1").physics("tds").feature("conc_d").selection().named("bnd_dial_in");
    model.component("comp1").physics("tds").feature("conc_d").set("is", "0");

    model.component("comp1").physics("tds").create("outfl_d", "Outflow", 1);
    model.component("comp1").physics("tds").feature("outfl_d").label("Dialysate outflow");
    model.component("comp1").physics("tds").feature("outfl_d").selection().named("bnd_dial_out");

    // No flux on membrane/cell axial ends (default No Flux) — explicit for clarity
    model.component("comp1").physics("tds").create("nflx_mem0", "NoFlux", 1);
    model.component("comp1").physics("tds").feature("nflx_mem0").label("No axial flux membrane z=0");
    model.component("comp1").physics("tds").feature("nflx_mem0").selection().named("bnd_mem_ends");
    model.component("comp1").physics("tds").create("nflx_memL", "NoFlux", 1);
    model.component("comp1").physics("tds").feature("nflx_memL").label("No axial flux membrane z=L");
    model.component("comp1").physics("tds").feature("nflx_memL").selection().named("bnd_mem_ends_L");
    model.component("comp1").physics("tds").create("nflx_cell0", "NoFlux", 1);
    model.component("comp1").physics("tds").feature("nflx_cell0").label("No axial flux cell z=0");
    model.component("comp1").physics("tds").feature("nflx_cell0").selection().named("bnd_cell_ends");
    model.component("comp1").physics("tds").create("nflx_cellL", "NoFlux", 1);
    model.component("comp1").physics("tds").feature("nflx_cellL").label("No axial flux cell z=L");
    model.component("comp1").physics("tds").feature("nflx_cellL").selection().named("bnd_cell_ends_L");

    model.component("comp1").physics("tds").create("nflx_outer", "NoFlux", 1);
    model.component("comp1").physics("tds").feature("nflx_outer").label("Impermeable housing");
    model.component("comp1").physics("tds").feature("nflx_outer").selection().named("bnd_outer");

    // ----- OAT1: membrane-cell surface flux (THE replacement for volume MM) -----
    // Inward flux on the CELL side. After first GUI open, confirm the boundary
    // normal: positive J_OAT1 must enter the cell. If the flux goes the wrong
    // way, set N0_is to -J_OAT1. Use membrane-side concentration if available
    // (up(is) or down(is)); start with local is (cell-side) then switch.
    model.component("comp1").physics("tds").create("oat1_bl", "Fluxes", 1);
    model.component("comp1").physics("tds").feature("oat1_bl")
        .label("OAT1 basolateral flux (membrane-cell)");
    model.component("comp1").physics("tds").feature("oat1_bl").selection().named("bnd_mc");
    model.component("comp1").physics("tds").feature("oat1_bl")
        .setIndex("N0", "J_OAT1", 0);

    // ----- Apical efflux: cell-dialysate surface flux -----
    model.component("comp1").physics("tds").create("mrp_ap", "Fluxes", 1);
    model.component("comp1").physics("tds").feature("mrp_ap")
        .label("Apical efflux flux (cell-dialysate)");
    model.component("comp1").physics("tds").feature("mrp_ap").selection().named("bnd_cd");
    model.component("comp1").physics("tds").feature("mrp_ap")
        .setIndex("N0", "J_apical", 0);
  }

  private static void mesh(Model model) {
    model.component("comp1").mesh("mesh1").label("Mapped quads (radial refinement)");
    model.component("comp1").mesh("mesh1").create("map1", "Map");
    model.component("comp1").mesh("mesh1").feature("map1").selection().all();

    model.component("comp1").mesh("mesh1").feature("map1").create("dis_r", "Distribution");
    model.component("comp1").mesh("mesh1").feature("map1").feature("dis_r")
        .set("numelem", 20);
    model.component("comp1").mesh("mesh1").feature("map1").create("dis_z", "Distribution");
    model.component("comp1").mesh("mesh1").feature("map1").feature("dis_z")
        .set("numelem", 80);

    model.component("comp1").mesh("mesh1").create("size1", "Size");
    model.component("comp1").mesh("mesh1").feature("size1").selection().named("dom_cell");
    model.component("comp1").mesh("mesh1").feature("size1").set("hauto", 2);
    model.component("comp1").mesh("mesh1").feature("size1")
        .set("custom", "on");
    model.component("comp1").mesh("mesh1").feature("size1")
        .set("hmax", "0.005[mm]");

    model.component("comp1").mesh("mesh1").run();
  }

  private static void studies(Model model) {
    // Step 1: stationary flow (blood + dialysate)
    // Step 2: time-dependent species with frozen velocity
    model.study().create("std1");
    model.study("std1").label("Flow then IS transport (240 min)");

    model.study("std1").create("stat", "Stationary");
    model.study("std1").feature("stat").label("Stationary laminar flow");
    model.study("std1").feature("stat").set("activate", new String[]{
        "spf", "on", "spf2", "on", "tds", "off"
    });

    model.study("std1").create("time", "Transient");
    model.study("std1").feature("time").label("Time-dependent IS transport");
    model.study("std1").feature("time").set("tunit", "min");
    model.study("std1").feature("time").set("tlist", "range(0,20,T_end)");
    model.study("std1").feature("time").set("activate", new String[]{
        "spf", "off", "spf2", "off", "tds", "on"
    });

    // Parametric sweep of OAT1 areal capacity (apical held at 10*Vmax_A in Parameters)
    model.study().create("std2");
    model.study("std2").label("Parametric Vmax_A bottleneck sweep");
    model.study("std2").create("param", "Parametric");
    model.study("std2").feature("param").label("Sweep Vmax_A");
    model.study("std2").feature("param").set("pname", new String[]{"Vmax_A"});
    model.study("std2").feature("param").set("plistarr", new String[]{
        "1e-9 3e-9 1e-8 3e-8 1e-7 3e-7 1e-6 3e-6 1e-5 3e-5 1e-4"
    });
    model.study("std2").feature("param").set("punit", new String[]{"mol/(m^2*s)"});
    model.study("std2").create("stat2", "Stationary");
    model.study("std2").feature("stat2").set("activate", new String[]{
        "spf", "on", "spf2", "on", "tds", "off"
    });
    model.study("std2").create("time2", "Transient");
    model.study("std2").feature("time2").set("tunit", "min");
    model.study("std2").feature("time2").set("tlist", "range(0,20,T_end)");
    model.study("std2").feature("time2").set("activate", new String[]{
        "spf", "off", "spf2", "off", "tds", "on"
    });
  }

  private static void results(Model model) {
    model.result().numerical().create("int_bm", "IntLine");
    model.result().numerical("int_bm").label("Molar flow blood-membrane");
    model.result().numerical("int_bm").selection().named("bnd_bm");
    model.result().numerical("int_bm").set("expr", "2*pi*r*tds.ndflux_is");
    model.result().numerical("int_bm").set("descr", "Normal IS flux * 2*pi*r");
    model.result().numerical("int_bm").set("unit", "mol/s");

    model.result().numerical().create("int_oat1", "IntLine");
    model.result().numerical("int_oat1").label("Molar flow OAT1 (membrane-cell)");
    model.result().numerical("int_oat1").selection().named("bnd_mc");
    model.result().numerical("int_oat1").set("expr", "2*pi*r*tds.ndflux_is");
    model.result().numerical("int_oat1").set("unit", "mol/s");

    model.result().numerical().create("int_cd", "IntLine");
    model.result().numerical("int_cd").label("Molar flow apical (cell-dialysate)");
    model.result().numerical("int_cd").selection().named("bnd_cd");
    model.result().numerical("int_cd").set("expr", "2*pi*r*tds.ndflux_is");
    model.result().numerical("int_cd").set("unit", "mol/s");

    model.result().table().create("tbl_bm", "Table");
    model.result().table("tbl_bm").label("Flux BM vs time");
    model.result().numerical("int_bm").set("table", "tbl_bm");

    model.result().table().create("tbl_oat1", "Table");
    model.result().table("tbl_oat1").label("Flux OAT1 vs time");
    model.result().numerical("int_oat1").set("table", "tbl_oat1");

    model.result().table().create("tbl_cd", "Table");
    model.result().table("tbl_cd").label("Flux CD vs time");
    model.result().numerical("int_cd").set("table", "tbl_cd");

    model.result().create("pg_c", "PlotGroup2D");
    model.result("pg_c").label("IS concentration");
    model.result("pg_c").create("surf1", "Surface");
    model.result("pg_c").feature("surf1").set("expr", "is");
    model.result("pg_c").feature("surf1").set("unit", "mol/m^3");
  }
}
