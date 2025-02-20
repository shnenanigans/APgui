import numpy as np
import math
import os
from datetime import datetime

import constants

def is_prime(n):
    """fun facts"""
    if n % 2 == 0 and n > 2:
        return False
    return all(n % i for i in range(3, int(math.sqrt(n)) + 1, 2))


def get_distance(x1, x2):
    """find distance between x1 and x2"""
    return round(np.sqrt(((x1[0] - x2[0]) ** 2) + ((x1[1] - x2[1]) ** 2)))


def get_nether_coords(coords: tuple) -> tuple:
    """find nether coords from overworld coords"""
    return (round(coords[0] / 8), round(coords[1] / 8))

def get_overworld_coords(coords: tuple) -> tuple:
    """find overworld coords from nether coords"""
    return (coords[0] * 8, coords[1] * 8)

def backup_strongholds(first8, spawn_coords):
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
        for sh in first8:
            lines += f"{sh[0]} {sh[1]}\n"
        lines += f"{spawn_coords[0]} {spawn_coords[1]}"
        print("creating backups file")
        print(lines)
        backup.writelines(lines)


def parse_input(input) -> tuple:
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


def distance_from_origin(coord):
    x, y = coord
    return math.sqrt(x**2 + y**2)


def get_key_string(key):
    """returns the key that was just pressed"""
    if hasattr(key, "char"):
        return str(key.char)
    else:
        return str(key).replace("Key.", "")