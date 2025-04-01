import tkinter as tk
from tkinter import ttk
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import threading
import time
import re
import zipfile
import string
import os
import csv
import random
import psycopg2
from user_authentication import authenticate_user
import threading
from datetime import datetime
import json
from tkinter import filedialog
stop_thread = False  



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
    cursor, conn = get_db()
    cursor.execute("""
        SELECT name, boolean_search, start_date, end_date, 
               min_age, max_age, min_salary, max_salary, batch_size 
        FROM "CRM_campaign"
        WHERE boolean_search IS NOT NULL
          AND CURRENT_DATE BETWEEN start_date AND end_date;
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows ``


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
    PROXY_HOST = "102.129.157.76"
    PROXY_PORT = "12323"
    PROXY_USER = "14ab645c6d19b"
    PROXY_PASS = "99c354882c"

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
    co.add_argument("--force-device-scale-factor=0.7")
    time.sleep(1)
    driver = webdriver.Chrome(options=co)
    driver.maximize_window()
    return driver

def run():
    campaigns = get_campaigns()
    for campaign in campaigns:
        name, boolean_search, start_date, end_date, min_age, max_age, min_salary, max_salary, batch_size = campaign
        driver = driverInit()
        driver.get("")
        cookies = 