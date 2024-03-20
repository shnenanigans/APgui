import numpy as np
import math
import matplotlib.pyplot as plt
import os
from datetime import datetime

import constants


def is_prime(n):
    """fun facts"""
    if n % 2 == 0 and n > 2:
        return False
    return all(n % i for i in range(3, int(math.sqrt(n)) + 1, 2))


def write_nodes_qs_file(pos: tuple, estimations: list):
    """writes estimated sh list to qs file for concord to calculate"""
    #return
    #get rid of the 'return' after testing
    with open("strongholds.qs", "w+") as qs_file:
        # write node count, edge count, and starting position to the qs file
        qs_file.writelines(
            ["{0} 0\n".format(len(estimations) + 1), "{0} {1}\n".format(pos[0], pos[1])]
        )
        # write all the estimations to the qs file as nodes
        qs_file.writelines(
            ["{0} {1}\n".format(estimate.get_coords()[0], estimate.get_coords()[1]) for estimate in estimations]
        )


def read_path_qs_file():
    """return 'path' dictionary from solved concord file"""
    #concord is confusing
    #lets say you have 5 cities you gotta go to
    #and you give concord the coordinates of all of them
    #it will put something like this a few lines down in the qs file
    # 0 2 (dist)
    # 2 1 
    # 1 4
    # 4 3
    # 3 0
    #and theres a third number which is distance but we dont care about that its not added to the dict in this function
    #so we make dict = {0:2, 2:1, 1:4, 4:3, 3:0}
    #then we have to take that dict and find out which numbers match the coordinates we gave it earlier
    #dict.values-1 will give the index in whatever array we gave concord
    #that part is solved in sort_estimations_order_by_path in strongholds.py
    #also the first key and the last value are always 0
    try:
        with open("strongholds.qs", "r") as qs_file:
            lines = qs_file.readlines()

        path = {}
        for i in range(int(lines[0].split()[0]) + 1, len(lines)):
            start, next_node, dist = lines[i].split()
            path[int(start)] = int(next_node)

        return path
    except Exception as e:
        return {}


def get_distance(x1, x2):
    """find distance between x1 and x2"""
    return round(np.sqrt(((x1[0] - x2[0]) ** 2) + ((x1[1] - x2[1]) ** 2)))


def get_nether_coords(coords: tuple) -> tuple:
    """find nether coords from ow coords"""
    return (round(coords[0] / 8), round(coords[1] / 8))


def backup_strongholds(strongholds):
    """these will be in the backups folder in the directory, named with the date and time"""
    try:
        os.mkdir("backups")
    except FileExistsError:
        pass
    with open(
        "backups/first_strongholds_backup_{0}.txt".format(
            datetime.now().strftime("%m-%d-%Y %H-%M-%S")
        ),
        "w+",
    ) as backup:
        # overly silly regex to simplify the list for writing to the file
        lines = ""
        for sh in strongholds:
            lines += f"{sh.get_coords()[0]} {sh.get_coords()[1]}\n"
        print(lines)
        backup.writelines(lines)


def printHelp():
    """wow this is completely useless now"""
    print(
        "\n-------------------------------------------------------------------------------------------\n"
        "All valid commands\n"
        + "Enter\t\t-\t"
        + "Marks stronghold as complete and updates count\n"
        + "0\t\t-\t"
        + "Marks that you checked the coordinates but there was no stronghold\n"
        + "e\t\t-\t"
        + "Allows you to manually adjust the stronghold count\n"
        + "d\t\t-\t"
        + "Mark that you went back to spawn, and restart pathfinding from 0 0\n"
        + "d*\t\t-\t"
        + "Restart pathfinding from specific coordinates\n"
        + "-------------------------------------------------------------------------------------------\n"
    )


def parse_input(input):
    """gets coordinates into a tuple when you give it f3c or manually typed coords, returns false if entered wrong"""
    try:
        integers = input.split()
        if "/" == input[0]:
            integers = [integers[6], integers[8]]
            integers = list(map(float, integers))
        results = tuple(map(int, integers))
        return results
    except Exception as e:
        print(e)
        return False


def get_stronghold_ring(coords):
    """return ring of coords given, or 0 if not in a ring"""
    dist = get_distance((0, 0), coords)
    for ring, bounds in enumerate(constants.sh_bounds):
        if bounds[0] < dist < bounds[1]:
            return ring + 1
    return 0


def get_graphed_sh(start, destination, color, empty: bool = False):
    line = plt.arrow(
        start[0],
        start[1],
        (destination[0] - start[0]),
        (destination[1] - start[1]),
        color=color,
        width=0.0001,
        head_width=0,
        head_length=0,
        length_includes_head=True,
    )
    point = (
        plt.scatter(destination[0], destination[1], c=color, s=30)
        if not empty
        else None
    )
    return line, point


def get_mc_angle(start, destination):
    """find angles using current position and next stronghold to go to"""
    opposite = start[0] - destination[0]
    adjacent = start[1] - destination[1]

    if opposite == 0 and adjacent == 0:
        return 0
    if adjacent == 0:
        return opposite / abs(opposite) * 90
    if opposite == 0:
        return adjacent / abs(adjacent) * 90 + 90

    cartesian_angle = abs(math.degrees(math.atan(opposite / adjacent)))

    if opposite >= 0 and adjacent >= 0:
        mc_angle = 180 - cartesian_angle
    elif opposite < 0 and adjacent < 0:
        mc_angle = 0 - cartesian_angle
    elif opposite < 0 and adjacent >= 0:
        mc_angle = cartesian_angle - 180
    else:
        mc_angle = cartesian_angle

    return round(mc_angle, 1)


# thanks chatgpt
def distance_from_origin(coord):
    x, y = coord
    return math.sqrt(x**2 + y**2)


def get_key_string(key):
    """returns the key that was just pressed"""
    if hasattr(key, "char"):
        return str(key.char)
    else:
        return str(key).replace("Key.", "")


def sort_estimations_order_by_path(path: dict, estimations: list, spawn: tuple) -> list:
    """takes concord stuff and sorts estimations according to the path it gives, returns sorted array"""
    sorted_estimations = []
    for destination in path.values(): # see qs file for path values, its the second number starting from where it starts giving you rows of 3 numbers
        if destination < 1: # last path value is always 0, you've reached the end
            continue
        sorted_estimations.append(estimations[destination - 1]) # adds the next sh in optimal path to sorted_estimations
    return optimize_spawnpoint_abuse(sorted_estimations, spawn)


def optimize_spawnpoint_abuse(estimations: list, spawn: tuple) -> list:
        """if sh 2nd in the future (2) is closer to current one (0) than the next one (1) is, swap 2 and 1 in the estimations array. You will go from (before swapping) 0 -> 2, leave spawn, 2 -> 1, then continue from 2."""
        sorted_estimations = estimations.copy()

        temp = []
        for elem in sorted_estimations:
            temp.append(elem.get_leave_spawn())

        i = 0
        while i < len(estimations):
            try:
                if get_distance(
                    estimations[i].get_coords(
                    ), estimations[i + 2].get_coords()
                ) < get_distance(estimations[i].get_coords(), estimations[i + 1].get_coords()):
                    print("swap made between", i + 10, i + 11)
                    sorted_estimations[i + 1], sorted_estimations[i + 2] = (
                        estimations[i + 2],
                        estimations[i + 1],
                    )

            except IndexError:
                break
            i += 1

        for i in range(len(sorted_estimations)):
            try:
                if get_distance(
                        sorted_estimations[i+1].get_coords(), sorted_estimations[i+2].get_coords()) > get_distance(sorted_estimations[i].get_coords(), sorted_estimations[i+2].get_coords()):
                    sorted_estimations[i].set_leave_spawn(1) #leave spawn
                    sorted_estimations[i+1].set_leave_spawn(2) #dont set spawn

                if get_distance(sorted_estimations[i].get_coords(), sorted_estimations[i+1].get_coords()) > get_distance((spawn), sorted_estimations[i+1].get_coords()):
                    sorted_estimations[i].set_leave_spawn(3) # dont set spawn if next sh is closer to spawn than your current sh
            except IndexError:
                break

        # for i in range(len(temp)):
        #     print(temp[i], sorted_estimations[i].get_leave_spawn(), temp[i] ==
        #           sorted_estimations[i].get_leave_spawn())
            

        return sorted_estimations