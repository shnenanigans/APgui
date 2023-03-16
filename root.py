import tkinter as tk
#import afterend
#import obbypearls
import findportals
#import AllPortals\
import tkinter.font as tkFont

class Root:
    def __init__(self):
        self.root = tk.Tk()
        def_font = tkFont.nametofont("TkDefaultFont")
        def_font.config(family="Arial")
        self.root.title("All Portals")
        self.root.geometry("300x200")
        self.root.config(bg="#fee5b5")

        bt1 = tk.Button(self.root, text=("Find Portals"), command=lambda: findportals.FindPortals(self.root), font=('Arial', 16), borderwidth=3, bg="#fecca8")
        bt1.place(relx=0.5, rely=0.5, anchor="center")

        #exit program
        quit_button = tk.Button(self.root, text="Quit", command=exit, font=('Arial', 12), bg="#fecca8")
        quit_button.place(relx=0.05, rely=0.95, anchor="sw")

    def start(self):
        self.root.mainloop()