try:
    from typing import Any, Tuple, Self
    from pydantic import BaseModel, Field, field_validator, model_validator
except ImportError as e:
    print(e)
    exit(0)


class MazeValidator(BaseModel):
    """
    BaseModel from Pydantic to verify appropriate values for maze running

    width: int[8-100]
    height: int[8-100]
    entry: Tuple[int, int], len = 2
    exit: Tuple[int, int], len = 2
    output_file: str(any)
    perfect: bool
    seed: int | None
    generative_algorithm: str('Prim' or 'Backtracking')
    solver_algorithm: str('BFS' or 'A*')
    """
    width: int = Field(le=100, ge=2)
    height: int = Field(le=100, ge=2)
    entry: Tuple[int, int] = Field(min_length=2, max_length=2)
    solution: Tuple[int, int] = Field(min_length=2, max_length=2, alias='exit')
    output_file: str
    perfect: bool
    seed: int | None = Field(default=None)
    generative_algorithm: str | None = Field(default=None)
    solver_algorithm: str | None = Field(default=None)

    @field_validator('entry', mode='before')
    @classmethod
    def ensure_entry(cls, value: Any) -> Any:
        """raise an error if passed value does not contain ','"""
        value = value.split(',')
        if not isinstance(value, list):
            raise ValueError(f"Expected ',' separated values, got {value}")
        return tuple(value)

    @field_validator('solution', mode='before')
    @classmethod
    def ensure_exit(cls, value: Any) -> Any:
        """raise an error if passed value does not contain ','"""
        value = value.split(',')
        if not isinstance(value, list):
            raise ValueError(f"Expected ',' separated values, got {value}")
        return tuple(value)

    @field_validator('perfect', mode='before')
    @classmethod
    def ensure_bool(cls, value: Any) -> Any:
        """raise an error if value is neither 'False' nor 'True'"""
        if not value == 'True' and not value == 'False':
            raise ValueError(f"Expected 'True' or 'False', got {value}")
        return value

    @field_validator('seed', mode='before')
    @classmethod
    def ensure_none(cls, value: Any) -> Any:
        """value becomes NoneType if passed value is 'None'"""
        if value == "None":
            return None
        return value

    @field_validator('generative_algorithm', mode='before')
    @classmethod
    def ensure_gen_algo(cls, value: Any) -> Any:
        """raise an error if value is not a correct str argument"""
        if value == 'None':
            return None
        args = ['Prim', 'Backtracking']
        if value not in args:
            raise ValueError(f"{value} not in expected algorithm ({args})")
        return value

    @field_validator('solver_algorithm', mode='before')
    @classmethod
    def ensure_solve_algo(cls, value: Any) -> Any:
        """raise an error if value is not a correct str argument"""
        if value == 'None':
            return None
        args = ['BFS', 'A*']
        if value not in args:
            raise ValueError(f"{value} not in expected algorithm ({args})")
        return value

    @model_validator(mode='after')
    def ensure_entry_and_exit(self) -> Self:
        """raise an error if entry/exit are out of bounds"""
        entry_x, entry_y = self.entry
        exit_x, exit_y = self.solution
        if entry_x == exit_x and entry_y == exit_y:
            raise ValueError("Entry and exit cannot be the same")
        if entry_x >= self.width or exit_x >= self.width:
            raise ValueError("Entry or exit cannot be outside of width")
        if entry_y >= self.height or exit_y >= self.height:
            raise ValueError("Entry or exit cannot be outside of height")
        if entry_x < 0 or entry_y < 0 or exit_x < 0 or exit_y < 0:
            raise ValueError("Entry or exit cannot be negaative")
        coords_42 = self.get_42_coords()
        if self.entry in coords_42 or self.solution in coords_42:
            raise ValueError("Entry or exit cannot be in 42 pattern")
        return self

    def get_42_coords(self) -> set[tuple[int, int]]:
        """
        Generate a set of coordinates that form the number "42" pattern
        centered in the maze.
        Returns an empty set if the maze dimensions are too small (< 10x10).
        Returns:
            set[tuple[int, int]]: Coordinates forming the "42" pattern, empty
            if maze is too small.
        """

        if self.width < 10 or self.height < 10:
            return set()

        mid_x = self.width // 2
        mid_y = self.height // 2

        return {
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
        }
