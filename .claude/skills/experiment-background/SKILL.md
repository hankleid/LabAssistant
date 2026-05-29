---
name: experiment-background
description: "Reference knowledge about the V_Si cavity QED experiment: system, data file, optical transitions, possible physics."
---
**Analysis goals**
- Which physical models best describe the data?
- Is strong coupling present? (important)
- What is coupling "g" for this emitter-cavity system?
- Determine exactly which effects must be present in order to best to explain the data.

**What is known about the experimental system:**
- We are measuring a SINGLE color center in 4H-SiC. This was independently verified with a g(2) measurement (not included here).
- The color center is the V2 Si defect (consider only cubic k-V_Si), emission at ~916 nm.
- The V_Si has two optical transitions, one for the spin-1/2 state and one for the spin-3/2 state, separated by 1.075 GHz. The emitter may be in one spin state or the other at any given time. See more information below.
- The color center is embedded in a disk resonator and therefore coupled equally to two degenerate clockwise and counter clockwise optical modes. But the lifetime measurement is conducted through measuring photon statistics from a single mode.
- The cavity has a quality factor Q = 7.21e5 (721,000). Use Kappa = (327000)/Q * 2*np.pi.

**Information about the experiment:**
- This measurement is a time-resolved lifetime measurement. X-axis is time bin and Y-axis is counts.
- The excitation peak is present in the data, followed by the decay.
- The data you see is the result of repeating and aggregating the counts from this measurement many times.

**Problem statement**
Although we are certain to be measuring only one emitter, the lifetime data is not represented by a single exponential decay. Rather, there exists a kink, or bend, in the lifetime decay at t = ~2.5 to 3.5 ns FROM the start of the data returned by `load_timeresolved_data` (around 1.5 to 2.5 ns AFTER t0) which indicates interesting physics may be present overall.

The resulting lifetime measurement is in `experimental_data/lifetime_data.dat`. We preprocessed the data for you in `load_timeresolved_data`, so the onset of population buildup (start of the rise) happens sometime between t0 = [0, 2] ns relative to where I truncated the data. It's important your systems can model this rise and fall in addition to the decay, including the onset time t0. You must profile out the count magnitude (normalization) before optimizing. Additionally, because the counts will never be zero (due to noise), you also MUST fit a count_offset which gives a vertical offset to the model.

There are many possible explanations for the interesting lifetime decay shape, especially because you only have one data file to base your analysis on. This requires you to not only generate an exploratory list of possible Hamiltonian/Lindbladian systems to describe the system, but also creative ways of testing your hypothesis for each model. The ultimate goal is to assess all possible physics to understand what best fits the data and also reveal the relationship with *g*.


**IMPORTANT Visualization Task**
You must come up with a metric or strategy for comparing all the different effects you decide to model. Which effects are required to model the system well and which are not? Which effect(s) explain the kink in the data best? This metric or strategy should have a straightforward visualization that you provide as the analysis progresses. The result of including each specific physical effect should be well-illustrated here. Ultimately, you must also relate this to the coupling factor *g* in some way.


**IMPORTANT Physical Considerations**
- Spectral diffusion may be present in this system. There are multiple ways to model this. The rate of spectral diffusion is unknown but note that it tends to be larger when the emitter is integrated in nanophotonics. 
- If an emitter is strongly coupled to a cavity, we would expect to see Rabi oscillations in a single lifetime measurement. You should use the **kappa/4** definition for strong coupling.
- You may assume the laser pulse is a perfect delta function that instantaneously prepares the emitter in the excited state at t0 = [0, 2] ns (you must fit this excitation onset time) and plays no further role. No IRF modeling necessary.
- There may be backscattering between the two cavity modes.
- You must describe a method(s) for accounting for the two spin transitions, spin-1/2 and spin-3/2, which are 1.075 GHz apart. More information below.
- Multiple of the above mentioned effects may be present at once. Every model should consider EVERY permutation of possible effects, including spectral diffusion, so that we can isolate contributions from specific effects.
- Are there any other reasonably possible effects? Come up with at least 1 and include it in the PLAN.

**EVERY SINGLE PARAMETER in ALL MODELS must be bounded by physically meaningful numbers. Read the literature to check yourself. State bounds for every parameter in the PLAN.**

**Additional information about the spin transitions.**
You may assume any spectral diffusion shifts these transitions in tandem. Consult the energy structure of the V2 defect for more information. You MUST use the following information:
    - O1 (spin-1/2) transition QE = 0.34. Do NOT use gamma_01 as a free parameter - it should be fixed to the bulk value from literature.
    - O2 (spin-3/2) transition QE = 0.64. Do NOT use gamma_02 as a free parameter - it should be fixed to the bulk value from literature.
    - For the population 'p' ensure the bounds you choose are backed by literature.
    - Coupling 'g' for the two transitions should be equal to each other, since they have the same dipole moment.
    - If you include a single transition model, use the O1 transition. Again, don't fit gamma.