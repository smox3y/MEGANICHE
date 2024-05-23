from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests
import re

# Instagram message details
MESSAGE_BUTTON_SELECTOR = 'div[role="button"][tabindex="0"]'
TEXT_BOX_SELECTOR = 'div[aria-label="Message"][contenteditable="true"]'
SEND_BUTTON_SELECTOR = "//div[@role='button'][@tabindex='0' and text()='Send']"
MESSAGE_TO_SEND = (
    "Hey! We would love to work with you for paid collaborations with your content. "
    "What do you typically charge? And what sorts of brands do you typically work with? "
    "If you already work with someone from our team, let us know."
)

# Function to fetch creators with "instagram.com" in their link and status is "cold"
def fetch_instagram_creators():
    response = requests.get('https://blitz-backend-nine.vercel.app/crm/creator/creators')
    if response.status_code == 200:
        creators = response.json()
        instagram_creators = [creator for creator in creators if 'instagram.com' in creator['link'] and creator['status'] == 'cold']
        return instagram_creators
    else:
        print("Failed to fetch creators")
        return []

# Function to update creator status to "DM"
def update_creator_status(creator_id, status):
    response = requests.post('https://blitz-backend-nine.vercel.app/crm/creator/update', json={'id': creator_id, 'status': status})
    if response.status_code == 200:
        print(f"Creator ID {creator_id} status updated to {status}")
    else:
        print(f"Failed to update status for Creator ID {creator_id}. Response: {response.text}")

# Function to send DMs on Instagram
def send_dms(driver, instagram_creators):
    for creator in instagram_creators:
        try:
            link = creator['link']
            creator_id = creator['id']
            driver.get(link)
            time.sleep(8)  # Allow time for the page to load

            # Attempt to find and click the 'Message' button
            found_message_button = False
            buttons = driver.find_elements(By.XPATH, "//div[@role='button']")
            for button in buttons:
                if 'Message' in button.text:
                    button.click()
                    found_message_button = True
                    time.sleep(4)  # Ensure the message dialog is fully loaded
                    break

            try:
                not_now_button = driver.find_element(By.XPATH, "//button[text()='Not Now']")
                not_now_button.click()
                print("Dismissed 'Not Now' popup.")
                time.sleep(5)  # Allow time for the popup to be dismissed
            except Exception as popup_exception:
                print("No 'Not Now' popup found or error dismissing it:", popup_exception)

            # If 'Message' button was found and clicked, proceed to send a message
            if found_message_button:
                text_box = driver.find_element(By.CSS_SELECTOR, TEXT_BOX_SELECTOR)
                text_box.send_keys(MESSAGE_TO_SEND)
                time.sleep(4)  # Ensure the message is properly typed

                send_button = driver.find_element(By.XPATH, SEND_BUTTON_SELECTOR)
                send_button.click()
                time.sleep(1)  # Wait for the message to be sent

                # Update the creator status to "DM"
                update_creator_status(creator_id, "DM")

                print(f"Message successfully sent for {link}")
            else:
                print(f"'Message' button not found for {link}")
        except Exception as e:
            print(f"An error occurred while processing {link}: {e}")

# Main function
def main(driver):
    instagram_creators = fetch_instagram_creators()
    if instagram_creators:
        send_dms(driver, instagram_creators)
    else:
        print("No Instagram creators found.")

if __name__ == "__main__":
    print("Starting script...")
    options = webdriver.ChromeOptions()
    # Add any required Chrome options
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.instagram.com/")  # Navigate to Instagram

    # Allow time to input credentials
    input("Please log in to Instagram and then press Enter to continue...")

    print("WebDriver started and navigated to Instagram.")

    try:
        main(driver)
    finally:
        driver.quit()
        print("WebDriver closed.")
