# BAK_IO verification protocol (do this before OI fair)

The IO model is built. **Do not start OI fair until this list is done.**
These steps test whether the `.mph` solves the **surface-OAT1 equations you
intended**. They are **verification** (the numerics). True **validation**
against a wet experiment is step 11 and can wait.

Work in `BAK_IO.mph` only. Save a copy `BAK_IO_verify.mph` if you will change
the mesh or switch the transporter off.

Default numbers this protocol assumes:

```
Vmax_A = 1e-7 mol/(m^2 s)
A_OAT1 = 2 π (0.25 mm) (20 mm) = 3.142e-5 m^2
n_max_OAT1 = Vmax_A * A_OAT1 = 3.14e-12 mol/s
Q_b * C_in  ≈ 1.67e-10 mol/s
C_in = 0.1 mol/m^3
```

IO edges you already mapped (click to confirm before each integral):

| Role | Typical boundary |
|---|---|
| Blood inlet `z = 0` | 2 |
| Blood–membrane | 4 |
| OAT1 | 7 |
| Apical | 10 |
| Dialysate inlet `z = L` | 12 |

---

## Step 1 — Geometry and domains

**What we are testing:** four layers in the right order; Form Union; no extra
domains.

Hover domains:

| Domain | Must be |
|---|---|
| 1 | blood 0–0.15 mm |
| 2 | membrane 0.15–0.25 mm |
| 3 | cell 0.25–0.27 mm |
| 4 | dialysate 0.27–1.80 mm |

**Pass:** 4 domains, 13 boundaries. Domain 1 is blood, not dialysate.

---

## Step 2 — Physics assignment

**What we are testing:** flow and the three concentration fields sit on the
correct domains; no volumetric sink in the cell.

| Interface | Domains |
|---|---|
| `spf` | 1 only |
| `spf2` | 4 only |
| `tds` (`c`) | 1 and 2 |
| `tds2` (`c2`) | 3 |
| `tds3` (`c3`) | 4 |

Cell: convection off, **no Reaction** node. Fluid properties User defined.
`tds3` velocity = **`spf2`**.

**Pass:** those selections match. Fail if `spf` includes domain 4 or the cell
has `R = -Vmax*c2/(Km+c2)`.

---

## Step 3 — Steady flow looks like pipe flow

**What we are testing:** Navier–Stokes in blood and dialysate only; inlets
carry the intended mean speed; membrane and cell have **no** velocity.

After the Stationary step:

1. Plot speed in domain 1: should be Poiseuille-like, max on the axis, 0 at
   `r = R_BM`.
2. Speed in domains 2 and 3: ~0.
3. Domain 4: countercurrent (inlet at `z = L`).
4. Optional Derived Value, surface integration of `w` (or the axial velocity
   COMSOL uses) over the blood inlet, times the axisymmetric factor, should
   recover `Q_b ≈ 0.10 mL/min`.

**Pass:** no flow in the wall; blood in at `z = 0`; dialysate in at `z = L`.

---

## Step 4 — Sign check: the cell fills

**What we are testing:** OAT1 flux pair points **into** the cell, not out.

Plot `c2` vs time (point probe in the middle of domain 3, or a surface plot at
t = 60 min).

**Pass:** `c2` starts at 0 and **rises**, then levels off.  
**Fail:** `c2` stays 0 (wrong edge) or goes negative / only falls (swap both
OAT1 Flux signs together: `tds` `J0 = -J_OAT1`, `tds2` `J0 = +J_OAT1`).

This is the single most important check. Do not export clearance until it
passes.

---

## Step 5 — Concentrations stay physical

**What we are testing:** no unphysical source; blood/membrane field is the
inlet-limited `c`.

At t = 60 min:

- Blood + membrane `c`: **0 ≤ c ≤ C_in** (0.1 mol/m³).
- Dialysate `c3`: ≥ 0 and much smaller than `C_in`.
- Cell `c2` **may** exceed local `c`. That is allowed (active uptake).

**Fail:** `c > C_in` in blood or membrane → sign or inlet error.

---

## Step 6 — Add the three molar-flow tables

**What we are testing:** we can measure mass crossing each cylinder.

Results → Derived Values → Line Integration, unit **mol/s**:

| Name | Edge | Expression |
|---|---|---|
| Flux BM | blood–membrane (4) | `2*pi*r*tds.ndflux_c` |
| Flux OAT1 | OAT1 (7) | `2*pi*r*J_OAT1` |
| Flux CD | apical (10) | `2*pi*r*J_apical` |

Evaluate **all time steps**. Keep the tables. You will use them in steps 7–8
and for Python.

---

## Step 7 — Mass balance at late time

**What we are testing:** solute is not created or destroyed at the cell. At
steady state, what OAT1 puts in must leave through the apical face.

At the last time (60 min), compare **absolute** molar flows:

```
|n_OAT1|  ≈  |n_apical|
relative difference = | |n_OAT1| - |n_apical| | / |n_OAT1|
```

**Pass:** difference **< 1%**.  
**Fail:** Flux pair incomplete, wrong boundary, or mesh too coarse in the cell.

Blood–membrane flow `n_BM` can differ slightly from `n_OAT1` while the membrane
is still filling; they should approach each other as t → ∞.

---

## Step 8 — Capacity bounds

**What we are testing:** the transporter cannot exceed its areal ceiling, and
the fibre cannot clear more solute than the blood brings in.

```
|n_OAT1|  <  3.14e-12 mol/s     (Vmax_A * A_OAT1)
|n_OAT1|  <  1.67e-10 mol/s     (Q_b * C_in)
```

At `Vmax_A = 1e-7` you should be **well below** the flow-delivery limit and
**not too close** to 3.14e-12 unless the cell is empty and `c ≈ C_in` all along
the fibre (it is not).

**Fail:** `|n_OAT1|` above `Vmax_A A_OAT1` → area factor `2*pi*r` missing, or
`Vmax_A` not the value you think.

---

## Step 9 — Transporter off (passive membrane)

**What we are testing:** without OAT1/apical, IS should barely enter the cell
and dialysate; the jump at the cell membrane should disappear. This checks that
**the biology, not a numerical leak**, is doing the transport.

Save As `BAK_IO_passive.mph`. Set `Vmax_A = 0` (then `Vmax_ap = 0` too).
Recompute transport only.

**Pass:** `c2` stays ~0; `|n_OAT1|` and `|n_apical|` ~ 0; `c3` stays ~0;
membrane still shows a radial drop in `c` if anything leaks by diffusion, but
there is **no** dedicated path into dialysate through the cell.

Restore `Vmax_A = 1e-7` in the production file. Do not leave the passive file
as your main model.

---

## Step 10 — Mesh check (one refinement)

**What we are testing:** the reported OAT1 molar flow is not a mesh artefact.

Keep the production mesh. Duplicate the study or Save As and **double** radial
counts (blood / membrane / cell / dialysate) and axial 80 → 160. Recompute.
Compare `|n_OAT1|` at t = 60 min.

**Pass:** change **< 2%**.  
If not, keep the finer mesh as production.

Write a tiny table (you will need it in the thesis):

| Mesh | DOF (approx.) | `|n_OAT1|` (mol/s) |
|---|---|---|
| production | | |
| 2× | | |

---

## Step 11 — Time / solver (short)

**What we are testing:** 5 min output steps are enough for a 60 min run.

Either: recompute with `range(0,1,60)` or tighten time-dependent relative
tolerance by 10×.

**Pass:** `|n_OAT1|` at 60 min changes **< 1%**.  
If `c2` is still climbing a lot at 60 min, the physics is not at steady state
yet — extend to 240 min for a later production run; you can still use 60 min
for these checks if mass balance (step 7) is already close.

---

## Step 12 — Export and Python (IO only)

**What we are testing:** the pipeline from COMSOL table → clearance.

Copy to the repo:

```
data/comsol_surface_oat1/IO/flux_BM.txt
data/comsol_surface_oat1/IO/flux_OAT1.txt
data/comsol_surface_oat1/IO/flux_CD.txt
```

From the repository root:

```
python src/comsol_io_oi_comparison.py
```

**Pass:** script prints an IO `CL_end` and writes
`figures/comsol_io_oi/oat1_molar_flow_vs_time.png`. Missing OI folders is
expected.

---

## What this is *not* (yet)

| Later | Why wait |
|---|---|
| OI fair | Different geometry; IO must be trusted first |
| Formulation artefact (S1, volumetric vs areal) | Extra physics, not a check of this `.mph` |
| `Vmax_A` sweep / resistance map | Production science after verification |
| Protein binding | Model extension E1 |
| Match to a published clearance number | **Validation**. Best cheap option: membrane-only experiment or literature `P_m` vs your `D_mem/d_mem`. Do after steps 1–10 |

---

## Record as you go

Copy this into a lab note (one line per step):

```
Step 1 geometry: pass / fail
Step 2 physics: pass / fail
Step 3 flow: pass / fail
Step 4 c2 rises: pass / fail   c2(60 min) = ___
Step 5 c bounds: pass / fail
Step 7 |n_OAT1| = ___   |n_apical| = ___   rel diff = ___
Step 8 vs 3.14e-12: pass / fail
Step 9 Vmax=0: pass / fail
Step 10 mesh change %: ___
Step 12 Python CL_end: ___
```

When every line is pass, you are allowed to start `BUILD_OI_FAIR_GUI_COMSOL64.md`.
