import numpy as np
import matplotlib.pyplot as plt
import itertools
from PyLTSpice import LTspice, SpiceEditor, SimRunner, RawRead
from datetime import datetime
import csv
import os

SIM_TIME = 8e-6
ANALYSIS_START = 0

def main():

    # Get current date and time
    now = datetime.now()
    date_time_str = now.strftime("%m-%d_%H-%M-%S")

    output_dir = "./optimization/{}/".format(date_time_str)
    os.makedirs(output_dir)
    runner =SimRunner(output_folder=output_dir, simulator=LTspice)

    # Initialize the netlist
    netlist = SpiceEditor("C:/Users/taf27/Desktop/Class-E-Optimization/GaN_Class_E_main.net")  # Specify your LTspice file here

    # Define the ranges of the components to test
    C1_values = np.linspace((440e-12)*0.5, 440e-12*1.5, 10)#[440e-12] #np.linspace(1e-12, 1e-9, 2)  # Example range for C1
    C2_values = np.linspace((250e-12)*0.5, (250e-12)*1.5, 40)#[250e-12] #np.linspace(1e-12, 1e-9, 2)  # Example range for C2
    C3_values = [10e-6] #[10e-6]
    C4_values = np.linspace((500e-12)*0.5, (500e-12)*1.5, 40) #[500e-12]
    L1_values = [4.2e-6]
    L2_values = np.linspace((66e-9)*0.5, 66e-9*1.5, 10)#[66e-9]
    VDD_values = [10]
    RL_values = [50]
    t_rf_values = [1e-12]
    t_on_values = [6.35e-9] #[5e-9]
    period_values = [25.38e-9] #[20e-9]
    freq_values = [39.4e6] #[50e6]
    combinations = itertools.product(C1_values, C2_values, C3_values, C4_values, L1_values, L2_values, VDD_values, RL_values, t_rf_values, t_on_values, period_values, freq_values)
    combinations_list = [{"C1":c1, "C2":c2, "C3":c3, "C4":c4, "L2":l2, "L1":l1, "VDD":vdd, "RL":rl, "T_RF": t_rf, "T_ON":t_on, "PERIOD":period, "FREQ":freq} for c1, c2, c3, c4, l1, l2, vdd, rl, t_rf, t_on, period, freq in combinations]
    print(str(len(combinations_list)) + " combinations to simulate")

    # File names
    text_filename = f"{output_dir}/map_{date_time_str}.txt"
    csv_filename = f"{output_dir}/map_{date_time_str}.csv"
    
    # Write to text file
    with open(text_filename, 'w') as text_file:
        for index, combination in enumerate(combinations_list):
            text_file.write(f"{index}: {combination}\n")

    # Write to CSV file
    with open(csv_filename, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Index", "C1", "C2", "C3", "C4", "L2", "L1", "VDD", "RL", "T_RF", "T_ON", "PERIOD", "FREQ"])  # Write header
        for index, combination in enumerate(combinations_list):
            writer.writerow([index, combination["C1"],  combination["C2"],  combination["C3"],  combination["C4"], combination["L2"],  combination["L1"],  combination["VDD"],  combination["RL"],  combination["T_RF"],  combination["T_ON"],  combination["PERIOD"],  combination["FREQ"]])

    
     # Write to CSV file
    output_filename = csv_filename = f"{output_dir}/results_{date_time_str}.csv"
    with open(output_filename, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        #Write Header
        writer.writerow(["Index", "C1", "C2", "C3", "C4", "L1", "L2", "VDD", "RL", "T_RF", "T_ON", "PERIOD", "FREQ", "EFFICIENCY", "POWER OUT", "PAE", "THD"])  # Write header
    # Record the best combination
    best_pae = 0
    best_pae_combination = []
    best_pae_combination_index = 0

    best_efficiency = 0
    best_efficiency_combination = []
    best_efficiency_combination_index = 0

    best_power_out = 0
    best_power_out_combination = []
    best_power_out_combination_index = 0

    run_num=0
    
    # Run the simulation for each combination
    for i  in range(len(combinations_list)):
        run_num += 1
        print(str(run_num) + " of " + str(len(combinations_list)))
        combination = combinations_list[i]
        C1 = combination["C1"]
        C2 = combination["C2"]
        C3 = combination["C3"]
        C4 = combination["C4"]
        L1 = combination["L1"]
        L2 = combination["L2"]
        VDD = combination["VDD"]
        RL = combination["RL"]
        T_RF = combination["T_RF"]
        T_ON =  combination["T_ON"]
        PERIOD = combination["PERIOD"]
        FREQ = combination["FREQ"]
        # Set the component values
        netlist.set_parameter("C1", C1)
        netlist.set_parameter("C2", C2)
        netlist.set_parameter("C3", C3)
        netlist.set_parameter("C4", C4)
        netlist.set_parameter("L1", L1)
        netlist.set_parameter("L2", L2)
        netlist.set_parameter("VDD", VDD)
        netlist.set_parameter("RL", RL)
        netlist.set_parameter("T_RF", T_RF)
        netlist.set_parameter("T_ON", T_ON)
        netlist.set_parameter("PERIOD", PERIOD)
        netlist.set_parameter("FREQ", FREQ)
        run_netlist_file = "GaN_Class_E_{}_{}.net".format(date_time_str, i)
        # Run the simulation
        raw,log = runner.run_now(netlist, run_filename=run_netlist_file)

        # Get the waveform data
        raw = RawRead("{}/GaN_Class_E_{}_{}.raw".format(output_dir,date_time_str, i))
        logfile = "{}/GaN_Class_E_{}_{}.log".format(output_dir,date_time_str, i)
        pae = calc_pae(logfile)
        efficiency = calc_efficiency(logfile)
        power_out = meas_power_out(logfile)
        thd = calc_thd(logfile)
        combinations_list[i]["efficiency"] = efficiency
        combinations_list[i]["power_out"] = power_out
        combinations_list[i]["pae"] = pae
        combinations_list[i]["thd"] = thd
        # Check if this is the best in any category
        if pae > best_pae:
            best_pae = pae
            best_pae_combination = combination
            best_pae_combination_index = i
        if efficiency > best_efficiency:
            best_efficiency = efficiency
            best_efficiency_combination = combination
            best_efficiency_combination_index = i
        if power_out > best_power_out:
            best_power_out = power_out
            best_power_out_combination = combination
            best_power_out_combination_index = run_num

        with open(output_filename, 'a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([run_num, C1,  C2, C3,  C4, L1, L2, VDD, RL, T_RF, T_ON, PERIOD, FREQ, efficiency, power_out, pae, thd])
        os.remove("{}/GaN_Class_E_{}_{}.log".format(output_dir,date_time_str, i))
        os.remove("{}/GaN_Class_E_{}_{}.net".format(output_dir,date_time_str, i))
        os.remove("{}/GaN_Class_E_{}_{}.op.raw".format(output_dir,date_time_str, i))
        os.remove("{}/GaN_Class_E_{}_{}.raw".format(output_dir,date_time_str, i))
                
    # Print the results and combinations
    # print(f"Best PAE: {best_pae}% \nBest PAE Combination: {best_pae_combination}")
    # print(f"Best efficiency: {best_efficiency}% \nBest PAE Combination: {best_efficiency_combination}")
    # print(f"Best power out: {best_power_out}% \nBest PAE Combination: {best_power_out_combination}")
    
    # Print the overall best results 
    print(f"Best PAE: {best_pae}% \nBest PAE Combination: {best_pae_combination_index}")
    print(f"Best efficiency: {best_efficiency}% \nBest PAE Combination: {best_efficiency_combination_index}")
    print(f"Best power out: {best_power_out} \nBest Power Out Combination: {best_power_out_combination_index}")
    
    # # Write to CSV file
    # output_filename = csv_filename = f"{output_dir}/results_{date_time_str}.csv"
    # with open(output_filename, 'w', newline='') as csv_file:
    #     writer = csv.writer(csv_file)
    #     writer.writerow(["Index", "C1", "C2", "C3", "C4", "L2", "L1", "VDD", "RL", "T_RF", "T_ON", "PERIOD", "FREQ", "EFFICIENCY", "POWER OUT", "PAE", "THD"])  # Write header
    #     for index, combination in enumerate(combinations_list):
    #         writer.writerow([index, combination["C1"],  combination["C2"], combination["C3"],  combination["C4"], combination["L2"],  combination["L1"],  combination["VDD"],  combination["RL"],  combination["T_RF"],  combination["T_ON"],  combination["PERIOD"], combination["FREQ"], combination["efficiency"],  combination["power_out"],  combination["pae"],  combination["thd"]])

def meas_power_out(logfile):
    return get_power("power_out", logfile)

def meas_dc_power(logfile):
    return get_power("dc_power", logfile)

def meas_gate_power(logfile):
    return get_power("gate_power", logfile)

def get_power(label, logfile):
    percentage = None

    with open(logfile, 'r') as log_file:
        for line in log_file:
            if label in line:
                # Split the line by ':' and then by '%'
                parts = line.split('=')
                if len(parts) > 1:
                    value_part = parts[1].strip().split(' ')[0].strip()
                    try:
                        power = abs(float(value_part))
                    except ValueError:
                        pass
                break
    return power

def calc_pae(logfile):
    power_out = meas_power_out(logfile)
    dc_power = meas_dc_power(logfile)
    gate_power = meas_gate_power(logfile)
    return 100 * ((power_out-gate_power)/dc_power)

def calc_power_at_freq(raw):
    # Step 2: Extract the waveform data
    voltage = raw.get_trace("V(vout)")
    voltage_data = voltage.get_wave()
    time = raw.get_time_axis()
    start_index = np.searchsorted(time, ANALYSIS_START, side='right')
    values = voltage_data
    
    # Determine the appropriate sampling interval
    desired_sampling_interval = 1e-9  # 1 nanosecond (1 GHz sampling rate)
    new_time = np.arange(time[0], time[-1], desired_sampling_interval)

    # Interpolate the values to the new time axis
    new_values = np.interp(new_time, time, values)

    # Step 3: Perform FFT using NumPy
    fft_values = np.fft.fft(new_values)
    fft_freqs = np.fft.fftfreq(len(new_values), desired_sampling_interval)
    fft_values = fft_values/np.sqrt(len(values))
    # Only keep positive frequencies up to a specified max frequency
    max_frequency = 10e8  # Replace with your desired max frequency in Hz (e.g., 100 MHz)
    positive_freq_indices = np.where((fft_freqs >= 0) & (fft_freqs <= max_frequency))
    positive_freqs = fft_freqs[positive_freq_indices]
    positive_fft_values = np.abs(fft_values[positive_freq_indices])

    # Convert to dB
    positive_fft_values_db = 20 * np.log10(positive_fft_values)
    # Diagnostic prints
    print(f"Max FFT magnitude: {positive_fft_values.max()}")
    print(f"Min FFT magnitude: {positive_fft_values.min()}")
    # Plotting the FFT result in dB
    plt.plot(positive_freqs, positive_fft_values_db)
    plt.xscale('log')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.title('FFT of the waveform (Positive Frequencies in dB)')
    plt.show()

def calc_efficiency(logfile):
    power_out = meas_power_out(logfile)
    dc_power = meas_dc_power(logfile) 
    return 100 * (power_out/dc_power)

def calc_thd(logfile):
    percentage = None
    target_string = "Total Harmonic Distortion:"

    with open(logfile, 'r') as log_file:
        for line in log_file:
            if target_string in line:
                # Split the line by ':' and then by '%'
                parts = line.split(':')
                if len(parts) > 1:
                    value_part = parts[1].strip().split('%')[0].strip()
                    try:
                        percentage = float(value_part)
                    except ValueError:
                        pass
                break

    return percentage

if __name__ == "__main__":
    main()