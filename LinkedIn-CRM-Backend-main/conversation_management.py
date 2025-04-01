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
from chatgpt_api import get_intro_message, get_follow_up, close_conversation, information_received_prompt, video_information_received_prompt, reconnect_prompt, jd_follow_up, extract_contact
from get_prompts import prompts
from write_job_descriptions import generate_detailed_job_description

intro_prompt, follow_up_prompt = prompts()

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

    connected = False
    while not connected:
        try:
            conn = psycopg2.connect(
                dbname=db_settings['NAME'],
                user=db_settings['USER'],
                password=db_settings['PASSWORD'],
                host=db_settings['HOST'],
                port=db_settings['PORT']
            )
            connected = True
            # If the connection was successful, you can proceed with your operations
            # ...
        except psycopg2.OperationalError as e:
            print(f"Error connecting to the database: {e}")
            print("Attempting to reconnect in 5 seconds...")
            time.sleep(5)
    # Get a cursor
    cursor = conn.cursor()
    return cursor, conn



def get_campaigns():
    # Setup database connection
    cursor, conn = get_db()

    # Specify the fields to select based on the model's fields
    cursor.execute("""
        SELECT
            "id",
            "name",
            "location",
            "start_date",
            "end_date",
            "job_title",
            "connects_sent",
            "connect_accepted",
            "account_id", 
            "daily_count",
            "category",
            "search_value",
            "boolean_search",
            "min_salary",
            "max_salary",
            "min_age",
            "max_age",
            "batch_size",
            "total_profile_count",
            "status"
        FROM "CRM_campaign"
        WHERE "boolean_search" IS NULL;
    """)

    # Fetch all rows from the executed query
    rows = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Return the retrieved rows
    return rows


# Function to convert timestamp text to actual date string
def convert_to_date_string(text):
    # Current date and time
    now = datetime.now()

    if text.lower() == 'today':
        return now.strftime('%Y-%m-%d')  # Return today's date as string
    elif text.lower() in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
        # Calculate how many days to subtract to get to the last occurrence of the given day
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        day_diff = (now.weekday() - days.index(text.lower())) % 7
        target_date = now - timedelta(days=day_diff)
        return target_date.strftime('%Y-%m-%d')
    else:
        # Try to parse the date directly
        for fmt in ('%b %d, %Y', '%B %d, %Y'):  # Add more formats here if needed
            try:
                actual_date = datetime.strptime(text, fmt)
                return actual_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
    # Return an empty string or a predefined string if none of the formats matched
    return 'Unknown Date'
       
def get_account_by_id(account_id):
    cursor, conn = get_db()
    cursor.execute("""SELECT * FROM "CRM_account" WHERE id = %s;""", (account_id,))
    row = cursor.fetchone()  # Assuming account IDs are unique, so you'd get at most one row
    conn.close()
    return row

def get_accounts():
    

    cursor, conn = get_db()
    cursor.execute("""SELECT * FROM "CRM_account";""")
    rows = cursor.fetchall()
    conn.close()
    return rows




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
                message = get_follow_up(lead_name, profile_name.split(" ")[0], total_messages_list[p], last_message_day_string)
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

def scroll_container_down(driver, container):
    SCROLL_PAUSE_TIME = 1

    # Get container's scroll height
    last_height = driver.execute_script("return arguments[0].scrollHeight", container)

    while True:
        # Scroll down
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)

        # Wait to load
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return arguments[0].scrollHeight", container)
        if new_height == last_height:
            break
        last_height = new_height


def video_call_detection(message):
    keywords = ["video call", "video chat", "skype", "zoom", "teams", "google meet", "video meeting", "video conference", "video session", "video meeting"]
    # Convert the message to lower case to make the search case-insensitive
    message = message.lower()
    
    # Check each keyword in the list
    for keyword in keywords:
        if keyword in message:
            return True
    
    return False

def jd_detection(message):
    keywords =  [
    "job description",
    "position details",
    "role overview",
    "job responsibilities",
    "job duties",
    "role responsibilities",
    "position summary",
    "employment details",
    "job specifics",
    "position specifics",
    "job role",
    "position description",
    "job outline",
    "role outline",
    "work description",
    "duties and responsibilities",
    "job functions",
    "role expectations",
    "job profile",
    "job qualifications",
    "position qualifications",
    "role summary",
    "job summary",
    "position duties",
    "job specs",
    "jd",
    "job requirements",
    "role qualifications",
    "essential functions",
    "job competencies",
    "position requirements",
    "employment qualifications",
    "role duties",
    "work responsibilities",
    "career opportunity details",
    "position attributes",
    "employment responsibilities",
    "job scope",
    "role scope",
    "position scope",
    "job criteria",
    "role criteria",
    "position criteria",
    "work specifics",
    "employment specifics",
    "career specifics",
    "job expectations",
    "role performance criteria",
    "position performance criteria",
    "job activities",
    "role activities",
    "position activities",
    "work duties",
    "employment duties",
    "career duties",
    "job summary details",
    "role summary details",
    "position summary details",
    "job description summary",
    "employment overview",
    "career overview",
    "job description outline",
    "role description outline",
    "position description outline",
    "job task list",
    "role task list",
    "position task list",
    "job qualification requirements",
    "role qualification requirements",
    "position qualification requirements",
    "job experience requirements",
    "role experience requirements",
    "position experience requirements",
    "work experience requirements",
    "employment experience requirements",
    "career experience requirements",
    "more details",
    "high level details",
    "detailed job information",
    "in-depth job details",
    "comprehensive job overview",
    "expanded job description",
    "detailed role description",
    "comprehensive role specifics",
    "expanded position details",
    "in-depth employment details",
    "JD",
    "QR",
    "PD",
    "JDs",
    "PRs",
    "JQs",
    "RQs",
    "JSs",
    "RSs",
    "PSs"
]


    # Convert the message to lower case to make the search case-insensitive
    message = message.lower()
    
    # Check each keyword in the list
    for keyword in keywords:
        if keyword in message:
            return True
    
    return False

def get_phone_numbers_updated(driver, profile_name):
    try:
        decoded_urls = []
        contact_numbers = []
        actual_urls = []
        driver.get("https://www.linkedin.com/")
        time.sleep(5)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located((By.XPATH, "(//span[contains(@class,'t-12 break-words block t-black--light t-normal')])[4]")))
        driver.find_element(By.XPATH, "(//span[contains(@class,'t-12 break-words block t-black--light t-normal')])[4]").click()
        time.sleep(random.randint(3,6))
        wait.until(EC.visibility_of_element_located((By.XPATH, "(//h3[contains(@class,'msg-conversation-listitem__participant-names msg-conversation-card__participant-names')])")))



        total_messages_list = []
        messages_profiles = []
        profiles_container = driver.find_element(By.XPATH, "(//ul[contains(@class,'list-style-none msg-conversations-container__conversations-list')])")
        for j in range(1,4):
            for i in range(1,3):
                scroll_container_down(driver, profiles_container)
                print("scrolling")
                time.sleep(5)
            try:
                driver.find_element(By.XPATH, "//buttom[@class='block mlA mrA artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view']//span").click()
            except:
                break
       
        profile_messages = driver.find_elements(By.XPATH, "(//h3[contains(@class,'msg-conversation-listitem__participant-names msg-conversation-card__participant-names')])")
        print(len(profile_messages))
        for p in range(1, 100):
            profile_clicked = None

            if p  == 55:
                break
            try:
                driver.find_element(By.XPATH, f"(//h3[contains(@class,'msg-conversation-listitem__participant-names msg-conversation-card__participant-names')])[{p + 1}]").click()
                #profile_message.click()
                time.sleep(2)
                messages = driver.find_elements(By.XPATH, "(//p[contains(@class,'msg-s-event-listitem__body t-14')])")
                messages_names = driver.find_elements(By.XPATH, "(//span[contains(@class,'msg-s-message-group__profile-link msg-s-message-group__name t-14 t-black t-bold hoverable-link-text')])")
                for m, message_name in enumerate(messages_names):
                    if m == len(messages_names) - 1:
                        last_message_name = message_name.text
                try:
                    last_message_time = driver.find_elements(By.XPATH, "(//time[@class='msg-s-message-list__time-heading t-12 t-black--light t-bold'])")[-1].text
                    last_message_day_string = convert_to_date_string(last_message_time)
                    print(last_message_day_string)
                except:
                    continue
                phone_flag = None
                video_flag = None
                jd_flag = None
                profile_clicked = None
                contact_exist = None
                messages_list = []

                for message in messages:
                    messages_list.append(message.text)

                if last_message_name != driver.find_element(By.ID, "thread-detail-jump-target").text:
                    if len(messages_list) == 1:
                        try:
                            driver.find_element(By.ID, "thread-detail-jump-target").click()
                            time.sleep(random.randint(3,6))
                            wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(@class,'text-heading-xlarge inline t-24 v-align-middle break-words')]")))
                            profile_clicked = True
                            lead_name = driver.find_element(By.XPATH, "//h1[contains(@class,'text-heading-xlarge inline t-24 v-align-middle break-words')]").text
                            location = driver.find_element(By.XPATH, "(//span[contains(@class,'text-body-small inline t-black--light break-words')])").text
                            time.sleep(1)
                            profile_url = driver.current_url
                            cursor, conn = get_db()
                            query = """
                                        SELECT "last_communication", "status" 
                                        FROM "CRM_profile" 
                                        WHERE "link" = %s AND "status" = 'Accepted' AND "contact_number" IS NULL
                                    """
                            cursor.execute(query, (profile_url,))
                            result = cursor.fetchone()
                            
                            # Check if the last_communication field exists and is not None
                            if result and result[0]:
                                last_communication = result[0]
                                status = result[1]
                                if status != "Reconnected":
                                    current_date = datetime.now(timezone.utc)

                                    # Calculate the difference in days
                                    difference = (current_date - last_communication).days
                                    if difference > 14:
                                        print('Reconnect message trigerred')
                                        print('Crossed 14 days')
                                        
                                        message = reconnect_prompt(lead_name.split(" ")[0], profile_name.split(" ")[0], messages_list)
                                        print(message)
                                        time.sleep(40)
                                        close_elements = driver.find_elements(By.XPATH, "(//button[contains(@class,'artdeco-modal__dismiss artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view')])")
                                        for element in close_elements:
                                            element.click()
                                            time.sleep(1)
                                        additional_close_buttons = driver.find_elements(By.XPATH, "//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--1 artdeco-button--primary ember-view') or contains(@class,'artdeco-modal__dismiss artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view')]")
                                        for button in additional_close_buttons:
                                            button.click()
                                            time.sleep(1)
                                        print("closed all messages")
                                        buttons = driver.find_elements(By.XPATH, "(//button[contains(@class,'artdeco-button artdeco-button--2')]//span)")
                                                
                                        for button in buttons:
                                            print(button.text)
                                            if button.text == "Message":
                                                button.click()
                                                break
                                        
                                        wait.until(EC.visibility_of_element_located((By.XPATH, "(//div[contains(@class,'msg-form__contenteditable t-14 t-black--light t-normal flex-grow-1 full-height notranslate')])")))

                                        driver.find_element(By.XPATH, "(//div[contains(@class,'msg-form__contenteditable t-14 t-black--light t-normal flex-grow-1 full-height notranslate')])").send_keys(message)
                                        time.sleep(20)
                                        
                                        driver.find_element(By.XPATH, "(//button[contains(@class,'msg-form__send-button artdeco-button artdeco-button--1')])").click()
                                        time.sleep(1.5)
                                        driver.find_element(By.XPATH, "(//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view')])").click()
                                        time.sleep(1.5)
                                        cursor, conn = get_db()
                                        
                                        update_query = """UPDATE "CRM_profile" SET "status" = %s WHERE "link" = %s;"""
                                        cursor.execute(update_query, ("Reconnected", profile_url))
                                        conn.commit()
                            if profile_clicked:
                                driver.back()
                                #driver.refresh()

                                time.sleep(random.randint(4,7))
                                profiles_container = driver.find_element(By.XPATH, "(//ul[contains(@class,'list-style-none msg-conversations-container__conversations-list')])")

                                for j in range(1,4):
                                    for i in range(1,3):
                                        scroll_container_down(driver, profiles_container)
                                        print("scrolling")
                                        time.sleep(5)
                                    try:
                                        driver.find_element(By.XPATH, "//buttom[@class='block mlA mrA artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view']//span").click()
                                    except:
                                        break
                            continue
                        except:
                            logging.exception('msg')
                            if profile_clicked:
                                driver.back()
                                #driver.refresh()

                                time.sleep(random.randint(4,7))
                                profiles_container = driver.find_element(By.XPATH, "(//ul[contains(@class,'list-style-none msg-conversations-container__conversations-list')])")

                                for j in range(1,4):
                                    for i in range(1,3):
                                        scroll_container_down(driver, profiles_container)
                                        print("scrolling")
                                        time.sleep(5)
                                    try:
                                        driver.find_element(By.XPATH, "//buttom[@class='block mlA mrA artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view']//span").click()
                                    except:
                                        break
                            continue
                    else:
                        contact_exist = True

                
                for msg in messages_list:
                    if extract_contact(msg) != None:
                        print(msg)
                        phone_flag = True
                        print("Phone Number : ",extract_contact(msg))
                        contact_numbers.append(extract_contact(msg))
                        contact_number = extract_contact(msg)
                        profile_link = driver.find_element(By.XPATH, "(//a[contains(@class,'app-aware-link  msg-thread__link-to-profile')])").get_attribute("href")
                        print("Profile Link : ", profile_link)
                        decoded_urls.append(profile_link)
                        driver.find_element(By.ID, "thread-detail-jump-target").click()
                        time.sleep(random.randint(3,6))
                        wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(@class,'text-heading-xlarge inline t-24 v-align-middle break-words')]")))
                        profile_clicked = True
                        lead_name = driver.find_element(By.XPATH, "//h1[contains(@class,'text-heading-xlarge inline t-24 v-align-middle break-words')]").text
                        location = driver.find_element(By.XPATH, "(//span[contains(@class,'text-body-small inline t-black--light break-words')])").text
                        time.sleep(1)
                        profile_url = driver.current_url
                        cursor, conn = get_db()
                        check_query = """SELECT COUNT(*) FROM "CRM_profile" WHERE "link" = %s"""
                        cursor.execute(check_query, (profile_url,))
                        exists = cursor.fetchone()[0]
                        if exists:
                            cursor, conn = get_db()
                            check_query = """SELECT COUNT(*) FROM "CRM_profile" WHERE "link" = %s AND "contact_number" IS NULL;"""
                            cursor.execute(check_query, (profile_url,))
                            contact_not_exists = cursor.fetchone()[0]
                            if contact_not_exists:
                                 
                                message = information_received_prompt(lead_name.split(" ")[0], profile_name.split(" ")[0], messages_list, last_message_day_string)
                                print(message)
                                time.sleep(40)
                                
                                buttons = driver.find_elements(By.XPATH, "(//button[contains(@class,'artdeco-button artdeco-button--2')]//span)")
                                        
                                close_elements = driver.find_elements(By.XPATH, "(//button[contains(@class,'artdeco-modal__dismiss artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view')])")
                                for element in close_elements:
                                    element.click()
                                    time.sleep(1)
                                
                                additional_close_buttons = driver.find_elements(By.XPATH, "//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--1 artdeco-button--primary ember-view') or contains(@class,'artdeco-modal__dismiss artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view')]")
                                for button in additional_close_buttons:
                                    button.click()
                                    time.sleep(1)
                                print("closed all messages")
                                buttons = driver.find_elements(By.XPATH, "(//button[contains(@class,'artdeco-button artdeco-button--2')]//span)")
                                        
                                for button in buttons:
                                    print(button.text)
                                    if button.text == "Message":
                                        button.click()
                                        break
                                
                                wait.until(EC.visibility_of_element_located((By.XPATH, "(//div[contains(@class,'msg-form__contenteditable t-14 t-black--light t-normal flex-grow-1 full-height notranslate')])")))
                                driver.find_element(By.XPATH, "(//div[contains(@class,'msg-form__contenteditable t-14 t-black--light t-normal flex-grow-1 full-height notranslate')])").send_keys(message)
                                time.sleep(20)
                                
                                driver.find_element(By.XPATH, "(//button[contains(@class,'msg-form__send-button artdeco-button artdeco-button--1')])").click()
                                time.sleep(1.5)
                                driver.find_element(By.XPATH, "(//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view')])").click()
                                time.sleep(1.5)
                                # Update the record if it exists
                                update_query = """UPDATE "CRM_profile" SET "contact_number" = %s, "last_communication" = %s WHERE "link" = %s;"""
                                cursor.execute(update_query, (contact_number, datetime.now(), profile_url))
                            else:
                                # Query to get the last_communication field and check if status is not closed
                                query = """
                                    SELECT "last_communication", "status" 
                                    FROM "CRM_profile" 
                                    WHERE "link" = %s AND "status" != 'closed'
                                """
                                cursor.execute(query, (profile_url,))
                                result = cursor.fetchone()
                                
                                # Check if the last_communication field exists and is not None
                                if result and result[0]:
                                    print("Checking for last conversation")
                                    last_communication = result[0]
                                    current_date = datetime.now(timezone.utc)

                                    # Calculate the difference in days
                                    difference = (current_date - last_communication).days
                                    if difference > 5:
                                        print('Crossed 5 days')
                                        
                                        message = close_conversation(lead_name.split(" ")[0], profile_name.split(" ")[0], messages_list)
                                        print(message)
                                        time.sleep(40)
                                        
                                        close_elements = driver.find_elements(By.XPATH, "(//button[contains(@class,'artdeco-modal__dismiss artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view')])")
                                        for element in close_elements:
                                            element.click()
                                            time.sleep(1)
                                        
                                        additional_close_buttons = driver.find_elements(By.XPATH, "//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--1 artdeco-button--primary ember-view') or contains(@class,'artdeco-modal__dismiss artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view')]")
                                        for button in additional_close_buttons:
                                            button.click()
                                            time.sleep(1)
                                        print("closed all messages")
                                        buttons = driver.find_elements(By.XPATH, "(//button[contains(@class,'artdeco-button artdeco-button--2')]//span)")
                                                
                                        for button in buttons:
                                            print(button.text)
                                            if button.text == "Message":
                                                button.click()
                                                break
                                        
                                        wait.until(EC.visibility_of_element_located((By.XPATH, "(//div[contains(@class,'msg-form__contenteditable t-14 t-black--light t-normal flex-grow-1 full-height notranslate')])")))
                                        driver.find_element(By.XPATH, "(//div[contains(@class,'msg-form__contenteditable t-14 t-black--light t-normal flex-grow-1 full-height notranslate')])").send_keys(message)
                                        time.sleep(20)
                                        
                                        driver.find_element(By.XPATH, "(//button[contains(@class,'msg-form__send-button artdeco-button artdeco-button--1')])").click()
                                        time.sleep(1.5)
                                        driver.find_element(By.XPATH, "(//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view')])").click()
                                        time.sleep(1.5)
                                        cursor, conn = get_db()
                                        
                                        update_query = """UPDATE "CRM_profile" SET "status" = %s WHERE "link" = %s;"""
                                        cursor.execute(update_query, ("closed", profile_url))
                                        conn.commit()

                        conn.commit()
                        driver.back()
                        #driver.refresh()

                        time.sleep(random.randint(4,7))
                        profiles_container = driver.find_element(By.XPATH, "(//ul[contains(@class,'list-style-none msg-conversations-container__conversations-list')])")

                        for j in range(1,4):
                            for i in range(1,3):
                                scroll_container_down(driver, profiles_container)
                                print("scrolling")
                                time.sleep(5)
                            try:
                                driver.find_element(By.XPATH, "//buttom[@class='block mlA mrA artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view']//span").click()
                            except:
                                break
                        break

                    print(extract_phone_numbers(msg))
                    time.sleep(4)

                if not contact_exist:
                    if messages_list and not phone_flag: 
                        video_call_status = video_call_detection(messages_list[-1])
                        if video_call_status:
                            print("Video call Detected")
                            video_flag = True
                            driver.find_element(By.ID, "thread-detail-jump-target").click()
                            time.sleep(random.randint(3,6))
                            wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(@class,'text-heading-xlarge inline t-24 v-align-middle break-words')]")))
                            profile_clicked = True
                            lead_name = driver.find_element(By.XPATH, "//h1[contains(@class,'text-heading-xlarge inline t-24 v-align-middle break-words')]").text
                            location = driver.find_element(By.XPATH, "(//span[contains(@class,'text-body-small inline t-black--light break-words')])").text
                            time.sleep(1)
                            profile_url = driver.current_url
                            cursor, conn = get_db()
                            check_query = """SELECT COUNT(*) FROM "CRM_profile" WHERE "link" = %s"""
                            cursor.execute(check_query, (profile_url,))
                            exists = cursor.fetchone()[0]
                            if exists:
                                cursor, conn = get_db()
                                check_query = """SELECT COUNT(*) FROM "CRM_profile" WHERE "link" = %s AND "contact_number" IS NULL;"""
                                cursor.execute(check_query, (profile_url,))
                                contact_not_exists = cursor.fetchone()[0]
                                if contact_not_exists:
                                    
                                    message = video_information_received_prompt(lead_name.split(" ")[0], profile_name.split(" ")[0], messages_list, last_message_day_string)
                                    print(message)
                                    time.sleep(40)
                                    
                                    close_elements = driver.find_elements(By.XPATH, "(//button[contains(@class,'artdeco-modal__dismiss artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view')])")
                                    for element in close_elements:
                                        element.click()
                                        time.sleep(1)
                                    additional_close_buttons = driver.find_elements(By.XPATH, "//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--1 artdeco-button--primary ember-view') or contains(@class,'artdeco-modal__dismiss artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view')]")
                                    for button in additional_close_buttons:
                                        button.click()
                                        time.sleep(1)
                                    print("closed all messages")
                                    buttons = driver.find_elements(By.XPATH, "(//button[contains(@class,'artdeco-button artdeco-button--2')]//span)")
                                            
                                    for button in buttons:
                                        print(button.text)
                                        if button.text == "Message":
                                            button.click()
                                            break
                                    
                                    wait.until(EC.visibility_of_element_located((By.XPATH, "(//div[contains(@class,'msg-form__contenteditable t-14 t-black--light t-normal flex-grow-1 full-height notranslate')])")))
                                    driver.find_element(By.XPATH, "(//div[contains(@class,'msg-form__contenteditable t-14 t-black--light t-normal flex-grow-1 full-height notranslate')])").send_keys(message)
                                    time.sleep(20)
                                    
                                    driver.find_element(By.XPATH, "(//button[contains(@class,'msg-form__send-button artdeco-button artdeco-button--1')])").click()
                                    time.sleep(1.5)
                                    driver.find_element(By.XPATH, "(//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view')])").click()
                                    time.sleep(1.5)
                                    # Update the record if it exists
                                    update_query = """UPDATE "CRM_profile" SET "contact_number" = %s, "last_communication" = %s WHERE "link" = %s;"""
                                    cursor.execute(update_query, ("Video Call Excluded", datetime.now(), profile_url))
                                else:
                                    # Query to get the last_communication field and check if status is not closed
                                    query = """
                                        SELECT "last_communication", "status" 
                                        FROM "CRM_profile" 
                                        WHERE "link" = %s AND "status" != 'closed'
                                    """
                                    cursor.execute(query, (profile_url,))
                                    result = cursor.fetchone()
                                    
                                    # Check if the last_communication field exists and is not None
                                    if result and result[0]:
                                        last_communication = result[0]
                                        current_date = datetime.datetime.now()

                                        # Calculate the difference in days
                                        difference = (current_date - last_communication).days
                                        if difference > 5:
                                            print('Crossed 5 days')
                                            
                                            message = close_conversation(lead_name.split(" ")[0], profile_name.split(" ")[0], messages_list)
                                            print(message)
                                            time.sleep(40)
                                            
                                            close_elements = driver.find_elements(By.XPATH, "(//button[contains(@class,'artdeco-modal__dismiss artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view')])")
                                            for element in close_elements:
                                                element.click()
                                                time.sleep(1)
                                            additional_close_buttons = driver.find_elements(By.XPATH, "//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--1 artdeco-button--primary ember-view') or contains(@class,'artdeco-modal__dismiss artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view')]")
                                            for button in additional_close_buttons:
                                                button.click()
                                                time.sleep(1)
                                            print("closed all messages")
                                            buttons = driver.find_elements(By.XPATH, "(//button[contains(@class,'artdeco-button artdeco-button--2')]//span)")
                                                    
                                            for button in buttons:
                                                print(button.text)
                                                if button.text == "Message":
                                                    button.click()
                                                    break
                                            
                                            wait.until(EC.visibility_of_element_located((By.XPATH, "(//div[contains(@class,'msg-form__contenteditable t-14 t-black--light t-normal flex-grow-1 full-height notranslate')])")))
                                            driver.find_element(By.XPATH, "(//div[contains(@class,'msg-form__contenteditable t-14 t-black--light t-normal flex-grow-1 full-height notranslate')])").send_keys(message)
                                            time.sleep(20)
                                            
                                            driver.find_element(By.XPATH, "(//button[contains(@class,'msg-form__send-button artdeco-button artdeco-button--1')])").click()
                                            time.sleep(1.5)
                                            driver.find_element(By.XPATH, "(//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view')])").click()
                                            time.sleep(1.5)
                                            cursor, conn = get_db()
                                            
                                            update_query = """UPDATE "CRM_profile" SET "status" = %s WHERE "link" = %s;"""
                                            cursor.execute(update_query, ("closed", profile_url))
                                            conn.commit()

                

                            conn.commit()
                            driver.back()
                            #driver.refresh()

                            time.sleep(random.randint(4,7))
                            profiles_container = driver.find_element(By.XPATH, "(//ul[contains(@class,'list-style-none msg-conversations-container__conversations-list')])")

                            for j in range(1,4):
                                for i in range(1,3):
                                    scroll_container_down(driver, profiles_container)
                                    print("scrolling")
                                    time.sleep(5)
                                try:
                                    driver.find_element(By.XPATH, "//buttom[@class='block mlA mrA artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view']//span").click()
                                except:
                                    break
                            break


                    

                    
                    if not phone_flag and not video_flag and messages_list:
                        for msg in messages_list:
                            jd_flag = jd_detection(msg)
                            if jd_flag:
                                break
                        if jd_flag:
                                print("JD Follow up")
                                try:
                                    messages_profiles.append(driver.find_element(By.XPATH, "(//a[contains(@class,'app-aware-link  msg-thread__link-to-profile')])").get_attribute("href"))
                                    total_messages_list.append(messages_list)
                                    driver.find_element(By.ID, "thread-detail-jump-target").click()
                                    time.sleep(random.randint(3,6))
                                    wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(@class,'text-heading-xlarge inline t-24 v-align-middle break-words')]")))
                                    profile_clicked = True
                                    lead_name = driver.find_element(By.XPATH, "//h1[contains(@class,'text-heading-xlarge inline t-24 v-align-middle break-words')]").text
                                    location = driver.find_element(By.XPATH, "(//span[contains(@class,'text-body-small inline t-black--light break-words')])").text

                                    time.sleep(1)
                                    profile_url = driver.current_url
                                    cursor, conn = get_db()
                                    check_query = """SELECT COUNT(*) FROM "CRM_profile" WHERE "link" = %s AND "contact_number" IS NULL AND ("jd_status" IS NULL OR "jd_status" = FALSE);"""
                                    cursor.execute(check_query, (profile_url,))
                                    contact_not_exists = cursor.fetchone()[0]
                                    if contact_not_exists:
                                        bio = driver.find_element(By.XPATH, "//div[@class='text-body-medium break-words']").text

                                        time.sleep(random.randint(3, 5))

                                        scroll_down(driver)
                                        #try:
                                        #   get_experience(driver)
                                        #except:
                                        #   logging.exception('msg')
                                        #  time.sleep(1000)
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
                                        #message_prompt = intro_prompt.replace("{recruiter_name}", profile_name).replace("{lead_name}", name.split(" ")[0]).replace("{experience}", experience).replace("{bio}", bio)
                                        #message = get_intro_message(name.split(" ")[0], experience, profile_name, message_prompt)
                                        #driver.back()
                                        #time.sleep(1.5)
                                        #driver.get(url)
                                        scroll_up(driver)
                                        time.sleep(5)
                                        try:
                                            driver.find_element(By.XPATH, "(//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view')])").click()
                                            time.sleep(1.5)
                                        except:
                                            pass
                                    
                                        message = jd_follow_up(lead_name.split(" ")[0], profile_name.split(" ")[0], messages_list, location, experience, bio, last_message_day_string)
                                        print(message)
                                        time.sleep(20)
                                        jd_path = generate_detailed_job_description(lead_name.split(" ")[0], experience, location)
                                        close_elements = driver.find_elements(By.XPATH, "(//button[contains(@class,'artdeco-modal__dismiss artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view')])")
                                        for element in close_elements:
                                            element.click()
                                            time.sleep(1)
                                        additional_close_buttons = driver.find_elements(By.XPATH, "//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--1 artdeco-button--primary ember-view') or contains(@class,'artdeco-modal__dismiss artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view')]")
                                        for button in additional_close_buttons:
                                            button.click()
                                            time.sleep(1)
                                        print("closed all messages")
                                        buttons = driver.find_elements(By.XPATH, "(//button[contains(@class,'artdeco-button artdeco-button--2')]//span)")
                                                
                                        for button in buttons:
                                            print(button.text)
                                            if button.text == "Message":
                                                button.click()
                                                break
                                        
                                        wait.until(EC.visibility_of_element_located((By.XPATH, "(//div[contains(@class,'msg-form__contenteditable t-14 t-black--light t-normal flex-grow-1 full-height notranslate')])")))
                                        driver.find_element(By.XPATH, "(//div[contains(@class,'msg-form__contenteditable t-14 t-black--light t-normal flex-grow-1 full-height notranslate')])").send_keys(message)
                                        time.sleep(10)
                                        # Locate the file input element using its XPath
                                        file_input_element = driver.find_element(By.XPATH, "(//div[@class='msg-form__upload-attachment inline-block']//input[3])")

                                        # Convert it to an absolute path
                                        jd_path_absolute = os.path.abspath(jd_path)

                                        # Then use this absolute path when sending the file
                                        file_input_element.send_keys(jd_path_absolute)


                                        time.sleep(20)
                                        
                                        driver.find_element(By.XPATH, "(//button[contains(@class,'msg-form__send-button artdeco-button artdeco-button--1')])").click()
                                        time.sleep(1.5)
                                        driver.find_element(By.XPATH, "(//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view')])").click()
                                        time.sleep(1.5)
                                        cursor, conn = get_db()
                                        check_query = """SELECT COUNT(*) FROM "CRM_profile" WHERE "link" = %s"""
                                        cursor.execute(check_query, (profile_url,))
                                        exists = cursor.fetchone()[0]
                                        if exists:
                                            update_query = """UPDATE "CRM_profile" SET "intro_message" = %s, "last_communication" = %s, "jd_status" = %s WHERE "link" = %s;"""
                                            cursor.execute(update_query, ("Success", datetime.now(), True, profile_url))
                                            conn.commit()
                                        else:
                                            # Insert a new record if it doesn't exist
                                            insert_query = """INSERT INTO "CRM_profile" ("name", "intro_message", "link", "status", "last_communication", "jd_status")
                                                            VALUES (%s, %s, %s, 'Accepted', %s);"""
                                            cursor.execute(insert_query, (lead_name, "Success", profile_url, datetime.now(), True))
                                            conn.commit()
                                    else:
                                        jd_flag = None
                                        print("Contact Exist")
                                    

                                    driver.back()
                                    #driver.refresh()

                                    time.sleep(random.randint(4,7))
                                    profiles_container = driver.find_element(By.XPATH, "(//ul[contains(@class,'list-style-none msg-conversations-container__conversations-list')])")

                                    for j in range(1,4):
                                        for i in range(1,3):
                                            scroll_container_down(driver, profiles_container)
                                            print("scrolling")
                                            time.sleep(5)
                                        try:
                                            driver.find_element(By.XPATH, "//buttom[@class='block mlA mrA artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view']//span").click()
                                        except:
                                            break


                                    
                                except:
                                    logging.exception('msg')
                                    if profile_clicked:
                                        driver.back()
                                        #driver.refresh()

                                        time.sleep(random.randint(4,7))
                                        profiles_container = driver.find_element(By.XPATH, "(//ul[contains(@class,'list-style-none msg-conversations-container__conversations-list')])")

                                        for j in range(1,4):
                                            for i in range(1,3):
                                                scroll_container_down(driver, profiles_container)
                                                print("scrolling")
                                                time.sleep(5)
                                            try:
                                                driver.find_element(By.XPATH, "//buttom[@class='block mlA mrA artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view']//span").click()
                                            except:
                                                break
                                    continue
                        

                        if not jd_flag:
                            print("General Follow up")
                            try:

                                messages_profiles.append(driver.find_element(By.XPATH, "(//a[contains(@class,'app-aware-link  msg-thread__link-to-profile')])").get_attribute("href"))
                                total_messages_list.append(messages_list)
                                driver.find_element(By.ID, "thread-detail-jump-target").click()
                                time.sleep(random.randint(3,6))
                                wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(@class,'text-heading-xlarge inline t-24 v-align-middle break-words')]")))
                                profile_clicked = True
                                lead_name = driver.find_element(By.XPATH, "//h1[contains(@class,'text-heading-xlarge inline t-24 v-align-middle break-words')]").text
                                location = driver.find_element(By.XPATH, "(//span[contains(@class,'text-body-small inline t-black--light break-words')])").text

                                time.sleep(1)
                                profile_url = driver.current_url
                                cursor, conn = get_db()
                                check_query = """SELECT COUNT(*) FROM "CRM_profile" WHERE "link" = %s AND "contact_number" IS NULL;"""
                                cursor.execute(check_query, (profile_url,))
                                contact_not_exists = cursor.fetchone()[0]
                                if contact_not_exists:
                                    bio = driver.find_element(By.XPATH, "//div[@class='text-body-medium break-words']").text

                                    time.sleep(random.randint(3, 5))

                                    scroll_down(driver)
                                    #try:
                                    #   get_experience(driver)
                                    #except:
                                    #   logging.exception('msg')
                                    #  time.sleep(1000)
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
                                    #message_prompt = intro_prompt.replace("{recruiter_name}", profile_name).replace("{lead_name}", name.split(" ")[0]).replace("{experience}", experience).replace("{bio}", bio)
                                    #message = get_intro_message(name.split(" ")[0], experience, profile_name, message_prompt)
                                    #driver.back()
                                    #time.sleep(1.5)
                                    #driver.get(url)
                                    scroll_up(driver)
                                    time.sleep(5)
                                    try:
                                        driver.find_element(By.XPATH, "(//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view')])").click()
                                        time.sleep(1.5)
                                    except:
                                        pass
                                
                                    message = get_follow_up(lead_name.split(" ")[0], profile_name.split(" ")[0], messages_list, location, experience, bio, last_message_day_string)
                                    print(message)
                                    time.sleep(40)
                                    close_elements = driver.find_elements(By.XPATH, "(//button[contains(@class,'artdeco-modal__dismiss artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view')])")
                                    for element in close_elements:
                                        element.click()
                                        time.sleep(1)
                                    additional_close_buttons = driver.find_elements(By.XPATH, "//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--1 artdeco-button--primary ember-view') or contains(@class,'artdeco-modal__dismiss artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view')]")
                                    for button in additional_close_buttons:
                                        button.click()
                                        time.sleep(1)
                                    print("closed all messages")
                                    buttons = driver.find_elements(By.XPATH, "(//button[contains(@class,'artdeco-button artdeco-button--2')]//span)")
                                            
                                    for button in buttons:
                                        print(button.text)
                                        if button.text == "Message":
                                            button.click()
                                            break
                                    
                                    wait.until(EC.visibility_of_element_located((By.XPATH, "(//div[contains(@class,'msg-form__contenteditable t-14 t-black--light t-normal flex-grow-1 full-height notranslate')])")))
                                    driver.find_element(By.XPATH, "(//div[contains(@class,'msg-form__contenteditable t-14 t-black--light t-normal flex-grow-1 full-height notranslate')])").send_keys(message)
                                    time.sleep(20)
                                    
                                    driver.find_element(By.XPATH, "(//button[contains(@class,'msg-form__send-button artdeco-button artdeco-button--1')])").click()
                                    time.sleep(1.5)
                                    driver.find_element(By.XPATH, "(//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view')])").click()
                                    time.sleep(1.5)
                                    cursor, conn = get_db()
                                    check_query = """SELECT COUNT(*) FROM "CRM_profile" WHERE "link" = %s"""
                                    cursor.execute(check_query, (profile_url,))
                                    exists = cursor.fetchone()[0]
                                    if exists:
                                        update_query = """UPDATE "CRM_profile" SET "intro_message" = %s, "last_communication" = %s WHERE "link" = %s;"""
                                        cursor.execute(update_query, ("Success", datetime.now(), profile_url))
                                        conn.commit()
                                    else:
                                        # Insert a new record if it doesn't exist
                                        insert_query = """INSERT INTO "CRM_profile" ("name", "intro_message", "link", "status", "last_communication")
                                                        VALUES (%s, %s, %s, 'Accepted', %s);"""
                                        cursor.execute(insert_query, (lead_name, "Success", profile_url, datetime.now()))
                                        conn.commit()
                                else:
                                    print("Contact Exist")

                                driver.back()
                                #driver.refresh()

                                time.sleep(random.randint(4,7))
                                profiles_container = driver.find_element(By.XPATH, "(//ul[contains(@class,'list-style-none msg-conversations-container__conversations-list')])")

                                for j in range(1,4):
                                    for i in range(1,3):
                                        scroll_container_down(driver, profiles_container)
                                        print("scrolling")
                                        time.sleep(5)
                                    try:
                                        driver.find_element(By.XPATH, "//buttom[@class='block mlA mrA artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view']//span").click()
                                    except:
                                        break


                                
                            except:
                                logging.exception('msg')
                                if profile_clicked:
                                    driver.back()
                                    #driver.refresh()

                                    time.sleep(random.randint(4,7))
                                    profiles_container = driver.find_element(By.XPATH, "(//ul[contains(@class,'list-style-none msg-conversations-container__conversations-list')])")

                                    for j in range(1,4):
                                        for i in range(1,3):
                                            scroll_container_down(driver, profiles_container)
                                            print("scrolling")
                                            time.sleep(5)
                                        try:
                                            driver.find_element(By.XPATH, "//buttom[@class='block mlA mrA artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view']//span").click()
                                        except:
                                            break
                                continue
            except:
                if profile_clicked:
                    driver.back()
                    #driver.refresh()

                    time.sleep(random.randint(4,7))
                    profiles_container = driver.find_element(By.XPATH, "(//ul[contains(@class,'list-style-none msg-conversations-container__conversations-list')])")
                    for j in range(1,4):
                        for i in range(1,3):
                            scroll_container_down(driver, profiles_container)
                            print("scrolling")
                            time.sleep(5)
                        try:
                            driver.find_element(By.XPATH, "//buttom[@class='block mlA mrA artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view']//span").click()
                        except:
                            break
                logging.exception('msg')
                time.sleep(3)
                driver.quit()
                break
                    
       

        print("All processed")

    except:
        logging.exception("msg")
        pass
    


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

def scroll_up(driver):
    SCROLL_PAUSE_TIME = 1
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll up
        driver.execute_script("window.scrollTo(0, 0);")

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
        (?:                   # non-capturing group
            \(?               # open bracket (optional)
            \+?               # plus sign (optional)
            \d{1,4}?          # country code (1-4 digits, optional)
            \)?               # close bracket (optional)
            [\s.-]?           # separator (space, dot, or hyphen, optional)
        )?                    # entire group is optional
        \b                    # word boundary
        (                     # start capturing group for number
            \d{1,}            # digits (1 or more)
            (?:               # non-capturing group for separators and digits
                [\s.-]?       # separator (space, dot, or hyphen, optional)
                \d+           # one or more digits
            )+                # repeat the non-capturing group
        )                     # end capturing group
        \b                    # word boundary
    ''', re.VERBOSE)

    # Find all matches
    matches = pattern.findall(text)

    # Filter out numbers with fewer than 8 digits
    return [number for number in matches if len(re.sub(r'\D', '', number)) > 7]

def get_experience(driver):
    containers = driver.find_elements(By.XPATH, "//div[@class='pvs-header__container']")
    about = None
    experience = None
    education = None

    for c, container in enumerate(containers):
        heading = container.find_element(By.XPATH, ".//h2//span").text
        print(heading)
        if heading == "About":
            about = container.find_element(By.XPATH, ".//div[@class='pv-shared-text-with-see-more full-width t-14 t-normal t-black display-flex align-items-center']//div//span").text
            print(about)
        elif heading == "Experience":
            experience = []
            outer_container = driver.find_element(By.XPATH, f"(//div[@class='pvs-list__outer-container'])[{c+1}]")
            experience_containers = outer_container.find_elements(By.XPATH, ".//ul//li")
            print(len(experience_containers))
            for experience_container in experience_containers:
                name = experience_container.find_element(By.XPATH, ".//div[@class='display-flex flex-wrap align-items-center full-height']//div//div//div//span").text
                try:
                    duration = experience_container.find_element(By.XPATH, ".//span[@class='pvs-entity__caption-wrapper']").text
                except:
                    duration = ""
                try:
                    location = experience_container.find_element(By.XPATH, ".(//span[@class='t-14 t-normal t-black--light']//span)[2]").text
                except:
                    location = ""
                experience.append({"organization" : name, "duration" : duration, "location": location})
            print(experience)
        
        elif heading == "Education":
            education = []
            education_containers = container.find_elements(By.XPATH, ".//li[@class='artdeco-list__item zrBNestyLvBsyHsXIAhMSDoiZeTTKIZmL xyURnRxRrVaomfNsTwnJuGOUObqvUhnSMPoo']")
            for education_container in education_containers:
                name = education_container.find_element(By.XPATH, ".//div[@class='display-flex flex-wrap align-items-center full-height']//div//div//div//span").text
                try:
                    duration = education_container.find_element(By.XPATH, ".//span[@class='pvs-entity__caption-wrapper']").text
                except:
                    duration = ""
                try:
                    title = education_container.find_element(By.XPATH, ".//span[@class='t-14 t-normal']//span").text
                except:
                    title = ""
                education.append({"institue": name, "title" : title, "duration": duration})
            print(education)
    time.sleep(1000)
    
    return about, experience, education
            
                




def send_intro_message(driver, url, profile_name, connection_name):
    #driver.get(url)
    actions = ActionChains(driver)
    actions.move_to_element(connection_name)
    time.sleep(random.randint(3,5))
    actions.click().perform()
    wait = WebDriverWait(driver, 10)
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(@class,'text-heading-xlarge inline t-24 v-align-middle break-words')]")))


    name = driver.find_element(By.XPATH, "//h1[contains(@class,'text-heading-xlarge inline t-24 v-align-middle break-words')]").text
    #name = names[index]
    #name = driver.find_element(By.XPATH, "//div[@class='pv-text-details__left-panel']//div//h1[1]").text
    #print(name)
    #print(driver.find_element(By.XPATH, "//div[@class='text-body-medium break-words']").text)
    bio = driver.find_element(By.XPATH, "//div[@class='text-body-medium break-words']").text
    time.sleep(random.randint(4, 7))

    scroll_down(driver)
    #try:
     #   get_experience(driver)
    #except:
     #   logging.exception('msg')
      #  time.sleep(1000)
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
    #message_prompt = intro_prompt.replace("{recruiter_name}", profile_name).replace("{lead_name}", name.split(" ")[0]).replace("{experience}", experience).replace("{bio}", bio)
    #message = get_intro_message(name.split(" ")[0], experience, profile_name, message_prompt)
    #driver.back()
    #time.sleep(1.5)
    #driver.get(url)s
    scroll_up(driver)
    time.sleep(5)
    try:
        driver.find_element(By.XPATH, "(//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view')])").click()
        time.sleep(1.5)
    except:
        pass
    close_elements = driver.find_elements(By.XPATH, "(//button[contains(@class,'artdeco-modal__dismiss artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view')])")
    for element in close_elements:
        element.click()
        time.sleep(1)
    additional_close_buttons = driver.find_elements(By.XPATH, "//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--1 artdeco-button--primary ember-view') or contains(@class,'artdeco-modal__dismiss artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view')]")
    for button in additional_close_buttons:
        button.click()
        time.sleep(1)
    print("closed all messages")
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
    profile_messages = driver.find_elements(By.XPATH, "(//p[contains(@class,'msg-s-event-listitem__body t-14')])")
    conversation = ""
    for message in profile_messages:
        conversation = conversation +"[" + message.text + "]"
    #connect_message = get_connect_promt(name.split(" ")[0], experience, profile_name)
    message = get_intro_message(name.split(" ")[0], profile_name.split(" ")[0], conversation, experience, bio)
    time.sleep(2)
    close_elements = driver.find_elements(By.XPATH, "(//button[contains(@class,'artdeco-modal__dismiss artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view')])")
    for element in close_elements:
        element.click()
        time.sleep(1)
    
    additional_close_buttons = driver.find_elements(By.XPATH, "//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--1 artdeco-button--primary ember-view') or contains(@class,'artdeco-modal__dismiss artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view')]")
    for button in additional_close_buttons:
        button.click()
        time.sleep(1)
    print("closed all messages")
    buttons = driver.find_elements(By.XPATH, "(//button[contains(@class,'artdeco-button artdeco-button--2')]//span)")
            
    for button in buttons:
        print(button.text)
        if button.text == "Message":
            button.click()
            break
    
    wait.until(EC.visibility_of_element_located((By.XPATH, "(//div[contains(@class,'msg-form__contenteditable t-14 t-black--light t-normal flex-grow-1 full-height notranslate')])")))

    driver.find_element(By.XPATH, "(//div[contains(@class,'msg-form__contenteditable t-14 t-black--light t-normal flex-grow-1 full-height notranslate')])").send_keys(message)
    print(message)
    time.sleep(12)
    
    driver.find_element(By.XPATH, "(//button[contains(@class,'msg-form__send-button artdeco-button artdeco-button--1')])").click()
    time.sleep(6)
    driver.find_element(By.XPATH, "(//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view')])").click()
    time.sleep(7)
    driver.back()
    



def run():
    try:
        # close path "msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--1 artdeco-button--primary ember-view"
        linkedin_accounts = get_accounts()
        for linkedin_account in linkedin_accounts:
            account_id, profile_name, cookies, proxyip, proxyport, proxyuser, proxypass, account_status, restrict_view, capacity_limit = linkedin_account
            if account_id not in [1,2,5,6,8,11,13,53,65]:
        
                continue
            print(profile_name)
            driver = driverInit(proxyip, proxyport, proxyuser, proxypass)
            driver.get("http://www.whatsmyip.org/")
            time.sleep(3)
            wait = WebDriverWait(driver, 10)
            login_using_cookie_string(driver, cookies)
            get_phone_numbers_updated(driver, profile_name)
            driver.quit()
        print("Finished")
        #time.sleep(100000)
        campaigns = get_campaigns()
        # Count the number of active campaigns for today
        active_campaigns = sum(1 for campaign in campaigns if campaign[3] <= datetime.now(timezone.utc) <= campaign[4])
        
        
        # Calculate the time spent on all active campaigns in seconds (30 minutes each)
        total_active_time = active_campaigns * 40 * 60
        
        # Calculate sleep duration by subtracting total active time from 24 hours
        sleep_duration = 86400 - total_active_time
        print(sleep_duration)
        for campaign in campaigns:
            try:
                print(campaign)
                campaign_id, campaign_name, location, start_date, end_date, job_title, connects_sent, connect_accepted, account, daily_count, category, search_value, boolean_search, min_salary, max_salary, min_age, max_age, batch_size, profiles_count, status = campaign

                if campaign_id in [48, 81, 78]:
                    continue
                if category == 'lion': 
                    continue
                if campaign_id < 135:
                    continue
                if not connects_sent:
                    connects_sent = 0
                today_count = 0
            
                #while datetime.now(timezone.utc) < end_time:
                if daily_count:
                    if today_count == daily_count:
                        break
                print("in campaign")
                linkedin_account = get_account_by_id(account)
                account_id, profile_name, cookies, proxyip, proxyport, proxyuser, proxypass, account_status, restrict_view, capacity_limit = linkedin_account
                
                print(profile_name)
                job_title.replace(" ", "%20")

                #driver = driverInit()
                
                driver = driverInit(proxyip, proxyport, proxyuser, proxypass)
                driver.get("http://www.whatsmyip.org/")
                time.sleep(3)
                wait = WebDriverWait(driver, 10)
                login_using_cookie_string(driver, cookies)
                #get_phone_numbers_updated(driver, campaign_id, profile_name)
                time.sleep(4)
                driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
                scroll_down(driver)
                connect_urls = driver.find_elements(By.XPATH, "(//div[contains(@class,'mn-connection-card__details')]//a)")
                #connection_names = driver.find_elements(By.XPATH, "(//div[contains(@class,'mn-connection-card__details')]//a//span[2])")
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
                        index = connection_urls.index(profile_url)
                        scroll_down(driver)
                        connection_names = driver.find_elements(By.XPATH, "(//div[contains(@class,'mn-connection-card__details')]//a//span[2])")
                        if category != 'lion':
                            if "lion" not in campaign_name.lower():  
                                send_intro_message(driver, profile_url, profile_name, connection_names[index])
                        # Update the status field to "Accepted"
                        update_query = """UPDATE "CRM_profile" SET "status" = 'Accepted', "last_communication" = %s WHERE "link" = %s;"""
                        cursor.execute(update_query, (datetime.now(), profile_url))
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

                
                driver.quit()
            except:
                logging.exception('msg')
                continue
    except:
        logging.exception('msg')
        #continue

run()
#print(get_images())