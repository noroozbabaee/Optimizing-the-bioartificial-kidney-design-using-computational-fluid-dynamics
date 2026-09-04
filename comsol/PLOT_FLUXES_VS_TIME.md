# Plot BM, OAT1, and apical molar flow vs time (one figure)

Three **Line Integration** nodes must already exist (different edges). This
makes **one 1D figure** with three curves. COMSOL 6.4 GUI.

If you want the **rise**, Step 2 times should be `range(0,0.25,5)` (or include
60 min with `range(0,0.25,5) range(5,5,60)`). With only `0,5,10,…` you get a
step, not a smooth start.

---

## 1. Evaluate the three integrals

For each of **Flux BM**, **Flux OAT1**, **Flux CD**:

1. Click the **Line Integration** node.
2. **Selection** = the correct edge (IO: BM **4**, OAT1 **7**, apical **10**).
3. **Expression** as you already used (mol/s).
4. **Data set** = `Study 1/Solution 1 (sol1)`.
5. **Time selection** = **All**.
6. Click **Evaluate**.

You should get **three tables** under **Results → Tables** (names like
`Table 1`, `Table 2`, …). Each: column 1 = time (min), column 2 = molar flow.

Rename the tables (right-click → Rename): `tbl_BM`, `tbl_OAT1`, `tbl_CD`.

If a flux is **negative**, that is only sign convention. You will plot
**absolute value** in step 3 so the three curves sit on top of each other.

---

## 2. One 1D plot group, three table graphs

1. Right-click **Results** → **1D Plot Group**.
2. Rename it `Flux vs time`.
3. Click **Flux vs time** (the parent).
   - **x-axis:** Time
   - Optional **x-axis range:** manual **0 to 5** for the short movie; **0 to 60**
     for the plateau.
4. Right-click **Flux vs time** → **Table Graph**. Repeat until you have
   **three** Table Graph nodes.

| Table Graph | Table | y-column |
|---|---|---|
| 1 | `tbl_BM` | the molar-flow column |
| 2 | `tbl_OAT1` | same |
| 3 | `tbl_CD` | same |

On each Table Graph:

- **Data → Table** = that table (not Cut Point, not Cut Plane).
- **y-axis data:** the **second** column (flow). If you can type an expression:
  `abs(data)` or pick the column and note the sign.
- **Legends:** `Blood-membrane`, `OAT1`, `Apical`.
- **Coloring:** three different colours (e.g. blue / red / green).
- Line width ~2.

5. Click **Flux vs time** → **Plot**.

**Pass:** three curves **together**; they rise (if you stored t &lt; 5 min) and
meet near **1.93×10⁻¹² mol/s**.

---

## 3. If Table Graph has no “abs”

Add a **column** in the table: Derived Values expression already `abs(2*pi*r*J_OAT1)`
and re-Evaluate, **or** in Table Graph use **Transformation → Absolute value**
if that menu exists, **or** export and use Python (below).

---

## 4. Axis labels (paper)

- x: **Time (min)**
- y: **Molar flow (mol/s)** or **|ṅ| (mol/s)**
- Title: **IO fibre, interface molar flow**

**File → Export → Image** (PNG, 300 dpi): `figS_flux_vs_time_IO.png`.

---

## 5. Same figure in Python (after export)

Save the three tables as:

```
data/comsol_surface_oat1/IO/flux_BM.txt
data/comsol_surface_oat1/IO/flux_OAT1.txt
data/comsol_surface_oat1/IO/flux_CD.txt
```

`%` comments allowed; col 1 = t (min), col 2 = mol/s.

```python
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

p = Path("data/comsol_surface_oat1/IO")

def load(name):
    d = np.loadtxt(p / name, comments="%")
    t, n = d[:, 0], np.abs(d[:, 1])
    if t[-1] > 1000:
        t = t / 60.0
    return t, n

fig, ax = plt.subplots(figsize=(6.2, 3.8))
for fname, lab in [
    ("flux_BM.txt", "Blood–membrane"),
    ("flux_OAT1.txt", "OAT1"),
    ("flux_CD.txt", "Apical"),
]:
    t, n = load(fname)
    ax.plot(t, n * 1e12, label=lab)
ax.set_xlabel("Time (min)")
ax.set_ylabel(r"$|\dot n|$ (pmol/s)")
ax.set_xlim(0, 5)          # drop this line for 0–60 min
ax.legend()
fig.tight_layout()
fig.savefig("figures/comsol_io_oi/flux_three_interfaces_vs_time.png", dpi=300)
```

Run from the **repository root**. `comsol_io_oi_comparison.py` currently plots
**OAT1 only**; this overlay is the paper/supplement figure you want.

---

## 6. What you should see

| Time | BM / OAT1 / apical |
|---|---|
| 0 min | ~0 |
| first 1–2 min | rise, **together** |
| 5–60 min | ~**1.93 pmol/s** (`1.93e-12 mol/s`), overlap |

If one curve is far from the other two, that edge or `2*pi*r` is wrong.
