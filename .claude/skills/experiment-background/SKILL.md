---
name: experiment-background
description: "Reference knowledge about the V_Si cavity QED experiment: system, data, chirality, analysis goals."
---
**Analysis goals**
- Which physical models best describe the data?
- What is the disorder of this cavity QED system?
- Determine exactly which effects must be present in order to best to explain the data.

**What is known about the experimental system:**
- The data provided is a cross-correlation measurement g(2), one arm reading out the clockwise mode of a 4H-SiC disk resonator, and the other arm reading out the counter-clockwise mode of the disk. All data is from the same disk measured at the same position.
- MULTIPLE color centers are embedded in the disk resonator, and its the emitters' emission (from excitation with 780 nm laser) which is coupled to the disk mode(s) and which we are cross-correlating.
- The color centers are the V2 Si defects (consider only cubic k-V_Si), emission at ~916 nm, and we are only considering one optical transition per emitter here.

**Information about the data:**
- This measurement is a STEADY STATE g(2) cross-correlating the CW and CCW modes of the disk resonator, recorded at 12 points while the disk resonance wavelength is swept by gas tuning (`experimental_data/g2_data.npz`). The actual tau axis might be offset from the tau array by -80 to 80 picoseconds, since the MZI arms are not precisely calibrated, and needs to be fit.
- The cavity resonance wavelength and quality factor is reported at the beginning of the gas tuning and at the end (`experimental_data/resonance_pos_Q_info.txt`), which you should use for kappa. Assume a linear progression of the resonance wavelength and quality factor over 12 steps between the first measurement and the last. Emitters may be resonant with any wavelength within that cavity sweep.
- The counts are integrated over many minutes or hours per g(2).
- The auto-correlation g(2)s (not included here) are indeed symmetric (no chirality).

**Problem statement**
This high Q SiC disk containing multiple (anywhere from 2 to 10) emitters produces g(2) with some CHIRALITY or ASYMMETRY when photons from the two nearly-degenerate CW/CCW modes are cross-correlated. This asymmetry around tau=0 is unusual for this kind of system. It is likely caused by some DISORDER in the cavity-emitters system, for example:

    - Coupling factor 'g'.
    - Cavity-emitter detuning '\Delta'. (Caused by inhomogeneous broadening AND/OR spectral diffusion.)
    - Azimuthal phase '\phi' between emitter sites along the WGM.

are all quantities which all vary from emitter to emitter and contribute to the global dynamics. These are global parameters and do NOT change from one g(2) to another. Further, backscattering ('g_{bs}') between the otherwise degenerate CW and CCW cavity modes likely also plays a role. Because the interaction with the cavity is so important here, the g(2) is taken for 12 different cavity resonance wavelengths as it is swept (presumably) across several emitters. At the beginning of the gas tuning, the chirality is strong, but by the most "red" g(2), the chirality/asymmetry is mostly gone.

Quantifying every aspect of the disorder and DETERMINING THE MAIN SOURCE(S) of this chirality or asymmetry is your main objective. Note that ALL sources of disorder are likely influencing the chirality, especially in the presence of cw-ccw backscattering. Your goal is to determine: are some parameters necessary to explain the chirality but others not so much? Only base your hypotheses on results in the literature whose simulation/experimental setting is comparable (same simplifications/assumptions) to the one we simulate in `g2_calculations.py`. Otherwise, assume nothing. By the end of the analysis, your solution should reproduce the g(2) traces and the trend of the chirality across cavity-detuning positions. Pick your candidate models carefully to achieve this goal. 

**How to manage analysis complexity**:
Look at the full data first (g(2) trace 0). You will see some bunching as a result of metastable shelving, and a steep dip in the g(2) around tau=0. Use the full data to get a guess/bounds for future determination of tau0. Starting point for the fit, which you are free to change: Fit `g(2)_phenom = [1-A*exp(-|tau-tau0|/tf) + C*exp(-|tau-tau0|/ts)] conv IRF + bg` over the ±6 µs range.

Combined with a convolution with the IRF (Gaussian, sigma = 115 ps; edge-value padding convolution), the final model should predict the data well and reveal the asymmetry around tau=0.

See how the chirality shifts over the 12 data. The final step should be nearly symmetric. Make sure your choice of chirality assessment reveals a (nearly) monotonic increase in symmetry from most chiral (step 1) to least chiral (step 12).

Start with ONE g(2) measurement only. Use the most chiral g(2) (first step of 12). Use only this single g(2) to determine the most appropriate candidate physical model and most likely parameter values. Then, for the leading model only (or a leading subset of the candidate models), use the full dataset to derive the final parameter values. Further specific methodological details to achieve this analysis are up to you and you must specify them. The statistics methods must be appropriate and straightforward.

A steady state g(2) simulation tool is outlined for you under `tools/`, with simulation timing information also reported under `tools/`. To use this simulation code, it will be helpful to keep all relevant parameters in units of kappa (and kappa=1 is used in the simulations), and then only convert back to real values when interpreting results. Emitter spectral positions and cavity wavelength should be implemented relative to the midpoint frequency of the cavity scan and in units of kappa. E.g.: omega = -0.3 is -0.3*kappa GHz from the reference frequency (midpoint of the scan).

Simulate with N=4 emitters. Your statistics methods should keep in mind the amount of time required for one N=4 simulation, which is provided to you in `tools/timing.txt`. This timing is given when paralellizing the positive/negative tau lists (x2 speedup) but you should not parallelize at that step.

Any one full evaluation of a model (including fitting) must finish within 5 hours of computation time. Reduce sampling to achieve this time restraint.

**Note about processing**: 
The raw g(2) data hould be normalized by the mean counts at the outer edges. The only further correction required for the qutip g2 simulation is for uncorrelated background photons (dark counts, stray light) which dilute the quantum signal. This gives the background dilution model:

    g2_measured(τ) = α * (g2_sim(τ) - 1) + 1

Profile α analytically at each cost function evaluation as a weighted regression:

    x_i = g2_sim(τ_i) - 1
    y_i = g2_data(τ_i) - 1
    α = Σ(w_i * x_i * y_i) / Σ(w_i * x_i²)    [clip to [0, 1]]
    chi2 = Σ w_i * (y_i - α * x_i)²

Note that tau0 is a fitting parameter and should not shift the data itself. If you shift the data itself, you will find the mask region will no longer be correct, which must be avoided.

You must MASK OUT and IGNORE the region from tau = [-630, 60] ps in all the raw data. Eg: `gap_mask = (taulist >= r[0]) & (taulist <= r[1]);counts_plot[gap_mask] = np.nan`. Your goal is to fit the dip of this g(2) without the blip feature in that tau region from disrupting the findings.

You will see an incoherent pump rate as one of the simulation parameters. This pump does change the g2, but it's not one of the important disorder-causing parameters. Therefore you need to find a way to profile out this value or fit it in an efficient way that doesn't detract from determining the values for the other more interesting parameters.

Importantly, the quantum simulations and final model fits should be over **-2 ns to 2 ns** ONLY to prioritize only the chiral features. Note that the simulation tau is also normalized to kappa. You should bin the raw data 2:1 so as to minimize simulation points while still maintaning the quality of the data. You must propose a parallelization strategy to minimize simulation time as well. You have access to 7 CPU cores. Make sure the parallelization method is appropriate (given `tools/g2_computation.py`) and feasible, considering both time expenditure and RAM usage (which should remain under 3 GB). Use n_cav = 4 and ss_method = "mesolve", and parallel = False so that you can use your own parallelization method.

It is ESSENTIAL that ALL RESULTS CONVERGE before making any judgements that carry over to subsequent analysis steps. Keep track of your progress and be able to pick up from where you left off, so that you can allocate more compute easily and converge the results without having to start over.

**IMPORTANT Visualization Task**
You must come up with a metric or strategy for comparing all the different effects you decide to model. Which effects are required to model the system well and which are not? Which effect(s) explain the asymmetry/chirality in the data best? This metric or strategy should have a straightforward visualization that you provide as the analysis progresses. The result of including each specific physical effect should be well-illustrated. Make sure real values of paramaters are calculated from the normalized quantity and recorded. Be sure to illustrate how the models compare to the real data.


**IMPORTANT Physical Considerations**
- The experiment should be modeled as continuous incoherent above-resonant pumping; compute g(2)(tau) from the steady-state density matrix.
- Assume pure dephasing is 40 MHz and the intrinsic emitter linewidth is 65 MHz -- these are not free parameters. However, you must allow some wiggle room for the pure dephasing without including it as a full free parameter.
- Adhere to the following parameter bounds:
    - g: [0.0, 0.4] kappa
    - omega (emitter spectral position): should cover the full range of the cavity scan, plus outside the range to the extent that the cavity at the edge of the scan could feasibly still interact (you decide the exact bound).
    - phi: [0, 2pi)
    - cw/ccw backscattering: ?. `experimental_data/resonance_pos_Q_info_GHz.txt` shows the resonance information, which was determined from transmission measurements before and after the cavity scan (`transmission_start.dat`, `transmission_end.dat`). Use the transmission data to determine a maximum bounds for backscattering. You will see the dip is fit well with a single Lorentzian (so the backscattering might be small) but you must determine how much backscattering is present and consistent with the data.
    - pump: [0.02, 0.4] kappa