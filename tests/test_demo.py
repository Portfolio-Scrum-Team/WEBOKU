"""Tests for RIC-09 deterministic complete-game demonstration."""

from weboku.demo import DEMO_SOLUTION, create_demo_game, run_demo


def test_demo_solution_is_valid():
    """The demonstration puzzle must be a valid completed Sudoku."""

    assert len(DEMO_SOLUTION) == 9
    assert all(len(row) == 9 for row in DEMO_SOLUTION)

    expected = set(range(1, 10))

    # Every floor contains 1-9.
    for row in DEMO_SOLUTION:
        assert set(row) == expected

    # Every column contains 1-9.
    for column in range(9):
        assert {
            DEMO_SOLUTION[row][column]
            for row in range(9)
        } == expected

    # Every 3x3 region contains 1-9.
    for region_row in range(3):
        for region_column in range(3):
            values = {
                DEMO_SOLUTION[row][column]
                for row in range(region_row * 3, region_row * 3 + 3)
                for column in range(
                    region_column * 3,
                    region_column * 3 + 3,
                )
            }

            assert values == expected


def test_demo_game_uses_real_engine():
    """The demo must construct the real Weboku engine."""

    game = create_demo_game()

    assert game.board is not None
    assert game.sudoku_engine is not None
    assert game.climber is not None
    assert game.scoring is not None
    assert game.timer is not None


def test_demo_game_starts_through_game_engine():
    """Starting the demo game must use Game.start()."""

    game = create_demo_game()

    state = game.start()

    assert state.game_status == "PLAYING"
    assert "Game started." in game.get_recent_events()


def test_demo_accepts_real_valid_sudoku_move():
    """A demo move must pass through Game.process_move()."""

    game = create_demo_game()
    game.start()

    value = DEMO_SOLUTION[0][0]
    symbol = game.value_to_symbol(value)

    result = game.process_move(1, 1, symbol)

    assert result.success is True
    assert result.value == value
    assert result.symbol == symbol
    assert game.board.get_value(1, 1) == value


def test_demo_timeout_uses_real_princess_life_rule():
    """A timeout must use the real Game.handle_timeout() behavior."""

    game = create_demo_game()
    game.start()

    assert game.princess_life == 27
    assert game.failed_timeouts == 0

    continues = game.handle_timeout()

    assert continues is True
    assert game.failed_timeouts == 1
    assert game.princess_life == 26


def test_demo_reaches_victory():
    """The complete deterministic demonstration must reach victory."""

    output = []

    game = run_demo(output.append)

    text = "\n".join(output)

    assert game.completed_objectives == 27
    assert len(game.completed_rings) == 9
    assert len(game.completed_columns) == 9
    assert len(game.completed_regions) == 9

    assert game.is_victory()

    assert "27/27 OBJECTIVES COMPLETE" in text
    assert "CLIMBER REACHED THE PRINCESS" in text
    assert "VICTORY!" in text
    assert "MARRIAGE COMPLETE." in text


def test_demo_is_deterministic():
    """Two demo runs must produce the same authoritative final state."""

    output_one = []
    output_two = []

    game_one = run_demo(output_one.append)
    game_two = run_demo(output_two.append)

    assert game_one.completed_objectives == game_two.completed_objectives
    assert game_one.completed_rings == game_two.completed_rings
    assert game_one.completed_columns == game_two.completed_columns
    assert game_one.completed_regions == game_two.completed_regions
    assert game_one.score == game_two.score
    assert game_one.princess_life == game_two.princess_life
    assert game_one.failed_timeouts == game_two.failed_timeouts
    assert game_one.game_status == game_two.game_status
    assert game_one.current_position == game_two.current_position

    assert output_one == output_two
