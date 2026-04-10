try:
    from ..cells.cell import Cell
    from ..walls.wall import Wall
    from random import shuffle, choice
    from sys import setrecursionlimit
    from typing import Tuple, List
    from ..maze_gen import MazeGenerator

except ImportError as e:
    print(e)
    exit(0)


class Generator():
    def __init__(self, maze: "MazeGenerator") -> None:
        """stores maze_data"""
        self.maze = maze

    def add_walls_to_cells(self) -> None:
        """add a Wall to every Cell, border==True if on edges"""
        for cell in self.maze.cells.values():
            (x, y) = cell.coords
            if x == 0:
                cell.west = Wall(True)
            if y == 0:
                cell.north = Wall(True)

            if x < self.maze.data.width - 1:
                right_cell = self.maze.cells[(x + 1, y)]
                if right_cell:
                    wall_x = Wall(False)
                    cell.east = wall_x
                    right_cell.west = wall_x
            else:
                cell.east = Wall(True)
            if y < self.maze.data.height - 1:
                south_cell = self.maze.cells[(x, y + 1)]
                if south_cell:
                    wall_y = Wall(False)
                    cell.south = wall_y
                    south_cell.north = wall_y
            else:
                cell.south = Wall(True)

    def add_42(self) -> None:
        """close every cell at 42 coordinates (middle) or print an error"""
        if self.maze.data.width < 10 or self.maze.data.height < 10:
            return
        mid_x = self.maze.data.width // 2
        mid_y = self.maze.data.height // 2
        coords = [
            (mid_x - 1, mid_y),
            (mid_x - 2, mid_y),
            (mid_x - 3, mid_y),
            (mid_x - 3, mid_y - 1),
            (mid_x - 3, mid_y - 2),
            (mid_x - 1, mid_y + 1),
            (mid_x - 1, mid_y + 2),
            (mid_x + 1, mid_y),
            (mid_x + 2, mid_y),
            (mid_x + 3, mid_y),
            (mid_x + 3, mid_y - 1),
            (mid_x + 3, mid_y - 2),
            (mid_x + 1, mid_y + 1),
            (mid_x + 1, mid_y + 2),
            (mid_x + 2, mid_y - 2),
            (mid_x + 1, mid_y - 2),
            (mid_x + 2, mid_y + 2),
            (mid_x + 3, mid_y + 2),
        ]
        if self.maze.data.entry in coords or self.maze.data.solution in coords:
            print("Maze too tight to fit 42 in !")
            return
        for coor_to_close in coords:
            cell_to_close = self.maze.cells.get(coor_to_close)
            if cell_to_close:
                Generator.close_cell(cell_to_close)

    @staticmethod
    def close_cell(cell: Cell) -> None:
        """closes walls in every direction and sets them as borders"""
        for drct in ("north", "south", "east", "west"):
            w = getattr(cell, drct)
            if w is not None and not w.border:
                w.border = True
        cell.closed = True

    def recursive_backtracking(self) -> None:
        """
        Generates a maze based on a recursive algorithm

        starting values are: the starting cell
        passes a list of directions of which to try to explore cells
        """
        start = self.maze.cells[self.maze.data.entry]
        setrecursionlimit(10000)
        self.carve_passages(start)

    def carve_passages(self, cell: Cell) -> None:
        """
        Worker function for the backtracking algorithm

        shuffles the directions in which to try to explore
        marks the current cell as visited
        gets neighbouring cell for each direction (None if out of bounds)
        checks if the neighbouring cell has not been visited
        then checks if the wall is breakable
        if these two checks are correct: calls itself with neigbour
        else: parses other directions(backtracks) until all cells visited
        """

        directions = ['north', 'south', 'east', 'west']
        shuffle(directions)
        cell.visited = True
        for direction in directions:
            neighbour = self.maze.cells.get(self.get_direction_coordinates(
                cell, direction))
            if neighbour is None:
                continue
            if not neighbour.visited:
                wall = getattr(cell, direction)
                if not wall or wall.border:
                    continue
                if self.try_open_wall(cell, neighbour, wall):
                    self.carve_passages(neighbour)

    def get_direction_coordinates(self, cell: Cell,
                                  direction: str) -> Tuple[int, int]:
        """return (x, y) coordinates of cell in given direction"""
        if direction == 'north':
            return (cell.x, cell.y - 1)
        if direction == 'south':
            return (cell.x, cell.y + 1)
        if direction == 'west':
            return (cell.x - 1, cell.y)
        if direction == 'east':
            return (cell.x + 1, cell.y)
        return (cell.x, cell.y - 1)

    def try_open_wall(self, from_cell: Cell, to_cell: Cell,
                      wall: Wall) -> bool:
        """Open a wall if conditions are met and saves info, return bool"""
        if wall.open:
            return True
        wall.open = True
        if self.maze_has_three_by_three([from_cell, to_cell]):
            wall.open = False
            return False
        self.maze.gen_path[to_cell.coords] = self.get_hex_digit(to_cell)
        self.maze.gen_path[from_cell.coords] = self.get_hex_digit(from_cell)
        return True

    def maze_has_three_by_three(self, cell_list: List[Cell]) -> bool:
        """Check all neighbouring cells for 3x3 break, return bool"""
        for cell in cell_list:
            if self.cell_has_three_by_three(cell):
                return True
            (x, y) = cell.coords
            directions = {
                    "north": (x, y - 1),
                    "north_east": (x + 1, y - 1),
                    "north_west": (x - 1, y - 1),
                    "south": (x, y + 1),
                    "south_east": (x + 1, y + 1),
                    "south_west": (x - 1, y + 1),
                    "east": (x + 1, y),
                    "west": (x - 1, y)
                    }
            for coordinates in directions.values():
                neighbour = self.maze.cells.get(coordinates)
                if neighbour is None:
                    continue
                if self.cell_has_three_by_three(neighbour):
                    return True
        return False

    def cell_has_three_by_three(self, cell: Cell) -> bool:
        """Check if an individual cell is part of a 3x3, return bool"""
        (x, y) = cell.coords
        if x <= 0 or x >= self.maze.data.width - 1:
            return False
        if y <= 0 or y >= self.maze.data.height - 1:
            return False
        center = self.maze.cells[(x, y)]
        north_cell = self.maze.cells[(x, y - 1)]
        west_cell = self.maze.cells[(x - 1, y)]
        east_cell = self.maze.cells[(x + 1, y)]
        south_cell = self.maze.cells[(x, y + 1)]
        internal_walls = [
            center.north,
            center.south,
            center.east,
            center.west,
            north_cell.east,
            north_cell.west,
            east_cell.north,
            east_cell.south,
            west_cell.north,
            west_cell.south,
            south_cell.east,
            south_cell.west
        ]
        for wall in internal_walls:
            if wall is None:
                return False
            if wall.border:
                return False
            if not wall.open:
                return False
        return True

    @staticmethod
    def get_hex_digit(cell: Cell) -> int:
        """convert a cell object to its hexadecimal bit representation"""
        bits = 0
        if cell.north and not cell.north.open:
            bits |= 1
        if cell.east and not cell.east.open:
            bits |= 2
        if cell.south and not cell.south.open:
            bits |= 4
        if cell.west and not cell.west.open:
            bits |= 8
        return bits

    def prim(self) -> None:
        """Prim's algorithm for breaking walls in a maze"""
        entry = self.maze.cells[self.maze.data.entry]
        frontier = []
        entry.visited = True
        frontier += self.get_walls(entry)
        while frontier:
            link = choice(frontier)
            frontier.remove(link)
            from_cell, to_cell, wall = link
            if to_cell.visited:
                continue
            if self.try_open_wall(from_cell, to_cell, wall):
                to_cell.visited = True
                frontier += self.get_walls(to_cell)

    def get_walls(self, cell: Cell) -> List[Tuple[Cell, Cell, Wall]]:
        """return a tuple[Cell, Cell, Wall] to get info on neighbour cell"""
        directions = {
                "north": (cell.x, cell.y - 1),
                "south": (cell.x, cell.y + 1),
                "west": (cell.x - 1, cell.y),
                "east": (cell.x + 1, cell.y),
                }
        links = []
        for direction, coordinates in directions.items():
            wall = getattr(cell, direction)
            if wall and not wall.border:
                neighbour = self.maze.cells.get(coordinates)
                if not neighbour:
                    continue
                if neighbour.visited:
                    continue
                if not neighbour.closed:
                    links.append((cell, neighbour, wall))
        return links

    def open_other_paths(self) -> bool:
        """If maze is not perfect, open some random walls

        return true on success and false if no wall could be broken
        """
        links = []
        for cell in self.maze.cells.values():
            if not cell.closed:
                new = self.get_other_paths(cell)
                if new:
                    links += new
        budget = max(1, len(links)//5)
        i = 0
        shuffle(links)
        for link in links:
            if self.try_open_wall(*link):
                i += 1
            if i >= budget:
                break
        if i == 0:
            return False
        return True

    def get_other_paths(self, cell: Cell) -> List[Tuple[Cell, Cell, Wall]]:
        """return information on neighbouring cells to try to open walls"""
        links = []
        directions = {
            "north": (cell.x, cell.y - 1),
            "south": (cell.x, cell.y + 1),
            "east": (cell.x + 1, cell.y),
            "west": (cell.x - 1, cell.y),
            }
        for drct, coords in directions.items():
            wall = getattr(cell, drct)
            if wall and not wall.border and not wall.open:
                neightbor_cell = self.maze.cells[coords]
                if not neightbor_cell.closed:
                    if (cell.x, cell.y) < (neightbor_cell.x, neightbor_cell.y):
                        links.append((cell, neightbor_cell, wall))
        return links

    def reset_maze(self) -> None:
        """Set all cells to unvisited and all walls to closed"""
        for cell in self.maze.cells.values():
            cell.visited = False
            for drct in ("north", "south", "east", "west"):
                wall = getattr(cell, drct)
                if wall is None:
                    continue
                if wall.border:
                    wall.open = False
                    continue
                if wall.open:
                    wall.open = False
