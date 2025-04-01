import os
import json
import time
from os import system, name
from datetime import datetime, timezone, timedelta
from typing import Dict, List
from selenium import webdriver
from selenium.webdriver import ActionChains
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from urllib.parse import urlparse
import re
import openai
import psycopg2
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import zipfile
import string
from chatgpt_api import get_intro_message, get_follow_up
SCRAPPER = False

def get_db():
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'yes54321',
        'HOST': 'linkedin-crm.cjqbwdujjpbk.eu-west-2.rds.amazonaws.com',
        'PORT': '5432',
    }
}

    db_settings = DATABASES['default']

    conn = psycopg2.connect(
        dbname=db_settings['NAME'],
        user=db_settings['USER'],
        password=db_settings['PASSWORD'],
        host=db_settings['HOST'],
        port=db_settings['PORT']
    )
    # Get a cursor
    cursor = conn.cursor()
    return cursor, conn



def get_campaigns():
    

    cursor, conn = get_db()
    cursor.execute("""SELECT * FROM "CRM_campaign";""")
    rows = cursor.fetchall()
    conn.close()
    return rows
       
def get_account_by_id(account_id):
    cursor, conn = get_db()
    cursor.execute("""SELECT * FROM "CRM_account" WHERE id = %s;""", (account_id,))
    row = cursor.fetchone()  # Assuming account IDs are unique, so you'd get at most one row
    conn.close()
    return row




def driverInit(PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS):
    #PROXY_HOST =  "91.245.90.167"
    #PROXY_PORT = "12323"
    #PROXY_USER = "josephwest"
    #PROXY_PASS = "118811"

    def create_proxyauth_extension(proxy_host, proxy_port,
                                   proxy_username, proxy_password,
                                   plugin_path, scheme='http'):
        """Proxy Auth Extension
        args:
            proxy_host (str): domain or ip address, ie proxy.domain.com
            proxy_port (int): port
            proxy_username (str): auth username
            proxy_password (str): auth password
        kwargs:
            scheme (str): proxy scheme, default http
            plugin_path (str): absolute path of the extension
        return str -> plugin_path
        """
        # Check if the file exists and delete it
        if os.path.exists(plugin_path):
            os.remove(plugin_path)

        if plugin_path is None:
            plugin_path = 'proxy_auth_plugin.zip'

        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = string.Template(
            """
            var config = {
                    mode: "fixed_servers",
                    rules: {
                      singleProxy: {
                        scheme: "${scheme}",
                        host: "${host}",
                        port: parseInt(${port})
                      },
                      bypassList: ["foobar.com"]
                    }
                  };
            chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
            function callbackFn(details) {
                return {
                    authCredentials: {
                        username: "${username}",
                        password: "${password}"
                    }
                };
            }
            chrome.webRequest.onAuthRequired.addListener(
                        callbackFn,
                        {urls: ["<all_urls>"]},
                        ['blocking']
            );
            """
        ).substitute(
            host=proxy_host,
            port=proxy_port,
            username=proxy_username,
            password=proxy_password,
            scheme=scheme,
        )

        with zipfile.ZipFile(plugin_path, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)

        return plugin_path

    proxyauth_plugin_path = create_proxyauth_extension(
        proxy_host=PROXY_HOST,
        proxy_port=PROXY_PORT,
        proxy_username=PROXY_USER,
        proxy_password=PROXY_PASS,
        plugin_path=f"{os.getcwd()}\proxy_auth_plugin.zip"
    )
    co = webdriver.ChromeOptions()
    co.add_experimental_option(
        "prefs", {"profile.default_content_setting_values.notifications": 2,
                  "credentials_enable_service": False,
                  "profile.password_manager_enabled": False}
    )
    co.add_extension(proxyauth_plugin_path)
    time.sleep(1)
    driver = webdriver.Chrome(options=co)
    driver.maximize_window()
    return driver

def get_connect_promt(name, experience, myname):
    # Set up your OpenAI API credentials
    openai.api_key = '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'
    model_engine = "text-davinci-003"
    prompt = "Can you write a linkedin connect message of maximum 250 characters for a person with this experience: " + experience
    completion = openai.Completion.create(
        engine = model_engine,
        prompt = prompt,
        max_tokens = 1024,
        n=1,
        stop = None,
        temperature = 0.5,
    )
    response = completion.choices[0].text
    response = response.replace("[Name]", name).replace("[name]", name).replace("[Your Name]", myname).replace("[Your name]", myname).replace("[your name]", myname)
    return response


def get_images():
    # Set up your OpenAI API credentials
    openai.api_key = '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'
    model_engine = "image-alpha-001"
    prompt = "a realistic image talks about work life balance"
    response = openai.Image.create(
        model = model_engine,
        prompt = prompt,
        n=1,
        size="1024x1024"
    )
    image_url = response['data'][0]['url']

    return image_url




def get_phone_numbers(driver, campaign, profile_name):
    decoded_urls = []
    contact_numbers = []
    actual_urls = []
    driver.get("https://www.linkedin.com/messaging/")
    time.sleep(5)
    total_messages_list = []
    messages_profiles = []
    profile_messages = driver.find_elements(By.XPATH, "(//h3[contains(@class,'msg-conversation-listitem__participant-names msg-conversation-card__participant-names')])")
    for profile_message in profile_messages:
        profile_message.click()
        time.sleep(2)
        messages = driver.find_elements(By.XPATH, "(//p[contains(@class,'msg-s-event-listitem__body t-14')])")
        phone_flag = None
        messages_list = []
        for message in messages:
            messages_list.append(message.text)
            if extract_phone_numbers(message.text) !=[]:
                phone_flag = True
                print("Phone Number : ", extract_phone_numbers(message.text)[0])
                contact_numbers.append(extract_phone_numbers(message.text)[0])
                profile_link = driver.find_element(By.XPATH, "(//a[contains(@class,'app-aware-link  msg-thread__link-to-profile')])").get_attribute("href")
                print("Profile Link : ", profile_link)
                decoded_urls.append(profile_link)
                break

            print(extract_phone_numbers(message.text))
            time.sleep(4)
        if not phone_flag:
            try:
                messages_profiles.append(driver.find_element(By.XPATH, "(//a[contains(@class,'app-aware-link  msg-thread__link-to-profile')])").get_attribute("href"))
                total_messages_list.append(messages_list)
            except:
                continue
            
                    
    for p, profile_url in enumerate(messages_profiles):
        if len(total_messages_list[p]) > 1:
            driver.get(profile_url)
            time.sleep(1)
            profile_url = driver.current_url
            cursor, conn = get_db()
            check_query = """SELECT COUNT(*) FROM "CRM_profile" WHERE "link" = %s AND "intro_message" IS NULL;"""
            cursor.execute(check_query, (profile_url,))
            exists = cursor.fetchone()[0]
            if exists:
                get_name_query = """SELECT "name" FROM "CRM_profile" WHERE "link" = %s;"""
                cursor.execute(get_name_query, (profile_url,))
                lead_name = cursor.fetchone()[0]
                scroll_down(driver)
                message = get_follow_up(lead_name, profile_name.split(" ")[0], total_messages_list[p])
                driver.back()
                time.sleep(1.5)
                driver.get(profile_url)
                time.sleep(3)
                buttons = driver.find_elements(By.XPATH, "(//button[contains(@class,'artdeco-button artdeco-button--2')]//span)")
                        
                for button in buttons:
                    print(button.text)
                    if button.text == "Message":
                        button.click()
                        break

                #message_buttons[c+1].click()
                try:
                    time.sleep(2)
                    driver.find_element(By.XPATH, "(//button[contains(@class,'artdeco-modal__dismiss artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view')])").click()
                except:
                    pass
                time.sleep(2)
                driver.find_element(By.XPATH, "(//div[contains(@class,'msg-form__contenteditable t-14 t-black--light t-normal flex-grow-1 full-height notranslate')])").send_keys(message)
                time.sleep(2)
                
                driver.find_element(By.XPATH, "(//button[contains(@class,'msg-form__send-button artdeco-button artdeco-button--1')])").click()
                time.sleep(1.5)
                driver.find_element(By.XPATH, "(//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view')])").click()
                time.sleep(1.5)
                update_query = """UPDATE "CRM_profile" SET "intro_message" = %s WHERE "link" = %s;"""
                cursor.execute(update_query, ("Success", profile_url))
                conn.commit()
            driver.back()

                


    names = []
    for decoded_url in decoded_urls:
        driver.get(decoded_url)
        time.sleep(1.5)
        names.append(driver.find_element(By.XPATH, "//h1[contains(@class,'text-heading-xlarge inline t-24 v-align-middle break-words')]").text)
        actual_urls.append(driver.current_url)
    print(actual_urls)
    print(contact_numbers)
    print(names)
    time.sleep(30)
    cursor, conn = get_db()
    for c, contact_number in enumerate(contact_numbers):    
        # Check if the link already exists in the table
        check_query = """SELECT COUNT(*) FROM "CRM_profile" WHERE "link" = %s;"""
        cursor.execute(check_query, (actual_urls[c],))
        exists = cursor.fetchone()[0]

        if exists:
            # Update the record if it exists
            update_query = """UPDATE "CRM_profile" SET "contact_number" = %s WHERE "link" = %s;"""
            cursor.execute(update_query, (contact_number, actual_urls[c]))
        else:
            # Insert a new record if it doesn't exist
            insert_query = """INSERT INTO "CRM_profile" ("name", "contact_number", "link", "campaign_id", "status")
                            VALUES (%s, %s, %s, %s, 'Accepted');"""
            cursor.execute(insert_query, (names[c], contact_number, actual_urls[c], campaign))

    conn.commit()

    
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


def login_using_cookie_string(driver: WebDriver, cookie_string: str) -> bool:
    """Restore auth cookies from a string. Does not guarantee that the user is logged in afterwards.
    Visits the domains specified in the cookies to set them, the previous page is not restored."""
    domain_cookies: Dict[str, List[object]] = {}
    cookies = json.loads(cookie_string)  # Parse the cookie string

    # Sort cookies by domain, because we need to visit to domain to add cookies
    for cookie in cookies:
        domain_cookies.setdefault(cookie["domain"], []).append(cookie)

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

# Helper function
def domain_to_url(domain: str) -> str:
    """Converts a domain to a usable URL by adding an HTTP protocol."""
    if not domain.startswith(("http://", "https://")):
        return "http://" + domain
    return domain

def returnFiletoList(filename):
    with open(filename, "r") as f:
        LinesToList = f.read().split("\n")
    return LinesToList

def get_base_url(url):
    """Returns the base URL without query parameters."""
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"


def extract_phone_numbers(text):
    # Regular expression pattern to match phone numbers
    pattern = re.compile(r'''
        (
            \(?                  # open bracket (optional)
            \+?                  # plus sign (optional)
            \d{1,4}?             # country code (1-4 digits, optional)
            \)?                  # close bracket (optional)
            [\s.-]?              # separator (space, dot, or hyphen, optional)
            \d{1,4}              # first group of numbers (1-4 digits)
            [\s.-]?              # separator (space, dot, or hyphen)
            \d{1,4}              # second group of numbers (1-4 digits)
            [\s.-]?              # separator (space, dot, or hyphen)
            \d{1,4}              # third group of numbers (1-4 digits)
            (?:[\s.-]?           # separator (space, dot, or hyphen, optional, non-capturing)
            \d{1,4}              # fourth group of numbers (1-4 digits, optional)
            )?                   
        )
    ''', re.VERBOSE)
    
    return pattern.findall(text)



def send_intro_message(driver, url, profile_name):
    driver.get(url)
    time.sleep(3)
    name = driver.find_element(By.XPATH, "//h1[contains(@class,'text-heading-xlarge inline t-24 v-align-middle break-words')]").text
    #name = names[index]
    #name = driver.find_element(By.XPATH, "//div[@class='pv-text-details__left-panel']//div//h1[1]").text
    #print(name)
    #print(driver.find_element(By.XPATH, "//div[@class='text-body-medium break-words']").text)

    scroll_down(driver)
    try:
        titles = driver.find_elements(By.XPATH, "(//h2[contains(@class,'pvs-header__title')]//span)")
        titles_text = []
        for title in titles:
            titles_text.append(title.text) 
        indices = [i for i, s in enumerate(titles_text) if 'Experience' in s]
        print(indices)
        experience_title = []
        experience_desc = []
        experience_timeline = []
        try:
            driver.find_element(By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[' + str(indices[0]) + ']/div[3]/ul/li[1]/div/div[2]/div/div[1]/div/div/div/div/span[1]').text
            index = indices[0]
        except:
            try:
                driver.find_element(By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[' + str(indices[1]) + ']/div[3]/ul/li[1]/div/div[2]/div/div[1]/div/div/div/div/span[1]').text
                index = indices[1]
            except:
                try:
                    driver.find_element(By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[' + str(indices[0]) + ']/div[3]/ul/li[1]/div/div[2]/div[1]/a/div/div/div/div/span[1]').text
                    index = indices[0]
                except:
                    driver.find_element(By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[' + str(indices[1]) + ']/div[3]/ul/li[1]/div/div[2]/div[1]/a/div/div/div/div/span[1]').text
                    index = indices[1]


        for i in range(1, 4):
            try:
                experience_title.append(driver.find_element(By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[' + str(index) + ']/div[3]/ul/li[' + str(i) + ']/div/div[2]/div/div[1]/div/div/div/div/span[1]').text)
                experience_desc.append(driver.find_element(By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[' + str(index) + ']/div[3]/ul/li[' + str(i) + ']/div/div[2]/div/div[1]/span[1]/span[1]').text)
                experience_timeline.append(driver.find_element(By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[' + str(index) + ']/div[3]/ul/li[' + str(i) + ']/div/div[2]/div/div[1]/span[2]/span[1]').text)
            except:
                try:
                    experience_title.append(driver.find_element(By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[' + str(index) + ']/div[3]/ul/li[' + str(i) + ']/div/div[2]/div[1]/a/div/div/div/div/span[1]').text)
                    experience_desc.append("")
                    experience_timeline.append("")
                except:
                    continue
    
        experience = ""
        for i in range(len(experience_title)):
            experience += experience_title[i] + " " + experience_desc[i] + " " + experience_timeline[i] + " "
    except:
        experience = driver.find_element(By.XPATH, "//div[@class='text-body-medium break-words']").text
    
    #connect_message = get_connect_promt(name.split(" ")[0], experience, profile_name)
    message = get_intro_message(name.split(" ")[0], experience, profile_name)
    driver.back()
    time.sleep(1.5)
    driver.get(url)
    time.sleep(5)
    try:
        driver.find_element(By.XPATH, "(//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view')])").click()
        time.sleep(1.5)
    except:
        pass
    buttons = driver.find_elements(By.XPATH, "(//button[contains(@class,'artdeco-button artdeco-button--2')]//span)")
            
    for button in buttons:
        print(button.text)
        if button.text == "Message":
            button.click()
            break

    #message_buttons[c+1].click()
    try:
        time.sleep(2)
        driver.find_element(By.XPATH, "(//button[contains(@class,'artdeco-modal__dismiss artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view')])").click()
    except:
        pass
    time.sleep(2)
    driver.find_element(By.XPATH, "(//div[contains(@class,'msg-form__contenteditable t-14 t-black--light t-normal flex-grow-1 full-height notranslate')])").send_keys(message)
    time.sleep(2)
    
    driver.find_element(By.XPATH, "(//button[contains(@class,'msg-form__send-button artdeco-button artdeco-button--1')])").click()
    time.sleep(1.5)
    driver.find_element(By.XPATH, "(//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view')])").click()
    time.sleep(1.5)
    driver.back()
    



def run():
    while True:
        try:
            campaigns = get_campaigns()
            # Count the number of active campaigns for today
            active_campaigns = sum(1 for campaign in campaigns if campaign[3] <= datetime.now(timezone.utc) <= campaign[4])
            
            # Calculate the time spent on all active campaigns in seconds (30 minutes each)
            total_active_time = active_campaigns * 40 * 60
            
            # Calculate sleep duration by subtracting total active time from 24 hours
            sleep_duration = 86400 - total_active_time
            print(sleep_duration)
            for campaign in campaigns:
                print(campaign)
                campaign_id, campaign_name, location, start_date, end_date, job_title, connects_sent, connect_accepted, account, daily_count = campaign
                
                if not connects_sent:
                    connects_sent = 0
                today_count = 0
                if start_date <= datetime.now(timezone.utc) <= end_date:
                    end_time = datetime.now(timezone.utc) + timedelta(minutes=40) 
                    while datetime.now(timezone.utc) < end_time:
                        if daily_count:
                            if today_count == daily_count:
                                break
                        print("in campaign")
                        linkedin_account = get_account_by_id(account)
                        account_id, profile_name, cookies, proxyip, proxyport, proxyuser, proxypass = linkedin_account
                        job_title.replace(" ", "%20")

                        #driver = driverInit()
                        
                        driver = driverInit(proxyip, proxyport, proxyuser, proxypass)
                        driver.get("https://whatismyipaddress.com/")
                        time.sleep(3)
                        wait = WebDriverWait(driver, 10)
                        login_using_cookie_string(driver, cookies)
                        get_phone_numbers(driver, campaign_id, profile_name)
                        time.sleep(4)
                        driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
                        scroll_down(driver)
                        connect_urls = driver.find_elements(By.XPATH, "(//div[contains(@class,'mn-connection-card__details')]//a)")
                        print(connect_urls)
                        connection_urls = []
                        for connect_url in connect_urls:
                            connection_urls.append(connect_url.get_attribute('href'))
                        print(connection_urls)
                        

                        # Iterate through each profile to get its link
                        cursor, conn = get_db()
                        select_query = """SELECT "link" FROM "CRM_profile" WHERE "campaign_id" = %s AND "status" = 'Sent';"""
                        cursor.execute(select_query, (campaign_id,))
                        profiles = cursor.fetchall()
                        connect_accepted = 0
                        for profile in profiles:
                            profile_url = profile[0]
                            #base_profile_url = get_base_url(profile_url) + "/"
                            if profile_url in connection_urls:
                                print(profile_url)
                                send_intro_message(driver, profile_url, profile_name)
                                # Update the status field to "Accepted"
                                update_query = """UPDATE "CRM_profile" SET "status" = 'Accepted' WHERE "link" = %s;"""
                                cursor.execute(update_query, (profile_url,))
                                conn.commit()
                                connect_accepted = connect_accepted + 1
                        update_query = """
                        UPDATE "CRM_campaign"
                        SET "connect_accepted" = %s
                        WHERE "id" = %s;
                        """

                        # Prepare the data
                        update_data = (connect_accepted, campaign_id)  # replace new_connects_sent with the actual value
                        cursor, conn = get_db()
                        # Execute the update query
                        cursor.execute(update_query, update_data)

                        cursor, conn = get_db()
                        select_query = """SELECT * FROM "CRM_excel_file" WHERE "campaign_id" = %s LIMIT 1;"""
                        cursor.execute(select_query, (campaign_id,))
                        excel_file = cursor.fetchone()
                        conn.commit()
                        conn.close()


                        


                        # Initialize an empty list for URLs
                        urls = []

                        # Check if excel_file object was found
                        if excel_file:
                            # Extract the JSON string
                            json_string = excel_file[1]

                            # Parse the JSON string to get a Python dictionary
                            data_dict = json.loads(json_string)

                            # Extract the list of URLs
                            urls = data_dict.get("urls", [])
                        if urls == []:
                            driver.get("https://www.linkedin.com/search/results/people/?keywords=" + str(job_title) + "&origin=SWITCH_SEARCH_VERTICAL&searchId=e8feff38-c208-4344-b22d-adc4a1532ea0&sid=SST")
                            wait.until(EC.visibility_of_element_located((By.XPATH, "(//button[contains(@class,'artdeco-pill artdeco-pill--slate')])[3]")))
                            if location:
                                driver.find_element(By.XPATH, "(//button[contains(@class,'artdeco-pill artdeco-pill--slate')])[3]").click()
                                wait.until(EC.visibility_of_element_located((By.XPATH, " (//input[@role='combobox'])[2]")))
                                driver.find_element(By.XPATH, " (//input[@role='combobox'])[2]").send_keys(location)
                                time.sleep(2)
                                wait.until(EC.visibility_of_element_located((By.XPATH, "(//div[@class='search-typeahead-v2__hit search-typeahead-v2__hit--autocomplete'])[1]")))
                                driver.find_element(By.XPATH, "(//div[@class='search-typeahead-v2__hit search-typeahead-v2__hit--autocomplete'])[1]").click()
                                wait.until(EC.visibility_of_element_located((By.XPATH, "(//button[contains(@class,'artdeco-button artdeco-button--2')]//span)[2]")))
                                driver.find_element(By.XPATH, "(//button[contains(@class,'artdeco-button artdeco-button--2')]//span)[2]").click()
                                time.sleep(3)
                            url = driver.current_url + "&page="
                            urls = []
                            names = []
                            bios = []
                            for i in range(1, 10):
                                temp_url = url + str(i)
                                driver.get(temp_url)
                                time.sleep(3)
                                scroll_down(driver)
                                for j in range(2,20):
                                    try:
                                        profile = driver.find_element(By.XPATH, "(//a[@class='app-aware-link '])[" + str(j) + "]").get_attribute('href')
                                        name = driver.find_element(By.XPATH, "(//a[@class='app-aware-link ']//span)[" + str(j) + "]").text
                                        bio = driver.find_element(By.XPATH, "(//div[contains(@class,'entity-result__primary-subtitle t-14')])[" + str(j-1) + "]").text
                                        # Define the regex pattern
                                        pattern = r'https://www\.linkedin\.com/in/[\w\.-]+'

                                        # Check if a URL is a profile URL
                                        def is_profile_url(url):
                                            return bool(re.match(pattern, url))

                                        # Filter the list
                                        if is_profile_url(profile):
                                            print(profile)
                                            urls.append(profile)
                                            names.append(name)
                                            bios.append(bio)
                                    except:
                                        break
                            
                        
                        for index, url in enumerate(urls):
                            if datetime.now(timezone.utc) > end_time:
                                break
                            if daily_count:
                                if today_count == daily_count:
                                    break
                                

                            # Check if URL already exists in the CRM_profile
                            # Get connection and cursor
                            cursor, conn = get_db()
                            check_query = """SELECT COUNT(*) FROM "CRM_profile" WHERE "link" = %s;"""
                            cursor.execute(check_query, (url,))
                            exists = cursor.fetchone()[0]
                            if exists:
                                continue
                            try:
                                
                                #get_into_message(name.split(" ")[0], experience, profile_name)
                                try:
                                    driver.get(url)
                                    time.sleep(random.randint(2,5))
                                    name = driver.find_element(By.XPATH, "//h1[contains(@class,'text-heading-xlarge inline t-24 v-align-middle break-words')]").text
                                    scroll_down(driver)
                                    driver.back()
                                    driver.get(url)
                                    time.sleep(random.randint(2,5))
                                    buttons = driver.find_elements(By.XPATH, "(//button[contains(@class,'artdeco-dropdown__trigger artdeco-dropdown__trigger--placement-bottom')]//span)")
                                    
                                    for button in buttons:
                                        print(button.text)
                                    if driver.find_element(By.XPATH, "(//button[contains(@class,'artdeco-button artdeco-button--2')]//span)[3]").text == "Connect":
                                        driver.find_element(By.XPATH, "(//button[contains(@class,'artdeco-button artdeco-button--2')]//span)[3]").click()
                                    elif driver.find_element(By.XPATH, "(//button[contains(@class,'artdeco-button artdeco-button--2')]//span)[4]").text == "Connect":
                                        driver.find_element(By.XPATH, "(//button[contains(@class,'artdeco-button artdeco-button--2')]//span)[4]").click()
                                    elif driver.find_element(By.XPATH, "(//button[contains(@class,'artdeco-dropdown__trigger artdeco-dropdown__trigger--placement-bottom')]//span)[3]").text == "More":
                                        driver.find_element(By.XPATH, "(//button[contains(@class,'artdeco-dropdown__trigger artdeco-dropdown__trigger--placement-bottom')]//span)[3]").click()
                                        dropdown_elements = driver.find_elements(By.XPATH, "(//span[contains(@class,'display-flex t-normal flex-1')])")
                                        for d, element in enumerate(dropdown_elements):
                                            if element.text == "Connect":
                                                element.click()
                                                break
                                    elif driver.find_element(By.XPATH, "(//button[contains(@class,'artdeco-dropdown__trigger artdeco-dropdown__trigger--placement-bottom')]//span)[2]").text == "More":
                                        driver.find_element(By.XPATH, "(//button[contains(@class,'artdeco-dropdown__trigger artdeco-dropdown__trigger--placement-bottom')]//span)[2]").click()
                                        dropdown_elements = driver.find_elements(By.XPATH, "(//span[contains(@class,'display-flex t-normal flex-1')])")
                                        for d, element in enumerate(dropdown_elements):
                                            if element.text == "Connect":
                                                element.click()
                                                break
                                    else:
                                        continue
                                    
                                    
                                    driver.find_element(By.XPATH, "(//span[@class='artdeco-button__text'])[3]").click()
                                    time.sleep(random.randint(4,7))
                                    current_url = driver.current_url
                                    query = """
                                    INSERT INTO "CRM_profile" ("campaign_id", "name", "status", "link")
                                    VALUES (%s, %s, %s, %s);
                                    """

                                    # Prepare the data
                                    data = (campaign_id, name, 'Sent', current_url)
                                    # Execute the query
                                    cursor.execute(query, data)
                                


                                    # Commit the transaction
                                    conn.commit()
                                    conn.close()
                                    print("Profile added")
                                    connects_sent = connects_sent + 1
                                    today_count = today_count + 1
                                except:
                                    pass

                            except:
                                continue

                        driver.quit()
            time.sleep(sleep_duration)        
        except:
            logging.exception('msg')
            time.sleep(1000)
            #continue

run()
#print(get_images())