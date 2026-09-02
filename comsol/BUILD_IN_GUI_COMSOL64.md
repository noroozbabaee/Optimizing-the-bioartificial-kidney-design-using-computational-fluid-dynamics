# Build the BAK surface-OAT1 model by hand in COMSOL 6.4

Use this instead of the Java files. You build **one** model, then change four
parameters to get all three geometries. No compiling, no Model Java, no
"Unknown parameter" errors — the GUI can only offer settings your build has.

Time: about 45 minutes for the first model, 5 minutes for each other geometry.

---

## 0. What you are building

An axisymmetric fiber, 20 mm long, with four stacked layers. Solute (indoxyl
sulfate, IS) moves:

```
blood  --diffusion-->  membrane  --OAT1 surface flux-->  cell  --apical flux-->  dialysate
```

Three separate concentration fields are needed because OAT1 sees a different
concentration on each side of the cell membrane. They are linked only by
equal-and-opposite surface fluxes, so mass is transferred and never created.

---

## 1. New model

1. `File > New > Model Wizard`
2. **2D Axisymmetric**
3. Add physics: `Fluid Flow > Single-Phase Flow > Laminar Flow (spf)`
4. Add physics again: `Chemical Species Transport > Transport of Diluted Species (tds)`
5. Study: **Stationary**, then Done. (More studies come later.)

---

## 2. Parameters

`Global Definitions > Parameters 1`. Type these exactly (IO values shown):

| Name | Expression | Description |
|---|---|---|
| `L` | `20[mm]` | Fiber length |
| `R_BM` | `0.15[mm]` | Blood-membrane radius |
| `R_OAT1` | `0.25[mm]` | Membrane-cell radius (OAT1 surface) |
| `R_AP` | `0.27[mm]` | Cell-dialysate radius (apical) |
| `R_house` | `1.8[mm]` | Housing radius |
| `C_in` | `0.1[mol/m^3]` | Inlet free IS (100 uM) |
| `D_is` | `5.58e-10[m^2/s]` | IS diffusivity in water |
| `eps_mem` | `0.45` | Membrane porosity |
| `D_mem` | `eps_mem*D_is` | Effective membrane diffusivity |
| `Q_b` | `1.666772e-9[m^3/s]` | Blood flow (0.10 mL/min) |
| `Q_d` | `3.382911e-9[m^3/s]` | Dialysate flow (0.20 mL/min) |
| `U_avg_b` | `2.358e-2[m/s]` | Mean blood speed (geometry specific) |
| `U_avg_d` | `3.400e-4[m/s]` | Mean dialysate speed (geometry specific) |
| `Km_bl` | `0.02[mol/m^3]` | OAT1 Km (20 uM) |
| `Km_ap` | `0.02[mol/m^3]` | Apical Km |
| `Vmax_A` | `1e-7[mol/(m^2*s)]` | OAT1 areal capacity |
| `Vmax_ap` | `10*Vmax_A` | Apical capacity |
| `T_end` | `60[min]` | Transport duration |

Geometry-specific values for the other two models are in section 10.

---

## 3. Geometry

`Component 1 > Geometry 1`, set **Length unit = mm**.

Add four rectangles (`Right-click Geometry > Rectangle`). For each, set
**Position r** and **Width**; height is always `L`, position z is `0`.

| Rectangle | Position r | Width | Layer |
|---|---|---|---|
| r1 | `0` | `R_BM` | Blood |
| r2 | `R_BM` | `R_OAT1-R_BM` | Membrane |
| r3 | `R_OAT1` | `R_AP-R_OAT1` | Cell |
| r4 | `R_AP` | `R_house-R_AP` | Dialysate |

Click **Build All**. You should see four stacked strips, domains numbered
**1, 2, 3, 4** from the axis outward.

Hover each domain to confirm: 1 = blood, 2 = membrane, 3 = cell, 4 = dialysate.

---

## 4. Second flow interface and two more transport interfaces

`Component 1 > Add Physics`:

- `Laminar Flow` again → becomes **spf2** (dialysate)
- `Transport of Diluted Species` twice → becomes **tds2** (cell) and **tds3** (dialysate)

Then set each interface's **Domain Selection**:

| Interface | Domains | Meaning |
|---|---|---|
| spf | 1 | blood |
| spf2 | 4 | dialysate |
| tds | 1, 2 | blood + membrane (species `c`) |
| tds2 | 3 | cell (species `c2`) |
| tds3 | 4 | dialysate (species `c3`) |

Note the species names COMSOL gives you (usually `c`, `c2`, `c3`). Use those
exact names in section 6.

---

## 5. Flow settings

**spf (blood)**

- `Inlet` on the bottom edge of domain 1 (z = 0): Velocity, **Normal inflow
  velocity** `U_avg_b`
- `Outlet` on the top edge of domain 1 (z = L): Pressure `0`

**spf2 (dialysate, countercurrent)**

- `Inlet` on the **top** edge of domain 4 (z = L): `U_avg_d`
- `Outlet` on the **bottom** edge of domain 4 (z = 0): Pressure `0`

Countercurrent means the dialysate inlet is at the opposite end from blood.

---

## 6. Variables (the transporter kinetics)

`Component 1 > Definitions > Variables 1`:

| Name | Expression |
|---|---|
| `J_OAT1` | `Vmax_A*(c/(Km_bl+c) - c2/(Km_bl+c2))` |
| `J_apical` | `Vmax_ap*c2/(Km_ap+c2)` |

`J_OAT1` is reversible: positive when extracellular exceeds intracellular.
`J_apical` is irreversible: cell to dialysate only.

If your species are not named `c`, `c2`, replace the names above.

---

## 7. Transport settings

**tds (blood + membrane)**

- `Transport Properties`/`Fluid` on domain 1: Diffusion `D_is`
- Add a second `Fluid` node on domain 2: Diffusion `D_mem`, and clear the
  Convection checkbox for that node (no flow in the polymer)
- `Concentration` on the blood inlet edge: `C_in`
- `Outflow` on the blood outlet edge
- `Flux` on the **membrane-cell** edge (r = R_OAT1): inward flux `-J_OAT1`

**tds2 (cell)**

- `Fluid`: Diffusion `D_is`, Convection off
- `Flux` on the membrane-cell edge: `J_OAT1`
- `Flux` on the cell-dialysate edge (r = R_AP): `-J_apical`

**tds3 (dialysate)**

- `Fluid`: Diffusion `D_is`
- `Concentration` on the dialysate inlet edge: `0`
- `Outflow` on the dialysate outlet edge
- `Flux` on the cell-dialysate edge: `J_apical`

The two members of each pair must be equal and opposite. That is what makes
the transfer conservative.

---

## 8. Multiphysics coupling

`Component 1 > Multiphysics > Reacting Flow, Diluted Species` twice:

| Coupling | Fluid flow | Species transport |
|---|---|---|
| 1 | Laminar Flow (spf) | Transport of Diluted Species (tds) |
| 2 | Laminar Flow 2 (spf2) | Transport of Diluted Species 3 (tds3) |

This is what feeds the computed velocity into the transport equations.

---

## 9. Mesh, study, first check

**Mesh:** `Mapped`, then `Distribution` on the axial edges with 80 elements.
Add a `Size` node on domain 3 (cell) with maximum element size `0.005 mm` —
the cell layer is only 20 um thick and needs several elements across it.

**Study:**

1. `Study 1 > Step 1: Stationary` — under **Physics and Variables Selection**,
   disable tds, tds2, tds3. This solves the flow only.
2. Right-click Study 1 → `Study Steps > Time Dependent`. Times
   `range(0,5,60)`, unit **min**. Disable spf and spf2 in this step.
3. Compute.

**Sign check (do not skip):** plot `c2` (cell concentration). It must rise from
zero. If it falls or goes negative, flip **both** OAT1 flux signs together
(`-J_OAT1` and `J_OAT1` swap places). Keep them equal and opposite.

---

## 10. The other two geometries

**Next model after a working IO file:** follow the full click-path, tables, and
domain map in [`BUILD_OI_FAIR_GUI_COMSOL64.md`](BUILD_OI_FAIR_GUI_COMSOL64.md).
Do not only edit radii on the IO rectangles — the layer order reverses.

Save as `BAK_IO.mph` first. Then change only these parameters and save under a
new name. Everything else stays identical — that is what makes the comparison
fair.

| Parameter | IO | OI original | OI fair |
|---|---|---|---|
| `R_BM` | `0.15[mm]` | `0.27[mm]` | `0.35[mm]` |
| `R_OAT1` | `0.25[mm]` | `0.17[mm]` | `0.25[mm]` |
| `R_AP` | `0.27[mm]` | `0.15[mm]` | `0.23[mm]` |
| `R_house` | `1.8[mm]` | `1.8[mm]` | `0.3808[mm]` |
| `U_avg_b` | `2.358e-2[m/s]` | `1.675192e-4[m/s]` | `2.358e-2[m/s]` |
| `U_avg_d` | `3.400e-4[m/s]` | `4.785840e-2[m/s]` | `2.035565e-2[m/s]` |

**Important:** in the OI models the layer order reverses — dialysate is in the
lumen and blood is in the shell. So for OI you must also swap the domain
assignments: spf on domain 4 becomes the **outer** blood, spf2 on domain 1
becomes the lumen dialysate, and tds/tds3 follow. Rebuild the rectangles in the
order dialysate, cell, membrane, blood.

**Why `R_house` is 0.3808 mm for fair OI:** it is the housing radius that gives
the same blood volume as IO at the same OAT1 area. The thesis "adjusted OI"
kept 1.8 mm and inflated the membrane instead, which is why it could not answer
which arrangement is better.

---

## 11. Export for the Python comparison

For each model, add three **Line Integration** nodes under Results > Derived
Values, with expression and unit `mol/s`:

| Node | Edge | Expression |
|---|---|---|
| Flux BM | r = R_BM | `2*pi*r*tds.ndflux_c` |
| Flux OAT1 | r = R_OAT1 | `2*pi*r*J_OAT1` |
| Flux CD | r = R_AP | `2*pi*r*J_apical` |

Evaluate each over all time steps, then `Table > Export` as plain text into:

```
data/comsol_surface_oat1/IO/flux_BM.txt
data/comsol_surface_oat1/IO/flux_OAT1.txt
data/comsol_surface_oat1/IO/flux_CD.txt
```

and the same three names under `OI_original/` and `OI_fair/`.

Then from the repository root:

```bash
python3 src/comsol_io_oi_comparison.py
```

That script computes clearance, normalizes by OAT1 area, and writes the
IO vs OI comparison figures.
