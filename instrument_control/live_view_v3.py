"""
Version 3

Program that controls signal generator, oscilloscope, and VNA and captures data
from the devices.
"""

import os.path
import pyvisa
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pathlib

# If True, only scope data is saved. If False only VNA data is saved.
SAVE_SCOPE = False

rm = pyvisa.ResourceManager()

# For setup of the signal generator. The frequency that it starts its sweep at.
RF_GEN_START = 560000000


# Directories for result data. Creates the necessary directories to distinguish between different scenarios and configurations.
root_dir = pathlib.Path("./detuning_data_2022_11_29")

scenario = "metal_data"
cap_value = "10nh"
with_cap = False

final_dir = pathlib.Path(
    root_dir, f"{cap_value}_{'with_cap' if with_cap else 'no_cap'}", scenario)
final_dir.mkdir(parents=True, exist_ok=True)

DATA_PATH = final_dir


def scope_setup(time_div="10E-9", ampl_div=["20E-3", "20E-3", "10E-3", "10E-3"], connection_string="TCPIP::192.168.1.101"):
    """Configures the oscilloscope at a given IP-address to use a particular timebase and amplitude division for each channel.
    """

    scope_instr = rm.open_resource(connection_string)

    # Initial setup of scope. Setting timebase and amplitude scaling
    scope_instr.write(f"TIMebase:SCALe {time_div}")

    for i in range(4):
        chan_num = i + 1
        scope_instr.write(f"CHANnel{chan_num}:STATe ON")
        scope_instr.write(f"CHANnel{chan_num}:SCALe {ampl_div[i]}")

    return scope_instr


def scope_get_data(instr, chan):
    """Gets data from the given oscilloscope on the given channel.
    """

    data = instr.query_binary_values(
        f"FORM REAL,32;:CHAN{chan}:DATA?", is_big_endian=True)
    return data, len(data)


def sig_gen_setup(power="-6", frequency=str(RF_GEN_START), connection_string="TCPIP::192.168.1.69"):
    """Configures the signal generator at a given IP-address to start at a specific frequency and power level at the output.
    """
    sig_gen_instr = rm.open_resource(connection_string)

    # Initial setup of signal generator. Setting power, enabling RF, disabling IQ modulation and baseband. Frequency start.
    print(sig_gen_instr.query("*IDN?"))
    sig_gen_instr.write(f"FREQ {frequency}")
    sig_gen_instr.write(f"POWer:POWer {power}")
    sig_gen_instr.write("OUTPut1 ON")

    return sig_gen_instr


def sig_gen_set_freq(instr, frequency):
    """Updates the frequency of the signal generator.
    """
    instr.write(f"FREQ {frequency}")


def vna_setup(connection_string="TCPIP::192.168.1.59", power="+12"):
    """Configures the VNA at a given IP-address to use a manual point trigger (sweep now), set its output power level, 
    sweep frequency range, creating a diagram to attach the output trace to, setting the output data format.
    """
    vna_instr = rm.open_resource(connection_string)

    # Initial setup of of VNA. Setting trace measure, trigger, sweep.
    # Setting manual, point trigger
    vna_instr.write("TRIG:SEQ:SOURCE MAN")
    # vna_instr.write("TRIG:LINK 'POINt'")
    vna_instr.write("TRIG:LINK 'SWEep''")

    # Setting source power to 12 dBm
    vna_instr.write(f"SOURCE:POWER {power}")

    # Setting sweep from 600-1000 MHz
    vna_instr.write("FREQ:STAR 600MHz")
    vna_instr.write("FREQ:STOP 1GHz")

    # Creating new trace, Trc1, with s11. Creating a diagram and attaching the trace to it.
    vna_instr.write("CALC1:PAR:SDEF 'Trc1', 's11'")
    vna_instr.write("DISP:WIND1:STAT ON")
    vna_instr.write("DISP:WIND1:TRAC:FEED 'Trc1'")

    # Setting the diagram display to magnitude, and the export format to ASCII
    vna_instr.write("CALC1:FORM MAGN")
    vna_instr.write("FORM:DATA ASCii")

    time.sleep(1)

    return vna_instr


# Setting up the instruments
if SAVE_SCOPE:
    scope = scope_setup(ampl_div=["5E-3", "5E-3", "5E-3", "5E-3"])
# sig_gen = sig_gen_setup(power="-30")
vna = vna_setup(power="0")

step_size = int(vna.query("SWEep:STEP?"))

# Manual point trigger the VNA 201 times, and record the data for the oscilloscope
# for i in range(201):
#     vna.write("*TRG")
#     time.sleep(0.01)
#     new_freq = RF_GEN_START + i * step_size
#     sig_gen_set_freq(sig_gen, str(new_freq))
#     time.sleep(0.01)

#     if SAVE_SCOPE:
#         channels = {}
#         for n in range(1, 5):
#             channels[f"chan{n}"] = scope_get_data(scope, n)[0]

#         df = pd.DataFrame.from_dict(channels)
#         df.to_csv(os.path.join(DATA_PATH, f"{new_freq // 1000000}.csv"))

# Full sweep on single trigger
vna.write("*TRG")
time.sleep(5)

# Save VNA data
if not SAVE_SCOPE:
    data = vna.query_ascii_values("CALC1:DATA? FDAT")

    df = pd.DataFrame.from_dict({"chan1": data})
    df.to_csv(os.path.join(DATA_PATH, "magn.csv"))

    # Change the VNA format from magnitude to smith
    vna.write("CALC1:FORM SMITh")
    time.sleep(1)
    data = vna.query_ascii_values("CALC1:DATA? FDAT")
    data_array = np.array(data)

    x = data_array[::2]
    y = data_array[1::2]

    smith_data = {"real": x, "imag": y}
    df = pd.DataFrame.from_dict(smith_data)
    df.to_csv(os.path.join(DATA_PATH, "smith.csv"))

if SAVE_SCOPE:
    print("Finished, only saved scope data.")
else:
    print("Finished, only saved VNA data.")
