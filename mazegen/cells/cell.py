try:
    from ..walls.wall import Wall
except ImportError as e:
    print(e)
    exit(0)


class Cell():
    """Cell object that represents a node on the grid"""
    def __init__(self, x: int, y: int) -> None:
        """
        Cell object specifiers

        has a wall object on each direction (or None)
        has coordinates (x, y) = int
        has a "visited" boolean flag for parsing
        has a "closed" boolean flag for impassable tiles (for 42 logo)
        """
        self.north: None | Wall = None
        self.south: None | Wall = None
        self.east: None | Wall = None
        self.west: None | Wall = None
        self.x: int = x
        self.y: int = y
        self.coords: tuple[int, int] = (x, y)
        self.visited: bool = False
        self.closed: bool = False
