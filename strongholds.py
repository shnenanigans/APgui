import numpy as np
import time

from utils import get_stronghold_ring, get_distance, get_mc_angle, get_nether_coords
import constants


class Strongholds:
    def __init__(self) -> None:
        # starting strongholds testing array
        #"""
        self.completed = [
            (1512, -104),
            (5736, -712),
            (7512, 2280),
            (10584, 1368),
            (14168, 584),
            (17704, -312),
            (20920, 1160),
            (23528, -920),
        ]
        #self.completed = []
        self.estimations = []
        self.current_location = (0, 0)
        self.last_location = (0, 0)
        self.empty_index = 0

    def complete_sh(self, sh: tuple, empty: bool = False) -> None:
        self.completed.append(sh)
        if empty:
            self.empty_index = self.get_completed_count() - 1

    def set_current_location(self, coords: tuple) -> None:
        self.last_location = self.current_location
        self.current_location = coords

    def get_current_location(self) -> tuple:
        return self.current_location

    def get_last_location(self) -> tuple:
        return self.last_location

    def get_finished(self) -> bool:
        return self.get_completed_count() + (self.empty_index == 0) >= 128

    def get_completed_count(self) -> int:
        return len(self.completed)

    def get_completed_in_ring(self, ring: int) -> int:
        completed = 0
        for sh in self.completed:
            if get_stronghold_ring(sh) == ring:
                completed += 1
        return completed

    def get_empty_sh_index(self) -> int:
        return self.empty_index

    def get_next_sh(self) -> [int, tuple, tuple, int, float]:
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
        # the math is spread out like this to better show what is happening
        # len(self.estimations) - 129 is the difference between total strongholds and how many estimations were made
        # because already completed strongholds (usually the first 8) are already completed counted by get_completed_count
        # the entire thing is then offset by an optional argument so that u can get the coords for strongholds farther in the future
        return self.estimations[
            self.get_completed_count() + len(self.estimations) - 129 + (count - 1)
        ]

    def get_last_sh_coords(self, count: int = -1) -> tuple:
        try:
            return self.completed[count]
        except IndexError as e:
            return (0, 0)

    def get_optimal_3_node_path(self) -> int:
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
        # 0 = default path
        # 1 = skipped and left spawn
        # 2 = left spawn behind
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
        return get_distance(
            self.get_next_sh_coords(2 + adjust), self.get_next_sh_coords(3 + adjust)
        ) > get_distance(
            self.get_next_sh_coords(1 + adjust), self.get_next_sh_coords(3 + adjust)
        )

    def get_dont_set_spawn(self) -> bool:
        return get_distance(
            self.get_current_location(), self.get_next_sh_coords(1)
        ) > get_distance((0, 0), self.get_next_sh_coords(1))

    def get_dont_set_spawn_colours(self) -> bool:
        return get_distance(
            self.get_next_sh_coords(), self.get_next_sh_coords(2)
        ) > get_distance((0, 0), self.get_next_sh_coords(2))

    def skip_and_go_back(self) -> bool:
        return get_distance(
            self.get_last_sh_coords(), self.get_next_sh_coords(1)
        ) > get_distance(self.get_last_sh_coords(), self.get_next_sh_coords(2))

    def estimate_sh_locations(self) -> None:
        # Predict location of all the other strongholds
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
        sorted_estimations = []
        print(len(self.estimations))
        for destination in path.values():
            if destination < 1:
                continue
            print(destination - 1)
            print(self.estimations[destination - 1])
            sorted_estimations.append(self.estimations[destination - 1])
            print(len(sorted_estimations))
        print(sorted_estimations)
        print(self.estimations)
        print(path)
        self.estimations = sorted_estimations
        self.optimize_spawnpoint_abuse()

    def optimize_spawnpoint_abuse(self) -> None:
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
