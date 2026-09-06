"""Tests for the Weboku Game/Application coordinator."""

from weboku.game import (
    GAME_STATUS_GAME_OVER,
    GAME_STATUS_PLAYING,
    GAME_STATUS_READY,
    GAME_STATUS_VICTORY,
    MAX_OBJECTIVES,
    MAX_PRINCESS_LIFE,
    Game,
)


class FakeSudokuEngine:
    """Small fake Sudoku engine used to test Game coordination."""

    def __init__(self):
        self.valid = True
        self.rings = set()
        self.columns = set()
        self.regions = set()

    def validate_move(self, floor, column, value):
        return self.valid

    def get_completed_rings(self):
        return self.rings

    def get_completed_columns(self):
        return self.columns

    def get_completed_regions(self):
        return self.regions


class FakeBoard:
    """Small fake Board used to test Game coordination."""

    def __init__(self):
        self.values = {}
        self.locked = []

    def set_value(self, floor, column, value):
        self.values[(floor, column)] = value
        return True

    def lock_ring(self, ring):
        self.locked.append(("ring", ring))

    def lock_column(self, column):
        self.locked.append(("column", column))

    def lock_region(self, region):
        self.locked.append(("region", region))


class FakeTimer:
    """Small fake timer."""

    def __init__(self):
        self.started = False
        self.reset_count = 0
        self.stopped = False

    def start(self):
        self.started = True

    def reset(self):
        self.reset_count += 1

    def stop(self):
        self.stopped = True


class FakeClimber:
    """Small fake climber."""

    def __init__(self):
        self.position = None

    def move_to(self, ring, column):
        self.position = (ring, column)


def make_game():
    """Create a Game with lightweight test doubles."""

    sudoku = FakeSudokuEngine()
    board = FakeBoard()
    timer = FakeTimer()
    climber = FakeClimber()

    game = Game(
        board=board,
        sudoku_engine=sudoku,
        climber=climber,
        timer=timer,
        score_threshold=0,
    )

    return game, sudoku, board, timer, climber


def test_new_game_starts_ready():
    game, *_ = make_game()

    assert game.game_status == GAME_STATUS_READY
    assert game.score == 0
    assert game.completed_objectives == 0
    assert game.princess_life == MAX_PRINCESS_LIFE
    assert game.rescue_credits == 0
    assert game.failed_timeouts == 0


def test_start_changes_status_to_playing():
    game, _, _, timer, _ = make_game()

    game.start()

    assert game.game_status == GAME_STATUS_PLAYING
    assert timer.started is True


def test_symbol_conversion():
    assert Game.symbol_to_value("●") == 1
    assert Game.symbol_to_value("■") == 2
    assert Game.symbol_to_value("▲") == 3
    assert Game.symbol_to_value("╱") == 4
    assert Game.symbol_to_value("◆") == 5
    assert Game.symbol_to_value("★") == 6
    assert Game.symbol_to_value("✚") == 7
    assert Game.symbol_to_value("○") == 8
    assert Game.symbol_to_value("♥") == 9


def test_numeric_symbol_input_is_supported():
    assert Game.symbol_to_value("1") == 1
    assert Game.symbol_to_value("9") == 9


def test_invalid_symbol_returns_none():
    assert Game.symbol_to_value("X") is None


def test_invalid_coordinates_are_rejected():
    game, *_ = make_game()

    result = game.process_move(0, 1, "●")

    assert result.success is False
    assert game.score == 0


def test_invalid_symbol_is_rejected():
    game, *_ = make_game()

    result = game.process_move(1, 1, "X")

    assert result.success is False
    assert game.score == 0


def test_invalid_sudoku_move_is_rejected():
    game, sudoku, board, *_ = make_game()

    sudoku.valid = False

    result = game.process_move(1, 1, "●")

    assert result.success is False
    assert game.score == 0
    assert board.values == {}


def test_valid_move_updates_board():
    game, _, board, *_ = make_game()

    result = game.process_move(1, 1, "●")

    assert result.success is True
    assert board.values[(1, 1)] == 1


def test_valid_move_awards_base_and_symbol_score():
    game, *_ = make_game()

    result = game.process_move(1, 1, "●")

    assert result.success is True
    assert result.score_gained == 12
    assert game.score == 12


def test_objective_completion_is_counted_once():
    game, sudoku, board, timer, _ = make_game()

    sudoku.rings.add(5)

    first = game.process_move(1, 1, "●")

    assert first.new_rings == [5]
    assert game.completed_objectives == 1
    assert 5 in game.completed_rings
    assert ("ring", 5) in board.locked
    assert timer.reset_count == 1

    second = game.process_move(1, 2, "■")

    assert second.new_rings == []
    assert game.completed_objectives == 1
    assert timer.reset_count == 1


def test_column_completed_before_ring_sets_active_column():
    game, sudoku, _, _, climber = make_game()

    sudoku.columns.add(2)

    result = game.process_move(1, 1, "●")

    assert result.success is True
    assert game.active_column == 2
    assert game.current_position is None
    assert climber.position is None


def test_ring_completion_uses_active_column():
    game, sudoku, _, _, climber = make_game()

    sudoku.columns.add(2)
    game.process_move(1, 1, "●")

    sudoku.rings.add(5)

    result = game.process_move(1, 2, "■")

    assert result.new_rings == [5]
    assert game.current_position == (5, 2)
    assert climber.position == (5, 2)


def test_new_column_moves_using_current_ring():
    game, sudoku, _, _, climber = make_game()

    sudoku.columns.add(2)
    sudoku.rings.add(5)

    game.process_move(1, 1, "●")

    assert game.current_position == (5, 2)

    sudoku.columns.add(1)

    result = game.process_move(1, 2, "■")

    assert result.new_columns == [1]
    assert game.active_column == 1
    assert game.current_position == (5, 1)
    assert climber.position == (5, 1)


def test_region_completion_counts_as_objective():
    game, sudoku, board, timer, _ = make_game()

    sudoku.regions.add(5)

    result = game.process_move(1, 1, "●")

    assert result.new_regions == [5]
    assert game.completed_regions == {5}
    assert game.completed_objectives == 1
    assert ("region", 5) in board.locked
    assert timer.reset_count == 1


def test_multiple_objectives_restore_lost_princess_life():
    game, sudoku, _, _, _ = make_game()

    game.state.princess_life = 25

    sudoku.rings.add(5)
    sudoku.columns.add(5)
    sudoku.regions.add(5)

    result = game.process_move(1, 1, "●")

    assert result.new_objectives == 3
    assert game.princess_life == 27
    assert game.rescue_credits == 0


def test_multiple_objectives_create_rescue_credit_when_extra_remains():
    game, sudoku, _, _, _ = make_game()

    game.state.princess_life = 26

    sudoku.rings.add(5)
    sudoku.columns.add(5)
    sudoku.regions.add(5)

    game.process_move(1, 1, "●")

    assert game.princess_life == 27
    assert game.rescue_credits == 1


def test_timeout_without_rescue_credit_loses_one_life():
    game, *_ = make_game()

    game.start()

    result = game.handle_timeout()

    assert result is True
    assert game.failed_timeouts == 1
    assert game.princess_life == 26


def test_timeout_with_rescue_credit_preserves_life():
    game, *_ = make_game()

    game.start()

    game.state.rescue_credits = 1

    result = game.handle_timeout()

    assert result is True
    assert game.failed_timeouts == 1
    assert game.princess_life == 27
    assert game.rescue_credits == 0


def test_princess_dies_after_27_lost_lives():
    game, *_ = make_game()

    game.state.princess_life = 1

    game.handle_timeout()

    assert game.princess_life == 0
    assert game.game_status == GAME_STATUS_GAME_OVER


def test_completed_objectives_never_exceed_27():
    game, *_ = make_game()

    game.state.completed_rings.update(range(1, 10))
    game.state.completed_columns.update(range(1, 10))
    game.state.completed_regions.update(range(1, 10))

    assert game.completed_objectives == MAX_OBJECTIVES


def test_status_contains_required_game_state():
    game, *_ = make_game()

    status = game.get_status()

    assert status["score"] == 0
    assert status["completed_objectives"] == 0
    assert status["max_objectives"] == 27
    assert status["princess_life"] == 27
    assert status["max_princess_life"] == 27
    assert status["rescue_credits"] == 0
    assert status["failed_timeouts"] == 0
    assert status["difficulty"] == "beginner"


def test_recent_events_are_recorded():
    game, *_ = make_game()

    game.start()

    events = game.get_recent_events()

    assert events
    assert "Game started." in events


def test_game_can_report_victory_state():
    game, *_ = make_game()

    game.state.game_status = GAME_STATUS_VICTORY

    assert game.is_victory() is True
    assert game.is_game_over() is False


def test_game_can_report_game_over_state():
    game, *_ = make_game()

    game.state.game_status = GAME_STATUS_GAME_OVER

    assert game.is_game_over() is True
    assert game.is_victory() is False
    
  # ---------------------------------------------------------------------------
# RIC-07: Win / Lose Integration
# ---------------------------------------------------------------------------


def test_victory_requires_all_27_objectives():
    game = Game(score_threshold=0)

    game.state.completed_rings = set(range(1, 10))
    game.state.completed_columns = set(range(1, 10))
    game.state.completed_regions = set(range(1, 9))

    assert game.completed_objectives == 26
    assert game._check_victory() is False
    assert game.game_status != GAME_STATUS_VICTORY


def test_victory_requires_climber_to_reach_princess():
    class MockClimber:
        has_reached_princess = False

    game = Game(
        climber=MockClimber(),
        score_threshold=0,
    )

    game.state.completed_rings = set(range(1, 10))
    game.state.completed_columns = set(range(1, 10))
    game.state.completed_regions = set(range(1, 10))

    assert game.completed_objectives == 27
    assert game._check_victory() is False
    assert game.game_status != GAME_STATUS_VICTORY


def test_victory_requires_score_threshold():
    class MockClimber:
        has_reached_princess = True

    game = Game(
        climber=MockClimber(),
        score_threshold=1000,
    )

    game.state.completed_rings = set(range(1, 10))
    game.state.completed_columns = set(range(1, 10))
    game.state.completed_regions = set(range(1, 10))
    game.state.score = 999

    assert game._check_victory() is False
    assert game.game_status != GAME_STATUS_VICTORY


def test_complete_victory_triggers_marriage():
    class MockClimber:
        has_reached_princess = True

    game = Game(
        climber=MockClimber(),
        score_threshold=1000,
    )

    game.state.completed_rings = set(range(1, 10))
    game.state.completed_columns = set(range(1, 10))
    game.state.completed_regions = set(range(1, 10))
    game.state.score = 1000

    assert game._check_victory() is True
    assert game.game_status == GAME_STATUS_VICTORY
    assert game.is_victory() is True

    events = game.get_recent_events()

    assert "VICTORY! The young man reached the princess." in events
    assert "MARRIAGE COMPLETE." in events


def test_game_over_prevents_further_play():
    game = Game()

    game.state.princess_life = 0
    game._check_princess_life()

    assert game.game_status == GAME_STATUS_GAME_OVER
    assert game.is_game_over() is True
    assert game.can_play() is False


def test_timeout_with_no_life_ends_game():
    game = Game()

    game.state.princess_life = 1
    game.state.rescue_credits = 0
    game.start()

    result = game.handle_timeout()

    assert result is False
    assert game.princess_life == 0
    assert game.game_status == GAME_STATUS_GAME_OVER
    assert game.is_game_over() is True


def test_rescue_credit_prevents_game_over():
    game = Game()

    game.state.princess_life = 1
    game.state.rescue_credits = 1
    game.start()

    result = game.handle_timeout()

    assert result is True
    assert game.princess_life == 1
    assert game.rescue_credits == 0
    assert game.game_status == GAME_STATUS_PLAYING 
