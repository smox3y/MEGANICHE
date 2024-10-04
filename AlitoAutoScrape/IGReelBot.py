import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

class IGReelRefresh:
    def __init__(self, instagram_link):
        self.instagram_link = instagram_link
        self.driver = None

    def start_driver(self):
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

        self.driver = uc.Chrome(options=options)
        self.driver.get(self.instagram_link)
        print("Navigated to Instagram Reel page. Waiting for login...")
        
        # Wait 10 seconds for the user to log in
        time.sleep(10)

    def refresh_video(self, times=100):
        for i in range(times):
            print(f"Refreshing video - Attempt {i + 1}")
            try:
                # Find video element and refresh
                video_element = self.driver.find_element(By.TAG_NAME, 'video')
                self.driver.execute_script("arguments[0].currentTime = 0;", video_element)
                time.sleep(3)  # Wait to let the video play before refreshing
            except Exception as e:
                print(f"Error refreshing video: {e}")

    def close_driver(self):
        if self.driver:
            self.driver.quit()

# Usage
if __name__ == "__main__":
    instagram_link = "https://www.instagram.com/p/DAtUI5Axvu3/"  # Replace with actual Instagram Reel link
    ig_refresh = IGReelRefresh(instagram_link)
    
    try:
        ig_refresh.start_driver()
        ig_refresh.refresh_video(times=100)
    finally:
        ig_refresh.close_driver()
