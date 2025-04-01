import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import csv
import logging
import os
import json
import time
import random
from os import system, name
from datetime import datetime
import undetected_chromedriver as uc
from typing import Dict, List
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

SCRAPPER = False

def domain_to_url(domain: str) -> str:
    if domain.startswith(".") and "www" not in domain:
        domain = "www" + domain
        return "https://" + domain
    elif "www" in domain and domain.startswith("."):
        domain = domain[1:]
        return "https://" + domain
    else:
        return "https://" + domain

def login_using_cookie_file(driver: WebDriver, cookie_file: str):
    """Restore auth cookies from a file. Does not guarantee that the user is logged in afterwards.
    Visits the domains specified in the cookies to set them, the previous page is not restored."""
    domain_cookies: Dict[str, List[object]] = {}
    with open(cookie_file) as file:
        cookies: List = json.load(file)
        # Sort cookies by domain, because we need to visit to domain to add cookies
        for cookie in cookies:
            try:
                domain_cookies[cookie["domain"]].append(cookie)
            except KeyError:
                domain_cookies[cookie["domain"]] = [cookie]

    for domain, cookies in domain_cookies.items():
        driver.get(domain_to_url(domain + "/robots.txt"))
        for cookie in cookies:
            cookie.pop("sameSite", None)  # Attribute should be available in Selenium >4
            cookie.pop("storeId", None)  # Firefox container attribute
            try:
                driver.add_cookie(cookie)
            except:
                print(f"Couldn't set cookie {cookie['name']} for {domain}")
    return True

def driverInit():
    # setting options for undetected chrome driver
    option = uc.ChromeOptions()
    useragentstr = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36"
    option.add_argument("--log-level=3")
    option.add_argument("--disable-infobars")
    #option.add_argument("--headless")
    option.add_argument("--disable-extensions")
    prefs = {"credentials_enable_service": False,
             "profile.password_manager_enabled": False,
             "profile.default_content_setting_values.notifications": 2
             }
    option.add_experimental_option("prefs", prefs)

    option.add_argument(f"user-agent={useragentstr}")
    driverr = uc.Chrome(options=option)
    return driverr

def scroll_down(driver):
    SCROLL_PAUSE_TIME = 1
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        time.sleep(2)

def answers():
    try:
        driver = driverInit()

        driver.get("https://chat.openai.com")
        driver.refresh()

        time.sleep(4)
        try:
            driver.find_element(By.XPATH, "//button[contains(@class,'relative flex')]").click()
        except:
            driver.find_element(By.XPATH, "//div[contains(@class,'flex flex-row')]//button[1]").click()
        time.sleep(4)
        email = "muhammadharisrgs@gmail.com"
        password = "Yes54321"
        # Sending email
        email_element = driver.find_element(By.ID, "username")
        for char in email:
            email_element.send_keys(char)
            time.sleep(0.1)  # pause between each character, adjust as needed
        email_element.send_keys(Keys.ENTER)
        time.sleep(2)

        # Sending password
        password_element = driver.find_element(By.ID, "password")
        for char in password:
            password_element.send_keys(char)
            time.sleep(0.1)  # pause between each character, adjust as needed
        password_element.send_keys(Keys.ENTER)
        wait = WebDriverWait(driver, 1000)
        
        
        time.sleep(3)
        try:
            driver.find_element(By.ID, "prompt-textarea").send_keys(questions + Keys.ENTER)
        except:
            wait.until(EC.visibility_of_element_located((By.ID, "prompt-textarea")))
        time.sleep(4)
        try:
            driver.find_element(By.XPATH, "//button[@class='btn-md btn-primary flex-shrink-0 cursor-pointer sign-in-form__submit-btn--full-width']").click()
        except:
            pass
        try:
            driver.find_element(By.XPATH, "(//div[contains(@class,'flex gap-4 mt-6')]//button[2])").click()
        except:
            pass
        try:
            driver.find_element(By.XPATH, "(//div[contains(@class,'flex gap-4 mt-6')]//button[2])").click()
        except:
            pass
        # 1. Read the question from question.txt
        with open("question.txt", "r") as file:
            questions = file.read()
        driver.find_element(By.ID, "prompt-textarea").send_keys(questions + Keys.ENTER)
        time.sleep(10)
        output = driver.find_elements(By.XPATH, "(//div[contains(@class,'markdown prose')]//p)")
        answer = ""
        for o in range(0, len(output)):
            print(output[o].text)
            answer = answer + output[o].text
        # 4. Save the answer to answer.txt
        with open("answer.txt", "w") as file:
            file.write(answer)

        driver.quit()
        return answer
    except:
        logging.exception('msg')
        time.sleep(1000)
        
print(answers("What is the capital of Pakistan?"))