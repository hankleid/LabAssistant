# Hamiltonian/Lindbladian Learning Plan for Single V_Si Cavity QED Lifetime Data

## System Summary

We are studying a **single V_Si (cubic site) color center** embedded in a SiC ring resonator
(Q = 7.21 × 10⁵, λ ≈ 916 nm). The cavity sustains two counter-propagating modes; the lifetime
is measured through one mode. The emitter has two optical transitions (spin-1/2 and spin-3/2)
separated by **1.075 GHz**. The measured TCSPC trace shows a non-single-exponential decay
(a visible "kink"), which we seek to explain physically.

**Known fixed parameters** (used as constraints throughout):

| Parameter | Value | Source |
|---|---|---|
| κ/2π (cavity linewidth) | ≈ 454 MHz | ω_c/Q, Q = 7.21 × 10⁵, λ = 916 nm |
| Δ_spin/2π (spin-transition splitting) | 1.075 GHz | Independent spectroscopy |
| γ_free/2π (free-space decay rate) | ~21–143 MHz | τ_free = 7–11 ns, V_Si literature [2.1, 2.4] |
| τ_ISC,slow | ~160–220 ns | V_Si ISC metastable doublet [3.3, 4.1] |

**Data:** 901 time bins, 10 ps/bin, 9 ns window, Poissonian photon-counting statistics (peak
~108 ungated counts), background ~1.6 counts (t > 7 ns). The Ungated channel is the primary
fit target.

---

## Step 1 — Candidate Hamiltonian/Lindbladian Models

### Motivation

The "kink" in the lifetime decay can arise from several distinct physical mechanisms. We
enumerate all physically plausible candidate models, ordered from simplest (fewest terms) to
most complex. Each model is defined by its Hamiltonian H and Lindblad jump operators {L_k},
i.e., the GKSL master equation:

    dρ/dt = -i[H, ρ] + Σ_k γ_k ( L_k ρ L_k† − ½{L_k† L_k, ρ} )

We consider both Hamiltonian and effective-rate (rate-equation) descriptions where the
Lindbladian limit is valid. The primary physical phenomena guiding the model list are drawn
from the color-center community's priorities: coupling strength, number of active transitions,
spin dynamics, spectral diffusion, and counter-propagating mode effects.

---

### Model Library

**Model 0 — Single Exponential (null hypothesis)**
- H = 0; L = {√γ₁ σ⁻}
- Predicts: P(t) = A e^(−Γ₁t) + B (background)
- Tests: Is there anything interesting at all?
- Physical scenario: Emitter far off-resonance; no Purcell enhancement.

**Model 1 — Purcell-Enhanced Single Decay (Weak-Coupling JC, one transition)**
- H = g(a†σ⁻ + aσ⁺) + Δ_c a†a; L = {√κ a, √γ σ⁻}
- In the weak-coupling/Purcell regime (κ > 2g): effective enhanced rate
  Γ_eff = γ + 4g²κ / (κ² + 4Δ_c²)
- Predicts: single exponential with Purcell-modified rate (g and Δ_c as free parameters)
- Physical scenario: One spin transition is cavity-resonant; the other is too far off-resonance
  to matter.

**Model 2 — Two Optical Transitions at Different Purcell Rates (primary biexponential hypothesis)**
- Two two-level systems, each coupling to the same cavity mode:
  H = Σᵢ₌₁² [gᵢ(a†σᵢ⁻ + aσᵢ⁺) + Δᵢ σᵢᶻ]
  L = {√κ a, √γ₁ σ₁⁻, √γ₂ σ₂⁻}
- Constraint: Δ₂ − Δ₁ = 1.075 GHz (fixed by spin splitting)
- This collapses to a rate-equation system in weak coupling:
  P(t) = A₁ e^(−Γ_eff,1 t) + A₂ e^(−Γ_eff,2 t)
  where Γ_eff,i = γᵢ + 4gᵢ²κ / (κ² + 4Δᵢ²)
- Physical scenario: Both spin transitions are driven; cavity is resonant with one.
  Off-resonant transition (Δ ≈ 1.075 GHz >> κ/2π ≈ 454 MHz) is barely Purcell-enhanced,
  creating a fast (cavity-resonant) and slow (near-free-space) component.
- **This is considered the primary null-physics hypothesis for the kink.**

**Model 3 — Strong-Coupling Jaynes-Cummings (single transition, vacuum Rabi oscillations)**
- Same H as Model 1 but in the regime 4g > κ + γ (strong coupling criterion)
- Predicts: oscillatory decay at vacuum Rabi frequency ~2g, damped by (κ+γ)/2
  P(t) ∝ e^(−(κ+γ)t/4) [cos(Ωᴿt) + ...]  where Ωᴿ = √(g² − (κ−γ)²/16)
- Physical scenario: The emitter is strongly coupled; Rabi oscillations appear as an
  oscillatory modulation of the lifetime trace [3.6].
- Note: Requires g/2π ≳ 50 MHz (plausible given Lukin et al. [2.2]: g/2π = 202 MHz in SiC).

**Model 4 — Strong-Coupling JC + Second Spin Transition (combined oscillation + biexponential)**
- Extends Model 3: first transition in strong coupling (oscillatory), second transition
  in weak coupling (simple exponential at ~free-space rate)
- Predicts: oscillatory decay superimposed on a slower exponential baseline
- Physical scenario: Most complete single-emitter picture if strong coupling is achieved.

**Model 5 — ISC Shelving + Purcell Decay (intrinsic V_Si multilevel structure)**
- Three-level (or five-level) rate model: |Excited quartet⟩ → |Ground⟩ (rate Γ_rad) AND
  |Excited quartet⟩ → |Metastable doublet⟩ (rate Γ_ISC), |Metastable⟩ → |Ground⟩ (rate Γ_slow)
- L = {√Γ_rad σ⁻, √Γ_ISC σ_ISC, √Γ_slow σ_slow}
- Cavity modifies only Γ_rad via Purcell effect [3.4]
- Predicts: P(t) = A e^(−(Γ_rad + Γ_ISC)t) + B e^(−Γ_slow t)  [B term appears as flat background
  in 9 ns window since τ_slow ~ 160–220 ns >> 9 ns]
- Physical scenario: Kink from ISC population trapping. The slow component would appear as
  a nearly constant offset within the measurement window.

**Model 6 — Spectral Diffusion (stochastic detuning)**
- Emitter jumps between two detuning states (on-resonance Δ=0 and off-resonance Δ=Δ_SD)
  at rate γ_SD. Rate equations in the fast/slow diffusion limits [2.8]:
  Fast (γ_SD >> Γ_eff): motional narrowing → single effective rate
  Slow (γ_SD << Γ_eff): frozen disorder → biexponential with weights set by occupation fractions
  Intermediate: non-exponential decay with characteristic timescale ~ 1/γ_SD
- Predicts: in slow diffusion limit, P(t) ≈ p₁ e^(−Γ_on t) + p₂ e^(−Γ_off t), kink at t ~ 1/γ_SD
- Physical scenario: Emitter drifts spectrally during the measurement, sampling both resonant
  and off-resonant decay rates.

**Model 7 — Counter-Propagating Mode Coupling (ring resonator specifics)**
- Ring resonator: two degenerate modes (CW, CCW) with inter-mode backscattering rate h
  H = g(a_CW† σ⁻ + h.c.) + g(a_CCW† σ⁻ + h.c.) + h(a_CW† a_CCW + h.c.)
  L = {√κ_ext a_CW, √κ_ext a_CCW, √κ_int a_CW, √κ_int a_CCW, √γ σ⁻}
  (detection through one mode only)
- Effective coupling to measurement port is modified by backscattering; may create interference
  between decay paths seen through one mode [2.2].
- Physical scenario: Chirality or mode-splitting from backscattering creates two effective
  decay rates visible in the single-mode measurement.

---

### Model Selection Strategy

Begin with Models 0→2 (increasing complexity, fewest new parameters). Progress to Models 3–7
only if simpler models fail statistically. Models can be combined (e.g., Model 4 = 3+2).
This forms a natural Bayesian model space for exploration (following the QMLA framework [1.4]).

---

## Step 2 — Fitting Each Model to Experimental Data

### 2a. Forward Model and Likelihood

For each candidate model, compute the predicted photon count in bin i as:

    λᵢ(θ) = I₀ · [P_model(t; θ) * IRF(t)] |_{t=tᵢ} + B

where:
- θ = model parameter vector
- I₀ = overall amplitude (free parameter per fit)
- IRF = instrument response function (see §2b)
- B = background (estimated from t > 7 ns region: mean ≈ 1.6 counts; treated as fixed offset)
- P_model(t; θ) = normalized population decay predicted by the Lindbladian

Since the data are **Poissonian photon counts**, we use the **Poissonian log-likelihood**:

    ln L(θ) = Σᵢ [ nᵢ ln λᵢ(θ) − λᵢ(θ) ]   (sum over 901 bins)

This is the correct likelihood for TCSPC data [3.2]. Gaussian/chi-squared fitting is
inappropriate for bins with < 10 counts (which constitute the majority of the tail).

### 2b. Instrument Response Function (IRF)

The 10 ps bin width can resolve features if the IRF width is comparable. The rising edge of
the excitation peak in the data (bins 0–~0.64 ns relative time) encodes the IRF convolved
with the onset dynamics. We extract the IRF empirically by fitting the rising edge of the
excitation peak to a Gaussian or one-sided exponential-Gaussian convolution. The IRF width
is then a fixed or lightly-constrained input to all subsequent model fits, not a free parameter.

### 2c. Parameter Estimation: Bayesian MCMC

We use **Bayesian inference via Markov Chain Monte Carlo (MCMC)** to sample the posterior:

    P(θ | data) ∝ L(data | θ) × π(θ)

Prior distributions π(θ) encode **physical validity constraints**:

| Parameter | Prior Type | Constraint |
|---|---|---|
| κ/2π | Delta or narrow Gaussian | Fixed at 454 ± 5 MHz from Q measurement |
| Δ₂ − Δ₁ | Delta | Fixed at 1.075 GHz (spin splitting) |
| g/2π | Log-uniform | [1 MHz, 500 MHz] — literature range for V_Si in SiC [2.1, 2.2] |
| γ/2π | Log-uniform | [14 MHz, 143 MHz] — free-space lifetime 7–11 ns [3.3] |
| Γ_ISC/2π | Log-uniform | [1 MHz, 50 MHz] — V_Si ISC rate literature [4.1] |
| γ_SD | Log-uniform | [0.01/ns, 10/ns] — unknown, broad prior |
| Amplitudes A₁, A₂ | Dirichlet | Positive, sum ≤ 1 |
| Background B | Gaussian | 1.6 ± 0.5 counts (from pre-signal region) |

For models with analytical population dynamics (Models 0, 1, 2, 5), MCMC is fast
(Hamiltonian Monte Carlo via `NumPyro` or `emcee`). For Models 3–4 (JC oscillations)
and 7 (two-mode ring), we solve the Lindblad master equation numerically using QuTiP
with a truncated Fock space (n_max = 5 photons sufficient in weak/moderate coupling).
For Model 6 (spectral diffusion), we solve the stochastic rate equations analytically
in the two limiting cases and numerically in the intermediate regime.

**Addressing the low-count regime:** With peak ~108 counts and a 9 ns window, total
integrated photons are ~O(1000). This is a moderate-statistics regime. Bayesian methods
with physical priors substantially improve parameter estimation compared to pure MLE [1.1].

### 2d. Physical Validity Scoring (Per-Model, Per-Fit)

After MCMC, **every fitted parameter is checked against physical bounds**:

1. **Hard bounds**: Any posterior sample violating g > 0, κ > 0, γ > 0, or amplitude < 0
   is rejected during MCMC (enforced by prior support).

2. **Literature consistency score S_phys** (continuous, 0–1): For each parameter θ_k, compute
   the fraction of the marginal posterior that falls within the physically established range
   from literature (e.g., g/2π ∈ [50, 300] MHz for V_Si in SiC [2.2]):

       S_phys = Π_k P(θ_k ∈ [θ_k,min, θ_k,max] | data)

   This is a soft score: models with posteriors concentrated in physically unreasonable regions
   are penalized even if their fit quality is formally good.

3. **Strong-coupling self-consistency**: For Models 3–4, check whether fitted g satisfies the
   strong-coupling criterion (4g > κ + γ). If the posterior strongly prefers g below this
   threshold, Models 3–4 reduce to Models 1–2 and are redundant.

---

## Step 3 — Model Evaluation and Ranking

### 3a. Bayesian Model Comparison (Primary Metric)

The primary ranking metric is the **log-Bayesian evidence** (log-marginal likelihood):

    ln Z_m = ln ∫ L(data | θ) π(θ) dθ

Computed via **thermodynamic integration** (parallel tempering chains at β = 0→1) or
**nested sampling** (using `dynesty`). The Bayes factor between models M_i and M_j:

    K_ij = Z_i / Z_j

|K_ij| interpretation follows Jeffreys' scale: K > 100 = decisive evidence for M_i.
This metric naturally penalizes over-parameterized models through the Occam's razor
effect embedded in Bayesian marginalization [1.3, 1.4].

### 3b. Information-Theoretic Penalty (Cross-Check)

As a cross-check on evidence estimates, compute **AIC and BIC** from the maximum-likelihood
fit for each model:

    AIC = 2k − 2 ln L_max
    BIC = k ln(N_bins) − 2 ln L_max   (N_bins = 901)

Lower is better. ΔBIC > 10 is considered very strong evidence against the higher-BIC model.
BIC is consistent with Bayesian evidence in the large-N limit and provides a fast sanity check.

### 3c. Residuals Diagnostics

For each model's maximum-posterior fit, compute **Poisson-normalized residuals**:

    rᵢ = (nᵢ − λᵢ) / √λᵢ

A good fit should have: mean(r) ≈ 0, std(r) ≈ 1, and no autocorrelation structure.
Quantitative tests: (i) **Runs test** for temporal structure in residuals, (ii) **chi-squared
test** (Σ rᵢ² ~ χ²(N_bins − k)). A model that passes information-theoretic metrics but
shows structured residuals (e.g., a systematic oscillation not captured) is penalized.

### 3d. Physical Validity Integration into Final Score

The **composite ranking score** for each model is:

    Score_m = ln Z_m + ln S_phys,m

where S_phys,m is the log of the physical validity score from §2d. This additive combination
is motivated by treating S_phys as an additional prior (Bayesian consistency):
a model with excellent fit quality but physically unreasonable parameters (e.g., g/2π = 5 GHz)
is explicitly down-weighted.

### 3e. Final Ranked Output

Present results as a ranked table:

| Rank | Model | ln Z | ΔBIC | S_phys | Residual pass? | Composite Score | Interpretation |
|---|---|---|---|---|---|---|---|
| 1 | Model X | ... | 0 | ... | Y | ... | ... |
| 2 | Model Y | ... | +Δ | ... | Y | ... | ... |
| ... | | | | | | | |

The **top-ranked model** is the one with the highest composite score AND passing residual
diagnostics. If two models are within K < 3 Bayes factor, they are considered statistically
indistinguishable and both are reported with caveats.

---

## Literature Grounding and Attribution

The proposed methods draw on and adapt the following works:

| Method | Source |
|---|---|
| Sequential Monte Carlo / Bayesian Hamiltonian learning | Granade et al. 2012 [arXiv:1207.1655]; Wiebe et al. 2014 [arXiv:1309.0876] |
| Bayes factor model comparison (Exp. QHL) | Wang et al. 2017 [arXiv:1703.05402] |
| QMLA agent-based model search + Elo ranking | Flynn et al. 2021 [arXiv:2112.08409] |
| rj-MCMC open quantum system learning | Wallace et al. 2024 [arXiv:2410.17942] |
| oQMLA Lindblad learning + RMSE fitness | Fioroni et al. 2025 [arXiv:2501.05350] |
| Quantum AIC/BIC | Yano & Yamamoto 2023 [arXiv:2304.10949] |
| V_Si in SiC cavity QED (baseline parameters) | Lukin et al. 2022 [arXiv:2202.04845]; 2025 [arXiv:2504.09324] |
| V_Si ISC rates (biexponential origin) | Younesi et al. 2026 [arXiv:2602.14818]; Dong et al. 2019 [arXiv:1811.01398] |
| Non-exponential decay in cavity QED (theory) | Krimer et al. 2014 [arXiv:1306.4787] |
| Biexponential TCSPC fitting framework | Cleveland et al. 2024 [arXiv:2408.12192] |
| Anomalous Purcell decay, inhomogeneous broadening | Solomon et al. 2024 [arXiv:2309.16641] |
| V_Si spin dynamics characterization | Liu et al. 2023 [arXiv:2307.13648] |
| TC breakdown, disorder, dark states | Blaha et al. 2021 [arXiv:2107.04583]; Wierzchucka et al. 2023 [arXiv:2312.03833] |
| JC oscillations in lifetime (QD experiment) | Kuruma et al. 2018 [arXiv:1803.05618] |

**Novel contributions of this plan** (not directly from prior literature):
- Fixing κ and Δ_spin as hard constraints within the Bayesian priors (exploiting our specific
  knowledge of Q and spin structure), reducing the effective parameter space.
- The composite score S = ln Z + ln S_phys integrating Bayesian evidence with a literature-
  informed physical validity prior in a single unified ranking metric.
- Application of QMLA-style model search to a ring-resonator, two-counter-propagating-mode
  geometry with a two-optical-transition emitter (V_Si), which has not been explicitly treated
  in prior QMLA literature.
