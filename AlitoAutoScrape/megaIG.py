from datetime import date
from  selenium import webdriver
import pygsheets
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time, random
# from capcha import main_loop
import re
import os
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle
# Google Sheets API SCOPES
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Function to create Google Sheets service
def create_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens.
    # It is created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no valid credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    service = build('sheets', 'v4', credentials=creds)
    return service

# Use the service object
service = create_service()
spreadsheet_id = '1olH8cna9cJjtoUeJS9iNVmJBTQ7FNWhzX7wzzWvpUXo'
# Function to style numbers (e.g., converting '1M' to 1000000)
def style_num_to_float(value):
    """
    Convert string number with style to a float.
    For example, '3.1M' becomes 3100000.0, '5K' becomes 5000.0.
    """
    if 'M' in value:
        return float(value.replace('M', '')) * 1000000
    elif 'K' in value:
        return float(value.replace('K', '')) * 1000
    else:
        return float(value)

# Scrolling function adapted for Instagram (Placeholder - Implement scrolling and data collection for Instagram Reels)
def double_click_videos(driver, max_attempts=12):
    attempts = 0
    while attempts < max_attempts:
        # Find all video containers on the page
        video_containers = driver.find_elements(By.CSS_SELECTOR, 'div[class*="x78zum5"] video')
        for video_container in video_containers:
            # Perform a double-click action on the video element
            ActionChains(driver).double_click(video_container).perform()
            time.sleep(1)  # Wait a bit for any potential response

        attempts += 1
        print(f"Double-clicked on videos, attempt {attempts}")

def scrolling_function(driver, target_link_count=30, max_scroll_attempts=100):
    influencer_links = set()
    scroll_attempts = 0
    video_seen = set()  # To keep track of videos already interacted with

    while len(influencer_links) < target_link_count and scroll_attempts < max_scroll_attempts:
        # Get the current scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to the bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load the page
            time.sleep(2)

            # Find all video containers on the page
            video_containers = driver.find_elements(By.CSS_SELECTOR, 'div[class*="x78zum5"] video')
            for video_container in video_containers:
                video_src = video_container.get_attribute('src')
                # Check if the video has been seen before
                if video_src not in video_seen:
                    # Perform a double-click action on the video element
                    ActionChains(driver).double_click(video_container).perform()
                    video_seen.add(video_src)
                    # Wait 2 seconds to allow for the page to properly load after double-clicking
                    time.sleep(2)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # After scrolling, collect links if they haven't been collected before
        profile_links = driver.find_elements(By.CSS_SELECTOR, 'a[aria-label*="reels"]')
        for link in profile_links:
            href = link.get_attribute('href')
            if href not in influencer_links:
                influencer_links.add(href)

        scroll_attempts += 1
        print(f"Attempt {scroll_attempts}: Collected {len(influencer_links)} unique links.")
        if len(influencer_links) >= target_link_count:
            break

    print(f"Finished collecting links. Total unique links collected: {len(influencer_links)}")
    return list(influencer_links)

# Function to fetch Instagram Reel data (Placeholder - Implement logic for fetching data from Instagram Reels)
### average view grabber
def fetch_reels_data(link):
    print("Trying to fetch avg view data for:", link)
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Assuming 'view count' is contained within a specific element - this selector might need to be adjusted
    view_counts_elements = soup.select("span[class*='view-count']")
    view_counts = []

    for element in view_counts_elements[1:6]:  # Adjust based on how many reels you want to consider
        views_text = element.text.replace('views', '').strip()
        views = style_num_to_float(views_text)  # Reusing the provided conversion function
        view_counts.append(views)
    
    average_views = sum(view_counts) / len(view_counts) if view_counts else 0
    return {'Average Views': average_views}

# Influencer data collection function adapted for Instagram
def influencer_function(driver, links, service, spreadsheet_id):
    service = create_service()
    list_items = []
    range_name = 'Raw'
    csv_file = 'MEGANICHE_Data.csv'
    
    # Your existing code for handling the CSV file continues here...

    for page in links:
        print("Opening link: ", page)
        driver.execute_script("window.open('{}');".format(page))
        time.sleep(5)
        driver.switch_to.window(driver.window_handles[-1])
        
        try:
            # Adjusted selectors based on Instagram's HTML structure for Reels
            # Extracting bio information
            name_element = driver.find_element(By.CSS_SELECTOR, 'h2[class*="x1lliihq"]')
            page_name = name_element.text

            bio_element = driver.find_element(By.CSS_SELECTOR, 'h1[class*="_ap3a _aaco"]')
            bio_text = bio_element.text

            # Extracting followers count
            followers_element = driver.find_element(By.CSS_SELECTOR, 'a[href*="/followers/"] span')
            followers_text = followers_element.text

            # Extracting following count (if needed)
            following_element = driver.find_element(By.CSS_SELECTOR, 'a[href*="/following/"] span')
            following_text = following_element.text

            # Extract email(s) from bio_text
            emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', bio_text)
            email_text = ', '.join(emails)
            video_views_elements = driver.find_elements(By.CSS_SELECTOR, "span[class*='view-count']")
            video_views = [style_num_to_float(element.text) for element in video_views_elements[3:8]]
            average_views = sum(video_views) / len(video_views) if video_views else None
            fe = style_num_to_float(followers_text)
            # Additional details like name, likes, average views would need to be adapted
            # from your provided HTML structure if available
            
            emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', bio_text)
            email_text = ' , '.join(emails)

            # Initialize email and extension to empty if no email is found
            email_username = ''
            email_extension = ''
            aggregate_email = ''


            # If emails are found, split the first email into username and extension
            if emails:
                cleaned_email = emails[0].lstrip('-')
                email_parts = emails[0].split('@')
                email_username = email_parts[0]
                email_extension = email_parts[1] if len(email_parts) > 1 else ''
                aggregate_email = cleaned_email # Use the original email

            item = {
                'url': page,
                'name': page_name,
                'followers': fe,
                'email': email_username,
                'extension': email_extension,
                'x': "",
                'Average Views': average_views,
                'Alito Ratio': average_views / fe if average_views and fe else None,
                'date': date.today().strftime('%Y-%m-%d'),
                'Aggregate': aggregate_email
                # Add additional fields as needed
            }

            if item not in list_items:
                list_items.append(item)

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        except Exception as e:
            print(f"Error processing page {page}: {e}")


    if list_items:  # Check if list_items is not empty
            # Read the existing data to find the next empty row in column A
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range='Raw!A:A').execute()
            values = result.get('values', [])

            # Find the first empty row (assuming column A contains data for each entry)
            next_empty_row = len(values) + 1

            # Set the range to start appending from the next empty row
            append_range = f'Raw!A{next_empty_row}'

            # Prepare the data to be appended
            append_values = [[item[key] for key in item] for item in list_items]
            body = {'values': append_values}

            # Append the data
            service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=append_range,
                valueInputOption='USER_ENTERED',
                body=body).execute()

            # Convert list_items to a DataFrame
            df_new = pd.DataFrame(list_items)
            try:
                # Concatenate with existing DataFrame and remove duplicates
                final_df = pd.concat([df, df_new]).drop_duplicates(subset=['url'])
            except:
                # If concatenation fails, use the new DataFrame as the final DataFrame
                final_df = df_new

            # Save the final DataFrame to a CSV file
            final_df.to_csv(csv_file, index=False)
            print("Appended to sheet and CSV!")

# Main function adapted for Instagram
def main(driver):
    print("Collecting influencer links...")
    influencer_links = scrolling_function(driver, target_link_count=30, max_scroll_attempts=20)
    print(f"Collected {len(influencer_links)} influencer links.")
    
    if len(influencer_links) >= 20:
        print("Proceeding to process influencer data...")
        influencer_function(driver, influencer_links, service, spreadsheet_id)
    else:
        print("Insufficient links collected. Consider increasing scroll attempts or checking the CSS selectors.")

if __name__ == "__main__":
    print("Starting script...")
    options = webdriver.ChromeOptions()
    # [WebDriver configuration remains the same]
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.instagram.com/reels")  # Navigate to Instagram Reels
    print("WebDriver started and navigated to Instagram Reels.")

    try:
        while True:  # Start an infinite loop
            main(driver)
            time.sleep(10)  # Optional: Wait for 10 seconds or any time you deem necessary before restarting the main function
    except KeyboardInterrupt:
        print("Script interrupted by user. Closing WebDriver.")
        driver.quit()