import os
import pandas as pd

# Function to merge prediction files
def merge_prediction_files(prediction_dir):
    # List all files in the directory
    all_files = [os.path.join(prediction_dir, f) for f in os.listdir(prediction_dir) if f.endswith('.csv')]
    
    # Create an empty list to store dataframes
    df_list = []
    
    # Read each CSV file and append to the list
    for file in all_files:
        df = pd.read_csv(file)
        df_list.append(df)
    
    # Concatenate all dataframes
    merged_df = pd.concat(df_list, ignore_index=True)
    
    return merged_df

# Function to remove overlapping indexes with test.csv
def filter_non_overlapping(merged_df, test_df):
    # Find common "index" values
    overlapping_indexes = test_df['index'].isin(merged_df['index'])
    
    # Filter out rows from test_df that overlap with merged_df
    non_overlapping_df = test_df[~overlapping_indexes]
    
    return non_overlapping_df

# Paths (replace with your actual paths)
prediction_dir = "/Users/sayeedkhan/Desktop/mainllm/out"  # directory containing prediction CSV files
test_csv_path = "/Users/sayeedkhan/Desktop/mainllm/test.csv"           # path to the test.csv file

# Step 1: Merge all prediction files
merged_predictions = merge_prediction_files(prediction_dir)

# Step 2: Load the test.csv
test_df = pd.read_csv(test_csv_path)

# Step 3: Filter out overlapping rows
non_overlapping_df = filter_non_overlapping(merged_predictions, test_df)

# Step 4: Save the non-overlapping data to a new CSV file
output_path = "non_overlapping.csv"  # Specify where to save the output file
non_overlapping_df.to_csv(output_path, index=False)

print(f"Non-overlapping data has been saved to {output_path}")