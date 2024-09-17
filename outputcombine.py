import os
import pandas as pd

# Define the directory containing the CSV files
csv_dir = '/Users/sayeedkhan/Desktop/mainllm/out'  # Update this with your directory path

# Initialize an empty list to hold the dataframes
df_list = []

# Loop through all CSV files in the directory
for file in os.listdir(csv_dir):
    if file.endswith('.csv'):
        file_path = os.path.join(csv_dir, file)
        # Read each CSV file and append the dataframe to the list
        df = pd.read_csv(file_path)
        df_list.append(df)

# Concatenate all dataframes into a single dataframe
combined_df = pd.concat(df_list, ignore_index=True)

# Convert 'index' column to numeric to handle sorting properly
combined_df['index'] = pd.to_numeric(combined_df['index'], errors='coerce')

# Remove duplicate rows based on the 'index' column, keeping the first occurrence
unique_df = combined_df.drop_duplicates(subset='index')

# Sort by 'index' column
sorted_df = unique_df.sort_values(by='index')

# Save the sorted dataframe to a new CSV file
output_file = 'combined_sorted_unique_file.csv'  # Update this if you want a different filename
sorted_df.to_csv(output_file, index=False)

print(f"Combined, sorted, and deduplicated CSV saved to {output_file}")