# COMSOL models (surface OAT1)

**Start here on the university server:** [`RUN_ON_UNIVERSITY_COMSOL.md`](RUN_ON_UNIVERSITY_COMSOL.md)

These Java files are COMSOL 6.3 Model Java. Open with **File → Open** (file type Java). Binary `.mph` files are not in this repository.

| File | What it is |
|---|---|
| `BAK_IO_OAT1_SurfaceFlux.java` | Inside-out **reference** |
| `BAK_OI_OAT1_SurfaceFlux.java` | Thesis outside-in **control** (unfair area/volume) |
| `BAK_OI_fair_OAT1_SurfaceFlux.java` | Fair outside-in (same OAT1 area and blood volume as IO) |
| `apply_oat1_surface_flux.java` | Optional patch for an old thesis `.mph` (prefer the three full models) |

Physics (all three twins):

- four domains; polymer membrane is **one** diffusion domain
- **no** volumetric Michaelis–Menten
- three concentration fields: `is` (blood+membrane), `isc` (cell), `isd` (dialysate)
- reversible OAT1 flux at membrane–cell; apical efflux at cell–dialysate
- same \(Q_b\), \(Q_d\), \(C_{\mathrm{in}}\)

Regenerate after changing `src/bak_geometries.py`:

```text
python3 src/write_comsol_java_models.py
```
