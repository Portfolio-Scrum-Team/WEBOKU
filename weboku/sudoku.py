from __future__ import annotations

from .board import Board


class SudokuEngine:
    def __init__(self, board: Board | None = None) -> None:
        self.board = board if board is not None else Board()

    def validate_move(self, floor: int, column: int, value: int) -> bool:
        if not self._valid_position(floor, column):
            return False
        if not 1 <= value <= 9:
            return False

        cell = self.board.get_cell(floor, column)
        if not cell.is_editable:
            return False

        floor_values = self.board.get_floor(floor)
        column_values = self.board.get_column(column)
        region = self.board.region_for(floor, column)
        region_values = self.board.get_region(region)

        floor_values[column - 1] = None
        column_values[floor - 1] = None
        region_index = ((floor - 1) % 3) * 3 + ((column - 1) % 3)
        region_values[region_index] = None

        return (
            value not in floor_values
            and value not in column_values
            and value not in region_values
        )

    def place_value(self, floor: int, column: int, value: int) -> bool:
        if not self.validate_move(floor, column, value):
            return False
        return self.board.set_value(floor, column, value)

    def candidates(self, floor: int, column: int) -> set[int]:
        if not self._valid_position(floor, column):
            return set()
        if not self.board.get_cell(floor, column).is_editable:
            return set()

        used = {
            value
            for value in (
                self.board.get_floor(floor)
                + self.board.get_column(column)
                + self.board.get_region(self.board.region_for(floor, column))
            )
            if value is not None
        }
        return set(range(1, 10)) - used

    get_candidates = candidates

    def completed_floors(self) -> set[int]:
        return self.board.completed_floors()

    def completed_columns(self) -> set[int]:
        return self.board.completed_columns()

    def completed_regions(self) -> set[int]:
        return self.board.completed_regions()

    def is_complete(self) -> bool:
        return (
            all(self.board.is_floor_complete(floor) for floor in range(1, 10))
            and all(self.board.is_column_complete(column) for column in range(1, 10))
            and all(self.board.is_region_complete(region) for region in range(1, 10))
        )

    def solve(self) -> bool:
        """Solve the current board in place with deterministic backtracking.

        Existing values are treated as fixed for the solve attempt. A successful
        call leaves the solved values on the board. An invalid or unsolvable board
        returns ``False`` with its original values unchanged.
        """
        if not self._has_valid_state():
            return False
        return self._solve()

    def lock_completed_floor(self, floor: int) -> bool:
        if not self.board.is_floor_complete(floor):
            return False
        self.board.lock_floor(floor)
        return True

    def lock_completed_column(self, column: int) -> bool:
        if not self.board.is_column_complete(column):
            return False
        self.board.lock_column(column)
        return True

    def lock_completed_region(self, region: int) -> bool:
        if not self.board.is_region_complete(region):
            return False
        self.board.lock_region(region)
        return True

    def _solve(self) -> bool:
        next_cell = self._select_unsolved_cell()
        if next_cell is None:
            return self.is_complete()

        floor, column, candidates = next_cell
        for value in candidates:
            if not self.place_value(floor, column, value):
                continue
            if self._solve():
                return True
            self.board.clear_value(floor, column)

        return False

    def _select_unsolved_cell(self) -> tuple[int, int, list[int]] | None:
        selected: tuple[int, int, list[int]] | None = None

        for floor in range(1, 10):
            for column in range(1, 10):
                if not self.board.get_cell(floor, column).is_empty:
                    continue

                candidates = sorted(self.candidates(floor, column))
                if not candidates:
                    return floor, column, candidates
                if selected is None or len(candidates) < len(selected[2]):
                    selected = floor, column, candidates

        return selected

    def _has_valid_state(self) -> bool:
        units = (
            [self.board.get_floor(floor) for floor in range(1, 10)]
            + [self.board.get_column(column) for column in range(1, 10)]
            + [self.board.get_region(region) for region in range(1, 10)]
        )
        return all(self._has_no_duplicates(unit) for unit in units)

    @staticmethod
    def _has_no_duplicates(values: list[int | None]) -> bool:
        present_values = [value for value in values if value is not None]
        return len(present_values) == len(set(present_values))

    @staticmethod
    def _valid_position(floor: int, column: int) -> bool:
        return (
            isinstance(floor, int)
            and isinstance(column, int)
            and 1 <= floor <= 9
            and 1 <= column <= 9
        )
