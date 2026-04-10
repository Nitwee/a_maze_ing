class Wall():
    """Wall Class, is marked with booleans: border and open"""
    def __init__(self, border: bool) -> None:
        """border identifies the wall as an edge, open is passable / not"""
        self.border: bool = border
        self.open: bool = False
