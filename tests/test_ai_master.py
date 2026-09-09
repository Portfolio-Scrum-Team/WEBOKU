import copy

from weboku.ai_master import AIMaster


class FakeSudoku:
    def candidates(self, ring, column):
        return [1, 3, 5]

    def __eq__(self, other):
        return isinstance(other, FakeSudoku) and self.__dict__ == other.__dict__


class FakeGame:
    def __init__(self, position="BASE"):
        self.sudoku = FakeSudoku()
        self.current_position = position
        self.completed_rings = {1, 2, 3}
        self.completed_columns = {4, 5}
        self.completed_regions = {6, 7, 8}
        self.score = 1234
        self.princess_life = 25
        self.game_status = "PLAYING"
        self.active_column = 4
        self.difficulty = "beginner"


def test_ai_initializes():
    assert AIMaster() is not None


def test_explain_rules_returns_rule_summary():
    text = AIMaster().explain_rules()
    assert "Weboku is a Sudoku climbing adventure." in text
    assert "SOLVE" in text
    assert "UNLOCK" in text
    assert "CLIMB" in text
    assert "REACH" in text
    assert "MARRY" in text


def test_explain_status_reads_game_state():
    game = FakeGame(position="BASE")
    text = AIMaster().explain_status(game)

    assert "Objectives: 8/27" in text
    assert "Rings: 3/9" in text
    assert "Columns: 2/9" in text
    assert "Windows: 3/9" in text
    assert "Score: 1234" in text
    assert "Princess life: 25/27" in text
    assert "Current position: BASE" in text
    assert "Status: PLAYING" in text


def test_roof_position_handled():
    game = FakeGame(position="ROOF")
    text = AIMaster().explain_status(game)
    assert "Current position: ROOF — PRINCESS REACHED" in text


def test_candidate_suggestions_delegate_to_sudoku_api():
    game = FakeGame()
    assert AIMaster().suggest_candidates(game, 5, 4) == [1, 3, 5]


def test_ai_does_not_mutate_game():
    game = FakeGame()
    before = copy.deepcopy(game.__dict__)

    AIMaster().explain_status(game)

    assert game.__dict__ == before


def test_invalid_move_result_can_be_explained():
    result = type("Result", (), {"success": False, "floor": 5, "column": 5, "value": 6})()
    text = AIMaster().explain_move_result(result)

    assert "Move rejected." in text
    assert "R5C5" in text


def test_successful_move_result_can_be_explained():
    result = type(
        "Result",
        (),
        {
            "success": True,
            "floor": 5,
            "column": 5,
            "value": 6,
            "symbol": "★",
            "new_rings": [5],
            "new_columns": [],
            "new_regions": [5],
            "current_position": (5, 2),
        },
    )()
    text = AIMaster().explain_move_result(result)

    assert "Move accepted." in text
    assert "R5C5 = ★ (6)" in text
    assert "Ring 5" in text
    assert "Window 5" in text
    assert "The climber moved to R5C2." in text
