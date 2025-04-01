import tkinter as tk
import psycopg2
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os, zipfile, string
from selenium.common.exceptions import WebDriverException
from tkinter import ttk
import threading
import re

def sanitize_filename(filename):
    # Replace any character that is not a letter, number, underscore, or hyphen with an underscore
    return re.sub(r'[^\w\-_\. ]', '_', filename)


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

def get_accounts():
    

    cursor, conn = get_db()
    cursor.execute("""SELECT name, proxyip, proxyport, proxyuser, proxypass FROM "CRM_account";""")
    rows = cursor.fetchall()
    conn.close()
    return rows

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
  

def driverInit(account_name, proxy_host, proxy_port, proxy_user, proxy_pass):
    sanitized_account_name = sanitize_filename(account_name)
    # Define a unique user data directory for each account
    user_data_dir = f"{os.getcwd()}/user_profiles/{sanitized_account_name}"
    os.makedirs(user_data_dir, exist_ok=True)  # Create the directory if it doesn't exist
    
    proxyauth_plugin_path = create_proxyauth_extension(
        proxy_host=proxy_host,
        proxy_port=proxy_port,
        proxy_username=proxy_user,
        proxy_password=proxy_pass,
        scheme='http',
        plugin_path=f"{os.getcwd()}/proxy_auth_plugin.zip"
    )
    
    co = Options()
    co.add_argument(f"--user-data-dir={user_data_dir}")  # Set the user data directory
    co.add_argument("--profile-directory=Default")
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

def open_browser_with_proxy(name, proxyip, proxyport, proxyuser, proxypass):
    threading.Thread(target=_open_browser, args=(name, proxyip, proxyport, proxyuser, proxypass)).start()

def _open_browser(account_name, proxyip, proxyport, proxyuser, proxypass):
    driver = driverInit(account_name, proxyip, proxyport, proxyuser, proxypass)
    driver.get("http://www.whatsmyip.org/")
    # Keep the script running as long as the browser window is open
    while True:
        try:
            time.sleep(1)
            driver.title  # This is just to check if the browser is still running
        except WebDriverException:
            print("Browser closed")
            break

class DesktopApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Account Browser Opener")
        self.master.geometry('550x700')  # Set the size of the window
        self.initialize_ui()

    def initialize_ui(self):
        container = ttk.Frame(self.master)
        container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create a canvas for adding a scrollbar
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configure the canvas for scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        # Assume get_accounts() is defined elsewhere
        for account in get_accounts():
            self.create_account_frame(scrollable_frame, account)

        # Pack the canvas and scrollbar
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_account_frame(self, parent, account):
        name, proxyip, proxyport, proxyuser, proxypass = account
        
        # Frame for each account
        account_frame = ttk.Frame(parent, padding=5)
        account_frame.pack(fill='x', expand=True, padx=40, pady=15)

        # Label and button frame within the account frame
        label_frame = ttk.Frame(account_frame)
        label_frame.pack(side='left', fill='x', expand=True)

        # Name label on the left of the label frame, aligned to the west
        name_label = ttk.Label(label_frame, text=name, anchor='w')
        name_label.pack(side='left', padx=5)

        # Open button frame for precise button placement
        button_frame = ttk.Frame(account_frame)
        button_frame.pack(side='right', fill='y')

        # Open button on the right of the button frame, aligned to the east
        open_button = ttk.Button(button_frame, text="Open", command=lambda: open_browser_with_proxy(name, proxyip, proxyport, proxyuser, proxypass))
        open_button.pack(side='right', padx=5)


def main():
    root = tk.Tk()
    app = DesktopApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()