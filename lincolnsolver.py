import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from strongholds import Stronghold #to make stronghold objects
from utils import get_stronghold_ring, get_mc_angle

def make_stronghold_list(points: list[tuple], filled: list[tuple], spawn_coords: tuple) -> list[Stronghold]:
    """creates list of stronghold objects in the order that the player will go to them. points contains all stronghold location estimations and filled contains the filled shs in the first 8"""
    OR_SCALE_FACTOR = 10000

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

    distance_matrix = np.zeros((len(points), len(points)), np.float64)
    origin_reset_matrix = np.zeros((len(points), len(points)), bool)
    for i, (x1, y1) in enumerate(points):
        for j, (x2, y2) in enumerate(points[1:], start=1):
            origin_distance = np.sqrt((spawn_coords[0] - x2) ** 2 + (spawn_coords[1] - y2) ** 2)
            real_distance = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            if get_stronghold_ring((x1, y1)) == 8: #never go back to spawn on 8th ring in case it is empty sector
                distance_matrix[i][j] = real_distance
            else:
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
        #search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH #this makes it take forever
        search_parameters.first_solution_strategy = strategy
        search_parameters.time_limit.seconds = 50 #set to 5 with metaheuristic thing
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

    print(route)
    strongholds = [] #will contain all strongholds including first 8 and empty sector there are 129 strongholds now ive decided

    for i in range(len(filled)): #sh contains just tuple coords
        if i==0:
            line_start = (0, 0)
        else:
            line_start = filled[i-1]
        marker = "o"

        sh = filled[i] #just tuple coords
        strongholds.append(Stronghold(sh, get_stronghold_ring(sh), sh, line_start, marker, angle=0)) #now contains stronghold objects of filled shs

    for i, node in enumerate(route[1:-1], start=1):
        #each sh object should contain the the angle pointing to it from the last one, and the line going from the last one to the current one
        last_node = route[i - 1]
        next_node = route[i + 1]
        is_reset = origin_reset_matrix[last_node][node]
        is_last = next_node == 0
        coords = points[node]
        set_spawn = 0
        ring = get_stronghold_ring(coords)
        dot_colour="purple" if is_last else "red" if is_reset else "green"
        line_colour="green"
        marker = "*" if is_last else "o"
        line_start = points[last_node]
        line_destination = coords

        if is_reset:
            line_start = spawn_coords
            strongholds[-1].set_set_spawn(2)
            line_colour = "red"

        if i > 2 and strongholds[-2].get_dot_colour() == "blue":
            line_colour = "blue"
            line_start = strongholds[-2].get_coords()
            last_node = route[i - 2] #make the last sh the one that spawn is currently at, which was filled 2 shs ago

        elif 1 < i < len(route) - 2: #figure out if you should leave spawn or not, has to be elif so you dont get blue dot twice in a row honestly it's a miracle this works idk what i did
            any_reset = is_reset or origin_reset_matrix[node][next_node] #nearby node goes back to 0 0
            if not any_reset:
                if distance_matrix[last_node][next_node] < distance_matrix[node][next_node]:
                    strongholds[-1].set_dot_colour("blue")
                    strongholds[-1].set_set_spawn(1)
                    set_spawn = 2

        if i == 1: #angle from 8th to 9th stronghold unknown because the program only knows where sh is not where your portal is, which could be over 2k away
            angle = "N/A"
        else:
            angle = get_mc_angle(line_start, line_destination)

        sh = Stronghold(coords, ring, line_destination, line_start, marker, angle, line_colour, dot_colour, set_spawn)
        strongholds.append(sh)
    
    return strongholds
