from __future__ import annotations

from typing import Iterable

from .cell import Cell


class Board:
    SIZE = 9

    def __init__(self, values: Iterable[Iterable[int | None]] | None = None) -> None:
        self.cells = [
            [Cell(floor, column) for column in range(1, 10)]
            for floor in range(1, 10)
        ]
        if values is not None:
            self.load_values(values)

    def get_cell(self, floor: int, column: int) -> Cell:
        self._validate_position(floor, column)
        return self.cells[floor - 1][column - 1]

    def get_value(self, floor: int, column: int) -> int | None:
        return self.get_cell(floor, column).value

    def set_value(self, floor: int, column: int, value: int) -> bool:
        return self.get_cell(floor, column).set_value(value)

    def clear_value(self, floor: int, column: int) -> bool:
        return self.get_cell(floor, column).clear()

    def lock_cell(self, floor: int, column: int) -> None:
        self.get_cell(floor, column).lock()

    def get_floor(self, floor: int) -> list[int | None]:
        if not 1 <= floor <= 9:
            raise ValueError("Floor must be between 1 and 9.")
        return [self.cells[floor - 1][column - 1].value for column in range(1, 10)]

    def get_column(self, column: int) -> list[int | None]:
        if not 1 <= column <= 9:
            raise ValueError("Column must be between 1 and 9.")
        return [self.cells[floor - 1][column - 1].value for floor in range(1, 10)]

    def get_region(self, region: int) -> list[int | None]:
        if not 1 <= region <= 9:
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
        if not 1 <= floor <= 9 or not 1 <= column <= 9:
            raise ValueError("Floor and column must be between 1 and 9.")
        return ((floor - 1) // 3) * 3 + ((column - 1) // 3) + 1

    def is_floor_complete(self, floor: int) -> bool:
        return self._is_complete_unit(self.get_floor(floor))

    def is_column_complete(self, column: int) -> bool:
        return self._is_complete_unit(self.get_column(column))

    def is_region_complete(self, region: int) -> bool:
        return self._is_complete_unit(self.get_region(region))

    def completed_floors(self) -> set[int]:
        return {floor for floor in range(1, 10) if self.is_floor_complete(floor)}

    def completed_columns(self) -> set[int]:
        return {column for column in range(1, 10) if self.is_column_complete(column)}

    def completed_regions(self) -> set[int]:
        return {region for region in range(1, 10) if self.is_region_complete(region)}

    def lock_floor(self, floor: int) -> None:
        for column in range(1, 10):
            self.lock_cell(floor, column)

    def lock_column(self, column: int) -> None:
        for floor in range(1, 10):
            self.lock_cell(floor, column)

    def lock_region(self, region: int) -> None:
        if not 1 <= region <= 9:
            raise ValueError("Region must be between 1 and 9.")
        region_row = (region - 1) // 3
        region_column = (region - 1) % 3
        start_floor = region_row * 3 + 1
        start_column = region_column * 3 + 1
        for floor in range(start_floor, start_floor + 3):
            for column in range(start_column, start_column + 3):
                self.lock_cell(floor, column)

    def load_values(self, values: Iterable[Iterable[int | None]]) -> None:
        rows = [list(row) for row in values]
        if len(rows) != 9 or any(len(row) != 9 for row in rows):
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
        return [
            [self.get_value(floor, column) for column in range(1, 10)]
            for floor in range(1, 10)
        ]

    @staticmethod
    def _is_complete_unit(values: list[int | None]) -> bool:
        return (
            len(values) == 9
            and all(value is not None for value in values)
            and set(values) == set(range(1, 10))
        )

    @staticmethod
    def _validate_position(floor: int, column: int) -> None:
        if not 1 <= floor <= 9:
            raise ValueError("Floor must be between 1 and 9.")
        if not 1 <= column <= 9:
            raise ValueError("Column must be between 1 and 9.")
