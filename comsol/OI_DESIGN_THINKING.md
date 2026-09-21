# How to think about outside-in, and how to improve removal

Use the **same surface-OAT1 physics** as the working IO model. Do not go back to
volumetric Michaelis–Menten. Do not treat a 1.8 mm housing as “optimized OI”.

Your IO plateau (`n_dot ≈ 1.93e-12 mol/s`, `Vmax_A = 1e-7`) is already in the
**transporter-limited** regime. Design has to respect that, or you will “improve”
the wrong part of the fibre.

---

## 1. Two different questions (do not mix them)

| Question | Geometry | What it answers |
|---|---|---|
| Is **arrangement** better (blood outside vs inside)? | **OI fair** vs IO | orientation only |
| Can we **raise clearance**? | IO and/or OI fair, change `Vmax_A` or the membrane | bottleneck engineering |

**OI fair** (the design to build next):

- dialysate in the lumen, blood in a **thin outer shell**
- `R_OAT1 = 0.25 mm` (same OAT1 area as IO: 31.42 mm²)
- `R_house = 0.3808 mm` (same blood volume as IO)
- same `Q_b`, `Q_d`, `Vmax_A`, wall thicknesses

**Not** the best OI:

- thesis OI at 1.8 mm (different area and huge blood volume)
- “adjusted OI” that fattens the membrane to match volume

Those raise **total** moles by making the fibre **bigger**. That is not a better
outside-in idea.

Build OI fair with `comsol/BUILD_OI_FAIR_GUI_COMSOL64.md`.

---

## 2. What actually limits removal (from the IO run + the map)

Series resistances at working `Vmax_A = 1e-7` (IO estimate):

| Stage | Share | Lever |
|---|---|---|
| **OAT1** | ~66% | `Vmax_A` (expression, seeding) |
| Membrane | ~22% | thinner wall or higher `D_mem` / `eps_mem` |
| Apical | ~7% | already `10 × Vmax_A`; leave it |
| Blood film | ~3% | `Q_b`, gap shape (IO lumen vs OI annulus) |
| Cell diffusion | ~2% | almost useless to thicken/thin the cell |

**Consequence:** swapping to OI, even with a nicer blood gap, cannot give a large
win while OAT1 still owns two-thirds of the resistance. Expect **IO vs OI fair**
to be a **modest** difference. If unmatched 1.8 mm OI looks much better, that is
area/volume, not orientation.

Crossover: `Vmax_A ~ 3e-7`. Above that, **membrane** work pays; below it,
**transporter** work pays. Literature-scale `Vmax` is membrane-limited; your
working value is not.

---

## 3. Best characteristics to focus on (ranked)

**Always hold for a fair OI study**

1. `A_OAT1` (set by `R_OAT1` and `L`)
2. Blood volume `V_b`
3. `Q_b` and `Q_d` (throughput, not mean speed)
4. Membrane and cell **thickness** (same as IO)

**Then, to improve removal** (same physics, one change at a time)

| Rank | Characteristic | Why |
|---|---|---|
| 1 | **`Vmax_A`** toward ~`3e-7` | dominant resistance at your operating point |
| 2 | **Membrane permeance** `D_mem / d_mem` | next resistance; becomes #1 only after OAT1 is faster |
| 3 | **Fibre count / packing** | device-scale clearance; do not inflate one fibre’s housing |
| 4 | Blood-side gap / shear | OI’s real geometric extra: thin annulus, higher `k_b` — but it is a **small** slice of total R. Watch ΔP and hemolysis in a 31 µm gap |
| 5 | `Q_b` | thins the blood film; also shortens residence time — sweep, don’t guess |
| — | `Q_d` | almost inert here; use as a **negative control** |
| — | Cell thickness | artefact if you use volumetric MM; tiny if you use areal OAT1 |
| — | Co- vs counter-current | little gain when dialysate is not limiting |

**OI-specific caution:** do not “improve” OI by widening the housing. That
returns you to unmatched volume. If you ever vary the blood gap, report wall
shear and pressure drop with clearance.

---

## 4. How to think in this kind of study

1. **Verify one geometry** (you did this for IO: signs, mass balance, bounds).
2. **Ask where the bottleneck is** (resistance or `Vmax` sweep) *before* shape
   optimisation. Otherwise COMSOL will chase the wrong parameter.
3. **Change one idea per run.** “Blood outside” is one idea. “Also 6× more
   area” is another.
4. **Match what sets capacity** (`A_OAT1`, `V_b`, `Q`). Admit what you cannot
   match (blood hydrodynamics).
5. **Improve with the map:** raise the largest resistance, confirm clearance
   rises; raise a small one (`Q_d`) and confirm it does **not**.
6. **Normalise** by OAT1 area for arrangement; report absolute `n_dot` for
   device scale.

---

## 5. Practical sequence on the remote PC

1. Keep `BAK_IO.mph` as the reference (`n_dot ≈ 1.93e-12 mol/s`).
2. Build **`BAK_OI_fair.mph`** (GUI recipe). Same Flux pairs, reversed layers.
3. Same checks: `c2` rises; `|n_OAT1| ≈ |n_apical|`; export `OI_fair/flux_*.txt`.
4. Compare **area-normalised** clearance to IO (Python script).
5. Only then improve: e.g. `Vmax_A = 3e-7` on **both** IO and OI fair, then a
   thinner membrane, then `Q_d` as a dummy change.

Predicted story for the paper: matched OI is **not** a miracle; **OAT1 capacity
then membrane** are how you raise removal; OI’s thin blood shell is a
secondary, honest hydrodynamic footnote.
