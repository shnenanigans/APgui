import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pynput import keyboard
import time
import sys
from tkinter import simpledialog
from tkinter import messagebox

from constants import *
from utils import *
from strongholds import Strongholds
from strongholds import Stronghold
import random
import os
from time import sleep

"""
THINGS TO SET BACK TO NORMAL AFTER TESTING
next button disabled
qs file reading
delete print statements
2 read path qs file tests (i have no idea what this means anymore)

THINGS TO FIX
make pathfind from coords work
subprocess.run for running concord and adding concord to exe (dank)
comment code :D
fix readme
fix graph for repathfind (impossible)
place/grid in silly
leave spawn happens twice surely this gets fixed with new pathfinding
FIX X IN COORDS BOX FOR REPATHFINDING
completedcount-8 is wrong after empty sector probably
pathfinding despairge
line from empty sector to next sh because leave spawn wouldnt work
make hotkey pause not just return
make stronghold objects have the image properties
make it not create another backup when you use backups
"""

class AllPortals:
    def __init__(self):
        self.strongholds = Strongholds()

        self.next_stronghold_hotkey = ""
        self.done = False #true if you are done filling portals
        self.pathfind_pressed = False

    def start(self):
        """actually start the window and program"""
        self.update_count()
        self.create_image()
        self.build_window()
        self.create_inital_widgets()
        self.root.mainloop()

    def build_window(self):
        """creates the base starting window for the program"""
        self.root = tk.Tk()
        self.root.config(bg=peach)
        self.root.title("Find Portals")
        self.root.wm_attributes("-topmost", 0) #changes to 1 when the 'always on top' box is checked
        self.root.protocol("WM_DELETE_WINDOW", lambda: [print('destroy me...'), sys.exit(0)]) #for some reason the program doesnt stop when you close tkinter unless u have this thing

    def create_image(self):
        """create the image showing portals path and completed portals"""
        img = plt.imread("rings.png")
        plt.imshow(img, aspect="equal", extent=[-24320, 24320, -24320, 24320])
        plt.axis("off")

    def update_count(self):
        """tell the program and user how many portals are filled"""
        if (
            self.strongholds.get_completed_count() > 0
            and self.strongholds.get_completed_count()
            == self.strongholds.get_empty_sh_index()
        ):
            return #doesnt add 1 if you just found empty sector

        with open("sh_count.txt", "w+") as count_file:
            count_file.write(str(self.strongholds.get_completed_count()) + "/128\n")

        with open("fun_facts.txt", "w+") as facts_file:
            if self.strongholds.get_completed_count() == 69:
                facts_file.writelines(["nice.\n"])
            if self.strongholds.get_completed_count() == 71:
                facts_file.writelines(["BRA7-1L\n"])
            if self.strongholds.get_completed_count() == 128:
                facts_file.writelines(["DONE!\n"])
            if is_prime(self.strongholds.get_completed_count()):
                facts_file.writelines(["(prime)\n"])

    def complete_sh(self, sh):
        """add stronghold to completed shs array and update count"""
        self.strongholds.complete_sh(sh)
        self.update_count()

    def lock_entry(
        self, ring: int, entry: object, button: object, next_button: object
    ) -> None:
        """when user presses lock, check if coords are in correct ring and in the right format, add them to first strongholds array"""
        try:
            sh = tuple(parse_input(entry.get()))
            if len(sh) != 2:
                raise Exception
        except Exception as e:
            print(e)
            tk.messagebox.showerror(
                message="Something went wrong. Make sure you only input your x and z coordinate separated by a space, or copy paste the f3+c command"
            )
            return

        if get_stronghold_ring(sh) == 0:
            if not tk.messagebox.askyesno(
                message="Are you sure this is in the right ring? This stronghold does not appear to be in any ring."
                + "\nThis is possible to occur with biome snapping, but quite rare. If you are sure then click 'yes', otherwise hit 'no' and enter coords again"
            ):
                return
        elif ring != get_stronghold_ring(sh):
            if not tk.messagebox.askyesno(
                message="Are you sure this is in the right ring? Looks like this is a stronghold in ring "
                + str(get_stronghold_ring(sh))
                + ".\nIf you are completely sure this is in the right ring and my program is stupid then click 'yes', otherwise hit 'no' and enter coords again"
            ):
                return
            
        sh = Stronghold(sh, ring)
        self.complete_sh(sh)
        self.strongholds.set_current_location(sh.get_coords())
        self.update_image()
        plt.draw()
        # plt.savefig("output.png", bbox_inches="tight", transparent=True)

        entry.config(state="disabled", cursor="heart") # <3
        button.config(state="disabled", cursor="heart")


        if self.strongholds.get_completed_count() == 8:
            next_button.config(state="normal") # allow user to press next

    def check_next(self):
        """checks each sh location is locked before changing window setup and predicts other sh locations"""

        self.next_button.config(
            state="disabled"
        )  # very silly things happen if you press the next button twice...

        backup_strongholds(self.strongholds.completed)

        self.strongholds.estimate_sh_locations() # now estimations has sh objects

        write_nodes_qs_file(
            self.strongholds.get_last_sh_coords(), self.strongholds.estimations #estimations does not contain stronghold objects yet, just tuples
        )

        messagebox.showinfo(
            title=None,
            message="Open the strongholds.qs file in this directory with concorde, press solve in the top left, solve it, save it, then press OK.",
        )

        path = {}
        while path == {}:
            path = read_path_qs_file()
            sleep(3)

        if path=="stop": #not sure if this actually does anything at all
            self.next_button.config(
                state="normal"
            )
            self.strongholds.estimations=[]
            return

        self.strongholds.sort_estimations_order_by_path(path) 

        image_ests = [] # has to have a list of just coords cause idk how else to do the next part
        for sh in self.strongholds.estimations:
            image_ests.append(sh.get_coords())

        try:
            plt.scatter(
                *zip(*image_ests),
                c="gray",
                s=20,
            ) # puts fun little dots on the graph
            plt.draw()
        except:
            self.strongholds.estimations = []
            self.next_button.config(state="normal")
            tk.messagebox.showerror("no", "solve and save the qs file idiot") # gets here if you forget to have a saved qs file while in testing configuration (i am the idiot)
            return

        # get rid of all widgets from the first-strongholds part
        for lock in self.locks:
            lock.destroy()
        for sh in self.sh_labels:
            sh.destroy()
        for entry in self.entries:
            entry.destroy()
        self.lock_order_label.destroy()
        self.backups_button.destroy()

        #self.setspawn_button.destroy()
        self.checkring.destroy()
        self.setup_next()
        self.next_button.destroy()
        self.display_next_sh()
        self.update_image()

    def create_inital_widgets(self):
        """create the window for entering your first 8 sh locations"""
        # toggles window always on top or not
        self.toggle_frame = tk.Frame(self.root)
        self.toggle_frame.grid(row=1, column=6)
        always_on_top = tk.IntVar(self.root)
        self.topmost_toggle = tk.Checkbutton(
            self.toggle_frame,
            bg=peach,
            activebackground=peach,
            text="Always On Top",
            variable=always_on_top,
            onvalue=1,
            offvalue=0,
            command=lambda: self.root.wm_attributes("-topmost", always_on_top.get()),
        )
        self.topmost_toggle.pack()

        #button to use latest backups folder so user doesnt have to manually put them all in
        self.backups_button = tk.Button(
            self.root,
            bg=darkpeach,
            activebackground=lightpeach,
            text="Use Last Backup",
            command=self.use_backup,
        )
        self.backups_button.grid(row=2, column=6)

        # labels for the entry boxes and locks to save each coord into a list of first strongholds
        self.sh_labels = [
            tk.Label(self.root, bg=peach, text=f"sh {i}:") for i in range(1, 9)
        ]
        [self.sh_labels[i].grid(row=i, column=1) for i in range(0, 8)]

        self.entries = [
            tk.Entry(
                self.root,
                width=40,
                borderwidth=5,
                bg=lightpeach,
            )
            for i in range(0, 8)
        ]
        [self.entries[i].grid(row=i, column=2, columnspan=3) for i in range(0, 8)]

        # goes to next stage, only works once all 8 locations have been locked
        # IF TESTING U CAN SET THE STATE TO "normal" SO U CAN EASILY USE THE TEST SH LOCATIONS IN STRONGHOLDS.PY
        self.next_button = tk.Button(
            self.root,
            state="disabled",
            text="next",
            command=self.check_next,
            bg=darkpeach,
            activebackground=lightpeach,
        )

        # self.setspawn_button = tk.Button(
        #     self.root,
        #     text="Give Spawnpoint",
        #     command=self.set_spawn,
        #     bg=darkpeach,
        #     activebackground=lightpeach,
        # )

        self.checkring = tk.Button(
            self.root,
            text="Check Ring",
            command=self.find_sh_ring,
            bg=darkpeach,
            activebackground=lightpeach,
        )

        self.locks = [
            tk.Button(
                self.root,
                text="lock",
                borderwidth=3,
                bg=darkpeach,
                activebackground=lightpeach,
            )
            for i in range(0, 8)
        ]
        for i in range(0, 8):
            self.locks[i].config(
                command=lambda i=i: self.lock_entry(
                    i + 1, self.entries[i], self.locks[i], self.next_button
                )
            )
        [self.locks[i].grid(row=i, column=5) for i in range(0, 8)]

        # label telling user to lock in order so that the image updates accurately
        self.lock_order_label = tk.Label(
            self.root,
            text="Please make sure you\nlock strongholds in the\norder you found them",
            bg=peach,
        )
        self.lock_order_label.grid(row=3, column=6, rowspan=3)

        #self.setspawn_button.grid(row=7, column=6)
        self.checkring.grid(row=7, column=6)
        self.next_button.grid(row=9, column=6)

    def use_backup(self):
        path = (os.getcwd() + "\\backups")
        with open(path + "\\" + os.listdir(path)[0], "r") as f:
            lines = f.readlines()
            coords=[]
            for sh in lines[:-1]:
                coords.append(sh[:-1])
            coords.append(lines[-1])
        for coord in coords:
            sh = tuple(parse_input(coord))
            sh = Stronghold(sh, get_stronghold_ring(sh))
            self.complete_sh(sh)
            self.strongholds.set_current_location(sh.get_coords())
            self.update_image()
            plt.draw()
        self.check_next()
        return

    def setup_next(self):
        """changes entire window setup to just display sh coords and some options"""
        self.c2 = False
        self.noGraph = False # i still have no idea what either of these do

        #Get the current screen width and height
        screen_height = self.root.winfo_screenheight() #1080
        screen_width = self.root.winfo_screenwidth() #1920

        self.root.config(bg=lightblue)
        self.toggle_frame.config(height=70, width=200, bg=lightblue)
        self.topmost_toggle.config(bg=lightblue, activebackground=pressblue)

        # puts some nice lil frames in the gui and then the buttons go in the frames and its 10000x easier to have everything where you want it to go
        self.sh_frame = tk.Frame(self.root, height=(70/1080)*screen_height, width=(280/1920)*screen_width)             
        self.bt_frame = tk.Frame(self.root, height=(40/1080)*screen_height, width=(280/1920)*screen_width)
        self.new_buttons_frame = tk.Frame(self.root, height=(120/1080)*screen_height, width=(200/1920)*screen_width)
        self.inst_frame = tk.Frame(self.root, height=(70/1080)*screen_height, width=(280/1920)*screen_width)

        #frames inside frame for next/empty buttons
        self.newnext_button_frame = tk.Frame(self.bt_frame, height=(40/1080)*screen_height, width=(140/1920)*screen_width)
        self.empty_button_frame = tk.Frame(self.bt_frame, height=(40/1080)*screen_height, width=(140/1920)*screen_width)
        #put button frames into bt_frame
        self.newnext_button_frame.grid(row=1, column=1)
        self.empty_button_frame.grid(row=1, column=2)

        #make sure frames dont shrink to fit widget sizes
        self.toggle_frame.pack_propagate("false")
        self.sh_frame.pack_propagate("false")
        self.inst_frame.pack_propagate("false")
        self.newnext_button_frame.pack_propagate("false")
        self.empty_button_frame.pack_propagate("false")
        #grid propogate cause the stuff in them uses grid not pack
        self.bt_frame.grid_propagate("false")
        self.new_buttons_frame.grid_propagate("false")
        #the whole point of all of that is to let the user resize the window to hide the useless/rarely used buttons and info, and only display coords and next button

        #center the widgets (thanks pncake)
        self.new_buttons_frame.grid_columnconfigure(0, weight=1)
        self.new_buttons_frame.grid_rowconfigure(0, weight=1)
        self.new_buttons_frame.grid_rowconfigure(1, weight=1)
        self.new_buttons_frame.grid_rowconfigure(2, weight=1)
        self.toggle_frame.grid_rowconfigure(0, weight=1)

        #labels for sh location and when to set spawn/not set spawn/find empty sector
        self.sh_label = tk.Label(self.sh_frame, text="")
        self.inst_label = tk.Label(self.inst_frame, text="")

        #buttons that go in bt_frame
        #next button to display next sh
        self.newnext_button = tk.Button(
            self.newnext_button_frame,
            text="next",
            command=self.next_sh,
            height=1,
            width=5,
            borderwidth=3,
        )
        #press when found empty sector
        self.empty_button = tk.Button(
            self.empty_button_frame,
            text="empty",
            command=self.empty,
            height=1,
            width=5,
            borderwidth=3,
            state="disabled"
        )

        #buttons that go in new_buttons_frame
        #set hotkey that displays next sh
        self.set_hotkey_button = tk.Button(
            self.new_buttons_frame,
            text="Next SH Hotkey",
            command=self.set_next_hotkey,
            borderwidth=3,
        )
        #button for repathfinding probably shouldve found a better name than 'got lost' oh well
        # self.got_lost = tk.Button(
            # self.new_buttons_frame,
            # text="Pathfind from coords",
            # command=self.find_from_coords,
            # borderwidth=3,
        # )
        
        #button for checking what ring coords are
        self.check_ring_bt = tk.Button(
            self.new_buttons_frame,
            text="check ring",
            command=self.find_sh_ring,
            borderwidth=3,
        )

        #give program your spawnpoint for more accurate optimizations
        self.setspawn_button = tk.Button(
            self.new_buttons_frame,
            text="Give Spawnpoint",
            command=self.set_spawn,
            borderwidth=3,
        )
        if self.strongholds.spawn != (0, 0):
            self.setspawn_button.config(text=f"Spawnpoint: {self.strongholds.spawn}")

        self.set_bg_colours()

        #put the stuff into the frames
        self.topmost_toggle.pack(pady=20) # center the toggle

        self.sh_label.pack(fill="both")
        self.inst_label.pack(fill="both")

        self.set_hotkey_button.grid(row=0)
        self.setspawn_button.grid(row=1)
        #self.got_lost.grid(row=2)
        self.check_ring_bt.grid(row=2)

        self.newnext_button.pack()
        self.empty_button.pack()

        #place all the frames
        self.toggle_frame.grid(row=1, column=2, rowspan=1)
        self.sh_frame.grid(row=1, column=1)
        self.bt_frame.grid(row=2, column=1)
        self.inst_frame.grid(row=3, column=1)
        self.new_buttons_frame.grid(row=2, rowspan=2, column=2)

        # make a new tkinter window for the graph, has to be toplevel not a whole new tkinter thingy cause it cant multithread or something
        image=tk.Toplevel()
        image.title("Portals Graph")
        image.config(bg=lightblue)
        
        #make sure user can't accidentally close the image window cause there's no way to get it back
        #pressing q will close the window though for some reason i give up trying to fix
        def on_closing(): messagebox.showinfo("no", "You must close the main program to close this window.")
        image.protocol("WM_DELETE_WINDOW", on_closing)

        #using meaningful and descriptive variable names is a fundamental aspect of writing clean, maintainable, and understandable code. It's a practice that not only benefits you but also anyone who interacts with your code, now or in the future.
        aasdfae = plt.gcf()
        aasdfae.set_facecolor(lightblue)
        thang = FigureCanvasTkAgg(figure=aasdfae, master=image)
        thang.draw()
        thang.get_tk_widget().pack()

    def set_spawn(self):
        spawn = self.strongholds.set_spawn()
        self.setspawn_button.config(text=f"Spawnpoint: {spawn}")

    def update_image(self):
        """add stronghold to graph with the right colours"""
        try: #last_path is dot placed on last sh
            last_path = self.strongholds.completed[-1].get_leave_spawn()
            match last_path:
                case 0: 
                    colour = "green"
                case 1:
                    colour = "purple"
                case 2:
                    colour = "yellow"
                case 3:
                    colour = "yellow"
        except IndexError:
            pass

        if self.strongholds.get_current_location() == self.strongholds.spawn:
            colour = "yellow"

        self.graph_point(self.strongholds.get_last_sh_coords(), colour)

        if self.strongholds.get_current_location() == self.strongholds.spawn:
            self.graph_line(
                self.strongholds.get_last_sh_coords(-2),
                self.strongholds.get_last_location(), #setting curr location twice could fix graphing issues cause of this thing
                "green",
            )
        else:
            self.graph_line(
                self.strongholds.get_current_location(),
                self.strongholds.get_last_location(),
                "green",
            )

        try: #set colour of point on next sh
            match self.strongholds.next_stronghold().get_leave_spawn():
                case 0:
                    colour = "blue"
                case 1:
                    colour = "purple"
                case 2:
                    colour = "yellow"
                case 3:
                    colour = "yellow"
        except IndexError:
            pass

        # line to next sh always blue, dot colour set above
        try:
            self.graph_point(self.strongholds.get_next_sh_coords(), colour)
            self.graph_line(
                self.strongholds.get_current_location(),
                self.strongholds.get_next_sh_coords(),
                "blue",
            )
        except IndexError as e:
            pass
        plt.draw()

    def graph_point(self, coords, colour):
        plt.scatter(coords[0], coords[1], c=colour, s=30)
        plt.draw()

    def graph_line(self, start, end, colour):
        plt.arrow(
            start[0],
            start[1],
            (end[0] - start[0]),
            (end[1] - start[1]),
            color=colour,
            width=0.0001,
            head_width=0,
            head_length=0,
            length_includes_head=True,
        )
        plt.draw()

    def find_sh_ring(self) -> int:
        """find what ring coords given by user are in"""
        new_coords = tk.simpledialog.askstring(
            ":D",
            "Type out the x and z coordinates of the stronghold you want to check the ring of.",
        )
        try:
            sh_coords = tuple(parse_input(new_coords))
        except:
            tk.messagebox.showerror(
                message="Something went wrong. Make sure you only input your x and z coordinate separated by a space, or copy paste the f3+c command"
            )
            return
        try:
            ring = get_stronghold_ring(sh_coords)
        except:
            tk.messagebox.showinfo(
                message="These coords do not appear to be in any ring."
            )
            return
        
        if ring == 0:
            tk.messagebox.showinfo(
                message="These coords do not appear to be in any ring."
            )
            return
        
        tk.messagebox.showinfo(
            message=f"ring {get_stronghold_ring(sh_coords)}"
        )
        return

    def set_bg_colours(self):
        """colour codes the spawn point things so people dont forget surely they wont forget right suuuuurely"""
        match self.strongholds.next_stronghold().get_leave_spawn():
            case 0:
                frame = lightblue
                press = pressblue
                button = buttonblue
            case 1:
                frame = spawnpurple
                press = presspurple
                button = buttonpurple
            case 2:
                frame = spawngreen
                press = pressgreen
                button = buttongreen
            case 3:
                frame = spawngreen
                press = pressgreen
                button = buttongreen
        
        #bg=colour
        self.root.config(bg=frame)
        self.bt_frame.config(bg=frame)
        self.toggle_frame.config(bg=frame)
        self.sh_frame.config(bg=frame)
        self.new_buttons_frame.config(bg=frame)
        self.topmost_toggle.config(bg=frame, activebackground=press)
        self.newnext_button.config(bg=button, activebackground=press)
        self.set_hotkey_button.config(bg=button, activebackground=press)
        #self.got_lost.config(bg=button, activebackground=press)
        self.check_ring_bt.config(bg=button, activebackground=press)
        self.sh_label.config(bg=frame)
        self.setspawn_button.config(bg=button, activebackground=press)
        self.inst_frame.config(bg=frame)
        self.inst_label.config(bg=frame)
        self.empty_button.config(bg=button, activebackground=press)
        self.newnext_button_frame.config(bg=frame)
        self.empty_button_frame.config(bg=frame)

    def set_inst_label(self):
        """set the label containing instructions for each sh spawn points"""
        match self.strongholds.next_stronghold().get_leave_spawn():
            case 0:
                if self.strongholds.next_stronghold().is_8th_ring():
                    write = "8th ring, there could be\nno stronghold"
                else:
                    write = ""
            case 1:
                write = "LEAVE YOUR SPAWN AT THE NEXT STRONGHOLD.\nDO NOT BREAK BED AFTER FILLING PORTAL."
            case 2:
                write = "DO NOT SET YOUR SPAWN\nAT THE NEXT STRONGHOLD"
            case 3:
                write = "DO NOT SET YOUR SPAWN\nAT THE NEXT STRONGHOLD"
        self.inst_label.config(text=write)
        self.set_bg_colours()
        return

    def display_next_sh(self):
        """edit gui to show new coords and angle"""
        self.set_inst_label()
        sh_data = self.strongholds.get_next_sh()
        print(
            "Stronghold {0}:\n{1} at angle {2}".format(
                sh_data[0], sh_data[1], sh_data[3]
            )
        )  # print in case user needs to see previous locations
        print(f"GET LEAVE SPAWN = {self.strongholds.next_stronghold().get_leave_spawn()}\n")
        self.sh_label.config(
            text="Stronghold {0}:\n{1} at angle {2}".format(
                sh_data[0], sh_data[1], sh_data[3]
            ),
            font=("Cambria", 14),
        )

    def next_sh(self):
        """completes the last stronghold and finds coords of next one and checks all the 8th ring stuff and optimizations and if its the last sh and whatever, last_empty is true if it is the empty sector"""

        if self.newnext_button.cget("state") == "disabled": # stops the hotkey from pressing next when button is disabled
            return

        if self.strongholds.next_stronghold().is_8th_ring():
            self.strongholds.add_completed_8th_ring()

        # optimization for when last 8th ring is empty
        if self.strongholds.completed_8th_ring == 9 and not self.strongholds.empty_index:

            #for elem in self.strongholds.estimations[self.strongholds.get_completed_count()+1:]:
            for i in range(len(self.strongholds.estimations)-self.strongholds.get_completed_count()+1): # check strongholds left in estimations for empty sector, elem contains sh object
                elem = self.strongholds.estimations[i+self.strongholds.get_completed_count()+1]
                if elem.get_ring()==8:
                    elem.set_empty(True)
                    self.complete_sh(elem) # puts empty ring as the last completed sh
                    self.strongholds.empty_index = self.strongholds.get_completed_count()-1 # sets index of empty sector in completed sh array
                    self.strongholds.estimations[i+self.strongholds.get_completed_count()-1].set_leave_spawn(0) #otherwise program will tell user not to set spawn, but then skip the 8th ring sh taking them right to the next one.
                    self.strongholds.estimations.remove(elem) # gets it out of estimations for the new pathfinding
                    self.graph_point(elem.get_coords(), "red")
                    break
            self.strongholds.add_completed_8th_ring()
            #self.find_from_coords(True)
            return
        
        try:
            if self.strongholds.next_stronghold(2).is_8th_ring() and not self.strongholds.empty_index: #next_stronghold(2) because it hasnt been completed yet (happens below)
                self.empty_button.config(state="normal")
            else:
                self.empty_button.config(state="disabled")
        except IndexError:
            pass #error when u get to the end

        # very important
        if self.done:
            try:
                self.sh_label.config(text=silly_list[self.silly_count])
                self.silly_count += 1
            except IndexError:
                # self.new_buttons_frame.destroy()
                # self.toggle_frame.destroy()
                # self.sh_frame.destroy()
                # self.inst_frame.destroy()
                # self.bt_frame.pack()
                # self.bt_frame.config(background="pink")
                # self.bt_frame.lift()
                # self.newnext_button.config(command=self.movebutton)
                pass #sadpag i am too lazy to make this thing work

        elif self.strongholds.get_finished(): # means the user is done filling portals and gives the graph a pretty little star :D
            #this entire thing is broken idk man
            try:
                if (
                    self.strongholds.estimations.index(
                        self.strongholds.next_stronghold()
                    )
                    != self.strongholds.get_completed_count()
                    + len(self.strongholds.estimations)
                    - 129
                ):
                    return
                self.complete_sh(self.strongholds.estimations[self.strongholds.get_completed_count()])
                self.strongholds.set_current_location(
                    self.strongholds.get_last_sh_coords()
                )
                plt.scatter(
                    self.strongholds.get_last_sh_coords()[0],
                    self.strongholds.get_last_sh_coords()[1],
                    c="green",
                    s=200,
                    marker="*",
                )
                self.graph_line(
                    self.strongholds.get_current_location(),
                    self.strongholds.get_last_location(),
                    "green",
                )
                plt.draw()
            except IndexError:
                pass
            self.done = True
            self.silly_count = 0

        else:
            self.complete_sh(self.strongholds.estimations[self.strongholds.get_completed_count()-8]) # will probably change after empty sector
            try:
                self.optimize_next_3_nodes()
            except IndexError:
                pass #has to be try/except cause this thing gives an error in the gui colour updates idk why man but then if u dont pass the error it makes the second last line blue in the graph
            self.update_image()
            self.display_next_sh()

    def optimize_next_3_nodes(self):
        """sets your current location at your current location, which is complicated when you spawn at previous shs or 0 0"""
        #last sh is usually current location since this runs after sh is completed
        self.strongholds.set_current_location(self.strongholds.get_last_sh_coords())
        if self.pathfind_pressed:
            self.strongholds.set_current_location(self.pos)
            self.pathfind_pressed=False
            return
        if self.strongholds.last_stronghold().get_leave_spawn() == 2: # spawn was left behind
            self.strongholds.set_current_location(
                self.strongholds.get_last_sh_coords(-2) #sets location at 2nd last sh coords which is where your spawn was left i think
            )
        if self.strongholds.last_stronghold().get_leave_spawn()==3:
            self.strongholds.set_current_location(self.strongholds.spawn) # sets location at spawn when it was optimal

    def empty(self):
        """tells the program you have found the empty sector, runs when empty button is pressed. graphs empty sector as red"""
        print("empty sector\n")
        self.empty_button.config(state="disabled")
        self.strongholds.next_stronghold().set_empty(True)
        self.strongholds.empty_index = self.strongholds.get_completed_count()
        self.graph_point(self.strongholds.get_next_sh_coords(), "red")
        self.next_sh()

    def find_from_coords(self, auto: bool=False):
        """sets current location. Auto is false when user presses the button, true when program finds 8th ring optimization on its own"""
        # has to find out if sh listed has been completed or not and maybe adds it to completed array
        self.newnext_button.config(state="disabled")
        if not auto:
            msg = tk.messagebox.askyesno(
                message="Have you filled in the portal at the stronghold currently listed?"
            )
            if msg:
                self.complete_sh(Stronghold(self.strongholds.get_next_sh_coords(), get_stronghold_ring(self.strongholds.get_next_sh_coords()))) #setting 'empty'to 'False' could theoretically cause a bug if the user does this on the empty 8th ring sh before pressing 'empty'... but that wouldnt happen probably... surely...
                self.update_image()

            new_coords = tk.simpledialog.askstring(
                "",
                "Type out your x and z coordinates you want to start pathfinding from (OW):",
            )

            try:
                new_pos = tuple(parse_input(new_coords))
            except:
                tk.messagebox.showerror(
                    message="Something went wrong. Make sure you only input your x and z coordinate separated by a space, or copy paste the f3+c command"
                )
                self.newnext_button.config(state="normal")
                return

            if not new_pos:
                tk.messagebox.showerror(
                    message="Something went wrong. Make sure you only input your x and z coordinate separated by a space, or copy paste the f3+c command"
                )
                self.newnext_button.config(state="normal")
                return
            self.pos = new_pos
            self.get_new_path()
            self.pathfind_pressed = True

        else:
            if self.strongholds.next_stronghold().get_leave_spawn()==2:
                self.pos = self.strongholds.get_last_sh_coords() #7th ring sh where spawn was left
            else:
                self.pos = self.strongholds.get_next_sh_coords() #8th ring if spawn was not left
            self.pathfind_pressed = True
            self.get_new_path()




    def get_new_path(self):
        """redoes pathfinding with only the strongholds left and a new current location"""
        print("GET NEW PATH")
        #ests never contains empty sh, it will be in completed array
        reverse_ests = self.strongholds.estimations[self.strongholds.get_completed_count() - 8:] # for some reason this makes it backwards so we gotta reverse it
        unfinished_ests = reverse_ests[::-1] # using the reverse method didnt work dont ask idk
        copied_estimations = self.strongholds.estimations.copy()

        #get new path
        write_nodes_qs_file(
            self.pos, unfinished_ests
        )

        sorted_estimations = sort_estimations_order_by_path(read_path_qs_file(), unfinished_ests, self.strongholds.spawn) #THIS GOES TO THE SORT_ESTIMATIONS IN UTILS ITS CONFUSING I KNOW IM SORRY
        #ok that thing returns the sorted and optimized path for just the strongholds we havent been to yet
        #now we gotta put them back into strongholds.estimations by overwriting whats already there
        j=0
        for i in range(self.strongholds.get_completed_count()-8, len(self.strongholds.estimations)):
            self.strongholds.estimations[i] = sorted_estimations[j]
            j += 1

        # for i in range(len(self.strongholds.estimations)):
            # print(copied_estimations[i].get_coords(), self.strongholds.estimations[i].get_coords(), copied_estimations[i]==self.strongholds.estimations[i])

        try:
            self.optimize_next_3_nodes()
        except IndexError:
            pass
        #self.update_image()
        #self.display_next_sh()
        print("DONE GET NEW PATH")
        self.newnext_button.config(state="normal")

    def set_next_hotkey(self):
        """sets hotkey to go to the next stronghold when you press the set hotkey button, or esc to remove hotkey."""
        colour = self.set_hotkey_button.cget("background")
        try:
            self.listener.stop()
        except:
            pass
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.next_stronghold_hotkey = simpledialog.askstring("Input", "Enter a hotkey:")
        if self.next_stronghold_hotkey == "":
            self.set_hotkey_button.config(text="Next SH Hotkey", bg=colour)
        #if the graph is your active window and you press Q it closes it, and K and L will mess it up. Still happens if they arent your hotkey but hopefully this helps prevent it
        elif self.next_stronghold_hotkey == "k" or self.next_stronghold_hotkey == "l" or self.next_stronghold_hotkey == "q":
            tk.messagebox.showerror("no", "You cannont make this your hotkey.")
            self.set_hotkey_button.config(text="Next SH Hotkey", bg=colour)
            self.next_stronghold_hotkey = ""
        else:
            try:
                print("set hotkey to " + self.next_stronghold_hotkey) #user can press esc to set no hotkey. gives a typerror which is kinda goofy but thisll work
            except:
                self.set_hotkey_button.config(text=f"Next SH Hotkey", bg=colour)
            self.set_hotkey_button.config(text=f"Next SH Hotkey: {self.next_stronghold_hotkey}", bg=colour)
            self.listener.start()

    def on_press(self, key):
        """runs every time any key is pressed and checks if it's the next sh hotkey"""
        if get_key_string(key) == self.next_stronghold_hotkey:
            self.newnext_button.invoke()
            return

    def movebutton(self):
        """moves the next button around like an aim trainer hehehehe"""
        x=random.uniform(0.1,0.9)
        y=random.uniform(0.1,0.9)
        self.newnext_button.place(relx=x, rely=y)
        self.newnext_button.lift()