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
# smith_df = pd.read_csv("Test_of_pi_match_calc\Ant3Proto.s1p")
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

# Load the touchstone file
ntwrk = rf.Network("Test_of_pi_match_calc\Ant3Proto.s1p")

s_params = ntwrk.s[:, 0, 0]

real_s = [x.real for x in s_params]
imag_s = [x.imag for x in s_params]

touch_df = pd.DataFrame({
    "freq": np.linspace(600, 1000, 1001),
    "real": real_s,
    "imag": imag_s
})

# Load in CSV file for comparison
comparision_df = pd.read_csv("Test_of_pi_match_calc/test_of_export_of_smith.csv", sep=";", header=0, names=("freq", "real", "imag"))
z_compare =[]
for row in comparision_df.itertuples():
    z_compare.append(uv_to_impn(row.real,row.imag))

# Define the PI-match that is usued
Components_of_pi = [Capacitor(5E-12), Inductor(3.3E-9), Capacitor((20E-12))]
df_to_use = touch_df

# Apply the transformation to the touchstone
optimal_uv = apply_transform_df(df_to_use, Components_of_pi, Z0)
z2 = list(map(lambda x: uv_to_impn(x.real, x.imag), optimal_uv))



# optimal_uv_2 = apply_transform_df(df_to_use, [Capacitor(2.05E-12), Inductor(8.66E-9), Capacitor(1.05E-12)], Z0)

# z2 = list(map(lambda x: uv_to_impn(x.real, x.imag), optimal_uv_2))
# real3 = list(map(lambda x: x.real, z2))
# imag3 = list(map(lambda x: x.imag, z2))


# Split the data into two lists, for the plot
real2 = list(map(lambda x: x.real, z2))
imag2 = list(map(lambda x: x.imag, z2))

real3 = list(map(lambda x: x.real, z_compare))
imag3 = list(map(lambda x: x.imag, z_compare))


# Transform into numpy arrays for ease of error calculation
Transformed_by_python_real = np.asarray(real2)
Transformed_by_python_imag = np.asarray(imag2)

qucs_real = np.asarray(real3)
qucs_imag = np.asarray(imag3)

# Calculate the error
error = [Transformed_by_python_real-qucs_real,Transformed_by_python_imag-qucs_imag]

# Print the error
np.set_printoptions(threshold=sys.maxsize)
print("Error Average")
print(error[0].mean())
print(error[1].mean())

# Relative error
realtive_error= [(Transformed_by_python_real-qucs_real)/qucs_real,(Transformed_by_python_imag-qucs_imag)/qucs_imag]

print("Relative error")
print(realtive_error[0].mean())
print(realtive_error[1].mean())

fig = go.Figure([go.Scattersmith(imag=imag2, real=real2,name="Software under test"),go.Scattersmith(imag=imag3, real=real3,name="Comparison Dataset")])
fig.show()