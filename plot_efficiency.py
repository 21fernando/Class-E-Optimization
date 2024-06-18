import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Load the data
df = pd.read_csv('C:/Users/taf27/Desktop/Class-E-Optimization/optimization/06-12_22-41-35/results_200ohm_06-12_22-41-35.csv')
# Filter rows with POWER OUT < 8
df_filtered = df[df['POWER OUT'] < 8].copy()

# Scale C2 and C4 by 1e12
df_filtered.loc[:, 'C2'] = df_filtered['C2'] * 1e12
df_filtered.loc[:, 'C4'] = df_filtered['C4'] * 1e12

# Group by C2 and C4, choose the row with the largest POWER OUT < 8 for each group
df_grouped = df_filtered.drop_duplicates(['C2', 'C4'], keep='last')
# Create a pivot table with C2 and C4 as indices and EFFICIENCY as values
pivot_table = df_grouped.pivot(index='C4', columns='C2', values='EFFICIENCY')
pivot_table_power_out = df_grouped.pivot(index='C4', columns='C2', values='POWER OUT')

# Initialize all cells to -1 (representing black for POWER OUT <= 5)
all_c2_values = np.arange(215e12, 791e12, 50e12)
all_c4_values = np.arange(215e12, 791e12, 50e12)
# Loop through the pivot table and set EFFICIENCY to -1 where POWER OUT < 5
for i in range(pivot_table.shape[0]):
    for j in range(pivot_table.shape[1]):
        if pivot_table_power_out.iloc[i, j] < 5:
            pivot_table.iloc[i, j] = -1

# Create a custom discrete color map
# Create a custom discrete color map from red to green
cmap = mcolors.LinearSegmentedColormap.from_list('custom_cmap', ['red', 'yellow', 'green'])
bounds = np.arange(0, 110, 10)
norm = mcolors.BoundaryNorm(bounds, cmap.N)

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(10, 8))

# Plotting
cax = ax.imshow(pivot_table, cmap=cmap, norm=norm, aspect='auto', origin='lower')

# Add a color bar
cbar = fig.colorbar(cax, ax=ax, extend='both', ticks=bounds)
cbar.set_label('Efficiency')
cbar.set_ticks(bounds)

# Set ticks and labels
x_ticks = np.arange(0, 100, 10)
y_ticks = np.arange(0, 100, 10)
ax.set_xticks(x_ticks)
ax.set_xticklabels(215+x_ticks*(790-215)*0.01)
ax.set_yticks(y_ticks)
ax.set_yticklabels(215+y_ticks*(790-215)*0.01)

ax.set_xlabel('C2 (pF)')
ax.set_ylabel('C4 (pF)')
ax.set_title('Efficiency vs C2 and C4 for RL=200')

# Overlay black color for combinations with POWER OUT <= 5
for i in range(pivot_table.shape[0]):
    for j in range(pivot_table.shape[1]):
        if pivot_table.iloc[i, j] == -1:
            ax.add_patch(plt.Rectangle((j-0.5, i-0.5), 1, 1, fill=True, color='white', edgecolor=None))

plt.show()
