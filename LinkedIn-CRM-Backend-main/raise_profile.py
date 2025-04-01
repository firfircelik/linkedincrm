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
from selenium import webdriver
import logging
from urllib.parse import urlparse
import re
import openai


SCRAPPER = False


def driverInit():
    option = uc.ChromeOptions()
    useragentstr = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36"
    option.add_argument("--log-level=3")
    option.add_argument("--disable-infobars")
    option.add_argument("--disable-extensions")
    #option.add_argument("--headless")
    prefs = {"credentials_enable_service": False,
             "profile.password_manager_enabled": False,
             "profile.default_content_setting_values.notifications": 2
             }
    option.add_experimental_option("prefs", prefs)

    option.add_argument(f"user-agent={useragentstr}")
    driverr = uc.Chrome(options=option)
    return driverr


def get_connect_promt(name, experience):
    # Set up your OpenAI API credentials
    openai.api_key = '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'
    model_engine = "text-davinci-003"
    prompt = "Can you write a linkedin connect message for a person with this experience: " + experience
    completion = openai.Completion.create(
        engine = model_engine,
        prompt = prompt,
        max_tokens = 1024,
        n=1,
        stop = None,
        temperature = 0.5,
    )
    response = completion.choices[0].text
    response = response.replace("[Name]", name).replace("[name]", name).replace("[Your Name]", "Maeve O'Connor").replace("[Your name]", "Maeve O'Connor").replace("[your name]", "Maeve O'Connor")
    return response


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

def returnFiletoList(filename):
    with open(filename, "r") as f:
        LinesToList = f.read().split("\n")
    return LinesToList

def run():
    try:
        urls = ["https://www.linkedin.com/in/sara-bernardi-7686a8181/", "https://www.linkedin.com/in/julia-dederer-967533229/", "https://www.linkedin.com/in/maricruz-davatz-89b9aa3b/", "https://www.linkedin.com/in/julian-kupetz/", "https://www.linkedin.com/in/paulacarandomecoleta/", "https://www.linkedin.com/in/jeannine-schelbert-3340b6149/"]
        #urls = ["https://www.linkedin.com/in/julian-kupetz/"]
        driver = driverInit()
        login_using_cookie_file(driver, "cookies.txt")
        driver.get("https://www.linkedin.com/mynetwork/")
        time.sleep(10)
        for i in range(1,5):
            if "People you may know" in driver.find_element(By.XPATH, "(//h2[contains(@class,'display-flex flex-1')])[1]").text:
                temp = i
                break
        print(temp)
        try:
            driver.find_element(By.XPATH, "(//button[contains(@class,'artdeco-button artdeco-button--muted')]//span)[" + str(temp) + "]").click()
        except:
            driver.find_element(By.XPATH, "(//button[contains(@class,'artdeco-button artdeco-button--muted')]//span)[5]").click()

        time.sleep(2)
        action = webdriver.ActionChains(driver)
        action.move_to_element(driver.find_element(By.XPATH, "(//button[contains(@class,'artdeco-button artdeco-button--2')]//span)[3]"))
        action.perform()
        scroll_down(driver)
        for i in range(1,100):
            driver.find_element(By.XPATH, "(//button[contains(@class,'artdeco-button artdeco-button--2')]//span)[" + str(i) + "]").click()
            time.sleep(1.5)

    except:
        logging.exception("message")
        driver.quit()
       

run()