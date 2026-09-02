# Study design for publication

### Bioartificial kidney: where is the bottleneck, and does fibre orientation matter?

This document turns the working COMSOL model into a publishable study. It
defines the scientific claims, the simulation experiments that support each
claim, the model extensions needed for credibility, the verification and
validation plan, and a figure-by-figure specification.

---

## 1. The gap this paper fills

Existing computational work on bioartificial kidneys (BAKs) has two recurring
weaknesses:

**Weakness 1 - the transporter is modelled in the wrong place.** OAT1 uptake is
usually written as a volumetric Michaelis-Menten sink distributed through the
cell layer, `R = -Vmax_V c/(Km+c)` in mol/(m^3 s). OAT1 is a membrane protein.
A volumetric formulation makes total uptake capacity proportional to an assumed
cell-layer thickness, so a modeller can double the predicted performance by
drawing a thicker layer without adding a single transporter molecule. Published
`Vmax_V` values are also usually so large that the model is silently operating
in a regime where the transporter is irrelevant, which means the paper cannot
say anything about the biology it claims to be studying.

**Weakness 2 - geometry comparisons are confounded.** Inside-out (IO) and
outside-in (OI) fibre arrangements are compared without holding constant the
quantities that determine performance. Matching blood volume by inflating the
membrane, as previous work has done, changes membrane area and thickness at the
same time as the arrangement, so the resulting difference cannot be attributed
to orientation.

**What this paper does.** It reformulates the transporter as an areal flux on
the actual cell membrane surface, shows quantitatively that the conventional
volumetric parameterisation places the device in a membrane-limited regime where
transporter engineering cannot help, constructs a genuinely matched IO/OI
comparison, and delivers a resistance-partitioning design map that tells
experimentalists which component to improve.

### Claims to defend

**C1.** Representing OAT1 as an areal flux removes an artefactual dependence of
predicted clearance on the assumed cell-layer thickness.

**C2.** With literature-scale transporter capacity, the polymer membrane
contributes about 80% of the total mass-transfer resistance, so the device is
membrane-limited and transporter over-expression yields negligible gain.

**C3.** There is a crossover capacity, near `Vmax_A ~ 3e-7 mol m^-2 s^-1`, below
which the transporter dominates and above which the membrane dominates. This
threshold, not an absolute clearance number, is the transferable design result.

**C4.** When OAT1 area, blood volume and both flow rates are matched, the
IO/OI performance difference is far smaller than the unmatched comparison
suggests; most of the apparent advantage in previous work is a size effect.

**C5.** An improved fibre, designed from the resistance map and simulated with
the **same surface-flux model**, raises clearance by pulling the lever that
actually dominates at the working `Vmax_A` — not by returning to volumetric
kinetics or to the unmatched 1.8 mm housing.

The production model for every result except S1 is the corrected formulation.
S1 is a contrast experiment only. The improved design is a **consequence** of
the map, not a second physics.

---

## 2. Target journals

| Journal | Fit | Angle to emphasise |
|---|---|---|
| *Journal of Membrane Science* | strong | membrane resistance dominates; design map |
| *Biotechnology and Bioengineering* | strong | transporter kinetics, cell-layer modelling |
| *Acta Biomaterialia* | good | bioartificial organ design |
| *Computers in Biology and Medicine* | good | methodological correction to a modelling practice |
| *Artificial Organs* / *ASAIO Journal* | good | device-oriented, clinical framing |
| *International Journal for Numerical Methods in Biomedical Engineering* | fallback | verification-heavy, methods-first |

The methodological correction (C1, C2) is the most defensible novelty. Lead
with it. A geometry comparison alone (C4) is a weaker paper.

---

## 3. Research questions and hypotheses

| # | Question | Hypothesis | Tested by |
|---|---|---|---|
| RQ1 | Does the volumetric formulation bias predictions? | Predicted clearance scales with assumed cell thickness under the volumetric form but is invariant under the areal form | S1 |
| RQ2 | What limits solute removal? | Membrane resistance dominates at literature `Vmax`; transporter dominates only below a threshold | S2, S3 |
| RQ3 | Is there a transporter capacity worth engineering toward? | A crossover `Vmax_A` exists; beyond it returns are negligible | S3 |
| RQ4 | Does IO vs OI matter once matched? | Difference shrinks substantially under matched conditions | S4 |
| RQ5 | Which operating parameter is worth optimising? | Blood flow and membrane properties outrank dialysate flow | S5 |
| RQ6 | What device size reaches a clinically relevant clearance? | Fibre count scales linearly with the per-fibre ceiling | S7 |
| RQ7 | Can the map be used to design a better fibre? | Changing the dominant resistance raises clearance; changing a non-dominant one does not | S8 |

---

## 4. Simulation experiment matrix

Each row is a set of runs producing one specific figure panel.

### S1 - Formulation artefact (supports C1)

Vary the assumed cell-layer thickness `d_cell` over 5, 10, 20, 30, 50 um, twice:

- **volumetric**: fixed `Vmax_V`, so total capacity scales with thickness
- **areal**: fixed `Vmax_A`, capacity independent of thickness

Prediction: volumetric clearance rises roughly linearly with `d_cell`; areal
clearance is nearly flat (only the small intracellular diffusion resistance
changes). This is the cleanest possible demonstration of the artefact.

### S2 - Resistance partitioning (supports C2)

Base-case IO run. Extract from the converged solution:

- concentration drop across each layer
- molar flow at each interface
- resistance of each stage, `R_i = Delta c_i / n_dot`

Compare against the analytical series estimate in
[section 9](#9-expected-headline-numbers).

### S3 - Transporter capacity sweep (supports C2, C3)

`Vmax_A` over seven decades: `1e-9, 1e-8, 1e-7, 3e-7, 1e-6, 1e-5, 1e-4,
3.33e-4` mol m^-2 s^-1, IO geometry, all else fixed. Report clearance and the
resistance partition at each value. Mark the literature-equivalent value.

Run as a COMSOL **Parametric Sweep** on the transient study.

### S4 - Matched geometry comparison (supports C4)

Three geometries at identical `Q_b`, `Q_d`, `C_in`, `Vmax_A`, wall thicknesses:

| Case | Purpose |
|---|---|
| IO | reference |
| OI matched (`R_house = 0.3808 mm`) | the fair comparison |
| OI unmatched (`R_house = 1.8 mm`) | reproduces the confounded literature comparison |

Report both absolute clearance and clearance normalised by OAT1 area. The gap
between the matched and unmatched OI results **is** the size-effect artefact,
and quantifying it is a result in its own right.

### S5 - Operating-parameter sensitivity (supports RQ5)

One-at-a-time sweeps around the base case, each over a plausible experimental
range:

| Parameter | Range | Rationale |
|---|---|---|
| `Q_b` | 0.025 - 0.4 mL/min | thins the blood boundary layer |
| `Q_d` | 0.05 - 0.8 mL/min | expected to be nearly inert here |
| `d_mem` | 25 - 200 um | direct membrane resistance |
| `eps_mem` | 0.2 - 0.7 | direct membrane resistance |
| `C_in` | 10 - 300 uM | moves across `Km`, saturation behaviour |
| `Km` | 5 - 100 uM | transporter affinity uncertainty |

Present as normalised sensitivity coefficients,
`S = (dCL/CL)/(dp/p)`, in a tornado plot. This is more informative than raw
curves and is standard practice for reviewers.

### S6 - Flow configuration

Countercurrent vs co-current dialysate, at base case and at high `Vmax_A`.
Expected finding: a small difference, because the dialysate side carries almost
no resistance in this design. Reporting a *negative* result here is valuable and
pre-empts an obvious reviewer question.

### S7 - Device-scale projection

Convert per-fibre clearance to cartridge clearance for realistic fibre counts
and packing densities. State explicitly the assumption of identical, uniformly
perfused fibres, and note flow maldistribution as a limitation.

### S8 - Improved fibre from the map (supports C5)

Do **not** re-optimise the old volumetric model and then re-label it. Do **not**
treat unmatched OI (`R_house = 1.8 mm`) as an improved design: that is more
area, not a better arrangement.

Keep the surface-flux, three-field physics fixed. Propose **one** improved IO
fibre (and, if S4 is done, the same changes on matched OI) using only the
levers the map says to pull at the working point `Vmax_A = 1e-7`:

| Variant | What changes | Why |
|---|---|---|
| Baseline | working IO (and matched OI) | reference |
| Biology lever | raise `Vmax_A` to the crossover `~3e-7` | OAT1 is ~66% of resistance there |
| Membrane lever | thinner or more permeable membrane (e.g. `d_mem` halved **or** `D_mem` doubled), `Vmax_A` held at baseline | shows the *wrong* lever at this operating point: little gain |
| Combined (the “improved” candidate) | crossover `Vmax_A` **and** a manufacturable membrane step (thinner wall or higher `eps_mem`) | demonstrates stacked, map-guided improvement |
| Negative control | raise `Q_d` only | expected near-zero gain; proves the map is not just “change everything” |

Report absolute clearance, area-normalised clearance, and the resistance
partition before/after. The story is: **the formulation tells you where to
invest; the improved fibre is that investment, simulated with the same
equations.**

If a true shape optimisation is wanted later (housing radius, cell thickness,
packing), it belongs after S8, with explicit manufacturing constraints, still
on the surface-flux model. Do not open a COMSOL Optimization study until S2–S3
exist; otherwise the optimiser will chase mesh and parameter artefacts.

---

## 5. Model extensions needed before submission

The working model is the **surface-flux, three-field** description in the
teaching guide (no volumetric sink). Three additions strengthen the paper
without changing that formulation.

### E1 - Protein binding (high priority)

Indoxyl sulfate is more than 90% albumin-bound. Only the free fraction is
available to OAT1. Currently the model tracks free IS only and the inlet
concentration is a free concentration. A reviewer will raise this immediately.

Minimum viable treatment: assume instantaneous binding equilibrium and solve
for total IS with a free fraction

```
c_free = f_u * c_total,    f_u = 1 / (1 + n K_a [Alb])
```

so the effective diffusivity and the transporter driving force both use
`c_free`. This adds one algebraic relation, no new PDE. It also lets you make a
clinically framed statement: with `f_u ~ 0.05`, the delivered free load is
twenty-fold lower than total plasma concentration would suggest.

A more advanced version treats bound and free as two species with a finite
association rate; only do this if you can defend the rate constants.

### E2 - Intracellular transport realism (medium priority)

Currently the cell layer uses aqueous diffusivity. Cytoplasm is more crowded;
an effective diffusivity of roughly one third of aqueous is commonly used.
Because the cell contributes only about 2% of total resistance, this will not
change conclusions, which is precisely why it is worth showing as a sensitivity
case: it demonstrates robustness cheaply.

### E3 - Validation against experiment (high priority)

The paper needs at least one comparison against measured data. Options, in
descending order of strength:

1. In-house transwell or fibre clearance measurements, if available
2. Published BAK IS clearance data digitised from the literature
3. A membrane-only control: run the model with the cell layer disabled and
   compare against measured pure-diffusive permeability of the same membrane

Option 3 is the most achievable and still valuable: it validates the membrane
sub-model independently, which is the component the paper claims dominates.

### E4 - Optional extensions (mention as future work, do not implement)

Ultrafiltration and convective transport, non-Newtonian blood rheology,
fouling layer growth, transporter down-regulation over time, and multi-solute
competition at OAT1.

---

## 6. Verification and validation plan

Reviewers of computational papers reject on verification gaps more often than
on physics. Include all of the following, most of it in supplementary material.

| Check | Method | Acceptance |
|---|---|---|
| Mesh convergence | halve and double all mesh distributions | OAT1 molar flow changes < 2% |
| Time-step independence | tighten solver tolerance by 10x | outputs change < 1% |
| Mass balance | compare molar flow at OAT1 and apical interfaces at steady state | agreement < 1% |
| Analytical limit | disable the transporter, compare with the exact cylindrical diffusion solution | < 2% |
| Sign and physicality | `0 <= c <= C_in`; `c2` rises from zero | must hold |
| Capacity bound | total flow below `Vmax_A * A_OAT1` and below `Q_b C_in` | must hold |
| Series-resistance cross-check | numerical resistance partition vs analytical estimate | same ordering, within ~20% |

Report the mesh study as a table with degrees of freedom and the converged
quantity, not as prose.

---

## 7. Figure plan

Seven main figures. Each has one job; if a panel does not support a claim, move
it to supplementary.

### Figure 1 - Concept and model definition
Two panels. **(a)** Schematic of the BAK fibre showing the four layers, the
blood and dialysate flow directions, and the two transporter locations, with
the flux expressions written on the interfaces where they act. **(b)** The
computational domain: axisymmetric slice with domain numbering, boundary
conditions labelled, and the mesh inset showing refinement across the cell
layer. *Job: makes the three-field formulation and the surface-flux placement
immediately legible.*

### Figure 2 - The formulation artefact (claim C1)
Clearance versus assumed cell-layer thickness, two curves: volumetric `Vmax_V`
(rises roughly linearly) and areal `Vmax_A` (flat). Log-linear axes. Annotate
the thickness used in previous work. *Job: shows in one glance that the old
formulation lets an arbitrary geometric choice set the answer.*

### Figure 3 - Base-case fields
Three panels. **(a)** Concentration surface plot at steady state across all four
layers, log colour scale so the blood, membrane and cell values are all visible.
**(b)** Radial concentration profile at mid-length, with the jump at the cell
membrane marked and the layer boundaries shaded. **(c)** Axial profiles of the
local OAT1 flux and the cup-mixing blood concentration. *Job: shows the physics
is behaving, and the radial profile makes the transporter-driven concentration
jump visually obvious.*

### Figure 4 - Resistance partitioning (claim C2) - the key figure
Stacked bar or stacked area of the percentage of total mass-transfer resistance
contributed by blood boundary layer, membrane, cell diffusion, OAT1 and apical
efflux, plotted against `Vmax_A` across seven decades. Overlay total clearance
on a secondary axis. Mark the literature-equivalent `Vmax_A` with a vertical
line. *Job: this single figure carries claims C2 and C3 and is the figure people
will cite and reproduce.*

### Figure 5 - Design map (claim C3)
Contour plot of clearance over the plane of transporter capacity `Vmax_A`
(vertical) against membrane permeance `D_mem/d_mem` (horizontal), both
logarithmic, with iso-clearance contours, the `Da = 1` diagonal marked, the
current device plotted as a point, and shaded regions labelled
*transporter-limited* and *membrane-limited*. *Job: converts the results into
actionable design guidance and is what makes the paper useful to
experimentalists rather than only descriptive.*

### Figure 6 - Matched versus unmatched geometry comparison (claim C4)
Grouped bars for IO, matched OI, unmatched OI, showing area-normalised
clearance, with the OAT1 area and blood volume annotated under each bar so the
reader can see which quantities were held constant. Add a second panel with the
transient clearance curves. *Job: quantifies how much of the reported OI
advantage is a size effect.*

### Figure 7 - Parameter sensitivity and device projection
**(a)** Tornado plot of normalised sensitivity coefficients from S5.
**(b)** Cartridge clearance versus fibre count, with the per-fibre membrane-limited
ceiling as a horizontal asymptote and a clinically motivated target line.
*Job: tells the reader what to change and how big the device must be.*

### Figure 8 - Map-guided improved fibre (claim C5)
Before/after resistance bars and clearance for baseline, biology lever,
membrane lever, combined candidate, and `Q_d` negative control. Optional second
panel: the same candidate on matched OI. *Job: shows that the corrected model
is used for design, not only for criticising the old formulation.*

### Supplementary figures

- S1 mesh convergence table and plot
- S2 analytical validation, transporter disabled
- S3 mass-balance closure over time
- S4 co-current versus countercurrent
- S5 velocity and pressure fields, wall shear rate for IO and matched OI
- S6 `Km` and `C_in` sweeps, saturation behaviour
- S7 sensitivity to intracellular diffusivity

---

## 8. Analysis methods to write up

### Resistance-in-series decomposition

Treat the steady-state pathway as resistances in series, per unit OAT1 area:

```
1/K_total = R_blood + R_membrane + R_cell + R_OAT1 + R_apical
```

with

```
R_blood    = 1/k_b,          k_b from the Leveque solution, Sh = 1.62 Gz^(1/3)
R_membrane = d_mem / D_mem
R_cell     = d_cell / D_is
R_OAT1     = (Km + c)/Vmax_A          linearised about the local concentration
R_apical   = (Km_ap + c2)/Vmax_ap
```

The dialysate side does **not** appear, because the apical flux as formulated is
irreversible and does not depend on `c3`. State that explicitly; it is the
reason `Q_d` has so little influence, and a reviewer will otherwise assume an
omission.

This analytical backbone should be presented alongside the CFD, not instead of
it. Agreement between the two is itself a verification result, and the analytic
form is what makes the conclusions transferable to devices with different
dimensions.

### Dimensionless groups to report

| Group | Definition | Value (IO base case) | Meaning |
|---|---|---|---|
| `Re` blood | `rho u d/mu` | 2.1 | laminar |
| `Pe` axial | `u L/D` | 8.5e5 | convection dominates axially |
| `Gz` | `d^2 u/(D L)` | 190 | thin concentration boundary layer |
| `Da` | `Vmax_A d_mem/(D_mem C_in)` | 0.40 (default) / 1330 (literature) | transporter vs membrane |
| `C_in/Km` | - | 5 | partially saturated at inlet |

Presenting results against `Da` rather than against `Vmax_A` alone is what makes
the paper generalisable to other membranes and other transporters.

---

## 9. Expected headline numbers

From the analytical series decomposition for the IO base case. These are
predictions to be confirmed by the CFD; large disagreement means a bug.

### Resistance partition

| `Vmax_A` [mol m^-2 s^-1] | blood | membrane | cell | OAT1 | apical |
|---|---|---|---|---|---|
| `1e-9` | 0.0% | 0.3% | 0.0% | **90.6%** | 9.1% |
| `1e-7` (default) | 3.2% | 22.0% | 2.0% | **66.2%** | 6.6% |
| `1e-5` | 11.4% | **78.9%** | 7.1% | 2.4% | 0.2% |
| `3.33e-4` (literature-equivalent) | 11.7% | **80.9%** | 7.3% | 0.1% | 0.0% |

### Derived design statements

- **Crossover:** membrane and OAT1 resistances are equal at
  `Vmax_A ~ 3.0e-7 mol m^-2 s^-1`. Below this, transporter engineering pays;
  above it, membrane engineering pays.
- **Hard ceiling:** with the transporter infinitely fast, per-fibre clearance
  saturates at about `3.8e-3 mL/min`, i.e. about 3.8% single-pass extraction of
  the blood flow. No amount of cell engineering exceeds this while the membrane
  is unchanged.
- **Consequence for previous work:** at literature-scale `Vmax`, OAT1 carries
  0.1% of the resistance. A model in that regime cannot detect any effect of
  transporter expression, which is why such models report membrane-controlled
  behaviour regardless of the biology they assume.
- **Device scale:** reaching 1 mL/min of IS clearance requires of order 260
  fibres at the ceiling, or about 1000 fibres at the default transporter
  capacity, before accounting for flow maldistribution.

---

## 10. Paper outline

The paper describes the **model you actually built**: four domains, three
concentration fields, **surface OAT1 and surface apical fluxes**, no volumetric
sink in the cell, stationary flow, transient transport, countercurrent
dialysate, matched IO/OI. The volumetric Michaelis-Menten form is **not** the
model. It appears only as a literature contrast (S1) so readers can see why
prior parameterisations were biased.

**Title options** (do not lead with "membrane always limits" — that is true only
at literature-scale `Vmax`, not at the working `Vmax_A`)

1. *Surface-flux OAT1 modelling identifies a transporter-to-membrane crossover
   in bioartificial kidney fibres*
2. *Where to put the transporter: areal OAT1 kinetics and matched fibre
   geometries for indoxyl sulfate clearance*
3. *A three-field surface-transport model of the bioartificial kidney:
   formulation artefact, bottleneck map, and fair IO/OI comparison*

Option 1 states the actual claim. Drop any title that treats membrane limitation
as the sole result.

**Structure — what each section is about**

1. **Introduction**
   Protein-bound uraemic toxins and the BAK fibre. Two weaknesses in prior
   CFD: (i) OAT1 written as a volumetric cell sink `R = -Vmax_V c/(Km+c)`,
   which makes capacity scale with an assumed thickness; (ii) IO vs OI compared
   at unmatched OAT1 area and blood volume. Contribution: a surface-flux,
   three-field model and a matched geometric comparison.

2. **Methods — the working model, not the volumetric one**
   - **Geometry.** Axisymmetric IO: blood | membrane | cell | dialysate.
     Matched OI: same OAT1 area, same blood volume, same `Q_b` and `Q_d`
     (housing ~0.381 mm, not the unmatched 1.8 mm).
   - **Flow.** Laminar NS in blood (`spf`) and dialysate (`spf2`) only.
     Membrane and cell are stagnant. Stationary solve. Inlet mean velocities
     from matched flow rates; outlets `p = 0`. No-slip elsewhere, including
     axis.
   - **Transport — three fields.** `c` in blood+membrane; `c2` in cell; `c3`
     in dialysate. Convection only where there is flow (`spf` for `c` in
     blood, `spf2` for `c3`). Membrane: `u = 0`, `D = D_mem`. Cell: no
     convection, `D = D_is`. **No volumetric reaction in any domain.**
   - **Surface fluxes (the biology).** At the membrane–cell interface:
     reversible OAT1, `J_OAT1 = Vmax_A (c/(Km+c) - c2/(Km+c2))`, equal and
     opposite on `tds` and `tds2`. At the cell–dialysate interface:
     irreversible apical, `J_apical = Vmax_ap c2/(Km_ap+c2)` with
     `Vmax_ap = 10 Vmax_A`, equal and opposite on `tds2` and `tds3`.
     Blood–membrane interface: continuity, no Flux node.
   - **Study.** Stationary flow, then transient transport to 60 min.
   - **Literature contrast only (S1, not the model).** Repeat one sweep with
     a volumetric sink `R = -Vmax_V c2/(Km+c2)` inside the cell and no
     surface OAT1, to show the thickness artefact. Conversion
     `Vmax_A = Vmax_V * d_cell` is a **comparison note**, not how the
     production model is parameterised.
   - Verification as in Section 6.

3. **Results**
   Formulation artefact (Fig 2); working-model base case (Fig 3); resistance
   partition and `Vmax_A`–`D_mem` map (Fig 4, 5); matched vs unmatched
   geometry (Fig 6); sensitivity and scale-up (Fig 7); map-guided improved
   fibre (Fig 8). Every production panel except Fig 2 uses the surface-flux
   model. Fig 8 is the design improvement, not a return to volumetric kinetics.

4. **Discussion**
   At working `Vmax_A` the bottleneck is OAT1; at literature-equivalent
   `Vmax` it is the membrane. The crossover is the transferable result.
   Unmatched OI was a housing artefact. Countercurrent buys little when the
   membrane/OAT1 path dominates. Limitations. Falsifying experiments.

5. **Conclusions**
   Model the transporter on the membrane surface. Report the crossover
   `Vmax_A` and the membrane-limited ceiling. Compare geometries only when
   OAT1 area and blood volume are matched.

**Data and code availability.** Deposit the `.mph` files, the parameter tables,
and the post-processing scripts. This repository is already structured for that
and it is increasingly expected by these journals.

---

## 11. Limitations to state explicitly

State these in the paper; each is a predictable reviewer objection.

1. Free IS only, or equilibrium binding if E1 is implemented; no bound-pool
   kinetics.
2. Single fibre, uniformly perfused; no flow maldistribution across a cartridge.
3. Newtonian blood.
4. Transporter kinetics taken from cell-culture measurements; `Vmax_A` on a
   real seeded fibre is uncertain, which is why results are reported against a
   sweep rather than a single value.
5. No fouling, no ultrafiltration, no cell-layer remodelling over time.
6. Matched IO/OI comparison equalises OAT1 area, blood volume and flow rates,
   but blood-side hydrodynamics (gap width, wall shear) cannot simultaneously be
   matched; the residual difference is reported rather than eliminated.
7. Steady flow with transient transport, justified by one-way coupling; would
   not hold if ultrafiltration were included.

---

## 12. Work breakdown

Ordered by dependency, not by calendar time.

1. **Implement E1 (protein binding)** in the working `.mph`. One algebraic
   relation; affects the driving force everywhere, so do it before generating
   any production data.
2. **Run the verification suite** (section 6) and record it. Everything
   downstream is worthless if this fails.
3. **Generate S1 and S3** (formulation artefact, capacity sweep). These carry
   the two strongest claims and can be run as parametric sweeps.
4. **Build the matched OI and unmatched OI models** by changing parameters and
   redrawing the rectangle order; run S4.
5. **Run S5, S6, S7** for the sensitivity, flow configuration and scale-up
   panels.
6. **Run S8** on the same `.mph` physics: baseline vs map-guided improved
   fibre. Do not rebuild a volumetric model for this step.
7. **Post-process** through `src/comsol_io_oi_comparison.py`, extended to
   produce the resistance partition and design map.
7. **Implement E3 validation** against whichever experimental comparison is
   obtainable.
8. **Draft** in the order Methods, Results, Discussion, Introduction, Abstract.
