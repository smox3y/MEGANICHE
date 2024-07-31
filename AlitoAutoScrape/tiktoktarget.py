import time
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import date
import requests
import re
import os
import pandas as pd
from bs4 import BeautifulSoup

# Function to fetch creators from BlitzPay
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

# Function to scroll and collect TikTok links by clicking the next button
def scrolling_function(driver, target_count=20, max_scrolls=2000, max_time=2000):
    scroll_count = 0
    start_time = time.time()
    influencer_links = []

    try:
        print('Starting scroll function')
        while len(influencer_links) < target_count and scroll_count < max_scrolls and time.time() - start_time < max_time:
            WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.css-x6f6za-DivContainer-StyledDivContainerV2')))
            account_links = driver.find_elements(By.CSS_SELECTOR, 'div.css-85dfh6-DivInfoContainer a[href*="/@"]')
            for link in account_links:
                try:
                    account_url = link.get_attribute('href')
                    if account_url not in influencer_links:
                        influencer_links.append(account_url)
                        print(f"Found influencer URL: {account_url}")
                        if len(influencer_links) >= target_count:
                            break
                except NoSuchElementException:
                    print("No influencer link found in this item.")
            
            # Click the next button to go to the next video
            next_button = driver.find_element(By.CSS_SELECTOR, 'button[data-e2e="arrow-right"]')
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(3)
            scroll_count += 1
    except Exception as e:
        print(f'Error occurred in scrolling function: {e}')
    return driver, influencer_links

# Function to fetch TikTok data
def fetch_tiktok_data(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    video_elements = soup.select("div[data-e2e='user-post-item']")
    view_counts = [style_num_to_float(video.select_one("strong[data-e2e='video-views']").text) for video in video_elements[2:8] if video.select_one("strong[data-e2e='video-views']")]
    average_views = sum(view_counts) / len(view_counts) if view_counts else None
    return {'Average Views': average_views}

# Function to process influencers
def influencer_function(driver, links):
    list_items = []
    creators = fetch_creators()
    existing_emails = [creator['email'] for creator in creators]

    for page in links:
        driver.execute_script("window.open('{}');".format(page))
        time.sleep(5)
        driver.switch_to.window(driver.window_handles[-1])
        
        try:
            userbio_element = driver.find_element(By.CSS_SELECTOR, '.css-1s5lw4c-H2ShareDesc')
            userbio_text = userbio_element.text
            name_element = driver.find_element(By.CSS_SELECTOR, '.css-1nbnul7-DivShareTitleContainer .css-10pb43i-H2ShareSubTitle')
            name_text = name_element.text
            followers_element = driver.find_element(By.CSS_SELECTOR, '[title="Followers"]')
            followers_text = followers_element.text
            likes_element = driver.find_element(By.CSS_SELECTOR, '[title="Likes"]')
            likes_text = likes_element.text
            video_views_elements = driver.find_elements(By.CSS_SELECTOR, "strong[data-e2e='video-views']")
            video_views = [style_num_to_float(element.text) for element in video_views_elements[3:8]]
            average_views = sum(video_views) / len(video_views) if video_views else None
            fe = style_num_to_float(followers_text)
            emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', userbio_text)
            email_username = email_extension = aggregate_email = ''

            if emails:
                cleaned_email = emails[0].lstrip('-')
                email_parts = cleaned_email.split('@')
                email_username = email_parts[0]
                email_extension = email_parts[1] if len(email_parts) > 1 else ''
                aggregate_email = cleaned_email

            item = {
                'link': driver.current_url,
                'username': name_text,
                'following': fe,
                'email': aggregate_email,
                'bio_link': userbio_text,
                'likes': style_num_to_float(likes_text),
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

    if list_items:
        df_new = pd.DataFrame(list_items)
        df_new.to_csv('TIKTOKTARGET_Data.csv', mode='a', index=False, header=not os.path.exists('TIKTOKTARGET_Data.csv'))
        print("Appended to CSV!")
    else:
        print("No new items to append.")

# Main function
def main(driver, hashtags):
    while True:
        try:
            for hashtag in hashtags:
                print(f"Searching for hashtag: {hashtag}")
                driver.get(f"https://www.tiktok.com/tag/{hashtag}")
                time.sleep(5)

                # Click on the first video container
                first_video = driver.find_element(By.CSS_SELECTOR, 'div[data-e2e="challenge-item"]')
                first_video.click()
                time.sleep(5)

                influencer_links = []

                driver, influencer_links = scrolling_function(driver, target_count=20)
                print(f"Collected {len(influencer_links)} unique influencer links for hashtag: {hashtag}.")
                influencer_function(driver, influencer_links)

                # Clear local arrays and reinitialize the loop
                influencer_links.clear()
                print("Cleared local arrays and ready for the next search term.")
                driver.get("https://www.tiktok.com")

        except Exception as e:
            print(f"Error occurred: {e}")
            break

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
    options.add_argument("--headless=new")  # Run in headless mode

    driver = uc.Chrome(options=options)
    print("WebDriver started and navigated to TikTok.")

    hashtags = []
    print("Enter up to 5 hashtags. Press Enter without typing anything to finish input.")
    for i in range(5):
        hashtag = input(f"Enter hashtag {i+1}: ")
        if hashtag:
            hashtags.append(hashtag)
        else:
            break

    main(driver, hashtags)
    driver.quit()
    print("WebDriver closed.")
