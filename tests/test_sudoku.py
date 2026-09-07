import pytest

from weboku.board import Board
from weboku.cell import Cell
from weboku.sudoku import SudokuEngine


SOLVED_BOARD = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]


def test_board_has_nine_floors_and_eighty_one_cells() -> None:
    board = Board()

    assert Board.SIZE == 9
    assert len(board.cells) == 9
    assert all(len(floor) == 9 for floor in board.cells)
    assert sum(len(floor) for floor in board.cells) == 81


def test_cells_use_one_based_coordinates() -> None:
    board = Board()

    assert (board.get_cell(1, 1).floor, board.get_cell(1, 1).column) == (1, 1)
    assert (board.get_cell(9, 9).floor, board.get_cell(9, 9).column) == (9, 9)

    for floor, column in ((0, 1), (10, 1), (1, 0), (1, 10)):
        with pytest.raises(ValueError):
            board.get_cell(floor, column)


@pytest.mark.parametrize(
    ("floor", "column", "region"),
    [
        (1, 1, 1),
        (1, 4, 2),
        (1, 7, 3),
        (4, 1, 4),
        (4, 4, 5),
        (4, 7, 6),
        (7, 1, 7),
        (7, 4, 8),
        (7, 7, 9),
    ],
)
def test_all_nine_region_mappings(floor: int, column: int, region: int) -> None:
    assert Board.region_for(floor, column) == region
    assert Board.region_for(floor + 2, column + 2) == region


def test_get_region_returns_its_three_by_three_cells_in_floor_order() -> None:
    board = Board(SOLVED_BOARD)

    assert board.get_region(1) == [5, 3, 4, 6, 7, 2, 1, 9, 8]
    assert board.get_region(5) == [7, 6, 1, 8, 5, 3, 9, 2, 4]
    assert board.get_region(9) == [2, 8, 4, 6, 3, 5, 1, 7, 9]


def test_engine_places_a_valid_move() -> None:
    engine = SudokuEngine()

    assert engine.validate_move(1, 1, 5)
    assert engine.place_value(1, 1, 5)
    assert engine.board.get_value(1, 1) == 5


def test_engine_rejects_duplicate_floor_value() -> None:
    engine = SudokuEngine()
    engine.board.set_value(1, 1, 5)

    assert not engine.validate_move(1, 9, 5)
    assert not engine.place_value(1, 9, 5)


def test_engine_rejects_duplicate_column_value() -> None:
    engine = SudokuEngine()
    engine.board.set_value(1, 1, 5)

    assert not engine.validate_move(9, 1, 5)
    assert not engine.place_value(9, 1, 5)


def test_engine_rejects_duplicate_region_value() -> None:
    engine = SudokuEngine()
    engine.board.set_value(1, 1, 5)

    assert not engine.validate_move(3, 3, 5)
    assert not engine.place_value(3, 3, 5)


def test_replacing_an_editable_cells_current_value_is_valid() -> None:
    engine = SudokuEngine()
    engine.board.set_value(5, 5, 5)

    assert engine.validate_move(5, 5, 5)


def test_candidates_exclude_floor_column_and_region_values() -> None:
    values = [[None for _ in range(9)] for _ in range(9)]
    values[4][0] = 1
    values[0][4] = 2
    values[4][3] = 3
    values[3][3] = 4
    engine = SudokuEngine(Board(values))

    assert engine.candidates(5, 5) == {5, 6, 7, 8, 9}
    assert engine.get_candidates(5, 5) == {5, 6, 7, 8, 9}


def test_loaded_values_are_givens_and_cannot_be_changed() -> None:
    values = [[None for _ in range(9)] for _ in range(9)]
    values[0][0] = 5
    board = Board(values)
    engine = SudokuEngine(board)

    assert board.get_cell(1, 1).given
    assert not board.get_cell(1, 1).is_editable
    assert not engine.place_value(1, 1, 4)
    assert not board.clear_value(1, 1)
    assert engine.candidates(1, 1) == set()


def test_completed_floor_column_and_region_are_detected() -> None:
    board = Board()
    for index, value in enumerate(range(1, 10), 1):
        board.set_value(1, index, value)
    for floor, value in enumerate([9, 1, 2, 3, 4, 5, 6, 7, 8], 1):
        board.set_value(floor, 9, value)
    region_values = iter(range(1, 10))
    for floor in range(4, 7):
        for column in range(4, 7):
            board.set_value(floor, column, next(region_values))

    assert board.is_floor_complete(1)
    assert board.is_column_complete(9)
    assert board.is_region_complete(5)
    assert board.completed_floors() == {1}
    assert board.completed_columns() == {9}
    assert board.completed_regions() == {5}


def test_complete_and_incomplete_sudoku() -> None:
    engine = SudokuEngine(Board(SOLVED_BOARD))

    assert engine.is_complete()
    engine.board.get_cell(9, 9).given = False
    assert engine.board.clear_value(9, 9)
    assert not engine.is_complete()


def test_cell_and_completed_objective_locking() -> None:
    board = Board()
    cell = board.get_cell(9, 9)
    cell.lock()

    assert cell.locked
    assert not cell.is_editable
    assert not cell.set_value(1)
    assert not cell.clear()

    for column, value in enumerate(range(1, 10), 1):
        board.set_value(1, column, value)
    engine = SudokuEngine(board)

    assert engine.lock_completed_floor(1)
    assert all(board.get_cell(1, column).locked for column in range(1, 10))
    assert not engine.lock_completed_floor(2)


def test_completed_column_and_region_locking() -> None:
    column_board = Board()
    for floor, value in enumerate(range(1, 10), 1):
        column_board.set_value(floor, 1, value)
    column_engine = SudokuEngine(column_board)

    assert column_engine.lock_completed_column(1)
    assert all(column_board.get_cell(floor, 1).locked for floor in range(1, 10))
    assert not column_engine.lock_completed_column(2)

    region_board = Board()
    values = iter(range(1, 10))
    for floor in range(1, 4):
        for column in range(1, 4):
            region_board.set_value(floor, column, next(values))
    region_engine = SudokuEngine(region_board)

    assert region_engine.lock_completed_region(1)
    assert all(
        region_board.get_cell(floor, column).locked
        for floor in range(1, 4)
        for column in range(1, 4)
    )
    assert not region_engine.lock_completed_region(2)


def test_board_rejects_wrong_shape_and_invalid_values() -> None:
    with pytest.raises(ValueError, match="9x9"):
        Board([[None] * 9 for _ in range(8)])
    with pytest.raises(ValueError, match="1-9"):
        Board([[10] + [None] * 8] + [[None] * 9 for _ in range(8)])


def test_cell_rejects_invalid_coordinates_and_value() -> None:
    with pytest.raises(ValueError):
        Cell(0, 1)
    with pytest.raises(ValueError):
        Cell(1, 10)
    with pytest.raises(ValueError):
        Cell(1, 1, 0)


def test_invalid_move_coordinates_and_values_are_rejected() -> None:
    engine = SudokuEngine()

    assert not engine.validate_move(0, 1, 1)
    assert not engine.validate_move(1, 10, 1)
    assert not engine.validate_move(1, 1, 0)
    assert not engine.validate_move(1, 1, 10)
    assert engine.candidates(0, 1) == set()
