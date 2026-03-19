# Shared utilities for loading and parsing all experimental data files.

import json
import numpy as np
from pathlib import Path
from scipy.signal import find_peaks

C_NM_PER_NS = 2.99792458e8  # speed of light in nm/ns


def load_lifetime_data(path):
    """Load TCSPC lifetime data; returns time axis in ns and photon counts array (n_steps × n_bins)."""
    with open(path) as f:
        d = json.load(f)
    d = preprocess_lifetime_data(d)
    dt_ns = d["lifetime_resolution_picoseconds"] / 1000.0
    data = np.array(d["lifetime_data"], dtype=float)
    n_steps, n_bins = data.shape
    t_ns = np.arange(n_bins) * dt_ns
    return {
        "data": data,
        "t_ns": t_ns,
        "dt_ns": dt_ns,
        "n_steps": n_steps,
        "n_bins": n_bins,
        "integration_time_s": d["integration_time"],
        "lifetime_coord": d["lifetime_coord"],
    }

def preprocess_lifetime_data(_raw):
    _data_all = np.array(_raw["lifetime_data"], dtype=float)
    _data_all = _data_all[~np.all(_data_all == 0.0, axis=1)]   # remove all-zero traces
    bg_100 = _data_all[:, -100:].mean(axis=1)                  # per-trace background (1D)
    _data_all = _data_all - bg_100[:, np.newaxis]
    _data_all = _data_all[:110]                                 # first 110 non-zero traces
    # peak_bin = int(np.argmax(_data_all[75]))                    # peak of trace 75
    fit_bin_min, fit_bin_max = 1110, 1110 + 750 # 15ns fitting region
    _data_all = _data_all[:, fit_bin_min:fit_bin_max]                         # truncate all traces there
    _raw["lifetime_data"] = _data_all.tolist()
    return _raw


def load_fano_fits(path):
    """Load Fano fit parameters; returns per-step cavity wavelength (nm) and linewidth (nm)."""
    with open(path) as f:
        d = json.load(f)
    fp = d["fit_params_dict"]
    n_steps = len(fp)
    lambda_c = np.array([fp[str(s)]["x0"] for s in range(n_steps)])
    w_nm = np.array([fp[str(s)]["w"] for s in range(n_steps)])
    q_fano = np.array([fp[str(s)]["q"] for s in range(n_steps)])
    return {
        "lambda_c_nm": lambda_c,
        "w_nm": w_nm,
        "q_fano": q_fano,
        "n_steps": n_steps,
        "fit_params_dict": fp,
    }


def load_pl_spectrum(path):
    """Load off-resonant PL spectrum; returns wavelengths in nm and normalized intensity."""
    with open(path) as f:
        d = json.load(f)
    wl = np.array(d["wavelengths"])
    sp = np.array(d["spectra"])
    sp_norm = (sp - sp.min()) / (sp.max() - sp.min())
    return {
        "wavelengths_nm": wl,
        "spectra": sp,
        "spectra_norm": sp_norm,
        "int_time_s": d["int_time"],
    }


def load_spatial_map(path):
    """Load 2-D confocal PL scan; returns x/y axes (µm) and count array (n_x × n_y)."""
    with open(path) as f:
        d = json.load(f)
    x = np.array(d["x_axis"])
    y = np.array(d["y_axis"])
    counts = np.array(d["scan_data"])
    return {
        "x_um": x,
        "y_um": y,
        "counts": counts,
        "integration_time_s": d["integration_time"],
        "x_step_um": d["x_step"],
        "y_step_um": d["y_step"],
        "peak_finding_raw": d.get("peak_finding", {}),
    }


def extract_cavity_params(fano_fits_path):
    """
    Derive per-step cavity angular frequency (rad/ns) and half-linewidth kappa (rad/ns) from Fano fits.

    Convention: kappa is the HWHM of the cavity resonance in angular frequency.
    kappa/(2pi) [GHz] = c [nm/ns] * w_HWHM [nm] / lambda^2 [nm^2]
    The Fano fit 'w' parameter is the HWHM of the Lorentzian denominator,
    so FWHM_nm = 2*w and kappa/(2pi) = c * w / lambda^2.
    """
    fits = load_fano_fits(fano_fits_path)
    lam = fits["lambda_c_nm"]
    w = fits["w_nm"]
    omega_c = 2 * np.pi * C_NM_PER_NS / lam          # rad/ns
    kappa = 2 * np.pi * C_NM_PER_NS * w / lam**2     # rad/ns (HWHM)
    return omega_c, kappa, fits["lambda_c_nm"]


def extract_pl_peaks(pl_spectrum_path, wl_min_nm=618.0, wl_max_nm=623.0,
                     height_frac=0.08, min_distance_nm=0.3):
    """
    Find ZPL peak wavelengths and their amplitude ratio within the SnV spectral window.
    Returns sorted peak wavelengths (nm) and normalized peak heights.
    """
    spec = load_pl_spectrum(pl_spectrum_path)
    wl = spec["wavelengths_nm"]
    sp = spec["spectra_norm"]

    mask = (wl >= wl_min_nm) & (wl <= wl_max_nm)
    wl_r, sp_r = wl[mask], sp[mask]

    dw = np.median(np.diff(wl_r))
    min_dist_bins = max(1, int(min_distance_nm / dw))
    peaks_idx, props = find_peaks(sp_r, height=height_frac, distance=min_dist_bins)

    peak_wls = wl_r[peaks_idx]
    peak_heights = sp_r[peaks_idx]
    order = np.argsort(peak_wls)
    return peak_wls[order], peak_heights[order]


def estimate_emitter_count(spatial_map_path, center_um=None, mode_radius_um=1.5,
                           cluster_radius_um=0.2, count_threshold_frac=0.15):
    """
    Estimate the number of spatially distinct emitters inside the cavity mode.

    Searches for PL peaks within mode_radius_um of center_um (defaults to the
    map intensity-weighted centroid), then clusters peaks separated by less than
    cluster_radius_um to avoid double-counting a single bright spot.
    """
    smap = load_spatial_map(spatial_map_path)
    raw_pf = smap["peak_finding_raw"]
    if not raw_pf:
        return {"n_lower": 1, "n_upper": 3, "peak_coords": []}

    px = np.array(raw_pf["peaks_x_coords"])
    py = np.array(raw_pf["peaks_y_coords"])
    x_map = smap["x_um"]
    y_map = smap["y_um"]
    counts = smap["counts"]

    if center_um is None:
        w = np.maximum(counts, 0)
        cx = float(np.average(x_map, weights=w.sum(axis=1)))
        cy = float(np.average(y_map, weights=w.sum(axis=0)))
        center_um = (cx, cy)

    # Keep only peaks within the cavity mode footprint
    dist_from_center = np.sqrt((px - center_um[0])**2 + (py - center_um[1])**2)
    in_mode = dist_from_center <= mode_radius_um
    px, py = px[in_mode], py[in_mode]
    if len(px) == 0:
        return {"n_lower": 1, "n_upper": 1, "n_clusters": 0, "peak_coords": [], "center_um": center_um}

    def interpolate_count(x0, y0):
        ix = np.argmin(np.abs(x_map - x0))
        iy = np.argmin(np.abs(y_map - y0))
        return counts[ix, iy]

    peak_counts = np.array([interpolate_count(x, y) for x, y in zip(px, py)])
    threshold = peak_counts.max() * count_threshold_frac
    bright = peak_counts >= threshold
    bx, by, bc = px[bright], py[bright], peak_counts[bright]

    # Cluster spatially nearby bright peaks
    used = np.zeros(len(bx), dtype=bool)
    clusters = []
    for i in np.argsort(-bc):       # process brightest first
        if used[i]:
            continue
        dists = np.sqrt((bx - bx[i])**2 + (by - by[i])**2)
        members = dists <= cluster_radius_um
        clusters.append({
            "x_um": float(bx[i]),
            "y_um": float(by[i]),
            "count": float(bc[members].max()),
        })
        used[members] = True

    n = len(clusters)
    return {
        "n_lower": max(1, n),
        "n_upper": max(1, n),
        "n_clusters": n,
        "peak_coords": clusters,
        "center_um": center_um,
    }


def build_background_estimate(lifetime_data, t_min_ns=60.0, t_max_ns=80.0):
    """
    Estimate per-step background (dark counts) from a late-time flat region of each decay trace.
    Returns background counts per bin for each step.
    """
    t = lifetime_data["t_ns"]
    data = lifetime_data["data"]
    mask = (t >= t_min_ns) & (t <= t_max_ns)
    if mask.sum() == 0:
        return np.zeros(data.shape[0])
    return data[:, mask].mean(axis=1)


# ── Demo ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    base = Path(__file__).parent.parent / "experimental_data"

    lt = load_lifetime_data(base / "gas_tuning_lifetime_data.json")
    print(f"Lifetime data: {lt['n_steps']} steps × {lt['n_bins']} bins, dt={lt['dt_ns']*1000:.0f} ps")
    print(f"  Total counts step 0: {lt['data'][0].sum():.0f}")

    omega_c, kappa, lam = extract_cavity_params(base / "gas_tuning_cavity_resonance_fits.json")
    kappa_ghz = kappa / (2 * np.pi)  # GHz = 1/ns
    print(f"Cavity wavelength range: {lam.min():.2f} – {lam.max():.2f} nm")
    print(f"kappa/(2pi) range: {kappa_ghz.min():.1f} – {kappa_ghz.max():.1f} GHz")

    peak_wls, peak_heights = extract_pl_peaks(base / "off_resonant_PL_spectrum.json")
    print(f"PL ZPL peaks: {peak_wls} nm  (rel. heights: {peak_heights.round(3)})")

    lt_meta = load_lifetime_data(base / "gas_tuning_lifetime_data.json")
    center = tuple(lt_meta["lifetime_coord"])   # measurement coordinate in µm
    emitters = estimate_emitter_count(
        base / "spatial_PL_counts.json",
        center_um=center, mode_radius_um=0.4, cluster_radius_um=0.3,
    )
    print(f"Emitter count estimate: {emitters['n_lower']}–{emitters['n_upper']} "
          f"(found {emitters['n_clusters']} bright clusters near {center})")

    bg = build_background_estimate(lt)
    print(f"Background per bin: mean={bg.mean():.2f}, range=[{bg.min():.2f}, {bg.max():.2f}]")
