import numpy as np

def load_timeresolved_data(path):
    data = np.loadtxt(path, skiprows=4)

    start_t = 10.09 # ns
    end_t = start_t + 9 # ns

    all_times_ns = data[:, 0] / 1e3   # ps -> ns
    all_counts   = data[:, 2]

    mask = (all_times_ns >= start_t) & (all_times_ns <= end_t)
    return np.array(all_times_ns[mask])-start_t, np.array(all_counts[mask])
