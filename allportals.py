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

"""
THINGS TO SET BACK TO NORMAL AFTER TESTING
next button disabled
qs file reading
first 8 strongholds list

THINGS TO FIX
make pathfind from coords work
tell user when to set spawn on the gui somewhere
subprocess.run for running concord and adding concord to exe (dank)
hotkey button thing doesnt work sort of 
fix silly list (very important)
"""

class AllPortals:
    def __init__(self):
        self.strongholds = Strongholds()

        self.next_stronghold_hotkey = ""
        self.listener = keyboard.Listener(on_press=self.on_press)

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
        self.root.wm_attributes("-topmost", 0)
        self.root.protocol("WM_DELETE_WINDOW", lambda: [print('destroy me...'), sys.exit(0)])

    def create_image(self):
        """create the image showing portals path and completed portals"""
        img = plt.imread("rings.png")
        plt.imshow(img, aspect="equal", extent=[-24320, 24320, -24320, 24320])
        plt.axis("off")

    def update_count(self):
        if (
            self.strongholds.get_completed_count() > 0
            and self.strongholds.get_completed_count()
            == self.strongholds.get_empty_sh_index()
        ):
            return

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

    def complete_sh(self, sh, empty=False):
        self.strongholds.complete_sh(sh, empty)
        self.update_count()

    # checks if coords are in correct ring and in the right format, adds them to first strongholds list
    def lock_entry(
        self, ring: int, entry: object, button: object, next_button: object
    ) -> None:
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

        self.complete_sh(sh)
        self.strongholds.set_current_location(sh)
        self.update_image()
        plt.draw()
        # plt.savefig("output.png", bbox_inches="tight", transparent=True)

        entry.config(state="disabled", cursor="heart")
        button.config(state="disabled", cursor="heart")


        if self.strongholds.get_completed_count() == 8:
            next_button.config(state="normal")

    def check_next(self, next_button):
        """checks each sh location is locked before changing window setup and predicts other sh locations"""
        if self.strongholds.get_completed_count() < 8:
            tk.messagebox.showinfo(message="Please lock each stronghold location")
            return

        next_button.config(
            state="disabled"
        )  # very silly things happen if you press the next button twice...

        backup_strongholds(self.strongholds.completed)

        self.strongholds.estimate_sh_locations()

        write_nodes_qs_file(
            self.strongholds.get_last_sh_coords(), self.strongholds.estimations
        )

        self.strongholds.sort_estimations_order_by_path(read_path_qs_file())

        # get rid of all widgets from the first-strongholds part
        for lock in self.locks:
            lock.destroy()
        for sh in self.sh_labels:
            sh.destroy()
        for entry in self.entries:
            entry.destroy()

        print(
            *zip(
                *(
                    tuple(round(coord / 16) for coord in sh)
                    for sh in self.strongholds.estimations
                )
            )
        )
        plt.scatter(
            *zip(*self.strongholds.estimations),
            c="gray",
            s=20,
        )
        plt.draw()

        # self.root.geometry("400x200")
        self.setup_next()
        next_button.destroy()
        self.display_next_sh()
        self.update_image()

    def create_inital_widgets(self):
        # toggles window always on top or not
        self.toggle_frame = tk.Frame(self.root, width=150, height=20, bg=peach)
        self.toggle_frame.grid(row=1, column=6, rowspan=2)
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
        self.topmost_toggle.place(relx=0.5, rely=0.5, anchor="center")

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
        next_button = tk.Button(
            self.root,
            state="normal",
            text="next",
            command=lambda: self.check_next(next_button),
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
                    i + 1, self.entries[i], self.locks[i], next_button
                )
            )
        [self.locks[i].grid(row=i, column=5) for i in range(0, 8)]

        # label telling user to lock in order so that the image updates accurately
        lock_order_label = tk.Label(
            self.root,
            text="Please make sure you\nlock strongholds in the\norder you found them",
            bg=peach,
        )
        lock_order_label.grid(row=3, column=6, rowspan=3)

        next_button.grid(row=9, column=6)

    # changes entire window setup to just display sh coords and some options
    def setup_next(self):
        self.c2 = False
        self.noGraph = False

        self.root.config(bg=lightblue)
        self.toggle_frame.config(height=70, width=200, bg=lightblue)
        self.topmost_toggle.config(bg=lightblue, activebackground=pressblue)
        self.sh_frame = tk.Frame(self.root, height=70, width=300, bg=lightblue)
        self.sh_label = tk.Label(self.sh_frame, text="", bg=lightblue)
        self.sh_label.place(relx=0.5, rely=0.5, anchor="center")

        self.bt_frame = tk.Frame(self.root, height=40, width=280, bg=lightblue)
        self.newnext_button = tk.Button(
            self.bt_frame,
            text="next",
            command=self.next_sh,
            height=1,
            width=5,
            borderwidth=3,
            bg=buttonblue,
            activebackground=pressblue,
        )

        self.new_buttons_frame = tk.Frame(
            self.root, height=120, width=200, bg=lightblue
        )

        self.set_hotkey_button = tk.Button(
            self.new_buttons_frame,
            text="Next SH Hotkey",
            command=self.set_next_hotkey,
            borderwidth=3,
            bg=buttonblue,
            activebackground=pressblue,
        )

        self.newnext_button.place(relx=0.33, rely=0.5, anchor="center")
        self.set_hotkey_button.place(relx=0.9, rely=0.85, anchor="center")
        self.sh_frame.place(x=0, y=0)
        self.bt_frame.place(x=0, y=70)
        self.toggle_frame.place(x=280, y=0)


        self.got_lost = tk.Button(
            self.new_buttons_frame,
            text="Pathfind from coords",
            command=self.find_from_coords,
            borderwidth=3,
            bg=buttonblue,
            activebackground=pressblue,
        )
        self.new_buttons_frame.place(x=280, y=70)
        self.set_hotkey_button.place(relx=0.5, rely=0.33)
        self.got_lost.place(relx=0.5, rely=0.66, anchor="center")

        image=tk.Toplevel()
        image.geometry("400x400")

        #make sure user can't accidentally close the image window cause there's no way to get it back
        def on_closing(): messagebox.showinfo("no", "You must close the main program to close this window.")
        image.protocol("WM_DELETE_WINDOW", on_closing)

        #using meaningful and descriptive variable names is a fundamental aspect of writing clean, maintainable, and understandable code. It's a practice that not only benefits you but also anyone who interacts with your code, now or in the future.
        aasdfae = plt.gcf()
        aasdfae.set_facecolor(lightblue)
        thang = FigureCanvasTkAgg(figure=aasdfae, master=image)
        thang.draw()
        thang.get_tk_widget().place(relx=0.5, rely=0.5, anchor="center")

        self.root.geometry("480x190")

    def update_image(self, empty: bool = False):
        # graph path from last stronghold as green
        color = "green"
        try:
            last_path = self.strongholds.get_last_path()
            print(last_path)
            match last_path:
                case 0:
                    color = "green"
                case 1:
                    color = "green"
                case 2:
                    color = "yellow"

            if self.strongholds.get_leave_spawn(-1):
                color = "purple"
        except IndexError:
            pass

        if self.strongholds.get_current_location() == (0, 0):
            color = "yellow"

        self.graph_point(self.strongholds.get_last_sh_coords(), color)

        if self.strongholds.get_current_location() == (0, 0):
            self.graph_line(
                self.strongholds.get_last_sh_coords(-2),
                self.strongholds.get_last_location(),
                "green",
            )
        else:
            self.graph_line(
                self.strongholds.get_current_location(),
                self.strongholds.get_last_location(),
                "green",
            )

        color = "blue"

        try:
            if self.strongholds.get_leave_spawn():
                color = "purple"
            else:
                color = "blue"
        except IndexError:
            pass

        # graph path to next stronghold as blue
        try:
            self.graph_point(self.strongholds.get_next_sh_coords(), color)
            self.graph_line(
                self.strongholds.get_current_location(),
                self.strongholds.get_next_sh_coords(),
                "blue",
            )
        except IndexError as e:
            pass
        plt.draw()

    def graph_point(self, coords, color):
        plt.scatter(coords[0], coords[1], c=color, s=30)
        plt.draw()

    def graph_line(self, start, end, color):
        plt.arrow(
            start[0],
            start[1],
            (end[0] - start[0]),
            (end[1] - start[1]),
            color=color,
            width=0.0001,
            head_width=0,
            head_length=0,
            length_includes_head=True,
        )
        plt.draw()

    # new options for when next stronghold is in 8th ring
    def create_empty_widgets(self):
        if get_stronghold_ring(self.strongholds.get_next_sh_coords()) != 8:
            return

        print(self.strongholds.get_completed_in_ring(8))

        if (
            self.strongholds.get_completed_in_ring(8) == 9
            and self.strongholds.get_empty_sh_index() == 0
        ):
            print("skipping last 8th ring sh")
            self.skip_empty()  # dont make user check last 8th ring sh when you already know its empty
            return

        if self.strongholds.get_empty_sh_index() != 0:
            print("eighth ring stronghold\n")
            return

        print("prompting empty check")
        self.empty_frame = tk.Frame(self.root, height=70, width=280, bg=lightblue)
        self.empty_sector = tk.Label(
            self.empty_frame,
            text="8th ring, there could be no stronghold. \nIf there is no stronghold please press 'empty'.\nOtherwise, hit 'next'.",
            bg=lightblue,
        )
        self.empty_button = tk.Button(
            self.bt_frame,
            text="empty",
            command=self.empty,
            height=1,
            width=5,
            borderwidth=3,
            bg=buttonblue,
            activebackground=pressblue,
        )
        self.empty_frame.place(x=0, y=110)
        self.empty_sector.place(relx=0.5, rely=0.5, anchor="center")
        self.empty_button.place(relx=0.66, rely=0.5, anchor="center")
        self.newnext_button.place(relx=0.33, rely=0.5, anchor="center")

    def set_bg_colours(self):
        if self.strongholds.get_leave_spawn() or self.strongholds.get_dont_set_spawn():
            try:
                self.root.config(bg=spawngreen)

                self.bt_frame.config(bg=spawngreen)
                self.toggle_frame.config(bg=spawngreen)
                self.sh_frame.config(bg=spawngreen)
                self.new_buttons_frame.config(bg=spawngreen)

                self.topmost_toggle.config(bg=spawngreen, activebackground=pressgreen)
                self.newnext_button.config(bg=buttongreen, activebackground=pressgreen)
                self.set_hotkey_button.config(bg=buttongreen, activebackground=pressgreen)
                self.got_lost.config(bg=buttongreen, activebackground=pressgreen)
                self.sh_label.config(bg=spawngreen)
                #these two have to be last
                self.empty_frame.config(bg=spawngreen)
                self.empty_button.config(bg=buttongreen, activebackground=pressgreen)

            except:
                pass
        else:
            try:
                self.root.config(bg=lightblue)

                self.bt_frame.config(bg=lightblue)
                self.toggle_frame.config(bg=lightblue)
                self.sh_frame.config(bg=lightblue)
                self.new_buttons_frame.config(bg=lightblue)

                self.topmost_toggle.config(bg=lightblue, activebackground=pressblue)
                self.newnext_button.config(bg=buttonblue, activebackground=pressblue)
                self.set_hotkey_button.config(bg=buttonblue, activebackground=pressblue)
                self.got_lost.config(bg=buttonblue, activebackground=pressblue)
                self.sh_label.config(bg=lightblue)
                #these two have to be last
                self.empty_frame.config(bg=lightblue)
                self.empty_button.config(bg=buttonblue, activebackground=pressblue)
            except:
                pass


    def display_next_sh(self):
        print(f"GET LEAVE SPAWN? {self.strongholds.get_leave_spawn()}")
        self.set_bg_colours()
        sh_data = self.strongholds.get_next_sh()
        print(
            "Stronghold {0}:\n{1}, {2} blocks at angle {3}".format(
                sh_data[0], sh_data[1], sh_data[2], sh_data[3]
            )
        )  # print in case user needs to see previous locations
        self.sh_label.config(
            text="Stronghold {0}:\n{1}, {2} blocks at angle {3}".format(
                sh_data[0], sh_data[1], sh_data[2], sh_data[3]
            ),
            font=("Cambria", 12),
        )

    # finds next sh location and displays it
    def next_sh(self, last_empty: bool = False):
        try:
            if self.empty_button.winfo_exists():
                self.empty_button.destroy()
                self.empty_frame.destroy()
                print(
                    f"you have found {self.strongholds.get_completed_in_ring(8)} 8th ring strongholds\n"
                )
        except:
            pass

        if self.strongholds.get_finished():
            try:
                if (
                    self.strongholds.estimations.index(
                        self.strongholds.get_next_sh_coords()
                    )
                    != self.strongholds.get_completed_count()
                    + len(self.strongholds.estimations)
                    - 129
                ):
                    print("done!")
                    return
                self.complete_sh(self.strongholds.get_next_sh_coords(), last_empty)
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
            print("done!")
        else:
            self.complete_sh(self.strongholds.get_next_sh_coords(), last_empty)
            self.optimize_next_3_nodes()
            self.create_empty_widgets()
            self.update_image(last_empty)
            try:
                print("leave your spawn behind?", self.strongholds.get_leave_spawn())
                print(
                    "dont set your spawn at all?", self.strongholds.get_dont_set_spawn()
                )
            except IndexError:
                pass
            self.display_next_sh()

    def optimize_next_3_nodes(self):
        self.strongholds.set_current_location(self.strongholds.get_last_sh_coords())
        if self.strongholds.get_last_path() == 2:
            self.strongholds.set_current_location(
                self.strongholds.get_last_sh_coords(-2)
            )
        if self.strongholds.get_dont_set_spawn():
            self.strongholds.set_current_location((0, 0))
            print("leave ur spawn behind at the next portal")
        print(get_nether_coords(self.strongholds.get_current_location()))

    def empty(self):
        print("empty sector\n")
        self.empty_button.destroy()
        self.empty_frame.destroy()

        self.next_sh(True)
        # plot empty sh point
        try:
            self.point = plt.scatter(
                self.strongholds.get_last_sh_coords()[0],
                self.strongholds.get_last_sh_coords()[1],
                c="red",
                s=50,
            )
            plt.draw()
        except Exception as e:
            print("photo broken", e)
            pass

    def skip_empty(self):
        print("empty sector\n")
        self.empty_button.destroy()
        self.empty_frame.destroy()

        # plot empty sh point
        try:
            self.point = plt.scatter(
                *self.strongholds.get_next_sh_coords(),
                c="red",
                s=50,
            )
            plt.draw()
        except Exception as e:
            print("photo broken", e)
            pass

        self.strongholds.estimations.insert(
            len(self.strongholds.estimations), self.strongholds.get_next_sh_coords()
        )

    # redoes pathfinding from specific coords if user gets lost or something idk
    def find_from_coords(self):
        msg = tk.messagebox.askyesno(
            message="Have you filled in the portal at the stronghold currently listed?"
        )
        if msg:
            self.complete_sh(self.strongholds.get_next_sh_coords(), False) #setting this to 'False' could theoretically cause a bug if the user does this on the empty 8th ring sh before pressing 'empty'... but that wouldnt happen probably... surely...
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
            return

        if not new_pos:
            tk.messagebox.showerror(
                message="Something went wrong. Make sure you only input your x and z coordinate separated by a space, or copy paste the f3+c command"
            )
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

        #get new path
        self.strongholds.estimate_sh_locations()
        write_nodes_qs_file(
            self.strongholds.get_last_sh_coords(), self.strongholds.estimations
        )
        self.strongholds.sort_estimations_order_by_path(read_path_qs_file())

        self.display_next_sh()
        self.create_empty_widgets() #no idea why this is here

    def set_next_hotkey(self):
        """sets hotkey to go to the next stronghold when you press the set hotkey button"""
        self.listener.stop()
        self.next_stronghold_hotkey = simpledialog.askstring("Input", "Enter a hotkey:")
        if self.next_stronghold_hotkey == "":
            self.set_hotkey_button.config(text="Set Hotkey", bg=buttonblue)
        else:
            print("set hotkey to " + self.next_stronghold_hotkey)
            self.set_hotkey_button.config(text=f"Edit Hotkey: {self.next_stronghold_hotkey}", bg=buttonblue)
            #self.listener = keyboard.Listener(on_press=self.on_press) i put this line at the start of the program
            self.listener.start()

    def on_press(self, key):
        if get_key_string(key) == self.next_stronghold_hotkey:
            self.newnext_button.invoke()
            return
