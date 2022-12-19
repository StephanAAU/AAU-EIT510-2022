import eseries
import numpy as np
import itertools
import matplotlib.pyplot as plt
from scipy.optimize import nnls, lsq_linear

# Minimum and maximum equivalent capacitance that network should be adjustable to
CAP_RANGE = (1E-12, 4E-12)

# How many SPDT switches are utilized?
SWITCH_COUNT = 4

# Determines the points needed, assuming a linear distribution of capacitances with equal step size is wanted.
def expected_values(cap_range, n):
    n_states = 2**n

    expected = []
    for i in range(n_states):
        new = cap_range[0] + (cap_range[1] - cap_range[0])/(n_states - 1) * i
        expected.append(new)

    return expected


def expected_values_poly(caps, n):
    n_states = 2**n

    expected = []

    x = np.linspace(0,5,6)

    polynomial_coef = np.polyfit(x, caps, deg=5)

    polynomial_fit = np.poly1d(polynomial_coef)

    expected_values = polynomial_fit(np.linspace(0, 5, n_states))

    return expected_values

# Determines the points needed, assuming a linear distribution
def expected_values_from_points(caps, n):
    n_states = 2**n

    expected = []
    for i, c in enumerate(caps):
        if i < len(caps) - 1:
            next_cap = caps[i + 1]
            expected.extend(np.linspace(c, next_cap, 3, endpoint=False))
        else:
            expected.append(c)

    return expected

# Calculates the equivalent capacitance of all possible states. A state is any permutation of switch positions. 
def all_states(caps):
    states = list(itertools.product(*caps))
    state_sums = [sum(state) for state in states]

    return state_sums


def run(cap_range, switch_count, series):
    fig, ax = plt.subplots()
    ax2 = ax.twinx()

    # expected = expected_values(cap_range, switch_count)
    expected = expected_values(cap_range, switch_count)

    coefficient_matrix = [np.array(x).flatten() for x in list(itertools.product([[0, 1], [1, 0]], repeat=switch_count))]

    # result = nnls(coefficient_matrix, expected, maxiter=1000)
    result = lsq_linear(coefficient_matrix, expected, bounds=([1E-12]*(switch_count*2), [100E-12]*(switch_count*2)), method="bvls")
    
    print(result)

    result_caps = result['x']
    switch_chunks = np.array_split(result_caps, SWITCH_COUNT)

    result_caps_discrete = [eseries.find_nearest(series, cap) if cap != 0 else 0 for cap in result_caps]
    switch_chunks_discrete = np.array_split(result_caps_discrete, switch_count)

    print("Continuous switch chunks:", switch_chunks)
    print("Discrete switch chunks:", switch_chunks_discrete)
    print("Target values:", expected)
    print("Possible values:", sorted(all_states(switch_chunks_discrete)))

    line1, = ax.plot(expected)
    line2, = ax.plot(sorted(all_states(switch_chunks)), marker='x')
    line3, = ax.plot(sorted(all_states(switch_chunks_discrete)), marker='o')
    line4, = ax2.plot((np.array(expected) - np.array(sorted(all_states(switch_chunks_discrete))))/np.array(expected)*100, marker='o', color="red")



    line1.set_label("Expected values")
    line2.set_label("Selected values")
    line3.set_label("Selected values (discrete)")
    line4.set_label("Relative error [%]")


    ax.legend()
    plt.show()
    return expected_values, switch_chunks_discrete
    

if __name__ == '__main__':
    run(CAP_RANGE, SWITCH_COUNT, eseries.E48)