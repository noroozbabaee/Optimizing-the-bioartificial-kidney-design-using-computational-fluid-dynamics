/*
 * BAK_OI.java
 *
 * COMSOL 6.3 / 6.4 Model Java for surface OAT1 BAK fiber.
 *
 * UNIVERSITY COMSOL 6.4 (your Open dialog lists *.class, not *.java):
 *   1. Copy this file + compile_models.bat into Documents\\COMSOL\\Batch
 *   2. Double-click compile_models.bat  (creates BAK_OI.class)
 *   3. COMSOL -> File -> Open -> Compiled Model File for Java (*.class)
 *   4. Open BAK_OI.class
 *   5. File -> Save As -> BAK_OI.mph
 *   6. Right-click Mesh -> Build All, then Study 1 -> Compute
 *   7. Check plot isc rises. If not, flip both OAT1 N0 signs together.
 *
 * Do not open damaged RM_*.mph files from other folders.
 */

import com.comsol.model.Model;
import com.comsol.model.util.ModelUtil;

public class BAK_OI {

  public static Model run() {
    Model model = ModelUtil.create("Model");
    model.label("BAK outside-in (thesis) - surface OAT1");
    model.comments("OI_original: surface OAT1 + apical efflux. control (thesis outside-in, unmatched area and blood volume).");
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
    coupleFlowAndTransport(model);
    mesh(model);
    studies(model);
    results(model);
    return model;
  }

  public static void main(String[] args) {
    // File > Open of the .class calls run(). No save here (IOException on COMSOL 6.4).
    run();
  }

  private static void parameters(Model model) {
    model.param().set("L", "20[mm]", "Fiber length");
    model.param().set("R_AP", "0.150000[mm]", "Apical / cell-dialysate radius");
    model.param().set("R_OAT1", "0.170000[mm]", "OAT1 / membrane-cell radius");
    model.param().set("R_BM", "0.270000[mm]", "Blood-membrane radius");
    model.param().set("R_house", "1.800000[mm]", "Housing radius");

    model.param().set("C_in", "0.1[mol/m^3]", "Inlet free IS = 100 uM (thesis)");
    model.param().set("D_is", "5.58e-10[m^2/s]", "IS diffusivity in aqueous domains");
    model.param().set("eps_mem", "0.45", "Membrane porosity (thesis)");
    model.param().set("D_mem", "eps_mem*D_is", "Effective membrane diffusivity");

    model.param().set("rho_b", "1050.0[kg/m^3]", "Blood density");
    model.param().set("mu_b", "0.0035[Pa*s]", "Blood viscosity");
    model.param().set("rho_d", "1000.0[kg/m^3]", "Dialysate density");
    model.param().set("mu_d", "0.0007[Pa*s]", "Dialysate viscosity");

    // Volumetric flows are the FAIR quantities (same for IO and both OI models).
    model.param().set("Q_b", "1.666772e-09[m^3/s]", "Blood volumetric flow (~0.10 mL/min)");
    model.param().set("Q_d", "3.382911e-09[m^3/s]", "Dialysate volumetric flow (~0.20 mL/min)");
    model.param().set("U_avg_b", "1.675192e-04[m/s]", "Mean blood speed = Q_b / A_blood for THIS geometry");
    model.param().set("U_avg_d", "4.785840e-02[m/s]", "Mean dialysate speed = Q_d / A_dial for THIS geometry");

    model.param().set("Km_bl", "0.02[mol/m^3]", "OAT1 Km = 20 uM");
    model.param().set("Km_ap", "0.02[mol/m^3]", "Apical Km = 20 uM (same as thesis split-cell default)");
    // First-run default is in the OAT1-sensitive window. Thesis-equivalent areal
    // Vmax is Param.Vmax_A_equiv (Da >> 1, membrane-limited). Sweep both.
    model.param().set("Vmax_A", "1e-7[mol/(m^2*s)]", "OAT1 areal capacity (change this)");
    model.param().set("Vmax_ap", "10*Vmax_A", "Apical capacity; 10x so apical is not the bottleneck");
    model.param().set("Vmax_A_equiv", "0.0003333333333333334[mol/(m^2*s)]",
        "Thesis volumetric Vmax collapsed onto 20 um cell");
    model.param().set("T_end", "60[min]", "Transport duration (raise to 240 min to match thesis)");
  }

  private static void component(Model model) {
    model.component().create("comp1", true);
    model.component("comp1").geom().create("geom1", 2);
    model.component("comp1").mesh().create("mesh1");
    model.component("comp1").geom("geom1").label("OI_original fiber (axisymmetric)");
    model.component("comp1").geom("geom1").lengthUnit("mm");
    model.component("comp1").geom("geom1").axisymmetric(true);
  }

  private static void geometry(Model model) {

    model.component("comp1").geom("geom1").create("r_dial", "Rectangle");
    model.component("comp1").geom("geom1").feature("r_dial").label("Dialysate");
    model.component("comp1").geom("geom1").feature("r_dial")
        .set("pos", new String[]{"0.000000[mm]", "0"});
    model.component("comp1").geom("geom1").feature("r_dial")
        .set("size", new String[]{"0.150000[mm]", "L"});
    model.component("comp1").geom("geom1").create("r_cell", "Rectangle");
    model.component("comp1").geom("geom1").feature("r_cell").label("Cell layer");
    model.component("comp1").geom("geom1").feature("r_cell")
        .set("pos", new String[]{"0.150000[mm]", "0"});
    model.component("comp1").geom("geom1").feature("r_cell")
        .set("size", new String[]{"0.020000[mm]", "L"});
    model.component("comp1").geom("geom1").create("r_mem", "Rectangle");
    model.component("comp1").geom("geom1").feature("r_mem").label("Membrane");
    model.component("comp1").geom("geom1").feature("r_mem")
        .set("pos", new String[]{"0.170000[mm]", "0"});
    model.component("comp1").geom("geom1").feature("r_mem")
        .set("size", new String[]{"0.100000[mm]", "L"});
    model.component("comp1").geom("geom1").create("r_blood", "Rectangle");
    model.component("comp1").geom("geom1").feature("r_blood").label("Blood");
    model.component("comp1").geom("geom1").feature("r_blood")
        .set("pos", new String[]{"0.270000[mm]", "0"});
    model.component("comp1").geom("geom1").feature("r_blood")
        .set("size", new String[]{"1.530000[mm]", "L"});
    model.component("comp1").geom("geom1").run();
  }

  private static void selections(Model model) {
    explicitDomain(model, "dom_blood", "Blood domain", 4);
    explicitDomain(model, "dom_mem", "Membrane domain", 3);
    explicitDomain(model, "dom_cell", "Cell domain", 2);
    explicitDomain(model, "dom_dial", "Dialysate domain", 1);

    model.component("comp1").selection().create("dom_blood_mem", "Explicit");
    model.component("comp1").selection("dom_blood_mem").label("Blood + membrane (field is)");
    model.component("comp1").selection("dom_blood_mem").geom("geom1", 2);
    model.component("comp1").selection("dom_blood_mem").set(4, 3);

    boxEdge(model, "bnd_blood_in", "Blood inlet z=0", 0.26900, 1.80100, -0.02000, 0.02000);

    boxEdge(model, "bnd_blood_out", "Blood outlet z=L", 0.26900, 1.80100, 19.98000, 20.02000);

    boxEdge(model, "bnd_dial_in", "Dialysate inlet z=L (countercurrent)", -0.00100, 0.15100, 19.98000, 20.02000);

    boxEdge(model, "bnd_dial_out", "Dialysate outlet z=0", -0.00100, 0.15100, -0.02000, 0.02000);

    boxEdge(model, "bnd_bm", "Blood-membrane interface", 0.26850, 0.27150, 0.00000, 20.00000);

    boxEdge(model, "bnd_mc", "Membrane-cell interface (OAT1)", 0.16850, 0.17150, 0.00000, 20.00000);

    boxEdge(model, "bnd_cd", "Cell-dialysate interface (apical)", 0.14850, 0.15150, 0.00000, 20.00000);

    boxEdge(model, "bnd_axis", "Axis r=0", -0.01000, 0.01000, 0.00000, 20.00000);

    boxEdge(model, "bnd_outer", "Housing wall", 1.79800, 1.80200, 0.00000, 20.00000);

    boxEdge(model, "bnd_mem_ends", "Membrane axial end z=0", 0.16900, 0.27100, -0.02000, 0.02000);

    boxEdge(model, "bnd_mem_ends_L", "Membrane axial end z=L", 0.16900, 0.27100, 19.98000, 20.02000);

    boxEdge(model, "bnd_cell_ends", "Cell axial end z=0", 0.14900, 0.17100, -0.02000, 0.02000);

    boxEdge(model, "bnd_cell_ends_L", "Cell axial end z=L", 0.14900, 0.17100, 19.98000, 20.02000);
  }

  private static void explicitDomain(Model model, String tag, String label, int id) {
    model.component("comp1").selection().create(tag, "Explicit");
    model.component("comp1").selection(tag).label(label);
    model.component("comp1").selection(tag).geom("geom1", 2);
    model.component("comp1").selection(tag).set(id);
  }

  private static void boxEdge(
      Model model, String tag, String label,
      double xmin, double xmax, double ymin, double ymax) {
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
    model.component("comp1").variable("var1").label("Transporter fluxes and inlet profile");
    model.component("comp1").variable("var1")
        .set("u_blood", "U_avg_b", "Blood inlet axial speed");
    // Reversible OAT1: net flux positive when extracellular is > intracellular isc.
    model.component("comp1").variable("var1")
        .set("J_OAT1", "Vmax_A*(is/(Km_bl+is)-isc/(Km_bl+isc))",
            "OAT1 net flux mol/(m^2 s), membrane -> cell when >0");
    model.component("comp1").variable("var1")
        .set("J_apical", "Vmax_ap*isc/(Km_ap+isc)",
            "Apical efflux mol/(m^2 s), cell -> dialysate");
    model.component("comp1").variable("var1")
        .set("n_dot_OAT1", "2*pi*r*J_OAT1", "OAT1 molar flow per length * r-weight");
  }

  private static void materials(Model model) {
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
  }

  private static void laminarBlood(Model model) {
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
  }

  private static void laminarDialysate(Model model) {
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
  }

  private static void transportBloodMembrane(Model model) {
    model.component("comp1").physics().create("tds", "DilutedSpecies", "geom1");
    model.component("comp1").physics("tds").label("TDS - IS in blood + membrane");
    model.component("comp1").physics("tds").selection().named("dom_blood_mem");
    model.component("comp1").physics("tds").prop("ShapeProperty").set("order_concentration", 2);
    model.component("comp1").physics("tds").field("concentration").field("is");
    model.component("comp1").physics("tds").field("concentration").component(1, "is");

    // COMSOL 6.4: velocity via Multiphysics ReactingFlowDilutedSpecies
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
  }

  private static void transportCell(Model model) {
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
  }

  private static void transportDialysate(Model model) {
    model.component("comp1").physics().create("tds3", "DilutedSpecies", "geom1");
    model.component("comp1").physics("tds3").label("TDS - IS in dialysate");
    model.component("comp1").physics("tds3").selection().named("dom_dial");
    model.component("comp1").physics("tds3").prop("ShapeProperty").set("order_concentration", 2);
    model.component("comp1").physics("tds3").field("concentration").field("isd");
    model.component("comp1").physics("tds3").field("concentration").component(1, "isd");
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
  }

  private static void oat1AndApicalCoupling(Model model) {
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
  }


  private static void coupleFlowAndTransport(Model model) {
    // Reacting Flow, Diluted Species: sync Laminar Flow velocity into TDS (COMSOL 6.4).
    model.component("comp1").multiphysics().create("rfd_blood", "ReactingFlowDilutedSpecies", 2);
    model.component("comp1").multiphysics("rfd_blood").label("Flow-transport blood");
    model.component("comp1").multiphysics("rfd_blood").selection().named("dom_blood");
    model.component("comp1").multiphysics("rfd_blood").set("FluidFlow", "spf");
    model.component("comp1").multiphysics("rfd_blood").set("DilutedSpecies", "tds");

    model.component("comp1").multiphysics().create("rfd_dial", "ReactingFlowDilutedSpecies", 2);
    model.component("comp1").multiphysics("rfd_dial").label("Flow-transport dialysate");
    model.component("comp1").multiphysics("rfd_dial").selection().named("dom_dial");
    model.component("comp1").multiphysics("rfd_dial").set("FluidFlow", "spf2");
    model.component("comp1").multiphysics("rfd_dial").set("DilutedSpecies", "tds3");
  }

  private static void mesh(Model model) {
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
  }

  private static void studies(Model model) {
    String[] flowOn = new String[] {
        "spf", "on", "spf2", "on", "tds", "off", "tds2", "off", "tds3", "off"};
    String[] tdsOn = new String[] {
        "spf", "off", "spf2", "off", "tds", "on", "tds2", "on", "tds3", "on"};

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
    model.study("std2").feature("param").set("pname", new String[]{"Vmax_A"});
    model.study("std2").feature("param").set("plistarr", new String[]{
        "1e-9 1e-8 1e-7 1e-6 1e-5 1e-4 3.333e-4"});
    model.study("std2").feature("param").set("punit", new String[]{"mol/(m^2*s)"});
    model.study("std2").create("stat2", "Stationary");
    model.study("std2").feature("stat2").set("activate", flowOn);
    model.study("std2").create("time2", "Transient");
    model.study("std2").feature("time2").set("tunit", "min");
    model.study("std2").feature("time2").set("tlist", "range(0,5,T_end)");
    model.study("std2").feature("time2").set("activate", tdsOn);
  }

  private static void results(Model model) {
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
  }

  private static void intLine(Model model, String tag, String label, String sel, String expr) {
    model.result().numerical().create(tag, "IntLine");
    model.result().numerical(tag).label(label);
    model.result().numerical(tag).selection().named(sel);
    model.result().numerical(tag).set("expr", expr);
    model.result().numerical(tag).set("unit", "mol/s");
  }
}
