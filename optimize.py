import numpy as np
import matplotlib.pyplot as plt
from PyLTSpice import LTSpice

# Initialize LTSpice
ltspice = LTSpice("C:/Users/taf27/Documents/IndependentStudy/LTSPICE_GaN/GaN_Class_E.asc")  # Specify your LTspice file here

# Define the ranges of the components to test
C1_values = np.linspace(1e-12, 1e-9, 10)  # Example range for C1
C2_values = np.linspace(1e-12, 1e-9, 10)  # Example range for C2
L2_values = np.linspace(100e-9, 500e-9, 10)  # Example range for L2

# Record the best combination
best_rms_power = 0
best_combination = (0, 0, 0)

# Run the simulation for each combination
for C1 in C1_values:
    for C2 in C2_values:
        for L2 in L2_values:
            # Set the component values
            ltspice.set_component_value("C1", C1)
            ltspice.set_component_value("C2", C2)
            ltspice.set_component_value("L2", L2)
            
            # Run the simulation
            ltspice.run()

            # Get the waveform data
            time, V_R2 = ltspice.get_waveform_data("V(R2)")

            # Calculate the RMS power
            rms_voltage = np.sqrt(np.mean(V_R2**2))
            rms_power = (rms_voltage**2) / R2  # Assuming R2's value is known
            
            # Check if this is the best combination so far
            if rms_power > best_rms_power:
                best_rms_power = rms_power
                best_combination = (C1, C2, L2)

# Print the results
print(f"The best combination for the highest RMS power over R2 is C1={best_combination[0]}, C2={best_combination[1]}, L2={best_combination[2]} with an RMS power of {best_rms_power} W.")
