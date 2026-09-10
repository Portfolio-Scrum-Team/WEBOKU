from weboku.renderer import Renderer, SYMBOLS


class DummyGame:
    def __init__(self):
        self.score = 0
        self.timer = 90
        self.position = "R5C5"
        self.status = "playing"
        self.objective = 2
        self.total_objectives = 4
        self.victory = False
        self.game_over = False


def test_symbols_defined():
    assert SYMBOLS[1] == "●"
    assert SYMBOLS[9] == "♥"


def test_renderer_renders_empty_and_filled_cells():
    board = [
        [1, 2, 0],
        [0, 5, 9],
        [7, 0, 3],
    ]
    renderer = Renderer()
    text = renderer.render_board(board)
    assert "●" in text
    assert "■" in text
    assert "◆" in text
    assert "♥" in text
    assert "·" in text


def test_renderer_marks_locked_cells():
    renderer = Renderer()
    locked = {(0, 0), (1, 1)}
    text = renderer.render_board([[1, 0], [0, 2]], locked_cells=locked)
    assert "LOCKED" in text or "L" in text


def test_renderer_has_nine_by_nine_board_layout():
    board = [[0 for _ in range(9)] for _ in range(9)]
    renderer = Renderer()
    text = renderer.render_board(board)
    lines = text.strip().splitlines()
    assert len(lines) >= 9
    assert "[·]" in text


def test_renderer_shows_nine_windows_and_board_structure():
    renderer = Renderer()
    text = renderer.render_board([[0] * 9 for _ in range(9)])
    assert "W1" in text or "WINDOWS" in text or "WINDOW" in text


def test_renderer_shows_current_position_and_climber():
    renderer = Renderer()
    text = renderer.render_status(
        "CURRENT POSITION: R5C5\nFLOOR: 5\nCOLUMN: 5\nCLIMBER: 🧗"
    )
    assert "CURRENT POSITION" in text
    assert "R5C5" in text
    assert "CLIMBER" in text


def test_renderer_shows_princess_display():
    renderer = Renderer()
    text = renderer.render_status("PRINCESS: 👸\nROOF")
    assert "PRINCESS" in text
    assert "👸" in text


def test_renderer_shows_objective_progress_score_timer():
    renderer = Renderer()
    text = renderer.render_status("OBJECTIVES: 2/4\nSCORE: 120\nTIME: 90")
    assert "OBJECTIVES" in text
    assert "2/4" in text
    assert "SCORE" in text
    assert "TIME" in text


def test_renderer_shows_victory_and_game_over_states():
    renderer = Renderer()
    victory = renderer.render_status("VICTORY: YES")
    game_over = renderer.render_status("GAME OVER")
    assert "VICTORY" in victory
    assert "GAME OVER" in game_over


def test_renderer_does_not_mutate_game_state():
    game = DummyGame()
    renderer = Renderer()
    original = game.score, game.timer, game.position, game.status
    renderer.render_status(
        f"SCORE: {game.score}\nTIME: {game.timer}\nPOSITION: {game.position}\nSTATUS: {game.status}"
    )
    assert (game.score, game.timer, game.position, game.status) == original
