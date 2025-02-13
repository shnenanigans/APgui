import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pynput import keyboard
from sys import exit
from tkinter import simpledialog
from tkinter import messagebox
from lincolnsolver import make_stronghold_list

from constants import *
from utils import *
from os import getcwd, listdir

"""
todo
fix backups not using most recent file
add set origin in case nether roof portal is far from 0, 0
next just gives an error at the end of the run
add warning if next button is pressed too fast to have filled in a portal (Aware)
make a repathfind button in case someone messes up (i really do not want to do this the thought of repathfinding makes me want to throw my monitor at the wall)
add found/filled option on first 8 for coop mode
NO ORIGIN ON 8TH RING IN CASE ITS EMPTY SECTOR i hate this stupid awful empty sector

to make exe:
pyinstaller --onefile --hiddenimport=ortools.constraint_solver.routing_parameters_pb2 main.py
make sure it's parameters not enums even though the regular import is called routing enums
"""

class AllPortals:
    def __init__(self):
        self.next_stronghold_hotkey = ""
        self.done = False #true if you are done filling portals
        self.completed_count = 0
        self.first8 = []
        self.create_backups_file = True

    def start(self):
        """actually start the window and program"""
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
        self.root.protocol("WM_DELETE_WINDOW", lambda: [print('destroy me...'), exit(0)]) #for some reason the program doesnt stop when you close tkinter unless u have this thing (thanks desktopfolder)
        def on_closing(): #putting this in the lambda didnt work :(
            if self.completed_count <=8:
                shs = self.first8
                if len(shs)<=8:
                    with open("emergency backup for stupid idiots.txt", "w") as idiot:
                        stupid = ""
                        for sh in shs:
                            stupid += f"{sh[0]} {sh[1]}\n"
                        idiot.writelines(stupid)
                print('destroy me...')
                exit(0)
            self.root.protocol("WM_DELETE_WINDOW", on_closing)

    def create_image(self):
        """create the image showing portals path and completed portals"""
        img = plt.imread("rings.png")
        plt.imshow(img, aspect="equal", extent=[-24320, 24320, -24320, 24320])
        plt.axis("off")

    def add_count(self):
        """count 1 more stronghold and write to files for obs"""
        self.completed_count += 1

        with open("sh_count.txt", "w+") as count_file:
            count_file.write(str(self.completed_count) + "/129\n")

        with open("fun_facts.txt", "w+") as facts_file:
            if self.completed_count == 69:
                facts_file.writelines(["nice.\n"])
            if self.completed_count == 71:
                facts_file.writelines(["BRA7-1L\n"])
            if self.completed_count == 129:
                facts_file.writelines(["DONE!\n"])
            if is_prime(self.completed_count):
                facts_file.writelines(["(prime)\n"])

    def check_next(self):
        """checks each sh location is locked before changing window setup and predicts other sh locations"""

        self.next_button.config(
            state="disabled"
        )  # very silly things happen if you press the next button twice...

        if self.create_backups_file:
            backup_strongholds(self.first8)

        def estimate_sh_locations(first8) -> None:
            """Predict location of all the other strongholds using the first 8, in overworld coords"""
            points = []
            points.append(first8[-1]) #points must contain starting point
            for ring, strongholds in enumerate(constants.strongholds_per_ring):
                for sh in first8:
                    if get_stronghold_ring(sh)-1 != ring:
                        continue
                    x, z = sh
                    magnitude = constants.magnitude_per_ring[ring]
                    angle = np.arctan2(z, x)
                    for i in range(strongholds - 1):
                        angle += (2 * np.pi) / strongholds
                        estimate_x = magnitude * np.cos(angle)
                        estimate_z = magnitude * np.sin(angle)

                        points.append((round(estimate_x), round(estimate_z)))

                    break
            return points

        points = estimate_sh_locations(self.first8)

        self.strongholds = make_stronghold_list(points, self.first8) #contains sh objects in order of completion
        print(f"There are {len(self.strongholds)} strongholds")
        for sh in self.strongholds:
            ow_coords = sh.get_coords()
            nether_coords = get_nether_coords(ow_coords)
            angle = sh.get_angle()
            spawn = sh.get_set_spawn()
            print(f"overworld: {ow_coords}, nether: {nether_coords}, angle: {angle}, set spawn: {spawn}")


        plt.scatter(
            *zip(*points),
            c="gray",
            s=20,
        ) # puts fun little dots on the graph
        plt.draw()


        # get rid of all widgets from the first-strongholds part
        for lock in self.locks:
            lock.destroy()
        for sh in self.sh_labels:
            sh.destroy()
        for entry in self.entries:
            entry.destroy()
        self.lock_order_label.destroy()
        self.backups_button.destroy()

        self.checkring.destroy()
        self.setup_next()
        self.next_button.destroy()
        self.display_next_sh()
        self.make_initial_image()

    def lock_entry(self, ring: int, entry: object, button: object, next_button: object) -> None:
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
            
        self.first8.append(sh) #first8 contains only tuples of coords
        self.add_count()

        entry.config(state="disabled", cursor="heart") # <3
        button.config(state="disabled", cursor="heart")

        if len(self.first8) == 8:
            next_button.config(state="normal") # allow user to press next

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
        self.next_button = tk.Button(
            self.root,
            state="disabled",
            text="next",
            command=self.check_next,
            bg=darkpeach,
            activebackground=lightpeach,
        )

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

        self.checkring.grid(row=7, column=6)
        self.next_button.grid(row=9, column=6)

    def use_backup(self):
        path = (getcwd() + "\\backups")
        with open(path + "\\" + listdir(path)[0], "r") as f:
            lines = f.readlines()
            coords=[]
            for sh in lines[:-1]:
                coords.append(sh[:-1])
            coords.append(lines[-1])
        for coord in coords:
            sh = tuple(parse_input(coord))
            self.first8.append(sh)
        print("showing first 8")
        for sh in self.first8:
            print(sh)
        self.completed_count = 8
        self.create_backups_file = False
        self.check_next()
        return

    def setup_next(self):
        """changes entire window setup to just display sh coords and some options"""
        self.c2 = False
        self.noGraph = False # i still have no idea what either of these do

        #if any of the frames and grid stuff in here make no sense it's probably because of previously existing deleted things but it works so i havent checked

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

        #frame inside frame for next button
        self.newnext_button_frame = tk.Frame(self.bt_frame, height=(40/1080)*screen_height, width=(140/1920)*screen_width)
        #put button frames into bt_frame
        self.newnext_button_frame.grid(row=1, column=1)

        #make sure frames dont shrink to fit widget sizes
        self.toggle_frame.pack_propagate("false")
        self.sh_frame.pack_propagate("false")
        self.inst_frame.pack_propagate("false")
        self.newnext_button_frame.pack_propagate("false")
        #grid propogate cause the stuff in them uses grid not pack
        self.bt_frame.grid_propagate("false")
        self.new_buttons_frame.grid_propagate("false")
        #the whole point of all of that is to let the user resize the window to hide the useless/rarely used buttons and info, and only display coords and next button even though no one does this anyway yippee

        #center the widgets (thanks pncake)
        self.new_buttons_frame.grid_columnconfigure(0, weight=1)
        self.new_buttons_frame.grid_rowconfigure(0, weight=1)
        self.new_buttons_frame.grid_rowconfigure(1, weight=1)
        self.new_buttons_frame.grid_rowconfigure(2, weight=1)
        self.toggle_frame.grid_rowconfigure(0, weight=1)

        #labels for sh location and when to set spawn/not set spawn
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

        #buttons that go in new_buttons_frame
        #set hotkey that displays next sh
        self.set_hotkey_button = tk.Button(
            self.new_buttons_frame,
            text="Next SH Hotkey",
            command=self.set_next_hotkey,
            borderwidth=3,
        )
        
        #button for checking what ring coords are
        self.check_ring_bt = tk.Button(
            self.new_buttons_frame,
            text="check ring",
            command=self.find_sh_ring,
            borderwidth=3,
        )
        self.set_bg_colours()

        #put the stuff into the frames
        self.topmost_toggle.pack(pady=20) # center the toggle

        self.sh_label.pack(fill="both")
        self.inst_label.pack(fill="both")

        self.set_hotkey_button.grid(row=0)
        self.check_ring_bt.grid(row=2)

        self.newnext_button.pack()

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

    def display_next_sh(self):
        """edit gui to show new coords and angle"""
        self.set_inst_label()
        sh = self.strongholds[self.completed_count]
        coords = sh.get_coords()
        nether_coords = get_nether_coords(coords)
        angle = sh.get_angle()
        print(
            "Stronghold {0}:\n{1} at angle {2}".format(
                self.completed_count+1, nether_coords, angle #display number for next sh, which has not been completed yet
            )
        )  # print in case user needs to see previous locations
        self.sh_label.config(
            text="Stronghold {0}:\n{1} at angle {2}".format(
                self.completed_count+1, nether_coords, angle
            ),
            font=("Cambria", 14),
        )

    def set_inst_label(self):
        """set the label containing instructions for each sh spawn points"""
        spawn = self.strongholds[self.completed_count].get_set_spawn() #count == index of next(current) stronghold because count starts at 1
        match spawn:
            case 0:
                if self.strongholds[self.completed_count].is_8th_ring():
                    write = "8th ring, there could be\nno stronghold"
                else:
                    write = ""
            case 1:
                write = "LEAVE YOUR SPAWN AT THE NEXT STRONGHOLD.\nDO NOT BREAK BED AFTER FILLING PORTAL."
            case 2:
                write = "DO NOT SET YOUR SPAWN\nAT THE NEXT STRONGHOLD"
        self.inst_label.config(text=write)
        self.set_bg_colours(spawn)
        return

    def set_bg_colours(self, spawn: int=0):
        """colour codes the spawn point things so people dont forget surely they wont forget right suuuuurely"""
        match spawn:
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
        
        self.root.config(bg=frame)
        self.bt_frame.config(bg=frame)
        self.toggle_frame.config(bg=frame)
        self.sh_frame.config(bg=frame)
        self.new_buttons_frame.config(bg=frame)
        self.topmost_toggle.config(bg=frame, activebackground=press)
        self.newnext_button.config(bg=button, activebackground=press)
        self.set_hotkey_button.config(bg=button, activebackground=press)
        self.check_ring_bt.config(bg=button, activebackground=press)
        self.sh_label.config(bg=frame)
        self.inst_frame.config(bg=frame)
        self.inst_label.config(bg=frame)
        self.newnext_button_frame.config(bg=frame)

    def find_sh_ring(self) -> int:
        """find what ring coords given by user are in"""
        new_coords = tk.simpledialog.askstring(
            ":D",
            "Type out the x and z overworld coordinates of the stronghold you want to check the ring of.",
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

    def next_sh(self):
        """check if it's done and if not go next. update count, image, and display"""

        if self.newnext_button.cget("state") == "disabled": # stops the hotkey from pressing next when button is disabled
            return

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
                return #sadpag i am too lazy to make this thing work it is supposed to be like an aim trainer

        elif self.completed_count == len(self.strongholds): # means the user is done filling portals
            self.done = True
            self.silly_count = 0

        else:
            self.add_count()
            self.update_image()
            self.display_next_sh()

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

    def make_initial_image(self):
        """make the graph show first 8 and path to next stronghold"""
        for i in range(self.completed_count+1):
            sh = self.strongholds[i]
            self.graph_point(sh.get_coords(), sh.get_dot_colour())
            self.graph_line(sh.get_line_start(), sh.get_line_destination(), sh.get_line_colour())
        

    def update_image(self):
        """graph line and point of next stronghold"""
        sh = self.strongholds[self.completed_count] #updates image after adding count
        self.graph_line(sh.get_line_start(), sh.get_line_destination(), sh.get_line_colour())
        self.graph_point(sh.get_coords(), sh.get_dot_colour())