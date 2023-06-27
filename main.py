import os
import ctypes
import queue
import sys
import threading
import cv2
from tkinter import filedialog, RIGHT, CENTER, LEFT
from tktooltip import ToolTip
import customtkinter
from PIL import ImageTk, Image
import numpy as np
from datetime import datetime
from math import sqrt
from win10toast import ToastNotifier
import Languages.Languages_packs as L
import platform
import psutil
import win32api
import colorama
from colorama import Fore, Style

#
# @All rights Reserved to Ricardo Martins and João Marcos
#
colorama.init()
def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as error:
            import traceback
            tb = traceback.extract_tb(error.__traceback__)
            line = tb[-1].lineno
            error_message = f"An error occurred at {Fore.CYAN + Style.BRIGHT}line: {line}{Fore.RED} error: {error} {Style.RESET_ALL}"
            print(Fore.YELLOW + Style.BRIGHT + "\n" + error_message + "\n" + Style.RESET_ALL)
            with open("error_log.txt", "a") as file:
                file.write(error_message + "\n")
    return wrapper

@error_handler
def high_priority():
    # Constants for process priority classes
    HIGH_PRIORITY_CLASS = 0x00000080
    # Get the current process ID
    pid = os.getpid()
    # Open the current process with necessary access rights
    handle = ctypes.windll.kernel32.OpenProcess(
        ctypes.c_uint(0x1000),  # PROCESS_ALL_ACCESS
        ctypes.c_int(False),
        ctypes.c_uint(pid)
    )
    # Set the priority of the process to high
    ctypes.windll.kernel32.SetPriorityClass(handle, HIGH_PRIORITY_CLASS)
    # Close the handle
    ctypes.windll.kernel32.CloseHandle(handle)
high_priority()

@error_handler
def run_in_thread(func):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        thread.start()
    return wrapper

@error_handler
def read_config():
    from configparser import ConfigParser
    PATH = os.path.dirname(os.path.realpath(__file__))
    Config_File = os.path.join(PATH, L.Universal["Necessary Files Folder"], "config.ini")
    Config = ConfigParser()
    Config.read(Config_File)

    Language = Config["DEFAULTS"]["Language"]
    language_mapping = {
        "Pt-pt": (L.PT_pt, "Português-pt"),
        "English": (L.English, "English"),
        "German": (L.German, "Allemand"),
        "FR": (L.French, "Français"),
        "ES": (L.Spanish, "Espanõl")
        #"Pt-Br": (L.PT_br, "Português-br"),
    }
    SelectedLanguage, Option_lg_df = language_mapping.get(Language)

    Theme = Config["DEFAULTS"]["Theme"]
    match Theme:
        case "Green":
            Program_Theme = "green"
            Option_th_df = SelectedLanguage["Green"]
        case "Blue":
            Program_Theme = "blue"
            Option_th_df = SelectedLanguage["Blue"]
        case "Dark-Blue":
            Program_Theme = "dark-blue"
            Option_th_df = SelectedLanguage["Dark-Blue"]
        case "Red":
            Program_Theme = "Necessary files\\Red-Theme.json"
            Option_th_df = SelectedLanguage["Red"]
        case "Orange":
            Program_Theme = "Necessary files\\Orange-Theme.json"
            Option_th_df = SelectedLanguage["Orange"]

    Style = Config["DEFAULTS"]["style"]
    match Style:
        case "Dark":
            customtkinter.set_appearance_mode("dark")
        case "Light":
            customtkinter.set_appearance_mode("light")

    return PATH, Config, Config_File, SelectedLanguage, Option_th_df, Option_lg_df, Program_Theme

@error_handler
def get_gpu_info():
    gpu_name = win32api.EnumDisplayDevices(None, 0).DeviceString.strip()
    gpu_name = gpu_name.split(',')[0].strip("('")
    return gpu_name

@error_handler
def get_system_info():
    user = os.getlogin()
    user_pc = os.getenv("COMPUTERNAME")
    os_version = platform.version()
    os_edition = platform.win32_edition()
    architecture = platform.architecture()[0]
    ram = round(psutil.virtual_memory().total / (1024 ** 3), 0)  # RAM in GB
    processor = platform.processor()
    gpu = get_gpu_info()

    system_info = f"**User:** {user}\n**Pc:** {user_pc}\n**Windows Version:** {os_version}\n**Edition:** {os_edition}\n**Architecture:** {architecture}\n"
    system_info += f"**RAM:** {ram} GB\n"
    system_info += f"**Processor:** {processor}\n"
    system_info += f"**GPU:** {gpu}\n"
    system_info += "\n**-------------------------------------------------------------------**\n"

    return system_info

# Important variables
PATH, Config, Config_File, SelectedLanguage, Option_th_df, Option_lg_df, Program_Theme = read_config()
customtkinter.set_default_color_theme(Program_Theme)  # Themes: blue (default), dark-blue, green
image_extensions = r"*.jpg *.jpeg *.png"
#needed for stopping ctypes window duplication
thread_completed = threading.Event()
answer_queue = queue.Queue()
window_lock = threading.Lock()

# Mediapipe necessary points to find iris on image
LEFT_EYE =[362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385,384, 398]
RIGHT_EYE=[33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161 , 246] 
LEFT_IRIS = [474,475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]
count_imgs = []

# It takes an image, converts it to grayscale, applies an adaptive threshold to it, finds contours,
# and returns the contours that have an area greater than 2000
parameters = cv2.aruco.DetectorParameters_create()
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_50)
class HomogeneousBgDetector():
    def __init__(self):
        pass

    @error_handler
    def detect_objects(self, img):
        # Convert Image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Create a Mask with adaptive threshold
        mask = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 19, 5)
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #cv2.imshow("mask", mask)
        objects_contours = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 2000:
                #cnt = cv2.approxPolyDP(cnt, 0.03*cv2.arcLength(cnt, True), True)
                objects_contours.append(cnt)
        return objects_contours

# gets center of main monitor so it can later initialize the program on screen center instead of random location
@error_handler
def get_monitor_from_coord(x, y):
    import screeninfo
    monitors = screeninfo.get_monitors()

    for m in reversed(monitors):
        if m.x <= x <= m.width + m.x and m.y <= y <= m.height + m.y:
            return m
    return monitors[0]
detector = HomogeneousBgDetector()

@error_handler
class GUI(customtkinter.CTk):
    def __init__(self):
        # By using super().__init__(), the subclass can invoke the initializer of its superclass, 
        # allowing it to perform any necessary initialization steps defined in the superclass. 
        # This ensures that both the subclass-specific attributes and the superclass attributes are properly initialized.        super().__init__()
        super().__init__()
        # WINDOW SETTINGS
        WIDTH = 1280
        HEIGHT = 720
        self.toast = ToastNotifier()
        self.title("{} {}".format(L.Universal["Title"], L.Universal["Version"]))
        self.wm_iconbitmap("{}\\icon.ico".format(L.Universal["Necessary Files Folder"]))
        self.attributes('-topmost',True)
        self.minsize(WIDTH, HEIGHT)
        self.maxsize(1920, 1080)
        self.bind('<Escape>', lambda e: self.exit())
        current_screen = get_monitor_from_coord(self.winfo_x(), self.winfo_y())
        screen_width = current_screen.width
        screen_height = current_screen.height
        x_cord = int((screen_width / 2) - (WIDTH / 2))
        y_cord = int((screen_height / 2) - (HEIGHT / 2))
        self.geometry("{}x{}+{}+{}".format(WIDTH, HEIGHT, x_cord, y_cord))
        self.window = None
        self.MB_TOPMOST = 0x00040000
        self.window_opened = False
        
        
        # WINDOW SETTINGS #

        # VISUALS
        self.settings_img = ImageTk.PhotoImage(Image.open("{}/visuals1.png".format(L.Universal["Necessary Files Folder"])).resize((20, 20)))
        self.add_face_img = ImageTk.PhotoImage(Image.open("{}/visuals2.png".format(L.Universal["Necessary Files Folder"])).resize((20, 20)))
        self.bug_report_img = ImageTk.PhotoImage(Image.open("{}/visuals3.png".format(L.Universal["Necessary Files Folder"])).resize((20, 20)))
        self.tutorial_img = ImageTk.PhotoImage(Image.open("{}/visuals4.png".format(L.Universal["Necessary Files Folder"])).resize((20, 20)))
        self.save_img = ImageTk.PhotoImage(Image.open("{}/visuals5.png".format(L.Universal["Necessary Files Folder"])).resize((20, 20)))
        self.face_img = ImageTk.PhotoImage(Image.open("{}/visuals6.png".format(L.Universal["Necessary Files Folder"])).resize((20, 20)))
        self.glasses_img = ImageTk.PhotoImage(Image.open("{}/visuals7.png".format(L.Universal["Necessary Files Folder"])).resize((30, 15)))
        self.start_img = ImageTk.PhotoImage(Image.open("{}/visuals8.png".format(L.Universal["Necessary Files Folder"])).resize((20, 20)))
        self.folder_img = ImageTk.PhotoImage(Image.open("{}/visuals9.png".format(L.Universal["Necessary Files Folder"])).resize((20, 20)))
        self.icon_img = Image.open("{}/visuals10.png".format(L.Universal["Necessary Files Folder"])).resize((220, 100))
        self.about_img = ImageTk.PhotoImage(Image.open("{}/visuals11.png".format(L.Universal["Necessary Files Folder"])).resize((20, 20)))
        
        # VISUALS #
        
        # FRAMES
        # I have no idea which is which I knew when they were made, now only god knows.
        Frame1 = customtkinter.CTkFrame(self)
        Frame1.pack

        self.Frame2 = customtkinter.CTkFrame(self, 
                                                width=250, 
                                                height=725)
        self.Frame2.pack()
        self.Frame2.place(anchor="w", 
                            relx=0.0, 
                            rely=0.5, 
                            relwidth=0.2, 
                            relheight=1.1)

        self.Frame3 = customtkinter.CTkFrame(self, 
                                            width=250, 
                                            height=1)
        self.Frame3.pack(expand= True)
        self.Frame3.place(anchor="ne", 
                            relx=1, 
                            rely=0, 
                            relwidth=0.18, 
                            relheight=0.12)

        self.Frame4 = customtkinter.CTkFrame(self.Frame2, 
                                            width=200, 
                                            height=155)                    
        self.Frame4.pack(expand= True)
        self.Frame4.place(anchor="n", 
                            relx=0.5, 
                            rely=0, 
                            relwidth=1, 
                            relheight=0.261)
        self.attributes('-topmost',False)
        # FRAMES #

        # ICON
        self.icon_img = ImageTk.PhotoImage(self.icon_img)
        self.panel_icon = customtkinter.CTkLabel(self.Frame4, image=self.icon_img)
        self.panel_icon.place(relx=0.5, rely=0.52, anchor=CENTER)
        # ICON #
        
        # SETTINGS BUTTON
        self.settings_bt = customtkinter.CTkButton(self.Frame3, 
                                                    text=SelectedLanguage["Settings Button"],
                                                    image=self.settings_img,
                                                    compound=RIGHT,
                                                    command=self.settings)
        self.settings_bt.place(relx=0.5, rely=0.47, anchor=CENTER)
        self.tooltip(self.settings_bt, SelectedLanguage["Settings Button Tooltip"])
        # SETTINGS BUTTON #

        # SELECT FACE BUTTON
        self.button_get_Face = customtkinter.CTkButton(self.Frame2, 
                                                            width=200, 
                                                            height=50, 
                                                            border_width=0, 
                                                            corner_radius=8, 
                                                            hover=True, 
                                                            text=SelectedLanguage["Select Face Button"], 
                                                            command=self.browse_Face, 
                                                            image=self.face_img,
                                                            compound=RIGHT)
        self.button_get_Face.place(relx=0.5, rely=0.32, anchor=CENTER)
        self.tooltip(self.button_get_Face, SelectedLanguage["Select Face Button tooltip"])
        # SELECT FACE BUTTON #

        # ADD FACE BUTTON
        self.button_add_Face = customtkinter.CTkButton(self.Frame2, 
                                                            width=200, 
                                                            height=50, 
                                                            border_width=0, 
                                                            corner_radius=8, 
                                                            hover=True, 
                                                            text=SelectedLanguage["Add Faces Button"], 
                                                            command=self.add_faces, 
                                                            image=self.add_face_img,
                                                            compound=RIGHT, 
                                                            border_color=self.fg_color)
        self.button_add_Face.place(relx=0.5, rely=0.6, anchor=CENTER)
        self.tooltip(self.button_add_Face, SelectedLanguage["Add Faces Button Tooltip"])
        # ADD FACE BUTTON #

        # INPUT FRAME LENGTH 
        self.entry_comprimento = customtkinter.CTkEntry(self.Frame2, 
                                                        placeholder_text="mm")
        self.entry_comprimento.place(relx=0.5, rely=0.72, anchor=CENTER)
        self.tooltip(self.entry_comprimento, SelectedLanguage["Length Tooltip"])
        # INPUT FRAME LENGTH #

        # INPUT FRAME HEIGHT
        self.entry_altura = customtkinter.CTkEntry(self.Frame2, 
                                                    placeholder_text="mm")
        self.entry_altura.place(relx=0.5, rely=0.82, anchor=CENTER)
        self.tooltip(self.entry_altura, SelectedLanguage["Height Tooltip"])
        # INPUT FRAME HEIGHT #

        # INPUT FRAME LENGTH LABEL
        self.label_comprimento = customtkinter.CTkLabel(self.Frame2, 
                                                        text=SelectedLanguage["Length Label"])
        self.label_comprimento.place(relx=0.5, rely=0.67, anchor=CENTER)
        # INPUT FRAME LENGTH LABEL #
        
        # INPUT FRAME HEIGHT LABEL
        self.label_altura = customtkinter.CTkLabel(self.Frame2, 
                                                    text=SelectedLanguage["Height Label"])
        self.label_altura.place(relx=0.5, rely=0.77, anchor=CENTER)
        # INPUT FRAME HEIGHT LABEL #

        # SAVE MEASUREMENTS BUTTON
        self.button_medidas_oculos = customtkinter.CTkButton(self.Frame2, 
                                                                width=200, 
                                                                height=50, 
                                                                border_width=0, 
                                                                corner_radius=8, 
                                                                hover=True, 
                                                                text=SelectedLanguage["Save Measurements Button"], 
                                                                command=lambda:self.salvar(), 
                                                                image=self.save_img,
                                                                compound=RIGHT)
        self.button_medidas_oculos.place(relx=0.5, rely=0.9, anchor=CENTER)
        self.tooltip(self.button_medidas_oculos, SelectedLanguage["Save Measurements Button Tooltip"])
        # SAVE MEASUREMENTS BUTTON #

        self.open_results_bt = customtkinter.CTkButton(self.Frame2, 
                                                        width=200, 
                                                        height=50, 
                                                        border_width=0, 
                                                        corner_radius=8, 
                                                        hover=True, 
                                                        text=SelectedLanguage["Open Results Folder Button"], 
                                                        command=self.open_results, 
                                                        image=self.folder_img,
                                                        compound=RIGHT)
        self.open_results_bt.place(relx=0.5, rely=0.53, anchor=CENTER)
        self.tooltip(self.open_results_bt, SelectedLanguage["Open Results Folder Tooltip"])

        # PROGRESS BAR
        self.progressbar = customtkinter.CTkProgressBar(self.Frame4)
        
        # PROGRESS BAR #
    

    # SETTINGS WINDOW 
    @error_handler
    def closed_set_window(self):
        self.window.destroy()
        self.window = None
    
    @error_handler
    @run_in_thread
    def Warning_window(self, message, title, Options=False):
        # Acquire the lock to check and update the window status
        with window_lock:
            if self.window_opened:
                # Window is already open, so return immediately
                return
        self.window_opened = True
        if not Options:
            answer_queue.put(ctypes.windll.user32.MessageBoxW(0, message, title, self.MB_TOPMOST))
        else:
            answer_queue.put(ctypes.windll.user32.MessageBoxW(0, message, title, 1 | self.MB_TOPMOST))
        with window_lock:
            self.window_opened = False
            thread_completed.set()

        
    @error_handler
    def settings(self): 
        if self.window != None:
            self.window.lift()
            self.toast.show_toast(
                "Optica",
                f'{SelectedLanguage["Duplicate Window"]}',
                duration = 2,
                icon_path = "icon.ico",
                threaded = True,
            )
            return
        self.window = customtkinter.CTkToplevel(self)
        Width = 420
        Height = 240
        self.window.title(SelectedLanguage["Settings Button"])
        self.window.wm_iconbitmap(f"{L.Universal['Necessary Files Folder']}\\icon.ico")
        self.window.attributes('-topmost',True)
        self.window.attributes('-topmost',False)
        self.window.minsize(420, 200)
        self.window.maxsize(420, 200)
        self.window.protocol("WM_DELETE_WINDOW", self.closed_set_window)
        self.window.bind('<Escape>',lambda e: self.close_settings())
        current_screen = get_monitor_from_coord(self.window.winfo_x(), self.window.winfo_y())
        screen_width = current_screen.width
        screen_height = current_screen.height
        x_cord = int((screen_width / 2) - (Width / 2))
        y_cord = int((screen_height / 2) - (Height / 2))
        self.window.geometry("{}x{}+{}+{}".format(Width, Height, x_cord, y_cord))

        self.switch = customtkinter.CTkSwitch(master=self.window, 
                                                text=SelectedLanguage["Theme Switch"], 
                                                command=self.style_change,)
        self.switch.place(relx=0.12, rely=0.65)
        if Config["DEFAULTS"]["style"] == "Dark":
            self.switch.select()
        else:
            self.switch.deselect()
        self.tooltip(self.switch, SelectedLanguage["Theme Switch Tooltip"])
        self.report = customtkinter.CTkButton(self.window, 
                                                    width=150, 
                                                    height=25, 
                                                    border_width=0, 
                                                    corner_radius=8, 
                                                    hover=True, 
                                                    text=SelectedLanguage["Report Bug Button"], 
                                                    command=self.report_command, 
                                                    image=self.bug_report_img,
                                                    compound=RIGHT)
        self.report.place(relx=0.05, rely=0.3, anchor="w")
        self.tooltip(self.report, SelectedLanguage["Report Bug Button Tooltip"])

        self.about_bt = customtkinter.CTkButton(self.window, 
                                                    width=150, 
                                                    height=25, 
                                                    border_width=0, 
                                                    corner_radius=8, 
                                                    hover=True, 
                                                    text=SelectedLanguage["About Button"], 
                                                    command=self.about, 
                                                    image=self.about_img,
                                                    compound=RIGHT)
        self.about_bt.place(relx=0.05, rely=0.45, anchor="w")
        self.tooltip(self.about_bt, SelectedLanguage["About Button Tooltip"])

        self.button_get_tutorial = customtkinter.CTkButton(self.window, 
                                                                width=150, 
                                                                height=25, 
                                                                border_width=0, 
                                                                corner_radius=8, 
                                                                hover=True, 
                                                                text=SelectedLanguage["Tutorial Button"], 
                                                                command=self.tutorial, 
                                                                image=self.tutorial_img,
                                                                compound=RIGHT)
        self.button_get_tutorial.place(anchor="w", rely = 0.15, relx=0.05)
        self.tooltip(self.button_get_tutorial, SelectedLanguage["Tutorial Button Tooltip"])

        
        self.Optionmenu = customtkinter.CTkOptionMenu(self.window,
                                                    values=["Português-pt", "English", "Español", "Français", "Allemand"],
                                                    command=self.change_language,
                                                    hover=True)
        self.Optionmenu.place(relx=0.95, rely=0.16, anchor="e")
        self.Optionmenu.set(Option_lg_df)
        self.tooltip(self.Optionmenu, SelectedLanguage["Language Tooltip"])

        self.OptionmenuTheme = customtkinter.CTkOptionMenu(self.window,
                                                    values=[SelectedLanguage["Green"], SelectedLanguage["Blue"], SelectedLanguage["Dark-Blue"], SelectedLanguage["Red"], SelectedLanguage["Orange"]],
                                                    command=self.change_theme,
                                                    hover=True)
        self.OptionmenuTheme.place(relx=0.95, rely=0.45, anchor="e")
        self.OptionmenuTheme.set(Option_th_df)
        self.tooltip(self.OptionmenuTheme, SelectedLanguage["Color Theme Tooltip"])

    @error_handler
    def change_language(self, choice):
        choice = self.Optionmenu.get()
        language_mapping = {
            "Português-pt": "Pt-pt",
            "English": "English",
            "Español": "ES",
            "Français": "FR",
            "Allemand": "German"
            # Add other language mappings here
        }
        language = language_mapping.get(choice)
        Config.set("DEFAULTS", "Language", language)
        with open(Config_File, "w") as f:
            Config.write(f)
        self.restart_program()

    @error_handler
    def change_theme(self, choice):
        choice = self.OptionmenuTheme.get()
        #Set color options to selected language
        theme_mapping = {
            SelectedLanguage["Green"]: "Green",
            SelectedLanguage["Blue"]: "Blue",
            SelectedLanguage["Dark-Blue"]: "Dark-Blue",
            SelectedLanguage["Red"]: "Red",
            SelectedLanguage["Orange"]: "Orange"
        }
        
        Config.set("DEFAULTS", "Theme", theme_mapping[choice])
        with open(Config_File, "w") as f:
            Config.write(f)
        self.restart_program()

    @error_handler
    def restart_program(self):
        self.Warning_window(SelectedLanguage["Restart"], SelectedLanguage["Restart title"], True)
        thread_completed.wait()
        answer = answer_queue.get()
        if answer == 1:
            python = sys.executable
            print(python)
            os.execl(python, python, *sys.argv)

    @error_handler
    def close_settings(self):
        self.window.destroy()
        self.window = None

        # SETTINGS WINDOW #


    @error_handler
    @run_in_thread
    def exit(self):
        self.Warning_window(SelectedLanguage["Exit Window"], SelectedLanguage["Exit Window Title"], True)
        thread_completed.wait()
        answer = answer_queue.get()
        if answer == 1:
            #self.destroy()
            self.quit()
            sys.exit()

    @error_handler
    def style_change(self):
        selected_style = "Light" if self.switch.get() == 0 else "Dark"
        customtkinter.set_appearance_mode(selected_style)
        Config.set("DEFAULTS", "Style", selected_style)
        with open(Config_File, "w") as f:
            Config.write(f)

    @error_handler
    def report_command(self):
        try:
            import webbrowser
            url='https://forms.gle/n17W4q7ScDFCoEQT6'
            webbrowser.open(url)
        except Exception as error:
                error = str(error)
                self.send_errors_discord(error)
                self.Warning_window(SelectedLanguage["Report Bug Error Window"], SelectedLanguage["Error Window Title"])

    @error_handler
    def tooltip(self, bt, mensg):
        ToolTip(bt, 
                    msg=mensg, 
                    delay=0.5, 
                    follow=True, 
                    parent_kwargs={"bg": "black", "padx": 5, "pady": 5},
                    fg="#ffffff", 
                    bg="#1c1c1c",
                    padx=10, 
                    pady=10)
        
    @error_handler
    def add_faces(self):
        try:
            os.startfile("{}\\{}".format(PATH, L.Universal["Faces Folder"]))
            self.toast.show_toast(
                "Optica",
                f'{SelectedLanguage["Add Faces Toast notification"]}',
                duration = 15,
                icon_path = "icon.ico",
                threaded = True,
            )
        except Exception as error:
            self.send_errors_discord(error)
            self.Warning_window(SelectedLanguage["Open Faces Folder Error"], SelectedLanguage["Error Window Title"])

    @error_handler
    def open_results(self):
        try:
            os.startfile("{}\\{}".format(PATH, L.Universal["Ready Images Folder"]))
        except Exception as error:
            self.Warning_window(SelectedLanguage["Open Results Folder Error"], SelectedLanguage["Error Window Title"])
            self.send_errors_discord(error)
            
    @error_handler
    @run_in_thread
    def about(self):
        self.Warning_window(SelectedLanguage["About Window Info"], SelectedLanguage["About Window Title"])

    @error_handler
    def browse_Face(self):
        if os.path.exists(L.Universal["Faces Folder"]):
            self.Face_path = filedialog.askopenfilename(title=SelectedLanguage["Browse Face Window Title"], 
                                                                                    initialdir = L.Universal["Faces Folder"], 
                                                                                    filetypes=[(SelectedLanguage["Browse Window Hint"], 
                                                                                    image_extensions)])
        else:
           self.Face_path = filedialog.askopenfilename(title=SelectedLanguage["Browse Face Window Title"], 
                                                                                    filetypes=[(SelectedLanguage["Browse Window Hint"], 
                                                                                    image_extensions)]) 
        #image
        if os.path.isfile(self.Face_path):
            self.Face_image = Image.open(self.Face_path)
            self.Face_image = self.Face_image.resize((250, 250), Image.Resampling.LANCZOS)
            self.Face_image = ImageTk.PhotoImage(self.Face_image)
            self.panel_Face = customtkinter.CTkLabel(image=self.Face_image)
            self.panel_Face.place(relx=0.33, rely=0.45, anchor=CENTER)
        #button
            self.button_get_Oculos = customtkinter.CTkButton(self.Frame2, 
                                                                width=200, 
                                                                height=50, 
                                                                border_width=0, 
                                                                corner_radius=8, 
                                                                hover=True, 
                                                                text=SelectedLanguage["Select Glasses Button"], 
                                                                command=self.browse_Oculos, 
                                                                image=self.glasses_img,
                                                                compound=RIGHT)
            self.button_get_Oculos.place(relx=0.5, rely=0.39, anchor=CENTER)
            self.tooltip(self.button_get_Oculos, SelectedLanguage["Select Glasses Button Tooltip"])

    @error_handler
    def open_faces_folder():
        os.open(L.Universal["Faces Folder"])

    @error_handler
    def browse_Oculos(self):
        if os.path.exists(L.Universal["Glasses Folder"]):
            self.Oculos_path = filedialog.askopenfilename(title=SelectedLanguage["Browse Glasses Window Title"],
                                                                initialdir = L.Universal["Glasses Folder"], 
                                                                filetypes=[(SelectedLanguage["Browse Window Hint"], 
                                                                image_extensions)])
            if not os.path.isfile(self.Oculos_path):
                # Fixes a annoying error
                self.Oculos_path_saved = self.Oculos_path_saved
            else:
                self.Oculos_path_saved = self.Oculos_path
        else:
            self.Oculos_path = filedialog.askopenfilename(title=SelectedLanguage["Browse Glasses Window Title"], 
                                                                filetypes=[(SelectedLanguage["Browse Window Hint"], 
                                                                image_extensions)])
            if not os.path.isfile(self.Oculos_path):
                self.Oculos_path_saved = self.Oculos_path_saved
            else:
                self.Oculos_path_saved = self.Oculos_path
        #image
        if os.path.isfile(self.Oculos_path):
            self.Oculos_image = Image.open(self.Oculos_path)
            self.Oculos_image = self.Oculos_image.resize((700, 250), Image.Resampling.LANCZOS)
            self.Oculos_image = ImageTk.PhotoImage(self.Oculos_image)
            self.panel_Oculos = customtkinter.CTkLabel(image=self.Oculos_image)
            self.panel_Oculos.place(relx=0.73, rely=0.45, anchor=CENTER)
        #button
            self.button_Start = customtkinter.CTkButton(self.Frame2, 
                                                            width=200, 
                                                            height=50, 
                                                            border_width=0, 
                                                            corner_radius=8, 
                                                            hover=True, 
                                                            text=SelectedLanguage["Start Button"], 
                                                            command=lambda:self.get_object_size(self.Face_path), 
                                                            image=self.start_img,
                                                            compound=RIGHT)
            self.button_Start.place(relx=0.5, rely=0.46, anchor=CENTER)
            self.tooltip(self.button_Start, SelectedLanguage["Start Button Tooltip"])

    @error_handler
    def tutorial(self):
        try:
            os.startfile("{}\\tutorial.mp4".format(L.Universal["Necessary Files Folder"]))
        except Exception as error:
            error = str(error)
            self.send_errors_discord(error)
            self.Warning_window(SelectedLanguage["Tutorial Open Error Window"], SelectedLanguage["Error Window Title"])
    
    @error_handler
    @run_in_thread
    def draw_on_img(self, img):
        try:
            cv2.circle(img, self.center_left, int(self.l_radius), (255,0,255), 2, cv2.LINE_AA)
            cv2.circle(img, self.center_right, int(self.r_radius), (255,0,255), 2, cv2.LINE_AA)
            cv2.line(img, (self.nose_point_for_dnp_X, self.nose_point_for_dnp_Y), self.center_left, (0, 255, 0), 1)
            cv2.line(img, (self.nose_point_for_dnp_X, self.nose_point_for_dnp_Y), self.center_right, (0, 255, 0), 1)
            cv2.line(img, (self.left_face_x, self.left_face_y), (self.right_face_x, self.right_face_y), (255, 0, 0), 1)
            cv2.line(img, self.center_right, self.center_left, (0, 0, 255), 1)
            cv2.rectangle(img, (10, self.imy - 265), (self.imx, self.imy), (0, 0, 0), 350, cv2.FILLED)
            cv2.putText(img, SelectedLanguage["Pupillary Distance"] + f"{round(self.iris_to_iris_line_distance, 2)} mm", (10, self.imy - 5), cv2.FONT_HERSHEY_DUPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(img, SelectedLanguage["Left Nasopupillary distance"] + f"{round(self.dnp_left, 2)} mm", (10, self.imy - 55), cv2.FONT_HERSHEY_DUPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(img, SelectedLanguage["Right Nasopupillary distance"] + f"{round(self.dnp_right, 2)} mm", (10, self.imy - 105), cv2.FONT_HERSHEY_DUPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(img, SelectedLanguage["Face Length"] + f"{round(self.left_to_right_face, 2)} mm", (10, self.imy - 155), cv2.FONT_HERSHEY_DUPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(img, SelectedLanguage["Right eye"], (self.bmx, self.bmy), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, cv2.LINE_AA)
            cv2.putText(img, SelectedLanguage["Left eye"], (self.bmlx, self.bmly), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, cv2.LINE_AA)
            self.medidas_label = customtkinter.CTkLabel(self, text=SelectedLanguage["Pupillary Distance"] + f"{round(self.iris_to_iris_line_distance, 2)} mm\n" + SelectedLanguage["Left Nasopupillary distance"] + f"{round(self.minleft, 2)} mm\n" + SelectedLanguage["Right Nasopupillary distance"] + f"{round(self.minright, 2)} mm\n" + SelectedLanguage["Face Length"] + f"{round(self.left_to_right_face, 2)} mm\n" + SelectedLanguage["Right Height"] + f"{round(self.right_iris_Oculos, 2)} mm\n" + SelectedLanguage["Left Height"] + f"{round(self.left_iris_Oculos, 2)} mm")
            self.medidas_label.configure(font=("Courier", 18, "bold"), anchor="w", justify=LEFT)
            self.medidas_label.place(relx= 0.2, rely=0.67)
        except Exception as error:
            self.send_errors_discord(error,)

    @error_handler
    def get_point(self, x, y, width_original, height_original, width_res, height_res): # used to get a point (x,y) from a rescaled image
        x_transforming_ratio = x / width_original # its a ratio to get from the old x point (non rescaled image) to the new x point on the rescaled img
        y_transforming_ratio = y / height_original # that but for the Y point
        self.x = int(width_res * x_transforming_ratio) # variable of the resized x
        self.y = int(height_res * y_transforming_ratio) # that but for the y point

    @error_handler
    def put_glasses(self, ImageInput=None): #function to put glasses on the face
        img_path = "{}\\{}\\{}--{}.png".format(PATH, L.Universal["Ready Images Folder"], SelectedLanguage["Measurements Image"], self.t_stamp)
        img = Image.open(img_path) if ImageInput is None else ImageInput
        width_pic = int(img.size[0]) # gets the original picture width
        height_pic = int(img.size[1]) # gets the original picture height
        mask_Oculos = Image.open(self.Oculos_path) # opens the Oculos image
        width_oculos_original = int(mask_Oculos.size[0]) # gets the glasses image's width
        height_oculos_original = int(mask_Oculos.size[1]) # same but for the height
        #print(height_oculos_original)
        self.width_Oculos = int(self.comprimento * self.pixel_mm_ratio) # sets the width of the Oculos image to be the same as the distance between 2 points of the face
        mask_Oculos = mask_Oculos.resize((self.width_Oculos, int(self.altura * self.pixel_mm_ratio))) # resizes the glasses to the correct width.
        width_oculos_resized = int(mask_Oculos.size[0]) # gets the resized size of the width
        height_oculos_resized = int(mask_Oculos.size[1]) # same but height
        #print(height_oculos_resized)

        mask_Oculos.save("temp.png") # temp img to be used later, former "slave.png" <-- joão marcos
        if self.Oculos_path.endswith("Oculos2.png"): # all these ifs verify which glasses where chosen and define the coordinates to be put on the face
            self.get_point(430,69,width_oculos_original, height_oculos_original, width_oculos_resized, height_oculos_resized)
            x = self.nose_x - self.x
            y = self.nose_y - self.y
            self.get_point(245,278,width_oculos_original, height_oculos_original, width_oculos_resized, height_oculos_resized)
            right_iris_x = self.x + x
            right_iris_y = self.y + y
            self.get_point(612,279,width_oculos_original, height_oculos_original, width_oculos_resized, height_oculos_resized)
            left_iris_x = self.x + x
            left_iris_y = self.y + y
        elif self.Oculos_path.endswith("Oculos1.png"):
            self.get_point(453,26,width_oculos_original, height_oculos_original, width_oculos_resized, height_oculos_resized)
            x = self.nose_x - self.x
            y = self.nose_y - self.y
            self.get_point(226,236,width_oculos_original, height_oculos_original, width_oculos_resized, height_oculos_resized)
            right_iris_x = self.x + x
            right_iris_y = self.y + y
            self.get_point(700,230,width_oculos_original, height_oculos_original, width_oculos_resized, height_oculos_resized)
            left_iris_x = self.x + x
            left_iris_y = self.y + y
        elif self.Oculos_path.endswith("Oculos3.png"):
            self.get_point(667,121,width_oculos_original, height_oculos_original, width_oculos_resized, height_oculos_resized)
            x = self.nose_x - self.x
            y = self.nose_y - self.y
            self.get_point(334,397,width_oculos_original, height_oculos_original, width_oculos_resized, height_oculos_resized)
            right_iris_x = self.x + x
            right_iris_y = self.y + y
            self.get_point(974,400,width_oculos_original, height_oculos_original, width_oculos_resized, height_oculos_resized)
            left_iris_x = self.x + x
            left_iris_y = self.y + y
        elif self.Oculos_path.endswith("Oculos7.png"):
            self.get_point(465,117,width_oculos_original, height_oculos_original, width_oculos_resized, height_oculos_resized)
            x = self.nose_x - self.x
            y = self.nose_y - self.y
            self.get_point(255,323,width_oculos_original, height_oculos_original, width_oculos_resized, height_oculos_resized)
            right_iris_x = self.x + x
            right_iris_y = self.y + y
            self.get_point(671,319,width_oculos_original, height_oculos_original, width_oculos_resized, height_oculos_resized)
            left_iris_x = self.x + x
            left_iris_y = self.y + y
        elif self.Oculos_path.endswith("Oculos9.png"):
            self.get_point(353,83,width_oculos_original, height_oculos_original, width_oculos_resized, height_oculos_resized)
            x = self.nose_x - self.x
            y = self.nose_y - self.y
            self.get_point(190,247,width_oculos_original, height_oculos_original, width_oculos_resized, height_oculos_resized)
            right_iris_x = self.x + x
            right_iris_y = self.y + y
            self.get_point(528,249,width_oculos_original, height_oculos_original, width_oculos_resized, height_oculos_resized)
            left_iris_x = self.x + x
            left_iris_y = self.y + y
        
        r_iris_glasses = (sqrt((self.r_cx - right_iris_x)**2 + (self.r_cy - right_iris_y)**2)) / self.pixel_mm_ratio # measurement of the r ALT
        l_iris_glasses = (sqrt((self.l_cx - left_iris_x)**2 + (self.l_cy - left_iris_y)**2)) / self.pixel_mm_ratio # l ALT
        cv2.line(self.img, (right_iris_x, right_iris_y), (int(self.r_cx), int(self.r_cy)), (0,0,0), 1, cv2.LINE_AA)
        cv2.line(self.img, (left_iris_x, left_iris_y), (int(self.l_cx), int(self.l_cy)), (0,0,0), 1, cv2.LINE_AA)
        cv2.putText(self.img, SelectedLanguage["Right Height"] + f"{round(r_iris_glasses, 2)} mm", (10, self.imy - 205), cv2.FONT_HERSHEY_DUPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        cv2.putText(self.img, SelectedLanguage["Left Height"] + f"{round(l_iris_glasses, 2)} mm", (10, self.imy - 255), cv2.FONT_HERSHEY_DUPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        cv2.imwrite("temp.png", self.img)
        Oculos_img = Image.new('RGBA', (width_pic,height_pic), (0, 0, 0, 0)) # creates a blank image same size as the original
        Oculos_img.paste(img, (0,0)) # pastes the original on the blank 
        Oculos_img.paste(mask_Oculos, (x, y), mask=mask_Oculos) # pastes the Oculos over the original over the blank
        Oculos_img.save("{}/{}-{}.png".format(L.Universal["Ready Images Folder"], SelectedLanguage["Image With Glasses"], self.t_stamp))
        self.toast.show_toast(
                "Optica",
                SelectedLanguage["Done Toast Notification"],
                duration = 5,
                icon_path = "icon.ico",
                threaded = True,
            )

    @error_handler
    @run_in_thread
    def send_errors_discord(self, error):
        try:
            from discord_webhook import DiscordWebhook, DiscordEmbed
            system_info = get_system_info()
            error = str(f"{system_info}\n" + "**ERROR**:\n" + f'**__{error}__**')  # Replace the error message with the actual error
            embed = DiscordEmbed(title='Data', description=error, color='ff0000')
            embed.set_timestamp()
            webhook = DiscordWebhook(url='https://discord.com/api/webhooks/979917471878381619/R4jt6PLLlnxsuGXbeRm1wokotX4IjqQj3PbC2JqFlP7-4koEATZ3jqA_fVI_T7UXqaXe')
            webhook.add_embed(embed)
            response = webhook.execute()
        except Exception:
            pass
       

    @error_handler
    def salvar(self):
        try:
            self.comprimento = float(self.entry_comprimento.get())
            self.altura = float(self.entry_altura.get())
            if self.comprimento not in range(100,250) or self.altura not in range(20, 100):
                self.Warning_window(SelectedLanguage["Save  Measurements Error"], SelectedLanguage["Error Window Title"])
                self.toast.show_toast(
                "Optica",
                SelectedLanguage["Save Measurements Error Notification"],
                duration = 10,
                icon_path = "icon.ico",
                threaded = True,
                )
                return

            self.toast.show_toast(
            "Optica",
            "{}\n{}{}\n{}{}".format(SelectedLanguage["Save Measurements Success Tooltip"], SelectedLanguage["Length"], self.comprimento, SelectedLanguage["Height"], self.altura),
            duration = 5,
            icon_path = "icon.ico",
            threaded = True,
            )
        except Exception as error:
            error = str(error)
            self.send_errors_discord(error)
            self.Warning_window(SelectedLanguage["Save Measurements Error Notification"], SelectedLanguage["Error Window Title"])

    @error_handler
    @run_in_thread
    def get_object_size(self, image):
        try:
            if self.comprimento not in range(100,250) or self.altura not in range(20, 100):
                self.Warning_window(SelectedLanguage["Get Object Size Error"], SelectedLanguage["Error Window Title"])
                return
            # para o caso de haver muitas imagens assim ficam todas com o nome na ordem que foram processadas
            self.progressbar.place(relx=0.1, rely= 0.9)
            self.progressbar.determinate_speed = 0.3
            self.progressbar.set(0)
            import mediapipe
            self.progressbar.start()
            self.mp_face_mesh = mediapipe.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(static_image_mode=True, refine_landmarks=True, min_detection_confidence=0.5)
            try:
                self.image = image
                img = cv2.imread(image)
                # ir buscar o aruco marker
                corners, _, _ = cv2.aruco.detectMarkers(img, aruco_dict, parameters=parameters)
                int_corners = np.int0(corners)
                # desenhamos linhas verdes a volta do aruco marker sabendo que ele tem um perímetro de 20cm
                cv2.polylines(img, int_corners, True, (0, 255, 0), 5)
                # perímetro do aruco
                # funciona com apenas 1 aruco marker
                self.aruco_perimeter = cv2.arcLength(corners[0], True)
                # Pixel to mm ratio
                self.pixel_mm_ratio = self.aruco_perimeter / 200
            except Exception as error:
                error = str(error)
                self.send_errors_discord(error)
                self.Warning_window(SelectedLanguage["Aruco Marker Not detected"], SelectedLanguage["Error Window Title"])

            try:
                self.img = cv2.imread(image)
                self.imy, self.imx, _ = self.img.shape
                # opens the image with pil to put them Oculos on
                # é necessário converter a imagem de Blue green red para Red green blue
                rgb_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
                # tamanho da imagem
                height, width, _ = self.img.shape
                result = self.face_mesh.process(rgb_img)
                for facial_landmarks in result.multi_face_landmarks:
                    middle_nose = facial_landmarks.landmark[168]
                    middle_nose_bottom = facial_landmarks.landmark[8]
                    more_points_bottom_nose = facial_landmarks.landmark[197]
                    bottom_nose = facial_landmarks.landmark[6]
                    left_face = facial_landmarks.landmark[127] 
                    right_face = facial_landmarks.landmark[356] 
                    right_face2 = facial_landmarks.landmark[251]
                    left_face2 = facial_landmarks.landmark[21]
                    bottom_Oculos = facial_landmarks.landmark[101]
                    top_Oculos = facial_landmarks.landmark[66]
                    bottom_bottom = facial_landmarks.landmark[111]
                    bottom_b_left = facial_landmarks.landmark[330]
                    bottom_g_left = facial_landmarks.landmark[419]
                    # coordenadas não podem ser floats
                    # pontos necessários
                    self.bottom_x = int(more_points_bottom_nose.x * width)
                    self.bottom_y = int(more_points_bottom_nose.y * height)
                    self.bottom_nose_x = int(bottom_nose.x * width)
                    self.bottom_nose_y = int(bottom_nose.y * height)
                    self.middle_nose_bottom_x = int(middle_nose_bottom.x * width) #middle nose bottom "x"
                    self.middle_nose_bottom_y = int(middle_nose_bottom.y * height) #middle nose bottom "y"
                    self.nose_x = int(middle_nose.x * width) #nose "x"
                    self.nose_y = int(middle_nose.y * height) #nose "y"
                    self.left_face_x = int(left_face.x * width) #left face "x"
                    self.left_face_y = int(left_face.y * height) #Left face "y"
                    self.right_face_x = int(right_face.x * width) #right face "x"
                    self.right_face_y = int(right_face.y * height) #right face "y"
                    self.left_face_x1 = int(left_face2.x * width)
                    self.left_face_y1 = int(left_face2.y * height)
                    self.right_face_x1 = int(right_face2.x * width)
                    self.right_face_y1 = int(right_face2.y * height)
                    self.bottom_glasses_x = int(bottom_Oculos.x * width)
                    self.bottom_glasses_y = int(bottom_Oculos.y * height)
                    self.bottom_bottom_x = int(bottom_bottom.x * width)
                    self.bottom_bottom_y = int(bottom_bottom.y * height)
                    self.bottom_glasses_left_x = int(bottom_g_left.x * width)
                    self.bottom_glasses_left_y = int(bottom_g_left.y * height)
                    self.bblx = int(bottom_b_left.x * width)
                    self.bbly = int(bottom_b_left.y * height)
                    self.tgx = int(top_Oculos.x * width)
                    self.tgy = int(top_Oculos.y * height)
                    self.bmx = int((self.bottom_bottom_x + self.bottom_glasses_x) / 2)
                    self.bmy = int((self.bottom_bottom_y + self.bottom_glasses_y) / 2)
                    self.bmlx = int((self.bblx + self.bottom_glasses_left_x) / 2)
                    self.bmly = int((self.bbly + self.bottom_glasses_left_y) / 2)
                    self.midpoint_nose_x = int((self.middle_nose_bottom_x + self.nose_x) / 2)
                    self.midpoint_nose_y = int((self.middle_nose_bottom_y + self.nose_y) / 2)
                    self.mid_nose_x = int((self.bottom_nose_x + self.nose_x) / 2)
                    self.mid_nose_y = int((self.bottom_nose_y + self.nose_y) / 2)
                    self.mid_mid_bottom_x = int((self.bottom_nose_x + self.mid_nose_x) / 2)
                    self.mid_mid_bottom_y = int((self.bottom_nose_y + self.mid_nose_y) / 2)
                    self.mid_mid_top_x = int((self.nose_x + self.mid_nose_x) / 2)
                    self.mid_mid_top_y = int((self.nose_y + self.mid_nose_y) / 2)
                    self.midier_nose_x = int((self.mid_mid_top_x + self.mid_nose_x) / 2)
                    self.midier_nose_y = int((self.mid_mid_top_y + self.mid_nose_y) / 2)
                    self.mid_more_points_x = int((self.bottom_nose_x + self.bottom_x) / 2)
                    self.mid_more_points_y = int((self.bottom_nose_y + self.bottom_y) / 2)
                    self.mid_mid_mid_bottom_x = int((self.bottom_nose_x + self.mid_mid_bottom_x) / 2)
                    self.mid_mid_mid_bottom_y = int((self.bottom_nose_y + self.mid_mid_bottom_y) / 2)
                    self.mid_medium_mid_x = int((self.mid_nose_x + self.mid_mid_bottom_x) / 2)
                    self.mid_medium_mid_y = int((self.mid_nose_y + self.mid_mid_bottom_y) / 2)
                    self.mid_midier_top_x = int((self.midier_nose_x + self.mid_mid_top_x) / 2)
                    self.mid_midier_top_y = int((self.midier_nose_y + self.mid_mid_top_y) / 2)
                    self.mid_midier_bottom_x = int((self.midier_nose_x + self.mid_nose_x) / 2)
                    self.mid_midier_bottom_y = int((self.midier_nose_y + self.mid_nose_y) / 2)
                    self.mid_medium_nose_x = int((self.mid_medium_mid_x + self.mid_nose_x) / 2)
                    self.mid_medium_nose_y = int((self.mid_medium_mid_y + self.mid_nose_y) / 2)
                    self.mid_medium_bottom_x = int((self.mid_medium_mid_x + self.mid_mid_bottom_x) / 2)
                    self.mid_medium_bottom_y = int((self.mid_medium_mid_y + self.mid_mid_bottom_y) / 2)
                    self.mid_x = int((self.mid_mid_mid_bottom_x + self.mid_mid_bottom_x) / 2)
                    self.mid_y = int((self.mid_mid_mid_bottom_y + self.mid_mid_bottom_y) / 2)
                    self.mid2_x = int((self.mid_mid_mid_bottom_x + self.bottom_nose_x) / 2)
                    self.mid2_y = int((self.mid_mid_mid_bottom_y + self.bottom_nose_y) / 2)
                    self.mid3_x = int((self.mid_more_points_x + self.bottom_nose_x) / 2)
                    self.mid3_y = int((self.mid_more_points_y + self.bottom_nose_y) / 2)
                    self.mid4_x = int((self.mid3_x + self.bottom_nose_x) / 2)
                    self.mid4_y = int((self.mid3_y + self.bottom_nose_y) / 2)
                    self.mid5_x = int((self.mid4_x + self.bottom_nose_x) / 2)
                    self.mid5_y = int((self.mid4_y + self.bottom_nose_y) / 2)
                    self.mid6_x = int((self.mid4_x + self.mid3_x) / 2)
                    self.mid6_y = int((self.mid4_y + self.mid3_y) / 2)
                    self.mid7_x = int((self.mid_more_points_x + self.mid3_x) / 2)
                    self.mid7_y = int((self.mid_more_points_y + self.mid3_y) / 2)
                    self.mid8_x = int((self.mid7_x + self.mid3_x) / 2)
                    self.mid8_y = int((self.mid7_y + self.mid3_y) / 2)
                    self.mid9_x = int((self.mid7_x + self.mid_more_points_x) / 2)
                    self.mid9_y = int((self.mid7_y + self.mid_more_points_y) / 2)
                    self.mid10_x = int((self.bottom_x + self.mid_more_points_x) / 2)
                    self.mid10_y = int((self.bottom_y + self.mid_more_points_y) / 2)
                    self.mid11_x = int((self.nose_x + self.mid_mid_top_x) / 2)
                    self.mid11_y = int((self.nose_y + self.mid_mid_top_y) / 2)
                    self.mesh_points = np.array([np.multiply([p.x, p.y], [width, height]).astype(int) for p in result.multi_face_landmarks[0].landmark])
                    # x do circulo esquerdo/ y do ... raio do ...
                    (self.l_cx, self.l_cy), self.l_radius = cv2.minEnclosingCircle(self.mesh_points[LEFT_IRIS])
                    # x do circulo direito/ y do ... raio do ...
                    (self.r_cx, self.r_cy), self.r_radius = cv2.minEnclosingCircle(self.mesh_points[RIGHT_IRIS])
                    #distancias
                    self.iris_to_iris_line_distance = (sqrt((self.r_cx - self.l_cx)**2 + (self.r_cy - self.l_cy)**2)) / self.pixel_mm_ratio
                    self.left_iris_to_nose = (sqrt((self.l_cx - self.nose_x)**2 + (self.l_cy - self.nose_y)**2)) / self.pixel_mm_ratio
                    self.right_iris_to_nose = (sqrt((self.r_cx - self.nose_x)**2 + (self.r_cy - self.nose_y)**2)) / self.pixel_mm_ratio
                    self.left_to_right_face = (sqrt((self.left_face_x - self.right_face_x)**2 + (self.left_face_y - self.right_face_y)**2)) / self.pixel_mm_ratio
                    self.right_iris_Oculos = round((sqrt((self.r_cx - self.bmx)**2 + (self.r_cy - self.bmy)**2)) / self.pixel_mm_ratio, 2)
                    self.left_iris_Oculos = round((sqrt((self.l_cx - self.bmlx)**2 + (self.l_cy - self.bmly)**2)) / self.pixel_mm_ratio, 2)
                    self.center_left = np.array([self.l_cx, self.l_cy], dtype=np.int32)
                    self.center_right = np.array([self.r_cx, self.r_cy], dtype=np.int32)
                    right_iris_nose = []
                    left_iris_nose = []
                    iris_nose_points_x = [self.nose_x,
                                            self.mid_nose_x,
                                            self.mid_mid_bottom_x,
                                            self.mid_mid_top_x,
                                            self.bottom_nose_x,
                                            self.mid_more_points_x,
                                            self.midier_nose_x,
                                            self.mid_mid_mid_bottom_x,
                                            self.mid_medium_mid_x,
                                            self.mid_midier_top_x,
                                            self.mid_midier_bottom_x,
                                            self.mid_medium_nose_x,
                                            self.mid_medium_bottom_x,
                                            self.mid_x,
                                            self.mid2_x,
                                            self.mid3_x,
                                            self.mid4_x,
                                            self.mid5_x,
                                            self.mid6_x,
                                            self.mid7_x,
                                            self.mid8_x,
                                            self.mid9_x,
                                            self.mid10_x,
                                            self.mid11_x]

                    iris_nose_points_y = [self.nose_y,
                                            self.mid_nose_y,
                                            self.mid_mid_bottom_y,
                                            self.mid_mid_top_y,
                                            self.bottom_nose_y,
                                            self.mid_more_points_y,
                                            self.midier_nose_y,
                                            self.mid_mid_mid_bottom_y,
                                            self.mid_medium_mid_y,
                                            self.mid_midier_top_y,
                                            self.mid_midier_bottom_y,
                                            self.mid_medium_nose_y,
                                            self.mid_medium_bottom_y,
                                            self.mid_y,
                                            self.mid2_y,
                                            self.mid3_y,
                                            self.mid4_y,
                                            self.mid5_y,
                                            self.mid6_y,
                                            self.mid7_y,
                                            self.mid8_y,
                                            self.mid9_y,
                                            self.mid10_y,
                                            self.mid11_y]

                    right_iris_nose.append(self.right_iris_to_nose)
                    right_iris_nose.append((sqrt((self.r_cx - self.mid_nose_x)**2 + (self.r_cy - self.mid_nose_y)**2)) / self.pixel_mm_ratio)
                    right_iris_nose.append((sqrt((self.r_cx - self.mid_mid_bottom_x)**2 + (self.r_cy - self.mid_mid_bottom_y)**2)) / self.pixel_mm_ratio)
                    right_iris_nose.append((sqrt((self.r_cx - self.mid_mid_top_x)**2 + (self.r_cy - self.mid_mid_top_y)**2)) / self.pixel_mm_ratio)
                    right_iris_nose.append((sqrt((self.r_cx - self.bottom_nose_x)**2 + (self.r_cy - self.bottom_nose_y)**2)) / self.pixel_mm_ratio)
                    right_iris_nose.append((sqrt((self.r_cx - self.mid_more_points_x)**2 + (self.r_cy - self.mid_more_points_y)**2)) / self.pixel_mm_ratio)
                    right_iris_nose.append((sqrt((self.r_cx - self.midier_nose_x)**2 + (self.r_cy - self.midier_nose_y)**2)) / self.pixel_mm_ratio)
                    right_iris_nose.append((sqrt((self.r_cx - self.mid_mid_mid_bottom_x)**2 + (self.r_cy - self.mid_mid_mid_bottom_y)**2)) / self.pixel_mm_ratio)
                    right_iris_nose.append((sqrt((self.r_cx - self.mid_medium_mid_x)**2 + (self.r_cy - self.mid_medium_mid_y)**2)) / self.pixel_mm_ratio)
                    right_iris_nose.append((sqrt((self.r_cx - self.mid_midier_top_x)**2 + (self.r_cy - self.mid_midier_top_y)**2)) / self.pixel_mm_ratio)
                    right_iris_nose.append((sqrt((self.r_cx - self.mid_midier_bottom_x)**2 + (self.r_cy - self.mid_midier_bottom_y)**2)) / self.pixel_mm_ratio)
                    right_iris_nose.append((sqrt((self.r_cx - self.mid_medium_nose_x)**2 + (self.r_cy - self.mid_medium_nose_y)**2)) / self.pixel_mm_ratio)
                    right_iris_nose.append((sqrt((self.r_cx - self.mid_medium_bottom_x)**2 + (self.r_cy - self.mid_medium_bottom_y)**2)) / self.pixel_mm_ratio)
                    right_iris_nose.append((sqrt((self.r_cx - self.mid_x)**2 + (self.r_cy - self.mid_y)**2)) / self.pixel_mm_ratio)
                    right_iris_nose.append((sqrt((self.r_cx - self.mid2_x)**2 + (self.r_cy - self.mid2_y)**2)) / self.pixel_mm_ratio)
                    right_iris_nose.append((sqrt((self.r_cx - self.mid3_x)**2 + (self.r_cy - self.mid3_y)**2)) / self.pixel_mm_ratio)
                    right_iris_nose.append((sqrt((self.r_cx - self.mid4_x)**2 + (self.r_cy - self.mid4_y)**2)) / self.pixel_mm_ratio)
                    right_iris_nose.append((sqrt((self.r_cx - self.mid5_x)**2 + (self.r_cy - self.mid5_y)**2)) / self.pixel_mm_ratio)
                    right_iris_nose.append((sqrt((self.r_cx - self.mid6_x)**2 + (self.r_cy - self.mid6_y)**2)) / self.pixel_mm_ratio)
                    right_iris_nose.append((sqrt((self.r_cx - self.mid7_x)**2 + (self.r_cy - self.mid7_y)**2)) / self.pixel_mm_ratio)
                    right_iris_nose.append((sqrt((self.r_cx - self.mid8_x)**2 + (self.r_cy - self.mid8_y)**2)) / self.pixel_mm_ratio)
                    right_iris_nose.append((sqrt((self.r_cx - self.mid9_x)**2 + (self.r_cy - self.mid9_y)**2)) / self.pixel_mm_ratio)
                    right_iris_nose.append((sqrt((self.r_cx - self.mid10_x)**2 + (self.r_cy - self.mid10_y)**2)) / self.pixel_mm_ratio)
                    right_iris_nose.append((sqrt((self.r_cx - self.mid11_x)**2 + (self.r_cy - self.mid11_y)**2)) / self.pixel_mm_ratio)
                    left_iris_nose.append(self.left_iris_to_nose)
                    left_iris_nose.append((sqrt((self.l_cx - self.mid_nose_x)**2 + (self.l_cy - self.mid_nose_y)**2)) / self.pixel_mm_ratio)
                    left_iris_nose.append((sqrt((self.l_cx - self.mid_mid_bottom_x)**2 + (self.l_cy - self.mid_mid_bottom_y)**2)) / self.pixel_mm_ratio)
                    left_iris_nose.append((sqrt((self.l_cx - self.mid_mid_top_x)**2 + (self.l_cy - self.mid_mid_top_y)**2)) / self.pixel_mm_ratio)
                    left_iris_nose.append((sqrt((self.l_cx - self.bottom_nose_x)**2 + (self.l_cy - self.bottom_nose_y)**2)) / self.pixel_mm_ratio)
                    left_iris_nose.append((sqrt((self.l_cx - self.mid_more_points_x)**2 + (self.l_cy - self.mid_more_points_y)**2)) / self.pixel_mm_ratio)
                    left_iris_nose.append((sqrt((self.l_cx - self.midier_nose_x)**2 + (self.l_cy - self.midier_nose_y)**2)) / self.pixel_mm_ratio)
                    left_iris_nose.append((sqrt((self.l_cx - self.mid_mid_mid_bottom_x)**2 + (self.l_cy - self.mid_mid_mid_bottom_y)**2)) / self.pixel_mm_ratio)
                    left_iris_nose.append((sqrt((self.l_cx - self.mid_medium_mid_x)**2 + (self.l_cy - self.mid_medium_mid_y)**2)) / self.pixel_mm_ratio)
                    left_iris_nose.append((sqrt((self.l_cx - self.mid_midier_top_x)**2 + (self.l_cy - self.mid_midier_top_y)**2)) / self.pixel_mm_ratio)
                    left_iris_nose.append((sqrt((self.l_cx - self.mid_midier_bottom_x)**2 + (self.l_cy - self.mid_midier_bottom_y)**2)) / self.pixel_mm_ratio)
                    left_iris_nose.append((sqrt((self.l_cx - self.mid_medium_nose_x)**2 + (self.l_cy - self.mid_medium_nose_y)**2)) / self.pixel_mm_ratio)
                    left_iris_nose.append((sqrt((self.l_cx - self.mid_medium_bottom_x)**2 + (self.l_cy - self.mid_medium_bottom_x)**2)) / self.pixel_mm_ratio)
                    left_iris_nose.append((sqrt((self.l_cx - self.mid_x)**2 + (self.l_cy - self.mid_x)**2)) / self.pixel_mm_ratio)
                    left_iris_nose.append((sqrt((self.l_cx - self.mid2_x)**2 + (self.l_cy - self.mid2_y)**2)) / self.pixel_mm_ratio)
                    left_iris_nose.append((sqrt((self.l_cx - self.mid3_x)**2 + (self.l_cy - self.mid3_y)**2)) / self.pixel_mm_ratio)
                    left_iris_nose.append((sqrt((self.l_cx - self.mid4_x)**2 + (self.l_cy - self.mid4_y)**2)) / self.pixel_mm_ratio)
                    left_iris_nose.append((sqrt((self.l_cx - self.mid5_x)**2 + (self.l_cy - self.mid5_y)**2)) / self.pixel_mm_ratio)
                    left_iris_nose.append((sqrt((self.l_cx - self.mid6_x)**2 + (self.l_cy - self.mid6_y)**2)) / self.pixel_mm_ratio)
                    left_iris_nose.append((sqrt((self.l_cx - self.mid7_x)**2 + (self.l_cy - self.mid7_y)**2)) / self.pixel_mm_ratio)
                    left_iris_nose.append((sqrt((self.l_cx - self.mid8_x)**2 + (self.l_cy - self.mid8_y)**2)) / self.pixel_mm_ratio)
                    left_iris_nose.append((sqrt((self.l_cx - self.mid9_x)**2 + (self.l_cy - self.mid9_y)**2)) / self.pixel_mm_ratio)
                    left_iris_nose.append((sqrt((self.l_cx - self.mid10_x)**2 + (self.l_cy - self.mid10_y)**2)) / self.pixel_mm_ratio)
                    left_iris_nose.append((sqrt((self.l_cx - self.mid11_x)**2 + (self.l_cy - self.mid11_y)**2)) / self.pixel_mm_ratio)
                    self.minright = right_iris_nose[0]
                    self.minleft = left_iris_nose[0]
                    
                    # to get the smallest distance bet. the pupils and a horizontal point on the nose
                    for i in right_iris_nose:
                        if i < self.minright:
                            self.minright = i
                    for n in left_iris_nose:
                        if n < self.minleft:
                            self.minleft = n
                    # end of the smallest thing's verify #

                    if self.minright in right_iris_nose:
                        index = right_iris_nose.index(self.minright)
                        self.pointX_R = iris_nose_points_x[index]
                        self.pointY_R = iris_nose_points_y[index]
                    if self.minleft in left_iris_nose:
                        index_left = left_iris_nose.index(self.minleft)
                        self.pointX_L = iris_nose_points_x[index_left]
                        self.pointY_L = iris_nose_points_y[index_left]

                    # midpoint calculation, to get a horizontal line between both pupils
                    self.nose_point_for_dnp_X = int((self.pointX_R + self.pointX_L) / 2) 
                    self.nose_point_for_dnp_Y = int((self.pointY_R + self.pointY_L) / 2) 
                    # midpoint calculation #~
                    
                    # dnp calculation
                    self.dnp_left = sqrt((self.l_cx - self.nose_point_for_dnp_X)**2 + (self.l_cy - self.nose_point_for_dnp_Y)**2) / self.pixel_mm_ratio
                    self.dnp_right = sqrt((self.r_cx - self.nose_point_for_dnp_X)**2 + (self.r_cy - self.nose_point_for_dnp_Y)**2) / self.pixel_mm_ratio
                    # dnp calculation #
                    self.draw_on_img(self.img)
                    
                self.t_stamp = datetime.now().strftime("%I_%M_%S_%p--%d_%m_%Y")
                self.t_stamp = self.t_stamp
                cv2.imwrite("{}\\{}\\{}--{}.png".format(PATH, L.Universal["Ready Images Folder"], SelectedLanguage["Measurements Image"], self.t_stamp), self.img)
                self.put_glasses()
                imagee = Image.open("temp.png")
                self.put_glasses(ImageInput=imagee)
                self.progressbar.stop()
                self.progressbar.set(100)
                os.remove("temp.png")
            except Exception as error:
                self.progressbar.set(0)
                self.progressbar.stop()
                error = str(error)
                self.send_errors_discord(error)
                self.Warning_window(f"error: {error}", SelectedLanguage["Error Window Title"], self.MB_TOPMOST)
        except AttributeError:
            self.Warning_window(SelectedLanguage["Started Without Measurements Error"], SelectedLanguage["Error Window Title"])
            return
        

#DEBUG
#end_time = datetime.now()
#print('Duration: {}'.format(end_time - start_time))

@error_handler
def run():
    app.mainloop()
 
if __name__ == '__main__':
    app = GUI()
    run()
