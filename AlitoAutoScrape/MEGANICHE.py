import time
import random
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import os
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

# Function to fetch creators
def fetch_creators():
    response = requests.get('https://blitz-backend-nine.vercel.app/api/crm/creator/creators')
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch creators")
        return []

# Function to add creator
def add_creator(creator_data):
    print("Attempting to add creator with data:", creator_data)  # Log the request data
    response = requests.post('https://blitz-backend-nine.vercel.app/api/crm/creator/add', json=creator_data)
    if response.status_code == 200:
        print("Creator added successfully")
    else:
        print("Failed to add creator. Response:", response.text)

# Function to convert styled numbers to float
def style_num_to_float(value):
    if not value or value.strip() == '':
        return 0.0  # Return 0.0 or any default value when the input is empty or invalid
    try:
        if 'B' in value:
            return float(value.replace('B', '')) * 1000000000
        if 'M' in value:
            return float(value.replace('M', '')) * 1000000
        elif 'K' in value:
            return float(value.replace('K', '')) * 1000
        else:
            return float(value)
    except ValueError:
        print(f"ValueError: Could not convert {value} to float.")
        return 0.0  # Return 0.0 or any default value when conversion fails

# Scrolling function to collect influencer links endlessly
import time
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

def scrolling_function(driver):
    influencer_links = []
    print('Starting scroll function')
    
    while len(influencer_links) < 7:
        try:
            # Try to click "Continue as guest" if it exists
            try:
                continue_as_guest = driver.find_element(By.XPATH, "//div[@role='link' and @data-e2e='channel-item' and contains(text(), 'Continue as guest')]")
                continue_as_guest.click()
                print("Clicked on 'Continue as guest'.")
                time.sleep(2)
            except NoSuchElementException:
                # Element not found, so skip this step
                pass

            # Scroll to the bottom of the page
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Find influencer containers after scrolling
            video_containers = driver.find_elements(By.CSS_SELECTOR, 'div.css-1mnwhn0-DivAuthorContainer')
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Process each influencer container
            for container in video_containers:
                try:
                    anchor = container.find_element(By.CSS_SELECTOR, 'a.e1g2yhv81.css-fz9tz3-StyledLink-StyledAuthorAnchor.er1vbsz0')
                    influ_url_full = anchor.get_attribute('href').split('?')[0]
                    influ_url = '/'.join(influ_url_full.split('/')[:4]) + '/' if len(influ_url_full.split('/')) >= 4 else influ_url_full
                    if influ_url not in influencer_links:
                        influencer_links.append(influ_url)
                        print("Found influencer URL:", influ_url)

                        # Check if we have enough links
                        if len(influencer_links) >= 7:
                            influencer_function(driver, influencer_links)
                            influencer_links = []  # Reset list after processing
                            break  # Exit loop to refresh page
                        
                except StaleElementReferenceException:
                    print("Stale element reference error encountered. Skipping this element.")
                    continue  # Skip to the next container
                except Exception as e:
                    print(f"Error processing container: {e}")
                    continue

            # Refresh the page every 5 seconds if the target number of links hasn't been reached
            if len(influencer_links) < 7:
                driver.refresh()
                time.sleep(5)  # Wait 5 seconds before scrolling again
                driver.execute_script("window.scrollTo(0, 0);")
                print("Page refreshed, starting scroll again.")
                
        except Exception as e:
            print(f'Error occurred in scrolling function: {e}')
            break  # Exit loop if there's a major error

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
        
        # Check for the "Continue as guest" element
        try:
            continue_as_guest = driver.find_element(By.XPATH, "//div[@role='link' and @data-e2e='channel-item' and contains(text(), 'Continue as guest')]")
            continue_as_guest.click()
            print("Clicked on 'Continue as guest'.")
            time.sleep(2)  # Add a short delay after clicking
        except NoSuchElementException:
            # Element not found, continue as normal
            pass
        
        try:
            userbio_element = driver.find_element(By.CSS_SELECTOR, '.css-cm3m4u-H2ShareDesc')
            userbio_text = userbio_element.text
            name_element = driver.find_element(By.CSS_SELECTOR, '.css-11ay367-H1ShareTitle')
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
        df_new.to_csv('MEGANICHE_Data.csv', mode='a', index=False, header=not os.path.exists('MEGANICHE_Data.csv'))
        print("Appended to CSV!")
        driver.get("https://www.tiktok.com/foryou")
    else:
        print("No new items to append.")


# Main function
def main(driver):
    try:
        print("Starting scrolling...")
        driver, influencer_links = scrolling_function(driver)
    except Exception as e:
        print(f"Error occurred: {e}")

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
    driver.get("https://www.tiktok.com/foryou")
    print("WebDriver started and navigated to TikTok.")

    main(driver)
    driver.quit()
    print("WebDriver closed.")
