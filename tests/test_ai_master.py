from weboku.ai_master import AIMaster


class DummyGame:
    def __init__(self):
        self.status = "playing"
        self.score = 120
        self.position = "R5C5"
        self.objectives = ["window 1", "window 2"]
        self.climber = "floor 5"
        self.princess_life = 3
        self.board = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ]


def test_ai_explains_weboku_rules():
    ai = AIMaster()
    text = ai.explain_rules()
    assert "Sudoku" in text
    assert "climber" in text.lower()
    assert "princess" in text.lower()


def test_ai_explains_current_status():
    game = DummyGame()
    ai = AIMaster(game=game)
    text = ai.explain_status()
    assert "playing" in text.lower()
    assert "120" in text
    assert "R5C5" in text


def test_ai_provides_advisory_hint_without_mutating_game():
    game = DummyGame()
    ai = AIMaster(game=game)
    before = (game.status, game.score, game.position)
    hint = ai.provide_hint()
    after = (game.status, game.score, game.position)
    assert "hint" in hint.lower() or "check" in hint.lower()
    assert before == after


def test_ai_explains_move_result():
    ai = AIMaster()
    text = ai.explain_move_result({"cell": "R5C5", "value": 7, "ok": True})
    assert "R5C5" in text
    assert "accepted" in text.lower()


def test_ai_explains_objectives():
    game = DummyGame()
    ai = AIMaster(game=game)
    text = ai.explain_objectives()
    assert "objective" in text.lower()
    assert "window" in text.lower()


def test_ai_explains_climbing_system():
    game = DummyGame()
    ai = AIMaster(game=game)
    text = ai.explain_climbing_system()
    assert "climb" in text.lower()
    assert "automatically" in text.lower()


def test_ai_cannot_modify_game_state():
    game = DummyGame()
    ai = AIMaster(game=game)
    before = {
        "status": game.status,
        "score": game.score,
        "position": game.position,
        "princess_life": game.princess_life,
    }
    ai.explain_status()
    ai.provide_hint()
    after = {
        "status": game.status,
        "score": game.score,
        "position": game.position,
        "princess_life": game.princess_life,
    }
    assert before == after
