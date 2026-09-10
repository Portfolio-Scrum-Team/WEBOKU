from __future__ import annotations

from typing import Iterable

from .cell import Cell

# ---------------------------------------------------------------------------
# Weboku fixed development Sudoku
# ---------------------------------------------------------------------------
#
# The board uses normal Sudoku values internally:
#
#     1 2 3 4 5 6 7 8 9
#
# The Renderer converts those values into Weboku symbols for the CLI.
#
# None represents an empty editable cell.
#
# This puzzle has a known valid solution and is intentionally fixed for
# deterministic development and integration.
# ---------------------------------------------------------------------------

DEFAULT_SOLUTION = (
    (5, 3, 4, 6, 7, 8, 9, 1, 2),
    (6, 7, 2, 1, 9, 5, 3, 4, 8),
    (1, 9, 8, 3, 4, 2, 5, 6, 7),
    (8, 5, 9, 7, 6, 1, 4, 2, 3),
    (4, 2, 6, 8, 5, 3, 7, 9, 1),
    (7, 1, 3, 9, 2, 4, 8, 5, 6),
    (9, 6, 1, 5, 3, 7, 2, 8, 4),
    (2, 8, 7, 4, 1, 9, 6, 3, 5),
    (3, 4, 5, 2, 8, 6, 1, 7, 9),
)


DEFAULT_PUZZLE = (
    (5, 3, None, None, 7, None, None, None, None),
    (6, None, None, 1, 9, 5, None, None, None),
    (None, 9, 8, None, None, None, None, 6, None),
    (8, None, None, None, 6, None, None, None, 3),
    (4, None, None, 8, None, 3, None, None, 1),
    (7, None, None, None, 2, None, None, None, 6),
    (None, 6, None, None, None, None, 2, 8, None),
    (None, None, None, 4, 1, 9, None, None, 5),
    (None, None, None, None, 8, None, None, 7, 9),
)


class Board:
    """Represent the 9x9 Weboku Sudoku board."""

    SIZE = 9

    def __init__(
        self,
        values: Iterable[Iterable[int | None]] | None = None,
    ) -> None:
        self.cells = [
            [Cell(floor, column) for column in range(1, 10)] for floor in range(1, 10)
        ]

        if values is not None:
            self.load_values(values)

    @classmethod
    def default_puzzle(cls) -> "Board":
        """Create a fresh board containing the fixed development puzzle."""
        return cls(DEFAULT_PUZZLE)

    @classmethod
    def default_solution(cls) -> tuple[tuple[int, ...], ...]:
        """Return the known solution for the fixed development puzzle."""
        return DEFAULT_SOLUTION

    def get_cell(self, floor: int, column: int) -> Cell:
        """Return the cell at the given 1-based floor and column."""
        self._validate_position(floor, column)
        return self.cells[floor - 1][column - 1]

    def get_value(self, floor: int, column: int) -> int | None:
        """Return the value stored in a cell."""
        return self.get_cell(floor, column).value

    def set_value(self, floor: int, column: int, value: int) -> bool:
        """Set a value if the target cell is editable."""
        return self.get_cell(floor, column).set_value(value)

    def clear_value(self, floor: int, column: int) -> bool:
        """Clear an editable cell."""
        return self.get_cell(floor, column).clear()

    def lock_cell(self, floor: int, column: int) -> None:
        """Lock one cell."""
        self.get_cell(floor, column).lock()

    def get_floor(self, floor: int) -> list[int | None]:
        """Return all nine values on a floor."""
        if not 1 <= floor <= self.SIZE:
            raise ValueError("Floor must be between 1 and 9.")

        return [
            self.cells[floor - 1][column - 1].value
            for column in range(1, self.SIZE + 1)
        ]

    def get_column(self, column: int) -> list[int | None]:
        """Return all nine values in a column."""
        if not 1 <= column <= self.SIZE:
            raise ValueError("Column must be between 1 and 9.")

        return [
            self.cells[floor - 1][column - 1].value for floor in range(1, self.SIZE + 1)
        ]

    def get_region(self, region: int) -> list[int | None]:
        """Return all nine values in a 3x3 Weboku window/region."""
        if not 1 <= region <= self.SIZE:
            raise ValueError("Region must be between 1 and 9.")

        region_row = (region - 1) // 3
        region_column = (region - 1) % 3

        start_floor = region_row * 3 + 1
        start_column = region_column * 3 + 1

        return [
            self.get_value(floor, column)
            for floor in range(start_floor, start_floor + 3)
            for column in range(start_column, start_column + 3)
        ]

    @staticmethod
    def region_for(floor: int, column: int) -> int:
        """Return the 1-based 3x3 region containing a cell."""
        if not 1 <= floor <= 9 or not 1 <= column <= 9:
            raise ValueError("Floor and column must be between 1 and 9.")

        return ((floor - 1) // 3) * 3 + ((column - 1) // 3) + 1

    def is_floor_complete(self, floor: int) -> bool:
        """Return True when a floor contains 1-9 exactly once."""
        return self._is_complete_unit(self.get_floor(floor))

    def is_column_complete(self, column: int) -> bool:
        """Return True when a column contains 1-9 exactly once."""
        return self._is_complete_unit(self.get_column(column))

    def is_region_complete(self, region: int) -> bool:
        """Return True when a region contains 1-9 exactly once."""
        return self._is_complete_unit(self.get_region(region))

    def completed_floors(self) -> set[int]:
        """Return all currently completed floors."""
        return {
            floor for floor in range(1, self.SIZE + 1) if self.is_floor_complete(floor)
        }

    def completed_columns(self) -> set[int]:
        """Return all currently completed columns."""
        return {
            column
            for column in range(1, self.SIZE + 1)
            if self.is_column_complete(column)
        }

    def completed_regions(self) -> set[int]:
        """Return all currently completed regions/windows."""
        return {
            region
            for region in range(1, self.SIZE + 1)
            if self.is_region_complete(region)
        }

    def lock_floor(self, floor: int) -> None:
        """Lock every cell on a completed floor."""
        for column in range(1, self.SIZE + 1):
            self.lock_cell(floor, column)

    def lock_column(self, column: int) -> None:
        """Lock every cell in a completed column."""
        for floor in range(1, self.SIZE + 1):
            self.lock_cell(floor, column)

    def lock_region(self, region: int) -> None:
        """Lock every cell in a completed 3x3 region."""
        if not 1 <= region <= self.SIZE:
            raise ValueError("Region must be between 1 and 9.")

        region_row = (region - 1) // 3
        region_column = (region - 1) % 3

        start_floor = region_row * 3 + 1
        start_column = region_column * 3 + 1

        for floor in range(start_floor, start_floor + 3):
            for column in range(start_column, start_column + 3):
                self.lock_cell(floor, column)

    def load_values(
        self,
        values: Iterable[Iterable[int | None]],
    ) -> None:
        """
        Load a complete 9x9 board.

        Any supplied value becomes a given clue and therefore cannot be
        edited by the player.
        """
        rows = [list(row) for row in values]

        if len(rows) != self.SIZE or any(len(row) != self.SIZE for row in rows):
            raise ValueError("Board must be exactly 9x9.")

        for floor, row in enumerate(rows, 1):
            for column, value in enumerate(row, 1):
                if value is not None and not 1 <= value <= 9:
                    raise ValueError("Board values must be 1-9 or None.")

                cell = self.get_cell(floor, column)

                cell.value = value
                cell.given = value is not None
                cell.locked = False

    def to_values(self) -> list[list[int | None]]:
        """Return the board as a normal 9x9 numeric matrix."""
        return [
            [self.get_value(floor, column) for column in range(1, self.SIZE + 1)]
            for floor in range(1, self.SIZE + 1)
        ]

    @staticmethod
    def _is_complete_unit(values: list[int | None]) -> bool:
        """Return True when a Sudoku unit contains 1-9 exactly once."""
        return (
            len(values) == 9
            and all(value is not None for value in values)
            and set(values) == set(range(1, 10))
        )

    @staticmethod
    def _validate_position(floor: int, column: int) -> None:
        """Validate a 1-based floor/column coordinate."""
        if not 1 <= floor <= 9:
            raise ValueError("Floor must be between 1 and 9.")

        if not 1 <= column <= 9:
            raise ValueError("Column must be between 1 and 9.")
