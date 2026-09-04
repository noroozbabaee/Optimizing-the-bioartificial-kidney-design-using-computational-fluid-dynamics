# Computational Modeling of Protein-Bound Uremic Toxin Transport in Bioartificial Kidney Hollow-Fiber Systems
**Author:** Floriene Holvoet 

**Supervisors:**  
- Prof. Dr. ir. Charlotte Debbaut¹  
- Prof. Dr. ir. Aurélie Carlier²  

**Counsellors:**  
- Dr. Leyla Noroozbabaee²  
- Jessie Duquesne¹  

¹ Ghent University  
² Maastricht University

> **Student / pipeline guide (equations, parameters, diagnosed issues, COMSOL steps):**  
> **[`SURFACE_OAT1_PIPELINE_README.md`](SURFACE_OAT1_PIPELINE_README.md)**  
> Short university COMSOL run card: [`comsol/RUN_ON_UNIVERSITY_COMSOL.md`](comsol/RUN_ON_UNIVERSITY_COMSOL.md)

## Project Overview

This project investigates the transport and clearance of the protein-bound uremic toxin (PBUT) indoxyl sulfate (IS) in bioartificial kidney hollow-fiber systems using computational fluid dynamics (CFD) simulations in COMSOL Multiphysics.

The work compares inside-out and outside-in hollow-fiber configurations under static, cocurrent, and countercurrent dialysate conditions. Active cellular uptake was incorporated using Michaelis–Menten kinetics to represent organic anion transporter (OAT1)-mediated transport.

The simulations evaluate:
- geometric effects,
- parameter sensitivity analysis,
- blood-volume scaling,
- dialysate flow conditions,
- multifiber interactions,
- and the contribution of active transport mechanisms.

Post-processing was performed in Python.

---

# Background

Protein-bound uremic toxins (PBUTs), such as indoxyl sulfate (IS), are poorly removed by conventional dialysis therapies because only the free toxin fraction can diffuse across the dialysis membrane. In the native kidney, PBUT removal occurs primarily through active tubular secretion mediated by organic anion transporters (OATs) expressed in proximal tubule epithelial cells (PTECs).


<p align="center">
  <img src="figures/bioartificial_kidney%20(3).png" width="700">
</p>

<p align="center">
  <em>
  Schematic representation of a bioartificial kidney integrated with a conventional dialysis filter. 
  After conventional dialysis removes small and medium-sized solutes, blood enters the bioartificial kidney, 
  where OAT1-expressing proximal tubule epithelial cells actively transport protein-bound uremic toxins 
  across hollow-fiber membranes before the blood is returned to the patient.
  Adapted from Ramada et al. (2023) [1].
  </em>
</p>


Bioartificial kidney systems aim to restore this missing transport functionality by integrating living renal cells with hollow-fiber membrane technology. However, optimizing such systems requires understanding the coupled effects of:
- geometry,
- flow conditions,
- membrane transport,
- and active cellular uptake.

This work uses CFD-based transport modeling to systematically investigate how hollow-fiber configuration and flow conditions influence PBUT transport and clearance performance.

---

# Research Questions

This project addresses the following research questions:

1. How do inside-out and outside-in hollow-fiber configurations influence indoxyl sulfate transport and clearance?

2. What is the effect of cocurrent and countercurrent dialysate flow on clearance performance?

3. How do changes in IS concentration, blood flow rate, dialysate flow rate, and Michaelis--Menten uptake capacity influence transport and clearance performance?

4. What is the contribution of active Michaelis–Menten transport relative to passive diffusion?

5. How do multifiber configurations influence concentration gradients and overall transport behavior?

---

# Model Overview

## Geometry

Three hollow-fiber configurations were investigated:

| Configuration | Description |
|---|---|
| Inside-out | Blood flows through the lumen while dialysate occupies the outer shell |
| Outside-in | Blood occupies the outer shell while dialysate flows through the lumen |
| Adjusted outside-in | Modified outside-in geometry with the blood compartment volume matched to the blood compartment volume of the inside-out configuration |

The computational domain consisted of four compartments:
- blood,
- membrane,
- epithelial cell layer,
- dialysate.

Single-fiber simulations were modeled using a 2D axisymmetric geometry to reduce computational cost while preserving the dominant radial transport mechanisms.

Multifiber simulations were later extended to 3D configurations containing five repeated fiber units embedded within a shared compartment.

---

## Flow Configurations

Three dialysate conditions were investigated:
- stagnant dialysate,
- cocurrent flow,
- countercurrent flow.

Countercurrent flow was introduced to maintain concentration gradients along the fiber length and enhance solute transport.
### Inside-out countercurrent configuration
<p align="center">
  <img src="figures/inside_out_countercurrent (1).png" width="750">
</p>

<p align="center">
  <em>
  Figure: Inside-out countercurrent flow configuration, with blood flow in the lumen and dialysate flow imposed in the opposite direction in the outer compartment.
  </em>
</p>

### Outside-in countercurrent configuration
<p align="center">
  <img src="figures/outside_in_countercurrent (1).png" width="750">
</p>

<p align="center">
  <em>
  Figure: Outside-in countercurrent flow configuration, with blood flow in the outer domain and dialysate flow imposed in the opposite direction through the lumen.
  </em>
</p>

---

## Modelling Scenarios

A stepwise modeling strategy was adopted, progressing from single-fiber axisymmetric simulations to multifiber 3D configurations.

| Scenario | Purpose |
|---|---|
| Inside-out single fiber | Reference configuration |
| Outside-in single fiber | Geometric inversion |
| Adjusted outside-in | Volume-matched comparison |
| Cell-layer split model | Separate basolateral/apical transport behavior |
| Multifiber models | Fiber interaction effects |

Each configuration was evaluated under:
- static dialysate conditions,
- cocurrent flow,
- countercurrent flow.

---

# Mathematical Model

## General Transport Equation

Transport of indoxyl sulfate (IS) was modeled using the convection–diffusion–reaction equation:

$$
\frac{\partial c}{\partial t} + \mathbf{u}\cdot\nabla c
= D\nabla^2 c + R(c,V_{\max},K_m)
$$

where:
- $c$ = indoxyl sulfate (IS) concentration
- $D$ = diffusion coefficient
- $\mathbf{u}$ = velocity field
- $R(c,V_{\max},K_m)$ = cellular uptake term

The simulations were implemented using the *Transport of Diluted Species* interface in COMSOL Multiphysics 6.3.

---

## Domain-Specific Transport Mechanisms

| Domain | Convection | Diffusion | Reaction |
|---|---|---|---|
| Blood | Yes | Yes | No |
| Membrane | No | Yes | No |
| Cell layer | No | Yes | Michaelis–Menten uptake |
| Dialysate | Optional | Yes | No |

Transport in the blood and dialysate compartments included both convection and diffusion, while the membrane and cell layer were modeled as diffusion-dominated regions.

---

## Flow Model

Fluid motion in the blood and dialysate compartments was modeled using the incompressible Navier–Stokes equations under laminar conditions.

Countercurrent and cocurrent dialysate configurations were investigated. Reynolds number analysis confirmed laminar flow behavior for all simulated cases.

Fully developed parabolic inlet velocity profiles were imposed at the blood and dialysate inlets.

---

## Active Michaelis–Menten Transport

Active uptake within the epithelial cell layer was modeled using Michaelis–Menten kinetics:

$$
R_{\mathrm{uptake}} = V_{\max}\frac{c}{K_m+c}
$$

with:
- $V_{\max}=10^6\ \mu\mathrm{mol\ L^{-1}\ min^{-1}}$
- $K_m=20\ \mu\mathrm{M}$

Additional simulations were performed with varying $V_{\max}$ values to evaluate the influence of active transport capacity on overall clearance.

A split cell-layer model was also investigated to distinguish between basolateral and apical transport behavior.

## Surface OAT1 formulation and fair IO vs OI

The original cell-domain Michaelis–Menten term smears OAT1 through the full epithelial thickness. The corrected models keep the polymer membrane as **one diffusion domain** and move active transport to **surfaces**:

1. No volumetric reaction in the cell.
2. Reversible OAT1 at the **membrane–cell** face (separate concentrations `is` and `isc`).
3. Apical efflux at the **cell–dialysate** face.

**Run these on university COMSOL** (File → Open the Java file). Step-by-step: `comsol/RUN_ON_UNIVERSITY_COMSOL.md`.

| Java model | Role |
|---|---|
| `comsol/BAK_IO_OAT1_SurfaceFlux.java` | Inside-out reference |
| `comsol/BAK_OI_OAT1_SurfaceFlux.java` | Thesis outside-in (control, unfair) |
| `comsol/BAK_OI_fair_OAT1_SurfaceFlux.java` | Fair outside-in: same OAT1 area and blood volume as IO |

Export flux tables into `data/comsol_surface_oat1/<IO|OI_original|OI_fair>/`, then:

```text
python3 src/comsol_io_oi_comparison.py
```

Geometry equations live in `src/bak_geometries.py`. A 1D radial diagnostic (IO only, not the fair comparison) is still `python3 src/oat1_surface_flux_model.py`.

---

# Numerical Implementation

Simulations were performed in COMSOL Multiphysics 6.3 using time-dependent studies. To improve computational efficiency, studies were separated into multiple sequential solution steps, allowing intermediate results to be reused in subsequent calculations without affecting the final solution.

The nonlinear systems were solved using:
- fully coupled formulation,
- PARDISO direct solver,
- tolerance-controlled convergence.

For multifiber simulations, a two-step strategy was used:
1. stationary solution of the laminar flow field,
2. time-dependent solution of species transport.

This segregated study approach reduced computational cost while producing results equivalent to those obtained from a single combined study.

Mesh independence was verified through mesh sensitivity analysis for all configurations.

Post-processing and transport analysis were performed in Python.

---

# Quantification of Transport and Clearance

## Clearance Definition

Clearance was quantified using the total molar transport rate across the blood–membrane interface:

$$
\dot{n}_M(t)=\int_{\Gamma_M} J_n\, d\Gamma
$$

A time-averaged clearance metric was defined as:

$$
\overline{CL}(t)=
\frac{1}{tAC_{in}}
\int_0^t \dot{n}_M(\tau)\,d\tau
$$

where:
- $A$ = membrane surface area
- $C_{in}$ = inlet indoxyl sulfate concentration

All clearance values were normalized by membrane surface area to enable comparison between geometries.



---

## Contribution of Active Transport

To quantify the contribution of active transport, simulations with and without Michaelis–Menten uptake were compared.

The passive transport contribution ratio was defined as:

$$
R_{\Phi}(t)=
\frac{
|\Phi_{V_{\max}=0}(t)|
}{
|\Phi_{\mathrm{full}}(t)|
}
$$

where:
- $R_{\Phi}=1$: active transport has negligible effect
- $R_{\Phi}<1$: active transport enhances overall transport

This analysis was used to distinguish passive diffusive transport from transporter-mediated uptake.

---

# Main Findings

Key findings from the simulations include:

- Under static dialysate conditions, the inside-out configuration maintained the transmembrane concentration gradient substantially longer than the outside-in configuration due to the larger surrounding dialysate volume, resulting in higher sustained clearance.

- Countercurrent dialysate flow strongly enhanced transport performance by suppressing dialysate saturation and maintaining concentration gradients along the fiber length. However, only minor differences were observed between cocurrent and countercurrent operation because the investigated fiber lengths were relatively short.

- Under flow conditions, the original outside-in configuration achieved the highest area-normalized clearance (~9.5 μL/(min·cm²)) due to the strongest local blood-to-membrane concentration gradients.

- The adjusted outside-in configuration exhibited the largest non-area-normalized clearance because of its substantially increased membrane and cell-layer surface area, despite weaker local concentration gradients.

- Membrane-area normalization strongly influenced the interpretation of clearance performance. Configurations with larger membrane areas showed lower area-normalized clearance despite higher total solute transport.

- Transport remained predominantly diffusion-limited over most of the investigated parameter range. Clearance showed only weak sensitivity to Vmax up to approximately 10^7–10^8 μmol/(L·min), while the inlet indoxyl sulfate concentration had by far the strongest effect on clearance, followed by the dialysate flow rate. In contrast, changes in blood flow rate and moderate variations in Vmax produced only minor clearance changes.
  
-  At very high transporter capacities (Vmax ≥ 10^8 μmol/(L·min)), the system transitioned from a diffusion-limited regime to a blood-supply-limited regime. Transporters depleted toxin near the blood–membrane interface faster than it could be replenished from the bulk blood compartment, reducing the local concentration gradient driving uptake.

- Active Michaelis–Menten transport contributed negligibly at Vmax = 10^6 μmol/(L·min), where transport was governed almost entirely by passive diffusion. Significant contributions from active transport only became apparent once Vmax exceeded approximately 10^8 μmol/(L·min), consistent with the transition from a diffusion-limited regime toward a blood-supply-limited regime.

- Compared with the corresponding single-fiber configuration, the inside-out multifiber geometry exhibited an approximately proportional increase in total clearance with increasing fiber number, indicating that the individual fibers operated largely independently. In contrast, the outside-in multifiber geometry showed substantially weaker scaling because toxin extraction from a shared blood compartment reduced the blood-to-membrane concentration gradients and therefore the driving force for transport.

---

# Figure Reproducibility Overview

The figures included in this repository were generated from data exported from COMSOL Multiphysics and processed using Python post-processing scripts. The table below provides an overview of the figures used in the thesis and their corresponding Python scripts.

All Python scripts are located in the src folder. The required input data files can be found in the data folder, organized under the corresponding Python script name. Each subfolder contains the .txt files needed to run the associated Python code and reproduce the figures.

A PDF version of the complete master thesis is included in this repository and can be found at:
`thesis/masterproef-Floriene_Holvoet.pdf`

The figure numbering and references used throughout this repository correspond directly to those in the thesis.

The COMSOL Multiphysics model files used in this work are available separately and can be downloaded from the following link:

https://ugentbe-my.sharepoint.com/:u:/r/personal/floriene_holvoet_ugent_be/Documents/Master%20thesis%20-%20CFD%20modelling%20BAK/final%20configurations/final%20configurations.zip?csf=1&web=1&e=S3uOMR

| Figure | Description | Python script |
|---|---|---|
| `Figure 8.6` | Mesh sensitivity analysis | `src/mesh_sensitivity_analysis.py` |
| `Figure 9.1` | Radial velocity profiles | `src/velocity_and_pressure_analysis.py` |
| `Figure 9.2` | Axial pressure profiles | `src/velocity_and_pressure_analysis.py` |
| `Figure 9.3` | Static radial concentration profile: inside-out, outside-in, adjusted outside-in | `src/radial_profiles_static.py` |
| `Figure 9.5` | Outside-in countercurrent radial concentration profile at different axial positions | `src/radial_profiles_countercurrent.py` |
| `Figure 9.6` | Inside-out countercurrent radial concentration profile at different axial positions | `src/radial_profiles_countercurrent.py` |
| `Figure 9.7` | Adjusted outside-in countercurrent radial concentration profile at different axial positions | `src/radial_profiles_countercurrent.py` |
| `Figure 9.8` | Time-average clearance under static dialysate conditions | `src/clearance_analysis.py` |
| `Figure 9.9` | Dialysate-based clearance under static dialysate conditions | `src/clearance_analysis.py` |
| `Figure 9.10` | Time-average clearance under countercurrent dialysate flow | `src/clearance_analysis.py` |
| `Figure 9.11` | Axial concentration profile for extended cocurrent inside-out model, countercurrent inside-out model and axial concentration-difference comparison | `src/flow_direction_analysis.py` |
| `Figure 9.12` | End point time-average clearance normalized by membrane area | `src/clearance_analysis.py` |
| `Figure 9.13` | End point time-average clearance without membrane-area normalization | `src/clearance_analysis.py` |
| `Figure 9.14` | Sensitivity of clearance to `Vmax` | `src/parameter_sensitivity.py` |
| `Figure 9.15` | Sensitivity of cell-to-dialysate flux to `Vmax` | `src/parameter_sensitivity.py` |
| `Figure 9.16` | Radial concentration profiles for low and high `Vmax` | `src/parameter_sensitivity.py` |
| `Figure 9.17` | Sensitivity of clearance to inlet IS concentration | `src/parameter_sensitivity.py` |
| `Figure 9.18` | Sensitivity of clearance to blood flow rate | `src/parameter_sensitivity.py` |
| `Figure 9.19` | Sensitivity of clearance to dialysate flow rate | `src/parameter_sensitivity.py` |
| `Figure 9.20` | Split cell-layer model: clearance sensitivity to apical `Km` | `src/split_cell_layer_analysis.py` |
| `Figure 9.21` | Split cell-layer model: cell-to-dialysate transport sensitivity to apical `Km` | `src/split_cell_layer_analysis.py` |
| `Figure 9.22` | Michaelis-Menten contribution ratio for `Vmax = 10^6` | `src/MM_transport_contribution.py` |
| `Figure 9.23` | Michaelis-Menten contribution ratio for `Vmax = 10^9` | `src/MM_transport_contribution.py` |
| `Figure 9.25` | Total multifiber clearance under countercurrent conditions | `src/multifiber_clearance.py` |
| `Figure 9.26` | Individual fiber clearance in multifiber configurations | `src/multifiber_clearance.py` |
| Surface OAT1 | 1D radial diagnostic (IO only) | `src/oat1_surface_flux_model.py` |
| Surface OAT1 | Journal figures from 1D tables | `src/paper_figures_oat1.py` |
| IO vs OI | COMSOL export comparison (fair pair) | `src/comsol_io_oi_comparison.py` |


## Software

- COMSOL Multiphysics 6.3
- Python

---

## References

1. Ramada, M., et al. *Portable, wearable and implantable artificial kidney systems: needs, opportunities and challenges.*  
   **Nature Reviews Nephrology** 19(8), 481–490 (2023).  
   https://doi.org/10.1038/s41581-023-00726-9
2. Refoyo, R., Skouras, E.D., Chevtchik, N.V., Stamatialis, D. & Burganos, V.N.
   Transport and reaction phenomena in multilayer membranes functioning as bioartificial kidney devices.
   Journal of Membrane Science 565, 61–71 (2018).
   https://doi.org/10.1016/j.memsci.2018.08.007

