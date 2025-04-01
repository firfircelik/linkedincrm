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
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
import concurrent.futures

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
        WHERE "boolean_search" IS NULL and "account_id" IS NOT NULL;
    """)

    # Fetch all rows from the executed query
    rows = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Return the retrieved rows
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
        time.sleep(random.randint(3,6))

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



def send_keys_word_by_word(driver, input_element, text, delay=0.1):  # Reduced default delay
    print("inside function")
    input_element.clear()  # Clear the input field before sending new text
    
    temp_text = ""  # Initialize a variable to temporarily hold characters
    for char in text:
        # Accumulate BMP characters to send them together
        temp_text += char

        # Check if character is outside the BMP and temp_text is not empty
        if ord(char) > 0xFFFF and temp_text:
            # Send accumulated BMP characters if any
            input_element.send_keys(temp_text[:-1])  # Exclude the non-BMP character
            temp_text = char  # Reset temp_text to only contain the non-BMP character
            
            # Use JavaScript for the non-BMP character
            script = "arguments[0].value += arguments[1];"
            driver.execute_script(script, input_element, char)
            temp_text = ""  # Reset accumulator after sending non-BMP character

    # Send any remaining BMP characters
    if temp_text:
        input_element.send_keys(temp_text)

    # Press ENTER at the end (consider if necessary)
    input_element.send_keys(Keys.ENTER)
    time.sleep(0.1)  # Short delay between ENTER presses for reliability



def send_keys_all(driver, input_element, text, delay=0.5):
    time.sleep(1.5)

    # Clear the input field before sending new text
    input_element.clear()
    input_element.send_keys(input_element)

   
    
    input_element.send_keys(Keys.ENTER)
    time.sleep(3)  # Short delay between ENTER presses for reliability


def click_element_with_actions(driver, name):
    print("clicking")
   
    actions = ActionChains(driver)
    actions.move_to_element(name)
    time.sleep(random.randint(4,7))
    actions.click().perform()
    print("clicking performed")


def check_url_existence(url, campaign_id=None, campaign_name=None):
    """
    Check if a URL exists in the CRM_profile table.
    If campaign_name contains 'lion', check against both url and url+"/" with a specific campaign_id.
    Otherwise, check against both url and url+"/" without considering the campaign_id.
    """
    cursor, conn = get_db()  # Assuming get_db() is a function that returns cursor and connection objects
    
    if campaign_name and "lion" in campaign_name.lower():
        # Check for both url and url+"/" against a specific campaign_id
        check_query = """SELECT COUNT(*) FROM "CRM_profile" 
                         WHERE ("link" = %s OR "link" = %s) 
                         AND "campaign_id" = %s;"""
        cursor.execute(check_query, (url, url + "/", campaign_id))
    else:
        # Check for both url and url+"/" without a campaign_id
        check_query = """SELECT COUNT(*) FROM "CRM_profile" 
                         WHERE "link" = %s OR "link" = %s;"""
        cursor.execute(check_query, (url, url + "/"))

    exists = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return exists > 0

def check_url_existence_v1(url, campaign_id=None, campaign_name=None):
    """
    Check if a URL exists in the CRM_profile table where status is not 'Excluded'.
    If campaign_name contains 'lion', check against both url and url+"/" with a specific campaign_id.
    Otherwise, check against both url and url+"/" without considering the campaign_id.
    """
    cursor, conn = get_db()  # Assuming get_db() is a function that returns cursor and connection objects
    
    if campaign_name and "lion" in campaign_name.lower():
        # Check for both url and url+"/" against a specific campaign_id where status is not 'Excluded'
        check_query = """SELECT COUNT(*) FROM "CRM_profile" 
                         WHERE ("link" = %s OR "link" = %s)
                         AND "campaign_id" = %s
                         AND "status" != 'Excluded';"""
        cursor.execute(check_query, (url, url + "/", campaign_id))
    else:
        # Check for both url and url+"/" without a campaign_id where status is not 'Excluded'
        check_query = """SELECT COUNT(*) FROM "CRM_profile" 
                         WHERE ("link" = %s OR "link" = %s)
                         AND "status" != 'Excluded';"""
        cursor.execute(check_query, (url, url + "/"))

    exists = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return exists > 0



def clean_string_v2(s: str) -> str:
    import re
    # Remove BMP characters, symbols including | (assuming symbols mean non-alphanumeric and non-space characters)
    cleaned = re.sub(r'[^a-zA-Z0-9\s]+', ' ', s)
    # Remove acronyms of minimum length two
    cleaned = re.sub(r'\b[A-Z]{2,}\b', ' ', cleaned)
    # Replace multiple spaces with a single space
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def campaign_processing(campaign):
    print("in campaign")

    try:
        driver =None
        campaign_id, campaign_name, location, start_date, end_date, job_title, connects_sent, connect_accepted, account, daily_count, category, search_value, boolean_search, min_salary, max_salary, min_age, max_age, batch_size, profiles_count, status = campaign
        print(campaign_name)
        if campaign_id in [48, 81, 78, 87, 96]:
            return
      

        if category == "lion":
            return
            
                
        else:
            #if account == 6:
            if not connects_sent:
                connects_sent = 0
            today_count = 0
            if start_date <= datetime.now(timezone.utc) <= end_date:
                end_time = datetime.now(timezone.utc) + timedelta(minutes=240) 
                #while datetime.now(timezone.utc) < end_time:
                print("in campaign")
                linkedin_account = get_account_by_id(account)
                account_id, profile_name, cookies, proxyip, proxyport, proxyuser, proxypass, status, restrict_view, capacity_limit = linkedin_account
                cursor, conn = get_db()
                update_query = """UPDATE "CRM_account" SET "status" = %s WHERE "id" = %s;"""
                cursor.execute(update_query, ("In Progress", account_id))
                conn.commit()
                conn.close()
                job_title.replace(" ", "%20")

                #driver = driverInit()
                cursor, conn = get_db()
                select_query = """SELECT * FROM "CRM_excel_file" WHERE "campaign_id" = %s LIMIT 1;"""
                cursor.execute(select_query, (campaign_id,))
                excel_file = cursor.fetchone()
                conn.commit()
                conn.close()
                account_opened = True
                driver_opened = False
                while account_opened:
                    try:
                        driver = driverInit(proxyip, proxyport, proxyuser, proxypass)
                        driver.get("http://www.whatsmyip.org/")
                        time.sleep(3)
                        driver_opened = True
                        wait = WebDriverWait(driver, 50)
                        login_using_cookie_string(driver, cookies)
                        driver.get("https://www.linkedin.com/")
                        account_opened = False
                    except:
                        logging.exception('msg')
                        time.sleep(4)
                        if driver_opened:
                            driver.quit()
                            time.sleep(2)
                        return

                

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
                    names = data_dict.get("names", [])
                    company = data_dict.get("company", [])
                    profile_location = data_dict.get("profile_location", [])
                    jobtitle = data_dict.get("jobtitle", [])

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
                    while True:
                        if daily_count:
                            if today_count == daily_count:
                                break
                        time.sleep(random.randint(3,7))
                        total_links = driver.find_elements(By.XPATH, "(//a[@class='app-aware-link '])")

                        for j in range(1,len(total_links) + 1):
                            try:
                                profile = driver.find_element(By.XPATH, "(//a[@class='app-aware-link '])[" + str(j) + "]")
                                profile_url = profile.get_attribute('href')
                                if is_profile_url(profile_url):

                                    name = profile.find_element(By.XPATH, ".//span")
                                
                                    profile_url = profile_url.split("?")[0] 
                                    names.append(name)
                                    urls.append(profile_url)
                                
                            except:
                                return
                        if profile_opened:
                            time.sleep(random.randint(3, 7))
                            break
                        time.sleep(random.randint(3, 7))
                        try:
                            driver.find_element(By.XPATH, "(//button[@class='artdeco-pagination__button artdeco-pagination__button--next artdeco-button artdeco-button--muted artdeco-button--icon-right artdeco-button--1 artdeco-button--tertiary ember-view'])").click()
                        except:
                            logging.exception('msg')
                            break
                    
                    
                people_clicked = False
                for index, url in enumerate(urls):
                    print(url)
                    #if datetime.now(timezone.utc) > end_time:
                        #   break
                    if daily_count:
                        if today_count == daily_count:
                            break
                        
                    #url = "https://www.linkedin.com/in/clara-santos-7024aa8"
                    #url = "https://www.linkedin.com/in/clara-ssantos"
                    # Check if URL already exists in the CRM_profile
                    # Get connection and cursor
                        print(campaign_name.lower())
                    exists = check_url_existence_v1(url, campaign_id, campaign_name)

                    
                    if exists:
                        continue
                    try:
                        print("processing profile")
                        
                        lead_name = names[index].replace("nan", "")
                        search_string = lead_name
                        search_string_v2 = lead_name
                        search_string_v3 = lead_name
                        search_string_v4 = lead_name



                        
                                

                        #if index < len(profile_location):
                        #   if profile_location[index] and str(profile_location[index])!="nan" and not search_profile_filter:
                        #        search_string = search_string + " " + str(profile_location[index])
                        #        if str(profile_location[index]) != "" and not None:
                        #            search_profile_filter = True

                        if index < len(jobtitle):
                            if jobtitle[index] and str(jobtitle[index])!="nan":
                                search_string = search_string + " " + str(jobtitle[index])
                                search_string_v2 = search_string_v2 + " " + clean_string_v2(str(jobtitle[index]))
                                search_string_v3 = search_string_v3 + " " + ' '.join(str(jobtitle[index]).split()[:2])
                                search_string_v4 = search_string_v4 + " " + ' '.join(clean_string_v2(str(jobtitle[index])).split()[:2])


                        search_string = search_string.replace("nan", "")
                        search_string_v2 = search_string_v2.replace("nan", "")
                        search_array = [search_string, search_string_v2, search_string_v3, search_string_v4]
                        for s, search in enumerate(search_array):
                            try:
                                wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "search-global-typeahead__input")))
                            except:
                                break
                            time.sleep(3)
                            search_element = driver.find_element(By.CLASS_NAME, "search-global-typeahead__input")
                            send_keys_word_by_word(driver, search_element, search)


                            wait.until(EC.visibility_of_element_located((By.XPATH, "(//li[contains(@class,'search-reusables__primary-filter')]//button)")))
                            time.sleep(random.randint(2,5))
                            if not people_clicked:
                                filter_buttons = driver.find_elements(By.XPATH, "(//li[contains(@class,'search-reusables__primary-filter')]//button)")
                                print(len(filter_buttons))
                                if len(filter_buttons) == 10:
                                    for filter_button in filter_buttons:
                                        print(filter_button.text)
                                        if filter_button.text == "People":
                                            filter_button.click()
                                            break
                            profile_opened = False
                            time.sleep(5)
                            #driver.find_element(By.ID, "searchFilter_currentCompany").click()
                            #time.sleep(1.5)
                            #company_search = driver.find_element(By.XPATH, "(//div[@class='search-basic-typeahead search-vertical-typeahead']//input)[2]")
                            #send_keys_word_by_word_no_enter(driver, company_search, company[index])
                            #time.sleep(random.randint(3,6))
                            #driver.find_element(By.XPATH, "//span[contains(@class,'search-typeahead-v2__hit-text t-14')]").click()
                            #time.sleep(random.randint(3,6))
                            #driver.find_element(By.XPATH, "(//button[contains(@class,'artdeco-button artdeco-button--2')]//span)[3]").click()

                            pattern = r'https://www\.linkedin\.com/in/[\w\.-]+'
                            

                            def is_profile_url(url):
                                return bool(re.match(pattern, url))
                            while True:
                                time.sleep(random.randint(4,7))
                                scroll_down(driver)

                                total_links = driver.find_elements(By.XPATH, "(//a[@class='app-aware-link '])")
                                scroll_up(driver)
                                for j in range(1,len(total_links) + 1):
                                    try:
                                        profile = driver.find_element(By.XPATH, "(//a[@class='app-aware-link '])[" + str(j) + "]")
                                        profile_url = profile.get_attribute('href')
                                        if is_profile_url(profile_url):

                                            name = profile.find_element(By.XPATH, ".//span")
                                        
                                            profile_url = profile_url.split("?")[0] 
                                            print(name.text.split("\n")[0])
                                            print(profile_url)
                                            if profile_url == url:
                                                click_element_with_actions(driver, name)
                                                time.sleep(random.randint(2,5))
                                                profile_opened = True
                                                break
                                            if profile_url + "/" == url:
                                                click_element_with_actions(driver, name)
                                                time.sleep(random.randint(2,5))
                                                profile_opened = True
                                                break


                                        
                                    except:
                                        continue
                                print(profile_opened)
                                if profile_opened:
                                    time.sleep(random.randint(3, 7))
                                    break
                                time.sleep(random.randint(3, 7))
                                if not profile_opened:
                                    try:
                                        driver.find_element(By.XPATH, "(//button[@class='artdeco-pagination__button artdeco-pagination__button--next artdeco-button artdeco-button--muted artdeco-button--icon-right artdeco-button--1 artdeco-button--tertiary ember-view'])").click()
                                    except:
                                        logging.exception('msg')
                                        break
                            #get_into_message(name.split(" ")[0], experience, profile_name)
                            cursor, conn = get_db()

                            if profile_opened:
                                try:
                                    print("Inside profile")
                                    sent_flag = False
                                    time.sleep(random.randint(3, 7))
                                
                                    buttons = driver.find_elements(By.XPATH, "(//button[contains(@class,'artdeco-dropdown__trigger artdeco-dropdown__trigger--placement-bottom')]//span)")
                                    
                                    for button in buttons:
                                        print(button.text)
                                        if button.text == "More":
                                            button.click()
                                            dropdown_elements = driver.find_elements(By.XPATH, "(//span[contains(@class,'display-flex t-normal flex-1')])")
                                            for d, element in enumerate(dropdown_elements):
                                                if element.text == "Connect":
                                                    element.click()
                                                    sent_flag = True
                                                    break
                                            break

                                    if not sent_flag:
                                        for button in buttons:
                                            print(button.text)
                                            if button.text == "Connect":
                                                button.click()
                                                sent_flag == True
                                                break
                                    
                                    if not sent_flag:

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
                                            print("Didn't make a click")
                                            continue
                                    
                                    try:
                                        driver.find_element(By.XPATH, "(//span[@class='artdeco-button__text'])[3]").click()
                                    except:
                                        pass
                                    time.sleep(random.randint(4,7))
                                    print('Adding Profile')
                                    current_url = driver.current_url
                                    # Check if the same URL exists for this campaign ID
                                    check_query = """
                                    SELECT "status" FROM "CRM_profile" 
                                    WHERE "campaign_id" = %s AND "link" = %s;
                                    """
                                    cursor.execute(check_query, (campaign_id, url))
                                    result = cursor.fetchone()

                                    if result:
                                        # If the URL exists for this campaign, update its status
                                        update_query = """
                                        UPDATE "CRM_profile" 
                                        SET "status" = %s, "name" = %s 
                                        WHERE "campaign_id" = %s AND "link" = %s;
                                        """
                                        cursor.execute(update_query, ('Sent', lead_name, campaign_id, url))
                                        print("Profile status updated to 'Sent'.")
                                    else:
                                        # If the URL does not exist for this campaign, insert a new record
                                        insert_query = """
                                        INSERT INTO "CRM_profile" ("campaign_id", "name", "status", "link")
                                        VALUES (%s, %s, %s, %s);
                                        """
                                        cursor.execute(insert_query, (campaign_id, lead_name, 'Sent', url))
                                        print("Profile added.")

                                    # Commit the transaction
                                    conn.commit()
                                    conn.close()
                                    people_clicked = False
                                    connects_sent = connects_sent + 1
                                    today_count = today_count + 1
                                    break
                                except:
                                    if s != 3:
                                        continue
                                    check_query = """
                                    SELECT "status" FROM "CRM_profile" 
                                    WHERE "campaign_id" = %s AND "link" = %s;
                                    """
                                    cursor.execute(check_query, (campaign_id, url))
                                    result = cursor.fetchone()
                                    if not result:
                                        query = """
                                        INSERT INTO "CRM_profile" ("campaign_id", "name", "status", "link")
                                        VALUES (%s, %s, %s, %s);
                                        """

                                        # Prepare the data
                                        data = (campaign_id, lead_name, 'Excluded', url)
                                        # Execute the query
                                        cursor.execute(query, data)
                                    


                                        # Commit the transaction
                                        conn.commit()
                                        conn.close()
                                        print("Profile excluded")
                                    people_clicked = False
                                    pass
                            else:
                                if s != 3:
                                    continue
                                check_query = """
                                SELECT "status" FROM "CRM_profile" 
                                WHERE "campaign_id" = %s AND "link" = %s;
                                """
                                cursor.execute(check_query, (campaign_id, url))
                                result = cursor.fetchone()
                                if not result:
                                    query = """
                                    INSERT INTO "CRM_profile" ("campaign_id", "name", "status", "link")
                                    VALUES (%s, %s, %s, %s);
                                    """

                                    # Prepare the data
                                    data = (campaign_id, lead_name, 'Excluded', url)
                                    # Execute the query
                                    cursor.execute(query, data)
                                


                                    # Commit the transaction
                                    conn.commit()
                                    conn.close()
                                    print("Profile excluded")
                                people_clicked = True


                    except:
                        cursor, conn = get_db()
                        update_query = """UPDATE "CRM_account" SET "status" = %s WHERE "id" = %s;"""
                        cursor.execute(update_query, ("Paused", account_id))
                        conn.commit()
                        conn.close()
                        logging.exception('msg')
                        #time.sleep(1000)
                        continue
                cursor, conn = get_db()
                update_query = """UPDATE "CRM_account" SET "status" = %s WHERE "id" = %s;"""
                cursor.execute(update_query, ("Paused", account_id))
                conn.commit()
                conn.close()
                driver.quit()

    except:
        logging.exception('msg')
        print('sleeping')
        if driver:
            driver.quit()
        return



def run():
    while True:
        try:
            campaigns = get_campaigns()  # Make sure this function fetches the campaigns
        except Exception as e:
            print(f"Error fetching campaigns: {e}")
            continue

        # Count the number of active campaigns for today
        active_campaigns = sum(1 for campaign in campaigns if campaign[3] <= datetime.now(timezone.utc) <= campaign[4])
        print(active_campaigns)

        # Calculate the time spent on all active campaigns in seconds (40 minutes each)
        total_active_time = active_campaigns * 40 * 60

        # Calculate sleep duration by subtracting total active time from 24 hours
        sleep_duration = 86400 - total_active_time

        # Process campaigns, 5 at a time
        with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
            executor.map(campaign_processing, campaigns)

        print("All Processed")
        # Sleep for the calculated duration
        print(f"Sleeping for {sleep_duration} seconds")
        time.sleep(sleep_duration)

run()
