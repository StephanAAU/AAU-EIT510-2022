import pandas as pd
import eseries
import plotly.graph_objects as go
import numpy as np
import multiprocessing as mp
import itertools
import time
import skrf as rf
import smithimp_methods
from multiprocessing import shared_memory, Process, Lock
from multiprocessing import cpu_count, current_process

# Load in the antenna

ntwrk_testing = rf.Network("Test_of_pi_match_calc/Ant3Proto.s1p")

s_params_testing = ntwrk_testing.s[:, 0, 0]

real_s = [x.real for x in s_params_testing]
imag_s = [x.imag for x in s_params_testing]

touch_df_test = pd.DataFrame({
    "freq": np.linspace(600, 1200, 1001),
    "real": real_s,
    "imag": imag_s
})
# Load in antenna with parameter

comparision_df = pd.read_csv("Test_of_pi_match_calc/test_of_export_of_smith.csv", sep=";", header=0, names=("freq", "real", "imag"))

pd.set_option('display.max_rows', None)

#print(comparision_df)

# Transform
transformed = smithimp_methods.apply_transform_df(touch_df_test, (smithimp_methods.Capacitor(5E-12),smithimp_methods.Inductor(3.3E-9)))

#print(transformed)

real_s = [x.real for x in transformed]
imag_s = [x.imag for x in transformed]

transformed_df = pd.DataFrame({
    "real": real_s,
    "imag": imag_s
})




print(transformed_df)

# Check if they are equal
erros_real = transformed_df["real"]-comparision_df["real"]
erros_imag = transformed_df["imag"]-comparision_df["imag"]




error_df = pd.DataFrame({
    "real error": erros_real,
    "imag error": erros_imag
})

