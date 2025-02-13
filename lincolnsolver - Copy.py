import numpy as np
from matplotlib import pyplot as plt
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from strongholds import Stronghold #to make stronghold objects

def get_stronghold_order(points: list[tuple]) -> list:
    """return list of stronghold locations in order, preferably as stronghold objects"""











#angle = np.random.random() * np.pi * 2
#dist = np.random.randint(22784, 24320 + 1)
#STARTING_POINT = (np.cos(angle) * dist, np.sin(angle) * dist)
OR_SCALE_FACTOR = 10000
STRONGHOLD_DATA = (
    (3, 1280, 2816),
    (6, 4352, 5888),
    (10, 7424, 8960),
    (15, 10496, 12032),
    (21, 13568, 15104),
    (28, 16640, 18176),
    (36, 19712, 21248),
    (9, 22784, 24320),
)

STRATEGIES = (
    routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC,
    routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC,
    routing_enums_pb2.FirstSolutionStrategy.PATH_MOST_CONSTRAINED_ARC,
    # routing_enums_pb2.FirstSolutionStrategy.EVALUATOR_STRATEGY,
    routing_enums_pb2.FirstSolutionStrategy.SAVINGS,
    # routing_enums_pb2.FirstSolutionStrategy.SWEEP,
    routing_enums_pb2.FirstSolutionStrategy.CHRISTOFIDES,
    # routing_enums_pb2.FirstSolutionStrategy.ALL_UNPERFORMED,
    # routing_enums_pb2.FirstSolutionStrategy.BEST_INSERTION,
    routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION,
    routing_enums_pb2.FirstSolutionStrategy.SEQUENTIAL_CHEAPEST_INSERTION,
    routing_enums_pb2.FirstSolutionStrategy.LOCAL_CHEAPEST_INSERTION,
    routing_enums_pb2.FirstSolutionStrategy.LOCAL_CHEAPEST_COST_INSERTION,
    routing_enums_pb2.FirstSolutionStrategy.GLOBAL_CHEAPEST_ARC,
    routing_enums_pb2.FirstSolutionStrategy.LOCAL_CHEAPEST_ARC,
    routing_enums_pb2.FirstSolutionStrategy.FIRST_UNBOUND_MIN_VALUE,
)

#(-1147 -859), (-1147 5156), (-1996 7604), (-347 11316), (-59 13812), (1092 17204), (-1723 20292), (-3963 22900) first 8

points = [(4925, 22595), (-2046, 95), (940, -1819), (-5002, 1095), (-3449, -3784), (1552, -4879), (5002, -1095), (3449, 3784), (-4017, 7140), (-7446, 3415), (-8031, -1614), (-5549, -6027), (-947, -8137), (4017, -7140), (7446, -3415), (8031, 1614), (5549, 6027), (-5534, 9811), (-9046, 6712), (-10994, 2453), (-11041, -2231), (-9179, -6529), (-5730, -9698), (-1290, -11190), (3373, -10747), (7453, -8446), (10244, -4685), (11263, -113), (10336, 4478), (7621, 8295), (3588, 10677), (-2344, 14143), (-6408, 12824), (-9903, 10365), (-12519, 6986), (-14022, 2986), (-14279, -1280), (-13267, -5432), (-11077, -9101), (-7902, -11962), (-4025, -13759), (209, -14334), (4425, -13636), (8248, -11726), (11338, -8774), (13420, -5042), (14310, -862), (13928, 3394), 
(12309, 7349), (9596, 10650), (6031, 13006), (-4444, 16831), (-8078, 15420), (-11307, 13236), (-13969, 10388), (-15930, 7019), (-17093, 3299), (-17398, -588), (-16831, -4444), (-15420, -8078), (-13236, -11307), (-10388, -13969), (-7019, -15930), (-3299, -17093), (588, -17398), (4444, -16831), (8078, -15420), (11307, -13236), (13969, -10388), (15930, -7019), (17093, -3299), (17398, 588), (16831, 4444), (15420, 8078), (13236, 11307), (10388, 13969), (7019, 15930), (3299, 17093), (-2038, 20378), (-5545, 19715), (-8884, 18453), (-11954, 16629), (-14660, 14301), (-16920, 11538), (-18667, 8425), (-19846, 5055), (-20423, 1532), (-20378, -2038), (-19715, -5545), (-18453, -8884), (-16629, -11954), (-14301, -14660), (-11538, -16920), (-8425, -18667), (-5055, -19846), (-1532, -20423), (2038, -20378), (5545, -19715), (8884, -18453), (11954, -16629), (14660, -14301), (16920, -11538), (18667, -8425), (19846, -5055), (20423, -1532), (20378, 2038), (19715, 5545), (18453, 8884), (16629, 11954), (14301, 14660), (11538, 16920), (8425, 18667), (5055, 19846), (-9468, 21565), (-20335, 11881), (-23435, -2341), (-17584, -15669), (-5016, -23012), (9468, -21565), (20335, -11881), (23435, 2341), (17584, 15669)]

"""
for ring, (count, minimum, maximum) in enumerate(STRONGHOLD_DATA):
    first_angle = np.random.random() * np.pi * 2
    for i in range(count):
        angle = first_angle + i * np.pi * 2 / count
        distance = (maximum + minimum) / 2
        x = np.cos(angle) * distance
        y = np.sin(angle) * distance
        points.append((x, y))
"""

distance_matrix = np.zeros((len(points), len(points)), np.float64)
origin_reset_matrix = np.zeros((len(points), len(points)), bool)
for i, (x1, y1) in enumerate(points):
    for j, (x2, y2) in enumerate(points[1:], start=1):
        origin_distance = np.sqrt(x2**2 + y2**2)
        real_distance = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        if origin_distance < real_distance:
            origin_reset_matrix[i][j] = True

        distance_matrix[i][j] = min(origin_distance, real_distance)
distance_matrix = np.floor(distance_matrix * OR_SCALE_FACTOR).astype(int).tolist()

manager = pywrapcp.RoutingIndexManager(len(points), 1, 0)
routing = pywrapcp.RoutingModel(manager)


def distance_callback(from_index, to_index):
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return distance_matrix[from_node][to_node]


transit_callback_index = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

best_path = (1 << 60, None)
for strategy in STRATEGIES:
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = strategy
    search_parameters.time_limit.seconds = 10
    solution = routing.SolveWithParameters(search_parameters)

    if not solution:
        continue

    route_length = 0
    index = routing.Start(0)
    route = [manager.IndexToNode(index)]
    while not routing.IsEnd(index):
        index = solution.Value(routing.NextVar(index))
        node = manager.IndexToNode(index)
        route_length += routing.GetArcCostForVehicle(route[-1], index, 0)
        route.append(node)

    for i, node in enumerate(route[1:-1], start=1):
        last_node = route[i - 1]
        next_node = route[i + 1]
        if 1 < i < len(route) - 2:
            any_reset = (
                origin_reset_matrix[last_node][node]
                or origin_reset_matrix[node][next_node]
            )
            if not any_reset:
                if (
                    distance_matrix[last_node][next_node]
                    < distance_matrix[node][next_node]
                ):
                    route_length -= (
                        distance_matrix[node][next_node]
                        - distance_matrix[last_node][next_node]
                    )
    print(f"{strategy=} {route_length=}")
    if route_length < best_path[0]:
        best_path = (route_length, route)

route_length, route = best_path
assert route is not None, "No solution found"

plt.switch_backend("TkAgg")
print(route)
#print("->".join(map(str, route)))
print(f"Total Length: {route_length}")
last_line_drew_forward = False
for i, node in enumerate(route[1:-1], start=1):
    last_node = route[i - 1]
    next_node = route[i + 1]
    is_reset = origin_reset_matrix[last_node][node]
    is_first = last_node == 0
    if not last_line_drew_forward:
        print("here")
        plt.plot(
            (0 if is_reset else points[last_node][0], points[node][0]),
            (0 if is_reset else points[last_node][1], points[node][1]),
            "*-" if is_first else "o-",
            color="purple" if is_first else "red" if is_reset else "green",
        )
    last_line_drew_forward = False
    if 1 < i < len(route) - 2:
        any_reset = is_reset or origin_reset_matrix[node][next_node]
        if not any_reset:
            if distance_matrix[last_node][next_node] < distance_matrix[node][next_node]:
                plt.plot(
                    (points[last_node][0], points[next_node][0]),
                    (points[last_node][1], points[next_node][1]),
                    "o-",
                    color="blue",
                )
                last_line_drew_forward = True

plt.axis("equal")
plt.show()