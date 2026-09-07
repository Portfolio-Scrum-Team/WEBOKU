from __future__ import annotations


class Cell:
    def __init__(
        self,
        floor: int,
        column: int,
        value: int | None = None,
        given: bool = False,
        locked: bool = False,
    ) -> None:
        if not 1 <= floor <= 9:
            raise ValueError("Floor must be between 1 and 9.")
        if not 1 <= column <= 9:
            raise ValueError("Column must be between 1 and 9.")
        if value is not None and not 1 <= value <= 9:
            raise ValueError("Cell value must be between 1 and 9.")
        self.floor = floor
        self.column = column
        self.value = value
        self.given = given
        self.locked = locked

    @property
    def is_empty(self) -> bool:
        return self.value is None

    @property
    def is_editable(self) -> bool:
        return not self.given and not self.locked

    def set_value(self, value: int) -> bool:
        if not self.is_editable or not 1 <= value <= 9:
            return False
        self.value = value
        return True

    def clear(self) -> bool:
        if not self.is_editable:
            return False
        self.value = None
        return True

    def lock(self) -> None:
        self.locked = True

    def __repr__(self) -> str:
        return (
            f"Cell(floor={self.floor}, column={self.column}, "
            f"value={self.value}, given={self.given}, locked={self.locked})"
        )
