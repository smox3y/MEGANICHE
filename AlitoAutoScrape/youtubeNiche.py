import time
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import date
import requests
import re

# Function to fetch existing creators from BlitzPay
def fetch_creators():
    response = requests.get('https://blitz-backend-nine.vercel.app/api/crm/creator/creators')
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch creators")
        return []

# Function to add a new creator to BlitzPay
def add_creator(creator_data):
    print("Attempting to add creator with data:", creator_data)
    response = requests.post('https://blitz-backend-nine.vercel.app/api/crm/creator/add', json=creator_data)
    if response.status_code == 200:
        print("Creator added successfully")
    else:
        print("Failed to add creator. Response:", response.text)

# Function to convert styled numbers to float
def style_num_to_float(value):
    if 'B' in value:
        return float(value.replace('B', '')) * 1000000000
    if 'M' in value:
        return float(value.replace('M', '')) * 1000000
    elif 'K' in value:
        return float(value.replace('K', '')) * 1000
    else:
        return float(value)

# Function to scroll and collect YouTube usernames
def scrolling_function(driver, target_username_count=20, max_scroll_attempts=100):
    usernames = set()
    scroll_attempts = 0

    while len(usernames) < target_username_count and scroll_attempts < max_scroll_attempts:
        last_height = driver.execute_script("return document.documentElement.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(3)
            new_height = driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        channel_elements = driver.find_elements(By.XPATH, '//div[@id="text-container"]//a[@class="yt-simple-endpoint style-scope yt-formatted-string"]')
        for channel_element in channel_elements:
            href = channel_element.get_attribute('href')
            if href and '/@' in href:
                username = href.split('/')[-1]
                if username not in usernames:
                    usernames.add(username)
                    print(f"Collected username: {username}")

        scroll_attempts += 1
        print(f"Attempt {scroll_attempts}: Collected {len(usernames)} unique usernames.")
        if len(usernames) >= target_username_count:
            break

    print(f"Finished collecting usernames. Total unique usernames collected: {len(usernames)}")
    return list(usernames)

# Function to fetch account data for a username
def style_num_to_float(value):
    # Remove any non-numeric characters except for 'K', 'M', 'B', '.', and ','
    value = re.sub(r'[^\d.KMB]', '', value)
    if 'B' in value:
        return float(value.replace('B', '')) * 1000000000
    if 'M' in value:
        return float(value.replace('M', '')) * 1000000
    elif 'K' in value:
        return float(value.replace('K', '')) * 1000
    else:
        return float(value)

def fetch_account_data(driver, username):
    print(f"Trying to fetch account data for: {username}")
    account_url = f"https://www.youtube.com/{username}/about"
    driver.get(account_url)
    time.sleep(3)

    try:
        # Click the "more" button if it exists
        try:
            more_button = driver.find_element(By.XPATH, '//button[contains(@class, "truncated-text-wiz__inline-button")]')
            driver.execute_script("arguments[0].click();", more_button)
            time.sleep(2)
        except NoSuchElementException:
            print(f"No 'more' button found for {username}")

        # Extract account data
        title = driver.find_element(By.XPATH, '//yt-dynamic-text-view-model//h1').text
        subscriber_count_text = driver.find_element(By.XPATH, '//yt-content-metadata-view-model//span[contains(text(),"subscribers")]').text
        description = driver.find_element(By.XPATH, '//yt-attributed-string[@id="description-container"]').text

        # Convert subscriber count to float
        subscriber_count = re.sub(r'\D', '', subscriber_count_text)
        following = int(style_num_to_float(subscriber_count_text))

        email_matches = re.findall(r'[\w\.-]+@[\w\.-]+', description)
        email = email_matches[0] if email_matches else None

        return {
            'link': account_url,
            'username': username,
            'title': title,
            'following': following,
            'description': description,
            'email': email
        }
    except NoSuchElementException as e:
        print(f"Error fetching data for {username}: {e}")
        return None

# Main function to process and add creators for a single search term
def process_search_term(driver, search_term):
    search_url = f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}"
    driver.get(search_url)
    time.sleep(3)

    print(f"Collecting YouTube usernames for search term: {search_term}...")
    usernames = scrolling_function(driver, target_username_count=20, max_scroll_attempts=20)
    print(f"Collected {len(usernames)} unique usernames for search term: {search_term}.")

    if usernames:
        print(f"Fetching account data for search term: {search_term}...")
        creators = fetch_creators()
        existing_emails = [creator['email'] for creator in creators if creator['email']]
        account_data_list = []

        for username in usernames:
            account_data = fetch_account_data(driver, username)
            if account_data and (account_data['email'] is None or account_data['email'] not in existing_emails):
                add_creator(account_data)
                account_data_list.append(account_data)

        for account_data in account_data_list:
            print(account_data)
    else:
        print(f"No usernames collected for search term: {search_term}. Consider increasing scroll attempts or checking the selectors.")

# Start the script
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
    # options.add_argument("--headless=new")  # Run in headless mode

    driver = uc.Chrome(options=options)
    print("WebDriver started.")

    try:
        search_terms = []
        print("Enter up to 5 search terms. Press Enter without typing anything to finish input.")

        for i in range(5):
            term = input(f"Enter search term {i+1}: ")
            if term:
                search_terms.append(term)
            else:
                break

        for search_term in search_terms:
            process_search_term(driver, search_term)
            time.sleep(5)  # Adding a delay between search term processing for better stability

    except KeyboardInterrupt:
        print("Script interrupted by user. Closing WebDriver.")
    finally:
        driver.quit()
