import pandas as pd
import eseries
import plotly.graph_objects as go
import numpy as np
import multiprocessing as mp
import itertools
import time
import scipy
import glob
import optimize_v4
import si_prefix as SI
import tranform_lib
import matplotlib.pyplot as plt
from multiprocessing import shared_memory, Process, Lock
from multiprocessing import cpu_count, current_process



# --------------- Load data from saved np array ----------------- #
file_paths = glob.glob("discussion_switching_topology/np_array_for_test/optimal_solution_10nH_tx.npy")

file_paths.append("discussion_switching_topology/np_array_for_test/optimal_solution_10nH.npy")



# --------------- Find the proper span for each capcitors --------------------------- #

super_scenario = []
super_scenario_cost = []
super_scenario_paths = []


for path in file_paths:
    super_scenario_paths.append(path)
    optimal_solutions_list = np.load(path)
    
    print(optimal_solutions_list.shape)

    average_and_inductor=np.mean(optimal_solutions_list[:,:,0], axis=1)
    
    print(average_and_inductor)

    min_index=np.argmin(average_and_inductor)

    print(min_index)

    print(optimal_solutions_list[min_index,:,:])

    super_scenario.append(optimal_solutions_list[min_index,:,:])
    super_scenario_cost.append(average_and_inductor[min_index])

min_index = np.argmin(super_scenario_cost)

print(min_index)

print(f"Printing the tx only\n{super_scenario[0]}")
print(f"Print the whole bandwidth\n{super_scenario[1]}")

# Load in magn data to compare with
file_paths_magn = glob.glob("discussion_switching_topology/detuning_data_2022_11_29/10nh_no_cap/**/magn.csv", recursive=True)

file_paths_magn.extend(glob.glob("discussion_switching_topology/detuning_data_2022_11_29/10nh_with_cap/**/magn.csv", recursive=True))

all_the_magn = []
all_the_magn_numbering = []

for f in file_paths_magn:
    if "no_cap" in f:
        if "air" in f:
            all_the_magn_numbering.append(0)
        elif "hand" in f:
            all_the_magn_numbering.append(1)
        elif "metal" in f:
            all_the_magn_numbering.append(2)
    elif "with_cap" in f:
        if "air" in f:
            all_the_magn_numbering.append(3)
        elif "hand" in f:
            all_the_magn_numbering.append(4)
        elif "metal" in f:
            all_the_magn_numbering.append(5)


    magn_df_table= pd.read_csv(f)
    magn_df_table = magn_df_table.rename(columns={"Unnamed: 0": "freq"})

    magn_df_table["freq"] = magn_df_table["freq"].apply(lambda f: 600 + 2 * f)

    magn_df_table = magn_df_table[(magn_df_table["freq"] >= 700)]

    all_the_magn.append(magn_df_table)



# Load in data in smith Data to transform
file_paths = glob.glob("discussion_switching_topology/detuning_data_2022_11_29/10nh_no_cap/**/smith.csv", recursive=True)

file_paths.extend(glob.glob("discussion_switching_topology/detuning_data_2022_11_29/10nh_with_cap/**/smith.csv", recursive=True))

all_the_smith = []
all_the_smith_numbering = []

for f in file_paths:
    if "no_cap" in f:
        if "air" in f:
            all_the_smith_numbering.append(0)
        elif "hand" in f:
            all_the_smith_numbering.append(1)
        elif "metal" in f:
            all_the_smith_numbering.append(2)
    elif "with_cap" in f:
        if "air" in f:
            all_the_smith_numbering.append(3)
        elif "hand" in f:
            all_the_smith_numbering.append(4)
        elif "metal" in f:
            all_the_smith_numbering.append(5)


    smith_df_table= pd.read_csv(f)
    smith_df_table = smith_df_table.rename(columns={"Unnamed: 0": "freq"})

    smith_df_table["freq"] = smith_df_table["freq"].apply(lambda f: 600 + 2 * f)

    smith_df_table = smith_df_table[(smith_df_table["freq"] >= 700)]

    # Filter the smith Chart
    all_the_smith.append(smith_df_table)

fix, axs = plt.subplots(2,3)


for idx, f in enumerate(file_paths_magn):
    # Plot not transformed
    if idx/3 >= 1:
        y = 1
    else:
        y = 0

    if y == 0:
        x = idx
    else:
        x = idx-3
    axs[y,x].plot(all_the_magn[0]["freq"], all_the_magn[idx]["chan1"], label = "Original")

    #Transform by whole bandwidth
    old_uv = tranform_lib.apply_transform_df(all_the_smith[idx],[tranform_lib.Capacitor(super_scenario[1][idx,2]),tranform_lib.Inductor(super_scenario[1][idx,1]),tranform_lib.Capacitor(super_scenario[1][idx,3])])

    axs[y,x].plot(all_the_smith[0]["freq"],20*np.log10(np.abs(old_uv)), label="Whole Bandwidth")

    #Transform tx only
    new_uv = tranform_lib.apply_transform_df(all_the_smith[idx],[tranform_lib.Capacitor(super_scenario[0][idx,2]),tranform_lib.Inductor(super_scenario[0][idx,1]),tranform_lib.Capacitor(super_scenario[0][idx,3])])

    axs[y,x].plot(all_the_smith[0]["freq"],20*np.log10(np.abs(new_uv)), label="Tx only Bandwidth")

    axs[y,x].set_title("")

# box = axs.get_position()
# axs.set_position([box.x0 * 1.45, box.y0 + box.height * 0.4,
#                  box.width * 1.03, box.height * 0.7])


plt.legend(bbox_to_anchor=(-0,-0.65), loc='lower left')
plt.show()

#optimal_solution = [Capacitor(4.87E-12), Inductor(9.53E-9), Capacitor((4.02E-12))]