import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import date
import requests

# Message details
MESSAGE_TO_SEND = (
    "Hey! We would love to work with you for paid collaborations with your content. "
    "What do you typically charge? And what sorts of brands do you typically work with? "
    "If you already work with someone from our team, let us know."
)

# Function to fetch existing creators from BlitzPay
def fetch_creators():
    response = requests.get('https://blitz-backend-nine.vercel.app/crm/creator/creators')
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch creators")
        return []

# Function to add a new creator to BlitzPay
def add_creator(creator_data):
    print("Attempting to add creator with data:", creator_data)
    response = requests.post('https://blitz-backend-nine.vercel.app/crm/creator/add', json=creator_data)
    if response.status_code == 200:
        print("Creator added successfully")
    else:
        print("Failed to add creator. Response:", response.text)

# Function to collect unique Twitter usernames
def collect_twitter_usernames(driver, max_scrolls=5, max_usernames=100):
    usernames = set()
    scroll_count = 0

    while scroll_count < max_scrolls and len(usernames) < max_usernames:
        user_elements = driver.find_elements(By.XPATH, '//div[@data-testid="User-Name"]//a[@role="link"]')
        for user_element in user_elements:
            try:
                username = user_element.get_attribute('href').split('/')[-1]
                if username:
                    usernames.add(username)
                    if len(usernames) >= max_usernames:
                        break
            except Exception as e:
                print(f"Error collecting username: {e}")
                continue

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # Allow time for new tweets to load
        scroll_count += 1

    return list(usernames)

# Function to send DM on Twitter
def send_dm_on_twitter(driver, profile_link):
    driver.get(profile_link)
    time.sleep(5)  # Allow time for the page to load

    try:
        message_button = driver.find_element(By.XPATH, "//button[@data-testid='sendDMFromProfile']")
        message_button.click()
        time.sleep(5)  # Allow time for the message dialog to open

        text_box = driver.find_element(By.XPATH, "//div[@data-testid='dmComposerTextInputRichTextInputContainer']//div[@contenteditable='true']")
        text_box.send_keys(MESSAGE_TO_SEND)
        time.sleep(2)  # Ensure the message is properly typed

        send_button = driver.find_element(By.XPATH, "//button[@data-testid='dmComposerSendButton']")
        send_button.click()
        time.sleep(2)  # Wait for the message to be sent

        print(f"Message successfully sent for {profile_link}")
        return True
    except (NoSuchElementException, TimeoutException) as e:
        print(f"An error occurred while sending DM to {profile_link}: {e}")
        return False

# Main function
def main(driver):
    print("Collecting Twitter usernames...")
    usernames = collect_twitter_usernames(driver, max_scrolls=5, max_usernames=20)  # Adjust limits as needed
    unique_usernames = list(set(usernames))  # Ensure uniqueness

    if unique_usernames:
        print(f"Collected {len(unique_usernames)} unique usernames.")
        profile_links = [f"https://twitter.com/{username}" for username in unique_usernames]

        for profile_link in profile_links:
            success = send_dm_on_twitter(driver, profile_link)
            if success:
                creator_data = {
                    'link': profile_link,
                    'username': profile_link.split('/')[-1],
                    'date_sourced': date.today().strftime('%Y-%m-%d')
                }
                add_creator(creator_data)
            else:
                print(f"Failed to send DM for {profile_link}")
    else:
        print("No Twitter usernames found.")

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
    driver.get("https://twitter.com/login")  # Navigate to Twitter

    # Allow time to input credentials
    input("Please log in to Twitter and then press Enter to continue...")

    print("WebDriver started and navigated to Twitter.")

    try:
        main(driver)
    finally:
        driver.quit()
        print("WebDriver closed.")
