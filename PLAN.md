# Hamiltonian/Lindbladian Learning Plan: Chiral Cavity-QED with V_Si Color Centers

## Explainability Statement

This analysis is fully transparent and reproducible. **Every free parameter has a unique physical meaning:** {φ_j} = azimuthal positions of emitters along the WGM disk circumference; {g_j} = standing-wave coupling strengths to the cavity field; {ω_j} = optical transition frequencies relative to a common rotating-frame reference; g_bs (= `beta` in `g2_computation.py`) = coherent CW↔CCW backscattering amplitude from surface roughness; P = incoherent above-resonant pump rate; τ_0 = MZI arm delay offset. **Every fixed constant is set by independent measurements:** γ = 65 MHz and γ_φ = 40 MHz from prior spectroscopy; κ(step) linearly interpolated from resonance transmission measurements. **Every algorithmic hyperparameter is independently motivated:** IRF σ = 115 ps from detector characterization; 2:1 binning to reduce shot noise while preserving g(2) shape; mask region [−500, +150] ps defined by the experiment protocol to avoid the blip feature. Model comparison uses AICc [Burnham & Anderson 2002], a standard frequentist small-sample criterion with well-established ΔAIC thresholds. No opaque or black-box inference steps are used. The full result is reproducible from this plan, the provided data files, `tools/g2_computation.py`, and standard Python scientific libraries (QuTiP, scipy, numpy).

---

## System Overview

The experiment cross-correlates the CW and CCW output modes of a high-Q 4H-SiC WGM disk resonator (κ ≈ 1.05–1.12 GHz, Q ≈ 291k–312k) containing multiple V_Si color centers (ZPL ~916 nm). Twelve steady-state g(2) traces are recorded as the cavity is gas-tuned by ~3.15 GHz (~3 κ total, ~0.25 κ/step). The defining observable is **time-asymmetry**: g(2)(τ) ≠ g(2)(−τ) in the CW×CCW cross-correlation, which weakens across the scan. Auto-correlations are symmetric (confirmed experimentally).

The full Hamiltonian is a **disordered Tavis-Cummings model with counter-propagating WGM modes** [Lukin et al., arXiv:2504.09324]:

    H = Δ_c(â†â + b̂†b̂) + g_bs(â†b̂ + b̂†â)
        + Σ_j [ ω_j σ_j†σ_j + (g_j/√2)(e^{iφ_j} σ_j†â + e^{-iφ_j} σ_j†b̂ + H.c.) ]

where â (b̂) is the CW (CCW) mode annihilation operator, and g_bs corresponds to the parameter `beta` in `g2_computation.py`. The 1/√2 converts the standing-wave coupling g_j (as typically quoted) to the per-traveling-mode coupling, consistent with the code. Lindblad dissipators: κ (both modes), γ_j = 65 MHz (intrinsic decay), γ_φ,j = 40 MHz (pure dephasing), P ∈ [0.02, 0.4]κ (incoherent pump). All rates are expressed in units of κ_ref = (κ_start + κ_end)/2 ≈ 1.087 GHz; kappa=1 in simulation. The tool `g2_computation.py` (WGMEmitterSystem, N=4, n_cav=4, ss_method="mesolve", parallel=False) computes the steady-state CW×CCW cross-correlation g(2)(τ). One N=4 simulation takes **~22 s single-core** (parallel=False).

**Fixed (not free):** γ/κ ≈ 0.060, γ_φ/κ ≈ 0.037.
**Fixed per step:** Δ_c(step), κ(step) — linearly interpolated from resonance file.
**Global (shared across all 12 steps):** {φ_j, g_j, ω_j}, g_bs, P, τ_0.

---

## Pre-Processing Pipeline

1. **Bin 2:1** the raw data (nominal ~10 ps/bin, verify from `g2_data.npz`) → **~20 ps/bin effective**. Crop to |τ| ≤ 2 ns → **~200 bins total**. Convert to κ units: τ_κ = τ_ns × κ_ref_GHz (e.g., 2 ns × 1.087 → 2.174 κ⁻¹).

2. **Normalization:** Baseline B = median of bins with |τ| > 1.5 ns. Divide all bins by B (profiles out absolute count magnitude).

3. **Background:** Additive offset c_bg, profiled analytically at every optimizer call (closed-form 2×2 weighted least-squares). Not a DE parameter.

4. **Tau0:** Global τ_0 ∈ [−80, +80] ps, a free DE parameter. Phenomenological fit provides per-trace initial estimates.

5. **Mask:** Exclude bins with τ ∈ [−500, +150] ps (before τ_0 correction) from all residuals, removing the blip feature. This leaves **n ≈ 167 unmasked bins** for fitting and AICc.

6. **IRF convolution:** Convolve g(2)_sim with a Gaussian (σ = 115 ps, in physical units) before comparing to data.

7. **Phenomenological bootstrap:** Fit each of the 12 full (±6 µs) traces with:

       g(2)_phenom(τ) = [1 − A·exp(−|τ|/τ_fast) + C·exp(−|τ|/τ_slow)] ⊗ Gauss(σ_IRF)

   to extract τ_0 per trace (used as DE initialization), confirm the dark-state bunching envelope [Dastidar et al., arXiv:2408.01799], and verify normalization consistency. Also inspect the full data range to check for any envelope shape that needs to be layered on top of the quantum simulation output.

---

## Step 1 — Candidate Model Enumeration

### Disorder axes

| Axis | Off | On |
|------|-----|----|
| Azimuthal phase | φ_j = 0 ∀j (gauge choice) | {φ_j} individually free ∈ [0, 2π) |
| Coupling strength | g_j = g̅ (one global param) | {g_j} individually free ∈ [0.05, 0.4]κ |
| Emitter frequency | ω_j = ω̅ (one global param) | {ω_j} individually free |
| Backscattering | g_bs = 0 | g_bs free; bounded by transmission |

**ω_j bounds:** midpoint of scan ± (scan_width/2 + 1.5κ). Emitters outside this range cannot reach resonance during the scan and are unobservable.

**Backscattering bound:** The transmission dip is well-fit by a single Lorentzian (no visible mode doublet). A CW/CCW doublet is resolvable when 2g_bs ≳ κ/2. Since no splitting is seen, g_bs ≤ 0.5κ is a conservative upper bound. A Lorentzian fit to the transmission spectrum further constrains this; practically expect g_bs ≲ 0.2κ. The transmission fit residuals relative to the noise floor determine the tightest defensible upper bound.

**Note on chirality:** With all φ_j = 0 (set by gauge, absorbing any uniform phase into mode definitions), the Hamiltonian satisfies exact CW↔CCW exchange symmetry (â ↔ b̂ leaves H invariant for any real g_bs and any {ω_j, g_j}). This symmetry forces g(2)_{CW,CCW}(τ) = g(2)_{CCW,CW}(τ) = g(2)_{CW,CCW}(−τ), i.e., no time-asymmetry. Chirality therefore requires φ_j to differ across emitters [Lukin et al., arXiv:2504.09324]. Models M0 and M2 (uniform φ = 0) serve as null hypotheses for chirality; any asymmetry they fit is noise-driven.

**Note on spectral disorder and cross-step trend:** Models with uniform ω (M0–M3) predict the same g(2) shape for all 12 steps (all emitters detune identically from the cavity as it sweeps; only absolute detuning changes, not the relative coupling pattern between emitters). Reproducing the *observed change in chirality* across 12 steps requires per-emitter spectral disorder {ω_j}: as the cavity sweeps, different emitters come into resonance at different steps, altering the chiral interference [supported by disordered TC formalism: Wierzchucka et al., arXiv:2312.03833; Zeb, arXiv:2208.11990]. M0–M3 are therefore expected to fail the cross-step consistency test regardless of their trace-1 fit quality.

### Eight candidate models (N = 4 fixed throughout)

| ID | g_bs | φ_j | g_j | ω_j | Physics role | DE dims† |
|----|------|-----|-----|-----|--------------|----------|
| M0 | 0 | uniform | uniform | uniform | Null / symmetric TC | 4 |
| M1 | 0 | disordered | uniform | uniform | Phase disorder only | 7 |
| M2 | ≠0 | uniform | uniform | uniform | Backscattering, null for chirality | 5 |
| M3 | ≠0 | disordered | uniform | uniform | Phase + backscattering | 8 |
| M4 | 0 | disordered | uniform | disordered | Phase + spectral disorder | 10 |
| M5 | 0 | disordered | disordered | disordered | All disorder, no backscattering | 13 |
| M6 | ≠0 | disordered | uniform | disordered | Phase + spectral + backscattering | 11 |
| M7 | ≠0 | disordered | disordered | disordered | Full model | 14 |

†DE dims = free physics params + P (pump, included as DE parameter) + τ_0. φ_1 ≡ 0 by gauge (rotational degeneracy removed; saves 1 dim in all disordered-phase models). c_bg is profiled analytically and is not counted.

---

## Step 2 — Fitting Methodology

### 2a. Loss function

For each simulated g(2)_sim(τ; θ) (convolved with IRF, shifted by τ_0), the model prediction is:

    g(2)_fit(τ_i) = A · g(2)_sim(τ_i − τ_0; θ) + c_bg

The normalization A and offset c_bg are **profiled analytically** at every optimizer call via closed-form weighted least squares (2×2 linear system), with Poisson weights w_i = 1/g(2)_data(τ_i):

    χ²(θ) = Σ_{unmasked} w_i [g(2)_data(τ_i) − A(θ)·g(2)_sim(τ_i − τ_0; θ) − c_bg(θ)]²

The **incoherent pump P is included as a DE parameter** (bounds [0.02, 0.4]κ). This avoids the 8× simulation overhead that a discrete pump grid would impose (8 simulations × 22 s = 176 s per optimizer call per worker, which would make each model take ~105 min instead of ~10 min), while still allowing P to be freely optimized alongside physics parameters. P affects g(2)(0) depth but is not a chirality-determining parameter.

### 2b. Optimizer and parallelization — model-selection phase (trace 1)

**Algorithm:** `scipy.optimize.differential_evolution`, strategy `'best1bin'`, `updating='deferred'`, `workers=7`. This distributes the full population across 7 cores, each running one `WGMEmitterSystem` instance with `parallel=False` internally. Population size = `popsize` × DE_dims (scipy convention). Set `popsize=3`, `maxiter=5`.

**Time budget per model (one simulation = 22 s; 7 simulations run concurrently per batch):**

| Model | DE dims | Population | Total evals | Wall time (evals ÷ 7 × 22 s) |
|-------|---------|------------|-------------|-------------------------------|
| M0 | 4 | 12 | 60 | ~3 min |
| M1 | 7 | 21 | 105 | ~6 min |
| M2 | 5 | 15 | 75 | ~4 min |
| M3 | 8 | 24 | 120 | ~6 min |
| M4 | 10 | 30 | 150 | ~8 min |
| M5 | 13 | 39 | 195 | ~10 min |
| M6 | 11 | 33 | 165 | ~9 min |
| M7 | 14 | 42 | 210 | ~11 min |
| **Total** | | | | **~57 min** |

**RAM:** Each worker holds one 256×256 density matrix plus QuTiP operators ≈ 50–80 MB. Seven workers ≈ 350–560 MB, well within 3 GB.

**Top-model refinement (trace 1):** After model selection, run one additional DE pass on the top model with bounds tightened to ±20% around the best-fit values and `popsize=3`, `maxiter=5`. Wall time ≤ 11 min (same as the initial run).

**Global fit (all 12 traces, top model):** Physics params {φ_j, g_j, ω_j, g_bs, P} and τ_0 are shared globally across all 12 steps. Each optimizer call distributes the 12 trace simulations across `multiprocessing.Pool(7)` → ceil(12/7) = 2 batches × 22 s = **44 s per optimizer call**. Use `scipy.optimize.minimize` with `method='Nelder-Mead'`, seeded from the refined trace-1 result (good seed → fast local convergence). Target ~40 evaluations: 40 × 44 s ≈ **29 min**. Note: Nelder-Mead is serial per evaluation; Pool(7) parallelizes *within* each evaluation over the 12 traces.

**Total wall-time budget:**
| Phase | Time |
|-------|------|
| Phenomenological fit (scipy curve_fit, no quantum sim) | ~5 min |
| Model selection (8 models, trace 1, DE) | ~57 min |
| Top-model refinement (trace 1, tight-bounds DE) | ~10 min |
| Global fit (12 traces, Nelder-Mead + Pool(7)) | ~29 min |
| **Grand total** | **~101 min < 2 hours ✓** |

### 2c. Physical bounds (hard constraints, enforced natively by DE)

| Parameter | Lower | Upper | Source |
|-----------|-------|-------|--------|
| g_j | 0.05 κ | 0.4 κ | Experiment background |
| ω_j | midpoint − 2.5κ | midpoint + 2.5κ | Scan range ± 1.5κ buffer |
| φ_j | 0 | 2π | Geometry; φ_1 ≡ 0 fixed |
| g_bs | 0 | 0.5κ | Transmission (no visible doublet; 2g_bs < κ) |
| P | 0.02 κ | 0.4 κ | Experiment background |
| τ_0 | −80 ps | +80 ps | MZI calibration uncertainty |

Parameters found at a bound after fitting are flagged as potentially indicating model mis-specification.

### 2d. Accounting for all known physical restrictions

Every restriction from the experiment protocol is enforced as follows:

| Restriction | Enforcement strategy |
|-------------|----------------------|
| γ = 65 MHz, γ_φ = 40 MHz (fixed, not free) | Entered as constants in every `WGMEmitterSystem.add_emitter()` call |
| κ(step) fixed per trace | Linearly interpolated from `resonance_pos_Q_info.txt`; set as `kappa` argument per step |
| N=4, n_cav=4, ss_method="mesolve", parallel=False | Fixed `WGMEmitterSystem` constructor arguments throughout all phases |
| Mask [−500, +150] ps | Applied to τ array before computing χ² at every optimizer call |
| τ_0 ∈ [−80, +80] ps | Hard DE bound; initialized from phenomenological fit estimate |
| Normalization (A) and background (c_bg) | Profiled analytically (2×2 closed-form) at every χ² evaluation |
| IRF convolution σ = 115 ps | Applied to g(2)_sim (Gaussian kernel, physical units) before comparison |
| 2:1 binning → ~20 ps/bin | Applied once during pre-processing before any fitting |
| Simulate over ±2 ns | taulist spans [0, 2.174 κ⁻¹] = [0, 2 ns × κ_ref] |
| g_bs bounded by transmission | Hard DE upper bound 0.5κ; additionally verified by Lorentzian fit to `transmission_start.dat` and `transmission_end.dat` |
| Background fitting | c_bg profiled analytically; cannot be zero-locked or fixed |

### 2e. Analysis sequence

1. **Phenomenological fit** (all 12 full traces) → τ_0 per-trace estimates (DE seeds), dark-state lifetime, normalization sanity check.
2. **Model selection** (trace 1, all 8 models, DE with `popsize=3`, `maxiter=5`) → AICc and ε_chiral ranking.
3. **Top-model refinement** (trace 1, tight-bounds DE) → precise parameter estimates as global-fit seed.
4. **Global fit** (12 traces, top model, Nelder-Mead + Pool(7)) → global parameters and cross-step chirality trend.

### 2f. Assumption sensitivity

After model selection, the following hyperparameter robustness checks are applied to the top model: (a) IRF width: refit with σ = 100 ps and 130 ps; (b) mask boundary: shift to [−450, +200] ps; (c) ω_j bounds: expand to ±3κ. Any fitted parameter that shifts by more than 1.5× its DE population spread (IQR of the final-generation top 10% of individuals, used as a proxy for uncertainty) under these changes is reported as sensitive. These checks require at most one additional model run (~11 min) and are performed post-hoc.

---

## Step 3 — Model Evaluation and Ranking

### 3a. Fit-quality metric: corrected AIC (AICc)

For each model M_k with k free parameters (i.e., DE dims, after profiling A and c_bg):

    AICc_k = χ²_min(M_k) + 2k + 2k(k+1)/(n − k − 1)

where n ≈ 167 unmasked bins. AICc is preferred over BIC for n/k < 40 [Burnham & Anderson 2002]; with n = 167 and k_max = 14, n/k ≈ 12, firmly in the AICc regime.

**ΔAIC_k = AICc_k − min_j(AICc_j):**
- ΔAIC < 2 → substantial support (competitive with best model)
- ΔAIC 2–10 → some support
- ΔAIC > 10 → effectively ruled out

Report χ²_red = χ²_min / (n − k) per model.

### 3b. Physical validity checklist

| Check | Pass criterion |
|-------|---------------|
| All g_j within [0.05, 0.4]κ | No parameter at boundary |
| All ω_j within scan range ± 1.5κ | All emitters reachable by scan |
| g_bs ≤ 0.5κ (transmission bound) | Within transmission constraint |
| Cooperativity C_j = 4g_j²/(κγ) ∈ [0.01, 12] | Consistent with weak-to-intermediate coupling across the allowed g range; C > 12 would indicate g_j > 0.42κ, outside the physical bound |
| P within [0.02, 0.4]κ | Within physical pump range |
| χ²_red ∈ [0.5, 2.0] | Not dramatically over- or under-fitting |

**Validity score V_k = (# checks passed) / 6 ∈ [0, 1].** Models with V_k < 0.5 are excluded from the primary ranking as "physically suspect." Among valid models, **AICc alone determines ranking** — no arbitrary weighting factor is applied. Validity flags are reported alongside AICc in all comparison tables.

### 3c. Definition of success

A result is **decisive** when all of the following hold:
1. The top model has ΔAIC > 10 over all models with uniform φ (M0, M2) — establishing that phase disorder is required.
2. The top model has ΔAIC > 2 over all competing models with fewer disorder parameters — identifying which disorder sources are necessary vs. redundant.
3. ε_chiral < 0.20 for the top model (chirality fidelity within 20%; see 3d).
4. χ²_red ∈ [0.8, 1.5] for the top model.
5. The global fit reproduces the monotonic decrease of C_int from step 1 to step 12.

**Parameter values inconsistent with prior literature:** g_j < 0.05κ (coupling too weak to be observable in transmission); g_bs > 0.5κ (would produce a doublet in transmission inconsistent with observed single-Lorentzian); C_j > 12 (outside the allowed g range); P < 0.02κ or P > 0.4κ (outside the physical pump regime).

**Non-distinguishable model pairs:** M4 (phase + freq disorder, no g_bs) and M6 (phase + freq + g_bs) may be nearly degenerate if the fitted g_bs → 0. In this case, AICc will favor M4 (2 fewer parameters). The degeneracy is broken by: (i) if M6's fitted g_bs is consistent with the transmission residual noise floor and its ΔAIC is < 2 compared to M4, g_bs is physically meaningful; (ii) if g_bs hits the lower bound (zero), M4 is preferred. Similarly, M5 vs. M7 are distinguished by whether g_bs is supported.

### 3d. Chirality fidelity metric

Define A(τ) = g(2)(τ) − g(2)(−τ) over τ ∈ [150, 2000] ps (unmasked positive-τ side). The integrated chirality:

    C_int = ∫_{150 ps}^{2 ns} |A(τ)| dτ

Chirality residual:

    ε_chiral = |C_int(model) − C_int(data)| / C_int(data)

This scalar is independent of overall g(2) amplitude and specifically captures whether the model reproduces the magnitude of time-asymmetry. A model with low ΔAIC but high ε_chiral matches the dip shape but misses the key chiral physics — a red flag [motivated by arXiv:1608.00446 framework and arXiv:2504.09324 experimental context].

### 3e. Cross-step consistency (global fit metric)

After global fit: plot C_int(step) vs. step for data and top model. A correct model reproduces the trend of decreasing chirality from step 1 to step 12. Models M0–M3 (uniform ω) predict the same g(2) shape across all steps and are expected to fail this test. Report χ²_global = Σ_{steps} χ²_step and AICc_global with k = global physics params + τ_0.

### 3f. Visualization strategy

1. **g(2) overlay** per model vs. trace-1 data: masked region shaded; symmetric (flipped) data overlay to illustrate asymmetry.
2. **Asymmetry plot** A(τ) = g(2)(τ) − g(2)(−τ) for data and each model: clearly shows which models can/cannot reproduce chirality shape and magnitude.
3. **ΔAIC bar chart**: models on y-axis, ΔAIC on x-axis, colored by V_k (green: valid; red: physically suspect).
4. **Chirality-fidelity scatter**: ΔAIC vs. ε_chiral for all models. The ideal model sits at (low ΔAIC, low ε_chiral). This is the primary model-comparison figure.
5. **Cross-step chirality trend**: C_int(step) vs. step for data and top model(s).
6. **Parameter table**: top model parameters in both κ units and real (GHz/MHz) units, with IQR of the top-10% final DE population as uncertainty estimate.

---

## Summary of Novel Elements

- **Pump P in DE** (one additional dimension rather than an 8-point grid; eliminates the 8× simulation overhead — from 176 s to 22 s per optimizer call per worker — while keeping P free).
- **Analytical profiling of A and c_bg** at every optimizer call (closed-form linear algebra; zero additional simulation cost; analogous to linear marginalization).
- **Chirality fidelity metric ε_chiral** as a physics-specific scoring axis orthogonal to AICc [motivated by arXiv:1608.00446 and arXiv:2504.09324 experimental context].
- **AICc-primary ranking with validity-checklist veto** (no arbitrary weighting λ; validity flags are binary gates, not score modifiers; fully explainable to a reviewer).
- **Pool(7) inner parallelism for global fit** (parallelizes over the 12 traces within each Nelder-Mead call; outer optimizer is serial; respects the `parallel=False` constraint of the code).

---

## References

1. Lukin D.M. et al., "Mesoscopic cavity QED with phase-disordered emitters," arXiv:2504.09324 (2025). [Hamiltonian structure Eq. H^int with WGM CW/CCW modes and azimuthal phase φ_j; phase disorder → chirality in CW×CCW cross-correlation]
2. Lukin D.M. et al., "Two-Emitter Multimode Cavity QED in SiC," PRX 13, 011005 (2023). arXiv:2202.04845.
3. Wang J. et al., "Experimental Quantum Hamiltonian Learning," Nature Phys. 13, 551 (2017). arXiv:1703.05402. [Bayesian parameter inference in quantum systems]
4. Granade C. et al., "Hamiltonian Learning with Online Bayesian Experiment Design," arXiv:1806.02427 (2018). [Nuisance-parameter profiling in quantum inference]
5. Flynn B. et al., "Quantum Model Learning Agent," PRX Quantum (2022). arXiv:2112.08409. [Bayesian model comparison in quantum settings]
6. Lei M. et al., "Many-body cavity QED with driven inhomogeneous emitters," Nature 617, 271 (2023). arXiv:2208.04345. [Inhomogeneous TC model with spectral disorder {ω_j}; nanophotonic cavity platform — WGM mode structure not present]
7. Wierzchucka A., Piazza F., Claeys P.W., "Integrability, multifractality, and two-photon dynamics in disordered Tavis-Cummings models," PRA 109, 033716 (2024). arXiv:2312.03833. [Disordered TC formalism with per-emitter frequency disorder {ω_j}; supports use of spectral disorder in TC model]
8. Zeb M.A., "Analytical solution of the disordered Tavis-Cummings model and its Fano resonances," PRA 106, 063720 (2022). arXiv:2208.11990. [Analytical disordered TC model with per-emitter spectral and coupling disorder]
9. Anon., "Hamiltonian and Liouvillian learning in weakly-dissipative systems," arXiv:2405.06768 (2024).
10. Lodahl P. et al., "Chiral Quantum Optics," Nature 541, 473 (2017). arXiv:1608.00446. [Theoretical framework for directional emission; basis for chirality metrics]
11. Lodahl P. et al., "Chiral Quantum Optics: Recent Developments," PRX Quantum 6, 020101 (2025). arXiv:2411.06495.
12. Ostrowski L. et al., "Interference-induced directional emission from an unpolarized two-level emitter into a circulating cavity," PRA 105, 063719 (2022). arXiv:2109.09332. [Directional emission via interference in WGM cavity QED; context for chiral emission mechanisms]
13. Tian G. et al., "Disorder-induced strongly correlated photons in waveguide QED," PRL 135, 153604 (2025). arXiv:2510.11376. [Transition-frequency disorder induces photon blockade in waveguide QED with two-level emitters]
14. Dastidar M.G. et al., "Cooperative emission from two coupled solid-state quantum emitters," arXiv:2408.01799 (2024). [Dark-state bunching envelope and µs-scale lifetime in solid-state emitter g(2)]
15. Mazhorin G. et al., "Cavity-QED of a quantum metamaterial with tunable disorder," PRA 105, 033519 (2022). arXiv:2107.01420.
16. Burnham K.P. & Anderson D.R., "Model Selection and Multimodel Inference," Springer (2002). [AICc derivation; ΔAIC < 2 / 2–10 / > 10 thresholds for model support]
