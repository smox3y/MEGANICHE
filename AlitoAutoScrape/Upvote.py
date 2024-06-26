import time
import random
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import signal
import psutil
import sys

# Pretty UI Header
def print_header():
    print("="*60)
    print("        Welcome to the Upvote Blitz Automation Script")
    print("="*60)
    print("This script will automate the process of upvoting on the given page.")
    print("Please make sure you have the necessary dependencies installed.")
    print("="*60)

print_header()

# Ask the user if they want to run headless
headless_option = input("Run headless? (y/n): ").strip().lower()
headless_mode = headless_option == 'y'

# Read proxies from the file
with open('proxyscrape_premium_http_proxies.txt', 'r') as file:
    proxies = [line.strip() for line in file]

# Define the URL and the button XPATH
url = "https://beacons.ai/creator-agencies/the-culture-club-inc"
button_xpath = "/html/body/div/div/div/div/div[2]/div/div[2]/div[1]/button"
upvote_count_xpath = "/html/body/div/div/div/div/div[2]/div/div[2]/div[1]/button/div/span"
success_message_xpath = "/html/body/div/div/div[2]"

# Configure logging to suppress specific messages
logging.basicConfig(level=logging.ERROR)
uc_logger = logging.getLogger("uc")
uc_logger.setLevel(logging.ERROR)

# Function to check if the main content is loaded
def is_main_content_loaded(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.flex.h-\\[28px\\].w-max.items-center.justify-center.gap-1.rounded-\\[40px\\].px-2.text-12.font-semibold.text-white"))
        )
        return True
    except:
        return False

# Function to perform upvote and verify
def perform_upvote(driver):
    try:
        # Get initial upvote count
        initial_count_element = driver.find_element(By.XPATH, upvote_count_xpath)
        initial_count = int(initial_count_element.text)
        print(f"Initial upvote count: {initial_count}")
       
        button = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, button_xpath))
        )
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, button_xpath))
        )
       
        # Use JavaScript to click the button
        driver.execute_script("arguments[0].click();", button)
        print("Successfully clicked the upvote button")
       
        # Wait for the success message to appear
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, success_message_xpath))
        )
        print("Successfully upvoted message detected")
       
        # Check if the upvote count has increased without refreshing
        new_count_element = driver.find_element(By.XPATH, upvote_count_xpath)
        new_count = int(new_count_element.text)
        print(f"New upvote count: {new_count}")
       
        if new_count > initial_count:
            print(f"Upvote registered successfully: {initial_count} -> {new_count}")
            return initial_count, new_count
        else:
            print(f"Upvote not registered: {initial_count} -> {new_count}")
            return initial_count, initial_count
    except Exception as e:
        print(f"Failed to click the upvote button. Reason: {e}")
        return None, None

# Flag to control the main loop
running = True

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    global running
    print("\nGracefully shutting down...")
    running = False
    cleanup_chrome_processes()
    sys.exit(0)

# Register signal handler for interrupt signal (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

# Cleanup lingering Chrome processes
def cleanup_chrome_processes():
    for proc in psutil.process_iter():
        try:
            if proc.name().lower() in ['chrome', 'chromedriver']:
                proc.terminate()
                proc.wait(timeout=5)  # Wait for the process to terminate
        except (psutil.NoSuchProcess, psutil.TimeoutExpired):
            pass

# Function to start ChromeDriver with given options
def start_chromedriver(proxy, headless_mode):
    options = uc.ChromeOptions()
    options.add_argument(f'--proxy-server=http://{proxy}')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")  # Smaller window size
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    if headless_mode:
        options.add_argument("--headless=new")  # Use the new headless mode
        options.add_argument("--log-level=3")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-insecure-localhost")

    driver = None
    try:
        cleanup_chrome_processes()  # Ensure no lingering Chrome processes before starting
        driver = uc.Chrome(options=options)
    except Exception as e:
        print(f"Failed to start ChromeDriver. Reason: {e}")
        cleanup_chrome_processes()
    return driver

# Function to process proxies
def process_proxies(proxies, total_upvotes, upvote_start):
    for proxy in proxies:
        if not running:
            break

        print("\n" + "="*60)
        print(f"Trying proxy: {proxy}")

        driver = start_chromedriver(proxy, headless_mode)
        if not driver:
            print(f"Failed to load page with proxy: {proxy}. Skipping to next proxy.")
            continue
       
        try:
            print("Loading page...")
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
           
            if is_main_content_loaded(driver):
                print(f"Page fully loaded with proxy: {proxy}")
               
                initial_count, new_count = perform_upvote(driver)
                if new_count and initial_count != new_count:
                    total_upvotes += 1
                    if upvote_start is None:
                        upvote_start = initial_count
                    if total_upvotes % 10 == 0:
                        print(f"\n{total_upvotes} upvotes completed ({upvote_start} to {new_count})")
                        upvote_start = new_count
                else:
                    print(f"Upvote not registered with proxy: {proxy}")
            else:
                print(f"Main content did not load with proxy: {proxy}")
        except Exception as e:
            print(f"Failed to load page with proxy: {proxy}. Reason: {e}")
        finally:
            if driver:
                driver.quit()
            cleanup_chrome_processes()  # Ensure only tracked Chrome processes are terminated
            time.sleep(random.uniform(0.5, 1.5))  # Short delay before next proxy attempt
    return total_upvotes, upvote_start

# Initialize upvote variables
total_upvotes = 0
upvote_start = None

# Main loop to cycle through proxies indefinitely
while running:
    total_upvotes, upvote_start = process_proxies(proxies, total_upvotes, upvote_start)
    print("\n" + "="*60)
    print("Finished all proxies. Cycling back to the beginning...")