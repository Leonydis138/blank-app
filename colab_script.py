
# Install necessary libraries
!pip install pandas

# Importing libraries
import pandas as pd
import json

# Load the JSON data
with open('Self-Improving Code Analyzer_ Iterative Development__answer_ (1).json', 'r') as file:
    data = json.load(file)

# Convert the JSON data to a DataFrame for easier manipulation
# Assuming the data is structured as a list of dictionaries
# If it's a single dictionary, we can wrap it in a list
if isinstance(data, dict):
    data = [data]

# Create a DataFrame
df = pd.DataFrame(data)

# Display the head of the DataFrame
print(df.head())

# Save the DataFrame to a CSV file for cloud storage
# This will allow you to access it later in Google Drive
# Make sure to mount Google Drive first
from google.colab import drive

drive.mount('/content/drive')

# Save the DataFrame to a CSV file in Google Drive
csv_file_path = '/content/drive/My Drive/self_improving_code_analyzer.csv'
df.to_csv(csv_file_path, index=False)

print('Data saved to Google Drive at:', csv_file_path)
