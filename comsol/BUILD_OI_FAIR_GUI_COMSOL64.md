# Next model: fair outside-in (`BAK_OI_fair.mph`)

Build this **in the COMSOL 6.4 GUI**. Do not use Model Java.

This is the next production geometry after your working **inside-out** model
(`BAK_IO.mph`). Same physics: four domains, three concentration fields,
**surface OAT1 and surface apical**, no volumetric Michaelis–Menten in the cell,
stationary flow then transient transport, countercurrent dialysate.

**Do not** make the thesis “adjusted OI” (housing still 1.8 mm with a huge
membrane). That is not this model.

**Do not** only change radii on the IO rectangles. In OI the **layer order
reverses**: dialysate is the lumen, blood is the thin outer shell.

---

## 0. What you are matching (why this geometry exists)

| Quantity | IO (already built) | OI fair (this model) | Must match? |
|---|---|---|---|
| OAT1 area `A_OAT1 = 2 π R_OAT1 L` | 31.416 mm² | **31.416 mm²** | yes |
| Blood volume `V_b` | 1.414 mm³ | **1.414 mm³** | yes |
| Blood flow `Q_b` | 0.1000 mL/min | **0.1000 mL/min** | yes |
| Dialysate flow `Q_d` | 0.2030 mL/min | **0.2030 mL/min** | yes |
| Wall thicknesses (membrane 100 µm, cell 20 µm) | yes | yes | yes |
| Housing radius | 1.800 mm | **0.3808 mm** | no — this is how `V_b` is matched |
| Blood-side gap shape | 0.15 mm lumen | **0.0308 mm annulus** | no — hydrodynamics stay unmatched; report that |

Housing formula (do not type this in COMSOL; the number is already in `R_house`):

```
R_house = sqrt(R_BM^2 + R_blood_IO^2) = sqrt(0.35^2 + 0.15^2) = 0.3808 mm
```

---

## 1. How to start

**Recommended:** `File > Save As` from the working `BAK_IO.mph` →
`BAK_OI_fair.mph`, then change parameters, **redraw the four rectangles in the
OI order**, and **re-point every physics Domain Selection**. Domain 1 is no
longer blood.

If you start from Model Wizard instead, use the same physics list as IO
(`spf`, `tds`, then add `spf2`, `tds2`, `tds3`) and the tables below.

Length unit of Geometry 1: **mm**. Space dimension: **2D Axisymmetric**.
**Form Union** (not Form Assembly).

---

## 2. Dimensions (mm)

Radial order from the **axis outward**:

```
axis |  dialysate lumen  |  cell  |  membrane  |  blood shell  | housing
  0         0.23 mm        0.25      0.35 mm      0.3808 mm
                 ↑ OAT1 here (membrane–cell)
           ↑ apical here (cell–dialysate)
```

| Interface | Symbol | Radius (mm) | What sits there |
|---|---|---|---|
| Axis | — | 0 | symmetry |
| Apical (cell–dialysate) | `R_AP` | **0.23** | irreversible apical flux |
| OAT1 (membrane–cell) | `R_OAT1` | **0.25** | reversible OAT1 flux |
| Blood–membrane | `R_BM` | **0.35** | passive continuity (no Flux node) |
| Housing | `R_house` | **0.3808** | outer wall, no flux |
| Fibre length | `L` | **20** | axial |

| Layer | r from (mm) | r to (mm) | Thickness | Fluid? |
|---|---|---|---|---|
| Dialysate lumen | 0 | 0.23 | 0.23 mm | yes (`spf2`) |
| Cell | 0.23 | 0.25 | **20 µm** | no |
| Polymer membrane | 0.25 | 0.35 | **100 µm** | no |
| Blood shell | 0.35 | 0.3808 | **30.8 µm** | yes (`spf`) |

The blood gap is thin. Mesh it; do not use the IO radial distribution blindly.

---

## 3. Global Parameters (type these exactly)

`Global Definitions > Parameters 1`. Replace the IO radii and both mean
velocities. Keep `Q_b` and `Q_d` (throughput is matched, speed is not).

| Name | Expression | Description |
|---|---|---|
| `L` | `20[mm]` | Fibre length |
| `R_AP` | `0.23[mm]` | Cell–dialysate (apical), **inner** cell face |
| `R_OAT1` | `0.25[mm]` | Membrane–cell (OAT1) — **same as IO** |
| `R_BM` | `0.35[mm]` | Blood–membrane, **outer** membrane face |
| `R_house` | `0.3808[mm]` | Housing; matches IO blood volume |
| `C_in` | `0.1[mol/m^3]` | Inlet free IS (100 µM) |
| `D_is` | `5.58e-10[m^2/s]` | Aqueous IS diffusivity |
| `eps_mem` | `0.45` | Membrane porosity |
| `D_mem` | `eps_mem*D_is` | Effective membrane diffusivity |
| `Q_b` | `1.666772e-9[m^3/s]` | Blood flow (0.10 mL/min) — **same as IO** |
| `Q_d` | `3.382911e-9[m^3/s]` | Dialysate flow (~0.20 mL/min) — **same as IO** |
| `U_avg_b` | `2.358e-2[m/s]` | Mean blood speed = `Q_b / (π (R_house² − R_BM²))` |
| `U_avg_d` | `2.035565e-2[m/s]` | Mean dialysate speed = `Q_d / (π R_AP²)` |
| `Km_bl` | `0.02[mol/m^3]` | OAT1 Km (20 µM) |
| `Km_ap` | `0.02[mol/m^3]` | Apical Km |
| `Vmax_A` | `1e-7[mol/(m^2*s)]` | OAT1 areal capacity |
| `Vmax_ap` | `10*Vmax_A` | Apical capacity (not limiting) |
| `T_end` | `60[min]` | Transport duration |
| `rho_b` | `1050[kg/m^3]` | Blood density |
| `mu_b` | `0.0035[Pa*s]` | Blood viscosity |
| `rho_d` | `1000[kg/m^3]` | Dialysate density |
| `mu_d` | `0.0007[Pa*s]` | Dialysate viscosity |

`U_avg_d` is **much larger than in IO** (0.0204 vs 0.00034 m/s) because the
dialysate lumen is small. That is correct: same `Q_d`, smaller area.

---

## 4. Geometry rectangles

Delete or edit the four IO rectangles. **Width as expressions**, height `L`,
position z = `0`.

| Rectangle | Position r | Width | Layer after Build All |
|---|---|---|---|
| r1 | `0` | `R_AP` | **dialysate** (lumen) |
| r2 | `R_AP` | `R_OAT1-R_AP` | **cell** |
| r3 | `R_OAT1` | `R_BM-R_OAT1` | **membrane** |
| r4 | `R_BM` | `R_house-R_BM` | **blood** (thin shell) |

Click **Build All**. Expect **4 domains, 13 boundaries**.

Hover and confirm **from the axis**:

| Domain | Must be |
|---|---|
| 1 | dialysate |
| 2 | cell |
| 3 | membrane |
| 4 | blood |

If domain 1 is still blood, the rectangles are still in IO order. Stop and fix
geometry before physics.

Numeric widths (check only): r1 width 0.23 mm, r2 0.02 mm, r3 0.10 mm,
r4 0.0308 mm.

---

## 5. Physics domain assignment (the IO assignments are wrong here)

Edit **Domain Selection on the interface node**, not on Fluid Properties
(that list is often greyed out).

| Interface | Domains | Species / fluid |
|---|---|---|
| `spf` (Laminar Flow) | **4 only** | blood |
| `spf2` (Laminar Flow 2) | **1 only** | dialysate |
| `tds` | **3 and 4** | `c` in membrane + blood |
| `tds2` | **2 only** | `c2` in cell |
| `tds3` | **1 only** | `c3` in dialysate |

No physics on the wrong side of the wall: `spf` must not sit on domain 1.

### Fluid properties (User defined, not From material)

| Interface | Density | Dynamic viscosity |
|---|---|---|
| `spf` | `rho_b` | `mu_b` |
| `spf2` | `rho_d` | `mu_d` |

### Velocity field for transport

| Transport | Convection velocity |
|---|---|
| `tds` on blood (domain 4) | **`spf`** |
| `tds` on membrane (domain 3) | **off**, `u = 0`, `D = D_mem` (second Fluid node) |
| `tds2` | convection **off**, `D = D_is` |
| `tds3` | **`spf2`** (not `spf` — that was the IO `comp1.w` error) |

Concentration discretization: **Quadratic**.

---

## 6. Identify boundaries by location (do not reuse IO numbers)

Click each edge until the highlight matches the table. Numbers below are the
usual COMSOL order for this stack; **verify**.

| Typical bnd | Location | Physics |
|---|---|---|
| 1 | axis `r = 0` | axial symmetry (automatic) |
| | dialysate **outlet** `z = 0` on domain 1 | `spf2` Pressure 0; `tds3` Outflow |
| | dialysate **inlet** `z = L` on domain 1 | `spf2` Normal inflow `U_avg_d`; `tds3` `c3 = 0` |
| | apical `r = R_AP` | `tds2` Flux `J0 = -J_apical`; `tds3` Flux `J0 = +J_apical` |
| | OAT1 `r = R_OAT1` | `tds` Flux `J0 = -J_OAT1`; `tds2` Flux `J0 = +J_OAT1` |
| | blood–membrane `r = R_BM` | **no Flux** — `c` continuous inside `tds` |
| | blood **inlet** `z = 0` on domain 4 | `spf` Normal inflow `U_avg_b`; `tds` `c = C_in` |
| | blood **outlet** `z = L` on domain 4 | `spf` Pressure 0; `tds` Outflow |
| | housing `r = R_house` | wall, no flux |

Countercurrent: blood in at `z = 0`, dialysate in at `z = L`.

---

## 7. Variables (same as IO)

`Component 1 > Definitions > Variables 1`:

| Name | Expression |
|---|---|
| `J_OAT1` | `Vmax_A*(c/(Km_bl+c) - c2/(Km_bl+c2))` |
| `J_apical` | `Vmax_ap*c2/(Km_ap+c2)` |

Use your actual species names if they are not `c`, `c2`.

**No** volumetric reaction in the cell.

---

## 8. Transport and Flux pairs

| Interface | Condition | Where | Expression |
|---|---|---|---|
| `tds` | Fluid 1 | domain 4 | `D = D_is`, convection from `spf` |
| `tds` | Fluid 2 | domain 3 | `D = D_mem`, convection off |
| `tds` | Concentration | blood inlet | `C_in` |
| `tds` | Outflow | blood outlet | — |
| `tds` | Flux | OAT1 edge | **`J0 = -J_OAT1`** |
| `tds2` | Fluid | domain 2 | `D = D_is`, convection off |
| `tds2` | Flux | OAT1 edge | **`J0 = +J_OAT1`** |
| `tds2` | Flux | apical edge | **`J0 = -J_apical`** |
| `tds3` | Fluid | domain 1 | `D = D_is`, convection from `spf2` |
| `tds3` | Concentration | dialysate inlet | `0` |
| `tds3` | Outflow | dialysate outlet | — |
| `tds3` | Flux | apical edge | **`J0 = +J_apical`** |

Each pair must be equal and opposite. If `c2` does not rise, swap **both**
OAT1 signs together.

---

## 9. Mesh (thin blood shell)

Mapped mesh.

| Place | Distribution (first pass) |
|---|---|
| Axial edges (length `L`) | **80** |
| Dialysate lumen (radial) | **20** |
| Cell (20 µm) | **10** |
| Membrane (100 µm) | **20** |
| Blood shell (**31 µm**) | **15** |

If the solver struggles in the blood gap, increase the blood radial count,
not the cell count first.

---

## 10. Study (same as IO)

1. **Stationary**: enable `spf` and `spf2` only. Disable `tds`, `tds2`, `tds3`.
2. **Time Dependent**: `range(0,5,60)` with unit **min**. Enable transport only;
   disable both laminar-flow interfaces.
3. Compute.

### Checks before you trust it

1. `c2` in the cell **rises** from 0.
2. `c` in blood stays between 0 and `C_in`.
3. OAT1 molar flow (export, next section) does not exceed
   `Vmax_A * A_OAT1 = 1e-7 * 3.1416e-5 ≈ 3.14e-12 mol/s`.
4. Blood domain is the **outer** strip; dialysate is the **inner** strip.

---

## 11. Export for Python

Results → Derived Values → Line Integration, unit **mol/s**:

| Name | Edge | Expression |
|---|---|---|
| Flux BM | `r = R_BM` | `2*pi*r*tds.ndflux_c` |
| Flux OAT1 | `r = R_OAT1` | `2*pi*r*J_OAT1` |
| Flux CD | `r = R_AP` | `2*pi*r*J_apical` |

Evaluate all time steps. Export plain text to:

```
data/comsol_surface_oat1/OI_fair/flux_BM.txt
data/comsol_surface_oat1/OI_fair/flux_OAT1.txt
data/comsol_surface_oat1/OI_fair/flux_CD.txt
```

Then from the repository root:

```
python src/comsol_io_oi_comparison.py
```

---

## 12. After this: unmatched OI (control only)

Only after `BAK_OI_fair.mph` computes and `c2` rises. Save as
`BAK_OI_original.mph`. This geometry is **unfair** (different `A_OAT1` and
`V_b`). It exists so you can show the size artefact. It is not the improved
design.

### Parameters that change

| Name | OI original |
|---|---|
| `R_AP` | `0.15[mm]` |
| `R_OAT1` | `0.17[mm]` |
| `R_BM` | `0.27[mm]` |
| `R_house` | `1.8[mm]` |
| `U_avg_b` | `1.675192e-4[m/s]` |
| `U_avg_d` | `4.785840e-2[m/s]` |

### Rectangles (still OI order: dialysate | cell | membrane | blood)

| Rectangle | Position r | Width | Layer |
|---|---|---|---|
| r1 | `0` | `R_AP` | dialysate |
| r2 | `R_AP` | `R_OAT1-R_AP` | cell |
| r3 | `R_OAT1` | `R_BM-R_OAT1` | membrane |
| r4 | `R_BM` | `R_house-R_BM` | blood (thick shell) |

Same physics mapping: domain 1 dialysate, 2 cell, 3 membrane, 4 blood.
Export into `data/comsol_surface_oat1/OI_original/`.

---

## 13. Side-by-side geometry table (all three models)

| | IO | OI fair **(build this now)** | OI original (later) |
|---|---|---|---|
| Lumen fluid | blood | dialysate | dialysate |
| `R_AP` (mm) | 0.27 | **0.23** | 0.15 |
| `R_OAT1` (mm) | 0.25 | **0.25** | 0.17 |
| `R_BM` (mm) | 0.15 | **0.35** | 0.27 |
| `R_house` (mm) | 1.80 | **0.3808** | 1.80 |
| `U_avg_b` (m/s) | 2.358e-2 | **2.358e-2** | 1.675e-4 |
| `U_avg_d` (m/s) | 3.400e-4 | **2.036e-2** | 4.786e-2 |
| `A_OAT1` (mm²) | 31.42 | **31.42** | 21.36 |
| `V_b` (mm³) | 1.414 | **1.414** | 199.0 |

---

## 14. Errors you already hit on IO (same fixes)

| Message | Fix |
|---|---|
| Undefined `rho` | User defined density and viscosity |
| `Undefined variable comp1.w` on the blood or dialysate domain | `tds` velocity = `spf`; `tds3` velocity = `spf2` |
| Fluid Properties domain list greyed out | Change selection on the **Laminar Flow interface** node |
| `c2` stays 0 | OAT1 Flux is on the wrong edge, or signs not a pair |

---

## 15. What not to build in this version

- No volumetric `R = -Vmax_V c2/(Km+c2)` in the cell.
- No 1.8 mm housing with `R_OAT1 = 0.25` mm (that is unmatched area or the
  thesis adjusted OI).
- No Java `File > Open` of `BAK_OI_fair.java`.
