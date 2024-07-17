import time
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import date
import re

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
        subscriber_count = driver.find_element(By.XPATH, '//yt-content-metadata-view-model//span[contains(text(),"subscribers")]').text
        description = driver.find_element(By.XPATH, '//yt-attributed-string[@id="description-container"]').text

        subscriber_count = re.sub(r'\D', '', subscriber_count)
        email_matches = re.findall(r'[\w\.-]+@[\w\.-]+', description)
        email = email_matches[0] if email_matches else 'N/A'

        return {
            'username': username,
            'title': title,
            'subscribers': int(subscriber_count) if subscriber_count.isdigit() else 0,
            'description': description,
            'email': email
        }
    except NoSuchElementException as e:
        print(f"Error fetching data for {username}: {e}")
        return None

# Main function
def main(driver):
    search_term = input("Enter a search term for YouTube: ")
    search_url = f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}"
    driver.get(search_url)
    time.sleep(3)

    print("Collecting YouTube usernames...")
    usernames = scrolling_function(driver, target_username_count=20, max_scroll_attempts=20)
    print(f"Collected {len(usernames)} unique usernames.")

    if usernames:
        print("Fetching account data...")
        account_data_list = []
        for username in usernames:
            account_data = fetch_account_data(driver, username)
            if account_data:
                account_data_list.append(account_data)

        for account_data in account_data_list:
            print(account_data)
    else:
        print("No usernames collected. Consider increasing scroll attempts or checking the selectors.")

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
        main(driver)
    except KeyboardInterrupt:
        print("Script interrupted by user. Closing WebDriver.")
        driver.quit()
