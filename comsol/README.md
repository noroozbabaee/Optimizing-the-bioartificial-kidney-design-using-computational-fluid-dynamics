# COMSOL models (surface OAT1)

These Java files are **COMSOL Multiphysics 6.3 Model Java**. They are the portable source form of a `.mph` model (the binary `.mph` files from the thesis are not in this repository).

| File | What it is |
|---|---|
| `BAK_IO_OAT1_SurfaceFlux.java` | **Full new model**: inside-out 2D axisymmetric BAK fiber with surface OAT1 + apical efflux |
| `apply_oat1_surface_flux.java` | Patch method to add the same fluxes on an existing thesis `.mph` |

## What the new model does

- Four domains: blood | **one membrane** | cell | dialysate  
- Laminar blood flow (Poiseuille inlet) and countercurrent dialysate flow  
- Transport of diluted species (indoxyl sulfate)  
- **No** volumetric Michaelis–Menten in the cell  
- **OAT1 flux** on the membrane–cell boundary  
- **Apical efflux** on the cell–dialysate boundary  
- Line integrals of molar flow at blood–membrane, OAT1, and apical faces (for the bottleneck test)

## Open in COMSOL (GUI)

1. COMSOL Multiphysics 6.3 → **File → Open**  
2. File type: Java (`BAK_IO_OAT1_SurfaceFlux.java`)  
3. Check **Selections** (Box features) highlight the intended edges. Domain numbers are 1=blood, 2=membrane, 3=cell, 4=dialysate if the rectangles built in that order. If they differ, edit the Explicit domain selections.  
4. Confirm OAT1 flux **direction**: `J_OAT1` must go **into the cell**. If concentration in the cell falls instead of rising, set the OAT1 `N0` expression to `-J_OAT1`.  
5. Right-click **Study 1 → Compute**.  
6. For the bottleneck sweep, set `Vmax_ap = 10*Vmax_A` in Parameters, then compute **Study 2**.  
7. Export tables `Flux BM vs time`, `Flux OAT1 vs time`, `Flux CD vs time` as  
   `data/oat1_surface_flux/flux_BM_VmaxA_<value>.txt` (and OAT1, CD).  
8. Run `python src/oat1_comsol_export_analysis.py` from the repo root.

## Batch compile (optional)

```text
comsol compile BAK_IO_OAT1_SurfaceFlux.java
comsol batch -inputfile BAK_IO_OAT1_SurfaceFlux.class BAK_IO_OAT1_SurfaceFlux.mph
```

On Windows the `comsol` launcher is typically:

`C:\Program Files\COMSOL\COMSOL63\Multiphysics\bin\win64\comsol.exe`

## Parameters to sweep

| Parameter | Default | Role |
|---|---|---|
| `Vmax_A` | `1e-7[mol/(m^2*s)]` | OAT1 areal capacity |
| `Vmax_ap` | `1e-6[mol/(m^2*s)]` | Apical capacity (keep ~10× `Vmax_A` to isolate OAT1 vs membrane) |
| `Km_bl`, `Km_ap` | `0.02[mol/m^3]` | 20 µM |
| `C_in` | `0.1[mol/m^3]` | 100 µM |
| `Da_OAT1` | (defined) | ≪1 OAT1-limited; ≫1 membrane-limited |

Thesis volumetric `Vmax = 1e6 umol/(L·min)` over a 20 µm cell is about `Vmax_A = 3.3e-4 mol/(m^2·s)` (`Da ~ 10^3`, membrane-limited).
