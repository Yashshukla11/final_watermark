import pandas as pd
import requests
import os
import json

# Replace with the path to your Excel file
excel_path = '/Users/yashshukla/Desktop/final_watermark/data/original_excel/Untitled spreadsheet.xlsx'


# Replace with the directory where you want to save the images
save_directory = '/Users/yashshukla/Desktop/final_watermark/images/down'

# Create the directory if it doesn't exist
os.makedirs(save_directory, exist_ok=True)

# Load the Excel file
try:
    df = pd.read_excel(excel_path, header=None)  # Load without header
except ImportError:
    print("Please install 'openpyxl' using pip or conda to read Excel files.")
    exit()

# Function to download and save images
def download_image(url, save_path):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
                print(f"Downloaded: {save_path}")
        else:
            print(f"Failed to download {url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Exception occurred while downloading {url}: {str(e)}")

# Function to clean JSON-like data
def clean_json_data(json_str):
    # Replace single quotes with double quotes
    json_str = json_str.replace("'", '"')
    return json_str

# Only decode JSON data from the first cell in the DataFrame
# row_index = 0
# col_index = 0
# json_data = df.iloc[row_index, col_index]

# try:
#     # Clean JSON-like data
#     cleaned_json_data = clean_json_data(json_data)

#     # Load JSON data (assuming it's a string representation of a list of dictionaries)
#     images = json.loads(cleaned_json_data)

#     # Iterate over each image dictionary
#     for image_data in images:
#         url = image_data['url']
#         filename = os.path.basename(image_data['path'])  # Using 'path' as the filename
#         save_path = os.path.join(save_directory, filename)
#         download_image(url, save_path)

# except json.JSONDecodeError as e:
#     print(f"Error decoding JSON in cell ({row_index}, {col_index}): {str(e)}")

# except KeyError as e:
#     print(f"Missing key in JSON data in cell ({row_index}, {col_index}): {str(e)}")

# except Exception as e:
#     print(f"Exception occurred in cell ({row_index}, {col_index}): {str(e)}")

# print('Download process complete.')
