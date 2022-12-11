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
from multiprocessing import shared_memory, Process, Lock
from multiprocessing import cpu_count, current_process



# Make list of relative files
file_paths = glob.glob("np_array_extra_cost_fixed_v2/*.npy")

# --------------- Find the proper span for each capcitors --------------------------- #

# Make lists for the best configuration for each tuning inductor configuration
super_scenario = []
super_scenario_cost = []
super_scenario_paths = []

# Loop through each tuning inductor
for path in file_paths:
    # Put the path used in the list for identification purpose
    super_scenario_paths.append(path)

    # Load the NP_array result array
    optimal_solutions_list = np.load(path)

    # Make a list with the average cost for each pi-match inductor.
    average_and_inductor=np.mean(optimal_solutions_list[:,:,0], axis=1)

    # Find the index of the minimum average
    min_index=np.argmin(average_and_inductor)

    print(optimal_solutions_list[min_index,:,:])

    # Append the lowest average cost solution matrix and lowest average cost.
    super_scenario.append(optimal_solutions_list[min_index,:,:])
    super_scenario_cost.append(average_and_inductor[min_index])

# Find the index of the lowest
min_index = np.argmin(super_scenario_cost)

# Print the, matrix, path and cost of the optimal configuration
print(super_scenario[min_index])
print(super_scenario_paths[min_index])
print(super_scenario_cost)

# Sort the capacitors in the matrix
caps_1 = np.sort(super_scenario[min_index][:, 2])
caps_2 = np.sort(super_scenario[min_index][:, 3])


# cap_range1_min = np.min(sy[min_index, : ,2])

# cap_range1_max = np.max(optimal_solutions_list[min_index, : , 2])

# cap_range2_min = np.min(optimal_solutions_list[min_index, : , 3])

# cap_range2_max = np.max(optimal_solutions_list[min_index, : , 3])

# print("Cap 1")
# print(cap_range1_min)
# print(cap_range1_max)
# print("Cap 2")
# print(cap_range2_min)
# print(cap_range2_max)

# --------------- Check the eseries components equally distrubuted along the axis ---- #
switch_count = 4
expected, combo_cap1 = optimize_v4.run((caps_1[0], caps_1[-1]), switch_count, eseries.E48)
expected, combo_cap2 = optimize_v4.run((caps_2[0], caps_2[-1]), switch_count, eseries.E48)

# Print the required components.
print(f"-----------------Capacitor 1 needs -------------")
for idx, combo in enumerate(combo_cap1):
    print(f"Switch {idx+1}: First:{SI.si_format(combo[0])}F Second:{SI.si_format(combo[1])}F")
print(f"-----------------Capacitor 2 needs -------------")
for idx, combo in enumerate(combo_cap2):
    print(f"Switch {idx+1}: First:{SI.si_format(combo[0])}F Second:{SI.si_format(combo[1])}F")

# --------------- Check the cost of each component in 
#                 three scenarios and see if there is improvment----------------------#
# start = time.time()


#Defining the optimal storage

# def process(q, shm_name):
#     existing_shm = shared_memory.SharedMemory(name=shm_name)
#     optimal_storage = np.ndarray((len(inductor_range),len(all_the_smith), 4), dtype=np.float64, buffer=existing_shm.buf)

    

#     inductor_index = q.get()


#     while inductor_index != None:
#         #print(f"I am doing{inductor_index}")
#         ind = inductor_range[inductor_index]
#         for scenario_index, smith_df in enumerate(all_the_smith):
#             local_optimal_cost = 1
#             for cap in caps_range:
#                 for cap2 in caps_range2:    
#                     transformed_uv = apply_transform_df(smith_df, [Capacitor(cap), Inductor(ind), Capacitor(cap2)])
#                     solution_cost = cost(transformed_uv)

#                     # Compare the current solution in this count
#                     if solution_cost < local_optimal_cost:
#                         local_optimal_cost = solution_cost
#                         local_optimal_solution = (ind, cap,cap2)
#             lock.acquire()
#             #print(f"The cost of optimal is {local_optimal_cost} and the index is {inductor_index}, and the solution is {local_optimal_solution} in scenario {}")
#             optimal_storage[inductor_index, scenario_index] = [local_optimal_cost, *local_optimal_solution]
#             lock.release()
#         inductor_index = q.get()

#     existing_shm.close()
        

# lock = Lock()

# print (f"Optimizing space: {len(optimal_solutions_list[0,:,0])}")
# NCORE = 64

    

# # Create a shared memory NP array-----------------
# optimal_storage_form = np.zeros((len(inductor_range),len(all_the_smith), 4))

# shm = shared_memory.SharedMemory(create=True, size=optimal_storage_form.nbytes)
# # # Now create a NumPy array backed by shared memory
# optimal_storage = np.ndarray(optimal_storage_form.shape, dtype=np.float64, buffer=shm.buf)
# optimal_storage[:] = optimal_storage_form[:]  # Copy the original data into shared memory
# # ------------------------------------------------


# start = time.time()
# with mp.Manager() as manager:
#     q = mp.Queue(maxsize=NCORE)

#     p = mp.Pool(NCORE, initializer=process, initargs=(q, shm.name))

#     for index, combination in enumerate(inductor_range):
#         q.put(index)

#     for amount_of_cores in range(NCORE):
#         q.put(None)

#     p.close()
#     p.join()

# np.save("optimal_solution_list_new_attempt", optimal_storage)
# print(f"Done in {time.time() - start}")




