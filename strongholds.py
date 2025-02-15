from utils import get_mc_angle

class Stronghold:
    def __init__(self, coords: tuple, ring: int, line_destination: tuple, line_start: tuple, marker: str, angle, line_colour: str="green", dot_colour: str="green", set_spawn: int=0):
        """constructor for stronghold class"""
        self.coords = coords
        self.ring = ring
        self.set_spawn = set_spawn
        self.line_colour = line_colour
        self.dot_colour = dot_colour
        self.marker = marker
        self.line_start = line_start #previous stronghold
        self.line_destination = line_destination #current stronghold
        self.angle = angle #angle from last stronghold

    def get_line_colour(self) -> str:
        """return line colour"""
        return self.line_colour
    
    def get_angle(self) -> int:
        """return angle to get to current stronghold"""
        return self.angle
    
    def get_marker(self) -> str:
        """return marker for the stronghold that will show up on the graph"""
        return self.marker
    
    def get_line_start(self) -> str:
        """return line start"""
        return self.line_start
    
    def get_line_destination(self) -> str:
        """return line destination, usually just coords unless it's a weird spawn set one"""
        return self.line_destination

    def get_dot_colour(self) -> str:
        """return dot colour"""
        return self.dot_colour

    def get_coords(self) -> tuple:
        """return coords of sh"""
        return self.coords
    
    def set_dot_colour(self, dot_colour):
        """set colour of dot on graph for this sh"""
        self.dot_colour = dot_colour

    def get_set_spawn(self):
        """return where to set spawn. 0=normal, 1=leave spawn, 2=no spawn"""
        return self.set_spawn
    
    def set_set_spawn(self, set_spawn: int):
        """set spawn as 0=normal, 1=leave spawn, 2=no spawn"""
        self.set_spawn = set_spawn

    def set_coords(self, coords: tuple):
        """set coords of sh"""
        self.coords = coords

    def is_8th_ring(self) -> bool:
        """tell user if sh is in the 8th ring or not"""
        return self.ring == 8

