try:
    from typing import Dict, Tuple, List
    from random import shuffle
    from ..cells.cell import Cell
    from ..maze_gen import MazeGenerator
    from ..custom_dataclasses.solver_paths import SolverPaths
except ImportError as e:
    print(e)
    exit(0)


class SolverError(Exception):
    pass


class PathFinder():
    """
    PathFinder class: methods and algorithms to parse a maze

    two algorithm methods:
    breadth_first_search() and a_star()
    both yield a dict with two keys{'visited': Tuple[int, int],
    'paths': Tuple[int ,int]} for further processing
    get_reachable_neighbours() is a method to find nearby reachable cells
    PriorityQueue Class and all its methods are for A* usage (heuristics)
    get_manhattan_distance() yields an int for absolute distance of two coords
    convert_path() takes the 'paths' key of algo yield and returns only the
    shortest path
    convert_path_to_str() will convert that path into in NSEW format
    """
    def __init__(self, maze: MazeGenerator) -> None:
        """Pathfinder class contains a MazeGenerator reference"""
        self.maze = maze

    def breadth_first_search(self) -> SolverPaths:
        """
        BFS pathfinder using queue and visited stacks

        frontier is the queue where cell coordinates to explore are kept
        visited is the list that permits to skip over visited cells
        backtrack is a dict containing the paths taken between cells
        method ends when frontier is empty(no exit)
        or when the cell taken off frontier matches exit coordinates
        return a dict with visited list and backtrack dict
        """
        frontier = [self.maze.data.entry]
        visited = set()
        backtrack = {self.maze.data.entry: self.maze.data.entry}
        while frontier:
            current = frontier.pop(0)
            if current == self.maze.data.solution:
                break
            cell = self.maze.cells[current]
            visited.add(current)
            neighbours = self.get_reachable_neighbours(cell)
            for to_visit in neighbours:
                if to_visit.coords in visited:
                    continue
                backtrack[to_visit.coords] = current
                frontier.append(to_visit.coords)
        return SolverPaths(
                visited=visited,
                paths=backtrack,
                solution=self.convert_path(backtrack),
                inputs_to_exit=self.convert_path_to_str(
                    self.convert_path(backtrack))
                )

    def a_star(self) -> SolverPaths:
        """
        A* pathfinder that returns a dictionnary with paths taken and visited

        behaves like a standard bfs but with a priority queue
        priority is calculated with manhattan distance (absolute distance)
        and distance relative to the starting cell
        g_costs represents a dict where relative distances are kept
        f_costs represents the total cost g + h for each cell
        each cell is added to the queue as a Tuple[int, int, Cell]
        pathfinder works until queue is empty (no solution) or
        until exit is found
        traversal is noted in paths, which is a Dict containing
        {child_cell: parent_cell}
        visited is a set{cell} of traversed nodes
        """
        start = self.maze.cells[self.maze.data.entry]
        end = self.maze.cells[self.maze.data.solution]
        g_costs = {cell: float('inf') for cell in self.maze.cells.values()}
        f_costs = {cell: float('inf') for cell in self.maze.cells.values()}
        g_costs[start] = 0
        f_costs[start] = self.get_manhattan_distance(start, end) + 0
        queue = self.PriorityQueue()
        queue.add_to_queue((int(f_costs[start]), int(g_costs[start]), start))
        paths = {}
        visited = set()
        while queue.list:
            cell = queue.pop_cell()
            if cell.coords == self.maze.data.solution:
                break
            visited.add(cell)
            neighbours = self.get_reachable_neighbours(cell)
            for neighbour in neighbours:
                if neighbour in visited:
                    continue
                temp_g = g_costs[cell] + 1
                temp_f = temp_g + self.get_manhattan_distance(neighbour, end)
                if not queue.is_in_queue(neighbour):
                    g_costs[neighbour] = temp_g
                    f_costs[neighbour] = temp_f
                    queue.add_to_queue((int(temp_f), int(temp_g), neighbour))
                    paths.update({neighbour.coords: cell.coords})
                if temp_f < f_costs[neighbour]:
                    g_costs[neighbour] = temp_g
                    f_costs[neighbour] = temp_f
                    queue.update_value((int(temp_f), int(temp_g), neighbour))
                    paths.update({neighbour.coords: cell.coords})
        return SolverPaths(
                visited=set([cell.coords for cell in visited]),
                paths=paths,
                solution=self.convert_path(paths),
                inputs_to_exit=self.convert_path_to_str(
                    self.convert_path(paths))
                )

    def get_reachable_neighbours(self, cell: Cell) -> List[Cell]:
        """return a list of cells reachable by the one passed as parameter"""
        randomized_directions = ["north", "south", "east", "west"]
        shuffle(randomized_directions)
        directions = {
            "north": (cell.x, cell.y - 1),
            "south": (cell.x, cell.y + 1),
            "east": (cell.x + 1, cell.y),
            "west": (cell.x - 1, cell.y),
            }
        return [self.maze.cells[directions[direction]] for direction in
                randomized_directions if getattr(cell, direction).open]

    class PriorityQueue():
        """data class to handle priority queue operations"""
        def __init__(self) -> None:
            """contains a list"""
            self.list: list[tuple[int, int, Cell]] = []

        def add_to_queue(self, cell: Tuple[int, int, Cell]) -> None:
            """add a cell in descending order based on cost (f > g)"""
            if len(self.list) == 0:
                self.list.append(cell)
                return
            cell_f, cell_g, unpacked = cell
            for i, stored_cell in enumerate(self.list):
                f_cost, g_cost = stored_cell[0], stored_cell[1]
                if cell_f > f_cost:
                    self.list.insert(i, cell)
                    break
                if cell_f == f_cost and cell_g > g_cost:
                    self.list.insert(i, cell)
                    break
                if cell_f == f_cost and cell_g == g_cost:
                    self.list.insert(i, cell)
                    break
                if i == len(self.list) - 1:
                    self.list.append(cell)

        def pop_cell(self) -> Cell:
            """pop method to recuperate the Cell in the tuple"""
            cell_data = self.list.pop()
            return cell_data[2]

        def is_in_queue(self, cell: Cell) -> bool:
            """return a boolean for node presence in queue"""
            for item in self.list:
                if item[2] is cell:
                    return True
            return False

        def update_value(self, cell: Tuple[int, int, Cell]) -> None:
            """find an already existing cell and update costs"""
            for data in self.list:
                if cell[2] == data[2]:
                    self.list.remove(data)
                    self.add_to_queue(cell)

    def get_manhattan_distance(self, cell1: Cell, cell2: Cell) -> int:
        """takes two cells and return their absolute distance in a graph"""
        x1, y1 = cell1.x, cell1.y
        x2, y2 = cell2.x, cell2.y
        return abs(x1 - x2) + abs(y1 - y2)

    def convert_path(self, paths:
                     Dict[Tuple[int, int],
                          Tuple[int, int]]) -> Dict[Tuple[int, int],
                                                    Tuple[int, int]]:
        """return the path to the exit in dict format or raise an error"""
        if self.maze.data.solution not in paths:
            raise SolverError("Exit has not been found !")
        cursor = self.maze.data.solution
        path = {}
        while cursor != self.maze.data.entry:
            path[cursor] = paths[cursor]
            cursor = paths[cursor]
        path[self.maze.data.entry] = self.maze.data.entry
        path = dict(reversed(list(path.items())))
        return path

    def convert_path_to_str(self, path: Dict[Tuple[int, int],
                                             Tuple[int, int]]) -> str:
        """return a string containing directions from a dict of coords"""
        verbose_path = str()
        for cell_from, cell_to in path.items():
            if cell_to[0] == cell_from[0] + 1:
                verbose_path += 'W'
            if cell_to[0] == cell_from[0] - 1:
                verbose_path += 'E'
            if cell_to[1] == cell_from[1] + 1:
                verbose_path += 'N'
            if cell_to[1] == cell_from[1] - 1:
                verbose_path += 'S'
        return verbose_path
