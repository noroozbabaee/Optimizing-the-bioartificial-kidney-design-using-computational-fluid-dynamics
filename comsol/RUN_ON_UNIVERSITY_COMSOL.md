# How to run the new BAK models on the university COMSOL server

> **COMSOL 6.4:** File-Open lists `*.class`, not `*.java`.
> Follow **`OPEN_ON_COMSOL64.txt`** and run **`compile_models.bat`** first.
> Open `BAK_IO.class` (short name), not old `RM_*.mph` files.
> Always copy the **latest** `BAK_*.java` from git — Desktop copies go stale.

This is the whole plan, in order. Do not skip the sign check in step 3.

## What you are comparing

| Model | Java / class | What it is |
|---|---|---|
| **IO** | `BAK_IO` | Thesis inside-out. Blood in the lumen. **Reference.** |
| **OI original** | `BAK_OI` | Thesis outside-in (layers inverted out to 1.8 mm). **Control only — unfair area and blood volume.** |
| **OI fair** | `BAK_OI_fair` | Outside-in with the **same OAT1 area and same blood volume** as IO. **This is the fair pair.** |

All three use the **same physics**:

- polymer membrane = one diffusion domain
- **no** volumetric Michaelis–Menten in the cell
- **OAT1** = reversible surface flux at membrane–cell (`is` vs `isc`)
- **apical efflux** = irreversible surface flux at cell–dialysate
- same \(Q_b\), \(Q_d\), \(C_{\mathrm{in}}\), \(D\), \(\varepsilon\), \(K_m\), \(L\)

The thesis “adjusted OI” is **not** used. It matched blood volume by making the membrane huge, so it cannot answer “which arrangement is better”.

## Parameters (keep these unless you have a better measured value)

| Name | Value | Why |
|---|---|---|
| \(C_{\mathrm{in}}\) | 0.1 mol/m³ (100 µM) | Thesis free IS inlet |
| \(D_{\mathrm{IS}}\) | \(5.58\times 10^{-10}\) m²/s | Thesis |
| \(\varepsilon\) | 0.45 | Thesis membrane porosity |
| \(K_m\) | 20 µM | Thesis OAT1 |
| \(Q_b\) | 0.100 mL/min | From thesis IO mean blood speed × IO lumen area |
| \(Q_d\) | 0.203 mL/min | From thesis IO mean dialysate speed × IO shell area |
| \(L\) | 20 mm | Thesis fiber length |
| Membrane | 100 µm | Thesis |
| Cell | 20 µm | Thesis |
| Default \(V_{\max}^{A}\) | \(10^{-7}\) mol m⁻² s⁻¹ | In the range where OAT1 can still matter |
| Thesis-equivalent \(V_{\max}^{A}\) | \(3.33\times 10^{-4}\) mol m⁻² s⁻¹ | Old volumetric \(10^6\) µmol L⁻¹ min⁻¹ × 20 µm. **Membrane-limited.** |
| \(V_{\max}^{\mathrm{ap}}\) | \(10\,V_{\max}^{A}\) | So apical exit is not the hidden bottleneck |

Fair OI housing radius is **0.381 mm**, not 1.8 mm. That is required by matching blood volume at the same OAT1 radius. Blood-side *hydrodynamics* (gap, shear) are **not** matched — report that.

## On the remote server (COMSOL 6.4)

### 1. Copy + compile

Copy `comsol/BAK_IO.java`, `BAK_OI.java`, `BAK_OI_fair.java`, and `compile_models.bat` into a short folder (e.g. `Desktop\BAK`). Delete old `.class` files, then run `compile_models.bat`.

### 2. Open IO first

1. COMSOL 6.4 → **File → Open** → type **Compiled Model File (*.class)** → `BAK_IO.class`
2. Success = Model Builder shows **Component 1** (Geometry, Physics, Mesh, Studies). Save As `BAK_IO.mph`.
3. Under **Multiphysics**, confirm:
   - Flow-transport blood → Laminar Flow - blood + TDS blood+membrane
   - Flow-transport dialysate → Laminar Flow - dialysate + TDS dialysate
4. Click a few **Box** selections (blood inlet, OAT1, apical) and check highlighted edges.

**COMSOL 6.4 API already fixed in these files** (do not reintroduce):
`D_c` → use `Dc`; no `minput_velocity_src`; no `FluidFlow`/`DilutedSpecies` `.set()` on multiphysics; `main()` = `run()` only.

### 3. Sign check (5 minutes, do not skip)

Mesh → Build All. Study 1 → Compute.

Open plot **IS cell (isc)**. After a few minutes `isc` must be **positive and rising**.

- If `isc` stays 0: OAT1 flux is not connected (wrong boundary).
- If `isc` goes negative or the cell empties: flip **both** OAT1 `N0` signs together (`-J_OAT1` ↔ `J_OAT1` on membrane and cell). Keep them equal-and-opposite.

Then open `BAK_OI.class` and `BAK_OI_fair.class` and repeat the sign check once per geometry.

### 4. Production run

Keep Parameters identical except geometry (already baked into each file):

- `T_end = 60[min]` for a first comparison, `240[min]` to match the thesis window
- Either one `Vmax_A` (same in all three models) **or** Study 2 (the \(V_{\max}^{A}\) sweep)

### 5. Export (exact names)

For each model, evaluate the three line integrations vs time and export **plain text**:

```
data/comsol_surface_oat1/IO/flux_BM.txt
data/comsol_surface_oat1/IO/flux_OAT1.txt
data/comsol_surface_oat1/IO/flux_CD.txt

data/comsol_surface_oat1/OI_original/flux_BM.txt
data/comsol_surface_oat1/OI_original/flux_OAT1.txt
data/comsol_surface_oat1/OI_original/flux_CD.txt

data/comsol_surface_oat1/OI_fair/flux_BM.txt
data/comsol_surface_oat1/OI_fair/flux_OAT1.txt
data/comsol_surface_oat1/OI_fair/flux_CD.txt
```

COMSOL table format (comments allowed):

```
% Time (min)    Molar flow (mol/s)
0    0
5    1.2e-12
...
```

If you run the \(V_{\max}^{A}\) sweep, name files `flux_BM_VmaxA_1e-7.txt` (and OAT1, CD) in the same folders.

### 6. Plot on your laptop / this repo

```text
python3 src/comsol_io_oi_comparison.py
```

Figures go to `figures/comsol_io_oi/`. The script prints a checklist if exports are missing.

## Optional batch (no GUI)

```text
comsol compile BAK_IO_OAT1_SurfaceFlux.java
comsol batch -inputfile BAK_IO_OAT1_SurfaceFlux.class -outputfile BAK_IO_OAT1.mph
```

Same for the two OI files. GUI File → Open is more reliable the first time because of the sign check.

## Regenerating the Java

If you change radii in `src/bak_geometries.py`:

```text
python3 src/write_comsol_java_models.py
```

Do not hand-edit the three `BAK_*.java` files unless you are only fixing a COMSOL-version API issue on the server.
