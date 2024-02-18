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
import time
# from capcha import main_loop
import re
import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle

# The SCOPES should be the ones required for the Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

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
spreadsheet_id = '1Rp7dYchjaKN4dpchToDCXNuC_4A7ZAD7cf-8gfVO3pA'

# Example usage
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Sheet1!A1:D5").execute()
rows = result.get('values', [])

print(rows)

def get_user_input():
    while True:
        choice = input("What would you like to browse today? Enter 'sound' or 'hashtag': ").strip().lower()
        if choice in ['sound', 'hashtag']:
            break
        else:
            print("Invalid input. Please enter 'sound' or 'hashtag'.")

    links_or_hashtags = []
    print(f"Enter the {choice} links/hashtags (max 100). Type 'done' when finished:")

    while len(links_or_hashtags) < 100:
        input_value = input("> ").strip()
        if input_value.lower() == 'done':
            break
        links_or_hashtags.append(input_value)

    return choice, links_or_hashtags

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
    
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def new_scrolling_function(driver, choice, links_or_hashtags, service, spreadsheet_id):
    if choice == 'sound':
        for link in links_or_hashtags:
            driver.get(link)
            time.sleep(3)  # Wait for the page to load

            influencer_links = []
            try:
                for _ in range(100):  # Repeat process 100 times
                    try:
                        music_items = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-e2e="music-item"]'))
                        )

                        if len(music_items) >= 2:
                            second_item = music_items[1]
                            driver.execute_script("arguments[0].click();", second_item)
                            time.sleep(2)

                            try:
                                anchor_element = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a[data-e2e="browse-user-avatar"]'))
                                )
                                influencer_link = anchor_element.get_attribute('href')
                                if influencer_link and influencer_link not in influencer_links:
                                    influencer_links.append(influencer_link)
                                    print("Influencer link:", influencer_link)
                            except TimeoutException:
                                print("Unable to find the influencer link in the new content.")

                        else:
                            print("Not enough music items found.")

                    except NoSuchElementException:
                        print("Music items not found on the page.")

                    try:
                        next_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-e2e="arrow-right"]'))
                        )
                        next_button.click()
                        time.sleep(3)
                    except TimeoutException:
                        print("Next button not found or not clickable. Moving to the next link.")
                        break

            except TimeoutException:
                print("An error occurred while navigating through videos.")

            if influencer_links:
                influencer_function(driver, influencer_links, service, spreadsheet_id)

    return influencer_links


    # Add logic for 'hashtag' choice if required
    # ...

### average view grabber
def fetch_tiktok_data(link):
    print("trying to fetch avg view data", link)
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all elements with 'data-e2e="video-views"'

    video_elements = soup.select("div[data-e2e='user-post-item']")
    view_counts = []

    for video in video_elements[2:8]:  # Only consider the first three videos
            view_count_element = video.select_one("strong[data-e2e='video-views']")
            if view_count_element:
                views = style_num_to_float(view_count_element.text)
                view_counts.append(views)
    
    average_views = sum(view_counts) / len(view_counts) if view_counts else None
    item = {
        'Average Views': average_views,
    }
    
    return item

service = create_service()
spreadsheet_id = '1Rp7dYchjaKN4dpchToDCXNuC_4A7ZAD7cf-8gfVO3pA'  # Replace with your actual spreadsheet ID

def influencer_function(driver, links, service, spreadsheet_id):
    service = create_service()
    list_items = []
    range_name = 'Raw'
    csv_file = 'MEGANICHE_Data.csv'
    
    # ... [Your existing code for handling the CSV file] ...

    for page in links:
        print("Opening link: ", page)
        driver.execute_script("window.open('{}');".format(page))
        time.sleep(5)
        driver.switch_to.window(driver.window_handles[-1])
        
        try:
            userbio_element = driver.find_element(By.CSS_SELECTOR, '.css-4ac4gk-H2ShareDesc')
            userbio_text = userbio_element.text
    
            name_element = driver.find_element(By.CSS_SELECTOR, '.css-1nbnul7-DivShareTitleContainer .css-10pb43i-H2ShareSubTitle')
            name_text = name_element.text

            followers_element = driver.find_element(By.CSS_SELECTOR, '[title="Followers"]')
            followers_text = followers_element.text

            likes_element = driver.find_element(By.CSS_SELECTOR, '[title="Likes"]')
            likes_text = likes_element.text

            # Fetch average view data
            video_views_elements = driver.find_elements(By.CSS_SELECTOR, "strong[data-e2e='video-views']")
            video_views = [style_num_to_float(element.text) for element in video_views_elements[3:8]]

            average_views = sum(video_views) / len(video_views) if video_views else None
            fe = style_num_to_float(followers_text)

            item = {
                'url': driver.current_url,
                'name': name_text,
                'followers': followers_text,
                'email': ' , '.join(re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', userbio_text)),
                'a' : '',
                'b' : '',
                'likes': likes_text,
                'x' : '',
                'y' : '',
                'z' : '',
                'Average Views': average_views,
                'Alito Ratio': average_views / fe if average_views and fe else None,
                'q' : '',
                'v' : '',
                'date': date.today().strftime('%Y-%m-%d')
            }

            if item not in list_items:
                list_items.append(item)

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        except Exception as e:
            print(f"Error processing page {page}: {e}")

    if list_items:  # Check if list_items is not empty
        values = [[item[key] for key in item] for item in list_items]
        body = {'values': values}
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range='Raw',
            valueInputOption='USER_ENTERED', body=body).execute()

        df_new = pd.DataFrame(list_items)
        try:
            final_df = pd.concat([df, df_new]).drop_duplicates(subset=['url'])
        except:
            final_df = df_new
        final_df.to_csv(csv_file, index=False)
        print("Appended to sheet and CSV!")

    else:
        print("No new items to append.")

def main(driver, service, spreadsheet_id, choice, links_or_hashtags):
    print("WebDriver started and navigating...")
    for link in links_or_hashtags:
        driver.get(link)
        print(f"Navigated to {link}")

    while True:
        try:
            print("Starting scrolling...")
            new_scrolling_function(driver, choice, [link], service, spreadsheet_id)
            influencer_links = new_scrolling_function(driver, choice, [link], service, spreadsheet_id)

            if influencer_links:
                print("Ballsack empty!...")
            else:
                print("No new influencer links found. Restarting scrolling...")
            
        except Exception as e:
            print(f"Error occurred: {e}")
            break  # Optional: Remove this line if you want the loop to continue even after an error 
        finally:
            driver.quit()
            print("WebDriver closed.")

if __name__=="__main__":
    choice, links_or_hashtags = get_user_input()

    print("Starting script...")
    options = webdriver.ChromeOptions()
    # [Your existing WebDriver configuration options]
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)

    service = create_service()
    spreadsheet_id = '1Rp7dYchjaKN4dpchToDCXNuC_4A7ZAD7cf-8gfVO3pA'
    main(driver, service, spreadsheet_id, choice, links_or_hashtags)

    driver.quit()
    print("WebDriver closed.")