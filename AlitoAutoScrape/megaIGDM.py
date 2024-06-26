import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
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
SENT_MESSAGE_SELECTOR = f"span.x1lliihq.x193iq5w.x6ikm8r.x10wlt62.xlyipyv.xuxw1ft"

# Function to fetch creators with "instagram.com" in their link and status is "cold"
def fetch_instagram_creators():
    response = requests.get('https://blitz-backend-nine.vercel.app/crm/creator/creators')
    if response.status_code == 200:
        creators = response.json()
        instagram_creators = [creator for creator in creators if 'instagram.com' in creator['link'] and creator['status'] not in ('IGMDM', 'OTHER', 'DM')]
        return instagram_creators
    else:
        print("Failed to fetch creators")
        return []

# Function to update creator status
def update_creator_status(creator_id, status, link=None):
    data = {'id': creator_id, 'status': status}
    if link:
        data['link'] = link
    response = requests.post('https://blitz-backend-nine.vercel.app/crm/creator/update', json=data)
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

            # Check if the message was already sent
            try:
                sent_message_elements = driver.find_elements(By.CSS_SELECTOR, SENT_MESSAGE_SELECTOR)
                for element in sent_message_elements:
                    if MESSAGE_TO_SEND in element.text:
                        print(f"Message already sent for {link}")
                        update_creator_status(creator_id, "DM", link)
                        break
                else:
                    raise Exception("No matching message found")
            except Exception as e:
                print(f"No previous message found: {e}")

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
                update_creator_status(creator_id, "DM", link)

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
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = uc.Chrome(options=options)
    driver.get("https://www.instagram.com/")  # Navigate to Instagram

    # Allow time to input credentials
    input("Please log in to Instagram and then press Enter to continue...")

    print("WebDriver started and navigated to Instagram.")

    try:
        main(driver)
    finally:
        driver.quit()
        print("WebDriver closed.")
