# Shared data loading, preprocessing, and cavity parameter utilities for the V_Si cavity QED analysis.

import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

_DATA_DIR = Path(__file__).parent.parent / "experimental_data"


def load_g2_data(path=None):
    """Load raw g(2) coincidence data; applies the fixed +180 ps MZI arm correction."""
    if path is None:
        path = _DATA_DIR / "g2_data.npz"
    d = np.load(path)
    times = d["times"] + 180   # ps; corrects for MZI arm imbalance
    matrix = d["matrix"]       # shape (12, 600000), int32 photon counts
    print(f"loaded {path}  (matrix {matrix.shape})")
    return times, matrix


def load_resonance_info(path=None):
    """Parse cavity resonance wavelength (nm) and Q-factor from before/after scan file."""
    if path is None:
        path = _DATA_DIR / "resonance_pos_Q_info.txt"
    result = {}
    with open(path) as f:
        lines = [l.strip() for l in f if l.strip()]
    for line in lines[1:]:
        parts = line.split()
        label, wavelength_nm, Q = parts[0], float(parts[1]), float(parts[2])
        result[label] = {"wavelength_nm": wavelength_nm, "Q": Q}
    return result


def load_resonance_info_ghz(path=None):
    """Parse cavity center frequency (GHz), Q-factor, and kappa (GHz) from the GHz info file."""
    if path is None:
        path = _DATA_DIR / "resonance_pos_Q_info_GHz.txt"
    result = {}
    with open(path) as f:
        lines = [l.strip() for l in f if l.strip()]
    for line in lines[1:]:
        parts = line.split()
        result[parts[0]] = {
            "center_frequency_GHz": float(parts[1]),
            "quality_factor": float(parts[2]),
            "kappa_GHz": float(parts[3]),
        }
    return result


def load_lifetime_data(path=None):
    """Load time-resolved photoluminescence (lifetime) data for the V_Si emitters.
    Expected file: experimental_data/lifetime_data.npz with keys 'times' (ps) and 'counts'.
    Raises FileNotFoundError if no lifetime data file is present."""
    if path is None:
        path = _DATA_DIR / "lifetime_data.npz"
    if not Path(path).exists():
        raise FileNotFoundError(
            f"Lifetime data not found at {path}. "
            "Provide a .npz file with keys 'times' (ps, 1-D) and 'counts' (1-D)."
        )
    d = np.load(path)
    times  = d["times"].astype(float)   # ps
    counts = d["counts"].astype(float)
    print(f"loaded {path}  (lifetime: {len(times)} bins)")
    return times, counts


def get_cavity_params(n_steps=12):
    """
    Linearly interpolate cavity center frequency (GHz) and kappa (GHz) across n_steps.
    Returns dict with arrays of shape (n_steps,) and kappa_ref (mean kappa).
    """
    info = load_resonance_info_ghz()
    f0 = info["before_scan"]["center_frequency_GHz"]
    f1 = info["after_scan"]["center_frequency_GHz"]
    k0 = info["before_scan"]["kappa_GHz"]
    k1 = info["after_scan"]["kappa_GHz"]
    t = np.linspace(0, 1, n_steps)
    freq_ghz = f0 + t * (f1 - f0)
    kappa_ghz = k0 + t * (k1 - k0)
    kappa_ref = kappa_ghz.mean()
    omega_ref = freq_ghz.mean()   # midpoint of scan in GHz
    # cavity detuning per step, normalized to kappa_ref
    delta_c = (freq_ghz - omega_ref) / kappa_ref
    return {
        "freq_ghz": freq_ghz,
        "kappa_ghz": kappa_ghz,
        "kappa_ref": kappa_ref,
        "omega_ref_ghz": omega_ref,
        "delta_c": delta_c,      # shape (n_steps,), in kappa_ref units
    }
