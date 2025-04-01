import psycopg2
import time
import random
import json
import threading
import os
import string
import datetime
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
import re
from typing import Dict, List
import logging
import os
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


def get_account_by_id(user):
    cursor, conn = get_db()
    cursor.execute(
        """SELECT * FROM "CRM_linkedin_user" WHERE user_id_id = %s;""", (user,))
    row = cursor.fetchone()  
    conn.close()
    return row

def get_linkedin_account_by_id(user):
    cursor, conn = get_db()
    cursor.execute(
        """SELECT * FROM "CRM_linkedin_user" WHERE id = %s;""", (user,))
    row = cursor.fetchone()  
    conn.close()
    return row

def login_to_linkedin(driver, username, password):
    try:
        driver.get("https://www.linkedin.com/login")
        time.sleep(2)

        # Find the email input element
        email_element = driver.find_element(By.ID, "username")

        # Type the email letter by letter with a small delay
        for letter in username:
            email_element.send_keys(letter)
            # Adjust the delay to simulate typing speed
            time.sleep(random.uniform(0.1, 0.3))

        # Find the password input element
        password_element = driver.find_element(By.ID, "password")

        # Type the password letter by letter with a small delay
        for letter in password:
            password_element.send_keys(letter)
            # Adjust the delay to simulate typing speed
            time.sleep(random.uniform(0.1, 0.3))

        # Click the login button
        login_button = driver.find_element(
            By.XPATH, "//button[@type='submit']")
        login_button.click()

        # Wait for the main page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "main")))
    except Exception as e:
        print("An error occurred during login:", e)


def sanitize_filename(filename):
    # Replace any character that is not a letter, number, underscore, or hyphen with an underscore
    return re.sub(r'[^\w\-_\. ]', '_', filename)


def driverInit(proxy_host, proxy_port, proxy_user, proxy_pass):

    proxyauth_plugin_path = create_proxyauth_extension(
        proxy_host=proxy_host,
        proxy_port=proxy_port,
        proxy_username=proxy_user,
        proxy_password=proxy_pass,
        scheme='http',
        plugin_path=f"{os.getcwd()}/proxy_auth_plugin.zip"
    )

    co = Options()
    co.add_argument("--start-maximized")
    co.add_experimental_option("useAutomationExtension", False)
    co.add_experimental_option("excludeSwitches", ["enable-automation"])
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.notifications": 2
    }
    co.add_experimental_option("prefs", prefs)
    co.add_extension(proxyauth_plugin_path)

    driver = webdriver.Chrome(options=co)
    return driver


def open_chrome_browser( proxy_host, proxy_port, proxy_user, proxy_pass, cookies):
    print("DETAILS", proxy_host, proxy_pass, proxy_port, proxy_user)
    # chromedriver_autoinstaller.install()
    driver = driverInit(
        proxy_host, proxy_port, proxy_user, proxy_pass)

    # Set the new window position
    print("HEREEEE")
    driver.get("http://www.whatsmyip.org/")
    login_linkedin_using_cookies(
        driver, cookies)
    return driver


def login_using_cookie_string(driver: WebDriver, cookie_string: str) -> bool:
    """Restore auth cookies from a string. Does not guarantee that the user is logged in afterwards.
    Visits the domains specified in the cookies to set them, the previous page is not restored."""
    domain_cookies: Dict[str, List[object]] = {}
    cookies = json.loads(cookie_string)  # Parse the cookie string
    print("COOKIE 2nd Function")

    # Sort cookies by domain, because we need to visit to domain to add cookies
    for cookie in cookies:
        domain_cookies.setdefault(cookie["domain"], []).append(cookie)

    for domain, cookies in domain_cookies.items():
        driver.get(domain_to_url(domain + "/robots.txt"))
        for cookie in cookies:
            # Attribute should be available in Selenium >4
            cookie.pop("sameSite", None)
            cookie.pop("storeId", None)  # Firefox container attribute
            try:
                driver.add_cookie(cookie)
            except:
                print(f"Couldn't set cookie {cookie['name']} for {domain}")
    return True


def login_linkedin_using_cookies(driver, cookies):
    print("IN LOGIN USING COOKIES")
    login_using_cookie_string(driver, cookies)
    # Wait for the main page to load
    driver.get("https://www.linkedin.com/")
    # WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "main")))
    print("HERe")
    time.sleep(10)
    driver.get("https://www.linkedin.com/sales/index")
    time.sleep(10)
    # Click the sale nav button


def return_chrome_browser(proxy_host, proxy_port, proxy_user, proxy_pass, cookies):
    # global global_driver
    # chromedriver_autoinstaller.install()
    driver = driverInit(proxy_host, proxy_port, proxy_user, proxy_pass)

    driver.get("http://www.whatsmyip.org/")
    login_linkedin_using_cookies(
        driver, cookies)

    return driver


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


def domain_to_url(domain: str) -> str:
    if domain.startswith(".") and "www" not in domain:
        domain = "www" + domain
        return "https://" + domain
    elif "www" in domain and domain.startswith("."):
        domain = domain[1:]
        return "https://" + domain
    else:
        return "https://" + domain


def scroll_container_down(driver, container):
    SCROLL_PAUSE_TIME = 3
    SCROLL_FRACTION = 0.1

    # Get the initial scroll height of the container
    last_height = driver.execute_script(
        "return arguments[0].scrollHeight", container)

    while True:
        # Calculate the scroll amount based on the fraction of the total scroll height
        scroll_amount = driver.execute_script(
            "return arguments[0].scrollHeight * {0}".format(SCROLL_FRACTION), container)

        # Scroll down a small amount within the container
        driver.execute_script(
            "arguments[0].scrollTop += {0}".format(scroll_amount), container)

        # Wait a bit to load page after each small scroll
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with the last scroll height
        new_height = driver.execute_script(
            "return arguments[0].scrollHeight", container)
        if new_height == last_height or driver.execute_script("return arguments[0].scrollTop", container) + driver.execute_script("return arguments[0].clientHeight", container) >= new_height:
            # scroll_up(driver)
            break
        last_height = new_height


def click_element_with_actions(driver, name):
    print("clicking")

    actions = ActionChains(driver)
    actions.move_to_element(name)
    time.sleep(random.randint(4, 7))
    actions.click().perform()
    print("clicking performed")

def check_saved_search(id):
    cursor, conn = get_db()
    cursor.execute("""SELECT * FROM "CRM_savedsearch" WHERE id = %s;""", (id, ))

    row = cursor.fetchone()  # Assuming account IDs are unique, so you'd get at most one row
    conn.close()
    return row

def sales_navigator_search(global_driver, boolean_search, batch_size, saved_search, proxyip, proxyport, proxyuser, proxypass, cookies, min_page, max_page):
    # global global_driver
    # global stop_thread
    wait = WebDriverWait(global_driver, 10)
    stop_thread = False
    print(global_driver)
    print("IN SALES NAV")
    start_page_index = 1
    end_page_index = 100
    search_pages_index = end_page_index - start_page_index
    if search_pages_index == 0:
        search_pages_index = 1
    print(start_page_index)
    print(end_page_index)
    window_handles = global_driver.window_handles
    print(window_handles)

    # Switch to the new window (assuming it's the last one opened)

    time.sleep(random.randint(3, 6))

    global_driver.switch_to.window(window_handles[-1])

    time.sleep(random.randint(3, 6))
    # PAss the bool search value in search bar
    if boolean_search:

        search_bar = global_driver.find_element(By.ID, "global-typeahead-search-input")

        # Type the email letter by letter with a small delay
        for letter in boolean_search:
            search_bar.send_keys(letter)
            time.sleep(random.uniform(0.1, 0.3))

        search_button = global_driver.find_element(By.XPATH, "(//button[@class='artdeco-button artdeco-button--2 artdeco-button--primary ember-view global-typeahead__search-button-homepage mr1'])")
        search_button.click()
    if saved_search:
        search_objects = check_saved_search(saved_search)
        if search_objects:
            search_link = search_objects[1]
            global_driver.get(search_link)
            time.sleep(7)
    print("Search Link Opened")
    time.sleep(5)
    # global_driver.switch_to.new_window('tab')
    # scroll_down(global_driver)
    # scroll_up(global_driver)
    # scroll_down(global_driver)
    base_url = global_driver.current_url
    global_driver.quit()
    # global_driver.quit()
    parent_list = []
    for p in range(min_page, max_page  + 1):
        child_list = sales_nav_general_batch(global_driver, base_url, p, batch_size, len(parent_list), proxyip, proxyport, proxyuser, proxypass, cookies)
        parent_list.extend(child_list)
        print("parent list : ",len(parent_list))
        if len(parent_list) >= batch_size:
            break
    return parent_list


def sales_nav_general_batch(global_driver, base_url, page_index, batch_size, init_size, proxyip, proxyport, proxyuser, proxypass, cookies):
    # global proxies
    # global linkedin_account
    # global global_driver
    # global
    # global stop_thread
    user_details_list = []
    if cookies:
        global_driver = return_chrome_browser(
            proxyip, proxyport, proxyuser, proxypass, cookies)
        wait = WebDriverWait(global_driver, 30)
        base_url_list = base_url.split('?')
        if len(base_url_list) > 1:
            base_url_string = base_url_list[0] + "?page=" + \
                str(page_index) + "&" + base_url_list[1]
        global_driver.get(base_url_string)
        for p in range(1, 1):
            try:
                #global_driver.refresh()
                wait.until(EC.visibility_of_element_located(
                    (By.XPATH, "(//button[@class='artdeco-pagination__button artdeco-pagination__button--next artdeco-button artdeco-button--muted artdeco-button--icon-right artdeco-button--1 artdeco-button--tertiary ember-view'])")))
                time.sleep(2.5)
                # Locate the element
                next_button = global_driver.find_element(
                    By.XPATH, "(//button[@class='artdeco-pagination__button artdeco-pagination__button--next artdeco-button artdeco-button--muted artdeco-button--icon-right artdeco-button--1 artdeco-button--tertiary ember-view'])")

                # Scroll the element into view
                global_driver.execute_script(
                    "arguments[0].scrollIntoView(true);", next_button)

                time.sleep(2)  # Adjust sleep time as needed

                # Click the element
                next_button.click()

                # Wait for the next page to load, if necessary
                time.sleep(5)
            except Exception as e:
                logging.exception(
                    'An error occurred while trying to click the next button.')
                return
        #global_driver.refresh()
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "(//li[@class='artdeco-list__item pl3 pv3 '])")))
        time.sleep(4)
        total_links = global_driver.find_elements(
            By.XPATH, "(//li[@class='artdeco-list__item pl3 pv3 '])")
        print(len(total_links))
        wait.until(EC.visibility_of_element_located(
            (By.ID, "search-results-container")))

        container = global_driver.find_element(
            By.ID, "search-results-container")

        for i in range(1, 3):
            scroll_container_down(global_driver, container)
            time.sleep(4)

        try:
            for j in range(1, len(total_links)+1):
                if len(user_details_list) + init_size== batch_size:
                    if global_driver:
                        global_driver.quit()
                    return user_details_list
                try:
                    print("LIST LENGTHHHH", len(user_details_list))
                    profile_element = global_driver.find_element(
                        By.XPATH, f"(//div[@class='artdeco-entity-lockup__title ember-view']//a)[{j}]")
                    # print("CONTAINER FOUND")
                    name = profile_element.find_element(By.XPATH, ".//span")
                    name = name.text.split("\n")[0]
                    print("NAME>>>>>>>>", name)
                    # continue

                    click_element_with_actions(global_driver, profile_element)
                    time.sleep(2)
                    #profile_name_element = global_driver.find_element(By.XPATH, "//div[@class='MklcKUKPKuJKYnwhljcZKIdAHLXDMVbNuok']//h1//a")
                    profile_name_element = global_driver.find_element(By.XPATH, "//a[@class='ember-view _lead-page-link_sqh8tm']")
                    click_element_with_actions(global_driver, profile_name_element)
                    try:
                        wait.until(EC.visibility_of_element_located(
                            (By.XPATH, "//button[@class='ember-view _button_ps32ck _small_ps32ck _tertiary_ps32ck _circle_ps32ck _container_iq15dg _overflow-menu--trigger_1xow7n']")))
                        global_driver.find_element(
                            By.XPATH, "//button[@class='ember-view _button_ps32ck _small_ps32ck _tertiary_ps32ck _circle_ps32ck _container_iq15dg _overflow-menu--trigger_1xow7n']").click()
                        wait.until(EC.visibility_of_element_located(
                            (By.XPATH, "(//div[@class='_container_x5gf48 _visible_x5gf48 _container_iq15dg _raised_1aegh9']//ul//li)[3]")))

                        #global_driver.find_element(
                        #    By.XPATH, "(//div[@class='_container_x5gf48 _visible_x5gf48 _container_iq15dg _raised_1aegh9']//ul//li)[3]").click()
                        # Assuming global_driver is your Selenium WebDriver
                        options = global_driver.find_elements(
                            By.XPATH, "//div[@class='_container_x5gf48 _visible_x5gf48 _container_iq15dg _raised_1aegh9']//ul//li")

                        for option in options:
                            if option.text == "View LinkedIn profile":
                                option.click()
                                break
                        time.sleep(4)
                        # Get all the window handles
                        window_handles = global_driver.window_handles

                        # Check if there are at least two tabs
                        if len(window_handles) >= 2:
                            # Switch to the 2nd tab (which is at index 2 since indexing starts at 0)
                            global_driver.switch_to.window(window_handles[1])
                        else:
                            print("There are less than two tabs open.")
                        profile = global_driver.current_url
                        try:
                            wait.until(EC.visibility_of_element_located(
                                (By.XPATH, "(//span[contains(@class,'text-body-small inline t-black--light break-words')])")))

                            location = global_driver.find_element(
                                By.XPATH, "(//span[contains(@class,'text-body-small inline t-black--light break-words')])").text
                            headline = global_driver.find_element(
                                By.XPATH, "//div[@class='text-body-medium break-words']").text
                        except:
                            global_driver.close()
                            time.sleep(1)
                            window_handles = global_driver.window_handles
                            global_driver.switch_to.window(window_handles[0])
                            continue
                        global_driver.close()
                        time.sleep(1)
                        window_handles = global_driver.window_handles
                        global_driver.switch_to.window(window_handles[0])

                        print("INDEX", j)
                        print("PROFILE LINK", profile)
                        print("NAME", name)
                        print("Headline : ", headline)
                        print("Location : ", location)
                        parts = name.split(maxsplit=1)
                        first_name = parts[0]
                        last_name = parts[1] if len(parts) > 1 else ""
                        user_details = [profile, first_name, last_name, '', '', '', '', headline, location]
                        user_details_list.append(user_details)
                    except:
                        logging.exception('msg')
                        pass
                    global_driver.back()
                    time.sleep(2)
                    global_driver.refresh()
                    time.sleep(20)
                    # wait.until(EC.visibility_of_element_located((By.XPATH, f"(//div[@class='artdeco-entity-lockup__title ember-view']//a)[{j}]")))
                    wait.until(EC.visibility_of_element_located(
                        (By.ID, "search-results-container")))

                    container = global_driver.find_element(
                        By.ID, "search-results-container")

                    for i in range(1, 3):
                        scroll_container_down(global_driver, container)
                        time.sleep(4)
                except:
                    logging.exception("msg")
                    wait.until(EC.visibility_of_element_located(
                        (By.ID, "search-results-container")))
                    container = global_driver.find_element(
                        By.ID, "search-results-container")
                    for i in range(1, 3):
                        scroll_container_down(global_driver, container)
                        time.sleep(4)
                    continue

                # print(f"Profile {j}: {profile.text}")

        except Exception as e:
            print(f"An error occurred during search: {e}")
            if global_driver:
                global_driver.quit()
            return user_details_list
    if global_driver:
        global_driver.quit()
    return user_details_list

def get_users():

    cursor, conn = get_db()
    cursor.execute(
        """SELECT * FROM "CRM_account" WHERE name = %s;""", ("Amelia Hartwell",))
    rows = cursor.fetchone()
    conn.close()
    return rows

def get_campaigns():
    print("HERE")
    current_date = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    print(current_date)

    # Connecting to the database
    cursor, conn = get_db()

    # Modify the query to exclude campaigns with status 'Finished'
    query = """SELECT * FROM "CRM_campaign" 
               WHERE "autoscrapper" = 'true' 
               AND "start_date" <= %s 
               AND "end_date" >= %s
               AND "status" <> 'Finished';"""  

    # Executing the query
    cursor.execute(query, (current_date, current_date))
    rows = cursor.fetchall()
    print(rows)

    for row in rows:
        campaign_id = row[0]
        print(campaign_id)
        if campaign_id != 211 and campaign_id != 212:
            continue
        campaign_name = row[1]
        print(campaign_name)
        boolean_search = row[12]
        batch_size = row[17]
        saved_search=row[37]
        max_page = row[38]
        min_page = row[39]
        print(min_page, max_page)
        print(batch_size)
        #batch_size = 5
        print("RESULT CAMPAIGN FOR BOOL SEARCH", boolean_search, ">>>", batch_size)
        saved_search_results = check_saved_search(saved_search)
        if saved_search_results:
            linkedin_user = saved_search_results[3]
            linkedin_account = get_linkedin_account_by_id(linkedin_user)
            if linkedin_account:
                user = linkedin_account[3]
                cookies = linkedin_account[4]
                proxies = get_proxy_by_id(user)
                proxyip = proxies[1]
                proxyport = proxies[2]
                proxyuser = proxies[3]
                proxypass = proxies[4]
                print(proxyip, proxyport, proxyuser, proxypass)
        
                # Initializing the web driver for the search
                driver = open_chrome_browser(proxyip, proxyport, proxyuser, proxypass, cookies)
                
                # Executing the search with the given parameters
                output = sales_navigator_search(driver, boolean_search, batch_size, saved_search, proxyip, proxyport, proxyuser, proxypass, cookies, min_page, max_page)
                print(output)

                # Save the output to the database
                save_users_to_db(campaign_id, output, campaign_name)

                # Update the campaign status to 'Finished'
                update_query = """UPDATE "CRM_campaign" SET "status" = 'Finished' WHERE "id" = %s;"""
                cursor.execute(update_query, (campaign_id,))
                conn.commit()  # Commit the changes to the database

    conn.close()

def get_proxy_by_id(user):
    cursor, conn = get_db()
    cursor.execute(
        """SELECT * FROM "CRM_scrapperproxy" WHERE user_id_id = %s;""", (user,))
    row = cursor.fetchone()  # Assuming account IDs are unique, so you'd get at most one row
    conn.close()
    return row

def format_user_data_to_json(user_data):
    # Map the user data to the new format
    formatted_data = {
        "urls": [user[0].replace('"', "").replace("'", "") for user in user_data],
        "names": [f"{user[1].replace('"', "").replace("'", "")} {user[2].replace('"', "").replace("'", "")}" for user in user_data],
        "profile_location": [user[8].replace('"', "").replace("'", "") for user in user_data],
        "jobtitle": [user[7].replace('"', "").replace("'", "") for user in user_data]
    }
    # Convert the mapped data to JSON format
    json_data = json.dumps(formatted_data)
    # Manually escape the resulting JSON string
    escaped_json_string = json_data.replace('"', '\\"')
    return '"' + escaped_json_string + '"'

def save_users_to_db(campaign_id, user_details_list, campaign_name):
    # Generate the formatted JSON data
    user_json = format_user_data_to_json(user_details_list)
    print(type(user_json))

    # Assuming get_db() is defined elsewhere and connects to your database
    cursor, conn = get_db()
    filename = str(campaign_name) + " - Leads"
    
    query = """INSERT INTO "CRM_excel_file" ("name", "json_data", "duplicate", "created_at") VALUES (%s, %s, %s, %s);"""
    try:
        # Add the current UTC time as the fourth parameter
        current_utc_time = datetime.datetime.utcnow()
        cursor.execute(query, (filename, user_json, True, current_utc_time))
        conn.commit()
        print("DATA SAVED TO JSON SUCCESSFULLY")
    except Exception as e:
        logging.exception('Error when saving to database')
    finally:
        conn.close()



# Main functions execution 
#user = get_users()
# print("USER DETAILS", user)
#id, name, cookies, proxyip, proxyport, proxyuser, proxypass, status, restrict_view, capacity_limit = user
get_campaigns()
#test_data = [['https://www.linkedin.com/in/anilchityal3435/', 'Anil', 'Chityal {LION}', '', '', '', '', 'Account Manager @ Wipro ENU | CIS', 'Austin, Texas, United States'], ['https://www.linkedin.com/in/kevin-parrish-5b21a247/', 'Kevin', 'Parrish', '', '', '', '', 'Unemployed Injured Combat Veteran, looking for Secret Clearance Federal Job to Retirement', 'Tacoma, Washington, United States'], ['https://www.linkedin.com/in/jerisessler/', 'Jeri', 'Sessler', '', '', '', '', 'LION Dancing with ambiguity is my superpower. I excel at leading incredibly complex, high risk/high stakes programs, like healthcare operations and turnarounds, complicated contract negotiations. I love puzzles.', 'Greater Phoenix Area'], ['https://www.linkedin.com/in/jmarletto/', 'Janet', 'Marletto', '', '', '', '', '* PRIVATE MONEY BROKER * Manager at REAL DEAL 8, LLC.', 'Colorado Springs, Colorado, United States'], ['https://www.linkedin.com/in/patrick-hickey-423a6017/', 'Patrick', 'Hickey', '', '', '', '', 'Chief Operating Officer - Lion One Metals Ltd', 'Golden, Colorado, United States']]
#save_users_to_db(1, test_data, "auto scrapping test")