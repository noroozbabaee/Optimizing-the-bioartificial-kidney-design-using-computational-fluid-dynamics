# Preliminary BAK module — notes for the UC meeting (27 October)

For Leyla to use with Elham, Jeroen, and Karin. This is a **concept**, not a
final CAD. Per-fibre CFD is the working **inside-out, surface-OAT1** model
(`BAK_IO.mph`): plateau molar flow **≈ 1.93×10⁻¹² mol/s** at `Vmax_A = 1e-7`,
`L = 20 mm`.

---

## 1. What Karin’s points actually mean

| Karin | Translation in our language |
|---|---|
| Long fibres kink | Keep **short** fibres. Our CFD length **20 mm** already matches that. Do not jump to 20 cm “to get more area” without a support. |
| Coated fibres on the **outside** must not touch | That is **IO** in our stack: blood in the lumen, **cells on the outer** polymer, dialysate in the shell. Packing cannot be a tight hemodialysis bundle. |
| Cells outside → **disk, short fibres, separate tubes** (Jeroen) | One fibre (or a few) per tube, radial disk or stacked disks. Protects the epithelium; uses more housing volume. Size is allowed to grow (extracorporeal). |
| Cells **inside** → fibres closer | **OI-type packing**: cells face the lumen, blood in the extra-fibre space. Neighbours can approach like a dialyser. Still need a blood gap and potting. |
| Size not critical | Optimise **biology and packing rules**, not a wearable footprint. |
| Clearance before final modelling | Need **order-of-magnitude CL**, not a finished 3D cartridge model. We already have a per-fibre number; experiments refine `Vmax_A` and protein binding. |

Do not mix “cells outside / pack apart” with “unmatched 1.8 mm CFD housing”. Those are different issues.

---

## 2. Recommended preliminary concept for 27 October

**Lead with two configurations, not one “winner”.**

**Concept A — cells outside (IO), Karin’s constraints**  
Short fibres (`L ~ 20 mm`), **not touching**, each in its own tube or well-defined shell (disk / cassette). Blood in the lumen, dialysate around (or in a defined annulus). This is the geometry we can already defend with CFD.

**Concept B — cells inside (OI), closer pack**  
Short fibres, blood on the outside, cells lining toward the lumen (filtrate/dialysate). Fair comparison in CFD uses the **same OAT1 area and blood volume**, housing **≈ 0.38 mm** per fibre unit — not a 1.8 mm shell. Packing can be denser; still keep coated inner lumens patent.

**Do not** present 1.8 mm “thesis OI” as the module design.

---

## 3. First-order size (honest, preliminary)

IO CFD, free IS, `Vmax_A = 1e-7`:

```
n_dot ≈ 1.93e-12 mol/s per fibre
CL    ≈ 1.16e-3 mL/min per fibre   (CL = n_dot / C_in, C_in = 0.1 mol/m³)
```

To reach **~1 mL/min** free-IS clearance (illustrative, not a clinical target yet):

```
N ≈ 1 / 0.00116 ≈ 900 fibres
```

at this `Vmax_A`, if every fibre is equally perfused. The membrane-limited
ceiling is higher (~3.8×10⁻³ mL/min per fibre in the analytical map) → fewer
fibres **only if** transporter capacity is raised.

**Protein binding** (not yet in the `.mph`) will **lower** free driving force;
fibre count will go **up**. Say that out loud on 27 October.

Disk + separate tubes: housing is larger than a tight bundle of 900 fibres.
That is acceptable if the device is extracorporeal. Sketch **area of disk** from
tube pitch (fibre + coating + gap so coats never touch), not from CFD housing
1.8 mm.

---

## 4. What to focus on (and what not)

**Focus**

- IO vs OI as **cell location + packing**, with Karin’s no-touch / no-kink rules
- Short fibre (20 mm) as the unit cell we already simulate
- Clearance **per fibre** and a range of fibre counts vs `Vmax_A`
- Blood gap / shear if OI (thin annulus): transport vs hemolysis
- What experiment can give before or soon after 27 Oct: even a **membrane-only**
  or **few-fibre** IS clearance bounds `Vmax_A`

**Do not**

- Wait for “final clearance” before any sketch — use CFD + bounds
- Optimise dialysate flow or cell thickness (not the bottleneck at this `Vmax_A`)
- Promise a clinical cartridge CAD for 27 October
- Treat unmatched large-shell OI as an improved design

---

## 5. Suggested reply stance (to the email)

Agree to a short brainstorm. Bring: (1) two packing sketches A/B, (2) per-fibre
CFD clearance, (3) fibre-count order of magnitude, (4) list of data that would
change the sketch (`Vmax_A`, bound fraction, max wall shear). Ask Jeroen for
the disk/tube pitch he had in mind. Ask Karin what “must not touch” means in
millimetres (coating + medium gap).
