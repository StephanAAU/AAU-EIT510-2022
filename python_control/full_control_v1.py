import numpy as np
import matplotlib.pyplot as plt
import time
import serial
import pyvisa
import pandas as pd
import sys

ser_string = input("Connect to device: ")
ser = serial.Serial(ser_string, baudrate=115200)

rm = pyvisa.ResourceManager()

def vna_setup(connection_string="TCPIP::192.168.1.59", power="+12"):
    """Configures the VNA at a given IP-address to use a manual point trigger (sweep now), set its output power level, 
    sweep frequency range, creating a diagram to attach the output trace to, setting the output data format.
    """
    vna_instr = rm.open_resource(connection_string)

    # Initial setup of of VNA. Setting trace measure, trigger, sweep.
    # Setting manual, point trigger
    vna_instr.write("TRIG:SEQ:SOURCE IMM")
    # vna_instr.write("TRIG:LINK 'POINt'")
    vna_instr.write("TRIG:LINK 'SWEep''")

    # Setting source power to 12 dBm
    vna_instr.write(f"SOURCE:POWER {power}")

    # Setting sweep from 600-1000 MHz
    vna_instr.write("FREQ:STAR 800MHz")
    vna_instr.write("FREQ:STOP 900MHz")

    # Creating new trace, Trc1, with s11. Creating a diagram and attaching the trace to it.
    vna_instr.write("CALC1:PAR:SDEF 'Trc1', 's11'")
    vna_instr.write("DISP:WIND1:STAT ON")
    vna_instr.write("DISP:WIND1:TRAC:FEED 'Trc1'")

    # Setting the diagram display to magnitude, and the export format to ASCII
    vna_instr.write("CALC1:FORM MAGN")
    vna_instr.write("FORM:DATA ASCii")

    time.sleep(1)

    return vna_instr


def get_cost(vna):
    # vna.write("*TRG")
    time.sleep(0.1)

    data = vna.query_ascii_values("CALC1:DATA? FDAT")

    x = np.arange(800, 901, 2)
    df = pd.DataFrame.from_dict({"chan1": data})
    df["freq"] = x
    print(df[df["freq"] == 824]["chan1"].to_numpy()[0])
    return df[df["freq"] == 824]["chan1"].to_numpy()[0]

def shift_value_x(direction, init_val):
    if direction:
        for x in range(4):
            command_string_pre = f"s,{x},{post_list[init_val + 1][x]}\r\n"
            time.sleep(0.01)
            ser.write(bytes(command_string_pre, "ascii"))
    
    elif not direction:
        for x in range(4):
            command_string_pre = f"s,{x},{post_list[init_val - 1][x]}\r\n"
            time.sleep(0.01)
            ser.write(bytes(command_string_pre, "ascii"))

def shift_value_y(direction, init_val):
    if direction:
        for y in range(4):
            command_string_pre = f"s,{y + 4},{pre_list[init_val + 1][y]}\r\n"
            time.sleep(0.01)
            ser.write(bytes(command_string_pre, "ascii"))
    
    elif not direction:
        for y in range(4):
            command_string_pre = f"s,{y + 4},{pre_list[init_val - 1][y]}\r\n"
            time.sleep(0.01)
            ser.write(bytes(command_string_pre, "ascii"))

pre_list = [
    [0, 0, 1, 0], 
    [0, 0, 1, 1],
    [0, 1, 1, 0],
    [0, 1, 1, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 1],
    [1, 0, 1, 0],
    [1, 0, 1, 1],
    [0, 1, 0, 0],
    [0, 1, 0, 1],
    [1, 1, 1, 0],
    [1, 1, 1, 1],
    [1, 0, 0, 0],
    [1, 0, 0, 1],
    [1, 1, 0, 0],
    [1, 1, 0, 1],
    ]
post_list = [
    [0, 0, 1, 0], 
    [0, 0, 1, 1], 
    [0, 1, 1, 0], 
    [0, 1, 1, 1], 
    [0, 0, 0, 0], 
    [0, 0, 0, 1], 
    [1, 0, 1, 0], 
    [1, 0, 1, 1], 
    [0, 1, 0, 0], 
    [0, 1, 0, 1], 
    [1, 1, 1, 0], 
    [1, 1, 1, 1], 
    [1, 0, 0, 0], 
    [1, 0, 0, 1], 
    [1, 1, 0, 0], 
    [1, 1, 0, 1],
]

vna = vna_setup(power="0")
#costFunc = np.load("C:/Users/mikke/Downloads/cost_plots/cost_air.npy")


read_string = f"p,0,0\r\n"
time.sleep(0.01)
ser.write(bytes(read_string, "ascii"))
time.sleep(0.01)
read_buffer = ser.readline()

buffer = [int(chr(var)) for var in list(read_buffer[:-1])]
pre_init = buffer[:4]
post_init = buffer[4:8]

x_val = pre_list.index(pre_init)
y_val = post_list.index(post_init)

print(x_val, y_val)

extremum = 0

# try:
while True:

    current_cost = get_cost(vna)

    if abs((current_cost - extremum)) > 0.5:
        shift_value_x(False, x_val)
        rightXCost = get_cost(vna)

        shift_value_x(True, x_val)
        leftXCost = get_cost(vna)

        shift_value_x(False, x_val + 1)

        if current_cost < rightXCost and current_cost < leftXCost:
            new_val_x = x_val
            shift_value_y(False, y_val)
            rightYCost = get_cost(vna)

            shift_value_y(True, y_val)
            leftYCost = get_cost(vna)

            shift_value_y(False, y_val + 1)

            if current_cost < rightYCost and current_cost < leftYCost:
                new_val_y = y_val
                extremum = get_cost(vna)

            elif current_cost < rightYCost and current_cost > leftYCost:
                new_val_y = y_val - 1

            elif current_cost > rightYCost and current_cost < leftYCost:
                new_val_y = y_val + 1

            elif current_cost > rightYCost and current_cost > leftYCost:
                if rightYCost > leftYCost:
                    new_val_y = y_val - 1

                elif rightYCost < leftYCost:
                    new_val_y = y_val + 1

            if new_val_y <= 0:
                y_val = 0
            elif new_val_y >= 15:
                y_val = 15
            elif new_val_y < y_val:
                shift_value_y(True, y_val)
                y_val = new_val_y
            elif new_val_y > y_val:
                shift_value_y(False, y_val)
                y_val = new_val_y

            print("State y: ", y_val, leftYCost, rightYCost, current_cost)

        elif current_cost < rightXCost and current_cost > leftXCost:
            new_val_x = x_val - 1

        elif current_cost > rightXCost and current_cost < leftXCost:
            new_val_x = x_val + 1

        elif current_cost > rightXCost and current_cost > leftXCost:
            if rightXCost > leftXCost:
                new_val_x = x_val - 1

            elif rightXCost < leftXCost:
                new_val_x = x_val + 1

        if new_val_x <= 0:
            x_val = 0
        elif new_val_x >= 15:
            x_val = 15
        elif new_val_x < x_val:
            shift_value_x(True, x_val)
            x_val = new_val_x
        elif new_val_x > x_val:
            shift_value_x(False, x_val)
            x_val = new_val_x

        print("State x: ", x_val, leftXCost, rightXCost, current_cost)

    else:
        continue
# except Exception as e:
#     print("Exception:", e)
#     sys.stdout.flush()
#     vna.write("TRIG:SEQ:SOURCE IMM")
