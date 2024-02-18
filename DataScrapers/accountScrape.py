from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv
import os

# Other utility functions (like style_num_to_float) remain the same
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Updated function to fetch data from a TikTok link using Selenium
def fetch_tiktok_data(link):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(link)

    # Wait for the content to load
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "strong[data-e2e='video-views']")))
    except TimeoutException:
        print(f"Timeout while loading {link}")
        driver.switch_to.window(driver.window_handles[0])
        return None

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    video_views_elements = soup.find_all('strong', attrs={'data-e2e': 'video-views'})
    video_views = [style_num_to_float(element.get_text()) for element in video_views_elements[3:8]]

    item = {
        'Influencer': link.replace('https://www.tiktok.com/@', ''),
        'link': link,
        'video 1': video_views[0] if len(video_views) > 0 else "NO account found",
        'video 2': video_views[1] if len(video_views) > 1 else "NO account found",
        'video 3': video_views[2] if len(video_views) > 2 else "NO account found",
        'Average Views': sum(video_views) / len(video_views) if video_views else "NO account found",
    }

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return item
# Function to convert styled numbers to float
def style_num_to_float(style_num):
    if 'K' in style_num:
        return float(style_num.replace('K', '')) * 1000
    elif 'M' in style_num:
        return float(style_num.replace('M', '')) * 1000000
    else:
        return float(style_num)

# Function to create a dictionary with "NO account found" for all columns
def no_account_found_dict(link):
    return {key: "NO account found" for key in ['Influencer', 'link', 'video 1', 'video 2', 'video 3', 'Average Views', 'Multiplier']}

# Main function to process data
def get_data():
    print("Current Working Directory: ", os.getcwd())

    csv_columns = ['Influencer', 'link', 'video 1', 'video 2', 'video 3', 'Average Views', 'Multiplier']
    csvfile = open('Account_Data.csv', 'w', newline='', encoding="utf-8")
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()

    input_file = open('AccountLinks.txt', 'r')
    file_data = input_file.read().split('\n')

    for link in file_data:
        print(f"Processing link: {link}")  # Debugging statement

        try:
            item = fetch_tiktok_data(link)
            print(f"Fetched data: {item}")  # Debugging statement
            writer.writerow(item)
        except Exception as e:
            error_item = no_account_found_dict(link)
            writer.writerow(error_item)
            print(f'Error processing account {link}: {e}')

    csvfile.close()
    print("Thank you!")

# Run the script
if __name__ == '__main__':
    get_data()
