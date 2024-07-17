import time
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import date
import requests
from bs4 import BeautifulSoup
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

# Function to scroll and collect Instagram influencer links
def scrolling_function(driver, target_link_count=30, max_scroll_attempts=100):
    influencer_links = set()
    scroll_attempts = 0
    video_seen = set()

    while len(influencer_links) < target_link_count and scroll_attempts < max_scroll_attempts:
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            video_containers = driver.find_elements(By.CSS_SELECTOR, 'div[class*="x78zum5"] video')
            for video_container in video_containers:
                video_src = video_container.get_attribute('src')
                if video_src not in video_seen:
                    ActionChains(driver).double_click(video_container).perform()
                    video_seen.add(video_src)
                    time.sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        profile_links = driver.find_elements(By.CSS_SELECTOR, 'a[aria-label*="reels"]')
        for link in profile_links:
            href = link.get_attribute('href')
            if href not in influencer_links:
                influencer_links.add(href)
        scroll_attempts += 1
        print(f"Attempt {scroll_attempts}: Collected {len(influencer_links)} unique links.")
        if len(influencer_links) >= target_link_count:
            break
    print(f"Finished collecting links. Total unique links collected: {len(influencer_links)}")
    return list(influencer_links)

# Function to fetch Instagram Reel data
def fetch_reels_data(link):
    print("Trying to fetch avg view data for:", link)
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    view_counts_elements = soup.select("span[class*='view-count']")
    view_counts = [style_num_to_float(element.text.replace('views', '').strip()) for element in view_counts_elements[1:6]]
    average_views = sum(view_counts) / len(view_counts) if view_counts else 0
    return {'Average Views': average_views}

# Function to process influencer data and add to BlitzPay
def influencer_function(driver, links):
    list_items = []
    creators = fetch_creators()
    existing_emails = [creator['email'] for creator in creators]

    for page in links:
        driver.execute_script("window.open('{}');".format(page))
        time.sleep(5)
        driver.switch_to.window(driver.window_handles[-1])

        try:
            name_element = driver.find_element(By.CSS_SELECTOR, 'h2[class*="x1lliihq"]')
            page_name = name_element.text
            bio_element = driver.find_element(By.CSS_SELECTOR, 'span[class*="_ap3a _aaco _aacu _aacx _aad7 _aade"]')
            bio_text = bio_element.text
            followers_element = driver.find_element(By.CSS_SELECTOR, 'a[href*="/followers/"] span')
            followers_text = followers_element.text
            emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', bio_text)
            email_username = email_extension = aggregate_email = ''

            if emails:
                cleaned_email = emails[0].lstrip('-')
                email_parts = cleaned_email.split('@')
                email_username = email_parts[0]
                email_extension = email_parts[1] if len(email_parts) > 1 else ''
                aggregate_email = cleaned_email

            average_views = fetch_reels_data(page)['Average Views']
            followers = style_num_to_float(followers_text)

            item = {
                'link': driver.current_url,
                'username': page_name,
                'following': followers,
                'email': aggregate_email,
                'bio_link': bio_text,
                'avg_views': average_views,
                'date_sourced': date.today().strftime('%Y-%m-%d')
            }

            if aggregate_email and aggregate_email not in existing_emails:
                add_creator(item)
                list_items.append(item)

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        except Exception as e:
            print(f"Error processing page {page}: {e}")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

# Main function
def main(driver):
    print("Collecting influencer links...")
    influencer_links = scrolling_function(driver, target_link_count=30, max_scroll_attempts=20)
    print(f"Collected {len(influencer_links)} influencer links.")

    if len(influencer_links) >= 20:
        print("Proceeding to process influencer data...")
        influencer_function(driver, influencer_links)
    else:
        print("Insufficient links collected. Consider increasing scroll attempts or checking the CSS selectors.")

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
    driver.get("https://www.instagram.com/reels")
    print("WebDriver started and navigated to Instagram Reels.")

    try:
        while True:
            main(driver)
            time.sleep(5)
    except KeyboardInterrupt:
        print("Script interrupted by user. Closing WebDriver.")
        driver.quit()
