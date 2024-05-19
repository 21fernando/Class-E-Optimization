import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load data
csv_data = pd.read_csv('C:/Users/taf27/Documents/IndependentStudy/LTSPICE_GaN/Bad_class_E_PSPICE.csv', header=0, names=['Time', 'Data'])
txt_data = pd.read_csv('C:/Users/taf27/Documents/IndependentStudy/LTSPICE_GaN/bad_class_E_LTSPICE.txt', sep="\t", header=0, names=['Time', 'Data'])

# Normalize time for CSV data by subtracting the initial time
csv_data['Time'] = pd.to_numeric(csv_data['Time'], errors='coerce')
csv_data['Time'] = csv_data['Time'] - csv_data['Time'].iloc[0]

# Plotting
plt.figure(figsize=(10, 6))

plt.plot(csv_data['Time'], csv_data['Data'], label='PSPICE', linestyle='-')
plt.plot(txt_data['Time'], txt_data['Data'], label='LTSPICE', linestyle='--')

plt.xlabel('Time (s)')
plt.ylabel('I_D (A)')
plt.title('ID Comparison')
plt.legend()
plt.show()
