try:
    from mazegen.cells.cell import Cell
    from mazegen.errors.maze_error import MazeError
    from mazegen.validator.maze_validator import MazeValidator
    from mazegen.custom_dataclasses.solver_paths import SolverPaths
    from mazegen.parser.parser import parse_config, parse_config_from_txt
    from pydantic import ValidationError
    from typing import Dict, Any, Tuple
    from random import choice, seed
except ImportError as e:
    print(e)
    exit(0)


class MazeGenerator():
    def __init__(self) -> None:
        """Maze generator that gathers data and works on instanciation

        parses with parse_config() to gather data from config passed as arg
        imports the three needed objects to work with and instanciates them
        creates all internal object with initialize_maze()
        runs process_all, which in turns runs:
        generate_maze()
        pathfinding()
        visualize()
        gen_output_file()
        """
        try:
            config = parse_config()
            try:
                from mazegen.generator.generator import Generator
                from mazegen.pathfinder.pathfinder import PathFinder
                from mazegen.visualizer.maze_visualizer import MazeVisualizer
            except ImportError as e:
                print(e)
                exit(0)
            self.generator = Generator(self)
            self.pathfinder = PathFinder(self)
            self.visualizer = MazeVisualizer()
            self.initialize_maze(config)
        except ValidationError as e:
            print(e)
            exit(0)
        self.process_all()

    def initialize_maze(self, config: Dict[str, Any]) -> None:
        """Contains all useful data for working on the maze

        data is a BaseModel object (raises a ValidationError if not correct)
        cells is a dict of coordinates tuple[int, int] mapping to a Cell
        gen_path is a dictionnary of coordinates mapping to hexadecimal
        solver_paths is a complex object that recuperates data from
        pathfinding algorithms
        """
        self.data = MazeValidator(**config)
        self.cells: dict[tuple[int, int], Cell] = self.gen_cells()
        self.gen_path: dict[tuple[int, int], int] = {}
        self.solver_paths = SolverPaths(visited=set(),
                                        paths={},
                                        solution={},
                                        inputs_to_exit='')

    def process_all(self) -> None:
        """Call all methods in succession to render maze"""
        self.generate_maze()
        self.pathfinding()
        self.visualize()
        self.gen_output_file()

    def restart_from_textual(self) -> None:
        """Gather a new config file and runs the maze again"""
        config = parse_config_from_txt()
        self.initialize_maze(config)
        self.generate_maze()
        self.pathfinding()
        self.gen_output_file()

    def gen_cells(self) -> Dict[Tuple[int, int], Cell]:
        """generates Cell objects for the maze"""
        maze = {}
        for x in range(0, self.data.width):
            for y in range(0, self.data.height):
                maze[(x, y)] = Cell(x, y)
        return maze

    def generate_maze(self) -> None:
        """generate maze components and choose which algorithm to use

        has a "retry" factor if Prim fails to generate
        if no seed was specified, will simply regenerate with chosen algo
        if "Prim" is not enforced, will use Recursive Backtracking instead
        else: goes again with an incremented seed until success
        """
        generator = self.generator
        generator.add_walls_to_cells()
        generator.add_42()
        if self.data.seed:
            seed(self.data.seed)
        algos = {
                "Prim": generator.prim,
                "Backtracking": generator.recursive_backtracking}
        if self.data.generative_algorithm is None:
            self.data.generative_algorithm = choice(list(algos.keys()))
        algorithm = algos[self.data.generative_algorithm]
        while True:
            algorithm()
            if self.is_maze_ok():
                if self.data.perfect is False:
                    if generator.open_other_paths() is False:
                        pass
                    else:
                        break
                else:
                    break
            generator.reset_maze()
            if self.data.seed is None:
                continue
            if self.data.generative_algorithm == "Undefined":
                algorithm = algos['Backtracking']
                continue
            self.data.seed += 1
            seed(self.data.seed)

    def is_maze_ok(self) -> bool:
        """Method that checks if all cells have been visited"""
        for cell in self.cells.values():
            if not cell.visited and not cell.closed:
                return False
        return True

    def pathfinding(self) -> None:
        """runs pathfinder algorithm and outputs useful data in variable"""
        pathfinder = self.pathfinder
        algos = {
                "BFS": pathfinder.breadth_first_search,
                "A*": pathfinder.a_star}
        if self.data.solver_algorithm is None:
            self.data.solver_algorithm = choice(list(algos.keys()))
        algorithm = algos[self.data.solver_algorithm]
        self.solver_paths = algorithm()

    def visualize(self) -> None:
        """generates the visual components using textual and creates file"""
        if not self.gen_path or len(self.solver_paths.paths) == 0:
            raise MazeError("Missing configuration")
        app = self.visualizer
        app.maze = self
        app.config = self.data
        app.init_masks = self.gen_path
        app.init_path_finder = {self.data.entry: self.data.entry,
                                **self.solver_paths.paths}
        app.init_path_solution = {self.data.entry: self.data.entry,
                                  **self.solver_paths.solution}
        app.run()

    def get_hexa(self, decimal: int) -> str:
        """return hexa character for a given int"""
        base = "0123456789ABCDEF"
        return base[decimal]

    def gen_output_file(self) -> None:
        """write desired output format in output file specified as param"""
        from mazegen.generator.generator import Generator
        chars = []
        for y in range(0, self.data.height):
            for x in range(0, self.data.width):
                cell = self.cells.get((x, y))
                if cell:
                    digit = Generator.get_hex_digit(cell)
                    hex_digit = self.get_hexa(digit)
                    chars.append(hex_digit)
            chars.append("\n")
        out = "".join(chars)
        with open(self.data.output_file, "w") as f:
            f.write(out)
            entry = f"\n{str(self.data.entry[0])}"
            entry += f", {str(self.data.entry[1])}"
            f.write(entry)
            solution = f"\n{str(self.data.solution[0])}"
            solution += f", {str(self.data.solution[1])}\n"
            f.write(solution)
            f.write(self.solver_paths.inputs_to_exit)
            f.write("\n")
