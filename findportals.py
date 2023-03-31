import tkinter as tk
from tkinter import messagebox
from utils import *
import numpy as np
import matplotlib.pyplot as plt
from tkinter.simpledialog import askinteger
from tkinter.simpledialog import askstring

class FindPortals:
    def __init__(self):
        #create root window
        self.window3 = tk.Tk()
        self.window3.config(bg="#fee5b5")
        self.window3.title("Find Portals")
        self.window3.wm_attributes("-topmost", 0)
        #self.first_strongholds = [(1512, -104), (5736, -712), (7512, 2280), (10584, 1368), (14168, 584), (17704, -312), (20920, 1160), (23528, -920)]
        self.first_strongholds = []
        self.prev = (0, 0)
        self.new_strongholds = []
        self.completed_eighth_ring = 0
        self.found_empty = False #true when the user has found the 8th ring's empty sector

        self.sh_per_ring = [3, 6, 10, 15, 21, 28, 36, 10]
        self.magnitude_per_ring = [2048, 5120, 8192, 11264, 14336, 17408, 20480, 23552]
        self.count = 0
        updateCount(self.count)

        #create the image showing portals path and completed portals
        self.img = plt.imread("rings.png")
        plt.imshow(self.img, aspect="equal", extent=[-24320, 24320, -24320, 24320])
        plt.axis("off")
        plt.savefig("output.png", bbox_inches="tight", transparent=True)

        self.create_inital_widgets() #entry boxes for user to input first 8 sh coords
        self.window3.mainloop()

    def create_inital_widgets(self):
        #toggles window always on top or not
        self.toggle_frame = tk.Frame(self.window3, width=150, height=20, bg="#fee5b5")
        self.toggle_frame.grid(row=1, column=6, rowspan=2)
        top_value = tk.BooleanVar()
        self.topmost_toggle = tk.Checkbutton(self.toggle_frame, bg="#fee5b5", activebackground="#fee5b5", text="Always On Top", variable=top_value, onvalue=True, offvalue=False, command=lambda: [self.check_top(top_value.get())])
        self.topmost_toggle.place(relx=0.5, rely=0.5, anchor="center")
        
        #labels for the entry boxes and locks to save each coord into a list of first strongholds
        self.sh_labels = [tk.Label(self.window3, bg="#fee5b5", text=f"sh {i}:") for i in range(1,9)]
        [self.sh_labels[i].grid(row=i, column=1) for i in range(0,8)]

        self.entries = [tk.Entry(self.window3, width=40, borderwidth=5, bg="#feedcc") for i in range(0,8)]
        [self.entries[i].grid(row=i, column=2, columnspan=3) for i in range(0,8)]

        self.locks = [tk.Button(self.window3, text="lock", borderwidth=3, bg="#fecca8", activebackground="#feedcc") for i in range(0,8)]
        for i in range(0,8):
            self.locks[i].config(command=lambda i=i: self.lock_entry(self.entries[i].get(), self.locks[i], i+1))
        [self.locks[i].grid(row=i, column=5) for i in range(0,8)]

        #label telling user to lock in order cause i dont wanna sort the list myself
        lock_order_label = tk.Label(self.window3, text="Please make sure you\nlock strongholds in the\norder you found them", bg="#fee5b5")
        lock_order_label.grid(row=3, column=6, rowspan=3)

        #goes to next stage, only works once all 8 locations have been locked
        self.next_button = tk.Button(self.window3, text="next", command=self.check_next, bg="#fecca8", activebackground="#feedcc")
        self.next_button.grid(row=9, column=6)
            
    #changes window always on top or not
    def check_top(self, top_value):
        if top_value:
            self.window3.wm_attributes("-topmost", 1)
        else:
            self.window3.wm_attributes("-topmost", 0)

    #checks if coords are in correct ring and in the right format, adds them to first strongholds list
    def lock_entry(self, entry, lock, i):
        try:
            self.sh = tuple(getIntInput(entry))
        except:
            messagebox.showerror(message="Something went wrong. Make sure you only input your x and z coordinate separated by a space, or copy paste the f3+c command")
            return
        if len(self.sh) != 2:
            messagebox.showerror(message="Something went wrong. Make sure you only input your x and z coordinate separated by a space, or copy paste the f3+c command")
            return
        else:
            ring = getRing(self.sh)
            if i != ring:
                if ring > 0:
                    msg = messagebox.askyesno(message="Are you sure this is in the right ring? Looks like this is a stronghold in ring " + str(ring) +
                    ".\nIf you are completely sure this is in the right ring and my program is stupid then click 'yes', otherwise hit 'no' and enter coords again")
                    if msg == False:
                        return
                else:
                    msg = messagebox.askyesno(message="Are you sure this is in the right ring? This stronghold does not appear to be in any ring." +
                    "\nThis is possible to occur with biome snapping, but quite rare. If you are sure then click 'yes', otherwise hit 'no' and enter coords again")
                    if msg == False:
                        return

        self.first_strongholds.append(self.sh)
        self.count += 1
        #update image
        updateCount(self.count)
        plt.scatter(self.sh[0], self.sh[1], c="green", s=40)
        plt.arrow(
            self.prev[0],
            self.prev[1],
            self.sh[0] - self.prev[0],
            self.sh[1] - self.prev[1],
            color="green",
            width=0.0001,
            head_width=0,
            head_length=0,
            length_includes_head=True,
        )
        plt.savefig("output.png", bbox_inches="tight", transparent=True)
        self.prev = self.sh
        lock.config(state="disabled")

    #checks each sh location is locked before changing window setup and predicts other sh locations
    def check_next(self):
        if len(self.first_strongholds) == 8:
            # Predict location of all the other strongholds
            for i in range(len(self.first_strongholds)):
                x, z = self.first_strongholds[i]
                magnitude = self.magnitude_per_ring[i]
                vec1 = np.array([x, z])
                vec2 = np.array([1, 0])
                ang = np.arctan2(vec1[1], vec1[0]) - np.arctan2(vec2[1], vec2[0])
                # print("Ring", i + 1, ang)
                for j in range(self.sh_per_ring[i] - 1):
                    ang += (2 * np.pi) / self.sh_per_ring[i]
                    new_x = magnitude * np.cos(ang)
                    new_z = magnitude * np.sin(ang)
                    self.new_strongholds.append((round(new_x), round(new_z)))
                    print(round(new_x), round(new_z), ang)

            self.next_button.config(state="disabled") #very silly things happen if you press the next button twice...
            self.paths, nearest_idx = generatePath(self.new_strongholds, self.first_strongholds[-1])

            #get rid of all widgets from the first-strongholds part
            for lock in self.locks:
                lock.destroy()
            for sh in self.sh_labels:
                sh.destroy()
            for entry in self.entries:
                entry.destroy()
            
            nearest = self.new_strongholds[nearest_idx]
            self.eighth_ring = self.new_strongholds[-9:]
            self.curr = nearest_idx

            plt.scatter(*zip(*self.new_strongholds), c="gray", s=20)
            plt.savefig("output.png", bbox_inches="tight", transparent=True)

            #self.window3.geometry("400x200")
            self.completed_eighth_ring+=1
            self.setup_next()
            self.next_sh()
        else:
            messagebox.showinfo(message="please lock each stronghold location")
    
    #changes entire window setup to just display sh coords and some options
    def setup_next(self):

        self.completed = self.first_strongholds
        self.unfinished = self.new_strongholds
        self.prev = self.completed[-1]
        self.c2 = False
        self.noGraph = False

        self.window3.config(bg="#cdeaf7")
        self.toggle_frame.config(height=70, width=200, bg="#cdeaf7")
        self.topmost_toggle.config(bg="#cdeaf7", activebackground="#b3deef")
        self.sh_frame = tk.Frame(self.window3, height=70, width=280, bg="#cdeaf7")
        self.sh_label = tk.Label(self.sh_frame, text="", bg="#cdeaf7")
        self.sh_label.place(relx=0.5, rely=0.5, anchor="center")
        self.next_button.destroy()

        self.bt_frame = tk.Frame(self.window3, height=40, width=280, bg="#cdeaf7")
        self.newnext_button = tk.Button(self.bt_frame, text="next", command=self.next_sh, height=1, width=5, borderwidth=3, bg="#99d4e9", activebackground="#b3deef")
        self.newnext_button.place(relx=0.33, rely=0.5, anchor="center")
        self.sh_frame.place(x=0, y=0)
        self.bt_frame.place(x=0, y=70)
        self.toggle_frame.place(x=280, y=0)

        self.new_buttons_frame = tk.Frame(self.window3, height=120, width=200, bg="#cdeaf7")
        self.manual_count = tk.Button(self.new_buttons_frame, text="Change stronghold count", command=self.override_count, borderwidth=3, bg="#99d4e9", activebackground="#b3deef")
        self.forgot_spawn = tk.Button(self.new_buttons_frame, text="Forgot to set spawn", command=self.find_from_spawn, borderwidth=3, bg="#99d4e9", activebackground="#b3deef")
        self.got_lost = tk.Button(self.new_buttons_frame, text="Pathfind from coords", command=self.find_from_coords, borderwidth=3, bg="#99d4e9", activebackground="#b3deef")
        self.new_buttons_frame.place(x=280, y=70)
        self.manual_count.place(relx=0.5, rely=0.2, anchor="center")
        self.forgot_spawn.place(relx=0.5, rely=0.5, anchor="center")
        self.got_lost.place(relx=0.5, rely=0.8, anchor="center")

        self.window3.geometry("480x190")

    def update_image(self):
        self.line, self.point = graphAddSH(self.prev, self.sh, "blue", self.c2)
        if not self.noGraph:
            graphAddSH(
                self.completed[-2], self.prev, "green", self.c2
            )  # Do not mark sh as finished if there was a reset
        plt.savefig("output.png", bbox_inches="tight", transparent=True)

    #new options for when next stronghold is in 8th ring
    def create_empty_widgets(self):
        if self.sh in self.eighth_ring and self.completed_eighth_ring<9 and self.found_empty==False:
            self.empty_frame = tk.Frame(self.window3, height=70, width=280, bg="#cdeaf7")
            self.empty_sector = tk.Label(self.empty_frame, text="8th ring, there could be no stronghold. \nIf there is no stronghold please press 'empty'.\nOtherwise, hit 'next'.", bg="#cdeaf7")
            self.empty_button = tk.Button(self.bt_frame, text="empty", command=self.empty, height=1, width=5, borderwidth=3, bg="#99d4e9", activebackground="#b3deef")
            self.empty_frame.place(x=0, y=110)
            self.empty_sector.place(relx=0.5, rely=0.5, anchor="center")
            self.empty_button.place(relx=0.66, rely=0.5, anchor="center")
        elif self.sh in self.eighth_ring and self.found_empty==False:
            self.empty() #dont make user check last 8th ring sh when you already know its empty
        elif self.sh in self.eighth_ring and self.found_empty==True:
            print("eighth ring stronghold\n")
        else:
            return

    #finds next sh location and displays it
    def next_sh(self):
        try:
            if self.empty_button.winfo_exists():
                self.empty_button.destroy()
                self.empty_frame.destroy()
                self.completed_eighth_ring += 1 #if user did not press empty, add to the completed 8th ring list
                print(f"you have found {self.completed_eighth_ring} 8th ring strongholds\n") 
        except:
            pass

        if self.count <= 128:
            updateCount(self.count)
        self.count += 1
        if self.count <= 128:
            # dist = get_dist(new_strongholds[next], new_strongholds[int(prev)])
            self.completed.append(self.prev)
            self.sh = self.unfinished[self.curr]
            self.sh_n = (round(self.sh[0] / 8), round(self.sh[1] / 8))

            #comment out if you want it to run faster
            self.update_image()

            self.noGraph = False
            self.c2 = False
            self.prev = self.sh

            self.ang = find_angle(self.completed[-1], self.sh) #find the angle to travel at on the roof
            print(f"Stronghold {str(self.count)}:\n{str(self.sh_n)} at angle {str(self.ang)}") #print in case user needs to see previous locations
            self.sh_label.config(text=f"Stronghold {str(self.count)}:\n{str(self.sh_n)} at angle {str(self.ang)}", font=('Cambria', 14))
            
            self.create_empty_widgets()
        
            self.curr = self.paths[self.curr]

        #silly
        elif self.count<=210:
            self.manual_count.config(state="disabled")
            self.got_lost.config(state="disabled")
            self.forgot_spawn.config(state="disabled")
            sillylist = ["CONGRATULATIONS", "ok you don't have to\nkeep pressing next", "the run is over", "seriously please stop", "the x is in the top right", "im getting serious now", "do you think this is a joke", "you just spent hours\nfilling in minecraft portals", "and now this is what\nyou waste your time on?", "go take a shower or something", "ok this is the end bye", ":3"]
            i = self.count
            self.sh_label.config(text=sillylist[i-129], font=('Cambria', 14))
        else:
            self.sh_label.config(text="dude", font=('Cambria', 14))

    
    def empty(self):
        print("empty sector\n")
        #fix graph stuff
        self.c2 = True
        try:
            self.point.remove()
            plt.draw()
        except:
            print("photo broken")
            pass
    
        self.count -= 1 #this is a little scuffed but it works ok look
        updateCount(self.count)
        self.empty_button.destroy()
        self.empty_frame.destroy()
        self.found_empty = True
        self.next_sh()

    #changes count manually according to user
    def override_count(self):
        try:
            self.empty_button.destroy()
            self.empty_frame.destroy()
        except:
            pass
        new_count = askinteger('', 'Please enter the number of portals you have filled.')
        self.count = new_count + 1
        updateCount(new_count)
        print(f"Stronghold {str(self.count)}:\n{str(self.sh_n)} at angle {str(self.ang)}")
        self.sh_label.config(text=f"Stronghold {str(self.count)}:\n{str(self.sh_n)} at angle {str(self.ang)}", font=('Cambria', 14))
        self.create_empty_widgets()
    
    #redoes pathfinding from spawn when user forgets to set bed
    def find_from_spawn(self):
        msg = messagebox.askyesno(message="Have you filled in the portal at the stronghold currently listed?")
        if msg:
            self.completed.append(self.prev)
            sh = self.unfinished[self.curr]
            self.sh_n = (round(sh[0] / 8), round(sh[1] / 8))
            self.line, self.point = graphAddSH(self.prev, sh, "blue", self.c2)
            if not self.noGraph:
                graphAddSH(
                    self.completed[-2], self.prev, "green", self.c2
                )  # Do not mark sh as finished if there was a reset
            plt.savefig("output.png", bbox_inches="tight", transparent=True)
            self.noGraph = False
            self.c2 = False
            self.prev = sh
            self.count += 1

        self.pos = (0, 0)
        self.get_new_path()
    
    #redoes pathfinding from specific coords if user gets lost or something idk
    def find_from_coords(self):
        msg = messagebox.askyesno(message="Have you filled in the portal at the stronghold currently listed?")
        if msg:
            self.completed.append(self.prev)
            sh = self.unfinished[self.curr]
            self.sh_n = (round(sh[0] / 8), round(sh[1] / 8))
            self.line, self.point = graphAddSH(self.prev, sh, "blue", self.c2)
            if not self.noGraph:
                graphAddSH(
                    self.completed[-2], self.prev, "green", self.c2
                )  # Do not mark sh as finished if there was a reset
            plt.savefig("output.png", bbox_inches="tight", transparent=True)
            self.noGraph = False
            self.c2 = False
            self.prev = sh
            self.count += 1

        new_coords = askstring('', 'Type out your x and z coordinates you want to start pathfinding from (OW):')
        try:
            new_pos = tuple(getIntInput(new_coords))
        except:
            messagebox.showerror(message="Something went wrong. Make sure you only input your x and z coordinate separated by a space, or copy paste the f3+c command")
            return

        if not new_pos:
            return
        else:
            self.pos = new_pos
            self.get_new_path()

    def get_new_path(self):
        try:
            self.empty_button.destroy()
            self.empty_frame.destroy()
        except:
            pass
        self.unfinished = list(set(self.unfinished) - set(self.completed))
        self.paths, self.curr = generatePath(self.unfinished, self.pos)
        # noGraph = True
        self.sh = self.unfinished[self.curr]  # Next stronghold starting from 0,0
        self.prev = self.sh
        self.completed.append(self.pos)
        # Update prompt to nether coords
        self.sh_n = (round(self.sh[0] / 8), round(self.sh[1] / 8))
        # Clean graph's in progress stuff
        try:
            self.line.remove()
            self.point.remove()
        except Exception as e:
                messagebox.showerror(message="Must've forgotten bed after finding empty 8th ring sh, or else something went really wrong")
        plt.draw()
        graphAddSH(self.pos, self.sh, "blue", self.c2)
        plt.savefig("output.png", bbox_inches="tight", transparent=True)
        self.curr = self.paths[self.curr]

        updateCount(self.count)

        self.ang = find_angle(self.completed[-1], self.sh) #find the angle to travel at on the roof
        print(f"Stronghold {str(self.count)}:\n{str(self.sh_n)} at angle {str(self.ang)}")
        self.sh_label.config(text=f"Stronghold {str(self.count)}:\n{str(self.sh_n)} at angle {str(self.ang)}", font=('Cambria', 14))
        self.create_empty_widgets()

    def start(self):
        self.window3.mainloop()


app = FindPortals()
app.start()
