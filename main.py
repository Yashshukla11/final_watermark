import os
import pandas as pd
import json
from downloader import download_image
from watermark_remover import remove_watermark
from rehoster import rehost_images
from excel_updater import update_excel
import os
import time
import requests
import shutil
from threading import Thread, Lock
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from watermark_remover import init_driver_with_proxy, fetch_proxies, process_images_with_proxy

# Paths
EXCEL_PATH = '/Users/yashshukla/Desktop/final_watermark/data/original_excel/Untitled spreadsheet.xlsx'
DOWNLOAD_FOLDER = '/Users/yashshukla/Desktop/final_watermark/images/down'
FINAL_FOLDER = '/Users/yashshukla/Desktop/final_watermark/images/final'
DOWNLOADS_FOLDER = '/Users/yashshukla/Downloads'
EXCEL_COPY_PATH = '/Users/yashshukla/Desktop/final_watermark/data/processed_excel/Untitled spreadsheet_processed.xlsx'

# Create necessary folders if they don't exist
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(FINAL_FOLDER, exist_ok=True)
os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)

# Load the Excel file
df = pd.read_excel(EXCEL_PATH, header=None)

shutil.rmtree(DOWNLOAD_FOLDER)
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


# Iterate over each cell in the DataFrame
for row_index in range(len(df)):
    for col_index in range(len(df.columns)):
        # Extract JSON-like data from the cell
        json_data = df.iloc[row_index, col_index]

        # try:
        if(True):
            # Clean JSON-like data
            cleaned_json_data = json_data.replace("'", '"')
            
            # Load JSON data (assuming it's a string representation of a list of dictionaries)
            images = json.loads(cleaned_json_data)
            print(images)
            print(f"Processing images in cell ({row_index}, {col_index})")
            
            # URL to fetch proxy list
            # proxy_list_url = "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc"

            # Fetch proxies
            # proxies = fetch_proxies(proxy_list_url)
            
            # Download images for current cell
            for image_data in images:
                url = image_data['url']
                filename = os.path.basename(image_data['path'])  # Using 'path' as the filename
                save_path = os.path.join(DOWNLOAD_FOLDER, filename)
                download_image(url, save_path)
                
            down_folder = '/Users/yashshukla/Desktop/final_watermark/images/down'
            # threads = []
            num_images = len([f for f in os.listdir(down_folder) if f.endswith('.jpg') or f.endswith('.png')])
            
            options = webdriver.ChromeOptions()
            prefs = {"profile.default_content_settings.popups": 0,
                        "download.default_directory": r"/Users/yashshukla/Desktop/final_watermark/images/down/",
                        "directory_upgrade": True}
            options.add_experimental_option("prefs", prefs)
            service = Service(exeutable_path='chromedriver.exe')
            driver = webdriver.Chrome(service=service, options=options)
            
            # Check if download folder is empty
            if os.listdir(DOWNLOAD_FOLDER):
                # Remove watermark from downloaded images
                for filename in os.listdir(DOWNLOAD_FOLDER):
                    image_path = os.path.join(DOWNLOAD_FOLDER, filename)
                    remove_watermark(driver, image_path, DOWNLOAD_FOLDER, DOWNLOADS_FOLDER)
            else:
                print(f"{DOWNLOAD_FOLDER} is empty. Rehosting images instead.")
                # Rehost images and get new URLs
                new_urls = rehost_images(DOWNLOAD_FOLDER)
                
                # Update Excel file with new URLs
                update_excel(EXCEL_COPY_PATH, row_index, col_index, new_urls)
                continue  # Skip cleanup since there are no images to delete
            
            # Rehost images and get new URLs
            new_urls = rehost_images(DOWNLOAD_FOLDER)
            
            print(new_urls)
            
            # Update Excel file with new URLs
            update_excel(EXCEL_COPY_PATH, row_index, col_index, new_urls)
            
            # Clean up: delete images from down and final folders
            for file in os.listdir(DOWNLOAD_FOLDER):
                os.remove(os.path.join(DOWNLOAD_FOLDER, file))
            for file in os.listdir(FINAL_FOLDER):
                os.remove(os.path.join(FINAL_FOLDER, file))
            
        # except Exception as e:
        #     print(f"Error processing cell ({row_index}, {col_index}): {str(e)}")
        #     continue

print('Processing complete.')
