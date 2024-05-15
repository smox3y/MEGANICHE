from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pickle
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

# Google Sheets API SCOPES
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Function to create Google Sheets service
def create_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('sheets', 'v4', credentials=creds)
    return service

MESSAGE_BUTTON_SELECTOR = 'div[role="button"][tabindex="0"]'  # Assuming the 'Message' button can be uniquely identified like this.
TEXT_BOX_SELECTOR = 'div[aria-label="Message"][contenteditable="true"]'
SEND_BUTTON_SELECTOR = "//div[@role='button'][@tabindex='0' and text()='Send']"


message_to_send = ("Hey! We would love to work with you for paid collaborations with your content. "
                   "What do you typically charge? And what sorts of brands do you typically work with?"
                   "If you already work with someone from our team, let us know.")
# Function to read Instagram links from Google Sheet
# Adjusted Function to read Instagram links from Google Sheet where column F is empty
def get_instagram_links_with_row_numbers(service, spreadsheet_id):
    # Fetch both Instagram links and their corresponding status in column F
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="IGOutreachDM!A2:F",
        majorDimension="ROWS"
    ).execute()
    values = result.get('values', [])
    
    # Generate a list of tuples (row number, Instagram link) for rows where column F is empty
    instagram_links_with_row_numbers = [
        (i + 2, row[0])  # i + 2 to account for header row and 1-based indexing
        for i, row in enumerate(values) if len(row) < 6 or not row[5]
    ]
    
    return instagram_links_with_row_numbers


# Function to send DMs on Instagram
def send_dms(driver, service, spreadsheet_id, instagram_links_with_row_numbers):
    for row_number, link in instagram_links_with_row_numbers:
        try:
            time.sleep(10)  # Ample time for the page to load and for all elements to be interactable
            driver.get(link)
            time.sleep(2)  # Ample time for the page to load and for all elements to be interactable
    
            # Attempt to find and click the 'Message' button
            found_message_button = False
            buttons = driver.find_elements(By.XPATH, "//div[@role='button']")
            for button in buttons:
                if 'Message' in button.text:
                    button.click()
                    found_message_button = True
                    time.sleep(4)  # Increased sleep time to ensure message dialog is fully loaded
                    break
            try:
                not_now_button = driver.find_element(By.XPATH, "//button[text()='Not Now']")
                not_now_button.click()
                print("Dismissed 'Not Now' popup.")
                time.sleep(5)  # Give some time for the popup to be dismissed
            except Exception as popup_exception:
                print("No 'Not Now' popup found or error dismissing it:", popup_exception)
            # If 'Message' button was found and clicked, proceed to send a message
            if found_message_button:
                text_box = driver.find_element(By.CSS_SELECTOR, TEXT_BOX_SELECTOR)
                text_box.send_keys(message_to_send)
                time.sleep(4)  # Ensure message is properly typed and message dialog is ready
                
                send_button = driver.find_element(By.XPATH, SEND_BUTTON_SELECTOR)
                send_button.click()
                time.sleep(1)  # Wait for message to be sent
                
                # Mark as "SENT" in Google Sheet
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f"IGOutreachDM!F{row_number}",
                    valueInputOption="USER_ENTERED",
                    body={"values": [["SENT"]]}
                ).execute()

                print(f"Message successfully sent for {link}")
            else:
                print(f"'Message' button not found for {link}")
        except Exception as e:
            print(f"An error occurred while processing {link}: {e}")


if __name__ == "__main__":
    service = create_service()
    spreadsheet_id = '1BntpUcd5HUi1LaWX6F_DVv__me53qp_xBflOOHxRxZQ'  # Replace with your actual spreadsheet ID
    instagram_links_with_row_numbers = get_instagram_links_with_row_numbers(service, spreadsheet_id)
    options = webdriver.ChromeOptions()
    # Add any Chrome options you require
    driver = webdriver.Chrome(options=options)
    try:
        send_dms(driver, service, spreadsheet_id, instagram_links_with_row_numbers)
    finally:
        driver.quit()
