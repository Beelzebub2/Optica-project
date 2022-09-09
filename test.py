from tkinter import *
import tkinter
from tkinter import font
from PIL import ImageTk, Image 
import time
import screeninfo

root=tkinter.Tk()

def get_monitor_from_coord(x, y):
    monitors = screeninfo.get_monitors()

    for m in reversed(monitors):
        if m.x <= x <= m.width + m.x and m.y <= y <= m.height + m.y:
            return m
    return monitors[0]


def main(root):
    #Using piece of code from old splash screen
    WIDTH = 427
    HEIGHT = 250
    current_screen = get_monitor_from_coord(root.winfo_x(), root.winfo_y())
    screen_width = current_screen.width
    screen_height = current_screen.height
    x_cord = int((screen_width / 2) - (WIDTH / 2))
    y_cord = int((screen_height / 2) - (HEIGHT / 2))
    root.geometry("{}x{}+{}+{}".format(WIDTH, HEIGHT, x_cord, y_cord))
    #root.configure(bg='#ED1B76')
    root.overrideredirect(1) #for hiding titlebar

    #new window to open
    def new_win():
        q=Tk()
        q.title('main window')
        q.mainloop()

    Frame(root, width=427, height=250, bg='#272727').place(x=0,y=0)
    label1=tkinter.Label(root, text='Teac 21', fg='white', bg='#272727') #decorate it 
    label1.configure(font=("Calibri", 24, "bold"))   #You need to install this font in your PC or try another one
    label1.place(x=80,y=90)

    label2=tkinter.Label(root, text='Loading...', fg='white', bg='#272727') #decorate it 
    label2.configure(font=("Calibri", 11))
    label2.place(x=10,y=215)

    #making animation

    image_a=ImageTk.PhotoImage(Image.open('c2.png'))
    image_b=ImageTk.PhotoImage(Image.open('c1.png'))




    for i in range(5): #5loops
        l1=tkinter.Label(root, image=image_a, border=0, relief=tkinter.SUNKEN).place(x=180, y=145)
        l2=tkinter.Label(root, image=image_b, border=0, relief=tkinter.SUNKEN).place(x=200, y=145)
        l3=tkinter.Label(root, image=image_b, border=0, relief=tkinter.SUNKEN).place(x=220, y=145)
        l4=tkinter.Label(root, image=image_b, border=0, relief=tkinter.SUNKEN).place(x=240, y=145)
        root.update_idletasks()
        time.sleep(0.5)

        l1=tkinter.Label(root, image=image_b, border=0, relief=tkinter.SUNKEN).place(x=180, y=145)
        l2=tkinter.Label(root, image=image_a, border=0, relief=tkinter.SUNKEN).place(x=200, y=145)
        l3=tkinter.Label(root, image=image_b, border=0, relief=tkinter.SUNKEN).place(x=220, y=145)
        l4=tkinter.Label(root, image=image_b, border=0, relief=tkinter.SUNKEN).place(x=240, y=145)
        root.update_idletasks()
        time.sleep(0.5)

        l1=tkinter.Label(root, image=image_b, border=0, relief=tkinter.SUNKEN).place(x=180, y=145)
        l2=tkinter.Label(root, image=image_b, border=0, relief=tkinter.SUNKEN).place(x=200, y=145)
        l3=tkinter.Label(root, image=image_a, border=0, relief=tkinter.SUNKEN).place(x=220, y=145)
        l4=tkinter.Label(root, image=image_b, border=0, relief=tkinter.SUNKEN).place(x=240, y=145)
        root.update_idletasks()
        time.sleep(0.5)

        l1=tkinter.Label(root, image=image_b, border=0, relief=tkinter.SUNKEN).place(x=180, y=145)
        l2=tkinter.Label(root, image=image_b, border=0, relief=tkinter.SUNKEN).place(x=200, y=145)
        l3=tkinter.Label(root, image=image_b, border=0, relief=tkinter.SUNKEN).place(x=220, y=145)
        l4=tkinter.Label(root, image=image_a, border=0, relief=tkinter.SUNKEN).place(x=240, y=145)
        root.update_idletasks()
        time.sleep(0.5)
    root.destroy()
    new_win()
    root.mainloop()

main(root)