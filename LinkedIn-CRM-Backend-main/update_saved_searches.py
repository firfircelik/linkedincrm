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
       
def check_saved_search(link, linkedin_user):
    cursor, conn = get_db()
    cursor.execute("""SELECT * FROM "CRM_savedsearch" WHERE link = %s AND linkedinuser_id = %s;""", (link, linkedin_user))

    row = cursor.fetchone()  # Assuming account IDs are unique, so you'd get at most one row
    conn.close()
    return row

def get_proxy_by_id(user):
    cursor, conn = get_db()
    cursor.execute("""SELECT * FROM "CRM_scrapperproxy" WHERE user_id_id = %s;""", (user,))
    row = cursor.fetchone()  # Assuming account IDs are unique, so you'd get at most one row
    conn.close()
    return row

def get_linkedin_accounts():
    

    cursor, conn = get_db()
    cursor.execute("""SELECT * FROM "CRM_linkedin_user";""")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_saved_search(linkedin_account, name, link):
    cursor, conn = get_db()
    insert_query = """
    INSERT INTO "CRM_savedsearch" ("linkedinuser_id", "name", "link")
    VALUES (%s, %s, %s);
    """

    cursor.execute(insert_query, (linkedin_account, name, link))
    print("Saved Search added.")
    # Commit the transaction
    conn.commit()
    conn.close()


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

def create_proxyauth_extension(proxy_host, proxy_port, proxy_username, proxy_password, scheme='http', plugin_path=None):
    # Check if the file exists and delete it
    if plugin_path is None or os.path.exists(plugin_path):
        plugin_path = 'proxy_auth_plugin.zip'
        if os.path.exists(plugin_path):
            os.remove(plugin_path)
    
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


def driverInit(proxy_host, proxy_port, proxy_user, proxy_pass):
    proxyauth_plugin_path = create_proxyauth_extension(
        proxy_host=proxy_host,
        proxy_port=proxy_port,
        proxy_username=proxy_user,
        proxy_password=proxy_pass,
        scheme='http',
        plugin_path=f"{os.getcwd()}/proxy_auth_plugin.zip"
    )
  
    co = webdriver.ChromeOptions()

    #co.add_argument("--force-device-scale-factor=0.6")
    co.add_experimental_option("useAutomationExtension", False)
    co.add_experimental_option("excludeSwitches", ["enable-automation"])
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.notifications": 2
    }
    co.add_experimental_option("prefs", prefs)
    co.add_extension(proxyauth_plugin_path)

    time.sleep(1)
    driver = webdriver.Chrome(options=co)

    driver.maximize_window()
    return driver

def get_saved_searches(cookies, user, linkedin_account):
    proxies = get_proxy_by_id(user)
    if proxies:
        driver = driverInit(proxies[1], proxies[2], proxies[3], proxies[4])
        login_using_cookie_string(driver, cookies)
        driver.get("http://www.whatsmyip.org/")
        # Wait for the main page to load
        
        driver.get("https://www.linkedin.com/sales/index")
        time.sleep(20)
        try:
            driver.find_element(By.XPATH, "//button[@class='artdeco-button artdeco-button--1 artdeco-button--tertiary ember-view global-typeahead-container__link']").click()
            time.sleep(4)
            lines = driver.find_elements(By.XPATH, "//a[@class='ember-view mrA t-16 nowrap-ellipsis _panel-link_yma0zx']")
            print(lines)
            for line in lines:
                name = line.text
                link = line.get_attribute("href")
                if name and link:
                    saved_search = check_saved_search(link, linkedin_account)
                    if not saved_search:
                        add_saved_search(linkedin_account, name, link)
                    else:
                        print("Already added")
                        




            driver.quit()
            
        except:
            logging.exception('msg')
            driver.quit()








def update_searches():
    try:
        # close path "msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--1 artdeco-button--primary ember-view"
        linkedin_accounts = get_linkedin_accounts()
        for linkedin_account in linkedin_accounts:
            linkedin_user_id, email, password,user_id, cookies = linkedin_account
            if user_id and cookies:
                if user_id> 3:
                    print(email)
                    get_saved_searches(cookies, user_id, linkedin_user_id)
            


        print("Finished")
        
    except:
        logging.exception('msg')
        #continue

update_searches()
