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
message_to_send = "Hey! We would love to work with you for paid collaborations with your content."
# Function to read Instagram links from Google Sheet
def get_instagram_links(service, spreadsheet_id):
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="IGOutreachDM!A2:A").execute()
    values = result.get('values', [])
    return [row[0] for row in values if row]  # Return list of Instagram links

# Function to send DMs on Instagram
# Function to send DMs on Instagram
def send_dms(driver, service, spreadsheet_id, instagram_links):
    for index, link in enumerate(instagram_links, start=2):  # Adjusting start index to match sheet row numbers
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
                    time.sleep(5)  # Increased sleep time to ensure message dialog is fully loaded
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
                time.sleep(5)  # Ensure message is properly typed and message dialog is ready
                
                send_button = driver.find_element(By.XPATH, SEND_BUTTON_SELECTOR)
                send_button.click()
                time.sleep(5)  # Wait for message to be sent
                
                # Mark as "SENT" in Google Sheet
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f"IGOutreachDM!F{index}",
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
    spreadsheet_id = '1olH8cna9cJjtoUeJS9iNVmJBTQ7FNWhzX7wzzWvpUXo'  # Replace with your actual spreadsheet ID
    instagram_links = get_instagram_links(service, spreadsheet_id)
    options = webdriver.ChromeOptions()
    # Add any Chrome options you require
    driver = webdriver.Chrome(options=options)
    try:
        send_dms(driver, service, spreadsheet_id, instagram_links)
    finally:
        driver.quit()
