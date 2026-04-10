*This project has been created as part of the 42 curriculum by qrios and lumarcuc*

# Description

### Requirements

This project requires the **creation**, **solving** and **simple display** of mazes, with a preset number of parameters found in a configuration file that are further discussed [here](#config-file-requirements).

Additionally, the programm outputs a *maze.txt* file that represents the maze in a specific way described [here](#output-file-structure).

Lastly, the maze generation has to follow a set or very specific rules detailed [here](#maze-rules).
### Our approach

- Parsing data
    > Firstly, we check that all mandatory keys are present and that, if any additional keys are present, they actually match existing keys that we use to get data from.
    >
    > If any of these checks return an error, the programm never starts and the user will be prompted to make sure that the configuration file is properly set up.
    > 
    > To parse data from the configuration file, we chose to use the [***Pydantic***](https://docs.pydantic.dev/latest/concepts/models/ "BaseModel, model_validator, ValidationError") library, which offers a `BaseModel` class that makes it very intuitive and simple to convert strings to necessary data types, as well as offering really comprehensive error handling.
    >
    > Once properly formatted (or rejected), the values are then stored and the program starts working and creates the maze.

- Creating the maze

    > We decided to use **objects** to make it simple to code algorithms and calculate available moves. The maze is made of a dictionary of **Cells**, which are each attributed a **Wall** in each direction. 
    > 
    > The data is represented as a dictionnary of **[coordinates(x, y)]** mapping to these **Cells**. 
    >
    > Once every Cell is created and their Walls attributed, a [**generative algorithm**](#creation) is called (either its one specified, or chosen at random). 
    >
    > That algorithm will then break walls following a set of [rules](#maze-rules) until every cell has been visited.
    >
    > If it did not succeed, it will retry with the same parameters and if the maze is not **perfect**, it will then break additionnal walls, creating new paths to the exit.
- Solving the maze
    > Using the created dictionary of Cells, a [**solver algorithm**](#solving) is called (either its one specified, or chosen at random).
    >
    > This execution will output some useful information such as: **visited** Cells, **paths** explored and the **solution** found.
    >
    > This step also renders the human readable solution.
- Rendering the maze
    > We used Textual and Rich libraries for maze visualization.
    > There is:
        an App that will handle the global visualization (buttons, stats, config, styles and more). We used Textual reactive variables to keep track of changes and animate the maze.
        A widget that will handle the actual maze design and animation. We used the Render_line method with Rich Segments to print the maze line by line.
        A style.css file that handles the global visualization style. Cells, walls and paths are done using the Rich Style object.

    > The visualizer has 6 animated steps:

        Generating cells
        Adding walls
        Adding the 42 sign (if maze is big enough)
        Opening walls according to the selected generative algorithm
        Finding the solution according to the selected solver algorithm 
        Printing the path to exit

    > Animation speed is set using 2 factors: tick (default 0.1s) that will run the tick method on this interval, and batch (default 20) that is equal to the number of operations simultaneously done.

    > It also has the following possible actions:

        Change config and restart (top right box)
        Regenerate maze (restart the animations)
        Change maze colors
        Change speed (this will modify the number of operations simultaneously done by changing the batch factor)
        Show/Hide path: this will restart animations to the step 5
        Pause: this is using the builtin textual pause and resume methods

---
# Instructions
#### A number of `make` commands are at your disposal:
- `make venv` will create a *virtual environment* named **.venv**
    - you will then have to execute `source /.venv/bin/activate` to connect to that newly created venv
- `make install` will install the package dependencies of the project
- `make run` will run the programm with **config.txt** as argument
- `make debug` will run the programm in **debug mode** (without any argument)
    - in debug mode, run `run config.txt` to set **config.txt** as the argument of the programm, then run `continue` to actually execute it
- `make lint` will run [flake8](https://flake8.pycqa.org/en/latest/ "so that was it") and [mypy](https://mypy.readthedocs.io/en/stable/ "--warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs") for type checking.
- `make lint-strict` will run the same as above, but with no flag except **--strict**, which catches way more errors.
- `make clean` removes all **temporary** files
- `make package` is non necessary for testing purposes; its a demonstration on how to install the **.whl** package and get the [**MazeGenerator**](#code-reusability "part of the code reusability") class as a **pip install**.

#### Running a_maze_ing
1. Make sure that you are in a venv or in your main python interpreter with all dependencies installed.

2. Run `python3 a_maze_ing.py config.txt` or `make run`.

3. Inside the viewing window, you can:

    - Press `q` to **quit**.
    - Press `spacebar` to **play/pause** the display.
    - Press `r` to regenerate the maze with the same configuration.
    - Press `c` to change **all** the colours of the maze elements.
    - Press `p` to **show/hide** the path to the exit.
    - Press `+` or `-` to increase/decrease the speed of the animations.
    
> note that you can also mouse over the elements on the UI and click on them

4. To create a different maze, simply change the **values** of the parameters in the [configuration file](#config-file-requirements) passed as a parameter and run these steps again.

    You can also directly click on the values in the upper part of the UI and enter the desired **values**, then click on `save & restart` to reload a maze and save the parameters in a **config.txt** file.

# Resources

- algorithms:

    >[recursive backtracking](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)
    >
    >[all about mazes](https://professor-l.github.io/mazes/)
    >
    >[A* material](https://wiki.zahno.dev/days-of-algo/content/notebooks/011-maze-solver-astar.html)
    >
    >[more A*](https://levelup.gitconnected.com/a-star-a-search-for-solving-a-maze-using-python-with-visualization-b0cae1c3ba92)
    >
    >[algorithm ideas and visual representations](https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap)
    >
    >[some mazes](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
    >
    >[prim](https://weblog.jamisbuck.org/2011/1/10/maze-generation-prim-s-algorithm)
    >
    >[more prim](https://cantwell-tom.medium.com/prims-algorithm-as-a-maze-in-javascript-aec7415ad2cd)
    

- parsing and documentation:

    >[seeding info](https://www.geeksforgeeks.org/python/random-seed-in-python/)
    > 
    >[pydantic validators](https://docs.pydantic.dev/latest/concepts/validators)
    >
    >[textual timer](https://textual.textualize.io/api/timer/)
    >
    >[textual reactive](https://textual.textualize.io/guide/reactivity/)
    >
    >[textual widgets](https://textual.textualize.io/guide/widgets/)
    >
    >[rich segments](https://rich.readthedocs.io/en/stable/reference/segment.html)
    >
    >[rich styles](https://rich.readthedocs.io/en/latest/style.html)
    >
    >[textual inputs](https://textual.textualize.io/guide/input/)
    >
    > [textual buttons](https://textual.textualize.io/widgets/button/)

# Additional information

#### Maze rules
- the maze has to include the 42 logo in a different colour as impassable tiles if size permits it, else still render the maze but display a message
- minimum height and width is 2, maximum is 100 (arbitrary rules)
- entry and exit cannot be placed in the 42 logo (which is centered)
- exit and entry cannot be on the same coordinates
- exit and entry cannot be placed out of bounds
- the maze has to show the path to the exit, with an option to turn off the display
- the maze has to output a file named [**maze.txt**](#output-file-structure)
- the maze **CANNOT** contain 3 * 3 open cells areas
- **outside walls** cannot be broken

#### Config file requirements

###### Mandatory keys
 
- WIDTH=`int`
- HEIGHT=`int`
- ENTRY=`(int, int)`
- EXIT=`(int, int)`
- OUTPUT_FILE=`string`
- PERFECT=`bool`

###### Optional Keys
- SEED=`int` or `None`
- GENERATIVE_ALGORITHM=`Prim`, `Backtracking` or `None`
- SOLVER_ALGORITHM=`BFS`, `A*` or `None`

> note that keys are not case sensitive but values are
>
> optional keys **CAN** be present, but will default to `None` if unspecified
>
> if any key is present however, value has to follow KEY=VALUE format and the value **HAS** to be correct or an error will be raised

#### Output file structure
1. contains a hexadecimal maze representation, where each number from 0 (all walls open) up to F (all walls closed) represents a cell of the maze and the status of its walls
2. contains the entry and start coordinates
3. Contains a NSWE character sequence that indicates the path to take from start to exit

#### Our algorithms
###### Creation
- Prim: Prim’s algorithm generates a maze by progressively growing a spanning tree from a starting cell. The algorithm begins at the maze entry and marks it as visited, then adds all adjacent walls to a frontier list. At each step, it randomly selects a wall from this frontier. If the wall separates a visited cell from an unvisited one, the wall is removed, the new cell becomes part of the maze, and its neighbouring walls are added to the frontier. This process continues until all reachable cells have been visited, producing a connected maze with no isolated regions

- Recursive Backtracking: simple backtracking algorithm. starts from the **entry** coordinates, and calls itself on neighbours in each **randomized** directions if the neighbour has not yet been visited and if conditions are met (notably, that the wall is breakable). it will then break that wall that links both cells, and hop into the cell, and repeat until all directions of all cells have been visited

###### Solving

- BFS: classic maze solving algorithm. looks at one **cell**, store it in a **visited** closed list gets their **reachable neighbours** and stores them in a **queue** [(**FIFO**)](https://en.wikipedia.org/wiki/FIFO) if not yet visited. stores the **path** taken from cell to cell and proceeds so until *exit* has been reached or *queue* is empty (no exit possible).

- A*: remastering of the same principles, but the concept of a **priority queue**. code execution is exactly the same, but algorithm does not use **FIFO** for storage in queue. instead, a **heuristic** is used to calculate the **cost** of a cell, being `f(n) = g(n) + h(n)`, where `n` is a **cell**, `f` is the **total cost**, `g` is the **distance** between the **starting cell** and the **current** one and `h` is the **absolute distance** between the **current** cell and the **exit** position. for cells in queue, the **least costly** (following this method of cost calculating) is always choosen next.  

#### Code reusability

- The entire module is reusable and de-constructable. If you import **MazeGenerator** but want to change the parsing values to allow for more / less, you can hop into *validator/maze_validator.py* and change the rules there.
- If what you need is a change in how the pathfinding is done, simply check / replace the *pathfinder/pathfinder.py* module
- The Generator class used in MazeGenerator can be found in *generator/generator.py*
- Finally, the whole visualization is done through **Textual** in *visualize/maze_visualizer.py*.
- If you go into the MazeGenerator class, you can see that there are no arguments to pass. The only thing you have to do is instanciate a MazeGenerator object, and it will (in `self.init`) parse and recuperate data in the file passed as argument.
- If you don't want it to go to work straight away, you can simply remove `self.process_all()` in the init and then call it later yourself.
- That method is also highly customizable, as you can then change algorithms used / what is used for visualization.
- A basic example would be:
> `import mazegen` in your file
>
> declare `maze = mazegen.MazeGenerator()` in your file
>
> [change settings](#config-file-requirements "How to change values") in a config.txt file
>
> call `python3 'your_file.py' config.txt`
>
> the custom parameters will be passed through the confix.txt file
>
> you can also pass fixed parameters directly in the object variables themselves
>
> you could code `maze.data.seed = 'my_seed'` and that would also be fine
>
> to access the solution, you can retrieve the **SolverPaths** at `maze.solver_paths` which will be filled to the brim after pathfinding as been done
>
> this data structure contains:
>    - visited cells by the algo
>    - all paths taken leading to each cell visited
>    - all cells stored in queue
>    - the NSEW path to the exit
>
> if tou want to isolate the path to exit but not in string, the method `convert_path` in *pathfinder/pathinfder.py* is what you are looking for
>
> the most important data object is `maze.cells` which contains a dictionary of coordinates (x, y) mapping to each **Cell** object.

#### Our journey through the project
- lumarcuc:
    - at first I was kinda scared since **qrios** had finished the python piscine way before I did. He structured the project a lot and got a simple ASCII visu working + Prim + BFS.
    - I then hopped on the train and we decided together how we were gonna handle visualization. We ultimately chose Textual as **qrios** was familiar with the CSS rendering  style.
    - It was then my turn to code algos. I got the recursive backtracking and A* working pretty fast while **qrios** still hammered on visualization.
    - I chose recursive to work on the generation because I really liked how it looked visually. As for A*, I know its a complex algo that is used by big tech companies (like Google for maps) so I wanted to learn it.
    - One great hurdle was what values we needed to pass after pathfinding to actually render them in Textual. Once we got that working, everything clicked and was actually fun to code.
    - The rest of the project on my side was catching up to how **qrios** was coding the visualization, doing some refactoring and making the project glue together (I did code the 4 regenerate instructions though !).
    - I did handle mypy and most of the norm, while **qrios** kept shipping great Textual tools and we exchanged on what feature we wanted to implement and how we wanted to do it.
- qrios:
    - I started by thinking about how a maze is created and which structure could be the best. I thought about creating cells objects and walls objects so both are related and we could know who is who. Also, it was easier so cells could easily share a wall in common.
    - Then I learned about generative algorithms, and i picked Prim because I liked the way it creates multiple branches at the same time. Then I created a first very basic ASCII printer to see if everything was going as expected. 
    - I created a simple BFS backtracking solver algorithm to solve the maze. This part was pretty fast.
    - I then started thinking about visualization. I felt limited by basic ascii rendering so I wanted to use a library. After hesitating between Curse and Textual, I decided to pick Textual since it seems more modern and had a very good documentation
    - Our plan was to animate every step so we could see the whole process of creating the maze. However, Textual was really hard to handle at first. I took me many days before I could simply animate the cells generation. I tried creating multiple widgets for cells, walls etc like in the generator but it was way too resource consuming... So I changed. Then I used inline rich markup for colors but once again, too consuming. Then I discovered the render_line method and it was better but very slow, except by putting the timer rate to 0.001 but again, too consuming. I created a batch method that would do operations in batch, and it was finally working. From this point, its been much better to work with Textual because we had a solid base. I added the steps one by one.
    - We kept going, Luka was handling a lot on his site by reorganising the code in a more structured way, fixing bugs and many other things, on my side I added features one after another on the visualizer, and got the result you see here.

#### AI usage

- mypy error handling, comprehension for making it work with pydantic notably
- understanding the textual / rich libraries at first
