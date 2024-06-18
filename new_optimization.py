import numpy as np
import matplotlib.pyplot as plt
from PyLTSpice import LTspice, SpiceEditor, SimRunner, RawRead
from datetime import datetime
import csv
import os


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
    C2_values = np.linspace(215e-12, 790e-12, 100)#[250e-12] #np.linspace(1e-12, 1e-9, 2)  # Example range for C2
    C4_values = np.linspace(215e-12, 790e-12, 100) #[500e-12]
    RL_values = [25, 50, 100, 200]

    run_num=0

    for RL in RL_values:

        # Write to CSV file
        output_filename = f"{output_dir}/results_{str(RL)}ohm_{date_time_str}.csv"
        with open(output_filename, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            #Write Header
            writer.writerow(["Index", "C2", "C4", "VDD", "RL", "EFFICIENCY", "POWER OUT", "PAE", "THD"])  # Write header
        for C2 in C2_values:
            for C4 in C4_values:
                power_out = 1e5
                VDD = 11
                #keep running until we get a combination with output power below 8W 
                while power_out >=8:
                    run_num += 1
                    print(f"Run number: {str(run_num)}")
                    VDD = VDD - 1
                    # Set the component values
                    netlist.set_parameter("C2", C2)
                    netlist.set_parameter("C4", C4)
                    netlist.set_parameter("VDD", VDD)
                    netlist.set_parameter("RL", RL)
                    run_netlist_file = "GaN_Class_E_{}_{}.net".format(date_time_str, run_num)
                    # Run the simulation
                    raw,log = runner.run_now(netlist, run_filename=run_netlist_file)
                    # Get the waveform data
                    raw = RawRead("{}/GaN_Class_E_{}_{}.raw".format(output_dir,date_time_str, run_num))
                    logfile_path = "{}/GaN_Class_E_{}_{}.log".format(output_dir,date_time_str, run_num)
                    pae = calc_pae(logfile_path)
                    efficiency = calc_efficiency(logfile_path)
                    power_out = meas_power_out(logfile_path)
                    thd = calc_thd(logfile_path)
                    with open(output_filename, 'a', newline='') as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow([run_num, C2, C4, VDD, RL, efficiency, power_out, pae, thd])
                    os.remove("{}/GaN_Class_E_{}_{}.log".format(output_dir,date_time_str, run_num))
                    os.remove("{}/GaN_Class_E_{}_{}.net".format(output_dir,date_time_str, run_num))
                    os.remove("{}/GaN_Class_E_{}_{}.op.raw".format(output_dir,date_time_str, run_num))
                    os.remove("{}/GaN_Class_E_{}_{}.raw".format(output_dir,date_time_str, run_num))

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