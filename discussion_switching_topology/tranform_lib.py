import pandas as pd
import plotly.graph_objects as go
import numpy as np
import skrf as rf
import matplotlib.pyplot as plt
import sys


Z0 = 50

class Capacitor:
    def __init__(self, capacitance):
        self.capacitance = capacitance

    def impedance(self, freq):
        imp = 1/(1j*2*np.pi*freq*self.capacitance)
        return imp

class Inductor:
    def __init__(self, inductance):
        self.inductance = inductance

    def impedance(self, freq):
        imp = 1j*2*np.pi*freq*self.inductance
        return imp

# Read smith chart data and rename unnamed column
# smith_df = pd.read_csv("detuning_data_2022_11_29/10nh_with_cap/air_data/smith.csv")
# smith_df = smith_df.rename(columns={"Unnamed: 0": "freq"})

# # Convert indices to frequency, 600-1000 MHz
# smith_df["freq"] = smith_df["freq"].apply(lambda f: 600 + 2 * f)


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


def eseries_to_norm(impedance, norm = Z0):
    return impedance / norm

def transform_uv(u, v, imps):
    normalized_impedance = uv_to_impn(u, v)

    for i, z in enumerate(imps):
        #print(i, z)
        if i % 2 == 0:
            normalized_impedance = 1/(1/z+1/normalized_impedance)
        else:
            normalized_impedance = normalized_impedance + z
        
    uv_coords = impn_to_uv(normalized_impedance.real, normalized_impedance.imag)

    return uv_coords

def apply_transform_df(df, components, norm = Z0):
    result = []
    for row in df.itertuples():
        # if row.freq > 866 or row.freq < 790:
        #     #print(f"Skipping {row.freq}")
        #     continue
        imps = list(map(lambda x: x.impedance(row.freq*1E6)/norm, components))

        transformed_uv = transform_uv(row.real, row.imag, imps)

        result.append(transformed_uv)
        
    return result


#### PLOT FROM COMPONENT VALUES ####

# comparision_df = pd.read_csv("Test_of_pi_match_calc/test_of_export_of_smith.csv", sep=";", header=0, names=("freq", "real", "imag"))
# z3 =[]
# for row in comparision_df.itertuples():
#     z3.append(uv_to_impn(row.real,row.imag))

