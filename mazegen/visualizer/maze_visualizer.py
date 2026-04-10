from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.reactive import reactive
from textual.widgets import (Label, Button, Header, Footer, Static, Input,
                             Select, Switch)
from textual.validation import Number
from textual.widget import Widget
from typing import Any
from textual.strip import Strip
from rich.segment import Segment
from rich.style import Style
from textual.timer import Timer
from rich.text import Text
import random


class VisualizerError(Exception):
    """Custom exception for maze visualizer errors."""
    pass


class MazeViewer(Widget):
    """Widget for displaying and interacting with the maze visualization."""
    created: reactive[set[tuple[int, int]]] = reactive(set(),
                                                       repaint=True)
    walls_drawn: reactive[set[tuple[str, int, int]]] = reactive(set(),
                                                                repaint=True)
    cells_42: reactive[set[tuple[int, int]]] = reactive(set(),
                                                        repaint=True)
    width_cells = reactive(0, repaint=True)
    height_cells = reactive(0, repaint=True)
    entry_cell = reactive((0, 0), repaint=True)
    solution_cell = reactive((0, 0), repaint=True)
    masks: reactive[dict[tuple[int, int], int]] = reactive({}, repaint=True)
    path_finder: reactive[dict[tuple[int, int], tuple[int, int]]] =\
        reactive({}, repaint=True)
    path_solution: reactive[dict[tuple[int, int], tuple[int, int]]] =\
        reactive({}, repaint=True)
    wall_mode = reactive("hidden", repaint=True)

    printer = "  "

    style_cell: reactive[Style] = reactive(Style(), repaint=True)
    style_42: reactive[Style] = reactive(Style(), repaint=True)
    style_empty: reactive[Style] = reactive(Style(), repaint=True)
    style_wall: reactive[Style] = reactive(Style(), repaint=True)
    style_entry: reactive[Style] = reactive(Style(), repaint=True)
    style_solution: reactive[Style] = reactive(Style(), repaint=True)
    style_path_finder: reactive[Style] = reactive(Style(), repaint=True)
    style_path_solution: reactive[Style] = reactive(Style(), repaint=True)
    style_wall_open: reactive[Style] = reactive(Style(), repaint=True)
    style_wall_hidden: reactive[Style] = reactive(Style(), repaint=True)

    def watch_width_cells(self, _: int) -> None:
        """Update widget width when the number of cells changes."""
        self.styles.width = 2 + self.width_cells * (len(self.printer) + 2)

    def watch_height_cells(self, _: int) -> None:
        """Update widget height when the number of cells changes."""
        self.styles.height = self.height_cells * 2 + 1

    def get_east_wall_open(self, x: int, y: int) -> bool:
        """Check if the east wall of a cell is open."""
        hexa = self.masks.get((x, y), 15)
        if hexa & 2:
            return False
        return True

    def get_south_wall_open(self, x: int, y: int) -> bool:
        """Check if the south wall of a cell is open."""
        hexa = self.masks.get((x, y), 15)
        if hexa & 4:
            return False
        return True

    def get_wall_style(self, c: str, x: int, y: int) -> Style:
        """Return the style for a wall based on its type and state."""
        if self.wall_mode == "hidden":
            return self.style_wall_hidden

        elif self.wall_mode == "draw":
            if (c, x, y) in self.walls_drawn:
                return self.style_wall
            return self.style_wall_hidden

        elif self.wall_mode == "open":
            if c == "H":
                if y == 0 or y == self.height_cells:
                    return self.style_wall
                w_open = self.get_south_wall_open(x, y - 1)
                if w_open:
                    if (x, y) in self.path_solution and (x, y - 1)\
                            in self.path_solution:
                        return self.style_path_solution
                    elif (x, y) in self.path_finder and (x, y - 1)\
                            in self.path_finder:
                        return self.style_path_finder
                    return self.style_wall_open
                else:
                    return self.style_wall

            if c == "V":
                if x == 0 or x == self.width_cells:
                    return self.style_wall
                w_open = self.get_east_wall_open(x - 1, y)
                if w_open:
                    if (x, y) in self.path_solution and (x - 1, y)\
                            in self.path_solution:
                        return self.style_path_solution
                    elif (x, y) in self.path_finder and (x - 1, y)\
                            in self.path_finder:
                        return self.style_path_finder
                    return self.style_wall_open
                else:
                    return self.style_wall
        return self.style_wall_hidden

    def get_cell_style(self, cell: tuple[int, int]) -> Style:
        """Return the style for a cell based on its role in the maze."""
        if cell == self.entry_cell:
            style = self.style_entry
        elif cell == self.solution_cell:
            style = self.style_solution
        elif cell in self.cells_42:
            style = self.style_42
        elif cell in self.path_solution:
            style = self.style_path_solution
        elif cell in self.path_finder:
            style = self.style_path_finder
        elif cell in self.created:
            style = self.style_cell
        else:
            style = self.style_empty
        return style

    def render_line(self, row: int) -> Strip:
        """Render a single line of the maze for display."""
        segs = []
        cols = self.width_cells * 2 + 1

        y = row // 2
        if row % 2 == 0:
            if self.wall_mode == "hidden":
                wall_basic = self.style_wall_hidden
            else:
                wall_basic = self.style_wall
            segs.append(Segment(self.printer, wall_basic))
            for col in range(cols):
                x = col // 2
                if col % 2 == 0:
                    segs.append(Segment(self.printer,
                                        self.get_wall_style("H", x, y)))
                else:
                    segs.append(Segment(self.printer, wall_basic))
            return Strip(segs)
        else:
            segs.append(Segment(self.printer, self.get_wall_style("V", 0, y)))
            for col in range(cols):
                x = col // 2
                if col % 2 != 0:
                    segs.append(Segment(self.printer,
                                        self.get_wall_style("V", x + 1, y)))
                else:
                    c = (x, y)
                    style = self.get_cell_style(c)
                    segs.append(Segment(self.printer, style))
        return Strip(segs)


class MazeVisualizer(App[None]):
    """Textual application for visualizing and interacting with mazes."""
    try:
        from ..validator.maze_validator import MazeValidator
        from ..maze_gen import MazeGenerator
    except ImportError as e:
        print(e)
        exit(0)
    CSS_PATH = "styles.css"
    maze: MazeGenerator
    config: MazeValidator
    init_masks: reactive[dict[tuple[int, int], int]] = \
        reactive({})
    init_path_finder: reactive[dict[tuple[int, int], tuple[int, int]]] = \
        reactive({})
    init_path_solution: reactive[dict[tuple[int, int], tuple[int, int]]] = \
        reactive({})
    paused = reactive(False)
    styles_list: reactive[dict[str, dict[str, Style]]] = reactive({})
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("space", "toggle_pause", "Play/Pause"),
        ("r", "regenerate", "Regenerate"),
        ("c", "change_colors", "Change Colors"),
        ("p", "toggle_path", "Show/Hide Path"),
        ("+", "faster", "Faster"),
        ("-", "slower", "Slower"),
    ]
    TITLE = "A-MAZE-ING"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events in the UI sidebar."""
        bid = event.button.id
        if bid == "btn-quit":
            self.exit()
        elif bid == "btn-regenerate":
            self.action_regenerate()
        elif bid == "btn-play":
            self.action_toggle_pause()
        elif bid == "btn-path":
            self.action_toggle_path()
        elif bid == "btn-colors":
            self.action_change_colors()
        elif bid == "btn-faster":
            self.action_faster()
        elif bid == "btn-slower":
            self.action_slower()
        elif bid == "btn-save":
            self.action_save_config()

    def action_save_config(self) -> None:
        """Save the current config and restart the maze visualization."""
        err_box = self.query_one("#err-msg", Static)
        success_box = self.query_one("#success-msg", Static)
        err_box.update("")
        success_box.update("")
        try:
            data = self.collect_config_input()
            self.MazeValidator(**data)

            with open("config.txt", "w") as fd:
                fd.write(
                    f"WIDTH={data['width']}\n"
                    f"HEIGHT={data['height']}\n"
                    f"ENTRY={data['entry']}\n"
                    f"EXIT={data['exit']}\n"
                    f"OUTPUT_FILE={data['output_file']}\n"
                    f"PERFECT={data['perfect']}\n"
                    f"SEED={data['seed']}\n"
                    f"GENERATIVE_ALGORITHM={data['generative_algorithm']}\n"
                    f"SOLVER_ALGORITHM={data['solver_algorithm']}"
                )
            self.maze.restart_from_textual()
            self.maze.gen_output_file()
            self.init_masks = self.maze.gen_path
            self.init_path_finder = {self.maze.data.entry:
                                     self.maze.data.entry,
                                     **self.maze.solver_paths.paths}
            self.init_path_solution = {self.maze.data.entry:
                                       self.maze.data.entry,
                                       **self.maze.solver_paths.solution}
            self.config = self.maze.data
            self.view.width_cells = self.config.width
            self.view.height_cells = self.config.height
            self.view.entry_cell = self.config.entry
            self.view.solution_cell = self.config.solution
            self.restart_visu()
            success_box.update("Config saved and maze restarted.")
        except Exception as e:
            err_box.update(Text(f"Error: {e}"))

    def action_toggle_path(self) -> None:
        """Toggle the display of the solution path in the maze."""
        if not self.finish:
            return
        self.show_path: bool
        self.step: int
        if self.show_path:
            self.show_path = False
            self.view.path_finder = {}
            self.view.path_solution = {}
            self.counter_pf = 0
            self.counter_ps = 0
            if self.step >= 5:
                self.step = 5
        else:
            self.show_path = True
            self.view.path_finder = {}
            self.view.path_solution = {}
            self.counter_pf = 0
            self.counter_ps = 0
            self.step = 5
            self.timer.resume()

    def action_regenerate(self) -> None:
        """Regenerate the maze and update the visualization."""
        try:
            self.maze.generator.reset_maze()
            self.maze.generate_maze()
            self.maze.pathfinding()
            self.init_masks = self.maze.gen_path
            self.init_path_finder = {self.maze.data.entry:
                                     self.maze.data.entry,
                                     **self.maze.solver_paths.paths}
            self.init_path_solution = {self.maze.data.entry:
                                       self.maze.data.entry,
                                       **self.maze.solver_paths.solution}
            self.restart_visu()
            self.maze.gen_output_file()
        except Exception as e:
            err_box = self.query_one("#err-msg", Static)
            err_box.update(f"Error: {e}")

    def action_faster(self) -> None:
        """Increase the animation speed of the visualization."""
        self.paused = True
        self.timer.pause()
        self.batch_div: int = max(1, self.batch_div - 10)
        self.paused = False
        self.timer.resume()

    def action_slower(self) -> None:
        """Decrease the animation speed of the visualization."""
        self.paused = True
        self.timer.pause()
        self.batch_div = min(1000, self.batch_div + 10)
        self.paused = False
        self.timer.resume()

    def action_toggle_pause(self) -> None:
        """Pause or resume the maze animation."""
        if self.paused:
            self.paused = False
            self.timer.resume()
        else:
            self.paused = True
            self.timer.pause()

    def action_change_colors(self) -> None:
        """Randomize the color scheme of the maze visualization."""
        self.palette = random.choice(list(self.styles_list.values()))
        self.set_colors()
        self.restart_visu()

    def restart_visu(self) -> None:
        """Reset and restart the maze visualization state."""
        self.timer.pause()
        self.paused = True
        msg_42 = self.query_one("#pattern-42-err", Static)
        msg_42.update("")
        height = self.view.height_cells
        width = self.view.width_cells
        self.rng = random.Random(self.config.seed)
        self.step = 1
        self.finish: bool = False
        self.step_name = "Generating Cells"
        self.show_path = True
        self.view.wall_mode = "hidden"
        self.view.created = set()
        self.view.walls_drawn = set()
        self.view.cells_42 = set()
        self.view.masks = {}
        self.view.path_finder = {}
        self.view.path_solution = {}
        self.counter = 0
        self.order = [(x, y) for y in range(height) for x in range(width)]
        self.rng.shuffle(self.order)
        self.counter_w = 0
        order_w = []
        for y in range(height + 1):
            for x in range(width):
                order_w.append(("H", x, y))
        for x in range(width + 1):
            for y in range(height):
                order_w.append(("V", x, y))
        self.order_w = order_w
        self.rng.shuffle(self.order_w)
        self.counter_o = 0
        self.counter_pf = 0
        self.counter_ps = 0
        self.paused = False
        self.timer.resume()

    def compose(self) -> ComposeResult:
        """Compose the UI layout for the maze visualizer app."""
        if not self.config:
            raise VisualizerError("Missing config for visualization.")
        self.view = MazeViewer(id="maze")
        self.view.width_cells = self.config.width
        self.view.height_cells = self.config.height
        self.view.entry_cell = self.config.entry
        self.view.solution_cell = self.config.solution
        self.rng = random.Random(self.config.seed)
        self.styles_list = self.get_styles()
        self.palette = self.styles_list["tokyo_night"]
        self.step = 1
        self.show_path = True
        self.finish = False
        self.step_name = "Generating Cells"
        self.theme = "tokyo-night"
        yield Header()
        config_inputs = Vertical(
            Horizontal(
                Vertical(
                    Label("Width (2-100):"),
                    Input(
                        value=str(self.config.width),
                        validators=[Number(minimum=2, maximum=100)],
                        id="input-width",
                    ),
                    id="v-width",
                ),
                Vertical(
                    Label("Height (2-100):"),
                    Input(
                        value=str(self.config.height),
                        validators=[Number(minimum=2, maximum=100)],
                        id="input-height",
                    ),
                    id="v-height",
                ),
                id="wh-line"
            ),
            Horizontal(
                Vertical(
                    Label("Entry x:"),
                    Input(
                        value=str(self.view.entry_cell[0]),
                        validators=[Number(minimum=0, maximum=100)],
                        id="input-entry-x",
                    ),
                    id="v-entry-x",
                ),
                Vertical(
                    Label("Entry y:"),
                    Input(
                        value=str(self.view.entry_cell[1]),
                        validators=[Number(minimum=0, maximum=100)],
                        id="input-entry-y",
                    ),
                    id="v-entry-y",
                ),
                id="entry-line"
            ),
            Horizontal(
                Vertical(
                    Label("Exit x:"),
                    Input(
                        value=str(self.view.solution_cell[0]),
                        validators=[Number(minimum=0, maximum=100)],
                        id="input-exit-x",
                    ),
                    id="v-exit-x",
                ),
                Vertical(
                    Label("Exit y:"),
                    Input(
                        value=str(self.view.solution_cell[1]),
                        validators=[Number(minimum=0, maximum=100)],
                        id="input-exit-y",
                    ),
                    id="v-exit-y",
                ),
                id="exit-line"
            ),
            Horizontal(
                Vertical(
                    Label("Seed:"),
                    Input(
                        value="" if self.config.seed is None else
                        str(self.config.seed),
                        validators=[Number(minimum=0)],
                        id="input-seed",
                    ),
                    id="v-seed",
                ),
                Vertical(
                    Label("Output File:"),
                    Input(
                        value=str(self.config.output_file),
                        id="input-file",
                    ),
                    id="v-file",
                ),
                id="seed-line"
            ),
            Vertical(
                Label("Gen Algo:"),
                Select(
                    options=[
                        ("Prim", "Prim"),
                        ("Backtracking", "Backtracking"),
                    ],
                    value=self.config.generative_algorithm,
                    id="input-gen-algo",
                ),
                id="v-gen-algo",
            ),
            Vertical(
                Label("Solve Algo:"),
                Select(
                    options=[
                        ("BFS", "BFS"),
                        ("A*", "A*"),
                    ],
                    value=self.config.solver_algorithm or "BFS",
                    id="input-solver-algo",
                ),
                id="v-sol-algo"
            ),
            Horizontal(
                Vertical(
                    Label("Perfect:"),
                    Switch(
                        value=self.config.perfect,
                        animate=True,
                        id="input-perfect"
                        ),
                    id="v-perf",
                ),
                id="perf-save-line",
            ),
            Static("", id="success-msg"),
            id="config-inputs",
        )
        yield Horizontal(
            Static("Stats", id="stats"),
            config_inputs,
            id="top-options"
        )
        yield Static("", id="pattern-42-err")
        yield Static("", id="err-msg")
        yield Horizontal(
            ScrollableContainer(self.view, id="maze-container"),
            Vertical(
                Label("Actions", id="actions-title"),
                Button("Save & Restart", id="btn-save", variant="warning"),
                Button("Regenerate", id="btn-regenerate", variant="primary"),
                Button("Change Colors", id="btn-colors", variant="success"),
                Button("Play / Pause", id="btn-play"),
                Button("Show / Hide path", id="btn-path"),
                Button("Faster", id="btn-faster"),
                Button("Slower", id="btn-slower"),
                Button("Quit", id="btn-quit", variant="error"),
                id="sidebar",
            ),
            id="main",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize state and set up the maze visualization on mount."""
        height = self.view.height_cells
        width = self.view.width_cells
        self.set_colors()
        self.tick_rate = 0.1
        self.batch_div = 20

        self.counter = 0
        self.order = [(x, y)
                      for y in range(height)
                      for x in range(width)
                      ]
        self.rng.shuffle(self.order)
        self.view.created = set()

        self.counter_w = 0
        order_w = []
        for y in range(height + 1):
            for x in range(width):
                order_w.append(("H", x, y))
        for x in range(width + 1):
            for y in range(height):
                order_w.append(("V", x, y))
        self.order_w = order_w
        self.rng.shuffle(self.order_w)
        self.view.walls_drawn = set()

        self.counter_o = 0
        self.view.masks = {}

        self.counter_pf = 0
        self.view.path_finder = {}
        self.counter_ps = 0
        self.view.path_solution = {}
        self.timer: Timer = self.set_interval(self.tick_rate, self.tick)

    def set_colors(self) -> None:
        """Assign styles to different maze elements"""
        self.view.style_cell = self.palette["cell"]
        self.view.style_42 = self.palette["forty_two"]
        self.view.style_empty = self.palette["empty"]
        self.view.style_wall = self.palette["wall"]
        self.view.style_entry = self.palette["entry"]
        self.view.style_solution = self.palette["solution"]
        self.view.style_path_finder = self.palette["path_finder"]
        self.view.style_path_solution = self.palette["path_solution"]
        self.view.style_wall_open = self.palette["cell"]
        self.view.style_wall_hidden = self.palette["empty"]

    def get_styles(self) -> dict[str, dict[str, Style]]:
        """Return a dictionary of theme names mapped to style configurations
        for maze visualization elements."""
        return {
            "tokyo_night": {
                "cell": Style(bgcolor="#5285F5"),
                "forty_two": Style(bgcolor="#00FFFF"),
                "wall": Style(bgcolor="#3B4261"),
                "empty": Style(bgcolor="#1A1B26"),
                "entry": Style(bgcolor="#E0AF68"),
                "solution": Style(bgcolor="#F7768E"),
                "path_finder": Style(bgcolor="#E97DFF"),
                "path_solution": Style(bgcolor="#250069")
            },

            "ocean": {
                "cell": Style(bgcolor="#7CACC2"),
                "forty_two": Style(bgcolor="#FBFF00"),
                "wall": Style(bgcolor="#364555"),
                "empty": Style(bgcolor="#1A1B26"),
                "entry": Style(bgcolor="#D1D402"),
                "solution": Style(bgcolor="#E78300"),
                "path_finder": Style(bgcolor="#0357A7"),
                "path_solution": Style(bgcolor="#00E1FF"),
            },

            "matrix": {
                "cell": Style(bgcolor="#00ff41"),
                "forty_two": Style(bgcolor="#BB0000"),
                "wall": Style(bgcolor="#003b00"),
                "empty": Style(bgcolor="#1A1B26"),
                "entry": Style(bgcolor="#c40000"),
                "solution": Style(bgcolor="#ccc900"),
                "path_finder": Style(bgcolor="#A9FF78"),
                "path_solution": Style(bgcolor="#00B33C"),
            },

            "lava": {
                "cell": Style(bgcolor="#6e2e00"),
                "forty_two": Style(bgcolor="#0004FA"),
                "wall": Style(bgcolor="#3a0000"),
                "empty": Style(bgcolor="#1A1B26"),
                "entry": Style(bgcolor="#ffff00"),
                "solution": Style(bgcolor="#ff0000"),
                "path_finder": Style(bgcolor="#c56900"),
                "path_solution": Style(bgcolor="#ffaa00"),
            },

            "mountain": {
                "cell": Style(bgcolor="#554c46"),
                "forty_two": Style(bgcolor="#FF00DD"),
                "wall": Style(bgcolor="#4E3E0F"),
                "empty": Style(bgcolor="#1A1B26"),
                "entry": Style(bgcolor="#ffffff"),
                "solution": Style(bgcolor="#399248"),
                "path_finder": Style(bgcolor="#a8ce96"),
                "path_solution": Style(bgcolor="#ffaa00"),
            }
        }

    def collect_config_input(self) -> dict[str, Any]:
        """Collect and return configuration input values from the UI."""
        width = self.query_one("#input-width", Input).value.strip()
        height = self.query_one("#input-height", Input).value.strip()
        entry_x = self.query_one("#input-entry-x", Input).value.strip()
        entry_y = self.query_one("#input-entry-y", Input).value.strip()
        exit_x = self.query_one("#input-exit-x", Input).value.strip()
        exit_y = self.query_one("#input-exit-y", Input).value.strip()
        output_file = self.query_one("#input-file", Input).value.strip()
        seed = self.query_one("#input-seed", Input).value.strip() or "None"
        perfect_value = self.query_one("#input-perfect", Switch).value
        gen_algo_value = self.query_one("#input-gen-algo", Select).value
        solver_algo_value = self.query_one("#input-solver-algo", Select).value

        return {
            "width": width,
            "height": height,
            "entry": f"{entry_x},{entry_y}",
            "exit": f"{exit_x},{exit_y}",
            "output_file": output_file,
            "perfect": str(perfect_value),
            "seed": seed,
            "generative_algorithm": gen_algo_value,
            "solver_algorithm": solver_algo_value,
        }

    def show_stats(self) -> None:
        """Update the stats display with current maze information."""
        stats = self.query_one("#stats", Static)

        stats.update(
            "Stats:\n"
            f"Step: {self.step_name}\n"
            f"Batch size: {self.batch_div}\n"
            f"Created: {len(self.view.created)}\n"
            f"Walls: {len(self.view.walls_drawn)}\n"
            f"Visited: {len(self.view.path_finder)}\n"
            f"Path len: {len(self.view.path_solution)}"
        )

    def tick(self) -> None:
        """Advance the animation by one step, updating the maze state."""
        if self.step == 1:
            ok = self.tick_create_cells()
            if ok:
                self.step = 2
        elif self.step == 2:
            self.step_name = "Adding Walls"
            self.view.wall_mode = "draw"
            ok = self.tick_add_walls()
            if ok:
                self.step = 3
        elif self.step == 3:
            self.step_name = "Adding 42"
            ok = self.tick_add_42()
            if ok:
                self.step = 4
        elif self.step == 4:
            self.step_name = "Opening walls"
            self.view.wall_mode = "open"
            ok = self.tick_open_walls()
            if ok:
                self.step = 5
        elif self.step == 5:
            if not self.show_path:
                self.timer.pause()
                return
            self.step_name = "Searching solution"
            ok = self.tick_find_path()
            if ok:
                self.step = 6
        elif self.step == 6:
            self.step_name = "Showing solution"
            ok = self.tick_find_solution()
            if ok:
                self.finish = True
                self.timer.pause()
        self.show_stats()

    def tick_find_solution(self) -> bool:
        """Animate the display of the solution path step by step."""
        paths = list(self.init_path_solution.items())
        ps_len = len(paths)
        if self.counter_ps >= ps_len:
            return True
        batch = max(1, ps_len // self.batch_div)

        path = dict(self.view.path_solution)
        for _ in range(batch):
            if self.counter_ps >= ps_len:
                break
            sol_part = paths[self.counter_ps]
            curr = sol_part[0]
            prev = sol_part[1]
            self.counter_ps += 1
            path[curr] = prev
        self.view.path_solution = path
        return False

    def tick_find_path(self) -> bool:
        """Animate the display of the pathfinding process step by step."""
        paths = list(self.init_path_finder.items())
        pf_len = len(paths)
        if self.counter_pf >= pf_len:
            return True
        batch = max(1, pf_len // self.batch_div)

        path = dict(self.view.path_finder)
        for _ in range(batch):
            if self.counter_pf >= pf_len:
                break
            path_part = paths[self.counter_pf]
            curr = path_part[0]
            prev = path_part[1]
            self.counter_pf += 1
            path[curr] = prev
        self.view.path_finder = path
        return False

    def tick_open_walls(self) -> bool:
        """Animate the process of opening walls in the maze."""
        order = list(self.init_masks.items())
        if self.counter_o >= len(order):
            return True
        batch = max(1, len(order) // self.batch_div)
        opened = dict(self.view.masks)

        for _ in range(batch):
            if self.counter_o >= len(order):
                break
            w_open = order[self.counter_o]
            self.counter_o += 1
            coords = w_open[0]
            hexa = w_open[1]
            opened[coords] = hexa
        self.view.masks = opened
        return False

    def tick_add_walls(self) -> bool:
        """Animate the process of adding walls to the maze."""
        if self.counter_w >= len(self.order_w):
            return True
        batch = max(1, len(self.order_w) // self.batch_div)
        drawn = set(self.view.walls_drawn)
        for _ in range(batch):
            if self.counter_w >= len(self.order_w):
                break
            wall = self.order_w[self.counter_w]
            self.counter_w += 1
            drawn.add(wall)
        self.view.walls_drawn = drawn
        return False

    def tick_create_cells(self) -> bool:
        """Animate the process of creating maze cells."""
        if self.counter >= len(self.order):
            return True
        batch = max(1, len(self.order) // self.batch_div)
        created = set(self.view.created)
        for _ in range(batch):
            if self.counter >= len(self.order):
                break
            cell = self.order[self.counter]
            self.counter += 1
            created.add(cell)
        self.view.created = created
        return False

    def tick_add_42(self) -> bool:
        """Add the '42' pattern to the maze visualization if space allows."""
        if self.view.width_cells < 10 or self.view.height_cells < 10:
            msg_42 = self.query_one("#pattern-42-err", Static)
            msg_42.update("Not enough space for 42 pattern")
            return True
        mid_x = self.view.width_cells // 2
        mid_y = self.view.height_cells // 2
        self.view.cells_42 = set([
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
        ])
        return True
