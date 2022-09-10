import os
import ctypes
import cv2
import webbrowser
import tkinter
from tkinter import filedialog
from tktooltip import ToolTip
import customtkinter
from PIL import ImageTk, Image
from discord_webhook import DiscordWebhook, DiscordEmbed
import numpy as np
from datetime import datetime
import math
from win10toast import ToastNotifier
import Languages.Languages_packs as L
from configparser import ConfigParser
import screeninfo
import threading
import ntpath
PATH = os.path.dirname(os.path.realpath(__file__))
Config_File = "{}\\{}\\config.ini".format(PATH, L.Universal["Necessary Files Folder"])
Config = ConfigParser()
Config.read(Config_File)

Language = Config["DEFAULTS"]["Language"]
match Language:
    case "Pt-pt":
        SelectedLanguage = L.PT_pt
        Option_lg_df = ("Português-pt")
    case "English":
        SelectedLanguage = L.English
        Option_lg_df = ("English")

Theme = Config["DEFAULTS"]["Theme"]
match Theme:
    case "Green":
        Program_Theme = "green"
        Option_th_df = "Green"
    
    case "Blue":
        Program_Theme = "blue"
        Option_th_df = "Blue"
    
    case "Dark-Blue":
        Program_Theme = "dark-blue"
        Option_th_df = "Dark-blue"
    
    case "Red":
        Program_Theme = "Necessary files\\Red-Theme.json"
        Option_th_df = "Red"


if not os.path.exists(L.Universal["Ready Images Folder"]):
    os.makedirs(L.Universal["Ready Images Folder"])

if not os.path.exists(L.Universal["Faces Folder"]):
    os.makedirs(L.Universal["Faces Folder"])

user = os.getlogin()
user_pc = os.getenv("COMPUTERNAME")
customtkinter.set_default_color_theme(Program_Theme)  # Themes: blue (default), dark-blue, green


image_extensions = r"*.jpg *.jpeg *.png"
# variáveis importantes
# importar o facemesh da google

# pontos do mediapipe mesh da google na cara para os olhos e a iris(roubei do indiano entendo minimamente oq faz)
LEFT_EYE =[362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385,384, 398]
RIGHT_EYE=[33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161 , 246] 
LEFT_IRIS = [474,475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]
count_imgs = []

# It takes an image, converts it to grayscale, applies an adaptive threshold to it, finds contours,
# and returns the contours that have an area greater than 2000
class HomogeneousBgDetector():
    def __init__(self):
        pass
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

def get_monitor_from_coord(x, y):
    monitors = screeninfo.get_monitors()

    for m in reversed(monitors):
        if m.x <= x <= m.width + m.x and m.y <= y <= m.height + m.y:
            return m
    return monitors[0]

parameters = cv2.aruco.DetectorParameters_create()
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_50)
detector = HomogeneousBgDetector()

class GUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        # WINDOW SETTINGS
        WIDTH = 1280
        HEIGHT = 720
        self.toast = ToastNotifier()
        self.title("Face Dimensions Detector (Beta 2.0)")
        self.wm_iconbitmap("{}\\icon.ico".format(L.Universal["Necessary Files Folder"]))
        self.attributes('-topmost',True)
        self.minsize(WIDTH, HEIGHT)
        self.maxsize(1920, 1080)
        self.bind('<Escape>',lambda e: self.exit())
        current_screen = get_monitor_from_coord(self.winfo_x(), self.winfo_y())
        screen_width = current_screen.width
        screen_height = current_screen.height
        x_cord = int((screen_width / 2) - (WIDTH / 2))
        y_cord = int((screen_height / 2) - (HEIGHT / 2))
        self.geometry("{}x{}+{}+{}".format(WIDTH, HEIGHT, x_cord, y_cord))
        self.window = None
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
        self.panel_icon.place(relx=0.5, rely=0.52, anchor=tkinter.CENTER)
        # ICON #
        
        # SETTINGS BUTTON
        self.settings_bt = customtkinter.CTkButton(self.Frame3, 
                                                    text=SelectedLanguage["Settings Button"],
                                                    image=self.settings_img,
                                                    compound=tkinter.RIGHT,
                                                    command=self.settings)
        self.settings_bt.place(relx=0.5, rely=0.47, anchor=tkinter.CENTER)
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
                                                            compound=tkinter.RIGHT)
        self.button_get_Face.place(relx=0.5, rely=0.32, anchor=tkinter.CENTER)
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
                                                            compound=tkinter.RIGHT, 
                                                            border_color=self.fg_color)
        self.button_add_Face.place(relx=0.5, rely=0.6, anchor=tkinter.CENTER)
        self.tooltip(self.button_add_Face, SelectedLanguage["Add Faces Button Tooltip"])
        # ADD FACE BUTTON #

        # INPUT FRAME LENGTH 
        self.entry_comprimento = customtkinter.CTkEntry(self.Frame2, 
                                                        placeholder_text="mm")
        self.entry_comprimento.place(relx=0.5, rely=0.72, anchor=tkinter.CENTER)
        self.tooltip(self.entry_comprimento, SelectedLanguage["Length Tooltip"])
        # INPUT FRAME LENGTH #

        # INPUT FRAME HEIGHT
        self.entry_altura = customtkinter.CTkEntry(self.Frame2, 
                                                    placeholder_text="mm")
        self.entry_altura.place(relx=0.5, rely=0.82, anchor=tkinter.CENTER)
        self.tooltip(self.entry_altura, SelectedLanguage["Height Tooltip"])
        # INPUT FRAME HEIGHT #

        # INPUT FRAME LENGTH LABEL
        self.label_comprimento = customtkinter.CTkLabel(self.Frame2, 
                                                        text=SelectedLanguage["Length Label"])
        self.label_comprimento.place(relx=0.5, rely=0.67, anchor=tkinter.CENTER)
        # INPUT FRAME LENGTH LABEL #
        
        # INPUT FRAME HEIGHT LABEL
        self.label_altura = customtkinter.CTkLabel(self.Frame2, 
                                                    text=SelectedLanguage["Height Label"])
        self.label_altura.place(relx=0.5, rely=0.77, anchor=tkinter.CENTER)
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
                                                                compound=tkinter.RIGHT)
        self.button_medidas_oculos.place(relx=0.5, rely=0.9, anchor=tkinter.CENTER)
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
                                                        compound=tkinter.RIGHT)
        self.open_results_bt.place(relx=0.5, rely=0.53, anchor=tkinter.CENTER)
        self.tooltip(self.open_results_bt, SelectedLanguage["Open Results Folder Tooltip"])
    

    # SETTINGS WINDOW 
    def closed_set_window(self):
        self.window.destroy()
        self.window = None
        

    def settings(self): 
        if self.window == None:
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
            current_screen = get_monitor_from_coord(self.window.winfo_x(), self.window.winfo_y())
            screen_width = current_screen.width
            screen_height = current_screen.height
            x_cord = int((screen_width / 2) - (Width / 2))
            y_cord = int((screen_height / 2) - (Height / 2))
            self.window.geometry("{}x{}+{}+{}".format(Width, Height, x_cord, y_cord))

            self.warningLabel = customtkinter.CTkLabel(self.window,
                                                            text=SelectedLanguage["Warning Label"])
            self.warningLabel.place(relx = 0.03,rely = 0.85)

            self.switch = customtkinter.CTkSwitch(master=self.window, 
                                                    text=SelectedLanguage["Theme Switch"], 
                                                    command=self.theme_change,)
            self.switch.toggle(1)
            self.switch.place(relx=0.12, rely=0.65)
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
                                                        compound=tkinter.RIGHT)
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
                                                        compound=tkinter.RIGHT)
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
                                                                    compound=tkinter.RIGHT)
            self.button_get_tutorial.place(anchor="w", rely = 0.15, relx=0.05)
            self.tooltip(self.button_get_tutorial, SelectedLanguage["Tutorial Button Tooltip"])

            
            self.Optionmenu = customtkinter.CTkOptionMenu(self.window,
                                                        values=["Português-pt", "English"],
                                                        command=self.change_language,
                                                        hover=True)
            self.Optionmenu.place(relx=0.95, rely=0.16, anchor="e")
            self.Optionmenu.set(Option_lg_df)

            self.OptionmenuTheme = customtkinter.CTkOptionMenu(self.window,
                                                        values=["Green", "Blue", "Dark-Blue", "Red"],
                                                        command=self.change_theme,
                                                        hover=True)
            self.OptionmenuTheme.place(relx=0.95, rely=0.45, anchor="e")
            self.OptionmenuTheme.set(Option_th_df)


            
        else:
            self.window.lift()
            self.toast.show_toast(
                "Optica",
                f'{SelectedLanguage["Duplicate Window"]}',
                duration = 2,
                icon_path = "icon.ico",
                threaded = True,
            )
    
    def change_language(self, choice):
        choice = self.Optionmenu.get()
        match choice:
            case "Português-pt":
                Config.set("DEFAULTS", "Language", "Pt-pt")
                with open(Config_File, "w") as f:
                    Config.write(f)
                    f.close
            #case "Português-br":
            #    SelectedLanguage = L.PT_br
            #    self.destroy()
            #    self.__init__()
            case "English":
                Config.set("DEFAULTS", "Language", "English")
                with open(Config_File, "w") as f:
                    Config.write(f)
                    f.close

    def change_theme(self, choice):
        choice = self.OptionmenuTheme.get()
        match choice:
            case "Green":
                Config.set("DEFAULTS", "Theme", "Green")
                with open(Config_File, "w") as f:
                    Config.write(f)
                    f.close
            case "Blue":
                Config.set("DEFAULTS", "Theme", "Blue")
                with open(Config_File, "w") as f:
                    Config.write(f)
                    f.close
            case "Dark-Blue":
                Config.set("DEFAULTS", "Theme", "Dark-Blue")
                with open(Config_File, "w") as f:
                    Config.write(f)
                    f.close
            case "Red":
                Config.set("DEFAULTS", "Theme", "Red")
                with open(Config_File, "w") as f:
                    Config.write(f)
                    f.close

    def import_mediapipe(self):
        import mediapipe as mp
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(static_image_mode=True, refine_landmarks=True, min_detection_confidence=0.5)
        # SETTINGS WINDOW #
    def exit(self):
        answer = ctypes.windll.user32.MessageBoxW(0, SelectedLanguage["Exit Window"], SelectedLanguage["Exit Window Title"], 1)
        match answer:
            case 0:
                pass
            case 1:
                self.destroy()

    def theme_change(self):
        match self.switch.get():
            case 0:
                customtkinter.set_appearance_mode("light")
            case 1:
                customtkinter.set_appearance_mode("dark")

    def report_command(self):
        try:
            url='https://forms.gle/n17W4q7ScDFCoEQT6'
            webbrowser.open(url)
        except Exception as erroo:
                erroo = str(erroo)
                self.send_errors_discord(erroo)
                ctypes.windll.user32.MessageBoxW(0, SelectedLanguage["Report Bug Error Window"], SelectedLanguage["Error Window Title"])
            
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

    def add_faces(self):
        try:
            Faces_folder = "{}\\{}".format(PATH, L.Universal["Faces Folder"])
            os.startfile(f"{Faces_folder}")
            self.toast.show_toast(
                "Optica",
                f'{SelectedLanguage["Add Faces Toast notification"]}',
                duration = 15,
                icon_path = "icon.ico",
                threaded = True,
            )
        except Exception as errrro:
            self.send_errors_discord(errrro)
            ctypes.windll.user32.MessageBoxW(0, SelectedLanguage["Open Faces Folder Error"], SelectedLanguage["Error Window Title"])

    def open_results(self):
        try:
            Results_folder = "{}\\{}".format(PATH, L.Universal["Ready Images Folder"])
            os.startfile(f'"{Results_folder}"')
        except Exception as eroro:
            ctypes.windll.user32.MessageBoxW(0, SelectedLanguage["Open Results Folder Error"], SelectedLanguage["Error Window Title"])
            self.send_errors_discord(eroro)
            
    def about(self):
        ctypes.windll.user32.MessageBoxW(0, SelectedLanguage["About Window Info"], SelectedLanguage["About Window Title"])

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
        if ntpath.isfile(self.Face_path):
            self.Face_image = Image.open(self.Face_path)
            self.Face_image = self.Face_image.resize((250, 250), Image.Resampling.LANCZOS)
            self.Face_image = ImageTk.PhotoImage(self.Face_image)
            self.panel_Face = customtkinter.CTkLabel(image=self.Face_image)
            self.panel_Face.place(relx=0.33, rely=0.45, anchor=tkinter.CENTER)
        else:
            print("no image selected")
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
                                                            compound=tkinter.RIGHT)
        self.button_get_Oculos.place(relx=0.5, rely=0.39, anchor=tkinter.CENTER)
        self.tooltip(self.button_get_Oculos, SelectedLanguage["Select Glasses Button Tooltip"])

    def open_faces_folder():
        os.open(L.Universal["Faces Folder"])
        
    def browse_Oculos(self):
        if os.path.exists(SelectedLanguage["Glasses Folder"]):
            self.Oculos_path = filedialog.askopenfilename(title=SelectedLanguage["Browse Glasses Window Title"],
                                                                initialdir = SelectedLanguage["Glasses Folder"], 
                                                                filetypes=[(SelectedLanguage["Browse Window Hint"], 
                                                                image_extensions)])
            self.Oculos_path = self.Oculos_path
        else:
            self.Oculos_path = filedialog.askopenfilename(title=SelectedLanguage["Browse Glasses Window Title"], 
                                                                filetypes=[(SelectedLanguage["Browse Window Hint"], 
                                                                image_extensions)])
            self.Oculos_path = self.Oculos_path
        #image
        self.Oculos_image = Image.open(self.Oculos_path)
        self.Oculos_image = self.Oculos_image.resize((700, 250), Image.Resampling.LANCZOS)
        self.Oculos_image = ImageTk.PhotoImage(self.Oculos_image)
        self.panel_Oculos = customtkinter.CTkLabel(image=self.Oculos_image)
        self.panel_Oculos.place(relx=0.73, rely=0.45, anchor=tkinter.CENTER)
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
                                                        compound=tkinter.RIGHT)
        self.button_Start.place(relx=0.5, rely=0.46, anchor=tkinter.CENTER)
        self.tooltip(self.button_Start, SelectedLanguage["Start Button Tooltip"])

    def tutorial(self):
        try:
            os.startfile("{}\\tutorial.mp4".format(L.Universal["Necessary Files Folder"]))
        except:
            err = str(err)
            self.send_errors_discord(err)
            ctypes.windll.user32.MessageBoxW(0, SelectedLanguage["Tutorial Open Error Window"], SelectedLanguage["Error Window Title"])
   
    def draw_on_img(self, img):
        try:
            cv2.circle(img, self.center_left, int(self.l_radius), (255,0,255), 2, cv2.LINE_AA)
            cv2.circle(img, self.center_right, int(self.r_radius), (255,0,255), 2, cv2.LINE_AA)
            cv2.line(img, (self.pointx, self.pointy), self.center_left, (0, 255, 0), 1)
            cv2.line(img, (self.pointxl, self.pointyl), self.center_right, (0, 255, 0), 1)
            cv2.line(img, (self.left_face_x, self.left_face_y), (self.right_face_x, self.right_face_y), (255, 0, 0), 1)
            cv2.line(img, self.center_right, self.center_left, (0, 0, 255), 1)
            cv2.rectangle(img, (10, self.imy - 265), (self.imx, self.imy), (0, 0, 0), 350, cv2.FILLED)
            cv2.putText(img, SelectedLanguage["Pupillary Distance"] + f"{round(self.iris_to_iris_line_distance, 2)} mm", (10, self.imy - 5), cv2.FONT_HERSHEY_DUPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(img, SelectedLanguage["Left Nasopupillary distance"] + f"{round(self.minleft, 2)} mm", (10, self.imy - 55), cv2.FONT_HERSHEY_DUPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(img, SelectedLanguage["Right Nasopupillary distance"] + f"{round(self.minright, 2)} mm", (10, self.imy - 105), cv2.FONT_HERSHEY_DUPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(img, SelectedLanguage["Face Length"] + f"{round(self.left_to_right_face, 2)} mm", (10, self.imy - 155), cv2.FONT_HERSHEY_DUPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(img, SelectedLanguage["Right eye"], (self.bmx, self.bmy), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, cv2.LINE_AA)
            cv2.putText(img, SelectedLanguage["Left eye"], (self.bmlx, self.bmly), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2, cv2.LINE_AA)
            self.medidas_label = customtkinter.CTkLabel(self, text=SelectedLanguage["Pupillary Distance"] + f"{round(self.iris_to_iris_line_distance, 2)} mm\n" + SelectedLanguage["Left Nasopupillary distance"] + f"{round(self.minleft, 2)} mm\n" + SelectedLanguage["Right Nasopupillary distance"] + f"{round(self.minright, 2)} mm\n" + SelectedLanguage["Face Length"] + f"{round(self.left_to_right_face, 2)} mm\n" + SelectedLanguage["Right Height"] + f"{round(self.right_iris_Oculos, 2)} mm\n" + SelectedLanguage["Left Height"] + f"{round(self.left_iris_Oculos, 2)} mm")
            self.medidas_label.configure(font=("Courier", 18, "bold"), anchor="w", justify=tkinter.LEFT)
            self.medidas_label.place(relx= 0.2, rely=0.67)
        except Exception as eroro:
            self.send_errors_discord(eroro,)

    def get_point(self, x, y, width_original, height_original, width_res, height_res):
        x_transforming_ratio = x / width_original
        y_transforming_ratio = y / height_original
        self.x = int(width_res * x_transforming_ratio)
        self.y = int(height_res * y_transforming_ratio)

    def put_glasses(self, ImageInput=None):
        if ImageInput == None:
            img = Image.open("{}/{}--{}.png".format(L.Universal["Ready Images Folder"], SelectedLanguage["Measurements Image"], self.t_stamp))
        else:
            img = ImageInput
        width_pic = int(img.size[0]) # gets the original picture width
        height_pic = int(img.size[1]) # "" "" height
        mask_Oculos = Image.open(self.Oculos_path) # opens the Oculos image
        width_oculos_original = int(mask_Oculos.size[0])
        height_oculos_original = int(mask_Oculos.size[1])
        #print(height_oculos_original)
        self.width_Oculos = int(self.comprimento * self.pixel_mm_ratio) # sets the width of the Oculos image to be the same as the distance between 2 points of the face
        mask_Oculos = mask_Oculos.resize((self.width_Oculos, int(self.altura * self.pixel_mm_ratio))) #kinda obvious
        width_oculos_resized = int(mask_Oculos.size[0])
        height_oculos_resized = int(mask_Oculos.size[1])
        #print(height_oculos_resized)

        mask_Oculos.save("temp.png")
        if self.Oculos_path.endswith("Oculos2.png"):
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
        r_iris_glasses = (math.sqrt((self.r_cx - right_iris_x)**2 + (self.r_cy - right_iris_y)**2)) / self.pixel_mm_ratio
        l_iris_glasses = (math.sqrt((self.l_cx - left_iris_x)**2 + (self.l_cy - left_iris_y)**2)) / self.pixel_mm_ratio
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

    def send_errors_discord(self, erro):
        try:
            erro = str(f"User: {user}\nPc: {user_pc}\n\n" + erro)
            embed = DiscordEmbed(title='Erro', description=erro, color='03b2f8')
            embed.set_timestamp()
            webhook = DiscordWebhook(url='https://discord.com/api/webhooks/979917471878381619/R4jt6PLLlnxsuGXbeRm1wokotX4IjqQj3PbC2JqFlP7-4koEATZ3jqA_fVI_T7UXqaXe')
            webhook.add_embed(embed)
            response = webhook.execute()
        except Exception as er:
            pass
       

    def salvar(self):
        try:
            self.comprimento = float(self.entry_comprimento.get())
            self.altura = float(self.entry_altura.get())
            if self.comprimento not in range(100,250) or self.altura not in range(20, 100):
                ctypes.windll.user32.MessageBoxW(0, SelectedLanguage["Save  Measurements Error"], SelectedLanguage["Error Window Title"])
                self.toast.show_toast(
                "Optica",
                SelectedLanguage["Save Measurements Error Notification"],
                duration = 10,
                icon_path = "icon.ico",
                threaded = True,
                )
                return

            else:
                self.toast.show_toast(
                "Optica",
                "{}\n{}{}\n{}{}".format(SelectedLanguage["Save Measurements Success Tooltip"], SelectedLanguage["Length"], self.comprimento, SelectedLanguage["Height"], self.altura),
                duration = 5,
                icon_path = "icon.ico",
                threaded = True,
            )
        except Exception as eroo:
            eroo = str(eroo)
            self.send_errors_discord(eroo)
            ctypes.windll.user32.MessageBoxW(0, SelectedLanguage["Save Measurements Error Notification"], SelectedLanguage["Error Window Title"])

    def get_object_size(self, image):
        try:
            if self.comprimento not in range(100,250) or self.altura not in range(20, 100):
                ctypes.windll.user32.MessageBoxW(0, SelectedLanguage["Get Object Size Error"], SelectedLanguage["Error Window Title"])
                return
            else:
            # para o caso de haver muitas imagens assim ficam todas com o nome na ordem que foram processadas
                try:
                    Load_Mediapipe = threading.Thread(target=self.import_mediapipe(), daemon=True)
                    Load_Mediapipe.start()
                    self.image = image
                    img = cv2.imread(image)
                    # ir buscar o aruco marker
                    corners, _, _ = cv2.aruco.detectMarkers(img, aruco_dict, parameters=parameters)
                    int_corners = np.int0(corners)
                    # desenhamos linhas verdes a volta do aruco marker sabendo que ele tem um perímetro de 20cm
                    cv2.polylines(img, int_corners, True, (0, 255, 0), 5)
                    # perimetro do aruco
                    # funciona com apenas 1 aruco marker
                    self.aruco_perimeter = cv2.arcLength(corners[0], True)
                    # Pixel to mm ratio
                    self.pixel_mm_ratio = self.aruco_perimeter / 200
                except Exception as ero:
                    ero = str(ero)
                    self.send_errors_discord(ero)
                    ctypes.windll.user32.MessageBoxW(0, SelectedLanguage["Aruco Marker Not detected"], SelectedLanguage["Error Window Title"])

                try:
                    self.img = cv2.imread(image)
                    self.imy, self.imx, _ = self.img.shape
                    # opens the image with pil to put them Oculos on
                    # é necessario converter a imagem de Blue green red para Red green blue
                    rgb_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
                    # tamanho da imagem
                    height, width, _ = self.img.shape
                    result = self.face_mesh.process(rgb_img)
                    for facial_landmarks in result.multi_face_landmarks:
                        midle_nose = facial_landmarks.landmark[168]
                        midle_nose_bottom = facial_landmarks.landmark[8]
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
                        # cordenadas não podem ser floats
                        # pontos necessarios
                        self.bottom_x = int(more_points_bottom_nose.x * width)
                        self.bottom_y = int(more_points_bottom_nose.y * height)
                        self.bottom_nose_x = int(bottom_nose.x * width)
                        self.bottom_nose_y = int(bottom_nose.y * height)
                        self.midle_nose_bottom_x = int(midle_nose_bottom.x * width) #midle nose bottom "x"
                        self.midle_nose_bottom_y = int(midle_nose_bottom.y * height) #midle nose bottom "y"
                        self.nose_x = int(midle_nose.x * width) #nose "x"
                        self.nose_y = int(midle_nose.y * height) #nose "y"
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
                        self.midpoint_nose_x = int((self.midle_nose_bottom_x + self.nose_x) / 2)
                        self.midpoint_nose_y = int((self.midle_nose_bottom_y + self.nose_y) / 2)
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
                        self.iris_to_iris_line_distance = (math.sqrt((self.r_cx - self.l_cx)**2 + (self.r_cy - self.l_cy)**2)) / self.pixel_mm_ratio
                        self.left_iris_to_nose = (math.sqrt((self.l_cx - self.nose_x)**2 + (self.l_cy - self.nose_y)**2)) / self.pixel_mm_ratio
                        self.right_iris_to_nose = (math.sqrt((self.r_cx - self.nose_x)**2 + (self.r_cy - self.nose_y)**2)) / self.pixel_mm_ratio
                        self.left_to_right_face = (math.sqrt((self.left_face_x - self.right_face_x)**2 + (self.left_face_y - self.right_face_y)**2)) / self.pixel_mm_ratio
                        self.right_iris_Oculos = round((math.sqrt((self.r_cx - self.bmx)**2 + (self.r_cy - self.bmy)**2)) / self.pixel_mm_ratio, 2)
                        self.left_iris_Oculos = round((math.sqrt((self.l_cx - self.bmlx)**2 + (self.l_cy - self.bmly)**2)) / self.pixel_mm_ratio, 2)
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
                        right_iris_nose.append((math.sqrt((self.r_cx - self.mid_nose_x)**2 + (self.r_cy - self.mid_nose_y)**2)) / self.pixel_mm_ratio)
                        right_iris_nose.append((math.sqrt((self.r_cx - self.mid_mid_bottom_x)**2 + (self.r_cy - self.mid_mid_bottom_y)**2)) / self.pixel_mm_ratio)
                        right_iris_nose.append((math.sqrt((self.r_cx - self.mid_mid_top_x)**2 + (self.r_cy - self.mid_mid_top_y)**2)) / self.pixel_mm_ratio)
                        right_iris_nose.append((math.sqrt((self.r_cx - self.bottom_nose_x)**2 + (self.r_cy - self.bottom_nose_y)**2)) / self.pixel_mm_ratio)
                        right_iris_nose.append((math.sqrt((self.r_cx - self.mid_more_points_x)**2 + (self.r_cy - self.mid_more_points_y)**2)) / self.pixel_mm_ratio)
                        right_iris_nose.append((math.sqrt((self.r_cx - self.midier_nose_x)**2 + (self.r_cy - self.midier_nose_y)**2)) / self.pixel_mm_ratio)
                        right_iris_nose.append((math.sqrt((self.r_cx - self.mid_mid_mid_bottom_x)**2 + (self.r_cy - self.mid_mid_mid_bottom_y)**2)) / self.pixel_mm_ratio)
                        right_iris_nose.append((math.sqrt((self.r_cx - self.mid_medium_mid_x)**2 + (self.r_cy - self.mid_medium_mid_y)**2)) / self.pixel_mm_ratio)
                        right_iris_nose.append((math.sqrt((self.r_cx - self.mid_midier_top_x)**2 + (self.r_cy - self.mid_midier_top_y)**2)) / self.pixel_mm_ratio)
                        right_iris_nose.append((math.sqrt((self.r_cx - self.mid_midier_bottom_x)**2 + (self.r_cy - self.mid_midier_bottom_y)**2)) / self.pixel_mm_ratio)
                        right_iris_nose.append((math.sqrt((self.r_cx - self.mid_medium_nose_x)**2 + (self.r_cy - self.mid_medium_nose_y)**2)) / self.pixel_mm_ratio)
                        right_iris_nose.append((math.sqrt((self.r_cx - self.mid_medium_bottom_x)**2 + (self.r_cy - self.mid_medium_bottom_y)**2)) / self.pixel_mm_ratio)
                        right_iris_nose.append((math.sqrt((self.r_cx - self.mid_x)**2 + (self.r_cy - self.mid_y)**2)) / self.pixel_mm_ratio)
                        right_iris_nose.append((math.sqrt((self.r_cx - self.mid2_x)**2 + (self.r_cy - self.mid2_y)**2)) / self.pixel_mm_ratio)
                        right_iris_nose.append((math.sqrt((self.r_cx - self.mid3_x)**2 + (self.r_cy - self.mid3_y)**2)) / self.pixel_mm_ratio)
                        right_iris_nose.append((math.sqrt((self.r_cx - self.mid4_x)**2 + (self.r_cy - self.mid4_y)**2)) / self.pixel_mm_ratio)
                        right_iris_nose.append((math.sqrt((self.r_cx - self.mid5_x)**2 + (self.r_cy - self.mid5_y)**2)) / self.pixel_mm_ratio)
                        right_iris_nose.append((math.sqrt((self.r_cx - self.mid6_x)**2 + (self.r_cy - self.mid6_y)**2)) / self.pixel_mm_ratio)
                        right_iris_nose.append((math.sqrt((self.r_cx - self.mid7_x)**2 + (self.r_cy - self.mid7_y)**2)) / self.pixel_mm_ratio)
                        right_iris_nose.append((math.sqrt((self.r_cx - self.mid8_x)**2 + (self.r_cy - self.mid8_y)**2)) / self.pixel_mm_ratio)
                        right_iris_nose.append((math.sqrt((self.r_cx - self.mid9_x)**2 + (self.r_cy - self.mid9_y)**2)) / self.pixel_mm_ratio)
                        right_iris_nose.append((math.sqrt((self.r_cx - self.mid10_x)**2 + (self.r_cy - self.mid10_y)**2)) / self.pixel_mm_ratio)
                        right_iris_nose.append((math.sqrt((self.r_cx - self.mid11_x)**2 + (self.r_cy - self.mid11_y)**2)) / self.pixel_mm_ratio)
                        left_iris_nose.append(self.left_iris_to_nose)
                        left_iris_nose.append((math.sqrt((self.l_cx - self.mid_nose_x)**2 + (self.l_cy - self.mid_nose_y)**2)) / self.pixel_mm_ratio)
                        left_iris_nose.append((math.sqrt((self.l_cx - self.mid_mid_bottom_x)**2 + (self.l_cy - self.mid_mid_bottom_y)**2)) / self.pixel_mm_ratio)
                        left_iris_nose.append((math.sqrt((self.l_cx - self.mid_mid_top_x)**2 + (self.l_cy - self.mid_mid_top_y)**2)) / self.pixel_mm_ratio)
                        left_iris_nose.append((math.sqrt((self.l_cx - self.bottom_nose_x)**2 + (self.l_cy - self.bottom_nose_y)**2)) / self.pixel_mm_ratio)
                        left_iris_nose.append((math.sqrt((self.l_cx - self.mid_more_points_x)**2 + (self.l_cy - self.mid_more_points_y)**2)) / self.pixel_mm_ratio)
                        left_iris_nose.append((math.sqrt((self.l_cx - self.midier_nose_x)**2 + (self.l_cy - self.midier_nose_y)**2)) / self.pixel_mm_ratio)
                        left_iris_nose.append((math.sqrt((self.l_cx - self.mid_mid_mid_bottom_x)**2 + (self.l_cy - self.mid_mid_mid_bottom_y)**2)) / self.pixel_mm_ratio)
                        left_iris_nose.append((math.sqrt((self.l_cx - self.mid_medium_mid_x)**2 + (self.l_cy - self.mid_medium_mid_y)**2)) / self.pixel_mm_ratio)
                        left_iris_nose.append((math.sqrt((self.l_cx - self.mid_midier_top_x)**2 + (self.l_cy - self.mid_midier_top_y)**2)) / self.pixel_mm_ratio)
                        left_iris_nose.append((math.sqrt((self.l_cx - self.mid_midier_bottom_x)**2 + (self.l_cy - self.mid_midier_bottom_y)**2)) / self.pixel_mm_ratio)
                        left_iris_nose.append((math.sqrt((self.l_cx - self.mid_medium_nose_x)**2 + (self.l_cy - self.mid_medium_nose_y)**2)) / self.pixel_mm_ratio)
                        left_iris_nose.append((math.sqrt((self.l_cx - self.mid_medium_bottom_x)**2 + (self.l_cy - self.mid_medium_bottom_x)**2)) / self.pixel_mm_ratio)
                        left_iris_nose.append((math.sqrt((self.l_cx - self.mid_x)**2 + (self.l_cy - self.mid_x)**2)) / self.pixel_mm_ratio)
                        left_iris_nose.append((math.sqrt((self.l_cx - self.mid2_x)**2 + (self.l_cy - self.mid2_y)**2)) / self.pixel_mm_ratio)
                        left_iris_nose.append((math.sqrt((self.l_cx - self.mid3_x)**2 + (self.l_cy - self.mid3_y)**2)) / self.pixel_mm_ratio)
                        left_iris_nose.append((math.sqrt((self.l_cx - self.mid4_x)**2 + (self.l_cy - self.mid4_y)**2)) / self.pixel_mm_ratio)
                        left_iris_nose.append((math.sqrt((self.l_cx - self.mid5_x)**2 + (self.l_cy - self.mid5_y)**2)) / self.pixel_mm_ratio)
                        left_iris_nose.append((math.sqrt((self.l_cx - self.mid6_x)**2 + (self.l_cy - self.mid6_y)**2)) / self.pixel_mm_ratio)
                        left_iris_nose.append((math.sqrt((self.l_cx - self.mid7_x)**2 + (self.l_cy - self.mid7_y)**2)) / self.pixel_mm_ratio)
                        left_iris_nose.append((math.sqrt((self.l_cx - self.mid8_x)**2 + (self.l_cy - self.mid8_y)**2)) / self.pixel_mm_ratio)
                        left_iris_nose.append((math.sqrt((self.l_cx - self.mid9_x)**2 + (self.l_cy - self.mid9_y)**2)) / self.pixel_mm_ratio)
                        left_iris_nose.append((math.sqrt((self.l_cx - self.mid10_x)**2 + (self.l_cy - self.mid10_y)**2)) / self.pixel_mm_ratio)
                        left_iris_nose.append((math.sqrt((self.l_cx - self.mid11_x)**2 + (self.l_cy - self.mid11_y)**2)) / self.pixel_mm_ratio)
                        self.minright = right_iris_nose[0]
                        self.minleft = left_iris_nose[0]
                        for i in right_iris_nose:
                            if i < self.minright:
                                self.minright = i
                        for n in left_iris_nose:
                            if n < self.minleft:
                                self.minleft = n
                        if self.minright in right_iris_nose:
                            index = right_iris_nose.index(self.minright)
                            self.pointx = iris_nose_points_x[index]
                            self.pointy = iris_nose_points_y[index]
                        if self.minleft in left_iris_nose:
                            index_left = left_iris_nose.index(self.minleft)
                            self.pointxl = iris_nose_points_x[index_left]
                            self.pointyl = iris_nose_points_y[index_left]
                        #print(right_iris_nose, self.minright)
                        self.draw_on_img(self.img)
                    self.t_stamp = datetime.now().strftime("%I_%M_%S_%p--%d_%m_%Y")
                    self.t_stamp = self.t_stamp
                    cv2.imwrite("{}/{}--{}.png".format(L.Universal["Ready Images Folder"], SelectedLanguage["Measurements Image"], self.t_stamp), self.img)
                    self.put_glasses()
                    imagee = Image.open("temp.png")
                    self.put_glasses(ImageInput=imagee)
                    os.remove("temp.png")
                except Exception as e:
                    e = str(e)
                    self.send_errors_discord(e)
                    ctypes.windll.user32.MessageBoxW(0, f"Erro: {e}", SelectedLanguage["Error Window Title"])
        except AttributeError:
            ctypes.windll.user32.MessageBoxW(0, SelectedLanguage["Started Without Measurements Error"], SelectedLanguage["Error Window Title"])
            return

def run():
    app = GUI()
    app.mainloop()
 
if __name__ == '__main__':
    run()
    
    
    




