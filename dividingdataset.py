import pandas as pd

# Load the large CSV file
file_path = '/Users/sayeedkhan/Desktop/mainllm/train.csv'
data = pd.read_csv(file_path)

# Calculate the number of rows per chunk (for 3 parts)
rows_per_chunk = len(data) // 3

# Split the data into 3 parts
c1 = data.iloc[:rows_per_chunk]
c2 = data.iloc[rows_per_chunk:rows_per_chunk*2]
c3 = data.iloc[rows_per_chunk*2:]

# Save each part into a separate CSV file
c1.to_csv('train1.csv', index=False)
c2.to_csv('train2.csv', index=False)
c3.to_csv('train3.csv', index=False)

print("CSV files have been successfully created as non1.csv, non2.csv, and non3.csv")