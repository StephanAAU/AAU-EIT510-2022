import pandas as pd
import eseries
import plotly.graph_objects as go
import numpy as np
import multiprocessing as mp
import itertools
import time
#import skrf as rf
import uuid
import glob
from multiprocessing import shared_memory, Process, Lock
from multiprocessing import cpu_count, current_process


# -----------------Impedances ---------------------

# Feedline impedance
Z0 = 50

# Classes of different components
class Capacitor:
    def __init__(self, capacitance):
        self.capacitance = capacitance

    def impedance(self, freq):
        imp = 1/(1j*2*np.pi*freq*self.capacitance)
        # print(imp)
        return imp


class Inductor:
    def __init__(self, inductance):
        self.inductance = inductance

    def impedance(self, freq):
        imp = 1j*2*np.pi*freq*self.inductance
        # (imp)
        return imp

# ------------------Loading data portion-------------------------------

file_cap = "5.6"

file_paths = glob.glob(
    f"optimise_in_vivo/detuning_data_2022_11_29/{file_cap}nh_no_cap/**/smith.csv", recursive=True)

file_paths.extend(glob.glob(
    f"optimise_in_vivo/detuning_data_2022_11_29/{file_cap}nh_with_cap/**/smith.csv", recursive=True))

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

    smith_df_table = pd.read_csv(f)
    smith_df_table = smith_df_table.rename(columns={"Unnamed: 0": "freq"})

    smith_df_table["freq"] = smith_df_table["freq"].apply(
        lambda f: 600 + 2 * f)

    # Filter the smith Chart
    smith_df_table = smith_df_table[(smith_df_table["freq"] >= 790) & (
        smith_df_table["freq"] <= 866)]
    all_the_smith.append(smith_df_table)

# ------------------End of loading data portion------------------------

#-------------------Functions to do transformations-------------------

# Convert from UV coords to normalized impedance
def uv_to_impn(u, v):
    refl = complex(u, v)

    z = -(refl + 1)/(refl - 1)

    return z


# Convert from normalized impedance to UV coords
def impn_to_uv(r, x):
    impn = complex(r, x)

    refl = (impn-1)/(impn+1)

    return refl

# Transform an impedance to a normalised impedance
def eseries_to_norm(impedance, norm=Z0):
    return impedance / norm

# Transform a reflections coeffcient by a component list
def transform_uv(u, v, imps):
    normalized_impedance = uv_to_impn(u, v)

    for i, z in enumerate(imps):
        #print(i, z)
        if i % 2 == 0:
            normalized_impedance = 1/(1/z+1/normalized_impedance)
        else:
            normalized_impedance = normalized_impedance + z

    uv_coords = impn_to_uv(normalized_impedance.real,
                           normalized_impedance.imag)

    return uv_coords

# Transform a dataframe of reflection coeffcients by a component list
def apply_transform_df(df, components, norm=Z0):
    result = []
    for row in df.itertuples():
        if row.freq > 866 or row.freq < 790:
            #print(f"Skipping {row.freq}")
            continue
        imps = list(map(lambda x: x.impedance(row.freq*1E6)/norm, components))

        transformed_uv = transform_uv(row.real, row.imag, imps)

        result.append(transformed_uv)

    return result

#-------------------END Functions to do transformations-------------------

#-------------------Cost functions ---------------------------------------

# Primary cost, counting the amount of points within the bandwidth
def cost(uv_points):
    uv_array = np.array(uv_points)
    magn_magnitude = np.abs(uv_array)
    sum = 0
    for i in magn_magnitude:
        if i > 0.5:
            sum += 1

    #magn_squared = uv_array.imag ** 2 + uv_array.real ** 2

    # print(magn_average)

    return sum

# Secondary cost, average distrance of the points
def second_cost(uv_points):
    uv_array = np.array(uv_points)
    magn_magnitude = np.abs(uv_array)

    return magn_magnitude.mean()
#-------------------END Cost functions ---------------------------------------



# List of components within the erange.
caps_range = list(eseries.erange(eseries.E48, 4E-12, 1E-10))
inductor_range = list(eseries.erange(eseries.E48, 1E-9, 1E-7))
caps_range2 = list(eseries.erange(eseries.E48, 4E-12, 1E-10))


# -----------------Starting and managing the multiprocessing ---------------

# Process started by each core
def process(q, shm_name):

    # Point a numpy array at the sharedmemory.
    existing_shm = shared_memory.SharedMemory(name=shm_name)
    optimal_storage = np.ndarray((len(inductor_range), len(
        all_the_smith), 5), dtype=np.float64, buffer=existing_shm.buf)

    # Get the inductor to process
    inductor_index = q.get()
    while inductor_index != None:

        # Assign inductor value
        ind = inductor_range[inductor_index]
        
        #For each scenario, calculate the cost
        for scenario_index, smith_df in enumerate(all_the_smith):
            
            # Reset the cost
            local_optimal_cost = 1001
            local_second_optimal_cost = 1

            # Loop through capacitor 1
            for cap in caps_range:
                
                # Loop through capacitor 2
                for cap2 in caps_range2:
                    
                    # Apply the transform 
                    transformed_uv = apply_transform_df(
                        smith_df, [Capacitor(cap), Inductor(ind), Capacitor(cap2)])

                    # Calculate the primary cost
                    solution_cost = cost(transformed_uv)

                    # Compare the current solution in this count
                    if solution_cost < local_optimal_cost:
                        local_optimal_cost = solution_cost
                        local_optimal_solution = (ind, cap, cap2)
                    elif solution_cost == local_optimal_cost:
                        
                        # Calculate the secondary cost
                        second_solution_cost = second_cost(transformed_uv)
                        if second_solution_cost < local_second_optimal_cost:
                            local_second_optimal_cost = second_solution_cost
                            local_optimal_solution = (ind, cap, cap2)
            
            # Put the results in the shared memory, by acquiring semaphore.
            lock.acquire()
            optimal_storage[inductor_index, scenario_index] = [
                local_optimal_cost, *local_optimal_solution, all_the_smith_numbering[scenario_index]]
            lock.release()
        
        # Get the inductor
        inductor_index = q.get()

    existing_shm.close()

# Define semaphore lock
lock = Lock()

# Code to run if its the main thread.
if __name__ == '__main__':

    # Print optimsing space
    print(
        f"Optimizing space: {len(caps_range)*len(inductor_range)*len(caps_range2)}")
    NCORE = 64

    # Create a shared memory NP array-----------------
    optimal_storage_form = np.zeros(
        (len(inductor_range), len(all_the_smith), 5))

    shm = shared_memory.SharedMemory(
        create=True, size=optimal_storage_form.nbytes)
    # # Now create a NumPy array backed by shared memory
    optimal_storage = np.ndarray(
        optimal_storage_form.shape, dtype=np.float64, buffer=shm.buf)
    # Copy the original data into shared memory
    optimal_storage[:] = optimal_storage_form[:]
    # ------------------------------------------------

    # Start timer, and create queue manager
    start = time.time()
    with mp.Manager() as manager:
        # Create queue with length queue
        q = mp.Queue(len(inductor_range))

        # Start the NCORE amount of processes
        p = mp.Pool(NCORE, initializer=process, initargs=(q, shm.name))

        # Create the queue of inductors to be done
        for index, combination in enumerate(inductor_range):
            q.put(index)

        # Make the processes stop
        for amount_of_cores in range(NCORE):
            q.put(None)

        p.close()
        p.join()
    
    # See if file exists, and put the results in file.
    with open(f"optimal_solution_{file_cap}nH.npy", "wb") as file_name:
        print(file_name)
        np.save(file_name, optimal_storage)
    print(f"Done in {time.time() - start}")
    shm.close()

# print(f"The optimal CLC-network is: {optimal_solution[0]}, {optimal_solution[1]}, {optimal_solution[2]}. The cost is: {optimal_cost}.")
# print(len(optimal_uv))
# z2 = list(map(lambda x: uv_to_impn(x.real, x.imag), optimal_uv))
# real2 = list(map(lambda x: x.real, z2))
# imag2 = list(map(lambda x: x.imag, z2))

# fig = go.Figure([go.Scattersmith(imag=imag, real=real), go.Scattersmith(imag=imag2, real=real2)])
# fig.show()
