import pandas as pd

def main(file_path, column_name, n):
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)

    # Filter the DataFrame for rows where "POWER OUT" <= 8
    temp_df = df[df["POWER OUT"] <= 8]
    filtered_df = temp_df[temp_df["POWER OUT"] >= 5]

    # Sort the filtered DataFrame by the specified column in descending order
    sorted_df = filtered_df.sort_values(by=column_name, ascending=False)

    # Get the top N rows
    top_n_rows = sorted_df.head(n)
    for index, row in top_n_rows.iterrows():
        print(f"C2: {row["C2"]} C4: {row["C4"]} VDD: {row["VDD"]} PAE:{row["PAE"]}, POWER OUT:{row["POWER OUT"]}, THD:{row["THD"]}")

    return top_n_rows

# Example usage
if __name__ == "__main__":
    filepaths = ['C:/Users/taf27/Desktop/Class-E-Optimization/optimization/06-12_22-41-35/results_25ohm_06-12_22-41-35.csv',
                 'C:/Users/taf27/Desktop/Class-E-Optimization/optimization/06-12_22-41-35/results_50ohm_06-12_22-41-35.csv',
                 'C:/Users/taf27/Desktop/Class-E-Optimization/optimization/06-12_22-41-35/results_100ohm_06-12_22-41-35.csv',
                 'C:/Users/taf27/Desktop/Class-E-Optimization/optimization/06-12_22-41-35/results_200ohm_06-12_22-41-35.csv']
    column_name = 'EFFICIENCY'
    n = 2
    for file_path in filepaths:
        top_n = main(file_path, column_name, n)
