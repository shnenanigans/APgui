import numpy as np
import math
import matplotlib.pyplot as plt
from tkinter import messagebox


def is_prime(n):
    if n % 2 == 0 and n > 2:
        return False
    return all(n % i for i in range(3, int(math.sqrt(n)) + 1, 2))


def generatePath(shs, pos):
    f = open("strongholds.qs", "w+")
    print(str(len(shs)), "0", file=f)
    for sh in shs:
        print(str(sh[0]), str(sh[1]), file=f)
    f.close()
    while True:
        try:
            messagebox.showinfo(title=None, message="Use the strongholds.qs file in this directory to run concorde pathfinding, solve and save, THEN press ok")

            f = open("strongholds.qs", "r")
            lines = f.readlines()
            f.close()

            paths = {}
            for i in range(len(shs) + 1, len(lines)):
                start, end, dist = lines[i].split()
                paths[int(start)] = int(end)

            rev_paths = dict((v, k) for k, v in paths.items())

            new_x, new_z = zip(*shs)

            # Have to scale numbers down due to overflow errors
            new_x = np.array(list(new_x)) / 100
            new_z = np.array(list(new_z)) / 100
            new_pos = (pos[0] / 100, pos[1] / 100)

            dists = np.sqrt(((new_x - new_pos[0]) ** 2) + ((new_z - new_pos[1]) ** 2))
            nearest_idx = np.argmin(dists)
            normal = get_dist(shs[nearest_idx], shs[paths[nearest_idx]])
            reverse = get_dist(shs[nearest_idx], shs[rev_paths[nearest_idx]])
            if normal > reverse:
                paths = rev_paths
            break
        except Exception as e:
            messagebox.showerror(title=None, message="Something went wrong, make sure you hit save, and try again")
            continue

    return paths, nearest_idx


def get_dist(x1, x2):
    return np.sqrt(((x1[0] - x2[0]) ** 2) + ((x1[1] - x2[1]) ** 2))


def updateCount(count):
    f = open("sh_count.txt", "w+")
    facts = open("fun_facts.txt", "w+")

    lines = [str(count) + "/128\n"]

    if count == 69:
        facts.writelines(["nice.\n"])
    if count == 71:
        facts.writelines(["BRA7-1L\n"])
    if is_prime(count):
        facts.writelines(["(prime)\n"])

    f.writelines(lines)

    f.close()
    facts.close()


def printHelp():
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


def getIntInput(prompt):
    while True:
        try:
            integers = prompt.split()
            if "/" == prompt[0]:
                integers = [integers[6], integers[8]]
                integers = list(map(float, integers))
            results = list(map(int, integers))
            return results
        except Exception as e:
            print(e)
            return False

def getRing(coords):
    dist = get_dist((0, 0), coords)
    sh_bounds = [(1280, 2816), (4352, 5888), (7424, 8960), (10496, 12032), (13568, 15104), (16640, 18176), (19712, 21248), (22784, 24320)]
    for i in range(len(sh_bounds)):
        if dist > sh_bounds[i][0] and dist < sh_bounds[i][1]:
            return i + 1
    return 0

def graphAddSH(prev, sh, col1, flag):
    line = plt.arrow(
        prev[0],
        prev[1],
        sh[0] - prev[0],
        sh[1] - prev[1],
        color=col1,
        width=0.0001,
        head_width=0,
        head_length=0,
        length_includes_head=True,
    )
    point = None
    if not flag:
        point = plt.scatter(sh[0], sh[1], c=col1, s=30)
    return line, point


#find angles using current position and next stronghold to go to
def find_angle(pos, nexsh):
    x1 = int(pos[0])
    x2 = int(nexsh[0])
    z1 = int(pos[1])
    z2 = int(nexsh[1])
    opposite = x1-x2
    adjacent = z1-z2
    if adjacent==0:
        return None
    ref_angle = abs(math.degrees(math.atan(opposite/adjacent)))
    if opposite>=0 and adjacent>=0:
        actual_angle = 180 - ref_angle
    elif opposite<0 and adjacent<0:
        actual_angle = 0 - ref_angle
    elif opposite<0 and adjacent>=0:
        actual_angle = ref_angle - 180
    else:
        actual_angle = ref_angle
    actual_angle = round(actual_angle, 2)
    return actual_angle


#thanks chatgpt
def distance_from_origin(coord):
    x, y = coord
    return math.sqrt(x**2 + y**2)

def order_shs(coordinates): #orders the first 8 strongholds so that things dont break (sorry meebie and kruin)
    return sorted(coordinates, key=distance_from_origin)
