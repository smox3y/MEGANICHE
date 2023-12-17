import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google.oauth2 import service_account
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
# Function to convert styled numbers to float
def style_num_to_float(style_num):
    if 'K' in style_num:
        return float(style_num.replace('K', '')) * 1000
    elif 'M' in style_num:
        return float(style_num.replace('M', '')) * 1000000
    else:
        return float(style_num)

#################### new direct to sheets approach

# Function to process each video link
def process_video_link(link):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(link)

    # Wait for the content to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "strong[data-e2e='like-count']")))

    # Now use BeautifulSoup to parse the page source from Selenium
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Initialize the data dictionary with default values
    data = {
        'link': link,
        'Views': 'Not Found',
        'Likes': 'Not found',
        'Shares': 'Not found',
        'Saves': 'Not found',
        'Comments': 'Not found',
    }

    # Attempt to find each piece of data and update the dictionary if found
    likes_element = soup.find('strong', attrs={'data-e2e': 'like-count'})
    if likes_element:
        data['Likes'] = likes_element.get_text()

    comments_element = soup.find('strong', attrs={'data-e2e': 'comment-count'})
    if comments_element:
        data['Comments'] = comments_element.get_text()

    saves_element = soup.find('strong', attrs={'data-e2e': 'undefined-count'})  # Verify this selector
    if saves_element:
        data['Saves'] = saves_element.get_text()

    shares_element = soup.find('strong', attrs={'data-e2e': 'share-count'})
    if shares_element:
        data['Shares'] = shares_element.get_text()

    # Make sure to close the driver after each link is processed
    driver.quit()

    return data

# Main function to iterate over links and write data to CSV
def scrape_tiktok_videos(payload):
    print("Processing payload:", payload)
    # The ID of your spreadsheet
    SPREADSHEET_ID = payload['sheetId']
    # Specify your Google Sheets API credentials
    SERVICE_ACCOUNT_FILE = 'credentials1.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    creds = None
    creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Connect to the Sheets API
    service = build('sheets', 'v4', credentials=creds)

    # Example: Read data from the sheet
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range="Execution!C3:C").execute()
    values = result.get('values', [])
    
    results = []
    for row in values:
        if row:  # Check if the row is not empty
            link = row[0]
            item = process_video_link(link)
            results.append([item['Views'], item['Likes'], item['Comments'], item['Shares']])

    # Write results back to the sheet
    update_range = "Execution!I3"  # Assuming the data starts from A2
    value_input_option = "USER_ENTERED"
    update_body = {
        "values": results
    }

    request = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=update_range,
        valueInputOption=value_input_option, body=update_body)
    response = request.execute()
    print("Data written to sheet:", response)


# Run the script
if __name__ == '__main__':
    scrape_tiktok_videos()

