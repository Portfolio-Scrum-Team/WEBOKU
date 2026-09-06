"""Tests for the Weboku automatic movement algorithm."""

from weboku.game import Game


def make_game():
    """Create a Game instance without requiring team modules."""
    return Game()


def test_column_completion_without_ring_does_not_move_climber():
    game = make_game()

    game.state.current_position = None
    game.state.active_column = None

    moved = game._process_automatic_movement(
        new_rings=[],
        new_columns=[2],
    )

    assert moved is False
    assert game.state.active_column == 2
    assert game.state.current_position is None


def test_ring_completion_uses_active_column():
    game = make_game()

    game.state.current_position = None
    game.state.active_column = 2

    moved = game._process_automatic_movement(
        new_rings=[5],
        new_columns=[],
    )

    assert moved is True
    assert game.state.current_position == (5, 2)


def test_ring_completion_after_column_completion():
    game = make_game()

    game.state.current_position = None

    game._process_automatic_movement(
        new_rings=[],
        new_columns=[2],
    )

    moved = game._process_automatic_movement(
        new_rings=[5],
        new_columns=[],
    )

    assert moved is True
    assert game.state.active_column == 2
    assert game.state.current_position == (5, 2)


def test_new_ring_changes_current_ring():
    game = make_game()

    game.state.current_position = (5, 2)
    game.state.active_column = 2

    moved = game._process_automatic_movement(
        new_rings=[4],
        new_columns=[],
    )

    assert moved is True
    assert game.state.current_position == (4, 2)


def test_new_column_moves_on_current_ring():
    game = make_game()

    game.state.current_position = (4, 2)
    game.state.active_column = 2

    moved = game._process_automatic_movement(
        new_rings=[],
        new_columns=[1],
    )

    assert moved is True
    assert game.state.active_column == 1
    assert game.state.current_position == (4, 1)


def test_new_column_does_not_move_when_no_ring_exists():
    game = make_game()

    game.state.current_position = None
    game.state.active_column = None

    moved = game._process_automatic_movement(
        new_rings=[],
        new_columns=[1],
    )

    assert moved is False
    assert game.state.active_column == 1
    assert game.state.current_position is None


def test_window_completion_does_not_move_climber():
    game = make_game()

    game.state.current_position = (5, 2)
    game.state.active_column = 2

    # Windows/regions are deliberately not passed to the movement
    # method because they do not directly cause movement.
    moved = game._process_automatic_movement(
        new_rings=[],
        new_columns=[],
    )

    assert moved is False
    assert game.state.current_position == (5, 2)
    assert game.state.active_column == 2


def test_latest_completed_column_becomes_active():
    game = make_game()

    game.state.current_position = (5, 2)
    game.state.active_column = 2

    moved = game._process_automatic_movement(
        new_rings=[],
        new_columns=[1, 3],
    )

    assert moved is True
    assert game.state.active_column == 3
    assert game.state.current_position == (5, 3)


def test_ring_uses_latest_completed_ring():
    game = make_game()

    game.state.current_position = (5, 2)
    game.state.active_column = 2

    moved = game._process_automatic_movement(
        new_rings=[4, 3],
        new_columns=[],
    )

    assert moved is True
    assert game.state.current_position == (3, 2)


def test_movement_is_deterministic():
    game_one = make_game()
    game_two = make_game()

    game_one.state.active_column = 2
    game_two.state.active_column = 2

    result_one = game_one._process_automatic_movement(
        new_rings=[5],
        new_columns=[],
    )

    result_two = game_two._process_automatic_movement(
        new_rings=[5],
        new_columns=[],
    )

    assert result_one == result_two
    assert game_one.state.current_position == game_two.state.current_position