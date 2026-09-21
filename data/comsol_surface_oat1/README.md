# COMSOL exports for IO vs OI (surface OAT1)

Put tables from university COMSOL here. Python does not invent these numbers.

```
IO/flux_BM.txt
IO/flux_OAT1.txt
IO/flux_CD.txt
OI_original/flux_BM.txt
OI_original/flux_OAT1.txt
OI_original/flux_CD.txt
OI_fair/flux_BM.txt
OI_fair/flux_OAT1.txt
OI_fair/flux_CD.txt
```

Each file: column 1 = time (min), column 2 = molar flow (mol/s). `%` comments are allowed.

Then:

```text
python3 src/comsol_io_oi_comparison.py
```

`geometry_table.csv` is written even before any COMSOL run (radii, areas, volumes).
