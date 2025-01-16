import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import requests
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

# Instagram login credentials
credentials = [
    {"username": "useblitz.co", "password": "Resistance5"},
    {"username": "thecultureclub_", "password": "#xCultureClubx24*"},
    {"username": "iseeoneworld", "password": "#Oikrtd90"}
]

# Instagram message details
MESSAGE_TO_SEND = (
    "Hey! We would love to work with you for paid collaborations with your content. "
    "What do you typically charge? And what sorts of brands do you typically work with? "
    "If you already work with someone from our team, let us know."
)
SENT_MESSAGE_SELECTOR = 'span.x1lliihq.x193iq5w.x6ikm8r.x10wlt62.xlyipyv.xuxw1ft'

# Fetch creators from the API
def fetch_instagram_creators():
    response = requests.get('https://blitz-backend-nine.vercel.app/api/crm/creator/creators')
    if response.status_code == 200:
        creators = response.json()
        return [creator for creator in creators if 'instagram.com' in creator['link'] and creator['status'] != 'IGDM']
    else:
        print("Failed to fetch creators")
        return []

# Update creator status in the API
def update_creator_status(creator_id, status, username, link=None):
    data = {'id': creator_id, 'status': status, 'username': username}
    if link:
        data['link'] = link
    response = requests.post('https://blitz-backend-nine.vercel.app/api/crm/creator/update', json=data)
    if response.status_code == 200:
        print(f"Creator ID {creator_id} status updated to {status}")
    else:
        print(f"Failed to update status for Creator ID {creator_id}. Response: {response.text}")

# Log in to Instagram
def login_to_instagram(driver, credentials):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)  # Allow page to load

    for cred in credentials:
        try:
            username_input = driver.find_element(By.CSS_SELECTOR, 'input[name="username"]')
            password_input = driver.find_element(By.CSS_SELECTOR, 'input[name="password"]')

            username_input.clear()
            password_input.clear()

            username_input.send_keys(cred["username"])
            password_input.send_keys(cred["password"])

            login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            login_button.click()

            time.sleep(10)  # Wait for login

            if "instagram.com" in driver.current_url and "/accounts/login/" not in driver.current_url:
                print(f"Successfully logged in as {cred['username']}")
                return True

        except Exception as e:
            print(f"Login attempt failed for {cred['username']}: {e}")

    print("All login attempts failed.")
    return False

# Send DMs to creators
def send_dms(driver, instagram_creators):
    for creator in instagram_creators:
        try:
            link = creator['link']
            creator_id = creator['id']
            username = creator['username']

            driver.get(link)
            time.sleep(10)  # Allow time for the page to load

            # Locate and click the Message button
            buttons = driver.find_elements(By.XPATH, "//div[@role='button']")
            for button in buttons:
                if 'Message' in button.text:
                    button.click()
                    time.sleep(5)
                    break
            else:
                print(f"'Message' button not found for {link}")
                continue

            # Check if the message was already sent
            sent_message_elements = driver.find_elements(By.CSS_SELECTOR, SENT_MESSAGE_SELECTOR)
            for element in sent_message_elements:
                if MESSAGE_TO_SEND in element.text:
                    print(f"Message already sent for {link}")
                    update_creator_status(creator_id, "IGDM", username, link)
                    break
            else:
                # Type and send the message
                text_box = driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Message"][contenteditable="true"]')
                text_box.send_keys(MESSAGE_TO_SEND)
                time.sleep(2)

                send_button = driver.find_element(By.XPATH, "//div[@role='button'][@tabindex='0' and text()='Send']")
                send_button.click()
                time.sleep(5)

                update_creator_status(creator_id, "IGDM", username, link)
                print(f"Message successfully sent to {link}")

        except NoSuchElementException as e:
            print(f"Element not found while processing {link}: {e}")
        except Exception as e:
            print(f"An error occurred while processing {link}: {e}")

# Main function
def main(driver):
    if not login_to_instagram(driver, credentials):
        print("Failed to log in. Exiting script.")
        driver.quit()
        return

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
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    options.add_argument("--headless=new")  # Run in headless mode

    driver = uc.Chrome(options=options)

    try:
        main(driver)
    finally:
        driver.quit()
        print("WebDriver closed.")
