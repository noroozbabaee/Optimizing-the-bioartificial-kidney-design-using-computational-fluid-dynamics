# COMSOL plots for BAK_IO — short tutorial

COMSOL does **not** put coordinates on a graph node. A plot is always:

```
Data set  →  what to evaluate (expression)  →  how to draw it (2D surface or 1D curve)
```

If that chain is wrong, the picture is wrong even when the model is right.

---

## 1. Three objects you must not mix up

| Object | Where in the tree | What it is |
|---|---|---|
| **Physics** | `spf`, `tds`, `tds2`, `tds3` | The equations |
| **Data set** | **Results → Data Sets** | A **solution** (stationary flow, or concentrations vs time) plus optional **cuts** (a point, a line) |
| **Plot group** | **Results → Velocity / Concentration / 1D Plot Group** | A **picture** of a data set |

**Times (0, 5, 60 min)** live on the **time-dependent data set** and on the **1D plot**. They do **not** appear when you click `Study 1/Solution 1` in Data Sets. That node only *names* the solution.

| Data set | Use for |
|---|---|
| `Study 1/Solution Store 1 (sol2)` | Flow only (Step 3). **No** useful concentration-vs-time. |
| `Study 1/Solution 1 (sol1)` | Concentrations vs time (Steps 4–8). |
| `Cut Point 2D` | One `(r, z)` sitting on `sol1`. Coordinates are **here**, nowhere else. |

---

## 2. Which concentration is which

| Plot name | Variable | Where it exists |
|---|---|---|
| **Concentration (tds)** | `c` | blood + membrane (domains 1–2) |
| **Concentration (tds2)** | `c2` | cell only (domain 3, 20 µm) |
| **Concentration (tds3)** | `c3` | dialysate (domain 4) |

Plotting `c2` on a blood point is empty/wrong. Plotting `c` on the cell is wrong.

In 2D axisymmetric, **x = r**, **y = z**.

---

## 3. Colour plots (2D) — “what does the fibre look like at one time?”

**When to use:** Step 3 (speed), Step 4a (`c2` map), Step 5 (`c` map).

1. Click a ready-made group, e.g. **Concentration (tds)**.
2. Click **Surface 1** under it.
3. **Expression** must match the physics (`c`, `c2`, `spf.U`, `spf2.U`).
4. **Data** on the **plot group**: Time = **60 min** (one snapshot).
5. **Plot**, then **Zoom Extents**.

**All one colour (all red)** usually means the **legend range is tiny**, not that the physics failed.

- Read the **min and max on the colour bar**.
- To see inlet → outlet: Surface 1 → **Range** → manual **0** to **0.1** for `c`.

You normally **do not** need Selection on a Surface. `tds` already lives only on blood+membrane; `spf2` only on dialysate.

---

## 4. Time curves (1D) — “how does one point change with time?”

**When to use:** Step 4b (`c2` vs t), three radii vs t.

Coordinates are **not** on Point Graph. Selection on Point Evaluation is empty because that tool only likes **vertices**.

### 4a. Place a point

1. **Results → Data Sets** → right-click → **Cut Point 2D**.
2. **Data set** = `Study 1/Solution 1 (sol1)` — **not** `sol2`.
3. **X** = `r` with unit, **Y** = `z` with unit, e.g.  
   cell: `0.26[mm]`, `10[mm]`.

### 4b. Draw vs time

1. Right-click **Results** → **1D Plot Group**.
2. Right-click that group → **Point Graph**.
3. Point Graph: **Data set** = that Cut Point; **Expression** = `c` or `c2`; **Time selection** = **All**.
4. Click the **1D Plot Group** (parent) → **x-axis = Time** → **Plot**.

Empty **1D Plot Group 16** with **no Point Graph** will not show a curve. Use the group that **has** Point Graph (e.g. 18).

### Three radii (same z = 10 mm)

| Cut point r | Expression |
|---|---|
| `0.075[mm]` blood | `c` |
| `0.20[mm]` membrane | `c` |
| `0.26[mm]` cell | `c2` |

Three Cut Points, three Point Graphs, **one** 1D Plot Group.

---

## 5. Numbers (tables) — “what is the value?”

| Need | Node |
|---|---|
| Value at a cut point vs time | Point Graph → **Evaluate**, or Derived Values using the Cut Point data set |
| Molar flow through a **circle** (Step 6) | **Derived Values → Line Integration** on an **edge**, not a point |

Line Integration: select the **boundary** in Graphics (inlet, OAT1, …). For volume flow in axisymmetric, expression = **`w`** or **`spf.w`**, unit **m³/s**, do **not** also type `2*pi*r` (or you get m⁴/s). For **mole** flow later: `2*pi*r*J_OAT1` if COMSOL does **not** already revolve; if the unit becomes m⁴ or double, drop `2*pi*r`.

---

## 6. Recipe for the rest of BAK_IO checks

| Step | Plot | Pass |
|---|---|---|
| 4 | 1D: `c2` at 0.26 mm | t=0 is 0; then rises (**you already passed**) |
| 5 | 2D: **Concentration (tds)**, range 0–0.1 | colour-bar **max ≤ 0.1** |
| 6–8 | Line Integration on OAT1 and apical | `|n_OAT1| ≈ |n_apical|` at 60 min; below `3.14e-12` mol/s |

---

## 7. If it looks wrong, check this list first

1. Expression: `spf` vs `spf2`, `c` vs `c2` vs `c3`.
2. Data set: `sol1` (transport) vs `sol2` (flow).
3. 2D plot = one time; 1D Point Graph = all times, x = **Time**.
4. Cut point `r` actually in that layer.
5. Colour bar **numbers**, then maybe set Range by hand.
