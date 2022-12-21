import numpy as np
Z0 = 50

class Capacitor:
    def __init__(self, capacitance):
        self.capacitance = capacitance

    def impedance(self, freq):
        imp = 1/(1j*2*np.pi*freq*self.capacitance)
        #print(imp)
        return imp

class Inductor:
    def __init__(self, inductance):
        self.inductance = inductance

    def impedance(self, freq):
        imp = 1j*2*np.pi*freq*self.inductance
        #(imp)
        return imp

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
        #if row.freq > 866 or row.freq < 790:
        #    #print(f"Skipping {row.freq}")
        #    continue
        imps = list(map(lambda x: x.impedance(row.freq*1E6)/norm, components))

        transformed_uv = transform_uv(row.real, row.imag, imps)

        result.append(transformed_uv)
        
    return result




def cost(uv_points):
    uv_array = np.array(uv_points)
    magn_squared = uv_array.imag ** 2 + uv_array.real ** 2
    magn_average = magn_squared.mean()

    #print(magn_average)

    return magn_average
