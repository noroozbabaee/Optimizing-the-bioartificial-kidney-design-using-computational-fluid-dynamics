# Building the bioartificial kidney surface-OAT1 model in COMSOL 6.4

### A teaching document: what we built, and why every choice was made

This document reconstructs the complete model from first principles. Every
setting is given together with the reason it was chosen and the alternative
that was rejected. It is written so that someone who has never opened this
model can rebuild it, defend it in a thesis committee, and modify it safely.

---

## Contents

1. [The scientific question](#1-the-scientific-question)
2. [The physical system and the modelling assumptions](#2-the-physical-system-and-the-modelling-assumptions)
3. [Governing equations](#3-governing-equations)
4. [Why three concentration fields instead of one](#4-why-three-concentration-fields-instead-of-one)
5. [Why a surface flux and not volumetric Michaelis-Menten](#5-why-a-surface-flux-and-not-volumetric-michaelis-menten)
6. [Geometry and domain numbering](#6-geometry-and-domain-numbering)
7. [Parameters and where each number comes from](#7-parameters-and-where-each-number-comes-from)
8. [Dimensionless analysis: what actually limits transport](#8-dimensionless-analysis-what-actually-limits-transport)
9. [Step-by-step build in the GUI](#9-step-by-step-build-in-the-gui)
10. [Boundary conditions, with sign conventions](#10-boundary-conditions-with-sign-conventions)
11. [Coupling flow to transport](#11-coupling-flow-to-transport)
12. [Meshing: mapped elements and distributions](#12-meshing-mapped-elements-and-distributions)
13. [Study setup: why flow first, then transport](#13-study-setup-why-flow-first-then-transport)
14. [Verification: the checks that must pass](#14-verification-the-checks-that-must-pass)
15. [Extracting results](#15-extracting-results)
16. [The three geometries and the fairness argument](#16-the-three-geometries-and-the-fairness-argument)
17. [Troubleshooting log](#17-troubleshooting-log)
18. [Glossary](#18-glossary)

---

## 1. The scientific question

A bioartificial kidney (BAK) removes protein-bound uraemic toxins such as
indoxyl sulfate (IS) that ordinary dialysis clears poorly. It combines a
polymer membrane with a layer of living proximal tubule cells. Those cells
carry the **OAT1** transporter on their basolateral side, which actively pulls
IS out of the blood side, and efflux transporters on their apical side, which
push it into the dialysate.

Two questions drive this model:

**Q1. Where is the bottleneck?** Is the limiting step the diffusion of IS
through the polymer membrane, or the capacity of the OAT1 transporter? Design
effort should go to whichever one dominates.

**Q2. Which geometry is better, inside-out or outside-in?** In the inside-out
(IO) arrangement blood flows in the fibre lumen and dialysate in the shell. In
the outside-in (OI) arrangement they are swapped. These must be compared
**fairly**, meaning at equal transporter area, equal blood volume, and equal
flow rates. Otherwise the comparison rewards a design just for being bigger.

---

## 2. The physical system and the modelling assumptions

### The four layers

Going outward from the axis of a single hollow fibre in the IO arrangement:

| Layer | Radial extent | Role |
|---|---|---|
| Blood lumen | 0 to 0.15 mm | carries IS in, flows fast |
| Polymer membrane | 0.15 to 0.25 mm | porous barrier, diffusion only |
| Cell monolayer | 0.25 to 0.27 mm | living cells, contains OAT1 |
| Dialysate shell | 0.27 to 1.80 mm | carries IS away, countercurrent |

### Assumptions and their justification

**Axial symmetry.** A hollow fibre is a cylinder and nothing in the problem
breaks rotational symmetry, so we solve a 2D slice in `(r, z)` instead of a 3D
volume. This reduces the element count by roughly two orders of magnitude and
introduces no error. In COMSOL this is the **2D Axisymmetric** space dimension.

**Single fibre.** A real cartridge holds thousands of fibres. Modelling one
fibre with its share of the shell volume is the standard unit-cell approach.
Whole-device performance is recovered by multiplying by fibre count.

**Newtonian blood.** Blood is shear-thinning, but in a 0.3 mm lumen at these
flow rates the shear rate is high enough that the viscosity is near its
asymptotic value. Using `mu_b = 3.5 mPa*s` is the standard simplification. If a
reviewer objects, a Carreau model can be substituted without changing anything
else in the model.

**Dilute solute.** IS at 100 micromolar does not change the density or
viscosity of the fluid, so flow and transport are one-way coupled: velocity
affects concentration, concentration does not affect velocity. This is what
justifies solving the flow **once**, then the transport, instead of solving
both simultaneously. It saves a large amount of computing time.

**Free IS only.** In plasma, IS is >90% bound to albumin. This model tracks the
free fraction, which is the fraction the transporter actually sees. The bound
pool acts as a reservoir that is not modelled here. That is a deliberate scope
limit and must be stated in the thesis.

**Isothermal.** No heat sources; diffusivities are constants.

**Rigid, non-fouling membrane.** No deformation, no protein cake layer.

---

## 3. Governing equations

### Fluid flow: incompressible Navier-Stokes

In both the blood lumen and the dialysate shell:

```
rho (u . grad) u = -grad p + mu * laplacian(u)
div u = 0
```

Solved as steady state. Justification for steady state: the flow reaches
steady state in milliseconds, while the transport problem evolves over minutes.
There is no reason to resolve the flow start-up transient.

Justification for **laminar**: the Reynolds numbers are about 2 (see
[section 8](#8-dimensionless-analysis-what-actually-limits-transport)), far
below the transition value of roughly 2000. Turbulence models would be wrong
here, and creeping flow (which drops inertia entirely) would also be defensible
but adds an assumption we do not need.

### Solute transport: convection-diffusion

In each fluid or porous domain, for concentration `c`:

```
dc/dt + div( -D grad c + u c ) = R
```

with `R = 0` everywhere in this model. There are **no volumetric reactions**:
all the biology happens on surfaces. That is the central modelling decision,
explained in [section 5](#5-why-a-surface-flux-and-not-volumetric-michaelis-menten).

In the membrane the same equation holds with `u = 0` and an effective
diffusivity reduced by porosity:

```
D_mem = eps_mem * D_is
```

This is the simplest porous correction. A tortuosity factor could be added as
`D_eff = eps/tau * D`; with `tau` unknown for this membrane, folding it into the
single fitted parameter `eps_mem` is honest and keeps the parameter count low.

### Transporter kinetics: Michaelis-Menten as a surface flux

**Basolateral OAT1**, at the membrane-cell interface `r = R_OAT1`, written as a
**reversible** flux:

```
J_OAT1 = Vmax_A * [  c/(Km + c)  -  c2/(Km + c2)  ]        [mol/(m^2 s)]
```

where `c` is the extracellular concentration on the membrane side and `c2` the
intracellular concentration. When the cell is empty the second term vanishes
and the flux is the familiar forward Michaelis-Menten expression. When the cell
fills, the flux falls, and if the cell ever exceeded the outside the flux
reverses. This is essential: a purely forward expression would let the model
pump the cell to unbounded concentration, which is unphysical.

**Apical efflux**, at the cell-dialysate interface `r = R_AP`, written as
**irreversible** because the dialysate is continuously flushed and the efflux
pumps are ATP-driven:

```
J_apical = Vmax_ap * c2/(Km_ap + c2)                        [mol/(m^2 s)]
```

with `Vmax_ap = 10 * Vmax_A`. The factor of ten is deliberate: it makes the
apical step fast enough that it is **not** the bottleneck, so any bottleneck the
model reveals is genuinely at the membrane or at OAT1. If you want to study
apical limitation, lower this factor and re-run; that is a legitimate follow-up
experiment.

### Interface coupling: equal and opposite fluxes

At each of the two interfaces the flux leaving one field must equal the flux
entering the other:

```
at r = R_OAT1:   N_into(blood+membrane) = -J_OAT1     N_into(cell) = +J_OAT1
at r = R_AP:     N_into(cell) = -J_apical             N_into(dialysate) = +J_apical
```

This is a conservation statement, not a modelling choice. If the two signs were
not exactly opposite, the model would create or destroy mass at the interface.
**Checking this pairing is the single most important correctness check in the
whole model.**

---

## 4. Why three concentration fields instead of one

A single Transport of Diluted Species interface spanning all four domains would
force the concentration to be **continuous** at every internal boundary. That is
correct at the blood-membrane interface, where transport is purely passive. It
is **wrong** at the cell membrane, because the whole point of an active
transporter is that it maintains a concentration **jump**: intracellular
concentration can sit above extracellular concentration, which is exactly what
"active transport" means.

So the model uses three separate interfaces on disjoint domains:

| Interface | Domains | Species | Physical meaning |
|---|---|---|---|
| `tds` | blood + membrane | `c` | extracellular, blood side |
| `tds2` | cell | `c2` | intracellular |
| `tds3` | dialysate | `c3` | extracellular, dialysate side |

Because the domains are disjoint, each interface sees the cell membrane as an
**exterior** boundary of its own selection, and a Flux condition can be applied
there. The jump in concentration is then whatever the transporter kinetics
produce, rather than being forced to zero.

Note the deliberate grouping: **blood and membrane share one field**. That is
correct, because at `r = R_BM` there is no transporter, only passive diffusion,
so concentration should be continuous there. Putting them in one interface gets
that continuity automatically with no boundary condition at all.

### The rejected alternative

You could instead use one field everywhere plus a "thin diffusion barrier" or
an assembly with identity pairs. Both are more fragile: the barrier feature
assumes a linear resistance, which cannot represent saturable kinetics, and
identity pairs require non-conforming meshes and pair conditions. The
three-field approach is more transparent and each piece is separately
verifiable.

---

## 5. Why a surface flux and not volumetric Michaelis-Menten

Earlier work modelled OAT1 uptake as a **volumetric** reaction term spread
through the whole 20 micrometre cell layer:

```
R = -Vmax_V * c/(Km + c)          [mol/(m^3 s)]     <-- rejected
```

Three things are wrong with that:

**It is not where the protein is.** OAT1 sits in the basolateral membrane, a
surface. Spreading its capacity through the cell volume is a mathematical
convenience with no anatomical basis.

**It makes the answer depend on an arbitrary thickness.** With a volumetric
term, doubling the assumed cell layer thickness doubles the total uptake
capacity, even though the number of transporter proteins has not changed. The
model then reports a design improvement that is purely an artefact.

**It cannot saturate correctly.** The physically meaningful saturation is per
unit **area** of membrane, because that is what limits the number of transport
cycles per second.

The conversion between the two, for a cell layer of thickness `d_cell`, is:

```
Vmax_A = Vmax_V * d_cell
```

With the thesis value `Vmax_V = 1e6 micromol/(L min)` and `d_cell = 20 um` this
gives `Vmax_A_equiv = 3.33e-4 mol/(m^2 s)`, which is included as a parameter so
the old and new formulations can be compared directly. As
[section 8](#8-dimensionless-analysis-what-actually-limits-transport) shows,
that value is so large that the membrane becomes the sole bottleneck, which is
precisely the finding that motivated this rewrite.

---

## 6. Geometry and domain numbering

Four rectangles are drawn and merged with **Form Union**.

### Why Form Union and not Form Assembly

Form Union merges the rectangles into one geometry with **shared** interior
boundaries and a **conforming** mesh. This gives:

- automatic concentration continuity at `r = R_BM` within `tds`
- real, selectable edges at `r = R_OAT1` and `r = R_AP` for the Flux conditions
- no interpolation error between layers

Form Assembly would keep the objects separate, create identity pairs, and
require pair boundary conditions. It is the right tool when you need a genuine
discontinuity across a boundary, but here the discontinuity is already handled
by using separate physics interfaces, so Form Assembly would add complexity for
no benefit.

### Rectangles (IO geometry)

| Object | Position r | Width | Height | Layer |
|---|---|---|---|---|
| r1 | `0` | `R_BM` | `L` | blood |
| r2 | `R_BM` | `R_OAT1-R_BM` | `L` | membrane |
| r3 | `R_OAT1` | `R_AP-R_OAT1` | `L` | cell |
| r4 | `R_AP` | `R_house-R_AP` | `L` | dialysate |

Widths are written as **expressions**, not numbers. This is what makes the
model parametric: changing `R_OAT1` moves two rectangle edges consistently, and
the geometry can never become self-inconsistent.

After Build All, COMSOL reports **4 domains, 13 boundaries, 10 vertices**. That
count is itself a check: 5 vertical edges plus 4 bottom plus 4 top equals 13.

### Domain numbers

| Domain | Layer |
|---|---|
| 1 | blood |
| 2 | membrane |
| 3 | cell |
| 4 | dialysate |

### Boundary numbers

COMSOL numbers boundaries automatically, sorted by position. For this geometry:

| Boundary | Location | Used for |
|---|---|---|
| 1 | axis, `r = 0` | axial symmetry (automatic) |
| **2** | blood inlet, `z = 0` | velocity inlet, `c = C_in` |
| **3** | blood outlet, `z = L` | pressure outlet, outflow |
| 4 | blood-membrane, `r = R_BM` | nothing: continuity is automatic |
| 5, 6 | membrane ends | no flux (default) |
| **7** | **membrane-cell, `r = R_OAT1`** | **OAT1 flux pair** |
| 8, 9 | cell ends | no flux (default) |
| **10** | **cell-dialysate, `r = R_AP`** | **apical flux pair** |
| **11** | dialysate outlet, `z = 0` | pressure outlet, outflow |
| **12** | dialysate inlet, `z = L` | velocity inlet, `c3 = 0` |
| 13 | housing wall, `r = R_house` | no flux (default) |

Always verify a boundary number visually before relying on it: click it and
confirm the highlighted edge is where you expect.

---

## 7. Parameters and where each number comes from

| Name | Value | Origin and reasoning |
|---|---|---|
| `L` | `20[mm]` | fibre length used in the thesis experiments |
| `R_BM` | `0.15[mm]` | lumen radius of the hollow fibre |
| `R_OAT1` | `0.25[mm]` | membrane is 100 um thick |
| `R_AP` | `0.27[mm]` | cell monolayer is 20 um thick |
| `R_house` | `1.8[mm]` | shell radius, sets dialysate volume |
| `C_in` | `0.1[mol/m^3]` | 100 uM free IS, uraemic range |
| `D_is` | `5.58e-10[m^2/s]` | IS diffusivity in water at 37 C |
| `eps_mem` | `0.45` | membrane porosity |
| `D_mem` | `eps_mem*D_is` | effective diffusivity, `= 2.51e-10 m^2/s` |
| `Q_b` | `1.667e-9[m^3/s]` | 0.10 mL/min, matches thesis blood flow |
| `Q_d` | `3.383e-9[m^3/s]` | 0.20 mL/min dialysate |
| `U_avg_b` | `2.358e-2[m/s]` | `Q_b / (pi R_BM^2)` **for this geometry** |
| `U_avg_d` | `3.400e-4[m/s]` | `Q_d / (pi (R_house^2 - R_AP^2))` |
| `Km_bl` | `0.02[mol/m^3]` | 20 uM, OAT1 affinity for IS |
| `Km_ap` | `0.02[mol/m^3]` | apical transporter affinity |
| `Vmax_A` | `1e-7[mol/(m^2*s)]` | areal OAT1 capacity, first-run value |
| `Vmax_ap` | `10*Vmax_A` | apical deliberately not limiting |

### The key point about flows versus velocities

`Q_b` and `Q_d` are the **physically meaningful** quantities: they are what a
pump delivers, and they are what must be held constant when comparing designs.
The velocities are derived, `U = Q / A`, and therefore **differ between
geometries** because the cross-sections differ.

For IO, the dialysate carries twice the volumetric flow of blood but moves
about 70 times slower, because the shell cross-section is about 140 times the
lumen cross-section. Anyone who instead held the velocities constant would be
silently changing the flow rates and the comparison would be meaningless.

---

## 8. Dimensionless analysis: what actually limits transport

These numbers should be computed **before** trusting any simulation, because
they predict what the answer must look like.

### Reynolds numbers

```
Re_blood     = rho_b * U_avg_b * 2 R_BM / mu_b        = 2.1
Re_dialysate = rho_d * U_avg_d * D_h    / mu_d        = 1.5
```

Both far below transition. Laminar flow is correct, and inertia is nearly
negligible.

### Axial Peclet number

```
Pe = U_avg_b * L / D_is = 8.5e5
```

Axial transport is overwhelmingly convective; axial diffusion is irrelevant.
This is why the axial mesh can be relatively coarse while the radial mesh
cannot.

### Characteristic times

| Process | Expression | Value |
|---|---|---|
| Blood residence | `L / U_avg_b` | 0.85 s |
| Radial diffusion across lumen | `R_BM^2 / D_is` | 40 s |
| Diffusion across membrane | `d_mem^2 / D_mem` | 40 s |
| Diffusion across cell layer | `d_cell^2 / D_is` | 0.72 s |

**Interpretation.** A blood element crosses the whole device in under a second,
but needs 40 seconds to diffuse from the axis to the wall. So the lumen is
strongly **mass-transfer limited**: only the fluid near the wall gets cleaned on
a single pass. This is the classical Graetz problem, and here the Graetz number
is about 190, confirming a thin concentration boundary layer.

The membrane also takes 40 s, so membrane resistance and lumen resistance are
comparable. The cell layer is fast and never limits.

### Damkohler number: transporter versus membrane

Define the ratio of the transporter's maximum capacity to the membrane's
maximum diffusive supply:

```
Da = Vmax_A * d_mem / (D_mem * C_in)
```

| `Vmax_A` | `Da` | Meaning |
|---|---|---|
| `1e-7` (default) | **0.40** | transporter and membrane comparable; **OAT1 matters** |
| `3.33e-4` (thesis-equivalent) | **1330** | membrane completely limiting; **OAT1 is irrelevant** |

This is the model's central quantitative result, and it can be stated before
running anything. With the thesis's original volumetric `Vmax`, no improvement
to the cells could possibly help, because the membrane cannot deliver toxin
fast enough to keep the transporters busy. Only when `Vmax_A` is in the region
of `1e-7` does transporter capacity appear in the answer at all. That is why the
default was set there and why a sweep across `Vmax_A` is the informative
experiment.

### Saturation check

```
C_in / Km = 0.1 / 0.02 = 5
```

The inlet concentration is five times `Km`, so the transporter starts out
partially saturated and moves into the linear regime as concentration falls
along the fibre. Both regimes are therefore visited, which is what makes
Michaelis-Menten worth using instead of a linear rate.

### Sanity bound on total removal

```
Maximum possible transporter flow = Vmax_A * A_OAT1 = 3.1e-12 mol/s
Toxin delivered by blood          = Q_b   * C_in    = 1.7e-10 mol/s
```

The transporter can process at most about 2% of the delivered load at the
default `Vmax_A`. Any simulation reporting more than that has a bug.

---

## 9. Step-by-step build in the GUI

### 9.1 Create the model

`File > New > Model Wizard > 2D Axisymmetric`, add `Laminar Flow (spf)` and
`Transport of Diluted Species (tds)`, choose `Stationary`, click Done.

The concentration dependent variable is left at the default name `c`. Renaming
it is possible but the default names `c`, `c2`, `c3` are what the flux
expressions use, and keeping defaults removes a class of typing errors.

### 9.2 Parameters

Enter the table from [section 7](#7-parameters-and-where-each-number-comes-from)
in `Global Definitions > Parameters 1`. Every row must show a value in the
Value column; red text means a typo or a missing unit.

### 9.3 Geometry

Set `Geometry 1` length unit to **mm**, then add the four rectangles from
[section 6](#6-geometry-and-domain-numbering) and click **Build All**.

### 9.4 Add the remaining physics

`Home > Add Physics`, then add `Laminar Flow` once and
`Transport of Diluted Species` twice, giving `spf2`, `tds2`, `tds3`.

Then set each interface's **Domain Selection** to Manual:

| Interface | Domains |
|---|---|
| `spf` | 1 |
| `tds` | 1, 2 |
| `spf2` | 4 |
| `tds2` | 3 |
| `tds3` | 4 |

**This step is a common source of errors.** If an interface is left on "All
domains", COMSOL will try to solve blood flow inside the cell layer, and the
solver will fail with an undefined-variable error. Always set the domains on
the **interface node**, not on the sub-nodes, which inherit it.

Set **Discretization > Concentration** to **Quadratic** on all three TDS
interfaces. The default Linear elements are too diffusive across a 20 um layer
that is resolved by ten elements; quadratic elements also match the P2
velocity discretization used by Laminar Flow.

On `tds2` (cell), **uncheck Convection** in Transport Mechanisms. There is no
flow in the cell layer, and asking for a velocity field there would reference
variables that do not exist in that domain.

### 9.5 Fluid properties

| Interface | Density | Dynamic viscosity |
|---|---|---|
| `spf` (blood) | `1050[kg/m^3]` | `0.0035[Pa*s]` |
| `spf2` (dialysate) | `1000[kg/m^3]` | `0.0007[Pa*s]` |

Set these as **User defined** rather than "From material". Adding a Materials
node would work too, but entering two numbers directly avoids the
"Undefined material property rho" error entirely.

### 9.6 Diffusion coefficients

| Node | `Dc` | Tensor type |
|---|---|---|
| `tds > Fluid 1` (domains 1, 2) | `D_is` | Isotropic |
| `tds > Fluid 2` (domain 2 only) | `D_mem` | Isotropic |
| `tds2 > Fluid 1` | `D_is` | Isotropic |
| `tds3 > Fluid 1` | `D_is` | Isotropic |

`Fluid 2` is added by right-clicking `tds > Fluid`, then restricting it to
domain 2. Because it appears **after** `Fluid 1` in the node list, it overrides
`Fluid 1` on that domain. This is COMSOL's general rule: later nodes override
earlier ones on overlapping selections. It is how you apply a different
diffusivity in the membrane while keeping one continuous concentration field.

In `Fluid 2` the velocity is set to **User defined, 0, 0**: the polymer has no
bulk flow.

**Isotropic** is correct because diffusion of a small solute in water and in a
non-aligned polymer has no preferred direction. Diagonal, Symmetric, and Full
exist for anisotropic media such as fibre-aligned tissue.

---

## 10. Boundary conditions, with sign conventions

### Flow

| Interface | Node | Boundary | Setting | Why |
|---|---|---|---|---|
| `spf` | Inlet | 2 | Velocity, `U0 = U_avg_b` | fixes `Q_b` |
| `spf` | Outlet | 3 | Pressure `0` | reference; velocity is solved |
| `spf2` | Inlet | 12 | Velocity, `U0 = U_avg_d` | fixes `Q_d`, **top** end |
| `spf2` | Outlet | 11 | Pressure `0` | bottom end |

**Why velocity at one end and pressure at the other.** Specifying velocity at
both ends would over-determine the problem: an incompressible fluid must have
somewhere to go, and the pressure field is what makes that possible. One end
sets the flow rate, the other provides the pressure datum.

**Why the dialysate inlet is at the top.** This makes the flow
**countercurrent**. In co-current flow both streams enter together, the
concentration difference is large at the inlet and collapses as the streams
equilibrate. In countercurrent flow, fresh dialysate meets the most depleted
blood at one end and loaded dialysate meets fresh blood at the other, so the
driving force stays roughly uniform along the whole fibre. Every clinical
dialyser is countercurrent for this reason.

A caveat worth reporting: in this device the bottleneck is the membrane and the
transporter, not the dialysate-side gradient, so countercurrent operation buys
less here than in a conventional dialyser. That is a result, not a reason to
change the design.

**Normal inflow velocity versus fully developed flow.** Normal inflow imposes a
uniform profile whose average is exactly `U_avg`. Fully developed flow would
impose a parabolic profile, which is more realistic, but it adds a solver
constraint and the profile develops within a small fraction of 20 mm anyway.
Since the fair-comparison requirement is on the **flow rate**, uniform inflow is
the cleaner choice.

### Transport

| Interface | Node | Boundary | Setting | Reasoning |
|---|---|---|---|---|
| `tds` | Concentration | 2 | `c = C_in` | blood arrives loaded |
| `tds` | Outflow | 3 | none | solute leaves with the flow |
| `tds` | Flux | **7** | `J0,c = -J_OAT1` | OAT1 removes from blood side |
| `tds2` | Flux | **7** | `J0,c2 = +J_OAT1` | same solute arrives in cell |
| `tds2` | Flux | **10** | `J0,c2 = -J_apical` | efflux removes from cell |
| `tds3` | Flux | **10** | `J0,c3 = +J_apical` | same solute arrives in dialysate |
| `tds3` | Concentration | 12 | `c3 = 0` | fresh dialysate |
| `tds3` | Outflow | 11 | none | solute leaves |

### The sign convention, stated once

COMSOL's Flux feature defines `J0` as flux **into** the domain that the physics
interface occupies. So:

- On boundary 7, `tds` occupies blood plus membrane. Positive `J_OAT1` moves
  solute out of that region, hence `-J_OAT1`.
- On the same boundary, `tds2` occupies the cell. The same positive `J_OAT1`
  moves solute into the cell, hence `+J_OAT1`.

The two must always be a matched pair with opposite signs. **This is the check
to make first if results look wrong.**

**Why Outflow and not "zero concentration" at the outlets.** Outflow imposes
zero **diffusive** flux, letting solute leave purely by convection. Fixing
`c = 0` at an outlet would artificially suck solute out and inflate the apparent
clearance.

**Why no condition at boundary 4.** The blood-membrane interface needs none:
because both sides belong to the same interface `tds`, continuity of
concentration and of flux is automatic. Adding a condition there would be a
mistake.

**Why nothing at boundaries 5, 6, 8, 9, 13.** COMSOL applies No Flux by default
on all exterior boundaries of a transport interface. The membrane and cell end
faces are sealed by potting compound in a real cartridge, and the housing wall
is impermeable, so the default is physically right.

**Initial values** are all zero, representing a clean device at `t = 0`. The
lumen fills within about a second, negligible compared with the 60 minute
simulation.

---

## 11. Coupling flow to transport

Each transport interface must know the velocity field:

| Node | Velocity field |
|---|---|
| `tds > Fluid 1` | `Velocity field (spf)` |
| `tds > Fluid 2` (membrane) | User defined, `0, 0` |
| `tds2 > Fluid 1` (cell) | convection disabled |
| `tds3 > Fluid 1` | `Velocity field (spf2)` |

**The most likely mistake here** is pointing `tds3` at `spf` instead of `spf2`.
The symptom is an error such as:

```
Undefined variable comp1.w ... Domain 4
```

because `w` is `spf`'s axial velocity and `spf` exists only on domain 1.

A `Reacting Flow, Diluted Species` multiphysics coupling would do the same job
and additionally handle mass-transport wall functions for turbulent flow. Since
the flow here is laminar, selecting the velocity field directly is equivalent
and involves fewer moving parts.

---

## 12. Meshing: mapped elements and distributions

Set `Mesh 1` to **User-controlled mesh** and add a **Mapped** node.

### Why mapped and not free triangular

The geometry is four stacked rectangles, so a structured quadrilateral mesh
fits it exactly. Mapped meshing gives:

- elements aligned with the flow and with the concentration gradients, which
  are almost purely radial; aligned elements are far more accurate per degree of
  freedom than triangles cutting across the gradient
- exact control of how many elements sit across each layer
- no sliver elements in the 20 um cell layer, where a free mesher would either
  produce distorted triangles or explode the element count

### Distributions

| Boundary | Elements | Layer resolved | Reasoning |
|---|---|---|---|
| 2 | 20 | blood, 150 um | resolves the concentration boundary layer near the wall |
| 5 | 20 | membrane, 100 um | the profile here is near-linear but drives everything |
| 8 | **10** | cell, **20 um** | the thinnest layer; both fluxes act on its two faces |
| 11 | 30 | dialysate, 1.53 mm | thickest layer, mildest gradients |
| 1 | 80 | axial, 20 mm | axial gradients are gentle; `Pe` is large but the profile is smooth |

Ten elements across 20 micrometres gives 2 um elements. That matters because
the cell layer has a flux entering one face and leaving the other, and an
under-resolved layer would smear the intracellular gradient and misreport `c2`,
which feeds back into both flux expressions.

Mapped meshing forces opposite edges of each rectangle to carry the same number
of divisions, so a single axial distribution on boundary 1 propagates through
all four layers automatically.

**A mesh convergence check belongs in the thesis:** double every distribution,
re-run, and confirm the reported OAT1 molar flow changes by less than a
few percent.

---

## 13. Study setup: why flow first, then transport

| Step | Type | Solves | Disabled |
|---|---|---|---|
| 1 | Stationary | `spf`, `spf2` | `tds`, `tds2`, `tds3` |
| 2 | Time Dependent, `range(0,5,60)` min | `tds`, `tds2`, `tds3` | `spf`, `spf2` |

This split is justified by the dilute-solute assumption: the solute does not
alter the fluid properties, so the velocity field is independent of the
concentration field. Solving them separately is not an approximation, it is an
exact consequence of one-way coupling, and it is much cheaper than solving a
fully coupled nonlinear system at every time step.

Step 2 automatically uses the velocity field stored by Step 1.

Output every 5 minutes for 60 minutes gives 13 output points, enough to show the
approach to steady state. `T_end = 240 min` reproduces the thesis window.

---

## 14. Verification: the checks that must pass

Run these in order. Do not interpret results until all four pass.

### 1. The cell fills

Plot `c2`. It must rise from zero and level off. If it falls or goes negative,
the OAT1 flux pair has the wrong sign: swap `-J_OAT1` and `+J_OAT1` between the
`tds` and `tds2` nodes on boundary 7, keeping them opposite.

### 2. Mass balance closes

Add three Line Integration nodes (see [section 15](#15-extracting-results)) and
check at steady state:

```
molar flow across OAT1  =  molar flow across the apical face
```

If they differ by more than about 1%, either the mesh is too coarse or a flux
pair is not matched.

### 3. Concentrations stay in range

`0 <= c <= C_in` everywhere. Values above `C_in` in the blood or membrane are
impossible and indicate a sign error. `c2` may exceed the local `c`: that is the
active transport doing its job, and it is the reason for using three fields.

### 4. The result respects the analytical bound

Total OAT1 molar flow must not exceed `Vmax_A * A_OAT1 = 3.1e-12 mol/s`
at the default `Vmax_A`, nor the delivered load `Q_b * C_in = 1.7e-10 mol/s`.

---

## 15. Extracting results

Add three **Line Integration** nodes under `Results > Derived Values`, each with
unit `mol/s`:

| Name | Boundary | Expression |
|---|---|---|
| Flux BM | 4 | `2*pi*r*tds.ndflux_c` |
| Flux OAT1 | 7 | `2*pi*r*J_OAT1` |
| Flux CD | 10 | `2*pi*r*J_apical` |

The factor `2*pi*r` converts the axisymmetric line integral into a true surface
integral over the cylinder, giving molar flow in mol/s:

```
n_dot = integral over the interface of J_n * 2 pi r dl        [mol/s]
```

Evaluate over all time steps and export each as plain text to:

```
data/comsol_surface_oat1/IO/flux_BM.txt
data/comsol_surface_oat1/IO/flux_OAT1.txt
data/comsol_surface_oat1/IO/flux_CD.txt
```

and likewise under `OI_original/` and `OI_fair/`. Then run:

```bash
python3 src/comsol_io_oi_comparison.py
```

### From molar flow to clearance

```
CL(t)  = n_dot(t) / C_in                        [m^3/s]
CL'    = CL / A_OAT1,   A_OAT1 = 2 pi R_OAT1 L  [m/s]
```

Clearance is the virtual blood flow completely stripped of toxin. It is
**normalized by the OAT1 area**, not the membrane area, because OAT1 is the
biological working surface. Normalizing by membrane area would flatter any
design that simply used a bigger polymer cylinder, which is exactly the trap
the thesis's "adjusted OI" fell into.

---

## 16. The three geometries and the fairness argument

| Parameter | IO | OI original | OI fair |
|---|---|---|---|
| `R_BM` | `0.15[mm]` | `0.27[mm]` | `0.35[mm]` |
| `R_OAT1` | `0.25[mm]` | `0.17[mm]` | `0.25[mm]` |
| `R_AP` | `0.27[mm]` | `0.15[mm]` | `0.23[mm]` |
| `R_house` | `1.8[mm]` | `1.8[mm]` | **`0.3808[mm]`** |
| `U_avg_b` | `2.358e-2` | `1.675e-4` | `2.358e-2` |
| `U_avg_d` | `3.400e-4` | `4.786e-2` | `2.036e-2` |

In the OI models the layer order **reverses**: dialysate occupies the lumen and
blood the shell. The rectangles must therefore be drawn in the order dialysate,
cell, membrane, blood, and the interface domain assignments swapped
accordingly. The boundary numbering stays structurally the same but the physical
meaning of each number changes, so re-verify by clicking.

### Why `R_house = 0.3808 mm` for the fair comparison

The fair OI geometry is constructed to match IO on the two quantities that
actually determine performance:

- the same OAT1 area, `A_OAT1 = 2 pi R_OAT1 L = 31.42 mm^2`
- the same blood volume, `V_blood = 1.414 mm^3`

Holding `R_OAT1` fixed fixes the area. The blood is then an annulus in the
shell, and requiring its volume to equal the IO lumen volume determines the
housing radius uniquely as 0.3808 mm.

The thesis's "adjusted OI" instead kept the 1.8 mm housing and matched blood
volume by inflating the membrane. That changes the membrane area and thickness
at the same time as the arrangement, so any difference in performance cannot be
attributed to the arrangement. It answers a different question than the one
being asked.

**What the fair comparison still does not match**, and must be stated as a
limitation: the blood-side hydrodynamics. IO blood flows in a 0.15 mm cylinder;
fair OI blood flows in a thin annular gap. The wall shear rate and the
concentration boundary layer thickness therefore differ, even though flow rate,
transporter area and blood volume are identical. Matching all of them
simultaneously is geometrically impossible, so the honest approach is to match
the quantities that determine transporter supply and report the remainder.

---

## 17. Troubleshooting log

Errors actually encountered while building this model, with causes.

| Message | Cause | Fix |
|---|---|---|
| `Undefined material property 'rho'` | Fluid Properties set to "From material" but no material exists | set density and viscosity to User defined |
| `Undefined variable comp1.w ... Domain 4` | `tds3` velocity field pointed at `spf` instead of `spf2` | select `Velocity field (spf2)` |
| Fluid Properties shows two domains and cannot be edited | the sub-node inherits from the interface; the **interface** selection was wrong | edit Domain Selection on the interface node |
| `c2` stays exactly zero | the OAT1 Flux pair is on the wrong boundary | verify boundary 7 highlights the membrane-cell edge |
| `c2` grows without bound | forward-only Michaelis-Menten was used | use the reversible form with the `-c2/(Km+c2)` term |
| Solver very slow or non-convergent | Linear concentration elements on a 20 um layer | use Quadratic discretization and at least 10 elements across the cell |

### A note on the Model Java route

An earlier attempt generated this model as a COMSOL Model Java file. On this
COMSOL 6.4 installation it failed repeatedly at File > Open with
"Unknown parameter" or "Unknown feature ID" for `D_c`, `Dc`, `c0`, `N0`, `is`,
`ConvectionDiffusion`, `entitydim` on Explicit selections, and
`ReactingFlowDilutedSpecies`. Property and feature identifiers in the Java API
vary between versions and license configurations, and there is no way to
discover the correct ones without the software in front of you.

**The lesson is general and worth stating in the thesis methods section:** build
the model in the GUI, which can only ever offer settings the installation
actually supports, and then export Model Java from the finished model if a
scripted version is needed. Going in the other direction is guesswork.

---

## 18. Glossary

**BAK** - bioartificial kidney: polymer membrane plus living proximal tubule
cells.

**IS** - indoxyl sulfate: a protein-bound uraemic toxin poorly cleared by
conventional dialysis.

**OAT1** - organic anion transporter 1: basolateral membrane protein that
actively takes IS into the cell.

**Basolateral / apical** - the blood-facing and dialysate-facing sides of the
epithelial cell layer.

**IO / OI** - inside-out (blood in the lumen) and outside-in (blood in the
shell).

**Michaelis-Menten kinetics** - saturable rate law `V = Vmax c/(Km + c)`. `Km` is
the concentration at half-maximal rate; `Vmax` the maximum rate.

**Clearance** - the virtual volumetric flow of blood completely cleared of a
solute per unit time, `CL = n_dot / C_in`.

**Reynolds number** - ratio of inertial to viscous forces; below about 2000 the
flow is laminar.

**Peclet number** - ratio of convective to diffusive transport.

**Damkohler number** - here, ratio of transporter capacity to membrane
diffusive supply. `Da >> 1` means the membrane limits; `Da ~ 1` means the
transporter matters.

**Graetz problem** - developing concentration boundary layer in laminar duct
flow; the reason the lumen is mass-transfer limited.
