import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re

def init_driver():
    options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_settings.popups": 0,
             "download.default_directory": r"/Users/yashshukla/Desktop/final_watermark/images/down/",
             "directory_upgrade": True}
    options.add_experimental_option("prefs", prefs)
    service = Service(exeutable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    return driver

def rehost_images(final_folder):
    driver = init_driver()
    driver.get('https://postimages.org/')
    
    # Step 1: Wait for element with id "ddinput"
    upload_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, 'ddinput'))
    )
    upload_button.click()
    
    # Step 2: Find the file input element for uploading images
    file_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
    )
    
    # Step 3: Prepare the file paths for all images in the final folder
    file_paths = []
    print(final_folder)
    for filename in os.listdir(final_folder):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            image_path = os.path.join(final_folder, filename)
            file_paths.append(image_path)
    
    # Log the file paths
    print("File paths to upload:")
    for path in file_paths:
        print(path)
    
    # Step 4: Upload all images at once by sending all file paths to the file input
    if file_paths:
        file_input.send_keys('\n'.join(file_paths))
    else:
        print("No images found in the specified folder.")
        return
    
    # Determine which XPath to use based on the number of images
    if len(file_paths) == 1:
        # Single image case
        textarea_xpath = '/html/body/div[1]/div/div[3]/div/form/div[2]/div[2]/div/input'
    else:
        # Multiple images case (current implementation)
        textarea_xpath = '/html/body/div[1]/div/div[1]/div[3]/div/form/div[3]/div/textarea'
    
    # Step 5: Wait for images to upload and process
    print(f"Waiting for the element with XPath: {textarea_xpath}")
    textarea = WebDriverWait(driver, 300).until(
        EC.presence_of_element_located((By.XPATH, textarea_xpath))
    )
    
    # Step 6: Get URLs from the appropriate element
    if len(file_paths) == 1:
        urls = [textarea.get_attribute('value')]
    else:
        urls = textarea.get_attribute('value').split('\n')
    
    img_url_regex = r"\[img\](https://i\.postimg\.cc/[^[]+)\[/img\]"
    
    # Print URLs to the terminal
    print("Uploaded URLs:")
    
    hostedUrls = []
    
    # Save URLs to a file
    for url in urls:
        match = re.search(img_url_regex, url)
        if match:
            extracted_url = match.group(1)
            print(extracted_url)
            hostedUrls.append(str(extracted_url))
        else:
            print(url)
    
    # Step 7: Delete images from final folder
    for filename in os.listdir(final_folder):
        file_path = os.path.join(final_folder, filename)
        os.remove(file_path)
        print(f"Deleted {filename} from final folder.")
    
    return hostedUrls

# Example usage:
if __name__ == "__main__":
    final_folder_path = '/Users/yashshukla/Desktop/final_watermark/images/down'
    rehost_images(final_folder_path)
