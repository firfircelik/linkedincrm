import tkinter as tk
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import threading

# Function to open Chrome browser
# def open_chrome_browser():
#     # Automatically download and install Chrome WebDriver
#     chromedriver_autoinstaller.install()

#     # Create a Chrome WebDriver instance
#     driver = webdriver.Chrome()

#     # The rest of your code remains the same
#     driver.maximize_window()
#     driver.get("https://www.w3schools.com/")
    # while(True):
    #     pass
    # driver.refresh()
    # driver.close()

def open_chrome_browser():
    # Automatically download and install Chrome WebDriver
    chromedriver_autoinstaller.install()

    # Create a Chrome WebDriver instance
    driver = webdriver.Chrome()

    # Calculate half the screen width and height
    screen_width = driver.execute_script("return screen.width;")
    screen_height = driver.execute_script("return screen.height;")
    window_width = screen_width // 3
    window_height = screen_height

    # Set the window size to half the screen width and full screen height
    driver.set_window_size(window_width, window_height)

    # Set the window position to the right half of the screen
    driver.set_window_position(window_width+500, 0)

    # Navigate to a website
    driver.get("https://www.w3schools.com/")

    # Keep the browser open for 10 seconds or until manually closed
    driver.implicitly_wait(10)

# open_chrome_browser()
def run_browser():
    threading.Thread(target=open_chrome_browser, daemon=True).start()

root = tk.Tk()
# open_chrome_browser()
def on_entry_change(event):
    # Handle entry text change here
    pass

# def driverInit():
#     chrome_options = Options()
#     #chrome_options.add_argument("--headless")  # Run Chrome in headless mode.
#     chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration.
#     chrome_options.add_argument("--window-size=1920x1080")  # Set the window size.

#     driver = webdriver.Chrome(options=chrome_options)
#     driver.maximize_window()
#     return driver
# driver = driverInit()
# # Create a frame for the Right side box

# right_frame = tk.Frame(root, width=400, height=400, bg="lightblue")
# right_frame.pack(side=tk.RIGHT, padx=20, pady=20, anchor="ne")

# # Create a big box (frame) in the center of the right frame
# right_box_frame = tk.Frame(right_frame, width=300, height=300, bg="white")
# right_box_frame.place(relx=0.5, rely=0.5, anchor="center")

# # Create a square placeholder (entry widget) inside the box frame for text input
# label_to = tk.Label(right_box_frame, text="To", bg="white")
# label_to.place(relx=0.3, rely=0.3, anchor="center")

# placeholder1 = tk.Entry(right_box_frame, width=10, fg="black")
# placeholder1.place(relx=0.5, rely=0.3, anchor="center")
# placeholder1.bind("<KeyRelease>", on_entry_change)

# # Create the "From" label and entry
# label_from = tk.Label(right_box_frame, text="From", bg="white")
# label_from.place(relx=0.3, rely=0.5, anchor="center")

# placeholder2 = tk.Entry(right_box_frame, width=10, fg="black")
# placeholder2.place(relx=0.5, rely=0.5, anchor="center")
# placeholder2.bind("<KeyRelease>", on_entry_change)




# Create a redirect button
redirect_button = tk.Button(root, text="Redirect", command=open_chrome_browser)
redirect_button.pack(pady=5)

# Other parts of your code
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = int(screen_width * 0.9)
print(screen_height, screen_width)
window_height = int(screen_height * 0.9)
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")
root.title("Windows Application")
root.configure(bg="white")



left_frame = tk.Frame(root, width=window_width/2, height=window_height/2, bg="lightgray")
left_frame.pack(side=tk.LEFT, padx=0, pady=20, anchor="nw")
left_box_frame = tk.Frame(left_frame, width=300, height=300, bg="white")
left_box_frame.place(relx=0.25, rely=0.5, anchor="center")


label_email = tk.Label(left_box_frame, text="Email", bg="white")
label_email.place(relx=0.2, rely=0.3, anchor="center")

email_placeholder = tk.Entry(left_box_frame, width=15, fg="black")
email_placeholder.place(relx=0.5, rely=0.3, anchor="center")
email_placeholder.bind("<KeyRelease>", on_entry_change)

label_password = tk.Label(left_box_frame, text="Password", bg="white")
label_password.place(relx=0.2, rely=0.5, anchor="center")

password_placeholder = tk.Entry(left_box_frame, width=15, fg="black", show="*")
password_placeholder.place(relx=0.5, rely=0.5, anchor="center")
password_placeholder.bind("<KeyRelease>", on_entry_change)

submit_button = tk.Button(left_box_frame, text="Submit")
submit_button.place(relx=0.5, rely=0.7, anchor="center")

# LEFT BOX 2ND FRAME
left_box_frame2 = tk.Frame(left_frame, width=300, height=300, bg="white")
left_box_frame2.place(relx=0.7, rely=0.5, anchor="center")
# contents

label_to = tk.Label(left_box_frame2, text="To", bg="white")
label_to.place(relx=0.3, rely=0.3, anchor="center")

placeholder1 = tk.Entry(left_box_frame2, width=10, fg="black")
placeholder1.place(relx=0.5, rely=0.3, anchor="center")
placeholder1.bind("<KeyRelease>", on_entry_change)

# Create the "From" label and entry
label_from = tk.Label(left_box_frame2, text="From", bg="white")
label_from.place(relx=0.3, rely=0.5, anchor="center")

placeholder2 = tk.Entry(left_box_frame2, width=10, fg="black")
placeholder2.place(relx=0.5, rely=0.5, anchor="center")
placeholder2.bind("<KeyRelease>", on_entry_change)



# label = tk.Label(root, text="LinkedIn")
# label.pack()

# button = tk.Button(root, text="Search Now")
# button.pack()

# label_text = "RIGHT SIDE"
# label2 = tk.Label(right_frame, text=label_text, bg="lightgray")
# label2.place(relx=0.5, rely=0.5, anchor="center")

run_browser()
root.mainloop()


# import sys
# from PyQt5.QtCore import QUrl
# from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton
# from PyQt5.QtWebEngineWidgets import QWebEngineView

# class WebBrowser(QWidget):
#     def __init__(self):
#         super().__init__()

#         self.web_view = QWebEngineView()
#         self.url_entry = QLineEdit()
#         self.load_button = QPushButton("Load Website")
#         self.previous_button = QPushButton("Previous")
#         self.next_button = QPushButton("Next")

#         layout = QVBoxLayout()
#         layout.addWidget(self.previous_button)
#         layout.addWidget(self.next_button)
#         layout.addWidget(self.url_entry)
#         layout.addWidget(self.load_button)
#         layout.addWidget(self.web_view)
#         self.setLayout(layout)

#         self.load_button.clicked.connect(self.load_website)
#         self.previous_button.clicked.connect(self.go_back)
#         self.next_button.clicked.connect(self.go_forward)

#     def load_website(self):
#         url = self.url_entry.text()
#         if url:
#             self.web_view.load(QUrl(url))

#     def go_back(self):
#         if self.web_view.canGoBack():
#             self.web_view.back()

#     def go_forward(self):
#         if self.web_view.canGoForward():
#             self.web_view.forward()

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     browser = WebBrowser()
#     browser.show()
#     sys.exit(app.exec_())
