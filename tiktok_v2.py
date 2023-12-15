from  selenium import webdriver
import pandas
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from capcha import main_loop
import re


import time

def scrolling_function(driver):
    try:
        try:
            while True:
                time.sleep(3)

                if driver.find_element_by_class_name('tiktok-17bdhe6-ButtonGotIt'):
                    # driver.find_element_by_xpath('/html/body/div[7]/div[2]/div/button').click()
                    driver.close()
                    options = webdriver.ChromeOptions()
                    options.add_experimental_option("excludeSwitches", ["enable-automation"])
                    options.add_experimental_option('useAutomationExtension', False)
                    options.add_argument("--disable-blink-features=AutomationControlled")

                    driver = webdriver.Chrome(options=options)
                    driver.maximize_window()
                    driver.get('https://www.tiktok.com/')

        except:
            pass

        oldtime = time.time()
        influencer_links = []

        item_len = len(driver.find_elements_by_css_selector('#app > div.tiktok-19fglm-DivBodyContainer.etsvyce0 > div.tiktok-1id9666-DivMainContainer.e7i8kv30 > div:nth-child(1) > div'))

        while True:

            time.sleep(1)
            recentList = driver.find_elements_by_css_selector('#app > div.tiktok-19fglm-DivBodyContainer.etsvyce0 > div.tiktok-1id9666-DivMainContainer.e7i8kv30 > div:nth-child(1) > div')[item_len-1]
            allitems  = driver.find_elements_by_css_selector('#app > div.tiktok-19fglm-DivBodyContainer.etsvyce0 > div.tiktok-1id9666-DivMainContainer.e7i8kv30 > div:nth-child(1) > div')
            for influ in allitems:
                influ_url = influ.find_element_by_class_name('avatar-anchor').get_attribute('href')
                if influ_url not in influencer_links:
                    influencer_links.append(influ_url)
            time.sleep(1)
            driver.execute_script("arguments[0].scrollIntoView();", recentList)
            time.sleep(12)
            if time.time() - oldtime > 10:
                break
            try:
                if driver.find_element_by_xpath(
                        '//*[@id="tiktok-verify-ele"]/div/div[1]/div[2]/div').text == 'Verify to continue:':
                    while True:
                        try:
                            WebDriverWait(driver, 30).until(
                                EC.presence_of_element_located(
                                    (By.XPATH, '//*[@id="tiktok-verify-ele"]/div/div[2]/img[2]')))
                            try:
                                distance2 = main_loop()

                            except:
                                distance2 = 10

                            dragable = driver.find_element_by_xpath('//*[@id="secsdk-captcha-drag-wrapper"]/div[2]')
                            quoitent = int(distance2 / 20)
                            remainder = distance2 % 20
                            hit = ActionChains(driver).click_and_hold(dragable)
                            for i in range(1, quoitent + 2):
                                if i == quoitent + 1:
                                    hit.move_by_offset(remainder, 0).release().perform()
                                else:
                                    hit.move_by_offset(20, 0)
                            time.sleep(4)
                            try:
                                if driver.find_element_by_xpath(
                                        '//*[@id="tiktok-verify-ele"]/div/div[1]/div[2]/div').text == 'Verify to continue:':
                                    pass
                            except:
                                break

                        except:
                            pass
            except:
                pass
            if len(allitems) == len(driver.find_elements_by_css_selector("#app > div.tiktok-19fglm-DivBodyContainer.etsvyce0 > div.tiktok-1id9666-DivMainContainer.e7i8kv30 > div:nth-child(1) > div")):
                break
            item_len = len(driver.find_elements_by_css_selector("#app > div.tiktok-19fglm-DivBodyContainer.etsvyce0 > div.tiktok-1id9666-DivMainContainer.e7i8kv30 > div:nth-child(1) > div"))

    except:
        pass

    return driver,influencer_links

def influencer_function(driver,links):
    try:
        try:
            df = pandas.read_csv('influencer_data.csv')
            already_url = list(df['url'])
        except:
            already_url = []

        list_items = []
        for page in links:
            driver.execute_script("window.open('{}');".format(page))
            time.sleep(5)
            driver.switch_to.window(driver.window_handles[-1])
            try:

                userbio = driver.find_element_by_xpath('//*[@id="app"]/div[2]/div[2]/div/div[1]/h2[2]').text.split('\n')
                

                for info in userbio:
                    # if ('@' in info) and (('.com' in info) or ('.inc' in info) or ('.co' in info) or ('.net' in info) or ('gmail' in info)):
                    if re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', info):
                        if driver.current_url not in already_url:
                            # for atrate in info.split(' '):
                            #     if '@' in atrate:
                            item = dict()
                            item['url'] = driver.current_url
                            item['name'] = driver.find_element_by_xpath('//*[@id="app"]/div[2]/div[2]/div/div[1]/div[1]/div[2]/h2').text
                            item['followers'] = driver.find_element_by_xpath("//strong[@title='Followers']").text
                            item['email'] = ' , '.join(re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', info))
                            item['likes'] = driver.find_element_by_css_selector('strong[title="Likes"]').text
                            list_items.append(item)
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            except:
                time.sleep(8)
                if driver.find_element_by_xpath('//*[@id="verify-ele"]/div/div[1]/div[2]/div').text == 'Verify to continue:':
                    while True:
                        try:
                            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="verify-ele"]/div/div[2]/img[2]')))
                            try:
                                distance2 = main_loop()

                            except:
                                distance2 = 10

                            dragable = driver.find_element_by_xpath('//*[@id="secsdk-captcha-drag-wrapper"]/div[2]')
                            quoitent = int(distance2 / 20)
                            remainder = distance2 % 20
                            hit = ActionChains(driver).click_and_hold(dragable)
                            for i in range(1, quoitent + 2):
                                if i == quoitent + 1:
                                    hit.move_by_offset(remainder, 0).release().perform()
                                else:
                                    hit.move_by_offset(20, 0)
                            time.sleep(4)
                            try:
                                if driver.find_element_by_xpath('//*[@id="verify-ele"]/div/div[1]/div[2]/div').text == 'Verify to continue:':
                                    pass
                            except:
                                break

                        except:
                            pass
                time.sleep(6)
                userbio = driver.find_element_by_xpath('//*[@id="app"]/div[2]/div[2]/div/div[1]/h2[2]').text.split('\n')

                for info in userbio:
                    # if ('@' in info) and (('.com' in info) or ('.inc' in info) or ('.co' in info) or ('.net' in info) or ('gmail' in info)):
                    if re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', info):
                        if driver.current_url not in already_url:
                            # for atrate in info.split(' '):
                            #     if '@' in atrate:
                            item = dict()
                            item['url'] = driver.current_url
                            item['name'] = driver.find_element_by_xpath('//*[@id="app"]/div[2]/div[2]/div/div[1]/div[1]/div[2]/h2').text
                            item['followers'] = driver.find_element_by_xpath("//strong[@title='Followers']").text
                            item['email'] = ' , '.join(re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', info))
                            item['likes'] = driver.find_element_by_css_selector('strong[title="Likes"]').text
                            list_items.append(item)
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

    except:
        pass

    df_new = pandas.DataFrame(list_items)
    try:
        final_df = pandas.concat([df, df_new])
    except:
        final_df = df_new
    final_df.to_csv('influencer_data.csv', encoding='utf-8', index=False)

    driver.switch_to.window(driver.window_handles[0])



if __name__=="__main__":
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.get("https://www.tiktok.com/")
    old_influencer_links = []
    while True:
        try:
            driver,influencer_links = scrolling_function(driver)
            final_urls = []
            for link1 in influencer_links:
                if link1 not in old_influencer_links:
                    final_urls.append(link1)
            old_influencer_links = influencer_links
            influencer_function(driver,final_urls)

        except:
            break
