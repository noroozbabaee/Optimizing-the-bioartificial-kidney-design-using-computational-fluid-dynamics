# COMSOL models (surface OAT1)

**COMSOL 6.4 on university PC:** read [`OPEN_ON_COMSOL64.txt`](OPEN_ON_COMSOL64.txt) and run [`compile_models.bat`](compile_models.bat).

**Full student guide:** [`../SURFACE_OAT1_PIPELINE_README.md`](../SURFACE_OAT1_PIPELINE_README.md)

| File | Role |
|---|---|
| `BAK_IO.java` | Inside-out reference (compile to `BAK_IO.class`) |
| `BAK_OI.java` | Thesis outside-in control |
| `BAK_OI_fair.java` | Fair outside-in (matched OAT1 area + blood volume) |
| `compile_models.bat` | Windows: creates the `.class` files for File > Open |
| `OPEN_ON_COMSOL64.txt` | Exact clicks for COMSOL 6.4 |
| `apply_oat1_surface_flux.java` | Optional patch for an old `.mph` |

Physics: one polymer membrane; no volumetric MM; fields `is` / `isc` / `isd`; reversible OAT1; apical efflux; same Q_b, Q_d, C_in.
