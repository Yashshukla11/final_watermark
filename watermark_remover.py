import os
import time
import requests
from threading import Thread, Lock
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Function to fetch proxy list from URL
def fetch_proxies(url):
    response = requests.get(url)
    proxies = []
    if response.status_code == 200:
        data = response.json()
        for item in data['data']:
            ip = item['ip']
            port = item['port']
            proxies.append(f"{ip}:{port}")
    return proxies

# Function to initialize WebDriver with a proxy
def init_driver_with_proxy(proxy):
    options = Options()
    prefs = {
        "profile.default_content_settings.popups": 0,
        "download.default_directory": r"/Users/yashshukla/Desktop/final_watermark/images/down/",
        "directory_upgrade": True
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument(f'--proxy-server=socks4://{proxy}')
    service = Service(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Function to clear all cookies and site data
def clear_all_data(driver):
    driver.execute_cdp_cmd('Storage.clearDataForOrigin', {
        "origin": "*",
        "storageTypes": "all"
    })
    driver.delete_all_cookies()

# Function to remove watermark from an image
def remove_watermark(driver, image_path, final_folder, downloads_folder):
    try:
        # Clear all cookies and site data
        clear_all_data(driver)

        # Navigate to a new instance of the website
        driver.get('about:blank')
        driver.get('https://www.watermarkremover.io/')
        
        # Click on the upload button
        upload_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, 'UploadImage__HomePage'))
        )
        upload_button.click()

        # Wait for the file input dialog to appear and handle the file upload
        time.sleep(3)  # Adjust wait time as needed
        
        # Handling file upload using selenium directly (not pyautogui)
        file_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
        )
        file_input.send_keys(image_path)

        time.sleep(5)  # Adjust wait time as needed
        
        # Wait for the image to be processed for 'Remove Text'
        try:
            remove_text_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[2]/div/div[3]/div/div/div[2]/div/div[1]/div/label/span/span[2]'))
            )
            remove_text_button.click()
        except:
            pass

        # Additional wait time for processing stability
        time.sleep(5)

        # Wait for 'Remove Logo' button to be clickable and then click it
        try:
            remove_logo_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[2]/div/div[3]/div/div/div[2]/div/div[2]/div/label/span/span[2]'))
            )
            remove_logo_button.click()
        except:
            pass

        # Additional wait time for processing stability
        time.sleep(5)
        
        # Click on the download button
        download_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[2]/div/div[3]/div/div/div[3]/div/div[1]/div/div/button'))
        )
        download_button.click()

        # Additional wait time for processing stability
        time.sleep(2)

        # Get the original filename without extension
        original_filename = os.path.splitext(os.path.basename(image_path))[0]

        # Delete the original image from the 'down' folder
        os.remove(image_path)
        print(f"Deleted original image {image_path} from the 'down' folder.")
    except Exception as e:
        print(f"Error removing watermark: {str(e)}")
        return False
    return True

# URL to fetch proxy list
proxy_list_url = "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc"

# Fetch proxies
proxies = fetch_proxies(proxy_list_url)
if not proxies:
    print("No proxies fetched. Exiting...")
    exit(1)

# Path to the 'down' folder containing images
down_folder = '/Users/yashshukla/Desktop/final_watermark/images/down'

# Path to the Downloads folder
downloads_folder = '/Users/yashshukla/Downloads'

# Create the final folder if it doesn't exist
final_folder = '/Users/yashshukla/Desktop/final_watermark/images/down'
os.makedirs(final_folder, exist_ok=True)

# Shared counter for image indexing and a lock for thread safety
image_index = 0
index_lock = Lock()

# Function to process images with different proxies
def process_images_with_proxy(proxy):
    global image_index
    while True:
        with index_lock:
            images = [f for f in os.listdir(down_folder) if f.endswith('.jpg') or f.endswith('.png')]
            if image_index >= len(images):
                break
            image_path = os.path.join(down_folder, images[image_index])
            image_index += 1

        driver = init_driver_with_proxy(proxy)
        success = remove_watermark(driver, image_path, final_folder, downloads_folder)
        driver.quit()  # Close the driver after processing the image
        if success:
            print(f"Successfully processed image {image_path} with proxy {proxy}")
            break  # Exit loop if watermark removal is successful
        print(f"Retrying image {image_path} with proxy {proxy}")
        time.sleep(10)  # Add a small delay before the next iteration

# Start processing images with different proxies
threads = []
for proxy in proxies:
    thread = Thread(target=process_images_with_proxy, args=(proxy,))
    thread.start()
    threads.append(thread)

# Wait for all threads to finish
for thread in threads:
    thread.join()
