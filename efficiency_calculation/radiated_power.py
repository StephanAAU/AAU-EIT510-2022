import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

def set_size(width, fraction=1):
    """Set figure dimensions to avoid scaling in LaTeX.

    Parameters
    ----------
    width: float
            Document textwidth or columnwidth in pts
    fraction: float, optional
            Fraction of the width which you wish the figure to occupy

    Returns
    -------
    fig_dim: tuple
            Dimensions of figure in inches
    """
    # Width of figure (in pts)
    fig_width_pt = width * fraction

    # Convert from pt to inches
    inches_per_pt = 1 / 72.27

    # Golden ratio to set aesthetic figure height
    # https://disq.us/p/2940ij3
    golden_ratio = (5**.5 - 1) / 2

    # Figure width in inches
    fig_width_in = fig_width_pt * inches_per_pt
    # Figure height in inches
    fig_height_in = fig_width_in

    fig_dim = (fig_width_in, fig_height_in)

    return fig_dim

plt.rcParams['text.usetex'] = True
plt.rc('xtick', labelsize='x-small')
plt.rc('ytick', labelsize='x-small')

# Read in raw data from anechoic chamber measurements
raw_points = np.loadtxt("data_2022_12_15/without_hand.txt", skiprows=1, dtype=np.float64)
raw_points_without = np.loadtxt("v3_without_hand.txt", skiprows=1)

# Init defaultdicts to sum and count over points, grouped by the frequency.
grouped_by_freq = defaultdict(np.float64)
freq_count = defaultdict(int)

# Iterate through all data points, and calculate the sum of EIRP at each measured frequency.
# Scaled by Jacobian term, sin(theta).

for idx, point in enumerate(raw_points):
    freq = point[0]

    theta = point[2]

    if idx % 121 == 0:
        print("Yes", theta)
        continue
    
    grouped_by_freq[freq] += 10**(point[7]/10) * np.sin(point[1])
    freq_count[freq] += 1

# For each frequency multiply by pi/(2*M*N).
# Multiply by hundred to format percentage correctly.
scaling = 1/(4*np.pi) * 2 * np.pi * np.pi
for key, value in grouped_by_freq.items():
    grouped_by_freq[key] *= scaling / (freq_count[key])

##########
# Init defaultdicts to sum and count over points, grouped by the frequency.
grouped_by_freq_without = defaultdict(np.float64)
freq_count_without = defaultdict(int)

print(10*np.log10(grouped_by_freq[810000000]))

# Iterate through all data points, and calculate the sum of EIRP at each measured frequency.
# Scaled by Jacobian term, sin(theta).
for point in raw_points_without:
    freq = point[0]
    
    grouped_by_freq_without[freq] += 10**(point[7]/10) * np.sin(point[1])
    freq_count_without[freq] += 1

# For each frequency multiply by pi/(2*M*N).
# Multiply by hundred to format percentage correctly.
for key, value in grouped_by_freq_without.items():
    grouped_by_freq_without[key] *= scaling / (freq_count_without[key])

fig, ax = plt.subplots(figsize=set_size(453/2))

ax.plot(np.linspace(600, 1000, len(grouped_by_freq.values())), 10*np.log10(np.array(list(grouped_by_freq.values()))), label="With hand")
ax.plot(np.linspace(600, 1000, len(grouped_by_freq_without.values())), 10*np.log10(np.array(list(grouped_by_freq_without.values()))), label="Free space")

ax.set_xlabel("Frequency [MHz]")
ax.set_ylabel("Efficiency [dB]")
ax.legend(loc="lower right", bbox_to_anchor=(0.95, 0.05))

plt.tight_layout()
fig.savefig("radiated_efficiency.pdf")
plt.show()