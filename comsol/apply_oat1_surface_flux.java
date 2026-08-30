/*
 * COMSOL 6.3 — apply surface OAT1 + apical efflux on the existing BAK model.
 *
 * The polymer membrane stays ONE diffusion domain.
 * Remove the volumetric Michaelis-Menten reaction from the cell domain.
 * Place OAT1 as a flux on the membrane-cell (basolateral) interface.
 * Place apical efflux as a flux on the cell-dialysate interface.
 *
 * Usage:
 *   1. Open the inside-out (or outside-in) .mph in COMSOL 6.3.
 *   2. File > Reset History, then File > Save As Model Method, or
 *      run this as a model method after replacing the placeholders:
 *        tdsTag, cellDomain, bmBoundary, mcBoundary, cdBoundary
 *   3. Confirm selections in the Graphics window (membrane-cell vs cell-dialysate).
 *   4. Parametric sweep Param.Vmax_A over logspace(1e-9, 1e-4).
 *   5. Export line integrals of normal total flux at BM, MC (OAT1), and CD.
 *
 * Units: Vmax_A in mol/(m^2*s), Km in mol/m^3, is in mol/m^3.
 *
 * Adjacent-domain concentration:
 *   For an interior Flux feature on the CELL side of mcBoundary, "is"
 *   is the cell-side concentration. OAT1 should see the MEMBRANE-side
 *   (extracellular) concentration. Use the up()/down() operator, or
 *   an Identity Pair / adjacent-value coupling. Check the normal so that
 *   a positive J0 is INTO the cell and OUT OF the membrane.
 */

import com.comsol.model.*;
import com.comsol.model.util.*;

public class apply_oat1_surface_flux {

  public static void main(String[] args) {
    // load(args[0]) in a real batch job; this file is a method template
  }

  public static void run(Model model) {

    // --- Replace these tags from your .mph (Model Builder names) ---
    String tds = "tds";           // Transport of Diluted Species
    String cellDomSel = "cell";   // cell domain selection name, if defined
    String reacVol = "reac1";     // existing volumetric MM reaction feature
    String mcBnd = "bnd_mc";      // membrane-cell boundary selection
    String cdBnd = "bnd_cd";      // cell-dialysate boundary selection
    String bmBnd = "bnd_bm";      // blood-membrane (export only)

    // Parameters (SI)
    model.param().set("Km_bl", "0.02[mol/m^3]", "OAT1 Km");
    model.param().set("Km_ap", "0.02[mol/m^3]", "Apical Km");
    model.param().set("Vmax_A", "1e-7[mol/(m^2*s)]", "OAT1 areal Vmax");
    model.param().set("Vmax_ap", "1e-6[mol/(m^2*s)]", "Apical areal Vmax (not limiting if >> Vmax_A)");
    model.param().set("C_in", "0.1[mol/m^3]", "Inlet IS");

    // 1) Turn OFF volumetric uptake in the cell domain
    try {
      model.physics(tds).feature(reacVol).active(false);
    } catch (Exception e) {
      // If the tag differs: disable every Reactions feature whose domain is the cell
    }

    // 2) OAT1 flux on membrane-cell interface
    //    J_OAT1 = Vmax_A * c_mem / (Km_bl + c_mem)
    //    Put this Flux feature on the CELL physics/domain side of the interior boundary.
    //    Replace c_mem with the membrane-side concentration operator, e.g. down(is) or up(is).
    if (model.physics(tds).feature().index("oat1_bl") < 0) {
      model.physics(tds).create("oat1_bl", "Fluxes", 1);
    }
    model.physics(tds).feature("oat1_bl").label("OAT1 basolateral flux");
    // model.physics(tds).feature("oat1_bl").selection().named(mcBnd);
    model.physics(tds).feature("oat1_bl").set("species", 1, "is");
    model.physics(tds).feature("oat1_bl").set(
        "J0", 1, "Vmax_A*down(is)/(Km_bl+down(is))"
    );

    // Matching outward flux from the membrane side of the same boundary
    // so mass is not created at the interface. If a single interior Flux
    // already applies to both adjacent domains with a consistent normal,
    // skip oat1_bl_mem.
    if (model.physics(tds).feature().index("oat1_bl_mem") < 0) {
      model.physics(tds).create("oat1_bl_mem", "Fluxes", 1);
    }
    model.physics(tds).feature("oat1_bl_mem").label("OAT1 membrane-side counterpart");
    model.physics(tds).feature("oat1_bl_mem").set("species", 1, "is");
    model.physics(tds).feature("oat1_bl_mem").set(
        "J0", 1, "-Vmax_A*is/(Km_bl+is)"
    );

    // 3) Apical efflux on cell-dialysate interface
    if (model.physics(tds).feature().index("mrp_ap") < 0) {
      model.physics(tds).create("mrp_ap", "Fluxes", 1);
    }
    model.physics(tds).feature("mrp_ap").label("Apical efflux flux");
    model.physics(tds).feature("mrp_ap").set("species", 1, "is");
    model.physics(tds).feature("mrp_ap").set(
        "J0", 1, "Vmax_ap*is/(Km_ap+is)"
    );

    // 4) Parametric sweep of OAT1 capacity (keep Vmax_ap = 10*Vmax_A first)
    try {
      model.study().create("std_oat1");
      model.study("std_oat1").create("param", "Parametric");
      model.study("std_oat1").feature("param").set("pname", new String[]{"Vmax_A"});
      model.study("std_oat1").feature("param").set(
          "plistarr",
          new String[]{"1e-9 3e-9 1e-8 3e-8 1e-7 3e-7 1e-6 3e-6 1e-5 3e-5 1e-4"}
      );
    } catch (Exception e) {
      // Study may already exist
    }

    // Silence unused-name warnings in batch templates
    String unused = cellDomSel + bmBnd + cdBnd + mcBnd;
    if (unused.isEmpty()) {
      return;
    }
  }
}
