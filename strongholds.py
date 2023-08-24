import numpy as np
import time
from tkinter import simpledialog

from utils import get_stronghold_ring, get_distance, get_mc_angle, get_nether_coords
import constants
from utils import *


class Strongholds:
    def __init__(self) -> None:
        # starting strongholds testing array
        """
        self.oldcompleted = [
            (1512, -104),
            (5736, -712),
            (7512, 2280),
            (10584, 1368),
            (14168, 584),
            (17704, -312),
            (20920, 1160),
            (23528, -920),
        ]
        """
        #"""
        self.completed = [
            (885, 2419),
            (-1036, 4725),
            (-120, 8616),
            (-1192, 10872),
            (296, 14456),
            (744, 17624),
            (-600, 19896),
            (392, 23320),
        ]
        #"""
        #self.completed = []
        self.spawn = (0, 0)
        self.estimations = []
        self.current_location = (0, 0)
        self.last_location = (0, 0)
        self.empty_index = 0
        self.completed_8th_ring = 1
    
    def add_completed_8th_ring(self):
        """adds 1 to completed 8th ring shs"""
        self.completed_8th_ring +=1 

    def get_completed_8th_ring(self) -> int:
        """returns the number of shs found in 8th ring because i dont want to run completed_in_ring on every sh that sounds bad for efficiency"""
        return self.completed_8th_ring

    def set_spawn(self) -> tuple:
        """tells program spawnpoint for more accurate calculations"""
        spawn = simpledialog.askstring(
            "",
            "Enter your spawn point coordinates or paste f3+c"
        )
        try:
            spawn = tuple(parse_input(spawn))
        except:
            messagebox.showerror(
                message="Something went wrong. Make sure you only input your x and z coordinate separated by a space, or copy paste the f3+c command"
            )
            return

        if not spawn:
            messagebox.showerror(
                message="Something went wrong. Make sure you only input your x and z coordinate separated by a space, or copy paste the f3+c command"
            )
            return
        self.spawn = spawn
        return self.spawn

    def complete_sh(self, sh: tuple, empty: bool = False) -> None:
        """adds sh to completed sh array and tracks index of empty sector in it, if it has been found"""
        self.completed.append(sh)
        if empty:
            self.empty_index = self.get_completed_count() - 1

    def set_current_location(self, coords: tuple) -> None:
        """sets location at coords given, and sets last location at what it is currently"""
        self.last_location = self.current_location
        self.current_location = coords

    def get_current_location(self) -> tuple:
        """returns current location"""
        return self.current_location

    def get_last_location(self) -> tuple:
        """returns last location"""
        return self.last_location

    def get_finished(self) -> bool:
        """true if portals are all filled"""
        #apparently you can add ints and bools??? empty_index==0 when empty sector has not been found and adds 1 to completed count. if it has been found then completed count is normal cause empty sector location is added to completed array somewhere else
        return self.get_completed_count() + (self.empty_index == 0) >= 128

    def get_completed_count(self) -> int:
        """returns length of completed sh array"""
        return len(self.completed)

    def get_completed_in_ring(self, ring: int) -> int:
        """returns number of completed shs in a given ring"""
        completed = 0
        for sh in self.completed:
            if get_stronghold_ring(sh) == ring:
                completed += 1
        return completed

    def get_empty_sh_index(self) -> int:
        #returns index of empty sh in completed array
        return self.empty_index

    def get_next_sh(self) -> [int, tuple, int, float]:
        """returns # completed shs, next sh nether coords, distance to next sh (in nether), angle to next sh"""
        next_n_coords = get_nether_coords(self.get_next_sh_coords())
        return (
            self.get_completed_count() + (self.empty_index == 0),
            next_n_coords,
            get_distance(
                get_nether_coords(self.get_current_location()),
                next_n_coords,
            ),
            get_mc_angle(self.get_current_location(), self.get_next_sh_coords()),
        )

    def get_next_sh_coords(self, count: int = 1) -> tuple:
        """returns coords of next sh or shs further in the future from estimations array. To find coords of the sh after the next one, do get_next_sh_coords(2) as default is (1)."""
        # the math is spread out like this to better show what is happening
        # len(self.estimations) - 129 is the difference between total strongholds and how many estimations were made
        # because already completed strongholds (usually the first 8) are already completed counted by get_completed_count
        # the entire thing is then offset by an optional argument so that u can get the coords for strongholds farther in the future
        return self.estimations[
            self.get_completed_count() + len(self.estimations) - 129 + (count - 1)
        ]

    def get_last_sh_coords(self, count: int = -1) -> tuple:
        """returns coords of last stronghold or shs further in the past from completions array. To find coords of the one behind the last one, do get_last_sh_coords(-2) as default is (-1)"""
        try:
            return self.completed[count]
        except IndexError as e:
            return (0, 0)

    def get_optimal_3_node_path(self) -> int:
        """completely unused just ignore this its the next function you want"""
        # 0 = default path
        # 1 = skip and leave spawn
        # 2 = leave spawn behind
        distances = [
            get_distance(self.get_last_sh_coords(1), self.get_next_sh_coords(2))
            + get_distance(self.get_next_sh_coords(2), self.get_next_sh_coords(3)),
            get_distance(self.get_next_sh_coords(2), self.get_next_sh_coords(3))
            + get_distance(self.get_next_sh_coords(3), self.get_last_sh_coords(1)),
            get_distance(self.get_next_sh_coords(3), self.get_last_sh_coords(1))
            + get_distance(self.get_last_sh_coords(1), self.get_next_sh_coords(2)),
        ]
        return distances.index(min(distances))

    def get_last_path(self) -> int:
        """(0=normal path), (1=went from node 1 to 3, set spawn, went back to 2), (2=left spawn at 1, went to 2, then to 3 from 1)"""
        # 0 = default path
        # 1 = skipped and left spawn
        # 2 = left spawn behind
        #i asked mach what the difference between 'skipped and left spawn' and 'left spawn behind' was and she said technically nothing anymore so do with that information what you will
        distances = [
            get_distance(self.get_last_sh_coords(-2), self.get_last_sh_coords(-1))
            + get_distance(self.get_last_sh_coords(-1), self.get_next_sh_coords(1)),
            get_distance(self.get_last_sh_coords(-1), self.get_next_sh_coords(1))
            + get_distance(self.get_next_sh_coords(1), self.get_last_sh_coords(-2)),
            get_distance(self.get_next_sh_coords(1), self.get_last_sh_coords(-2))
            + get_distance(self.get_last_sh_coords(-2), self.get_last_sh_coords(-1)),
        ]
        return distances.index(min(distances))

    def get_leave_spawn(self, adjust: int = 0) -> bool:
        """returns true if you leave your spawn point behind, get_leave_spawn(-1) to see if you left your spawn behind 1 stronghold ago and so on"""
        # i dont think adjust is ever used
        return get_distance(
            self.get_next_sh_coords(2 + adjust), self.get_next_sh_coords(3 + adjust)
        ) > get_distance(
            self.get_next_sh_coords(1 + adjust), self.get_next_sh_coords(3 + adjust)
        )

    def get_dont_set_spawn(self) -> bool:
        """true if you don't set your spawn at all, only works for the 1st ring stuff"""
        return get_distance(
            self.get_current_location(), self.get_next_sh_coords(1)
        ) > get_distance((self.spawn), self.get_next_sh_coords(1))

    def get_dont_set_spawn_colours(self) -> bool:
        """you have to check slightly in the future for the gui colours so i made this thing"""
        return get_distance(
            self.get_next_sh_coords(), self.get_next_sh_coords(2)
        ) > get_distance((self.spawn), self.get_next_sh_coords(2))

    def skip_and_go_back(self) -> bool:
        """this is never used idk man but looks like it compares current location with next 2 strongholds and returns true if next one is closer"""
        return get_distance(
            self.get_last_sh_coords(), self.get_next_sh_coords(1)
        ) > get_distance(self.get_last_sh_coords(), self.get_next_sh_coords(2))

    def estimate_sh_locations(self) -> None:
        """Predict location of all the other strongholds using the first 8"""
        for ring, strongholds in enumerate(constants.strongholds_per_ring):
            for stronghold in self.completed:
                if get_stronghold_ring(stronghold) - 1 != ring:
                    continue
                x, z = stronghold
                magnitude = constants.magnitude_per_ring[ring]
                angle = np.arctan2(z, x)
                for i in range(strongholds - 1):
                    angle += (2 * np.pi) / strongholds
                    estimate_x = magnitude * np.cos(angle)
                    estimate_z = magnitude * np.sin(angle)
                    self.estimations.append((round(estimate_x), round(estimate_z)))
                    print(round(estimate_x), round(estimate_z), ring)
                break

    def sort_estimations_order_by_path(self, path: dict) -> None:
        """takes concord stuff and sorts estimations according to the path it gives"""
        sorted_estimations = []
        print(len(self.estimations))
        for destination in path.values(): # see qs file for path values, its the second number starting from where it starts giving you rows of 3 numbers
            if destination < 1: # last path value is always 0, you've reached the end
                continue
            print(destination - 1)
            print(self.estimations[destination - 1])
            sorted_estimations.append(self.estimations[destination - 1]) # adds the next sh in optimal path to sorted_estimations
            print(len(sorted_estimations))
        print(sorted_estimations)
        print(self.estimations)
        print(path)
        self.estimations = sorted_estimations
        self.optimize_spawnpoint_abuse()

    def optimize_spawnpoint_abuse(self) -> None:
        """if sh 2nd in the future (2) is closer to current one (0) than the next one (1) is, swap 2 and 1 in the estimations array. You will go from 0 -> 2, leave spawn, 2 -> 1, then continue from 2."""
        sorted_estimations = self.estimations.copy()
        i = 0
        while i < len(self.estimations):
            try:
                if get_distance(
                    self.estimations[i], self.estimations[i + 2]
                ) < get_distance(self.estimations[i], self.estimations[i + 1]):
                    print("swap made between", i + 10, i + 11)
                    sorted_estimations[i + 1], sorted_estimations[i + 2] = (
                        self.estimations[i + 2],
                        self.estimations[i + 1],
                    )
            except IndexError:
                self.estimations = sorted_estimations
                break
            i += 1
