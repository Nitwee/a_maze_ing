try:
    from typing import Dict, Set, Tuple
    from dataclasses import dataclass
except ImportError as e:
    print(e)
    exit(0)


@dataclass
class SolverPaths:
    """
    SolverPaths dataClass

    used to store data after parsing through a PathFinder algorithm
    visited: a set of coordinates of visited cells
    paths: a dict of {coordinates: coordinates} of all links between cells
    solution: a dict of {coordinateds: coordinates} of links between
    start and exit
    inputs_to_exit: a str (NSEW) with directions from start to exit
    """
    visited: Set[Tuple[int, int]]
    paths: Dict[Tuple[int, int], Tuple[int, int]]
    solution: Dict[Tuple[int, int], Tuple[int, int]]
    inputs_to_exit: str
