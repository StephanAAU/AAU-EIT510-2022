"""
Plots results from live_view script.
"""

import pandas as pd
import numpy as np
import glob
import os.path
import matplotlib.pyplot as plt
import os
from matplotlib.offsetbox import AnchoredText
import pathlib
import svgutils.compose as sc

plt.rcParams.update({
    "text.usetex": True,
    "font.size": 20
})

data_files = [f for f in glob.glob("./detuning_data_2022_11_29/5.6nh_no_cap/**/magn.csv", recursive=True)]

style_map = {
    "table_data": ("solid", "#d62728", True, 1),
    "flamingo_sandwich_hand_data": ("dashed", "#ff7f0e", False, 11),
    "hand_data": ("dashed", "#bcbd22", True, 10),
    "fakir_data": ("solid", "#bcbd22", False, 4),
    "sandwich_air_data": ("solid", "#ff7f0e", False, 5),
    "pants_data": ("dashed", "#d62728", True, 7),
    "flamingo_data": ("solid", "#e377c2", False, 3),
    "air_data": ("solid", "green", True, 2),
    "hand_on_small_table_data": ("dashed", "green", False, 8),
    "small_table_data": ("dashed", "#1f77b4", False, 6),
    "metal_data": ("solid", "#1f77b4", True, 0),
    "flamingo_sandwich_data": ("dashed", "#e377c2", False, 9)
}

fig, ax = plt.subplots()

def calculate_bandwidth(df, resonance_index):
    print("Calculating bandwidth", resonance_index)
    resonance_db = df["chan1"][resonance_index]

    if resonance_db > -6:
        return None


    low_index = resonance_index - 1
    low_db = df["chan1"][low_index]

    high_index = resonance_index + 1
    high_db = df["chan1"][high_index]

    print("res_indx", resonance_index)

    for i in range(resonance_index - 1, -1, -1):
        if abs(df["chan1"][i] + 6) < abs(low_db + 6):
            low_index = i
            low_db = df["chan1"][low_index]

    for i in range(resonance_index + 1, 201):
        if abs(df["chan1"][i] + 6) < abs(high_db + 6):
            high_index = i
            high_db = df["chan1"][high_index]

    return low_index, high_index

order = []

for f in data_files:
    scenario = pathlib.Path(f).parts[-2]
    if not style_map[scenario][2]:
        continue
    else:
        order.append(style_map[scenario][3])
    # Reading raw data in
    data_df = pd.read_csv(f)

    x = np.arange(600, 1001, 2)
    data = data_df["chan1"]

    resonance_index = data_df["chan1"].idxmin()
    resonance_x, resonance_y = 600 + 2 * resonance_index, data_df["chan1"][resonance_index]

    bandwidth = calculate_bandwidth(data_df, resonance_index)
    line, = ax.plot(x, data, color=style_map[scenario][1], linestyle=style_map[scenario][0])

    if bandwidth is not None:
        low_index, high_index = bandwidth
        line.set_label(f"{scenario} (Resonance = {resonance_x} MHz, Bandwidth = {(high_index - low_index) * 2} MHz)")

        low_x, low_y = 600 + low_index * 2, data[low_index]
        high_x, high_y = 600 + high_index * 2, data[high_index]

        # low_point, = ax.plot([low_x], [low_y], marker="o", markersize=5, markeredgecolor=line.get_color(), markerfacecolor=line.get_color())
        # high_point, = ax.plot([high_x], [high_y], marker="o", markersize=5, markeredgecolor=line.get_color(), markerfacecolor=line.get_color())
    else:
        line.set_label(f"{scenario} (Resonance = {resonance_x} MHz)")


    

    # res_point, = ax.plot([resonance_x], [resonance_y], marker="o", markersize=5, markeredgecolor=line.get_color(), markerfacecolor=line.get_color())

    # chan_1, chan_2, chan_3, chan_4 = data_df["chan1"], data_df["chan2"], data_df["chan3"], data_df["chan4"]
    
    # chan_3_mean = np.mean(chan_3)
    # chan_4_mean = np.mean(chan_4) 

handles, labels = ax.get_legend_handles_labels()
sorted_legend = [(x, y) for _, x, y in sorted(zip(order, handles, labels), key=lambda pair: pair[0])]

print(sorted_legend)
plt.ylabel("$S_{11}$ [dB]")
plt.xlabel("Frequency [MHz]")
plt.legend([x[0] for x in sorted_legend], [x[1] for x in sorted_legend])
plt.show()

data_folders = os.listdir("./detuning_data/")

def complex_to_string(num):
    is_negative = num.imag < 0

    return f"{round(num.real, 2)} + {'-' if is_negative else ''}\mathrm{{j}}{round(abs(num.imag), 2)}"




for f in data_folders:
    smith_data_df = pd.read_csv(os.path.join("./detuning_data/", f, "smith.csv"))
    magn_data_df = pd.read_csv(os.path.join("./detuning_data/", f, "magn.csv"))

    print(smith_data_df)


    resonance_index = magn_data_df["chan1"].idxmin()
    resonance_x, resonance_y = (smith_data_df["real"][resonance_index], smith_data_df["imag"][resonance_index])
    resonance_freq = 600 + 2 * resonance_index
    
    refl = complex(resonance_x, resonance_y)
    resonance_imp = -50*(refl + 1)/(refl - 1)

    fig, ax = plt.subplots()
    img = plt.imread("./smith.png")
    ax.imshow(img, extent=[-1.205, 1.205, -1.575, 1.29])

    bandwidth_limits = calculate_bandwidth(magn_data_df, resonance_index)
    

    if bandwidth_limits is not None:

        low_index, high_index = bandwidth_limits
        low_freq = 600 + 2 * low_index
        high_freq = 600 + 2 * high_index

        bandwidth = (high_index - low_index) * 2

        low_x, low_y = (smith_data_df["real"][low_index], smith_data_df["imag"][low_index])
        high_x, high_y = (smith_data_df["real"][high_index], smith_data_df["imag"][high_index])

        line, = ax.plot(smith_data_df["real"][0:low_index + 1], smith_data_df["imag"][0:low_index + 1], color="orange", zorder=2)
        line2, = ax.plot(smith_data_df["real"][low_index:high_index + 1], smith_data_df["imag"][low_index:high_index + 1], color="blue", zorder=2)
        line3, = ax.plot(smith_data_df["real"][high_index:], smith_data_df["imag"][high_index:], color="orange", zorder=2)

        low_point, = ax.plot([low_x], [low_y], marker="o", markersize=5, markeredgecolor="blue", markerfacecolor="blue")
        high_point, = ax.plot([high_x], [high_y], marker="o", markersize=5, markeredgecolor="blue", markerfacecolor="blue")

        at = AnchoredText(f"Bandwidth = {bandwidth} MHz ({low_freq} to {high_freq} MHz)\nResonance = {resonance_freq} MHz ($Z = {complex_to_string(resonance_imp)}$)",
                      loc='upper left', prop=dict(size=8), frameon=True,
                      )

        line2_x, line2_y = line2.get_data()
        ax.arrow(line2_x[line2_x.size // 4], line2_y[line2_y.size // 4], line2_x[line2_x.size // 4 + 1] - line2_x[line2_x.size // 4], line2_y[line2_y.size // 4 + 1] - line2_y[line2_y.size // 4], shape='full', lw=0, length_includes_head=False, head_width=.05, zorder=3, color="blue")
        ax.arrow(line2_x[int(line2_x.size * 3/4)], line2_y[int(line2_y.size *3/4)], line2_x[int(line2_x.size * 3/4) + 1] - line2_x[int(line2_x.size * 3/4)], line2_y[int(line2_y.size * 3/4) + 1] - line2_y[int(line2_y.size * 3/4)], shape='full', lw=0, length_includes_head=False, head_width=.05, zorder=3, color="blue")
    else:
        line, = ax.plot(smith_data_df["real"], smith_data_df["imag"], color="orange")

        at = AnchoredText(f"Resonance = {resonance_freq} MHz ($Z = {complex_to_string(resonance_imp)}$)",
                      loc='upper left', prop=dict(size=8), frameon=True,
                      )
    
    ax.add_artist(at)
    line.set_label(f)

    ax.set_xlabel("$\mathrm{Re}(\Gamma)$")
    ax.set_ylabel("$\mathrm{Im}(\Gamma)$")


    res_point, = ax.plot([resonance_x], [resonance_y], marker="o", markersize=5, markeredgecolor="blue", markerfacecolor="blue")
    # res_point.set_label("Resonance point")

    fig.set_figwidth(7.5)
    fig.set_figheight(8.895)

    ax.legend()
    ax.set_xlim(-1.205, 1.205)
    ax.set_ylim(-1.575, 1.29)
    fig.savefig(f"./detuning_figures/{f}_smith.png", dpi=200)
    # plt.show()
    