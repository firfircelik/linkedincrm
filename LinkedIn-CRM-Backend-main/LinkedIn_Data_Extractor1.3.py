import tkinter as tk
from tkinter import ttk
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import threading
import time
import re
import undetected_chromedriver as uc

import csv
import random
import logging
from selenium.common.exceptions import SessionNotCreatedException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
import psycopg2
from user_authentication import authenticate_user
import threading
from tkinter import filedialog
from datetime import datetime
from selenium.webdriver import ActionChains
import os, zipfile, string
import json
from selenium.webdriver.remote.webdriver import WebDriver
from typing import Dict, List
import json
from cryptography.fernet import Fernet
import os



stop_thread = False 

# Global variables
global_driver = None
browser_open = True
email_entry = None
password_entry = None
proxies = None
linkedin_account = None

def load_and_decrypt_credentials():
    credentials_path = "encrypted_credentials.json"
    if os.path.exists(credentials_path):
        with open(credentials_path, "r") as file:
            data = json.load(file)
        key = data["key"].encode()
        cipher_suite = Fernet(key)
        decrypted_username = cipher_suite.decrypt(data["credentials"]["username"].encode()).decode()
        decrypted_password = cipher_suite.decrypt(data["credentials"]["password"].encode()).decode()
        return decrypted_username, decrypted_password
    else:
        return None, None

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
    cursor.execute("""SELECT * FROM "CRM_linkedin_user" WHERE user_id_id = %s;""", (user,))
    row = cursor.fetchone()  # Assuming account IDs are unique, so you'd get at most one row
    conn.close()
    return row

def get_proxy_by_id(user):
    cursor, conn = get_db()
    cursor.execute("""SELECT * FROM "CRM_scrapperproxy" WHERE user_id_id = %s;""", (user,))
    row = cursor.fetchone()  # Assuming account IDs are unique, so you'd get at most one row
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
            time.sleep(random.uniform(0.1, 0.3))  # Adjust the delay to simulate typing speed

        # Find the password input element
        password_element = driver.find_element(By.ID, "password")

        # Type the password letter by letter with a small delay
        for letter in password:
            password_element.send_keys(letter)
            time.sleep(random.uniform(0.1, 0.3))  # Adjust the delay to simulate typing speed

        # Click the login button
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()

        # Wait for the main page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "main")))
    except Exception as e:
        print("An error occurred during login:", e)


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


def login_linkedin_using_cookies(driver, cookies):
    login_using_cookie_string(driver, cookies)
    # Wait for the main page to load
    driver.get("https://www.linkedin.com/")
    #WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "main")))
    time.sleep(20)


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

    co.add_argument("--force-device-scale-factor=0.6")
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

def click_element_with_actions(driver, name):
    print("clicking")

    actions = ActionChains(driver)
    actions.move_to_element(name)
    time.sleep(random.randint(4, 7))
    actions.click().perform()
    print("clicking performed")

def open_chrome_browser(proxy_host, proxy_port, proxy_user, proxy_pass, driver, linkedin_account):
    global global_driver
    # chromedriver_autoinstaller.install()
    global_driver = driverInit(proxy_host, proxy_port, proxy_user, proxy_pass)

    zoom_level = 0.6  # 70% zoom
    scale_factor = 0.5  # Further reduce the size by 20%
    downward_shift = 10  # Pixels to move the window downward
    left_shift = 2550  # Pixels to move the window to the left

    # Get the screen dimensions
    screen_width = global_driver.execute_script("return screen.width;")
    screen_height = global_driver.execute_script("return screen.height;")

    # Calculate the new window dimensions with zoom and scale adjustments
    window_width = int(((screen_width // 4) / zoom_level) * scale_factor) - 300
    window_height = int((screen_height / zoom_level) * scale_factor) - 950

    # Set the new window size
    global_driver.set_window_size(window_width, window_height)

    # Calculate the new window position
    # Adjust the position to account for the change in window size and move the window to the left
    new_x_position = int(
        (screen_width - (window_width * zoom_level)) - 130) - left_shift
    # Move the window downward by the specified number of pixels
    new_y_position = downward_shift

    # Set the new window position
    global_driver.set_window_position(new_x_position, new_y_position)

    global_driver.get("http://www.whatsmyip.org/")
    login_linkedin_using_cookies(
                    global_driver, linkedin_account[4])

    global browser_open
    while browser_open:
        pass

    global_driver.quit()



def return_chrome_browser(proxy_host, proxy_port, proxy_user, proxy_pass, driver, linkedin_account):
    global global_driver
    # chromedriver_autoinstaller.install()
    global_driver = driverInit(proxy_host, proxy_port, proxy_user, proxy_pass)

    zoom_level = 0.6  # 70% zoom
    scale_factor = 0.5  # Further reduce the size by 20%
    downward_shift = 10  # Pixels to move the window downward
    left_shift = 2550  # Pixels to move the window to the left

    # Get the screen dimensions
    screen_width = global_driver.execute_script("return screen.width;")
    screen_height = global_driver.execute_script("return screen.height;")

    # Calculate the new window dimensions with zoom and scale adjustments
    window_width = int(((screen_width // 4) / zoom_level) * scale_factor) - 300
    window_height = int((screen_height / zoom_level) * scale_factor) - 950

    # Set the new window size
    global_driver.set_window_size(window_width, window_height)

    # Calculate the new window position
    # Adjust the position to account for the change in window size and move the window to the left
    new_x_position = int(
        (screen_width - (window_width * zoom_level)) - 130) - left_shift
    # Move the window downward by the specified number of pixels
    new_y_position = downward_shift

    # Set the new window position
    global_driver.set_window_position(new_x_position, new_y_position)

    global_driver.get("http://www.whatsmyip.org/")
    login_linkedin_using_cookies(
                    global_driver, linkedin_account[4])

    return global_driver



def run_browser(proxy_host, proxy_port, proxy_user, proxy_pass, global_driver, linkedin_account):
    threading.Thread(target=open_chrome_browser(proxy_host, proxy_port, proxy_user, proxy_pass, global_driver, linkedin_account), daemon=True).start()


def on_closing():
    global browser_open
    browser_open = False
    root.destroy()


def save_credentials(username, password):
    # Generate a key
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)


    # Encrypt the credentials
    encrypted_username = cipher_suite.encrypt(username.encode()).decode()
    encrypted_password = cipher_suite.encrypt(password.encode()).decode()

    # Save the encrypted credentials and key to a JSON file
    data_to_store = {
        "key": key.decode(),
        "credentials": {
            "username": encrypted_username,
            "password": encrypted_password
        }
    }

    with open("encrypted_credentials.json", "w") as file:
        json.dump(data_to_store, file, indent=4)


def on_submit(save_status):
    global global_driver
    global proxies
    global linkedin_account
    proxies = None
    email = email_entry.get()
    password = password_entry.get()
    user = authenticate_user(email, password)
    if user:
        if save_status:
            save_credentials(email, password)
           

        linkedin_account = get_account_by_id(user)
        if linkedin_account:
            proxies = get_proxy_by_id(user)
            if proxies and not global_driver:
                run_browser(proxies[1], proxies[2], proxies[3], proxies[4], global_driver, linkedin_account)
        else:
            message_label.config(text="No LinkedIn Account Linked")

    else:
        message_label.config(text="Invalid credentials")

def restart_browser():
    global global_driver
    global proxies
    global linkedin_account
    if global_driver:
        global_driver.quit()
    run_browser(proxies[1], proxies[2], proxies[3], proxies[4], global_driver, linkedin_account)



def create_image_button(parent, image, text, width, height, **kwargs):
    frame = tk.Frame(parent, width=width, height=height)
    frame.pack_propagate(False)
    button = tk.Button(frame, image=image, text=text,
                       compound="left", **kwargs)
    button.pack(expand=True, fill=tk.BOTH)
    button.image = image
    return frame


def scroll_down(driver):
    SCROLL_PAUSE_TIME = 1
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        time.sleep(20)

# def scroll_container_down(driver, container):
#     SCROLL_PAUSE_TIME = 1

#     # Get container's scroll height
#     last_height = driver.execute_script("return arguments[0].scrollHeight", container)

#     while True:
#         # Scroll down
#         driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)

#         # Wait to load
#         time.sleep(SCROLL_PAUSE_TIME)

#         # Calculate new scroll height and compare with last scroll height
#         new_height = driver.execute_script("return arguments[0].scrollHeight", container)
#         if new_height == last_height:
#             break
#         last_height = new_height


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
        time.sleep(20)




def search_profiles():

    global global_driver
    if global_driver is not None:
        fetch_profiles(global_driver)
        # names, profile_links = fetch_profiles()


def fetch_profiles(global_driver):
    global stop_thread
    stop_thread = False
    start_page_index = int(start_page.get())
    end_page_index = int(end_page.get())
    search_pages_index = end_page_index - start_page_index

 
    scroll_down(global_driver)
    global_driver.find_element(By.XPATH, "(//button[@class='msg-overlay-bubble-header__control msg-overlay-bubble-header__control--new-convo-btn artdeco-button artdeco-button--circle artdeco-button--1 artdeco-button--primary ember-view'])")
    for s in range(1, start_page_index):
        global_driver.find_element(
                    By.XPATH, "(//button[@class='artdeco-pagination__button artdeco-pagination__button--next artdeco-button artdeco-button--muted artdeco-button--icon-right artdeco-button--1 artdeco-button--tertiary ember-view'])").click()
        time.sleep(5)
        scroll_down(global_driver)
 

    time.sleep(5)
    names = []
    profile_links = []

    for p in range(0, search_pages_index + 1):
        if stop_thread:
            return
        total_links = global_driver.find_elements(
            By.CLASS_NAME, "linked-area")
        print("Total Links : ", len(total_links))

        try:
            for j in range(1, len(total_links)+1):
                if stop_thread:
                    return
                print("IN ")
                profile_container = global_driver.find_elements(
            By.CLASS_NAME, "linked-area")[j -1]
                profile_element = profile_container.find_element(
                    By.XPATH, f".//a[@class='app-aware-link ']")
                profile = profile_element.get_attribute('href')

                pattern = r'https://www\.linkedin\.com/in/[\w\.-]+'

                def is_profile_url(url):
                    return bool(re.match(pattern, url))
                if is_profile_url(profile):
                    profile = profile.split('?')[0] + "/"
                    name = profile_element.find_element(By.XPATH, ".//span")
                    name = name.text.split("\n")[0]
                    try:
                        headline = profile_container.find_element(
                            By.XPATH, ".//div[@class='entity-result__primary-subtitle t-14 t-black t-normal']").text
                    except:
                        headline = ''
                    try:
                        location = profile_container.find_element(
                            By.XPATH, ".//div[@class='entity-result__secondary-subtitle t-14 t-normal']").text
                    except:
                        location = ''
                    print("INDEX", j)
                    print("PROFILE LINK", profile)
                    profile_links.append(profile)
                    print("NAME", name)
                    print(headline)
                    names.append(name)

                    first_name = name.split(' ')[0]
                    last_name = name.split(' ')[1]

                    tree.insert('', 'end', values=(
                        profile, first_name, last_name, '', '', '', '', headline, location))

                # print(f"Profile {j}: {profile.text}")

        except Exception as e:
            print(f"An error occurred during search: {e}")

        try:
            global_driver.find_element(
                By.XPATH, "(//button[@class='artdeco-pagination__button artdeco-pagination__button--next artdeco-button artdeco-button--muted artdeco-button--icon-right artdeco-button--1 artdeco-button--tertiary ember-view'])").click()
            time.sleep(5)
            scroll_down(global_driver)
        except:
            logging.exception('msg')
            break



def sales_nav_general_batch(base_url, page_index):
    global proxies
    global linkedin_account
    global global_driver
    global stop_thread
    if proxies and linkedin_account:
        global_driver = return_chrome_browser(proxies[1], proxies[2], proxies[3], proxies[4], global_driver, linkedin_account)
        wait = WebDriverWait(global_driver, 30)
        base_url_list = base_url.split('?')
        if len(base_url_list)> 1:
            base_url_string = base_url_list[0] + "?page=" + str(page_index) + "&" + base_url_list[1]
        global_driver.get(base_url_string)
        for p in range(1, 1):
            try:
                global_driver.refresh()
                wait.until(EC.visibility_of_element_located((By.XPATH, "(//button[@class='artdeco-pagination__button artdeco-pagination__button--next artdeco-button artdeco-button--muted artdeco-button--icon-right artdeco-button--1 artdeco-button--tertiary ember-view'])")))
                time.sleep(2.5)
                # Locate the element
                next_button = global_driver.find_element(
                    By.XPATH, "(//button[@class='artdeco-pagination__button artdeco-pagination__button--next artdeco-button artdeco-button--muted artdeco-button--icon-right artdeco-button--1 artdeco-button--tertiary ember-view'])")
                
                # Scroll the element into view
                global_driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                
                time.sleep(2)  # Adjust sleep time as needed
                
                # Click the element
                next_button.click()
                
                # Wait for the next page to load, if necessary
                time.sleep(5)
            except Exception as e:
                logging.exception('An error occurred while trying to click the next button.')
                return
        global_driver.refresh()
        wait.until(EC.visibility_of_element_located((By.XPATH, "(//li[@class='artdeco-list__item pl3 pv3 '])")))
        time.sleep(4)
        total_links = global_driver.find_elements(
        By.XPATH, "(//li[@class='artdeco-list__item pl3 pv3 '])")
        print(len(total_links))
        wait.until(EC.visibility_of_element_located((By.ID, "search-results-container")))

    
        container = global_driver.find_element(
            By.ID, "search-results-container")

        for i in range(1, 3):
            scroll_container_down(global_driver, container)
            time.sleep(4)

        try:
            for j in range(1, len(total_links)+1):
                if stop_thread:
                    return
                try:
                    
                    print("IN FOR LOOP")

                    profile_element = global_driver.find_element(
                        By.XPATH, f"(//div[@class='artdeco-entity-lockup__title ember-view']//a)[{j}]")
                    # print("CONTAINER FOUND")
                    name = profile_element.find_element(By.XPATH, ".//span")
                    name = name.text.split("\n")[0]
                    print("NAME>>>>>>>>", name)
                    # continue

                    click_element_with_actions(global_driver, profile_element)
                    try:
                        wait.until(EC.visibility_of_element_located((By.XPATH, "//button[@class='ember-view _button_ps32ck _small_ps32ck _tertiary_ps32ck _circle_ps32ck _container_iq15dg _overflow-menu--trigger_1xow7n']")))
                        global_driver.find_element(
                            By.XPATH, "//button[@class='ember-view _button_ps32ck _small_ps32ck _tertiary_ps32ck _circle_ps32ck _container_iq15dg _overflow-menu--trigger_1xow7n']").click()
                        wait.until(EC.visibility_of_element_located((By.XPATH, "(//div[@class='_container_x5gf48 _visible_x5gf48 _container_iq15dg _raised_1aegh9']//ul//li)[3]")))

                        #global_driver.find_element(
                        #    By.XPATH, "(//div[@class='_container_x5gf48 _visible_x5gf48 _container_iq15dg _raised_1aegh9']//ul//li)[3]").click()
                        # Assuming global_driver is your Selenium WebDriver
                        options = global_driver.find_elements(
                            By.XPATH, "//div[@class='_container_x5gf48 _visible_x5gf48 _container_iq15dg _raised_1aegh9']//ul//li")

                        for option in options:
                            if option.text == "View LinkedIn profile":
                                option.click()
                                break
                        time.sleep(2)
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
                            wait.until(EC.visibility_of_element_located((By.XPATH, "(//span[contains(@class,'text-body-small inline t-black--light break-words')])")))

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

                        tree.insert('', 'end', values=(
                            profile, first_name, last_name, '', '', '', '', headline, location))
                    except:
                        pass
                    global_driver.back()
                    time.sleep(2)
                    global_driver.refresh()
                    time.sleep(5)
                    #wait.until(EC.visibility_of_element_located((By.XPATH, f"(//div[@class='artdeco-entity-lockup__title ember-view']//a)[{j}]")))
                    wait.until(EC.visibility_of_element_located((By.ID, "search-results-container")))

                    container = global_driver.find_element(
                        By.ID, "search-results-container")

                    for i in range(1, 3):
                        scroll_container_down(global_driver, container)
                        time.sleep(4)
                except:
                    logging.exception("msg")
                    wait.until(EC.visibility_of_element_located((By.ID, "search-results-container")))
                    container = global_driver.find_element(
                        By.ID, "search-results-container")
                    for i in range(1, 3):
                        scroll_container_down(global_driver, container)
                        time.sleep(4)
                    continue

                # print(f"Profile {j}: {profile.text}")

        except Exception as e:
            logging.exception('msg')
            print(f"An error occurred during search: {e}")






def sales_navigator_search(event=None):
    global global_driver
    global stop_thread
    wait = WebDriverWait(global_driver, 10)
    stop_thread = False
    print(global_driver)
    print("IN SALES NAV")
    start_page_index = int(start_page.get())
    end_page_index = int(end_page.get())
    search_pages_index = end_page_index - start_page_index
    if search_pages_index == 0:
        search_pages_index = 1
    print(start_page_index)
    print(end_page_index)
    print("GLOBAL DRIVER", global_driver)
    window_handles = global_driver.window_handles
    print(window_handles)

    # Switch to the new window (assuming it's the last one opened)
    global_driver.switch_to.window(window_handles[-1])
    # global_driver.switch_to.new_window('tab')
    # scroll_down(global_driver)
    # scroll_up(global_driver)
    # scroll_down(global_driver)
    base_url = global_driver.current_url
    global_driver.quit()


    print("BEFORE FOR LOOP")
    for p in range(start_page_index, end_page_index  + 1):
        sales_nav_general_batch(base_url, p)

    

def lead_search_batch_function(base_url, page_index):
    global proxies
    global linkedin_account
    global global_driver
    global stop_thread

    if proxies and linkedin_account:
        global_driver = return_chrome_browser(proxies[1], proxies[2], proxies[3], proxies[4], global_driver, linkedin_account)
        wait = WebDriverWait(global_driver, 10)
        global_driver.get(base_url)
        for p in range(1, page_index):
            try:
                global_driver.refresh()
                wait.until(EC.visibility_of_element_located((By.XPATH, "(//button[@class='artdeco-pagination__button artdeco-pagination__button--next artdeco-button artdeco-button--muted artdeco-button--icon-right artdeco-button--1 artdeco-button--tertiary ember-view'])")))
                time.sleep(2.5)
                # Locate the element
                next_button = global_driver.find_element(
                    By.XPATH, "(//button[@class='artdeco-pagination__button artdeco-pagination__button--next artdeco-button artdeco-button--muted artdeco-button--icon-right artdeco-button--1 artdeco-button--tertiary ember-view'])")
                
                # Scroll the element into view
                global_driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                
                time.sleep(2)  # Adjust sleep time as needed
                
                # Click the element
                next_button.click()
                
                # Wait for the next page to load, if necessary
                time.sleep(5)
            except Exception as e:
                logging.exception('An error occurred while trying to click the next button.')
                return
        wait.until(EC.visibility_of_element_located((By.XPATH, "(//tr[@class='artdeco-models-table-row ember-view'])")))

        time.sleep(2.5)
        if stop_thread:
            return
        total_links = global_driver.find_elements(
            By.XPATH, "(//tr[@class='artdeco-models-table-row ember-view'])")
        print(len(total_links))


        try:
            for j in range(1, len(total_links)+1):
                if stop_thread:
                    return
                try:
                    print("IN FOR LOOP")
                    global_driver.refresh()
                    wait.until(EC.visibility_of_element_located((By.XPATH, "(//tr[@class='artdeco-models-table-row ember-view'])")))
                    time.sleep(2.5)

                    profile_element = global_driver.find_element(
                        By.XPATH, f"(//div[@class='white-space-nowrap overflow-hidden text-overflow-ellipsis']//a)[{j}]")
                    name = profile_element.text.split("\n")[0]

                    print(name)

                    click_element_with_actions(global_driver, profile_element)
                    try:
                        time.sleep(2.5)
                        global_driver.refresh()
                        wait.until(EC.visibility_of_element_located((By.XPATH, "//button[@class='ember-view _button_ps32ck _small_ps32ck _tertiary_ps32ck _circle_ps32ck _container_iq15dg _overflow-menu--trigger_1xow7n']")))

                        global_driver.find_element(
                            By.XPATH, "//button[@class='ember-view _button_ps32ck _small_ps32ck _tertiary_ps32ck _circle_ps32ck _container_iq15dg _overflow-menu--trigger_1xow7n']").click()
                        
                        wait.until(EC.visibility_of_element_located((By.XPATH, "(//div[@class='_container_x5gf48 _visible_x5gf48 _container_iq15dg _raised_1aegh9']//ul//li)[3]")))

                        #global_driver.find_element(
                        #    By.XPATH, "(//div[@class='_container_x5gf48 _visible_x5gf48 _container_iq15dg _raised_1aegh9']//ul//li)[3]").click()
                        # Assuming global_driver is your Selenium WebDriver
                        options = global_driver.find_elements(
                            By.XPATH, "//div[@class='_container_x5gf48 _visible_x5gf48 _container_iq15dg _raised_1aegh9']//ul//li")

                        for option in options:
                            if option.text == "View LinkedIn profile":
                                option.click()
                                break
                        time.sleep(2)
                        # Get all the window handles
                        window_handles = global_driver.window_handles

                        # Check if there are at least two tabs
                        if len(window_handles) >= 2:
                            # Switch to the 2nd tab (which is at index 1 since indexing starts at 0)
                            global_driver.switch_to.window(window_handles[1])
                        else:
                            print("There are less than two tabs open.")
                            global_driver.back()
                            time.sleep(2)
                            continue
                        profile = global_driver.current_url
                        try:
                            wait.until(EC.visibility_of_element_located((By.XPATH, "(//span[contains(@class,'text-body-small inline t-black--light break-words')])")))

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

                        tree.insert('', 'end', values=(
                            profile, first_name, last_name, '', '', '', '', headline, location))
                    except:
                        logging.exception('msg')
                        pass
                    time.sleep(1.5)
                    global_driver.refresh()
                    global_driver.back()
                    time.sleep(2)
                    
                except:
                    logging.exception('msg')
                    time.sleep(3)
                    global_driver.refresh()
                    time.sleep(3)

                    
                    continue
            global_driver.quit()

        except Exception as e:
            logging.exception('msg')
            print(f"An error occurred during search: {e}")
            global_driver.quit()





    


# Lead Search
def sales_navigator_lead_search(event=None):
    global global_driver
    global stop_thread
    stop_thread = False
    wait = WebDriverWait(global_driver, 10)
    print("IN SALES NAV")
    start_page_index = int(start_page.get())
    end_page_index = int(end_page.get())
    search_pages_index = end_page_index - start_page_index + 1
    if not end_page_index >= start_page_index:
        return


    window_handles = global_driver.window_handles

    # Switch to the new window (assuming it's the last one opened)
    global_driver.switch_to.window(window_handles[-1])
    base_url = global_driver.current_url
    global_driver.quit()



    print("BEFORE FOR LOOP")

    for p in range(start_page_index, end_page_index  + 1):
        lead_search_batch_function(base_url, p)
        
        
        


def save_to_csv():
    global tree
    initialdir = "/"
    filename = filedialog.asksaveasfilename(
        initialdir=initialdir, 
        title="Select file", 
        filetypes=(("CSV files", "*.csv"), ("all files", "*.*")),
        defaultextension=".csv",
        initialfile=f"profiles_data.csv"
    )

    if filename:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['ProfileLink', 'FirstName', 'LastName', 'Email',
                                'Phone', 'Twitter', 'Messenger', 'TagLineTitle', 'Location'])

            # Extract and write data from the tree
            for item in tree.get_children():
                csvwriter.writerow(tree.item(item, 'values'))

        print("Data saved to", filename)
    else:
        print("Save operation cancelled")


def on_search_now_click():
    """Determines which function to call based on the dropdown selection."""
    selected_option = linkedin_combobox.get()
    print("SELECTED OPTION", selected_option)
    if selected_option == "LinkedIn Search":
        search_profiles()
    elif selected_option == "LinkedIn Sales Nav General Search":
        sales_navigator_search()
    elif selected_option == "LinkedIn Sales Nav Lead Search":
        sales_navigator_lead_search()


current_dropdown_selection = "LinkedIn Search"


def on_dropdown_selection(event):
    """Updates the Search Now button's command based on the selected option."""
    # search_btn_frame.config(command=on_search_now_click)
    global current_dropdown_selection
    current_dropdown_selection = linkedin_combobox.get()

def on_stop_click():
    print('Stop Clicked')
    global stop_thread
    stop_thread = True

def on_reset_click():
    print('Reset Clicked')
    for i in tree.get_children():
        tree.delete(i)

def on_search_now_threaded():
    threading.Thread(target=on_search_now_click, daemon=True).start()

def on_submit_threaded(save_status):
    # Pass the target function and args correctly
    submit_thread = threading.Thread(target=on_submit, args=(save_status,))
    submit_thread.daemon = True  # This makes the thread exit when the main program exits
    submit_thread.start()

def on_restart_click():
    submit_thread = threading.Thread(target=restart_browser)
    submit_thread.daemon = True  # Optional: makes the thread exit when the main program exits
    submit_thread.start()

def upload_json_to_db():
    global tree

    # Create an empty dictionary to store the data
    data = {}
    keys = ['ProfileLink', 'FirstName', 'LastName', 'Email', 'Phone', 'Twitter', 'Messenger', 'TagLineTitle', 'Location']

    for key in keys:
        data[key] = []  # Initialize each key with an empty list

    # Extract and append data to the corresponding lists
    for item in tree.get_children():
        values = tree.item(item, 'values')
        for i in range(len(keys)):
            data[keys[i]].append(values[i])

    data_dict = json.dumps(data, indent=4)
    cursor, conn = get_db()
    query ="""INSERT INTO "CRM_excel_file" ("json_data") VALUES (%s);"""
    try: 
        cursor.execute(query, (data_dict,))
    
        conn.commit()
        conn.close()
        print("DATA SAVED TO JSON SUCCESSFULLY")
    except:
        logging.exception('msg')


def create_ui():
    global root, email_entry, password_entry, tree, start_page, end_page, message_label, linkedin_combobox, search_btn_frame
    # Load and decrypt credentials
    decrypted_username, decrypted_password = load_and_decrypt_credentials()
    root = tk.Tk()
    root.title("LinkedIn Data Extractor")
    # root.state('zoomed')
    # Get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Set window size to 75% of the screen size
    window_width = int(screen_width * 0.67)
    window_height = screen_height
    root.geometry(f"{window_width}x{window_height}+0+0")

    # Define colors
    frame_bg_color = "#f0f0f0"
    button_color = "#d9d9d9"
    button_active_color = "#c0c0c0"
    button_fg_color = "#000000"

    # Icons
    search_icon = tk.PhotoImage(file="global-search.png")
    stop_icon = tk.PhotoImage(file="stop.png")
    save_icon = tk.PhotoImage(file="diskette.png")
    reset_icon = tk.PhotoImage(file="restart.png")
    restart_icon = tk.PhotoImage(file="synchronize.png")
    upload_icon = tk.PhotoImage(file="upload.png")


    paned_window = tk.PanedWindow(
        root, orient=tk.HORIZONTAL, bg=frame_bg_color)
    paned_window.pack(fill=tk.BOTH, expand=True)

    left_panel = tk.Frame(paned_window, bd=2,
                          relief=tk.SUNKEN, bg=frame_bg_color)
    # right_panel = tk.Frame(paned_window, bd=2, relief=tk.SUNKEN, bg=frame_bg_color)
    left_panel.config(width=500)
    paned_window.add(left_panel)
    # paned_window.add(right_panel)

     # Login Frame
    login_frame = tk.LabelFrame(
        left_panel, text="LinkedIn Sign In", padx=10, pady=10, bg=frame_bg_color)
    login_frame.pack(fill=tk.X, expand=False, padx=5, pady=5)
    tk.Label(login_frame, text="Username/Email:",
             bg=frame_bg_color).grid(row=0, column=0, sticky='e')
    email_entry = tk.Entry(login_frame)
    email_entry.grid(row=0, column=1, sticky='we', padx=5)
    tk.Label(login_frame, text="Password:", bg=frame_bg_color).grid(
        row=1, column=0, sticky='e', pady=10)
    password_entry = tk.Entry(login_frame, show="*")
    password_entry.grid(row=1, column=1, sticky='we', padx=5)

    # Set the loaded credentials (if any) to the entry fields
    if decrypted_username and decrypted_password:
        email_entry.insert(0, decrypted_username)
        password_entry.insert(0, decrypted_password)
    submit_button = tk.Button(login_frame, text="Sign in", 
                          command=lambda: on_submit_threaded(save_credentials_var.get()),
                          bg=button_color, fg=button_fg_color, activebackground=button_active_color)
    submit_button.grid(row=0, column=2, rowspan=2, padx=10)

    save_credentials_var = tk.IntVar(value=0)  # Default to unchecked (0)

    # Checkbox for saving credentials
    save_credentials_checkbox = tk.Checkbutton(login_frame, text="Save Username/password.",
                                            variable=save_credentials_var, bg=frame_bg_color)
    save_credentials_checkbox.grid(row=2, column=1, sticky='w')
    # Message Label for authentication feedback
    message_label = tk.Label(
        login_frame, text="", fg="red", bg=frame_bg_color)  # Red text for errors
    message_label.grid(row=3, column=0, columnspan=3, sticky='we', pady=(5, 0))

    # Search Frame
    search_frame = tk.LabelFrame(
        left_panel, text="Search Criteria", padx=10, pady=10, bg=frame_bg_color)
    search_frame.pack(fill=tk.X, expand=False, padx=5, pady=5)
    tk.Label(search_frame, text="Extract from:",
             bg=frame_bg_color).grid(row=0, column=0, sticky='e')
    # Create the Spinbox widget and then apply the grid layout in a separate step
    start_page = tk.Spinbox(search_frame, from_=1, to=50, width=5)
    start_page.grid(row=0, column=1, sticky='w', padx=(5, 0))
    tk.Label(search_frame, text="to", bg=frame_bg_color).grid(
        row=0, column=2, sticky='e')
    # Similarly for end_page
    end_page = tk.Spinbox(search_frame, from_=1, to=50, width=5)
    end_page.grid(row=0, column=3, sticky='w', padx=(0, 5))

    # Dropdown
    linkedin_options = ["LinkedIn Search",
                        "LinkedIn Sales Nav General Search", "LinkedIn Sales Nav Lead Search"]
    linkedin_combobox = ttk.Combobox(
        search_frame, values=linkedin_options, state='readonly', width=30)
    linkedin_combobox.grid(row=0, column=5, sticky='w', padx=(10, 0))

    # Set the first option as default
    linkedin_combobox.current(0)

    # Bind the selection event
    linkedin_combobox.bind("<<ComboboxSelected>>", on_dropdown_selection)

    tk.Label(search_frame, text="pages only.", bg=frame_bg_color).grid(
        row=0, column=4, sticky='w')

    # Button Frame
    button_frame = tk.Frame(search_frame, bg=frame_bg_color)
    button_frame.grid(row=1, column=0, columnspan=7, pady=5, sticky='ew')
    # search_btn_frame = create_image_button(button_frame, search_icon, "Search Now", 150, 76, bg=button_color, fg=button_fg_color, activebackground=button_active_color)
    # search_btn_frame.pack(side=tk.LEFT, padx=5)
    search_btn_frame = create_image_button(button_frame, search_icon, "Search Now", 150, 76,
                                       command=on_search_now_threaded,
                                       bg=button_color, fg=button_fg_color, activebackground=button_active_color)
    search_btn_frame.pack(side=tk.LEFT, padx=5)
    stop_btn_frame = create_image_button(button_frame, stop_icon, "Stop", 150, 76,
                                     command=on_stop_click,
                                     bg=button_color, fg=button_fg_color, activebackground=button_active_color)
    stop_btn_frame.pack(side=tk.LEFT, padx=5)
    save_btn_frame = create_image_button(button_frame, save_icon, "Save", 150, 76, command=save_to_csv,
                                         bg=button_color, fg=button_fg_color, activebackground=button_active_color)
    save_btn_frame.pack(side=tk.LEFT, padx=5)
    reset_btn_frame = create_image_button(button_frame, reset_icon, "Reset All", 150,
                                      76, command=on_reset_click,
                                      bg=button_color, fg=button_fg_color, activebackground=button_active_color)
    reset_btn_frame.pack(side=tk.LEFT, padx=5)
    upload_btn_frame = create_image_button(button_frame, upload_icon, "Upload", 150,
                                      76, command=upload_json_to_db,
                                      bg=button_color, fg=button_fg_color, activebackground=button_active_color)
    upload_btn_frame.pack(side=tk.LEFT, padx=5)

    restart_btn_frame = create_image_button(button_frame, restart_icon, "Restart Browser", 150,
                                      76, command=on_restart_click,
                                      bg=button_color, fg=button_fg_color, activebackground=button_active_color)
    restart_btn_frame.pack(side=tk.LEFT, padx=5)

    # Result Frame
    result_frame = tk.LabelFrame(
        left_panel, text="Results", padx=10, pady=10, bg=frame_bg_color)
    result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    tree = ttk.Treeview(result_frame)
    tree['columns'] = ('ProfileLink', 'FirstName', 'LastName', 'Email',
                       'Phone', 'Twitter', 'Messenger', 'TagLineTitle', 'Location')
    for col in tree['columns']:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
    scrollbar = ttk.Scrollbar(
        result_frame, orient='vertical', command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
    # insert_in_tree(tree)
    # Inserting names in List

    root.protocol("WM_DELETE_WINDOW", on_closing)
    #run_browser()
    root.mainloop()


create_ui()
