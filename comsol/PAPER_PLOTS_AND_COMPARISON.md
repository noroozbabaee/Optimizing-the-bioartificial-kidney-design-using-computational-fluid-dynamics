# Paper plots and comparison from BAK_IO (then OI)

Use the **surface-OAT1** model only. Do not use old volumetric thesis Python
(`clearance_analysis.py`, …) or `paper_figures_oat1.py` (that is a 1D toy model).

**Comparison rule:** same `Q_b`, `Q_d`, `C_in`, `Vmax_A`, wall thicknesses.
Compare **IO vs OI_fair**. Show unmatched OI only as a control. Always report
clearance **per OAT1 area**.

---

## What you can plot now (IO only)

You have a working `BAK_IO.mph`. That is enough for **Figure 3** (base-case
fields) and for **supplementary** verification plots. **Figure 6** needs OI fair
later.

### A. Screenshots from COMSOL (Figure 3 / supplement)

Dataset always **`sol1`**, not Cut Plane, not Revolution.

| Panel | Plot | Settings |
|---|---|---|
| 3a | `c` at 60 min | Concentration (tds), Range **0–0.1**, Zoom Extents |
|  | `c2` at 60 min | Concentration (tds2), cell strip |
|  | `c3` at 60 min | Concentration (tds3), shell (small values) |
| 3b | `c` and `c2` vs **r** at `z = 10 mm` | Cut Line 2D from `(0, 10 mm)` to `(0.27 mm, 10 mm)`; Line Graph; mark 0.15 / 0.25 / 0.27 mm |
| Flow (supplement) | `spf.U`, `spf2.U` | already done |

Export: plot window → **File → Export → Image** (PNG, 300 dpi). Name them
`fig3_c_surface.png`, `fig3_c2.png`, `fig3_radial.png`.

### B. Numbers from COMSOL (must do this for Python)

**Results → Derived Values → Line Integration**, time-dependent `sol1`, **all times**.

| Name | Edge | Expression | Unit |
|---|---|---|---|
| Flux BM | blood–membrane (r = 0.15 mm) | `2*pi*r*tds.ndflux_c` | mol/s |
| Flux OAT1 | OAT1 (r = 0.25 mm) | `2*pi*r*J_OAT1` | mol/s |
| Flux CD | apical (r = 0.27 mm) | `2*pi*r*J_apical` | mol/s |

If the unit becomes m² or m⁴, drop `2*pi*r` and turn **axisymmetric revolution**
on, or the reverse — the **value** at 60 min must be on the order of **10⁻¹² mol/s**,
not 10⁻⁹ (that is volume flow).

**Evaluate all times.** Table → **Export** as plain text:

```
data/comsol_surface_oat1/IO/flux_BM.txt
data/comsol_surface_oat1/IO/flux_OAT1.txt
data/comsol_surface_oat1/IO/flux_CD.txt
```

Two columns: time, molar flow. `%` comments allowed.

**Paper check on the table (60 min):**

```
|n_OAT1| ≈ |n_apical|     (within 1%)     mass balance
|n_OAT1| < 3.14e-12       Vmax_A * A_OAT1
```

Clearance the paper uses:

```
CL      = |n_OAT1| / C_in              [m³/s]
CL'     = CL / A_OAT1                  [m/s]
CL'_uL  = CL' * 6e6                    [µL min⁻¹ cm⁻²]
```

`A_OAT1 = 31.42 mm²` for IO.

### C. Python (comparison-ready even with IO alone)

On the PC that has the repo (laptop is fine):

```
python -m pip install -r requirements.txt
python src/comsol_io_oi_comparison.py
```

Writes:

- `figures/comsol_io_oi/oat1_molar_flow_vs_time.png`
- `figures/comsol_io_oi/clearance_endpoint_bars.png` (IO bar only until OI exists)
- `data/comsol_surface_oat1/comparison_metrics.csv`

---

## What “comparison” means in the paper

| Compare | Fair? | Role |
|---|---|---|
| IO vs **OI_fair** | yes | main geometry result (Fig 6) |
| IO vs OI 1.8 mm housing | no | size artefact only |
| IO vs volumetric MM | methods contrast (Fig 2) | extra runs, not this `.mph` |
| `c` vs `c2` vs `c3` | same fibre | shows three-field physics (Fig 3) |
| t = 0 vs 5 vs 60 min | same point | transient (supplement) |

Do **not** compare total mol/s of unmatched OI to IO without dividing by
`A_OAT1`.

---

## After OI fair exists (same exports)

Same three `flux_*.txt` files under:

```
data/comsol_surface_oat1/OI_fair/
```

Run the **same** Python script. The bar chart becomes IO vs OI_fair.

Same `Vmax_A`, `Q_b`, `Q_d`. Different `U_avg_d`.

---

## Not yet (need extra COMSOL runs)

| Figure | Extra work |
|---|---|
| Fig 2 | volumetric vs areal cell-thickness sweep |
| Fig 4–5 | `Vmax_A` parametric sweep + resistance from Δc / n_dot |
| Fig 6 full | OI_fair + optional OI_original |
| Fig 7–8 | sensitivity and improved fibre |

Do those **after** IO flux files and Fig 3 are in the folder.

---

## File names to keep

```
figures/paper/
  fig3a_c_IO_60min.png
  fig3b_radial_z10.png
  fig3c_c2_vs_time.png
data/comsol_surface_oat1/IO/flux_*.txt
figures/comsol_io_oi/          ← from Python
```
