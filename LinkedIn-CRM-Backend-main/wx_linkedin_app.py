import wx
import wx.html2 as webview
import wx.grid as gridlib

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title)

        # Set the frame size to the size of the screen
        screenSize = wx.DisplaySize()
        self.SetSize(screenSize)

        # Create a splitter window
        splitter = wx.SplitterWindow(self)

        # Create left and right panels
        left_panel = wx.Panel(splitter)
        right_panel = wx.Panel(splitter)

        # Main sizer for the left panel
        self.left_main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Sign-In Box
        sign_in_box = wx.StaticBox(left_panel, label="LinkedIn Sign In")
        sign_in_sizer = wx.StaticBoxSizer(sign_in_box, wx.VERTICAL)

        # Components for the Sign-In Box
        username_label = wx.StaticText(left_panel, label="Username/Email:")
        self.username_input = wx.TextCtrl(left_panel, size=(200, -1))
        password_label = wx.StaticText(left_panel, label="Password:")
        self.password_input = wx.TextCtrl(left_panel, style=wx.TE_PASSWORD, size=(200, -1))
        save_credentials_checkbox = wx.CheckBox(left_panel, label="Save Username/password")
        sign_in_button = wx.Button(left_panel, label="Sign in")

        # Add components to the sign-in sizer
        sign_in_sizer.Add(username_label, 0, wx.ALL, 5)
        sign_in_sizer.Add(self.username_input, 0, wx.ALL, 5)
        sign_in_sizer.Add(password_label, 0, wx.ALL, 5)
        sign_in_sizer.Add(self.password_input, 0,wx.ALL, 5)
        sign_in_sizer.Add(save_credentials_checkbox, 0, wx.ALL, 5)
        sign_in_sizer.Add(sign_in_button, 0, wx.ALL|wx.CENTER, 5)

        # Add the Sign-In Box to the main sizer
        self.left_main_sizer.Add(sign_in_sizer, 0, wx.ALL|wx.EXPAND, 10)

        # Search Criteria Box
        search_criteria_box = wx.StaticBox(left_panel, label="Search Criteria")
        search_criteria_sizer = wx.StaticBoxSizer(search_criteria_box, wx.VERTICAL)
        
        # Filter sizer for search filters
        filter_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Create and add filter components to the filter_sizer
        label_extract_from = wx.StaticText(left_panel, label="Extract from:")
        spin_from = wx.SpinCtrl(left_panel, min=1, max=50, initial=1)
        label_to = wx.StaticText(left_panel, label="to")
        spin_to = wx.SpinCtrl(left_panel, min=1, max=50, initial=1)
        label_pages_only = wx.StaticText(left_panel, label="pages only.")
        source_choices = ["LinkedIn", "Linkedin Sales Navigator Site"]  # Add your sources here
        combo_source = wx.ComboBox(left_panel, value=source_choices[0],choices=source_choices, style=wx.CB_READONLY)
        
        # Add components to filter_sizer horizontally
        filter_sizer.Add(label_extract_from, 0, wx.ALL|wx.CENTER, 5)
        filter_sizer.Add(spin_from, 0, wx.ALL, 5)
        filter_sizer.Add(label_to, 0, wx.ALL|wx.CENTER, 5)
        filter_sizer.Add(spin_to, 0, wx.ALL, 5)
        filter_sizer.Add(label_pages_only, 0, wx.ALL|wx.CENTER, 5)
        filter_sizer.Add(combo_source, 0, wx.ALL, 5)
        
        # Add filter_sizer to the search_criteria_sizer
        search_criteria_sizer.Add(filter_sizer, 0, wx.EXPAND|wx.ALL, 5)
        
        # Horizontal sizer for search buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Components for the Search Criteria box buttons
        search_button = self.create_labeled_button(left_panel, "Search Now", 'global-search.png')
        stop_button = self.create_labeled_button(left_panel, "Stop", 'stop.png')
        save_button = self.create_labeled_button(left_panel, "Save", 'diskette.png')
        reset_button = self.create_labeled_button(left_panel, "Reset All", 'restart.png')

        # Add buttons to the button_sizer
        button_sizer.Add(search_button, 0, wx.ALL, 5)
        button_sizer.Add(stop_button, 0, wx.ALL, 5)
        button_sizer.Add(save_button, 0, wx.ALL, 5)
        button_sizer.Add(reset_button, 0, wx.ALL, 5)
        
        # Add button_sizer to the search_criteria_sizer below the filter_sizer
        search_criteria_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
        # Add the Search Criteria box to the main sizer
        self.left_main_sizer.Add(search_criteria_sizer, 0, wx.EXPAND|wx.ALL, 10)

        # Set the sizer for the left panel
        left_panel.SetSizer(self.left_main_sizer)

        # Create a web browser on the right panel
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        self.browser = webview.WebView.New(right_panel)
        right_sizer.Add(self.browser, 1, wx.EXPAND)
        right_panel.SetSizer(right_sizer)

        # add table
        self.create_results_table(left_panel)

        # Load a website in the WebView
        self.browser.LoadURL("https://www.google.com")

        # Split the window
        splitter.SplitVertically(left_panel, right_panel, screenSize[0] // 2)
        splitter.SetMinimumPaneSize(200)

        # Show the frame
        self.Show(True)

    def create_results_table(self, parent):
        # Results box
        results_box = wx.StaticBox(parent, label="Results")
        results_sizer = wx.StaticBoxSizer(results_box, wx.VERTICAL)

        # Create a grid and set its properties
        self.results_grid = gridlib.Grid(parent)
        self.results_grid.CreateGrid(0, 8)  # start with zero rows and 8 columns
        columns = ["ProfileLink", "FirstName", "LastName", "Email", "Phone", "Twitter", "Messenger", "TagLineTitle", "Summary"]
        for col_num, col_label in enumerate(columns):
            self.results_grid.SetColLabelValue(col_num, col_label)

        # Add the grid to the results sizer
        results_sizer.Add(self.results_grid, 1, wx.EXPAND | wx.ALL, 5)

        # Add the Results box to the main sizer
        self.left_main_sizer.Add(results_sizer, 1, wx.EXPAND | wx.ALL, 10)
        parent.SetSizer(self.left_main_sizer)
        
    def create_labeled_button(self, parent, label, bitmap_path):
        # Load the bitmap from an image file
        bitmap = wx.Bitmap(bitmap_path, wx.BITMAP_TYPE_ANY)
        button = wx.Button(parent, label=label)
        button.SetBitmap(bitmap, dir=wx.LEFT)  # set the image to the left of the text
        button.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL))  # set the font size
        return button

if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame(None, "My App")
    app.MainLoop()
