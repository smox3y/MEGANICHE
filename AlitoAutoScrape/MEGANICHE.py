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
spreadsheet_id = '1BntpUcd5HUi1LaWX6F_DVv__me53qp_xBflOOHxRxZQ'

# Example usage
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=spreadsheet_id, range="Sheet1!A1:D5").execute()
rows = result.get('values', [])

print(rows)

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

def scrolling_function(driver, max_scrolls=200000, max_time=2000000):
    close_button_clicked = False
    scroll_count = 0
    start_time = time.time()
    influencer_links = []

    try:
        print('Starting scroll function')
        while True:
            if not close_button_clicked:
                try:
                    driver.refresh()  # Refresh the page to ensure starting from the top of the "For You" page
                    time.sleep(5)  # Wait for 5 seconds to ensure the page has loaded completely

                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.css-1ecw34m-DivCloseWrapper'))).click()
                    print('Found and clicked "Close" button.')
                    close_button_clicked = True
                except TimeoutException:
                    print('No "Close" button found, continuing..., assuming recurrence')
                    close_button_clicked = True
                    driver.get("https://www.tiktok.com/foryou")
                    driver.refresh()  # Refresh the page to ensure starting from the top of the "For You" page
                    time.sleep(5)  # Wait for 5 seconds to ensure the page has loaded completely

            while len(influencer_links) < 30 and scroll_count < max_scrolls and time.time() - start_time < max_time:
                WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.css-14bp9b0-DivItemContainer')))
                print('Video containers found')

                video_containers = driver.find_elements(By.CSS_SELECTOR, 'div.css-14bp9b0-DivItemContainer')            
                for container in video_containers:
                    try:
                        anchor = container.find_element(By.CSS_SELECTOR, 'a.avatar-anchor')
                        influ_url_full = anchor.get_attribute('href').split('?')[0]

                        if len(influ_url_full.split('/')) >= 4:
                            influ_url = '/'.join(influ_url_full.split('/')[:4]) + '/'
                        else:
                            influ_url = influ_url_full
                        
                        if influ_url not in influencer_links:
                            influencer_links.append(influ_url)
                            print("Found influencer URL:", influ_url)
                    except NoSuchElementException:
                        print("No 'avatar-anchor' link found in this item.")

                time.sleep(1)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(5)
                scroll_count += 1

            if len(influencer_links) >= 7:
                print(f"{len(influencer_links)} Influencer Links have been collected, executing influencer_function.")
                spreadsheet_id = '1olH8cna9cJjtoUeJS9iNVmJBTQ7FNWhzX7wzzWvpUXo'
                influencer_function(driver, influencer_links, service, spreadsheet_id)
                break
            elif scroll_count >= max_scrolls or time.time() - start_time >= max_time:
                print("Maximum scrolls or time reached without collecting enough links.")
                break

    except Exception as e:
        print(f'Error occurred in scrolling function: {e}')

    return driver, influencer_links


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
spreadsheet_id = '1BntpUcd5HUi1LaWX6F_DVv__me53qp_xBflOOHxRxZQ'  # Replace with your actual spreadsheet ID

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

            # Extract email(s) from userbio_text
            emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', userbio_text)
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
                'url': driver.current_url,
                'name': name_text,
                'followers': fe,
                'email': email_username,
                'extension': email_extension,
                'likes': likes_text,
                'Average Views': average_views,
                'Alito Ratio': average_views / fe if average_views and fe else None,
                'date': date.today().strftime('%Y-%m-%d'),
                'Aggregate': aggregate_email
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
    else:
        print("No new items to append.")


def main(driver, service, spreadsheet_id):
    while True:
        try:
            print("Starting scrolling...")
            driver, influencer_links = scrolling_function(driver, max_scrolls=2000, max_time=200000)

            if influencer_links:
                print("Ballsack empty!...")
            else:
                print("No new influencer links found. Restarting scrolling...")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                scrolling_function(driver, max_scrolls=20000, max_time=200000)

        except Exception as e:
            print(f"Error occurred: {e}")
            break  # Optional: Remove this line if you want the loop to continue even after an error 
          
if __name__=="__main__":
    print("Starting script...")
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.tiktok.com/foryou")
    print("WebDriver started and navigated to TikTok.")

    service = create_service()
    spreadsheet_id = '1BntpUcd5HUi1LaWX6F_DVv__me53qp_xBflOOHxRxZQ'
    main(driver, service, spreadsheet_id)

    driver.quit()
    print("WebDriver closed.")