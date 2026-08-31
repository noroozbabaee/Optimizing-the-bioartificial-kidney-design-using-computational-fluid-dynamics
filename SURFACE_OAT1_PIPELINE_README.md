# Surface OAT1 BAK Pipeline — Student Guide

**Audience:** bachelor / master students who will open COMSOL, run the three hollow-fiber models, export tables, and plot them in Python.

**Goal of this work:** put organic anion transporter 1 (OAT1) on the **cell surface** (where it belongs biologically), keep the polymer membrane as **one** diffusion layer, and compare **inside-out (IO)** vs **outside-in (OI)** in a way that is **fair**.

**Repository branch with these files:** `cursor/oat1-surface-flux-bottleneck-4ac1`  
**Pull request:** https://github.com/noroozbabaee/Optimizing-the-bioartificial-kidney-design-using-computational-fluid-dynamics/pull/1

**Short path if you only want to run COMSOL today:** [`comsol/RUN_ON_UNIVERSITY_COMSOL.md`](comsol/RUN_ON_UNIVERSITY_COMSOL.md)

---

## Table of contents

1. [What this project is about](#1-what-this-project-is-about)
2. [Biological picture (why the layer order is fixed)](#2-biological-picture-why-the-layer-order-is-fixed)
3. [Two hollow-fiber arrangements](#3-two-hollow-fiber-arrangements)
4. [Governing equations](#4-governing-equations)
5. [Parameter tables (with explanations)](#5-parameter-tables-with-explanations)
6. [Geometry tables (IO, original OI, fair OI)](#6-geometry-tables-io-original-oi-fair-oi)
7. [Diagnosed issues in the original thesis workflow](#7-diagnosed-issues-in-the-original-thesis-workflow)
8. [Why each diagnosis matters (reasoning)](#8-why-each-diagnosis-matters-reasoning)
9. [The new pipeline (step by step)](#9-the-new-pipeline-step-by-step)
10. [Rationale behind each pipeline step](#10-rationale-behind-each-pipeline-step)
11. [Where the codes live](#11-where-the-codes-live)
12. [How to get the codes from GitHub](#12-how-to-get-the-codes-from-github)
13. [How to run COMSOL on the university server](#13-how-to-run-comsol-on-the-university-server)
14. [How to export results](#14-how-to-export-results)
15. [How to plot results in Python](#15-how-to-plot-results-in-python)
16. [Damköhler number: how to read “who is limiting”](#16-damköhler-number-how-to-read-who-is-limiting)
17. [Checklist before you trust a number](#17-checklist-before-you-trust-a-number)
18. [FAQ](#18-faq)

---

## 1. What this project is about

A **bioartificial kidney (BAK)** hollow fiber tries to remove protein-bound uremic toxins such as **indoxyl sulfate (IS)**. Conventional dialysis removes free toxin poorly when most of the toxin is bound to albumin. Proximal tubule cells use **OAT1** to take toxin up from the blood side and export it toward the dialysate (urine) side.

In the original master thesis, CFD was done in **COMSOL Multiphysics 6.3**. Post-processing was done in **Python**. This pipeline keeps that split:

| Stage | Tool | Your job |
|---|---|---|
| Build geometry + physics | COMSOL (Java model files) | Open → check selections → Compute |
| Diagnose bottleneck / fair IO vs OI | Same COMSOL models | Sweep \(V_{\max}^{A}\), export flux tables |
| Plot and compare | Python in this repository | Load exports, plot clearance |

We **cannot** invent COMSOL numbers in Python. Clearance plots of the two designs only become real after you export tables from the university COMSOL license.

---

## 2. Biological picture (why the layer order is fixed)

OAT1 sits on the **basolateral** membrane of the epithelial cell: it faces the polymer membrane / blood side. The **apical** membrane faces the dialysate (filtrate).

So the **material order** is always:

```text
blood  |  polymer membrane  |  cell  |  dialysate
         ↑ OAT1 here (basolateral)     ↑ apical efflux here
```

What changes between IO and OI is only **which fluid sits in the lumen**:

| Name | Lumen (center) | Shell (outside) |
|---|---|---|
| Inside-out (IO) | blood | dialysate |
| Outside-in (OI) | dialysate | blood |

**Student mistake to avoid:** do not put the cell on the blood side of the membrane. OAT1 would then face the wrong compartment.

---

## 3. Two hollow-fiber arrangements

### 3.1 Inside-out (IO) — reference

Radial stack from the axis (\(r = 0\)):

```text
blood (0 → 0.15 mm)
membrane (0.15 → 0.25 mm)     ← OAT1 at r = 0.25 mm
cell (0.25 → 0.27 mm)         ← apical at r = 0.27 mm
dialysate (0.27 → 1.80 mm)
```

### 3.2 Outside-in original (OI_original) — control only

Thesis inversion (housing still 1.80 mm):

```text
dialysate (0 → 0.15 mm)       ← apical at r = 0.15 mm
cell (0.15 → 0.17 mm)         ← OAT1 at r = 0.17 mm
membrane (0.17 → 0.27 mm)
blood (0.27 → 1.80 mm)
```

**Not a fair pair to IO:** OAT1 area and blood volume both differ a lot.

### 3.3 Outside-in fair (OI_fair) — fair comparison partner

Same wall thicknesses as IO, **same OAT1 radius** (hence same area), **same blood volume**:

```text
dialysate (0 → 0.23 mm)       ← apical at r = 0.23 mm
cell (0.23 → 0.25 mm)         ← OAT1 at r = 0.25 mm  (same as IO)
membrane (0.25 → 0.35 mm)
blood (0.35 → 0.381 mm)       ← thin shell: volume matched to IO
```

Housing is **0.381 mm**, not 1.80 mm. That is required by volume matching (see Eq. 4 below).

---

## 4. Governing equations

### 4.1 Fluid flow (blood and dialysate)

Incompressible laminar Navier–Stokes (COMSOL Laminar Flow):

\[
\rho\bigl(\mathbf{u}\cdot\nabla\bigr)\mathbf{u}
=
-\nabla p
+
\mu\nabla^2\mathbf{u},
\qquad
\nabla\cdot\mathbf{u}=0
\]

| Symbol | Meaning |
|---|---|
| \(\mathbf{u}\) | velocity |
| \(p\) | pressure |
| \(\rho\) | density |
| \(\mu\) | dynamic viscosity |

**Boundary conditions (flow):**

- Inlet: laminar mean speed \(U_{\mathrm{avg}}\) from volumetric flow \(Q/A_{\mathrm{cs}}\)
- Outlet: \(p = 0\)
- Walls (including membrane faces): no-slip
- Membrane and cell domains: **no flow** (diffusion only for the toxin)

Blood and dialysate are **countercurrent**: blood enters at \(z=0\), dialysate enters at \(z=L\).

### 4.2 Solute transport (indoxyl sulfate)

In each domain that holds concentration \(c\):

\[
\frac{\partial c}{\partial t}
+
\mathbf{u}\cdot\nabla c
=
\nabla\cdot\bigl(D\nabla c\bigr)
\]

| Domain | Convection? | Diffusivity |
|---|---|---|
| Blood | yes | \(D_{\mathrm{IS}}\) |
| Membrane | **no** | \(D_{\mathrm{mem}}=\varepsilon D_{\mathrm{IS}}\) |
| Cell | **no** | \(D_{\mathrm{IS}}\) |
| Dialysate | yes | \(D_{\mathrm{IS}}\) |

**Important change vs the thesis:** there is **no** volumetric reaction \(R(c)\) in the cell.

### 4.3 Why three concentration fields

OAT1 sees **two different concentrations** at the same geometric interface:

- extracellular / membrane-side concentration \(c_{\mathrm{extra}}\) (field `is` in COMSOL)
- intracellular concentration \(c_{\mathrm{cell}}\) (field `isc`)

One continuous concentration cannot represent that jump. The models therefore use:

| Field | Domains | Name in COMSOL |
|---|---|---|
| \(c\) blood+membrane | blood + polymer membrane | `is` (`tds`) |
| \(c\) cell | cell only | `isc` (`tds2`) |
| \(c\) dialysate | dialysate only | `isd` (`tds3`) |

### 4.4 OAT1 surface flux (basolateral)

Reversible Michaelis–Menten at the membrane–cell interface:

\[
J_{\mathrm{OAT1}}
=
V_{\max}^{A}
\left(
\frac{c_{\mathrm{extra}}}{K_m + c_{\mathrm{extra}}}
-
\frac{c_{\mathrm{cell}}}{K_m + c_{\mathrm{cell}}}
\right)
\quad
\bigl[\mathrm{mol\,m^{-2}\,s^{-1}}\bigr]
\]

Positive \(J_{\mathrm{OAT1}}\) means net transport **membrane → cell**.

In COMSOL this is applied as **equal-and-opposite** inward fluxes on the two fields (mass is moved, not created):

- membrane side: \(N_0 = -J_{\mathrm{OAT1}}\)
- cell side: \(N_0 = +J_{\mathrm{OAT1}}\)

### 4.5 Apical efflux (cell → dialysate)

Irreversible exit into toxin-poor dialysate:

\[
J_{\mathrm{ap}}
=
V_{\max}^{\mathrm{ap}}
\frac{c_{\mathrm{cell}}}{K_{m,\mathrm{ap}} + c_{\mathrm{cell}}}
\]

Without apical exit, the cell would fill and net clearance would stall even if OAT1 were fast.

### 4.6 Geometry identities

Cylinder surface area of radius \(R\) and length \(L\):

\[
A = 2\pi R L \tag{1}
\]

Blood volume, lumen:

\[
V_b = \pi R_{\mathrm{lumen}}^{2} L \tag{2}
\]

Blood volume, annular shell:

\[
V_b = \pi\bigl(R_{\mathrm{housing}}^{2} - R_{\mathrm{BM}}^{2}\bigr) L \tag{3}
\]

Fair OI housing so that \(V_b\) matches IO when OAT1 radius (and wall thicknesses) match IO:

\[
R_{\mathrm{housing}}
=
\sqrt{R_{\mathrm{BM}}^{2} + R_{\mathrm{blood,IO}}^{2}} \tag{4}
\]

### 4.7 Membrane permeance and Damköhler number

Effective membrane permeance referred to the OAT1 surface:

\[
P_m
=
\frac{D_{\mathrm{mem}}}{R_{\mathrm{OAT1}}\,\ln(R_{\mathrm{outer,mem}}/R_{\mathrm{inner,mem}})}
\quad
\bigl[\mathrm{m\,s^{-1}}\bigr]
\tag{5}
\]

Damköhler number (transporter capacity vs membrane diffusion of inlet concentration):

\[
Da
=
\frac{V_{\max}^{A}}{P_m\,C_{\mathrm{in}}}
\tag{6}
\]

| \(Da\) | Meaning |
|---|---|
| \(Da \ll 1\) | OAT1-limited: raising \(V_{\max}^{A}\) still raises clearance |
| \(Da \gg 1\) | Membrane-limited: clearance plateaus near \(\sim P_m C_{\mathrm{in}}\) |

### 4.8 Clearance from COMSOL molar flow

Axisymmetric molar flow through an interface (what you export):

\[
\dot n(t)
=
\int J_n\, 2\pi r\,\mathrm{d}\ell
\quad
\bigl[\mathrm{mol\,s^{-1}}\bigr]
\tag{7}
\]

Clearance and area-normalized clearance (**always use \(A_{\mathrm{OAT1}}\)**):

\[
CL = \frac{\dot n}{C_{\mathrm{in}}}
\quad
\bigl[\mathrm{m^{3}\,s^{-1}}\bigr]
\tag{8}
\]

\[
CL'
=
\frac{CL}{A_{\mathrm{OAT1}}}
\quad
\bigl[\mathrm{m\,s^{-1}}\bigr],
\qquad
CL'_{\mu\mathrm{L\,min^{-1}\,cm^{-2}}}
=
CL'\times 6\times 10^{6}
\tag{9}
\]

Time-averaged form (thesis style):

\[
\overline{CL}
=
\frac{1}{t_{\mathrm{end}}\,A\,C_{\mathrm{in}}}
\int_{0}^{t_{\mathrm{end}}}
\dot n(\tau)\,\mathrm{d}\tau
\tag{10}
\]

---

## 5. Parameter tables (with explanations)

### 5.1 Geometry and thickness

| Parameter | Symbol | Value | Why this value |
|---|---|---|---|
| Fiber length | \(L\) | 20 mm | Thesis fiber length |
| Membrane thickness | \(\delta_{\mathrm{mem}}\) | 100 µm | Thesis polymer wall |
| Cell thickness | \(\delta_{\mathrm{cell}}\) | 20 µm | Thesis epithelium |
| IO blood lumen radius | \(R_{\mathrm{blood,IO}}\) | 0.15 mm | Thesis IO |
| IO OAT1 radius | \(R_{\mathrm{OAT1,IO}}\) | 0.25 mm | Membrane–cell in IO |
| IO apical radius | \(R_{\mathrm{AP,IO}}\) | 0.27 mm | Cell–dialysate in IO |
| Thesis housing | \(R_{\mathrm{house,thesis}}\) | 1.80 mm | Original shell outer radius |
| Fair OI housing | \(R_{\mathrm{house,fair}}\) | 0.381 mm | From Eq. (4); matches \(V_b\) |

### 5.2 Transport and kinetics

| Parameter | Symbol | Value | Why this value |
|---|---|---|---|
| Inlet free IS | \(C_{\mathrm{in}}\) | 0.1 mol/m³ = 100 µM | Thesis inlet |
| IS diffusivity (aqueous) | \(D_{\mathrm{IS}}\) | \(5.58\times 10^{-10}\) m²/s | Thesis |
| Membrane porosity | \(\varepsilon\) | 0.45 | Thesis |
| Membrane diffusivity | \(D_{\mathrm{mem}}\) | \(\varepsilon D_{\mathrm{IS}}\) | Effective porous membrane |
| OAT1 half-saturation | \(K_m\) | 20 µM = 0.02 mol/m³ | Thesis OAT1 |
| Apical half-saturation | \(K_{m,\mathrm{ap}}\) | 20 µM | Same default as thesis split-cell; change only if you have data |
| Default OAT1 areal capacity | \(V_{\max}^{A}\) | \(10^{-7}\) mol m⁻² s⁻¹ | First runs: still in the OAT1-sensitive window |
| Apical areal capacity | \(V_{\max}^{\mathrm{ap}}\) | \(10\,V_{\max}^{A}\) | Keeps apical **non-limiting** so you can test OAT1 vs membrane |
| Thesis-equivalent areal capacity | \(V_{\max}^{A,\mathrm{equiv}}\) | \(3.33\times 10^{-4}\) mol m⁻² s⁻¹ | Old volumetric \(10^{6}\) µmol L⁻¹ min⁻¹ × 20 µm; **\(Da\sim 10^{3}\)** |

**How \(V_{\max}^{A,\mathrm{equiv}}\) is obtained**

Thesis volumetric sink:

\[
V_{\max}^{\mathrm{vol}}
=
10^{6}\,\mu\mathrm{mol\,L^{-1}\,min^{-1}}
=
\frac{1000}{60}\,\mathrm{mol\,m^{-3}\,s^{-1}}
\]

Collapse onto the 20 µm cell as an areal density:

\[
V_{\max}^{A,\mathrm{equiv}}
=
V_{\max}^{\mathrm{vol}}\times \delta_{\mathrm{cell}}
\approx
3.33\times 10^{-4}\,\mathrm{mol\,m^{-2}\,s^{-1}}
\]

This is a **conversion for comparison**, not a measured transporter density from a dish.

### 5.3 Flow and fluid properties

| Parameter | Symbol | Value | Why this value |
|---|---|---|---|
| Blood density | \(\rho_b\) | 1050 kg/m³ | Thesis |
| Blood viscosity | \(\mu_b\) | 0.0035 Pa·s | Thesis |
| Dialysate density | \(\rho_d\) | 1000 kg/m³ | Water-like |
| Dialysate viscosity | \(\mu_d\) | \(0.7\times 10^{-3}\) Pa·s | Thesis |
| Blood volumetric flow | \(Q_b\) | 0.100 mL/min | Fixed for **all** geometries (fair throughput) |
| Dialysate volumetric flow | \(Q_d\) | 0.203 mL/min | Fixed for **all** geometries |
| Mean blood speed | \(U_b = Q_b/A_{b,\mathrm{cs}}\) | geometry-dependent | Same \(Q_b\), different cross-section ⇒ different speed |
| Mean dialysate speed | \(U_d = Q_d/A_{d,\mathrm{cs}}\) | geometry-dependent | Same idea |

**Why we match \(Q\), not \(U\):** patients / cartridges deliver volumetric flow. Matching mean speed on a tiny fair-OI shell would force a tiny \(Q_b\) and would not be a fair device comparison.

### 5.4 Simulation controls

| Parameter | Value | Why |
|---|---|---|
| Default `T_end` | 60 min | Fast first comparison |
| Thesis-like `T_end` | 240 min | Match original thesis window |
| Time list | `range(0,5,T_end)` | Enough points for trapezoid average |
| Study 1 | flow stationary → IS transient | Reuse frozen velocity (faster, standard) |
| Study 2 | parametric \(V_{\max}^{A}\) | Bottleneck map |

---

## 6. Geometry tables (IO, original OI, fair OI)

Computed by `python3 src/bak_geometries.py` (also saved in `data/comsol_surface_oat1/geometry_table.csv`).

| Quantity | IO | OI_original | OI_fair |
|---|---:|---:|---:|
| Role | reference | control (unfair) | fair pair to IO |
| Lumen fluid | blood | dialysate | dialysate |
| \(R_{\mathrm{OAT1}}\) (mm) | 0.250 | 0.170 | 0.250 |
| \(R_{\mathrm{AP}}\) (mm) | 0.270 | 0.150 | 0.230 |
| \(R_{\mathrm{BM}}\) (mm) | 0.150 | 0.270 | 0.350 |
| \(R_{\mathrm{housing}}\) (mm) | 1.800 | 1.800 | **0.381** |
| \(A_{\mathrm{OAT1}}\) (mm²) | **31.42** | 21.36 | **31.42** |
| \(V_{\mathrm{blood}}\) (mm³) | **1.414** | 198.99 | **1.414** |
| \(Q_b\) (mL/min) | 0.100 | 0.100 | 0.100 |
| \(Q_d\) (mL/min) | 0.203 | 0.203 | 0.203 |
| \(Da\) at \(V_{\max}^{A,\mathrm{equiv}}\) | \(\sim 1695\) | \(\sim 1044\) | \(\sim 1117\) |

**Read this table like a student examiner would:**

- IO vs **OI_fair**: same \(A_{\mathrm{OAT1}}\) and same \(V_b\) → fair design question.
- IO vs **OI_original**: different area and huge blood volume → useful as a historical control only.
- Even OI_fair does **not** match blood-gap hydrodynamics (thin shell vs lumen). Say that in your report.

---

## 7. Diagnosed issues in the original thesis workflow

These are the problems that motivated the new pipeline.

### 7.1 OAT1 was modeled as a volumetric sink in the whole cell

The thesis used:

\[
R_{\mathrm{uptake}}
=
V_{\max}
\frac{c}{K_m + c}
\]

as a **volume reaction** filling the entire epithelial domain.

**What biology says:** OAT1 is a **membrane transporter** on the basolateral face, not a homogeneous reaction rate in the cytoplasm.

### 7.2 Membrane–cell interface was passive continuity

With one concentration field across membrane and cell, COMSOL enforces continuous \(c\) and continuous normal flux. There is no place to put an OAT1 jump / capacity.

### 7.3 You could not answer “is OAT1 the clearance bottleneck?”

If uptake is smeared through the cell volume and the membrane is only a diffusion resistor in series, raising volumetric \(V_{\max}\) does not isolate the **surface** transporter. The 1D diagnostic later showed that the thesis-equivalent \(V_{\max}^{A}\) sits at \(Da\sim 10^{3}\): **membrane-limited**. The original volumetric parameter was therefore a poor probe of OAT1 limitation.

### 7.4 The “adjusted outside-in” design was not a fair comparison

Adjusted OI matched **blood volume** by thinning the blood shell while the membrane/cell grew toward the 1.8 mm housing. Membrane / OAT1 area became much larger than in IO (\(\sim 198\) mm² class vs \(\sim 31\) mm²). Higher **total** clearance then mostly means “more area”, not “better arrangement”.

### 7.5 Original OI vs IO also mixed several effects

Original OI has a different OAT1 radius (\(0.17\) vs \(0.25\) mm), different \(A_{\mathrm{OAT1}}\), and a much larger blood volume. A single clearance number mixes geometry, area, and hydrodynamics.

### 7.6 Post-processing / data issues (legacy Python + exports)

Known problems in the **old** scripts and COMSOL text dumps (still in `src/` and `data/` for thesis figure reproduction):

| Issue | Effect |
|---|---|
| Scripts assume CWD = `data/<script_name>/` | Running from repo root fails |
| `np.trapz` on NumPy 2 | Breaks on newer Python |
| IO countercurrent radial profiles labeled as 5 min while `t=1` | Wrong time interpretation |
| \(C_{\mathrm{IS}}\) sweep scripts using fixed \(C_{\mathrm{in}}=0.1\) | Inlet and “IS level” confusion |
| Split-cell analysis using one area for all configs | Unfair normalization |
| No `.mph` in the GitHub repo | Models lived on SharePoint; hard to reproduce |

### 7.7 Early 1D surface-OAT1 diagnostic limitations

The quick 1D radial Python chain (`src/oat1_surface_flux_model.py`) is useful for Damköhler intuition, but it:

- fixes blood-side concentration at \(C_{\mathrm{in}}\) (no blood boundary layer, no axial depletion)
- fixes dialysate at 0
- is **IO-only**
- is **not** a substitute for the 2D COMSOL fair comparison

Some saved 1D map rows also contain `nan` / `success=False` where the nonlinear solver did not meet the residual tolerance — do not treat those rows as physical.

---

## 8. Why each diagnosis matters (reasoning)

### 8.1 Why surface fluxes instead of volumetric MM

**Reasoning:** clearance in a BAK is a series of resistances (blood film → membrane diffusion → OAT1 → cell diffusion → apical exit → dialysate film). Putting OAT1 in the **volume** mixes transporter kinetics with intracellular diffusion length. Putting OAT1 on the **surface** lets you assign an areal capacity \(V_{\max}^{A}\) and compare it to membrane capacity \(P_m C_{\mathrm{in}}\) through \(Da\).

**Student analogy:** a toll booth on a highway is not the same as “friction everywhere on the road”. Volumetric MM is friction everywhere; OAT1 is a toll booth.

### 8.2 Why apical efflux must exist

**Reasoning:** if toxin enters the cell through OAT1 but cannot leave, intracellular concentration rises until net OAT1 flux → 0 (for reversible kinetics). Then membrane and blood look “blocked” even though the real missing piece is apical exit. Keeping \(V_{\max}^{\mathrm{ap}} = 10\,V_{\max}^{A}\) makes apical fast on purpose during the OAT1-vs-membrane test.

### 8.3 Why three fields (`is`, `isc`, `isd`)

**Reasoning:** transporters create a **discontinuity of chemical potential / concentration** across a molecular membrane. Continuum FEM with one field forces continuity. Two fields coupled by equal-and-opposite flux is the standard continuum way to represent a surface transporter between compartments.

### 8.4 Why we reject adjusted OI as the fair pair

**Reasoning:** scientific comparison must change **one idea at a time**. “Blood inside vs blood outside” is one idea. “Also give OI six times more membrane area” is a second idea. Adjusted OI changed both. Fair OI keeps wall thicknesses and \(A_{\mathrm{OAT1}}\) and \(V_b\) matched, and only changes which fluid is in the lumen (plus the unavoidable hydrodynamic side effect of a thin shell).

### 8.5 Why report unmatched hydrodynamics honestly

**Reasoning:** matching \(A\) and \(V_b\) does **not** match blood-side mass-transfer coefficient \(k_b\). In OI_fair the blood gap is thin; shear and radial diffusion length differ from the IO lumen. Your report should say: “geometry and throughput matched; blood-side film resistance not matched.”

### 8.6 Why the thesis \(V_{\max}\) looked “inactive”

**Reasoning:** at \(Da\sim 10^{3}\), membrane diffusion already caps the flux near \(P_m C_{\mathrm{in}}\). Raising an already-huge volumetric \(V_{\max}\) barely changes clearance until you enter blood-supply limitation. That matches the thesis finding that MM “did almost nothing” at \(10^{6}\) µmol L⁻¹ min⁻¹ — not because transporters are irrelevant in principle, but because **that parameter set was deep in the membrane-limited regime**.

---

## 9. The new pipeline (step by step)

```text
┌─────────────────────────────────────────────────────────────┐
│ 0. Read this guide + comsol/RUN_ON_UNIVERSITY_COMSOL.md     │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. Get branch from GitHub (Section 12)                      │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Open BAK_IO_OAT1_SurfaceFlux.java in COMSOL 6.3          │
│    Check Box selections. Fix domain IDs if needed.          │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. SIGN CHECK (5–10 min): cell field isc must RISE          │
│    If not, flip both OAT1 N0 signs together.                │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Production run IO (Study 1 or Study 2 Vmax_A sweep)      │
│    Export flux_BM / flux_OAT1 / flux_CD                     │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Repeat steps 2–4 for OI_original and OI_fair             │
│    Same Vmax_A, Q_b, Q_d, C_in, T_end                       │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Copy tables into data/comsol_surface_oat1/<geometry>/    │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. python3 src/comsol_io_oi_comparison.py                   │
│    Compare IO vs OI_fair (primary). OI_original = control.  │
└─────────────────────────────────────────────────────────────┘
```

Optional diagnostic (does **not** replace COMSOL):

```text
python3 src/oat1_surface_flux_model.py
python3 src/paper_figures_oat1.py
```

---

## 10. Rationale behind each pipeline step

| Step | Rationale |
|---|---|
| Start with **IO** | Known thesis geometry; easiest to verify selections and flux signs |
| **Sign check before sweeps** | Wrong normal direction empties the cell; every later number would be garbage |
| Same \(Q_b,Q_d,C_{\mathrm{in}},V_{\max}^{A}\) across models | Isolates arrangement (IO vs OI), not accidental parameter drift |
| Include **OI_original** | Shows what the thesis geometry does under the **new** physics (control) |
| Prefer **OI_fair** for conclusions | Answers “is outside-in better?” without area/volume cheating |
| Export **BM, OAT1, and apical** molar flows | Checks mass routing through the chain; OAT1 alone can hide apical bottlenecks |
| Normalize by **\(A_{\mathrm{OAT1}}\)** | Compares transporter working area, not arbitrary housing size |
| Python after COMSOL | Keeps CFD licensed work on the server; plotting reproducible in Git |
| Keep 1D script optional | Cheap Damköhler intuition before expensive parametric COMSOL sweeps |

---

## 11. Where the codes live

### 11.1 COMSOL (open these on the university server)

| File | Purpose |
|---|---|
| [`comsol/RUN_ON_UNIVERSITY_COMSOL.md`](comsol/RUN_ON_UNIVERSITY_COMSOL.md) | Short run card |
| [`comsol/README.md`](comsol/README.md) | File index |
| [`comsol/BAK_IO_OAT1_SurfaceFlux.java`](comsol/BAK_IO_OAT1_SurfaceFlux.java) | IO model |
| [`comsol/BAK_OI_OAT1_SurfaceFlux.java`](comsol/BAK_OI_OAT1_SurfaceFlux.java) | Original OI control |
| [`comsol/BAK_OI_fair_OAT1_SurfaceFlux.java`](comsol/BAK_OI_fair_OAT1_SurfaceFlux.java) | Fair OI |
| [`comsol/apply_oat1_surface_flux.java`](comsol/apply_oat1_surface_flux.java) | Optional patch for an old `.mph` (prefer the three full models) |

### 11.2 Python (geometry, generation, plotting)

| File | Purpose |
|---|---|
| [`src/bak_geometries.py`](src/bak_geometries.py) | Single source of truth for radii, areas, volumes, equations |
| [`src/write_comsol_java_models.py`](src/write_comsol_java_models.py) | Regenerates the three Java files from `bak_geometries.py` |
| [`src/comsol_io_oi_comparison.py`](src/comsol_io_oi_comparison.py) | Loads COMSOL exports; plots fair comparison |
| [`src/test_bak_geometries.py`](src/test_bak_geometries.py) | Tests: fair OI matches IO area and blood volume |
| [`src/oat1_surface_flux_model.py`](src/oat1_surface_flux_model.py) | Optional 1D Damköhler diagnostic (IO only) |
| [`src/paper_figures_oat1.py`](src/paper_figures_oat1.py) | Journal figures from 1D tables |
| [`src/oat1_data_io.py`](src/oat1_data_io.py) | Save/load helpers for 1D paper tables |
| [`src/oat1_comsol_export_analysis.py`](src/oat1_comsol_export_analysis.py) | Older IO-only export helper |

### 11.3 Data folders

| Path | Contents |
|---|---|
| `data/comsol_surface_oat1/IO/` | **You** put `flux_*.txt` here after COMSOL |
| `data/comsol_surface_oat1/OI_original/` | Same |
| `data/comsol_surface_oat1/OI_fair/` | Same |
| `data/comsol_surface_oat1/geometry_table.csv` | Radii/areas/volumes (no COMSOL needed) |
| `data/oat1_surface_flux/paper/` | Optional 1D diagnostic outputs |
| `data/<old script names>/` | Original thesis COMSOL text dumps (legacy) |

### 11.4 Figures

| Path | Contents |
|---|---|
| `figures/comsol_io_oi/` | Created after a successful `comsol_io_oi_comparison.py` run |
| `figures/paper_oat1/` | 1D diagnostic journal figures |
| `figures/oat1_bottleneck/` | Extra 1D plots |

### 11.5 Legacy thesis reproduction (not the new pipeline)

Scripts such as `src/clearance_analysis.py`, `src/radial_profiles_static.py`, … still reproduce thesis figures from old exports. They use the **old volumetric MM** physics and the **old geometries**. Do not mix those clearance numbers with the new surface-OAT1 fair comparison without saying so.

---

## 12. How to get the codes from GitHub

The new files are on branch **`cursor/oat1-surface-flux-bottleneck-4ac1`**, not necessarily on `main` until the PR is merged.

### 12.1 Clone and checkout (recommended)

```bash
git clone https://github.com/noroozbabaee/Optimizing-the-bioartificial-kidney-design-using-computational-fluid-dynamics.git
cd Optimizing-the-bioartificial-kidney-design-using-computational-fluid-dynamics
git fetch origin
git checkout cursor/oat1-surface-flux-bottleneck-4ac1
```

### 12.2 Already have the repo

```bash
git fetch origin
git checkout cursor/oat1-surface-flux-bottleneck-4ac1
git pull origin cursor/oat1-surface-flux-bottleneck-4ac1
```

### 12.3 Browse in the browser

- PR: https://github.com/noroozbabaee/Optimizing-the-bioartificial-kidney-design-using-computational-fluid-dynamics/pull/1
- `comsol/` folder on the branch:  
  https://github.com/noroozbabaee/Optimizing-the-bioartificial-kidney-design-using-computational-fluid-dynamics/tree/cursor/oat1-surface-flux-bottleneck-4ac1/comsol

You need GitHub access to the **noroozbabaee** repository (owner account or collaborator invite). If you see 404, you are logged out or lack permission.

### 12.4 Copy to the university COMSOL machine

Copy at least the `comsol/` directory (the three `BAK_*.java` files + the run guide). You do **not** need Python on the COMSOL server to Compute; you need Python later on a machine where you plot.

---

## 13. How to run COMSOL on the university server

### 13.1 Open a model

1. Start **COMSOL Multiphysics 6.3**.
2. **File → Open**.
3. Set file type to **Java**.
4. Open `BAK_IO_OAT1_SurfaceFlux.java` first.
5. Wait until geometry builds.

### 13.2 Check selections (mandatory)

In the Model Builder, click each **Box** selection:

- Blood inlet / outlet
- Dialysate inlet / outlet
- Blood–membrane (`bnd_bm`)
- Membrane–cell OAT1 (`bnd_mc`)
- Cell–dialysate apical (`bnd_cd`)

The highlighted edges must match the names. If domain IDs are wrong after Finalize, edit the Explicit selections labeled Blood / Membrane / Cell / Dialysate.

### 13.3 Sign check (mandatory)

1. Study 1 → **Compute** (or compute only the first ~10 min by temporarily lowering `T_end`).
2. Open plot **IS cell (`isc`)**.
3. After a few minutes, `isc` must be **positive and rising**.

| Observation | Action |
|---|---|
| `isc` rises | Signs OK → continue |
| `isc` stays ~0 | OAT1 boundary not connected / wrong selection |
| `isc` falls or goes negative | Flip **both** OAT1 `N0` signs together (`J_OAT1` ↔ `-J_OAT1` on membrane and cell). Keep them equal-and-opposite |

### 13.4 If an API feature is rejected by the university build

- **LaminarInflow** unavailable → Inlet → Velocity → use average `U_avg_b` / `U_avg_d`.
- Dialysate velocity field not `u2` → in dialysate TDS, set convection velocity to **Laminar Flow 2**.

### 13.5 Production settings

Keep identical across the three models:

- `Vmax_A` (start with `1e-7`, also run `Vmax_A_equiv` once)
- `Vmax_ap = 10*Vmax_A`
- `C_in`, `Q_b`, `Q_d`, `T_end`

Then open `BAK_OI_OAT1_SurfaceFlux.java` and `BAK_OI_fair_OAT1_SurfaceFlux.java` and repeat sign check + production run.

### 13.6 Optional: regenerate Java after editing radii

On a laptop with Python (not required for normal use):

```bash
python3 src/bak_geometries.py
python3 src/write_comsol_java_models.py
python3 -m pytest -q src/test_bak_geometries.py
```

Do not hand-edit radii in the three Java files unless you are fixing a COMSOL version quirk; change `src/bak_geometries.py` and regenerate.

---

## 14. How to export results

### 14.1 What to export

Evaluate the three line integrations vs time and export **plain text**:

| Table in COMSOL | Save as |
|---|---|
| Flux BM vs time | `flux_BM.txt` |
| Flux OAT1 vs time | `flux_OAT1.txt` |
| Flux CD vs time | `flux_CD.txt` |

### 14.2 Where to put them

```text
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

### 14.3 File format

```text
% Time (min)    Molar flow (mol/s)
0    0
5    1.2e-12
10   1.1e-12
```

`%` comment lines are allowed. If time is in seconds and the last value is huge (>1000), the Python loader divides by 60 automatically.

### 14.4 Parametric sweep naming (optional)

```text
flux_OAT1_VmaxA_1e-7.txt
flux_BM_VmaxA_1e-7.txt
flux_CD_VmaxA_1e-7.txt
```

---

## 15. How to plot results in Python

### 15.1 Install

From the repository root:

```bash
python3 -m pip install -r requirements.txt
```

### 15.2 Run the comparison

```bash
python3 src/comsol_io_oi_comparison.py
```

**If exports are missing:** the script writes `geometry_table.csv` and prints the exact paths it still needs. It will **not** invent clearance.

**If exports are present:** it writes metrics and figures under `figures/comsol_io_oi/`.

### 15.3 What to report in a student report

1. Endpoint and/or time-averaged \(CL'\) for **IO** and **OI_fair** (µL min⁻¹ cm⁻²), same \(V_{\max}^{A}\).
2. Optionally OI_original as “thesis geometry control”.
3. \(Da\) for that \(V_{\max}^{A}\).
4. Explicit sentence: blood-gap hydrodynamics unmatched.
5. Sign-check confirmation (`isc` rose in all three models).

### 15.4 Optional 1D diagnostic only

```bash
python3 src/oat1_surface_flux_model.py
python3 src/paper_figures_oat1.py
python3 -m pytest -q src/test_oat1_surface_flux.py src/test_bak_geometries.py
```

---

## 16. Damköhler number: how to read “who is limiting”

1. Compute \(P_m\) from Eq. (5) (or read `P_m_m_s` in `geometry_table.csv`).
2. Compute \(Da = V_{\max}^{A}/(P_m C_{\mathrm{in}})\).
3. Interpret:

| Regime | What you should see in a \(V_{\max}^{A}\) sweep |
|---|---|
| OAT1-limited (\(Da\ll 1\)) | Clearance rises when \(V_{\max}^{A}\) rises |
| Transition (\(Da\sim 1\)) | Clearance bends toward a plateau |
| Membrane-limited (\(Da\gg 1\)) | Clearance almost flat; thesis-equivalent \(V_{\max}^{A}\) lives here |

**Design implication:**

- If your operating point is membrane-limited, buying “more OAT1 expression” will not help until the membrane permeance improves (thinner / higher \(\varepsilon\) / higher \(D\)).
- If your operating point is OAT1-limited, geometry still matters, but transporter density is a lever.

---

## 17. Checklist before you trust a number

- [ ] Correct branch checked out (`cursor/oat1-surface-flux-bottleneck-4ac1` or merged `main`)
- [ ] Opened the intended Java file (IO / OI_original / OI_fair)
- [ ] Box selections highlight the correct edges
- [ ] `isc` rises after a few minutes
- [ ] `Vmax_ap = 10*Vmax_A` (unless you are studying apical limitation on purpose)
- [ ] Same \(Q_b\), \(Q_d\), \(C_{\mathrm{in}}\), \(T_{\mathrm{end}}\) in all three models
- [ ] Exported BM, OAT1, and CD molar flows
- [ ] Files sit in the correct `data/comsol_surface_oat1/<geometry>/` folder
- [ ] Clearance normalized by **\(A_{\mathrm{OAT1}}\)** of that geometry
- [ ] Primary conclusion uses **IO vs OI_fair**, not adjusted OI
- [ ] Report states unmatched blood-side hydrodynamics

---

## 18. FAQ

### Do I need to merge the PR before running?

No. Checkout the feature branch. Merging to `main` only makes the default GitHub view show the files.

### Can Python create the COMSOL results for me?

No. Python plots **exports**. Without `flux_*.txt` from COMSOL, there is no fair IO/OI clearance plot.

### Which model answers “is outside-in better?”

**IO vs OI_fair.** OI_original is a control. Adjusted OI from the thesis is not used.

### Why is fair housing only 0.381 mm?

Because Eq. (4) forces that radius once you keep OAT1 at 0.25 mm and match IO blood volume. A 1.8 mm housing with that OAT1 radius would recreate a huge blood volume (unfair).

### Are the parameters “100% experimentally correct”?

They are the **thesis baseline**, chosen for continuity with the existing work. If you have better measured \(V_{\max}^{A}\), \(K_m\), or \(D_{\mathrm{mem}}\), change Parameters in COMSOL **identically** in all three models and document the source.

### Who built the `.mph` binary?

Nobody in this cloud environment (no COMSOL license here). Opening the `.java` file on the university license builds the model; **Save As** creates `.mph`.

---

## Document control

| Item | Value |
|---|---|
| Guide file | `SURFACE_OAT1_PIPELINE_README.md` (repository root) |
| Related short run card | `comsol/RUN_ON_UNIVERSITY_COMSOL.md` |
| Geometry source | `src/bak_geometries.py` |
| Intended users | Bachelor/master students running university COMSOL + local Python |

If something in COMSOL’s Java API differs on your exact 6.3 build, fix the smallest API call (inlet type / velocity field name), keep the physics and geometries above, and note the change in your lab notebook.
